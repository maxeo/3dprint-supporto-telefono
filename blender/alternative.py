"""Alternativa al pomello P06 della cerniera bassa (sulla base), per stringere meglio:
P13 galletto (pomello a farfalla) con le alette fuori dalla base.

Apre blender/Supporto_Telefono.blend (generato da costruisci.py), usa costanti e helper di costruisci.py,
monta il galletto al posto di P06 sulla cerniera bassa, controlla le interferenze aperto e piegato,
scrive gli STL, dati/alternative.json e blender/Supporto_Telefono_alternative.blend.
"""
import bpy, bmesh, math, json, os
import numpy as np
from mathutils import Matrix, Vector

try:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
except NameError:                                  # exec() dal Blender aperto
    ROOT = r"D:\3D Print\Supporto Telefono"
SRC = os.path.join(ROOT, "blender", "costruisci.py")
BLEND = os.path.join(ROOT, "blender", "Supporto_Telefono.blend")
if "P06_Pomello_montato" not in bpy.data.objects:
    bpy.ops.wm.open_mainfile(filepath=BLEND)

# costanti e helper di costruisci.py (senza svuotare la scena)
codice = open(SRC, encoding="utf-8").read()
STL = os.path.join(ROOT, "stl")
parti = [codice[codice.index("# --- misure"):codice.index("if bpy.app.background")],
         codice[codice.index("def obj_from_bm"):codice.index("\n# --- pezzi")],
         codice[codice.index("def k_r("):codice.index("\n\ndef pomello(")]]
sc = bpy.context.scene
exec(compile("\n".join(parti), SRC, "exec"))


def coll(name, hide=False):
    c = bpy.data.collections.get(name)
    if c:
        for o in list(c.objects):
            bpy.data.objects.remove(o)
    else:
        c = bpy.data.collections.new(name)
        sc.collection.children.link(c)
    c.hide_viewport = c.hide_render = hide
    return c


C_TMP = coll("TMP_ALT")
C_ALT = coll("ALTERNATIVE_STAMPA", True)
C_GAL = coll("GALLETTO_MONTATO")
for n in ("CAMMA_MONTATA",):                     # leva a camma scartata
    if n in bpy.data.collections:
        coll(n); bpy.data.collections.remove(bpy.data.collections[n])


VITE_PUNTA = L_CERN - Y_OUT - (Y_OUT + 0.05)      # punta della vite oltre la faccia del pomello (8,55)
# la cerniera bassa sta nell'incavo della base (raggio K_R + K_A + 0,6): ciò che è più largo va oltre il bordo
# della base, e lì il tavolo è a AX_A[1] dall'asse
Z_BORDO = B_W / 2 - (Y_OUT + 0.05) + 0.5         # oltre questa quota (dalla faccia dell'orecchia) si è fuori dalla base
R_MAX = AX_A[1] - 1.0                            # raggio massimo fuori dalla base (tavolo)
pz = {}

# P13 · galletto: mozzo zigrinato come P06 ma lungo fino al bordo della base, alette fuori dalla base
G_SP = 8.0
ga, gb = 9.0, Z_BORDO - 2.1                      # le alette partono a 45° dal mozzo: raggio 11,1 a Z_BORDO
G_HUB = gb + 3.0
G_ALA = [(-R_MAX, gb + R_MAX - ga), (-ga, gb), (ga, gb), (R_MAX, gb + R_MAX - ga), (R_MAX, gb + R_MAX - ga + 3),
         (12, gb + R_MAX - ga + 4), (0, gb + R_MAX - ga + 2), (-12, gb + R_MAX - ga + 4), (-R_MAX, gb + R_MAX - ga + 3)]
gal = radial_solid(lambda t, z: k_r(t, z, G_HUB), 0, G_HUB, "P13_Galletto", C_TMP, seg=144, dz=0.25)
boolean(gal, extrude(G_ALA, -G_SP / 2, G_SP / 2, "Y", "ala"), 'UNION')
boolean(gal, extrude(circ(0, 0, R_MAX, 144), -1, 60, "Z", "tavolo"), 'INTERSECT')   # punte rifilate: non toccano il tavolo
gal_pieno = gal.copy(); gal_pieno.data = gal.data.copy(); C_TMP.objects.link(gal_pieno)   # per i controlli da piegato
boolean(gal, madrevite(D_CERN, -0.5, K_H_MV - FONDO_POMELLO, "mv"), 'DIFFERENCE')
pz["P13_Galletto"] = (gal, Matrix())

MAT = {"P13": (0.95, 0.75, 0.15)}
for n, (o, mp) in pz.items():
    move_to(o, C_ALT)
    paint(o, mat("M_" + n, MAT[n[:3]]))

# --- montaggio al posto di P06 sulla cerniera bassa (stessa fase del filetto)
for n in ("PEZZI_MONTATI", "PIEGATO"):            # nelle collezioni nascoste matrix_world non è aggiornata
    bpy.data.collections[n].hide_viewport = False
bpy.context.view_layer.update()
Mk = bpy.data.objects["P06_Pomello_montato"].matrix_world.copy()
Mp = bpy.data.objects["P06_Pomello_piegato"].matrix_world.copy()


def copia(n, m, c, nome):
    o = bpy.data.objects.new(nome, pz[n][0].data)
    o.matrix_world = m
    c.objects.link(o)
    return o


gal_m = copia("P13_Galletto", Mk, C_GAL, "P13_Galletto_montato")
bpy.context.view_layer.update()


def tocca(a, b):
    def bb(o):
        co = [o.matrix_world @ Vector(v) for v in o.bound_box]
        return [(min(c[i] for c in co), max(c[i] for c in co)) for i in range(3)]
    ba, bb_ = bb(a), bb(b)
    return all(ba[i][0] < bb_[i][1] and bb_[i][0] < ba[i][1] for i in range(3))


def urti(nuovi, altri):
    out = {}
    for a in nuovi:
        for b in altri:
            if a is not b and tocca(a, b):
                v = interference(a, b)
                if v > 0.05:
                    out[f"{a.name}+{b.name}"] = v
    return out


montati = [o for o in bpy.data.collections["PEZZI_MONTATI"].objects if o.name != "P06_Pomello_montato"]
ctrl = {"galletto_fuori_dalla_base_da_mm": round(Z_BORDO, 2), "raggio_massimo_fuori_mm": R_MAX,
        "galletto_aperto_mm3": urti([gal_m], montati)}

# piegato: il galletto può restare girato in ogni modo, quindi si prova ogni 45° (senza la vite P08, che ha la sua fase)
piegati = [o for o in bpy.data.collections["PIEGATO"].objects if not o.name.startswith(("P06_Pomello_piegato", "P08_Vite_Cerniera_piegato"))]
liberi_g = []
prova = bpy.data.objects.new("prova", gal_pieno.data); C_TMP.objects.link(prova)
for phi in range(0, 360, 45):
    m = Mp @ Matrix.Rotation(math.radians(phi), 4, 'Z')
    prova.matrix_world = m
    bpy.context.view_layer.update()
    if not urti([prova], piegati):
        liberi_g.append(phi)
ctrl["piegato_galletto_angoli_liberi"] = liberi_g
ctrl["galletto_vite_spazio_in_fondo_mm"] = round(K_H_MV - FONDO_POMELLO - VITE_PUNTA, 2)
for o in (prova, gal_pieno):
    bpy.data.objects.remove(o)

geo = {"controlli": ctrl, "pezzi": {}}
for n, (o, mp) in pz.items():
    bm = bmesh.new(); bm.from_mesh(o.data)                  # salda i vertici doppi lasciati dai booleani
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)
    bm.to_mesh(o.data); bm.free()
    write_stl(o, mp, os.path.join(STL, n + ".stl"))
    geo["pezzi"][n] = info(o)
json.dump(geo, open(os.path.join(ROOT, "dati", "alternative.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
bpy.data.collections.remove(C_TMP)
bpy.data.collections["PIEGATO"].hide_viewport = True
print("ALTERNATIVE", json.dumps(geo, ensure_ascii=False))
if bpy.app.background:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blender", "Supporto_Telefono_alternative.blend"))
