"""Scrive dati/guida_spec.json dalle misure di dati/geometria.json (lanciare dopo blender/costruisci.py)."""
import json, math, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
geo = json.load(open(os.path.join(root, "dati", "geometria.json"), encoding="utf-8"))
P, C, MS, MO, V = geo["pezzi"], geo["controlli"], geo["misure"], geo["montaggio"], geo["viti"]


def n(x, d=1):
    s = f"{x:.{d}f}".replace(".", ",")
    return s[:-2] if s.endswith(",0") else s


def g(k):
    return n(P[k]["peso_PETG_g"], 0)


def part(id_, key, label, group, prof, note, mont=None):
    m = MO[mont or key]
    return {"id": id_, "label": label, "group": group, "file": f"stl/{key.split('.')[0]}.stl", "print": prof,
            "mode": "mesh", "max_triangles": 4000, "matrix": m["matrice"], "assembled_bounds": m["bounds"],
            "note_html": note}


pz = MS["posa_uso"]
parts = [
 part("P01", "P01_Base", "Base", "Base", "base",
      f"<p>Piastra {n(MS['base'][0])} × {n(MS['base'][1])} × {n(MS['base'][2])} con la forchetta della cerniera bassa: due orecchie da {n(MS['orecchia'])} mm, foro M4 e, sull'orecchia sinistra, la sede esagonale della testa della vite. Sotto quattro incavi Ø10,5 per piedini adesivi; sopra, a destra della forchetta, un incavo dove gira il pomello. {g('P01_Base')} g a pezzo pieno.</p>"),
 part("P02", "P02_Guaina", "Guaina del braccio", "Braccio", "braccio",
      f"<p>Tubo {n(MS['guaina'][1])} × {n(MS['guaina'][2])} lungo {n(MS['guaina'][0])} mm dall'asse, con la nocca in fondo e il canale {n(MS['canale'][0])} × {n(MS['canale'][1])} per la slitta. Sul fianco destro il rinforzo con la sede del dado M4 della vite di blocco. {g('P02_Guaina')} g.</p>"),
 part("P03", "P03_Slitta", "Slitta del braccio", "Braccio", "braccio",
      f"<p>Barra {n(MS['slitta'][1])} × {n(MS['slitta'][2])} ({n(MS['gioco_slitta_per_lato'])} mm di gioco per lato nel canale) con la testa e la nocca della cerniera alta. Sul fianco destro una scanalatura dove punta la vite di blocco: fa anche da fermo, la slitta esce al massimo di {n(C['sfilo_massimo_mm'])} mm. {g('P03_Slitta')} g.</p>"),
 part("P04", "P04_Piatto", "Piatto", "Piatto", "piatto",
      f"<p>Piatto {n(MS['piatto'][0])} × {n(MS['piatto'][1])} × {n(MS['piatto'][2])} su cui appoggia il telefono, con la forchetta della cerniera alta sul dorso ({n(MS['asse_piatto_dal_dorso'])} mm dall'asse al dorso) e due fori M3 svasati in basso per l'appoggio. {g('P04_Piatto')} g.</p>"),
 part("P05", "P05_Appoggio", "Appoggio", "Piatto", "appoggio",
      f"<p>Mensola sotto il bordo del piatto con la sponda davanti: tiene telefoni spessi fino a {n(MS['telefono_max'])} mm con la cover. Due linguette dietro il piatto con le sedi dei dadi M3, e un'asola in mezzo per il cavo di ricarica. {g('P05_Appoggio')} g.</p>"),
 part("P06A", "P06_Pomello", "Pomello · cerniera bassa", "Pomelli", "pomelli",
      f"<p>Pomello zigrinato Ø{n(MS['pomello_diametro'])} con il dado M4 premuto nella sede: girandolo stringi le orecchie della base sulla nocca del braccio. {g('P06_Pomello')} g.</p>", "P06_Pomello"),
 part("P06B", "P06_Pomello", "Pomello · blocco della slitta", "Pomelli", "pomelli",
      "<p>Stesso pomello, ma con la <b>testa</b> della vite M4×12 nella sede: è la manopola che blocca lo sfilo del braccio.</p>", "P06_Pomello.3"),
 part("P06C", "P06_Pomello", "Pomello · cerniera alta", "Pomelli", "pomelli",
      "<p>Stesso pomello col dado M4: regola la durezza della cerniera del piatto.</p>", "P06_Pomello.2"),
]

items = []
for a, b, k in (("P01", "P02", "M4x50_cerniera"), ("P03", "P04", "M4x50_cerniera.2"), ("P02", "P03", "M4x12_blocco"),
                ("P04", "P05", "M3x10_appoggio"), ("P04", "P05", "M3x10_appoggio.2")):
    v = V[k]
    items.append({"a": a, "b": b, "p": v["centro"], "axis": v["asse"], "length": v["lunghezza"], "diameter": v["diametro"]})

a = math.radians(pz["alfa"]); s_dir = math.radians(90 + pz["piatto_dalla_verticale"])
braccio = [round(math.cos(a), 3), 0, round(math.sin(a), 3)]
sotto_piatto = [round(-math.cos(s_dir), 3), 0, round(-math.sin(s_dir), 3)]
davanti_piatto = [round(math.cos(s_dir - math.pi / 2), 3), 0, round(math.sin(s_dir - math.pi / 2), 3)]

# sezione della cerniera (vista dall'alto, asse orizzontale), 4 px/mm
Yo, Yi, Ta = MS["nocca"] / 2 + MS["gioco_nocca_per_lato"] + MS["orecchia"], MS["nocca"] / 2 + MS["gioco_nocca_per_lato"], 3.0
S, X0 = 6.0, 230.0
def X(y): return X0 + y * S
svg = (f"<svg viewBox='0 0 460 200' xmlns='http://www.w3.org/2000/svg' font-size='11' font-family='sans-serif'>"
       f"<rect x='{X(-Yo)}' y='40' width='{MS['orecchia'] * S}' height='120' fill='#bfc3c9'/>"
       f"<rect x='{X(Yi)}' y='40' width='{MS['orecchia'] * S}' height='120' fill='#bfc3c9'/>"
       f"<rect x='{X(-MS['nocca'] / 2)}' y='40' width='{MS['nocca'] * S}' height='120' fill='#8aa1b8'/>"
       f"<rect x='{X(-Yo + Ta - 2.8)}' y='79' width='{2.8 * S}' height='42' fill='#777'/>"
       f"<rect x='{X(-Yo + Ta)}' y='88' width='{50 * S if 50 * S < 400 else 0}' height='24' fill='#999' opacity='.85'/>"
       f"<rect x='{X(Yo)}' y='30' width='{11 * S}' height='140' fill='#333' rx='6'/>"
       f"<rect x='{X(Yo)}' y='79' width='{3.2 * S}' height='42' fill='#777'/>"
       f"<text x='{X(-Yo)}' y='185'>orecchia {n(MS['orecchia'])}</text>"
       f"<text x='{X(-8)}' y='30'>nocca {n(MS['nocca'])}</text>"
       f"<text x='{X(-Yo)}' y='22'>testa M4 in sede da {n(Ta)}</text>"
       f"<text x='{X(Yo) - 10}' y='185'>pomello + dado</text>"
       f"<text x='{X(-6)}' y='185'>gioco {n(MS['gioco_nocca_per_lato'])} per lato</text>"
       f"</svg>")

pk = C["piegato_ingombro_mm"]
spec = {
 "root": "..", "output": "guida.html", "title": "Supporto Telefono · Guida",
 "theme": {"accent": "#2f6fa8", "viewer_bg": "#1b1f24"},
 "header": {
  "eyebrow": "Supporto Telefono · pieghevole da scrivania · PETG",
  "h1": "Sei pezzi, tre pomelli, si chiude piatto.",
  "intro_html": f"<b>Supporto per telefono da scrivania, pieghevole, con braccio telescopico e due cerniere a frizione.</b> Come quello della foto, ma stampato: le cerniere sono viti M4 che passano in una forchetta e si stringono con un pomello zigrinato, così regoli la durezza a mano e la riprendi quando si allenta. Lo sfilo del braccio si blocca con un terzo pomello. In più rispetto all'originale: un'asola per il cavo di ricarica nella mensola, gli incavi per i piedini in gomma e la scanalatura che impedisce alla slitta di uscire.",
  "facts": [{"value": f"{n(pk[0][1] - pk[0][0], 0)} × {n(pk[1][1] - pk[1][0], 0)} × {n(pk[2][1], 0)} mm", "label": "chiuso"},
            {"value": f"+{n(C['sfilo_massimo_mm'], 0)} mm", "label": "sfilo del braccio"},
            {"value": f"≤ {n(MS['telefono_max'], 0)} mm", "label": "spessore del telefono con cover"},
            {"value": "M4 · M3", "label": "3 viti M4, 2 viti M3, 5 dadi"}]},
 "camera": {"yaw": -0.9, "pitch": 0.35},
 "caption": f"Il supporto aperto: braccio a {n(pz['alfa'], 0)}°, sfilato di {n(pz['sfilo'], 0)} mm, piatto inclinato di {n(pz['piatto_dalla_verticale'], 0)}°. In grigio le viti.",
 "model_note_html": f"<span class='badge'>Quote del modello</span><p>Aperto {n(C['uso_ingombro_mm'][2][1], 0)} mm di altezza nella posa della vista; la mensola sta a {n(C['mensola_altezza_dal_piano_mm'], 0)} mm dal tavolo. Con un telefono da 200 g il baricentro cade {n(C['telefono_baricentro_x_mm'])} mm davanti al bordo dietro della base. Chiuso: braccio sulla base, piatto sul braccio, {n(pk[2][1])} mm di spessore.</p>",
 "groups": {"Base": {"color": "#c9ccd1"}, "Braccio": {"color": "#7f9bb8"}, "Piatto": {"color": "#3f86c4"},
            "Pomelli": {"color": "#454a52"}},
 "parts": parts,
 "connectors": {"items": items, "label": "vite", "label_plural": "viti",
                "joint_labels": {"P01+P02": "cerniera bassa · M4×50", "P03+P04": "cerniera alta · M4×50",
                                 "P02+P03": "blocco dello sfilo · M4×12", "P04+P05": "appoggio · 2 × M3×10"}},
 "steps_section": {"eyebrow": "01 / Montaggio", "h2": "Dal braccio al piatto.",
  "intro_html": "Destra e sinistra guardando il supporto da davanti, dalla parte del telefono. Serve solo una chiave da 7 o una pinza per tenere i dadi mentre li spingi nelle sedi.",
  "start_html": "<h3>Prima i dadi.</h3><p>Spingi un dado M4 nella sede di due pomelli (P06A e P06C) e la testa della vite M4×12 nella sede del terzo (P06B): entrano un po' forzati, aiutati premendo su un tavolo. Se ballano, una goccia di colla.</p>"},
 "steps": [
  {"title": "Infila la slitta nella guaina", "short": "dall'alto", "text": "Infila la barra di P03 nel canale di P02, con la scanalatura dalla parte del rinforzo (a destra). Deve scorrere senza sforzo fino a che la testa batte sulla guaina.",
   "parts": ["P02", "P03"], "built": ["P02", "P03"], "moving": ["P03"], "dir": braccio, "travel": 80},
  {"title": "Vite di blocco", "short": "dado M4 + pomello", "text": "Spingi un dado M4 nella sede esagonale del rinforzo di P02, poi avvita il pomello P06B con la sua vite M4×12: la punta entra nella scanalatura della slitta. Stringi per bloccare lo sfilo, allenta di mezzo giro per regolarlo. Non svitarlo del tutto: è anche il fermo che non fa uscire la slitta.",
   "parts": ["P02", "P03", "P06B"], "built": ["P02", "P03", "P06B"], "moving": ["P06B"], "dir": [0, 1, 0], "travel": 30, "joints": ["P02+P03"]},
  {"title": "Braccio sulla base", "short": "nocca nella forchetta", "text": "Cala la nocca in fondo a P02 fra le due orecchie di P01 e allinea i fori. Infila la vite M4×50 da sinistra: la testa esagonale entra nella sua sede e non gira più.",
   "parts": ["P01", "P02"], "built": ["P01", "P02", "P03", "P06B"], "moving": ["P02", "P03", "P06B"], "dir": [0, 0, 1], "travel": 70, "joints": ["P01+P02"]},
  {"title": "Pomello della cerniera bassa", "short": "da destra", "text": "Avvita P06A sulla vite che sporge a destra. Stringi finché il braccio resta fermo in ogni posizione ma si muove ancora con una mano.",
   "parts": ["P01", "P06A"], "built": ["P01", "P02", "P03", "P06B", "P06A"], "moving": ["P06A"], "dir": [0, 1, 0], "travel": 30},
  {"title": "Appoggio sul piatto", "short": "2 viti M3", "text": "Spingi i dadi M3 nelle sedi delle linguette di P05 e appoggia la mensola sotto il bordo basso di P04, con le linguette dietro. Avvita le due M3×10 dalla faccia del telefono: le teste scendono nei loro svasi e restano a filo.",
   "parts": ["P04", "P05"], "built": ["P04", "P05"], "moving": ["P05"], "dir": sotto_piatto, "travel": 40, "joints": ["P04+P05"]},
  {"title": "Piatto sulla testa del braccio", "short": "forchetta sulla nocca", "text": "Porta la forchetta sul dorso di P04 attorno alla nocca in cima a P03 e infila la seconda M4×50 da destra, con la testa nella sede.",
   "parts": ["P03", "P04"], "built": ["P01", "P02", "P03", "P06B", "P06A", "P04", "P05"], "moving": ["P04", "P05"], "dir": davanti_piatto, "travel": 60, "joints": ["P03+P04"]},
  {"title": "Pomello della cerniera alta", "short": "da sinistra", "text": "Avvita P06C sulla vite che sporge a sinistra e regola la durezza come per la cerniera bassa.",
   "parts": ["P04", "P06C"], "built": ["P01", "P02", "P03", "P06B", "P06A", "P04", "P05", "P06C"], "moving": ["P06C"], "dir": [0, -1, 0], "travel": 30},
  {"title": "Prova e regola", "short": "con il telefono", "text": f"Metti il telefono e controlla che non si pieghi da solo; se cede, stringi un po' i pomelli. Con un tablet o un telefono pesante non inclinare troppo indietro braccio e piatto: con il braccio a {n(pz['alfa'], 0)}° il baricentro resta {n(C['telefono_baricentro_x_mm'], 0)} mm dentro la base. Per chiuderlo: slitta dentro, piatto sul braccio, braccio sulla base.",
   "parts": ["P01", "P02", "P03", "P04", "P05", "P06A", "P06B", "P06C"]}
 ],
 "print": {"eyebrow": "03 / Stampa", "h2": "Sei file, otto stampe.",
  "common_html": "<b>Profilo comune:</b> Kobra S1, ugello 0,4 mm, PETG, strato 0,20 mm. Sono parametri che <b>propongo io, da verificare</b>: il supporto non è ancora stato stampato. STL in millimetri, scala 100%, già orientati e appoggiati a Z = 0. Nessun pezzo ha bisogno di supporti. I pesi indicati sono a pezzo pieno: col riempimento consigliato vengono meno.",
  "profiles": [
   {"key": "base", "title": "P01 · base", "rows": [["Orientamento", "piastra sul piatto, orecchie in su"], ["Pareti", "4"], ["Riempimento", "40% Gyroid"], ["Supporti", "no"]],
    "why": "La base fa da contrappeso: più è piena, meno il supporto si ribalta con un telefono pesante. Le sedi esagonali sui fianchi hanno un vertice in alto, così il cielo si chiude senza supporti.",
    "summary": "4 pareti · 40% · senza supporti"},
   {"key": "braccio", "title": "P02 guaina · P03 slitta", "rows": [["Orientamento", "lato largo sul piatto (come negli STL)"], ["Pareti", "4"], ["Riempimento", "30%"], ["Supporti", "no: il cielo del canale è un ponte di 24 mm"], ["Compensazione zampa d'elefante", "0,15 mm"]],
    "why": f"Coricati, i pezzi hanno le fibre lungo il braccio, che è la direzione in cui lavora. La slitta ha {n(MS['gioco_slitta_per_lato'])} mm di gioco per lato: la compensazione del primo strato evita che lo spigolo allargato la faccia impuntare.",
    "summary": "coricati · 4 pareti · 30%"},
   {"key": "piatto", "title": "P04 · piatto", "rows": [["Orientamento", "faccia del telefono sul piatto, forchetta in su"], ["Pareti", "4"], ["Riempimento", "25%"], ["Supporti", "no"]],
    "why": "La faccia su cui appoggia il telefono viene liscia dal piatto di stampa; gli svasi delle viti M3 sono aperti verso il piatto, quindi si stampano senza ponti.",
    "summary": "faccia giù · 4 pareti · 25%"},
   {"key": "appoggio", "title": "P05 · appoggio", "rows": [["Orientamento", "mensola sul piatto, sponda e linguette in su"], ["Pareti", "4"], ["Riempimento", "40%"], ["Supporti", "no"]],
    "why": "Di fianco la mensola diventa una U aperta in alto: sponda e linguette salgono dritte e i fori M3 restano orizzontali e piccoli.",
    "summary": "4 pareti · 40%"},
   {"key": "pomelli", "title": "P06 · pomelli", "rows": [["Orientamento", "faccia con la sede esagonale sul piatto"], ["Pareti", "4"], ["Riempimento", "50%"], ["Copie", "3"]],
    "why": "La sede esagonale stampata a contatto col piatto viene precisa e tiene il dado a pressione.",
    "summary": "3 copie · 50%"}],
  "extra_rows": [{"label": "Viteria (si compra)", "what": "cerniere", "file": "", "quantity": 2, "dims": "M4×50 testa esagonale + dado M4", "print": ""},
                 {"label": "Viteria (si compra)", "what": "blocco", "file": "", "quantity": 1, "dims": "M4×12 testa esagonale + dado M4", "print": ""},
                 {"label": "Viteria (si compra)", "what": "appoggio", "file": "", "quantity": 2, "dims": "M3×10 testa cilindrica + dado M3", "print": ""},
                 {"label": "Piedini adesivi (facoltativi)", "what": "base", "file": "", "quantity": 4, "dims": "Ø10 × 1 mm", "print": ""}],
  "note_html": f"Le misure da cambiare sono in cima a <code>blender/costruisci.py</code>: <code>GIOCO_NOCCA</code> se le cerniere restano dure anche col pomello lento, <code>GIOCO_SLITTA</code> se la slitta scorre male, <code>TELEFONO_MAX</code> per telefoni più spessi. Lo script ricontrolla che nessun pezzo si tocchi, aperto e chiuso, e lo scrive in <code>dati/geometria.json</code>."},
 "notes": {"eyebrow": "04 / La cerniera", "h2": "Una vite, un pomello, la frizione la scegli tu.", "nav": "Cerniera",
  "cards": [{"title": "Sezione della cerniera", "html": f"<p>La nocca larga {n(MS['nocca'])} sta fra due orecchie con {n(MS['gioco_nocca_per_lato'])} mm di gioco per lato. La testa della M4×50 entra in una sede esagonale profonda {n(Ta)} e non gira; dall'altra parte il dado è chiuso nel pomello. Girando il pomello le orecchie si flettono un poco e serrano la nocca: è questa pressione a tenere il braccio. Il pacco è {n(C['pacco_cerniera_mm'])} mm, la vite sporge {n(C['vite_cerniera_filetto_oltre_il_dado_mm'])} mm oltre il dado e resta nascosta nel pomello.</p>" + svg},
            {"title": "Se la cerniera scivola", "html": "<p>Stringi il pomello. Se anche stretto non tiene (PETG molto liscio), metti una rondella di gomma o di sughero da 0,5–1 mm fra nocca e orecchia, oppure riduci <code>GIOCO_NOCCA</code> a 0,1 e ristampa la base. Non stringere con la chiave: le orecchie si aprono.</p>"}]},
 "files": {"h2": "I file.", "intro_html": "Gli STL sono in <code>stl/</code>; la scena e lo script che li genera in <code>blender/</code>. Nella scena la collezione <b>PIEGATO</b> (nascosta) mostra il supporto chiuso.",
  "links": [{"label": "README", "href": "README.md"}, {"label": "Scena Blender", "href": "blender/Supporto_Telefono.blend"},
            {"label": "Script di costruzione", "href": "blender/costruisci.py"}, {"label": "Misure e controlli", "href": "dati/geometria.json"},
            {"label": "Foto di riferimento", "href": "originale/foto_3.jpg"}]},
 "footer_html": "Guida offline: aprire questo file dalla cartella del progetto."
}
json.dump(spec, open(os.path.join(root, "dati", "guida_spec.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("ok", len(parts))
