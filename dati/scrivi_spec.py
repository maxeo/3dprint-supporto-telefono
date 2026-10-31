"""Scrive dati/guida_spec.json dalle misure di dati/geometria.json (lanciare dopo blender/costruisci.py).
La guida mostra il supporto con due prolunghe (posa CON_PROLUNGHE della scena)."""
import json, math, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
geo = json.load(open(os.path.join(root, "dati", "geometria.json"), encoding="utf-8"))
P, C, MS, MO, V = geo["pezzi"], geo["controlli"], geo["misure"], geo["montaggio"], geo["viti"]
NPRO = MS["posa_prolunghe"]["prolunghe"]


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
parts = [
 part("P01", "P01_Base", "Base", "Base", "base",
      f"<p>Piastra {n(MS['base'][0])} × {n(MS['base'][1])} × {n(MS['base'][2])} con la forchetta della cerniera bassa: due orecchie da {n(MS['orecchia'])} mm, foro M4 e, sull'orecchia sinistra, la sede esagonale della testa della vite. Sotto quattro incavi Ø10,5 per piedini adesivi; sopra due incavi dove girano i pomelli (uno da aperto, uno da chiuso). {g('P01_Base')} g a pezzo pieno.</p>"),
 part("P02", "P02_Guaina", "Guaina del braccio", "Braccio", "braccio",
      f"<p>Tratto {n(MS['braccio'][0])} × {n(MS['braccio'][1])} lungo {n(MS['tratto'])} mm dall'asse, con la nocca in fondo e il canale {n(MS['canale'][0])} × {n(MS['canale'][1])}. Davanti il canale ha una fessura da {n(MS['fessura'])} in cui corre la nervatura della barra. Sul fianco destro la morsa: rinforzo con la sede del dado M4 per la vite di blocco. {g('P02_Guaina')} g.</p>"),
 part("P07", "P07_Prolunga", "Prolunga", "Prolunghe", "braccio",
      f"<p>Sotto una barra come quella della slitta, sopra un tratto come la guaina con la sua morsa: entra nella guaina o in un'altra prolunga, e la slitta o un'altra prolunga entrano in lei. Ogni prolunga alza di {n(MS['tratto'], 0)} mm, più fino a {n(C['sfilo_massimo_per_tratto_mm'], 0)} di sfilo. Se ne mettono quante si vuole: nella vista ce ne sono {NPRO}. {g('P07_Prolunga')} g.</p>",
      copie=[f"P07_Prolunga.{k}" for k in range(2, NPRO + 1)], qty=NPRO),
 part("P03", "P03_Slitta", "Slitta del braccio", "Braccio", "braccio",
      f"<p>Barra {n(MS['barra'][1])} × {n(MS['barra'][2])} ({n(MS['gioco_slitta_per_lato'])} mm di gioco per lato) con la nervatura davanti e, in cima, la nocca della cerniera alta. Sul fianco destro una scanalatura dove punta la vite della morsa: fa anche da fermo, la barra esce al massimo di {n(C['sfilo_massimo_per_tratto_mm'])} mm. {g('P03_Slitta')} g.</p>"),
 part("P04", "P04_Piatto", "Piatto", "Piatto", "piatto",
      f"<p>Piatto {n(MS['piatto'][0])} × {n(MS['piatto'][1])} × {n(MS['piatto'][2])} con la forchetta della cerniera alta sul dorso. Dentro lo spessore corre la guida a T dell'appoggio: fessura da {n(ga['fessura'])} sulla faccia, cava da {n(ga['cava'])} per la testa della vite, aperta sul bordo basso. {g('P04_Piatto')} g.</p>"),
 part("P05", "P05_Appoggio", "Appoggio regolabile", "Piatto", "appoggio",
      f"<p>Mensola con la sponda davanti, per telefoni spessi fino a {n(MS['telefono_max'])} mm con la cover, e un'asola in mezzo per il cavo. Scorre lungo il piatto per {n(C['corsa_appoggio_mm'], 0)} mm: una vite M4×12 con la testa nella guida a T e il pomello sotto la mensola la bloccano. Una chiavetta sul retro corre nella fessura e non la fa girare. {g('P05_Appoggio')} g.</p>"),
 part("P06A", "P06_Pomello", "Pomello · cerniera bassa", "Pomelli", "pomelli",
      f"<p>Pomello zigrinato Ø{n(MS['pomello_diametro'])} con il dado M4 premuto nella sede: stringe le orecchie della base sulla nocca del braccio. {g('P06_Pomello')} g.</p>"),
 part("P06B", "P06_Pomello.2", "Pomello · cerniera alta", "Pomelli", "pomelli",
      "<p>Stesso pomello col dado M4: regola la durezza della cerniera del piatto.</p>"),
 part("P06C", "P06_Pomello.3", "Pomello · appoggio", "Pomelli", "pomelli",
      "<p>Stesso pomello col dado M4: blocca l'appoggio sul piatto.</p>"),
 part("P06D", "P06_Pomello.4", "Pomello · morse del braccio", "Pomelli", "pomelli",
      f"<p>Stesso pomello, ma con la <b>testa</b> della vite M4×12 nella sede: uno sulla guaina e uno su ogni prolunga ({NPRO + 1} nella vista).</p>",
      copie=[f"P06_Pomello.{k}" for k in range(5, 5 + NPRO)], qty=NPRO + 1),
]

pro_id = ["P07"] + [f"P07·{k}" for k in range(2, NPRO + 1)]
tratti = ["P02"] + pro_id
items, jl = [], {}
for k, v in V.items():
    if k.startswith("M4x50"):
        a, b, lab = ("P01", "P02", "cerniera bassa · M4×50") if k == "M4x50_cerniera" else ("P03", "P04", "cerniera alta · M4×50")
    elif k.startswith("M4x12_appoggio"):
        a, b, lab = "P04", "P05", "appoggio · M4×12 nella guida a T"
    else:
        j = 0 if "." not in k else int(k.split(".")[1]) - 1
        a, b = tratti[j], (tratti + ["P03"])[j + 1]
        lab = "morsa · M4×12"
    a, b = a.split("·")[0], b.split("·")[0]       # i giunti si citano con la sigla del pezzo, non della copia
    items.append({"a": a, "b": b, "p": v["centro"], "axis": v["asse"], "length": v["lunghezza"], "diameter": v["diametro"]})
    jl[f"{a}+{b}"] = lab

a = math.radians(pp["alfa"]); s_dir = math.radians(90 + pz["piatto_dalla_verticale"])
braccio = [round(math.cos(a), 3), 0, round(math.sin(a), 3)]
davanti_piatto = [round(math.cos(s_dir - math.pi / 2), 3), 0, round(math.sin(s_dir - math.pi / 2), 3)]
sotto_piatto = [round(-math.cos(s_dir), 3), 0, round(-math.sin(s_dir), 3)]

# sezione della cerniera (vista dall'alto, asse orizzontale), 6 px/mm
Yo, Yi, Ta = MS["nocca"] / 2 + MS["gioco_nocca_per_lato"] + MS["orecchia"], MS["nocca"] / 2 + MS["gioco_nocca_per_lato"], 3.0
S, X0 = 6.0, 230.0
def X(y): return X0 + y * S
svg = (f"<svg viewBox='0 0 460 200' xmlns='http://www.w3.org/2000/svg' font-size='11' font-family='sans-serif'>"
       f"<rect x='{X(-Yo)}' y='40' width='{MS['orecchia'] * S}' height='120' fill='#bfc3c9'/>"
       f"<rect x='{X(Yi)}' y='40' width='{MS['orecchia'] * S}' height='120' fill='#bfc3c9'/>"
       f"<rect x='{X(-MS['nocca'] / 2)}' y='40' width='{MS['nocca'] * S}' height='120' fill='#8aa1b8'/>"
       f"<rect x='{X(-Yo + Ta - 2.8)}' y='79' width='{2.8 * S}' height='42' fill='#777'/>"
       f"<rect x='{X(-Yo + Ta)}' y='88' width='{50 * S}' height='24' fill='#999' opacity='.85'/>"
       f"<rect x='{X(Yo)}' y='30' width='{11 * S}' height='140' fill='#333' rx='6'/>"
       f"<rect x='{X(Yo)}' y='79' width='{3.2 * S}' height='42' fill='#777'/>"
       f"<text x='{X(-Yo)}' y='185'>orecchia {n(MS['orecchia'])}</text>"
       f"<text x='{X(-8)}' y='30'>nocca {n(MS['nocca'])}</text>"
       f"<text x='{X(-Yo)}' y='22'>testa M4 in sede da {n(Ta)}</text>"
       f"<text x='{X(Yo) - 10}' y='185'>pomello + dado</text>"
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
        + R(15, 19, -9.5, 9.5, "#8aa1b8") +
        f"<line x1='{cx - 120}' y1='{cy + 10 * B}' x2='{cx + 170}' y2='{cy + 10 * B}' stroke='#888' stroke-dasharray='4 3'/>"
        f"<text x='{cx + 140}' y='{cy - 5}'>morsa</text><text x='{cx + 140}' y='{cy + 9}'>(vite M4)</text>"
        f"<text x='{cx - 145}' y='{cy - 60}'>canale {n(MS['canale'][0])} × {n(MS['canale'][1])}</text>"
        f"<text x='{cx - 145}' y='{cy - 45}'>barra {n(MS['barra'][1])} × {n(MS['barra'][2])}</text>"
        f"<text x='{cx - 145}' y='{cy + 88}'>faccia davanti = piatto di stampa</text>"
        f"<text x='{cx + 30}' y='{cy + 88}'>nervatura {n(MS['nervatura'])} in fessura {n(MS['fessura'])}</text></svg>")

pk = C["ingombro_piegato_mm"]
all_ids = [p["id"] for p in parts]
arm = ["P02"] + pro_id + ["P03", "P06D"] + [f"P06D·{k}" for k in range(2, NPRO + 2)]
steps = [
 {"title": "Prima prolunga nella guaina", "short": "dall'alto", "text": "Infila la barra di P07 nel canale di P02, con la nervatura dalla parte della fessura (davanti) e la scanalatura dalla parte della morsa (a destra). Deve scorrere senza sforzo fino a che il tratto largo batte sulla guaina.",
  "parts": ["P02", "P07"], "built": ["P02", "P07"], "moving": ["P07"], "dir": braccio, "travel": 80},
 {"title": "Morsa della guaina", "short": "dado M4 + pomello", "text": "Spingi un dado M4 nella sede esagonale del rinforzo di P02 e avvita il pomello P06D con la sua vite M4×12: la punta entra nella scanalatura della barra. Stringi per bloccare, allenta di mezzo giro per regolare l'altezza. Non svitarlo del tutto: è anche il fermo che non fa uscire la barra.",
  "parts": ["P02", "P07", "P06D"], "built": ["P02", "P07", "P06D"], "moving": ["P06D"], "dir": [0, 1, 0], "travel": 30, "joints": ["P02+P07"]},
]
built = ["P02", "P07", "P06D"]
for k in range(2, NPRO + 1):
    prev, cur = pro_id[k - 2], pro_id[k - 1]
    built += [cur, f"P06D·{k}"]
    steps.append({"title": f"Prolunga {k} e la sua morsa", "short": "come prima", "text": f"Infila la barra di un'altra prolunga nel tratto alto della precedente e chiudi la sua morsa con un pomello P06D, come al passaggio prima. Si ripete per ogni prolunga.",
                  "parts": [prev, cur, f"P06D·{k}"], "built": list(built), "moving": [cur, f"P06D·{k}"], "dir": braccio, "travel": 80, "joints": ["P07+P07"]})
built += ["P03", f"P06D·{NPRO + 1}"]
steps += [
 {"title": "Slitta nell'ultimo tratto", "short": "e l'ultima morsa", "text": "Infila la slitta P03 nell'ultima prolunga (o direttamente nella guaina, se non usi prolunghe) e chiudi la morsa con l'ultimo pomello P06D.",
  "parts": [pro_id[-1], "P03", f"P06D·{NPRO + 1}"], "built": list(built), "moving": ["P03", f"P06D·{NPRO + 1}"], "dir": braccio, "travel": 80, "joints": ["P07+P03"]},
 {"title": "Braccio sulla base", "short": "nocca nella forchetta", "text": "Cala la nocca in fondo a P02 fra le due orecchie di P01 e allinea i fori. Infila una vite M4×50 da sinistra: la testa esagonale entra nella sua sede e non gira più.",
  "parts": ["P01", "P02"], "built": ["P01"] + built, "moving": built, "dir": [0, 0, 1], "travel": 70, "joints": ["P01+P02"]},
 {"title": "Pomello della cerniera bassa", "short": "da destra", "text": "Avvita P06A (col dado) sulla vite che sporge a destra. Stringi finché il braccio resta fermo in ogni posizione ma si muove ancora con una mano.",
  "parts": ["P01", "P06A"], "built": ["P01", "P06A"] + built, "moving": ["P06A"], "dir": [0, 1, 0], "travel": 30},
 {"title": "Appoggio sul piatto", "short": "vite nella guida a T", "text": "Fai scorrere la testa di una M4×12 nella cava del piatto P04, entrando dal bordo basso: il gambo esce dalla fessura sulla faccia. Appoggia P05 con la chiavetta nella fessura e avvita il pomello P06C (col dado) sotto la mensola.",
  "parts": ["P04", "P05", "P06C"], "built": ["P04", "P05", "P06C"], "moving": ["P05", "P06C"], "dir": davanti_piatto, "travel": 40, "joints": ["P04+P05"]},
 {"title": "Piatto sulla testa del braccio", "short": "forchetta sulla nocca", "text": "Porta la forchetta sul dorso di P04 attorno alla nocca in cima a P03 e infila la seconda M4×50 da destra, con la testa nella sede.",
  "parts": ["P03", "P04"], "built": ["P01", "P06A"] + built + ["P04", "P05", "P06C"], "moving": ["P04", "P05", "P06C"], "dir": davanti_piatto, "travel": 60, "joints": ["P03+P04"]},
 {"title": "Pomello della cerniera alta", "short": "da sinistra", "text": "Avvita P06B sulla vite che sporge a sinistra e regola la durezza come per la cerniera bassa.",
  "parts": ["P04", "P06B"], "built": all_ids + pro_id[1:] + [f"P06D·{k}" for k in range(2, NPRO + 2)], "moving": ["P06B"], "dir": [0, -1, 0], "travel": 30},
 {"title": "Regola e prova", "short": "altezza, appoggio, inclinazione", "text": f"Altezza: allenta una morsa, sfila (fino a {n(C['sfilo_massimo_per_tratto_mm'], 0)} mm per tratto) e stringi. Appoggio: allenta P06C e fallo scorrere lungo il piatto. Con le prolunghe o con l'appoggio in alto tieni il braccio dritto: il telefono deve restare sopra la base. Per chiuderlo togli le prolunghe, poi slitta dentro, piatto sul braccio, braccio sulla base.",
  "parts": all_ids},
]

spec = {
 "root": "..", "output": "guida.html", "title": "Supporto Telefono · Guida",
 "theme": {"accent": "#2f6fa8", "viewer_bg": "#1b1f24"},
 "header": {
  "eyebrow": "Supporto Telefono · pieghevole da scrivania · PETG",
  "h1": "Si alza a tratti, si chiude piatto.",
  "intro_html": f"<b>Supporto per telefono da scrivania, pieghevole, con braccio telescopico, prolunghe e appoggio regolabile.</b> Le due cerniere sono viti M4 strette da un pomello zigrinato: la durezza la scegli a mano. Il braccio è fatto a tratti che si infilano uno nell'altro, ognuno con la sua <b>morsa</b> a pomello: senza prolunghe la mensola va da {n(mens['0_prolunghe'][0], 0)} a {n(mens['0_prolunghe'][1], 0)} mm dal tavolo, e ogni <b>prolunga</b> (P07, quante ne vuoi) aggiunge {n(MS['tratto'], 0)} mm più {n(C['sfilo_massimo_per_tratto_mm'], 0)} di sfilo. L'<b>appoggio</b> scorre lungo il piatto per {n(C['corsa_appoggio_mm'], 0)} mm su una guida a T e si blocca col suo pomello. Nella vista: {NPRO} prolunghe.",
  "facts": [{"value": f"{n(pk[0][1] - pk[0][0], 0)} × {n(pk[1][1] - pk[1][0], 0)} × {n(pk[2][1], 0)} mm", "label": "chiuso, senza prolunghe"},
            {"value": f"{n(mens['0_prolunghe'][0], 0)}–{n(mens['0_prolunghe'][1], 0)} mm", "label": "mensola dal tavolo, senza prolunghe"},
            {"value": f"+{n(MS['tratto'], 0)} mm", "label": "per ogni prolunga, più lo sfilo"},
            {"value": "solo M4", "label": "2 × M4×50, M4×12 e dadi"}]},
 "camera": {"yaw": -0.9, "pitch": 0.3},
 "caption": f"Il supporto con {NPRO} prolunghe, braccio dritto, piatto inclinato di {n(pz['piatto_dalla_verticale'], 0)}° e appoggio in basso. In grigio le viti.",
 "model_note_html": f"<span class='badge'>Quote del modello</span><p>Altezza della mensola dal tavolo, braccio dritto, dal tutto chiuso al tutto sfilato con l'appoggio in alto: senza prolunghe {n(mens['0_prolunghe'][0], 0)}–{n(mens['0_prolunghe'][1], 0)} mm, con una {n(mens['1_prolunghe'][0], 0)}–{n(mens['1_prolunghe'][1], 0)}, con due {n(mens['2_prolunghe'][0], 0)}–{n(mens['2_prolunghe'][1], 0)}, con tre {n(mens['3_prolunghe'][0], 0)}–{n(mens['3_prolunghe'][1], 0)}. Chiuso: {n(pk[2][1])} mm di spessore.</p>",
 "groups": {"Base": {"color": "#c9ccd1"}, "Braccio": {"color": "#7f9bb8"}, "Prolunghe": {"color": "#6db38a"},
            "Piatto": {"color": "#3f86c4"}, "Pomelli": {"color": "#454a52"}},
 "parts": parts,
 "connectors": {"items": items, "label": "vite", "label_plural": "viti", "joint_labels": jl},
 "steps_section": {"eyebrow": "01 / Montaggio", "h2": "Dal braccio al piatto.",
  "intro_html": "Destra e sinistra guardando il supporto da davanti, dalla parte del telefono. Le viti sono tutte M4 a testa esagonale: basta una chiave da 7 o una pinza per tenere i dadi mentre li spingi nelle sedi.",
  "start_html": "<h3>Prima i pomelli.</h3><p>Spingi un dado M4 nella sede dei tre pomelli delle cerniere e dell'appoggio (P06A, P06B, P06C) e la testa di una vite M4×12 nella sede di ogni pomello delle morse (P06D): entrano un po' forzati, premendo su un tavolo. Se ballano, una goccia di colla.</p>"},
 "steps": steps,
 "print": {"eyebrow": "03 / Stampa", "h2": "Sette file, un pomello per ogni morsa.",
  "common_html": "<b>Profilo comune:</b> Kobra S1, ugello 0,4 mm, PETG, strato 0,20 mm. Sono parametri che <b>propongo io, da verificare</b>: il supporto non è ancora stato stampato. STL in millimetri, scala 100%, già orientati e appoggiati a Z = 0. Nessun pezzo ha bisogno di supporti. I pesi indicati sono a pezzo pieno: col riempimento consigliato vengono meno. Le quantità sono quelle con 2 prolunghe: per ogni prolunga in più o in meno conta una P07 e un pomello P06D.",
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
   {"key": "pomelli", "title": "P06 · pomelli", "rows": [["Orientamento", "faccia con la sede esagonale sul piatto"], ["Pareti", "4"], ["Riempimento", "50%"], ["Copie", f"3 + 1 per ogni morsa ({NPRO + 4} con {NPRO} prolunghe)"]],
    "why": "La sede esagonale stampata a contatto col piatto viene precisa e tiene il dado a pressione.",
    "summary": "50% · un pomello per morsa"}],
  "extra_rows": [{"label": "Viteria (si compra)", "what": "cerniere", "file": "", "quantity": 2, "dims": "M4×50 testa esagonale + dado M4", "print": ""},
                 {"label": "Viteria (si compra)", "what": "appoggio", "file": "", "quantity": 1, "dims": "M4×12 testa esagonale + dado M4", "print": ""},
                 {"label": "Viteria (si compra)", "what": "morse", "file": "", "quantity": NPRO + 1, "dims": "M4×12 testa esagonale + dado M4, una per guaina e prolunga", "print": ""},
                 {"label": "Piedini adesivi (facoltativi)", "what": "base", "file": "", "quantity": 4, "dims": "Ø10 × 1 mm", "print": ""}],
  "note_html": "Le misure da cambiare sono in cima a <code>blender/costruisci.py</code>: <code>GIOCO_NOCCA</code> se le cerniere restano dure anche col pomello lento, <code>GIOCO_SLITTA</code> se barre e nervature scorrono male, <code>TELEFONO_MAX</code> per telefoni più spessi, <code>TRATTO</code> per prolunghe più corte o più lunghe. Lo script ricontrolla che nessun pezzo si tocchi (aperto, con le prolunghe e chiuso) e lo scrive in <code>dati/geometria.json</code>."},
 "notes": {"eyebrow": "04 / Cerniera e braccio", "h2": "Una vite, un pomello, la frizione la scegli tu.", "nav": "Giunti",
  "cards": [{"title": "Sezione della cerniera", "html": f"<p>La nocca larga {n(MS['nocca'])} sta fra due orecchie con {n(MS['gioco_nocca_per_lato'])} mm di gioco per lato. La testa della M4×50 entra in una sede esagonale profonda {n(Ta)} e non gira; dall'altra parte il dado è chiuso nel pomello. Girando il pomello le orecchie si flettono un poco e serrano la nocca. Il pacco è {n(C['pacco_cerniera_mm'])} mm, la vite sporge {n(C['vite_cerniera_filetto_oltre_il_dado_mm'])} mm oltre il dado e resta nascosta nel pomello.</p>" + svg},
            {"title": "Sezione del braccio", "html": "<p>Ogni tratto (guaina e prolunghe) ha il canale con una fessura davanti; ogni barra (prolunghe e slitta) ha sotto una nervatura che corre nella fessura e arriva a filo. La morsa è una vite M4 nel rinforzo sul fianco: la punta preme nella scanalatura della barra, che finisce prima del fondo e fa da fermo.</p>" + svg2},
            {"title": "Stabilità", "html": f"<p>Con un telefono da 200 g, braccio a {n(pz['alfa'], 0)}° e appoggio in basso il baricentro cade {n(C['telefono_baricentro_x_uso_mm'], 0)} mm dentro la base; con l'appoggio tutto in alto e il braccio a {n(pz['alfa'], 0)}° cadrebbe fuori ({n(C['telefono_baricentro_x_uso_appoggio_in_alto_mm'])} mm), col braccio dritto torna dentro ({n(C['telefono_baricentro_x_dritto_appoggio_in_alto_mm'])} mm). Con le prolunghe tieni il braccio dritto: il peso resta sopra la base, ma ogni grado di inclinazione sposta il telefono di più.</p>"},
            {"title": "Se la cerniera scivola", "html": "<p>Stringi il pomello. Se anche stretto non tiene (PETG molto liscio), metti una rondella di gomma o di sughero da 0,5–1 mm fra nocca e orecchia, oppure riduci <code>GIOCO_NOCCA</code> a 0,1 e ristampa. Non stringere con la chiave: le orecchie si aprono.</p>"}]},
 "files": {"h2": "I file.", "intro_html": "Gli STL sono in <code>stl/</code>; la scena e lo script che li genera in <code>blender/</code>. Nella scena le collezioni nascoste <b>CON_PROLUNGHE</b> e <b>PIEGATO</b> mostrano il supporto con due prolunghe e chiuso.",
  "links": [{"label": "README", "href": "README.md"}, {"label": "Scena Blender", "href": "blender/Supporto_Telefono.blend"},
            {"label": "Script di costruzione", "href": "blender/costruisci.py"}, {"label": "Misure e controlli", "href": "dati/geometria.json"},
            {"label": "Foto di riferimento", "href": "originale/foto_3.jpg"}]},
 "footer_html": "Guida offline: aprire questo file dalla cartella del progetto."
}
json.dump(spec, open(os.path.join(root, "dati", "guida_spec.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("ok", len(parts))
