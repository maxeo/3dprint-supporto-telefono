"""Scrive dati/guida_spec.json dalle misure di dati/geometria.json (lanciare dopo blender/costruisci.py).
La guida ha un selettore del numero di prolunghe: i pezzi sono nella posa CON_PROLUNGHE della scena (il massimo)
e ogni opzione abbassa slitta e piatto di un tratto per ogni prolunga tolta."""
import json, math, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
geo = json.load(open(os.path.join(root, "dati", "geometria.json"), encoding="utf-8"))
P, C, MS, MO = geo["pezzi"], geo["controlli"], geo["misure"], geo["montaggio"]
F = MS["filetto"]
NPRO = MS["posa_prolunghe"]["prolunghe"]       # prolunghe nella posa: il massimo del selettore
N_DEF = 1                                        # opzione proposta: una prolunga


def n(x, d=1):
    s = f"{x:.{d}f}".replace(".", ",")
    return s[:-2] if s.endswith(",0") else s


def g(k):
    return n(P[k]["peso_PETG_g"], 0)


def part(id_, key, label, group, prof, note, copie=None, qty=1):
    m = MO[key]
    p = {"id": id_, "label": label, "group": group, "file": f"stl/{key.split('.')[0]}.stl", "print": prof,
         "mode": "mesh", "max_triangles": 4000, "matrix": m["matrice"], "assembled_bounds": m["bounds"],
         "quantity": qty, "note_html": note}
    if copie:                                 # copie uguali e con la stessa rotazione: spostamenti dalla prima
        b0 = [r[0] for r in m["bounds"]]
        p["instances"] = [[0, 0, 0]] + [[round(MO[k]["bounds"][i][0] - b0[i], 3) for i in range(3)] for k in copie]
    return p


pz, pp = MS["posa_uso"], MS["posa_prolunghe"]
ga = MS["guida_appoggio"]
mens = C["mensola_dal_tavolo_mm"]
TEL = MS["telefono"]
ACC = json.load(open(os.path.join(root, "dati", "accessori.json"), encoding="utf-8"))
TEL_IDS = [a["id"] for a in ACC if a["piece"] == "Telefono"]
CAVO_IDS = [a["id"] for a in ACC if a["piece"] == "Cavo"]
parts = [
 part("P01", "P01_Base", "Base", "Base", "base",
      f"<p>Piastra {n(MS['base'][0])} × {n(MS['base'][1])} × {n(MS['base'][2])} con la forchetta della cerniera bassa: due orecchie da {n(MS['orecchia'])} mm, foro per la vite Ø{n(F['cerniere'])} e, sull'orecchia sinistra, la sede quadra del collo della vite: non la lascia girare. Sotto quattro incavi Ø10,5 per piedini adesivi; sopra tre incavi dove girano i pomelli (uno da aperto, due da chiuso). {g('P01_Base')} g a pezzo pieno.</p>"),
 part("P02", "P02_Guaina", "Guaina del braccio", "Braccio", "braccio",
      f"<p>Tratto {n(MS['braccio'][0])} × {n(MS['braccio'][1])} lungo {n(MS['tratto'])} mm dall'asse, con la nocca in fondo e il canale {n(MS['canale'][0])} × {n(MS['canale'][1])}. Davanti il canale ha una fessura da {n(MS['fessura'])} in cui corre la nervatura della barra. Sul fianco destro la morsa: rinforzo con la sede esagonale del dado P12 per la vite di blocco. Sulla faccia destra della nocca una corona di {MS['denti']['numero']} denti fa presa con la rondella P14: la cerniera bassa va a scatti di {n(MS['denti']['scatto_gradi'], 0)}°. {g('P02_Guaina')} g.</p>"),
 part("P14", "P14_Rondella_Dentata", "Rondella dentata · cerniera bassa", "Base", "pomelli",
      f"<p>Rondella spessa {n(C['rondella_spessore_mm'])} mm con {MS['denti']['numero']} denti alti {n(MS['denti']['altezza'])} da un lato: sta fra la nocca della guaina e l'orecchia destra della base, coi denti verso la nocca. Il piede appoggia sulla base e non la lascia girare, così i denti tengono il braccio anche col pomello poco stretto. {g('P14_Rondella_Dentata')} g.</p>"),
 part("P07", "P07_Prolunga", "Prolunga", "Prolunghe", "braccio",
      f"<p>Sotto una barra come quella della slitta, sopra un tratto come la guaina con la sua morsa: entra nella guaina o in un'altra prolunga, e la slitta o un'altra prolunga entrano in lei. Ogni prolunga alza di {n(MS['tratto'], 0)} mm, più fino a {n(C['sfilo_massimo_per_tratto_mm'], 0)} di sfilo. Se ne mettono quante si vuole: il selettore in cima ne mostra da 0 a {NPRO}. {g('P07_Prolunga')} g.</p>",
      copie=[f"P07_Prolunga.{k}" for k in range(2, NPRO + 1)], qty=NPRO),
 part("P03", "P03_Slitta", "Slitta del braccio", "Braccio", "braccio",
      f"<p>Barra {n(MS['barra'][1])} × {n(MS['barra'][2])} ({n(MS['gioco_slitta_per_lato'])} mm di gioco per lato) con la nervatura davanti e, in cima, la nocca della cerniera alta. Sul fianco destro una scanalatura dove punta la vite della morsa: fa anche da fermo, la barra esce al massimo di {n(C['sfilo_massimo_per_tratto_mm'])} mm. {g('P03_Slitta')} g.</p>"),
 part("P04", "P04_Piatto", "Piatto", "Piatto", "piatto",
      f"<p>Piatto {n(MS['piatto'][0])} × {n(MS['piatto'][1])} × {n(MS['piatto'][2])} con la forchetta della cerniera alta sul dorso. Dentro lo spessore corre la guida a T dell'appoggio: fessura da {n(ga['fessura'])} sulla faccia, cava da {n(ga['cava'])} per la testa della vite, aperta sul bordo basso. {g('P04_Piatto')} g.</p>"),
 part("P05", "P05_Appoggio", "Appoggio regolabile", "Piatto", "appoggio",
      f"<p>Mensola con la sponda davanti, per telefoni spessi fino a {n(MS['telefono_max'])} mm con la cover, e un'asola in mezzo per il cavo, aperta fino in cima alla sponda: il cavo si infila e si sfila dall'alto. Scorre lungo il piatto per {n(C['corsa_appoggio_mm'], 0)} mm: la vite P09 con la testa quadra nella guida a T e il pomello sotto la mensola la bloccano. Una chiavetta sul retro corre nella fessura e non la fa girare. {g('P05_Appoggio')} g.</p>"),
 part("P06A", "P06_Pomello", "Pomello · cerniera bassa", "Pomelli", "pomelli",
      f"<p>Pomello zigrinato Ø{n(MS['pomello_diametro'])} con la madrevite Ø{n(F['cerniere'])} stampata dentro, cieca: si avvita sulla vite P08 e stringe le orecchie della base sulla nocca del braccio. {g('P06_Pomello')} g.</p>"),
 part("P06B", "P06_Pomello.2", "Pomello · cerniera alta", "Pomelli", "pomelli",
      "<p>Stesso pomello: regola la durezza della cerniera del piatto.</p>"),
 part("P08A", "P08_Vite_Cerniera", "Vite · cerniera bassa", "Viti", "viti",
      f"<p>Vite stampata Ø{n(F['cerniere'])} passo {n(F['passo'])}, lunga {n(MS['vite_cerniera']['lunga'], 0)} mm: testa tonda Ø{n(MS['vite_cerniera']['testa'][0], 0)} e sotto un collo quadro che entra nella sede dell'orecchia e non gira. {g('P08_Vite_Cerniera')} g.</p>"),
 part("P08B", "P08_Vite_Cerniera.2", "Vite · cerniera alta", "Viti", "viti",
      "<p>Stessa vite, nella forchetta del piatto.</p>"),
 part("P09", "P09_Vite_Appoggio", "Vite · appoggio", "Viti", "viti",
      f"<p>Vite Ø{n(F['morse_appoggio'])} lunga {n(MS['vite_appoggio']['lunga'])} mm con la testa quadra da {n(MS['vite_appoggio']['testa'][0])}: scorre nella cava del piatto e non gira. {g('P09_Vite_Appoggio')} g.</p>"),
 part("P10", "P10_Pomello_Appoggio", "Pomello · appoggio", "Pomelli", "pomelli",
      f"<p>Pomello con la madrevite Ø{n(F['morse_appoggio'])}: sotto la mensola, blocca l'appoggio sul piatto. {g('P10_Pomello_Appoggio')} g.</p>"),
 part("P11", "P11_Pomello_Morsa", "Pomello · morse del braccio", "Pomelli", "pomelli",
      f"<p>Pomello e vite in un pezzo solo: vite Ø{n(F['morse_appoggio'])} lunga {n(MS['vite_morsa'], 0)} mm che si avvita nel dado P12 e punta nella scanalatura della barra. Uno sulla guaina e uno su ogni prolunga. {g('P11_Pomello_Morsa')} g.</p>",
      copie=[f"P11_Pomello_Morsa.{k}" for k in range(2, 2 + NPRO)], qty=NPRO + 1),
 part("P12", "P12_Dado_Morsa", "Dado · morse del braccio", "Viti", "viti",
      f"<p>Dado esagonale da {n(MS['dado_morsa'][0], 0)} alto {n(MS['dado_morsa'][1], 0)} mm con la madrevite Ø{n(F['morse_appoggio'])}: entra nella sede del rinforzo e non gira. Uno per morsa. {g('P12_Dado_Morsa')} g.</p>",
      copie=[f"P12_Dado_Morsa.{k}" for k in range(2, 2 + NPRO)], qty=NPRO + 1),
]

a = math.radians(pp["alfa"]); s_dir = math.radians(90 + pz["piatto_dalla_verticale"])
braccio = [round(math.cos(a), 3), 0, round(math.sin(a), 3)]
davanti_piatto = [round(math.cos(s_dir - math.pi / 2), 3), 0, round(math.sin(s_dir - math.pi / 2), 3)]
sotto_piatto = [round(-math.cos(s_dir), 3), 0, round(-math.sin(s_dir), 3)]
su_piatto = [-v for v in sotto_piatto]

# sezione della cerniera (vista dall'alto, asse orizzontale), 6 px/mm
Yo, Yi = MS["nocca"] / 2 + MS["gioco_nocca_per_lato"] + MS["orecchia"], MS["nocca"] / 2 + MS["gioco_nocca_per_lato"]
Ht, Lv, Dv = MS["vite_cerniera"]["testa"][1], MS["vite_cerniera"]["lunga"], F["cerniere"]
S, X0 = 6.0, 230.0
def X(y): return X0 + y * S
svg = (f"<svg viewBox='0 0 460 200' xmlns='http://www.w3.org/2000/svg' font-size='11' font-family='sans-serif'>"
       f"<rect x='{X(-Yo)}' y='40' width='{MS['orecchia'] * S}' height='120' fill='#bfc3c9'/>"
       f"<rect x='{X(Yi)}' y='40' width='{MS['orecchia'] * S}' height='120' fill='#bfc3c9'/>"
       f"<rect x='{X(-MS['nocca'] / 2)}' y='40' width='{MS['nocca'] * S}' height='120' fill='#8aa1b8'/>"
       f"<rect x='{X(-Yo - Ht)}' y='{100 - 9 * S}' width='{Ht * S}' height='{18 * S}' fill='#9aa0a8'/>"
       f"<rect x='{X(-Yo)}' y='{100 - Dv / 2 * S}' width='{Lv * S}' height='{Dv * S}' fill='#9aa0a8' opacity='.9'/>"
       f"<rect x='{X(Yo)}' y='30' width='{11 * S}' height='140' fill='#333' rx='6' opacity='.9'/>"
       f"<text x='{X(-Yo)}' y='185'>orecchia {n(MS['orecchia'])}</text>"
       f"<text x='{X(-8)}' y='30'>nocca {n(MS['nocca'])}</text>"
       f"<text x='{X(-Yo - Ht)}' y='22'>testa e collo quadro</text>"
       f"<text x='{X(Yo) - 10}' y='185'>pomello filettato</text>"
       f"<text x='{X(-6)}' y='185'>gioco {n(MS['gioco_nocca_per_lato'])} per lato</text></svg>")

# sezione del braccio: canale con fessura davanti, barra con nervatura, 7 px/mm
B = 7.0; cx, cy = 150.0, 100.0
def R(y0, y1, v0, v1, fill, op=1):
    return f"<rect x='{cx + y0 * B}' y='{cy - v1 * B}' width='{(y1 - y0) * B}' height='{(v1 - v0) * B}' fill='{fill}' opacity='{op}'/>"
by, bv, ny = MS["barra"][1] / 2, MS["barra"][2] / 2, MS["nervatura"] / 2
fy, chy, chv = MS["fessura"] / 2, MS["canale"][0] / 2, MS["canale"][1] / 2
svg2 = (f"<svg viewBox='0 0 420 200' xmlns='http://www.w3.org/2000/svg' font-size='11' font-family='sans-serif'>"
        + R(-15, 15, -10, 10, "#8aa1b8") + R(-chy, chy, -chv, chv, "#fff") + R(-fy, fy, -10, -chv, "#fff")
        + R(-by, by, -bv, bv, "#5aa678", .9) + R(-ny, ny, -10, -bv + 0.2, "#5aa678", .9)
        + R(15, 20, -9.5, 9.5, "#8aa1b8") +
        f"<line x1='{cx - 120}' y1='{cy + 10 * B}' x2='{cx + 170}' y2='{cy + 10 * B}' stroke='#888' stroke-dasharray='4 3'/>"
        f"<text x='{cx + 140}' y='{cy - 5}'>morsa</text><text x='{cx + 140}' y='{cy + 9}'>(P11 + P12)</text>"
        f"<text x='{cx - 145}' y='{cy - 60}'>canale {n(MS['canale'][0])} × {n(MS['canale'][1])}</text>"
        f"<text x='{cx - 145}' y='{cy - 45}'>barra {n(MS['barra'][1])} × {n(MS['barra'][2])}</text>"
        f"<text x='{cx - 145}' y='{cy + 88}'>faccia davanti = piatto di stampa</text>"
        f"<text x='{cx + 30}' y='{cy + 88}'>nervatura {n(MS['nervatura'])} in fessura {n(MS['fessura'])}</text></svg>")

pk = C["ingombro_piegato_mm"]


def ids_for(k):
    """Pezzi e copie presenti con k prolunghe."""
    return ([p["id"] for p in parts if p["id"] != "P07" or k] + [f"P07·{m}" for m in range(2, k + 1)]
            + [f"{b}·{m}" for b in ("P11", "P12") for m in range(2, k + 2)])


def steps_for(k):
    pro_id = (["P07"] + [f"P07·{m}" for m in range(2, k + 1)]) if k else []
    knob = ["P11"] + [f"P11·{m}" for m in range(2, k + 2)]
    nut = ["P12"] + [f"P12·{m}" for m in range(2, k + 2)]
    tratti = ["P02"] + pro_id
    out, built = [], ["P02"]
    for j, cur in enumerate(pro_id):
        prev = tratti[j]
        built += [cur]
        out.append({"title": "Prima prolunga nella guaina" if j == 0 else f"Prolunga {j + 1} nella precedente", "short": "dall'alto",
                    "text": f"Infila la barra di {cur.split('·')[0]} nel canale di {prev.split('·')[0]}, con la nervatura dalla parte della fessura (davanti) e la scanalatura dalla parte della morsa (a destra). Deve scorrere senza sforzo fino a che il tratto largo batte sul tratto sotto.",
                    "parts": [prev, cur], "built": list(built), "moving": [cur], "dir": braccio, "travel": 80})
        built += [nut[j], knob[j]]
        out.append({"title": "Morsa della guaina" if j == 0 else f"Morsa della prolunga {j}", "short": "dado P12 + pomello P11",
                    "text": f"Spingi un dado P12 nella sede esagonale del rinforzo di {prev.split('·')[0]} e avvitaci un pomello P11: la punta della sua vite entra nella scanalatura della barra. Stringi per bloccare, allenta di mezzo giro per regolare l'altezza. Non svitarlo del tutto: è anche il fermo che non fa uscire la barra.",
                    "parts": [prev, cur, nut[j], knob[j]], "built": list(built), "moving": [nut[j], knob[j]], "dir": [0, 1, 0], "travel": 30})
    last = tratti[-1]
    built += ["P03", nut[k], knob[k]]
    return out + [
     {"title": "Slitta nell'ultimo tratto" if k else "Slitta nella guaina", "short": "e la sua morsa",
      "text": f"Infila la slitta P03 in {last.split('·')[0]} come le barre prima, poi chiudi la morsa con un dado P12 e un pomello P11.",
      "parts": [last, "P03", nut[k], knob[k]], "built": list(built), "moving": ["P03", nut[k], knob[k]], "dir": braccio, "travel": 80},
     {"title": "Braccio sulla base", "short": "nocca e rondella nella forchetta", "text": "Appoggia la rondella P14 contro l'orecchia destra di P01, denti verso il centro e piede sulla base. Cala la nocca in fondo a P02 fra la rondella e l'orecchia sinistra, con la faccia dentata a destra, e allinea i fori. Infila la vite P08 da sinistra: il collo quadro sotto la testa entra nella sua sede e la vite non gira più.",
      "parts": ["P01", "P14", "P02", "P08A"], "built": ["P01", "P14", "P08A"] + built, "moving": list(built), "dir": [0, 0, 1], "travel": 70},
     {"title": "Pomello della cerniera bassa", "short": "da destra", "text": f"Avvita il pomello P06A sulla vite che sporge a destra finché i denti della nocca entrano in quelli della rondella e il braccio non scatta più: non serve stringere forte. Per cambiare inclinazione allenta di mezzo giro, porta il braccio allo scatto voluto (ogni {n(MS['denti']['scatto_gradi'], 0)}°) e richiudi.",
      "parts": ["P01", "P14", "P08A", "P06A"], "built": ["P01", "P14", "P08A", "P06A"] + built, "moving": ["P06A"], "dir": [0, 1, 0], "travel": 30},
     {"title": "Appoggio sul piatto", "short": "vite nella guida a T", "text": "Fai scorrere la testa quadra della vite P09 nella cava del piatto P04, entrando dal bordo basso: il gambo esce dalla fessura sulla faccia. Appoggia P05 con la chiavetta nella fessura e avvita il pomello P10 sotto la mensola.",
      "parts": ["P04", "P09", "P05", "P10"], "built": ["P04", "P09", "P05", "P10"], "moving": ["P05", "P10"], "dir": davanti_piatto, "travel": 40},
     {"title": "Piatto sulla testa del braccio", "short": "forchetta sulla nocca", "text": "Porta la forchetta sul dorso di P04 attorno alla nocca in cima a P03 e infila la seconda vite P08 da destra, col collo quadro nella sede.",
      "parts": ["P03", "P04", "P08B"], "built": ["P01", "P14", "P08A", "P06A"] + built + ["P04", "P09", "P05", "P10", "P08B"], "moving": ["P04", "P09", "P05", "P10", "P08B"], "dir": davanti_piatto, "travel": 60},
     {"title": "Pomello della cerniera alta", "short": "da sinistra", "text": "Avvita P06B sulla vite che sporge a sinistra e regola la durezza come per la cerniera bassa.",
      "parts": ["P04", "P08B", "P06B"], "built": ids_for(k), "moving": ["P06B"], "dir": [0, -1, 0], "travel": 30},
     {"title": "Cavo nell'asola", "short": "spina sopra la mensola", "text": "Cala il cavo dall'alto nell'apertura della sponda dell'appoggio P05 e porta la spina nell'asola: il guscio metallico sporge sopra la mensola e il corpo resta nell'asola. Fai scendere il cavo davanti al braccio, appoggialo sulla base dal lato sinistro (quello della testa della vite, lontano dal pomello) e fallo uscire dal bordo dietro.",
      "parts": ["P05"] + CAVO_IDS, "built": ids_for(k) + CAVO_IDS},
     {"title": "Telefono e regolazioni", "short": "sulla spina, poi altezza e appoggio", "text": f"Appoggia il telefono sul piatto con lo schermo verso di te e fallo scendere sulla mensola: la presa USB-C entra sulla spina. Ora regola. Altezza: allenta una morsa, sfila (fino a {n(C['sfilo_massimo_per_tratto_mm'], 0)} mm per tratto) e stringi. Appoggio: allenta P10 e fallo scorrere lungo il piatto, il cavo lo segue. Con le prolunghe o con l'appoggio in alto tieni il braccio dritto: il telefono deve restare sopra la base. Per chiuderlo togli il telefono, sfila il cavo dall'alto, poi le prolunghe, poi slitta dentro, piatto sul braccio, braccio sulla base.",
      "parts": TEL_IDS, "built": ids_for(k) + CAVO_IDS + TEL_IDS, "moving": TEL_IDS, "dir": su_piatto, "travel": 70},
    ]


def parola(k):
    return "senza prolunghe" if k == 0 else f"con {k} prolung{'a' if k == 1 else 'he'}"


def print_for(k):
    pr = json.loads(json.dumps(PRINT))
    pr["common_html"] = pr["common_html"].replace("{conto}", f"{parola(k)}: {k} × P07, {k + 1} pomelli P11 e {k + 1} dadi P12")
    return pr


def opzione(k):
    dz = -(NPRO - k) * MS["tratto"]               # braccio dritto nella posa: un tratto in meno = più in basso in Z
    m = mens[f"{k}_prolunghe"]
    return {"id": f"n{k}", "label": "Senza prolunghe" if k == 0 else f"{k} prolung{'a' if k == 1 else 'he'}",
            "description": f"mensola {n(m[0], 0)}–{n(m[1], 0)} mm dal tavolo",
            "parts": [p["id"] for p in parts if p["id"] != "P07" or k],
            "shift": {i: [0, 0, dz] for i in ("P03", "P04", "P05", "P06B", "P08B", "P09", "P10")},
            "copies": {"P07": k, "P11": k + 1, "P12": k + 1}, "quantity": {"P07": k, "P11": k + 1, "P12": k + 1},
            "steps": steps_for(k),
            "override": {"caption": f"Il supporto {parola(k)}, braccio dritto, piatto inclinato di {n(pz['piatto_dalla_verticale'], 0)}° e appoggio in basso.",
                         "print": print_for(k)}}


PRINT = {"eyebrow": "03 / Stampa", "h2": "Tutto stampato, anche le viti.",
  "common_html": "<b>Profilo comune:</b> Kobra S1, ugello 0,4 mm, PETG, strato 0,20 mm. Sono parametri che <b>propongo io, da verificare</b>: il supporto non è ancora stato stampato. STL in millimetri, scala 100%, già orientati e appoggiati a Z = 0. Nessun pezzo ha bisogno di supporti e non serve viteria: viti, dadi e pomelli si stampano. I pesi indicati sono a pezzo pieno: col riempimento consigliato vengono meno. Quantità {conto}.",
  "profiles": [
   {"key": "base", "title": "P01 · base", "rows": [["Orientamento", "piastra sul piatto, orecchie in su"], ["Pareti", "4"], ["Riempimento", "40% Gyroid"], ["Supporti", "no"]],
    "why": "La base fa da contrappeso: più è piena, meno il supporto si ribalta, soprattutto con le prolunghe. Le sedi esagonali sui fianchi hanno un vertice in alto, così il cielo si chiude senza supporti.",
    "summary": "4 pareti · 40% · senza supporti"},
   {"key": "braccio", "title": "P02 guaina · P07 prolunghe · P03 slitta", "rows": [["Orientamento", "faccia davanti (con la fessura) sul piatto, come negli STL"], ["Pareti", "4"], ["Riempimento", "30%"], ["Supporti", "no: il cielo del canale è un ponte di 24 mm"], ["Compensazione zampa d'elefante", "0,15 mm"]],
    "why": f"La nervatura sotto ogni barra arriva fino alla faccia davanti: barra e tratto largo poggiano sul piatto insieme, quindi le prolunghe si stampano coricate senza supporti e le fibre corrono lungo il braccio. Barra e nervatura hanno {n(MS['gioco_slitta_per_lato'])} mm di gioco per lato: la compensazione del primo strato evita che la nervatura si allarghi e impunti nella fessura.",
    "summary": "coricati · 4 pareti · 30%"},
   {"key": "piatto", "title": "P04 · piatto", "rows": [["Orientamento", "faccia del telefono sul piatto, forchetta in su"], ["Pareti", "4"], ["Riempimento", "25%"], ["Supporti", "no: il cielo della cava è un ponte di 7,4 mm"]],
    "why": "La faccia su cui appoggia il telefono viene liscia dal piatto di stampa e la fessura della guida a T si apre proprio lì.",
    "summary": "faccia giù · 4 pareti · 25%"},
   {"key": "appoggio", "title": "P05 · appoggio", "rows": [["Orientamento", "su un fianco, come negli STL (alto 70 mm)"], ["Pareti", "4"], ["Riempimento", "40%"], ["Supporti", "no"], ["Brim", "5 mm consigliato"]],
    "why": "Su un fianco il profilo di flangia, mensola e sponda è tutto in pianta e sale dritto; il foro della vite viene orizzontale e piccolo. Il brim tiene fermo un pezzo alto e stretto.",
    "summary": "di fianco · 4 pareti · brim"},
   {"key": "pomelli", "title": "P06 · P10 · P11 pomelli · P14 rondella", "rows": [["Orientamento", "come negli STL: P06 e P10 con l'imbocco della madrevite sul piatto, P11 con la cima sul piatto e la vite in su, P14 piatta coi denti in su"], ["Pareti", "4"], ["Riempimento", "50%"], ["Strato", "0,16 mm"], ["Supporti", "no"]],
    "why": "In piedi il filetto si stampa giro per giro senza supporti; l'invito a 45° all'imbocco assorbe la zampa d'elefante. Lo strato più fine fa fianchi più lisci: il pomello si avvita senza impuntarsi, e sulla rondella fa denti più netti.",
    "summary": "in piedi · 0,16 mm · 50%"},
   {"key": "viti", "title": "P08 · P09 viti · P12 dadi", "rows": [["Orientamento", "viti in piedi sulla testa, dadi piatti"], ["Pareti", "6 (le viti vengono piene)"], ["Riempimento", "100%"], ["Strato", "0,16 mm"], ["Velocità", "lenta: tempo minimo per strato 8 s"], ["Supporti", "no"]],
    "why": f"Il filetto trapezoidale passo {n(F['passo'])} ha fianchi ripidi e si stampa in piedi senza supporti (è quello già provato sulle palline, con {n(F['gioco_radiale'])} mm di gioco radiale). Una vite piena e lenta ha strati ben fusi: la vite di cerniera lavora a trazione quando stringi il pomello. Se si sbriciola, stampa la vite più calda di 10 °C.",
    "summary": "in piedi · piene · 0,16 mm"}],
  "extra_rows": [{"label": "Piedini adesivi (facoltativi)", "what": "base", "file": "", "quantity": 4, "dims": "Ø10 × 1 mm", "print": ""}],
  "note_html": "Le misure da cambiare sono in cima a <code>blender/costruisci.py</code>: <code>GIOCO_NOCCA</code> se le cerniere restano dure anche col pomello lento, <code>GIOCO_SLITTA</code> se barre e nervature scorrono male, <code>F_GIOCO</code> se i pomelli si avvitano duri o ballano sulle viti, <code>TELEFONO_MAX</code> per telefoni più spessi, <code>TRATTO</code> per prolunghe più corte o più lunghe. Lo script ricontrolla che nessun pezzo si tocchi (aperto, con le prolunghe e chiuso) e lo scrive in <code>dati/geometria.json</code>."}

spec = {
 "root": "..", "output": "guida.html", "title": "Supporto Telefono · Guida",
 "theme": {"accent": "#2f6fa8", "viewer_bg": "#1b1f24"},
 "header": {
  "eyebrow": "Supporto Telefono · pieghevole da scrivania · PETG",
  "h1": "Si alza a tratti, si chiude piatto.",
  "intro_html": f"<b>Supporto per telefono da scrivania, pieghevole, con braccio telescopico, prolunghe e appoggio regolabile.</b> Le due cerniere sono viti stampate strette da un pomello zigrinato filettato: la durezza la scegli a mano. Non serve comprare niente: anche viti e dadi si stampano. Il braccio è fatto a tratti che si infilano uno nell'altro, ognuno con la sua <b>morsa</b> a pomello: senza prolunghe la mensola va da {n(mens['0_prolunghe'][0], 0)} a {n(mens['0_prolunghe'][1], 0)} mm dal tavolo, e ogni <b>prolunga</b> (P07, quante ne vuoi) aggiunge {n(MS['tratto'], 0)} mm più {n(C['sfilo_massimo_per_tratto_mm'], 0)} di sfilo. L'<b>appoggio</b> scorre lungo il piatto per {n(C['corsa_appoggio_mm'], 0)} mm su una guida a T e si blocca col suo pomello. Scegli qui sotto quante prolunghe vuoi: vista, passaggi e lista di stampa si aggiornano.",
  "facts": [{"value": f"{n(pk[0][1] - pk[0][0], 0)} × {n(pk[1][1] - pk[1][0], 0)} × {n(pk[2][1], 0)} mm", "label": "chiuso, senza prolunghe"},
            {"value": f"{n(mens['0_prolunghe'][0], 0)}–{n(mens['0_prolunghe'][1], 0)} mm", "label": "mensola dal tavolo, senza prolunghe"},
            {"value": f"+{n(MS['tratto'], 0)} mm", "label": "per ogni prolunga, più lo sfilo"},
            {"value": "zero viteria", "label": "viti, dadi e pomelli stampati"}]},
 "camera": {"yaw": -0.9, "pitch": 0.3},
 "caption": "",
 "model_note_html": f"<span class='badge'>Quote del modello</span><p>Altezza della mensola dal tavolo, braccio dritto, dal tutto chiuso al tutto sfilato con l'appoggio in alto: senza prolunghe {n(mens['0_prolunghe'][0], 0)}–{n(mens['0_prolunghe'][1], 0)} mm, con una {n(mens['1_prolunghe'][0], 0)}–{n(mens['1_prolunghe'][1], 0)}, con due {n(mens['2_prolunghe'][0], 0)}–{n(mens['2_prolunghe'][1], 0)}, con tre {n(mens['3_prolunghe'][0], 0)}–{n(mens['3_prolunghe'][1], 0)}. Chiuso: {n(pk[2][1])} mm di spessore.</p>",
 "groups": {"Base": {"color": "#c9ccd1"}, "Braccio": {"color": "#7f9bb8"}, "Prolunghe": {"color": "#6db38a"},
            "Piatto": {"color": "#3f86c4"}, "Pomelli": {"color": "#454a52"}, "Viti": {"color": "#9aa0a8"}},
 "parts": parts,
 "steps_section": {"eyebrow": "01 / Montaggio", "h2": "Dal braccio al piatto.",
  "intro_html": "Destra e sinistra guardando il supporto da davanti, dalla parte del telefono. Viti, dadi e pomelli sono stampati: si avvitano a mano, senza attrezzi. Prima di montarli prova ogni pomello sulla sua vite: se è duro, avvita e svita un paio di volte.",
  "start_html": "<h3>Prima le viti.</h3><p>Le viti di cerniera P08 vanno nei pomelli P06, la vite P09 nel pomello P10, i pomelli delle morse P11 nei dadi P12. Prova ogni coppia prima di montarla: deve avvitarsi a mano fino in fondo. Se un filetto è sporco di fili, ripassalo avvitando e svitando.</p>"},
 "steps": steps_for(N_DEF),
 "configurations": {"default": f"n{N_DEF}", "options": [opzione(k) for k in range(NPRO + 1)]},
 "print": print_for(N_DEF),
 "notes": {"eyebrow": "04 / Cerniera e braccio", "h2": "Una vite, un pomello, la frizione la scegli tu.", "nav": "Giunti",
  "cards": [{"title": "Sezione della cerniera", "html": f"<p>La nocca larga {n(MS['nocca'])} sta fra due orecchie con {n(MS['gioco_nocca_per_lato'])} mm di gioco per lato. La vite stampata P08 (Ø{n(F['cerniere'])}) ha sotto la testa un collo quadro che entra nella sede dell'orecchia e non gira; dall'altra parte si avvita il pomello, che ha la madrevite dentro. Girando il pomello le orecchie si flettono un poco e serrano la nocca. Il pacco è {n(C['pacco_cerniera_mm'])} mm, la vite entra {n(C['vite_cerniera_in_presa_nel_pomello_mm'])} mm nel pomello (più di tre giri), con {n(C['vite_cerniera_spazio_in_fondo_al_pomello_mm'])} mm liberi sul fondo, e resta nascosta.</p>" + svg},
            {"title": "Sezione del braccio", "html": "<p>Ogni tratto (guaina e prolunghe) ha il canale con una fessura davanti; ogni barra (prolunghe e slitta) ha sotto una nervatura che corre nella fessura e arriva a filo. La morsa è il pomello P11, con la sua vite, avvitato nel dado P12 chiuso nel rinforzo sul fianco: la punta preme nella scanalatura della barra, che finisce prima del fondo e fa da fermo.</p>" + svg2},
            {"title": "Stabilità", "html": f"<p>Con un telefono da 200 g, braccio a {n(pz['alfa'], 0)}° e appoggio in basso il baricentro cade {n(C['telefono_baricentro_x_uso_mm'], 0)} mm dentro la base; con l'appoggio tutto in alto e il braccio a {n(pz['alfa'], 0)}° cadrebbe fuori ({n(C['telefono_baricentro_x_uso_appoggio_in_alto_mm'])} mm), col braccio dritto torna dentro ({n(C['telefono_baricentro_x_dritto_appoggio_in_alto_mm'])} mm). Con le prolunghe tieni il braccio dritto: il peso resta sopra la base, ma ogni grado di inclinazione sposta il telefono di più.</p>"},
            {"title": "Cerniera bassa a scatti", "html": f"<p>La cerniera bassa porta tutto il peso del braccio e del telefono: lì l'attrito fra PETG e PETG chiederebbe di stringere tanto la vite. Per questo la nocca della guaina ha sulla faccia destra {MS['denti']['numero']} denti radiali alti {n(MS['denti']['altezza'])} mm, e la rondella P14 gli stessi denti girati: in presa il braccio non può scivolare, e il pomello deve solo tenerli dentro. La rondella non gira perché il suo piede appoggia sulla base. A sinistra la nocca ha {n(C['denti_gioco_per_sganciarli_mm'])} mm di gioco in tutto: allentando il pomello di mezzo giro i denti si staccano e il braccio gira di uno scatto ogni {n(MS['denti']['scatto_gradi'], 0)}°.</p>"},
            {"title": "Se la cerniera alta scivola", "html": "<p>Stringi il pomello. Se anche stretto non tiene (PETG molto liscio), metti una rondella di gomma o di sughero da 0,5–1 mm fra nocca e orecchia, oppure riduci <code>GIOCO_NOCCA</code> a 0,1 e ristampa. Non forzare il pomello oltre la stretta di una mano: il filetto stampato si rovina prima delle orecchie.</p>"}]},
 "files": {"h2": "I file.", "intro_html": "Gli STL sono in <code>stl/</code>; la scena e lo script che li genera in <code>blender/</code>. Nella scena le collezioni nascoste <b>CON_PROLUNGHE</b> e <b>PIEGATO</b> mostrano il supporto con due prolunghe e chiuso.",
  "links": [{"label": "README", "href": "README.md"}, {"label": "Scena Blender", "href": "blender/Supporto_Telefono.blend"},
            {"label": "Script di costruzione", "href": "blender/costruisci.py"}, {"label": "Misure e controlli", "href": "dati/geometria.json"},
            {"label": "Foto di riferimento", "href": "originale/foto_3.jpg"}]},
 "footer_html": "Guida offline: aprire questo file dalla cartella del progetto.",
 "accessories": {"file": "dati/accessori.json", "label": "Telefono e cavo", "attach": "P04", "color": "#1c1d20",
                 "tip": f"Telefono {n(TEL[0], 0)} × {n(TEL[1], 0)} × {n(TEL[2], 0)} mm sulla mensola, col cavo USB-C nell'asola dell'appoggio: solo per vedere l'ingombro, non si stampano"}
}
json.dump(spec, open(os.path.join(root, "dati", "guida_spec.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("ok", len(parts))
