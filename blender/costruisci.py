"""Supporto Telefono · supporto pieghevole da scrivania con braccio telescopico e cerniere a frizione.

Uso (dalla cartella del progetto):
    blender -b --factory-startup --python blender/costruisci.py
oppure nel Blender aperto, via MCP: exec(open(r"D:\\3D Print\\Supporto Telefono\\blender\\costruisci.py", encoding="utf-8").read())

Scrive blender/Supporto_Telefono.blend, gli STL in stl/ (già orientati per la stampa) e dati/geometria.json.
Coordinate di montaggio: base sul piano Z = 0, X verso chi guarda il telefono (davanti), Y da sinistra a destra.
Ogni pezzo è costruito nel suo riferimento:
  base       = mondo;
  braccio    = asse della cerniera bassa, u (X) lungo il braccio, v (Z) verso il dietro quando è in piedi;
  piatto     = asse della cerniera alta, X lungo il piatto verso l'alto, Z dall'asse verso la faccia del telefono;
  pomello    = asse Z, faccia d'appoggio a Z = 0.
"""
import bpy, bmesh, math, json, os
import numpy as np
from mathutils import Matrix, Vector

try:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
except NameError:                                  # exec() dal Blender aperto
    ROOT = r"D:\3D Print\Supporto Telefono"
STL = os.path.join(ROOT, "stl")
os.makedirs(STL, exist_ok=True)
os.makedirs(os.path.join(ROOT, "dati"), exist_ok=True)

# --- misure (mm) ----------------------------------------------------------
SEG = 96
# viteria (si compra): M4 per cerniere e blocco, M3 per l'appoggio
D_M4 = 4.4                 # foro passante M4
AF_M4_TESTA = 7.3          # sede esagonale della testa M4 (chiave 7) nella forchetta: non gira
AF_M4_DADO = 7.1           # dado M4 nel pomello: entra un po' forzato
H_DADO_M4 = 3.4
D_M3, AF_M3, H_DADO_M3 = 3.4, 5.8, 2.6
D_TESTA_M3, H_TESTA_M3 = 6.2, 3.2   # svaso per la testa cilindrica M3

# cerniere: forchetta (due orecchie) + nocca larga 30 in mezzo
NOCCA = 30.0               # larghezza della nocca (braccio e testa della slitta)
GIOCO_NOCCA = 0.2          # per lato: il bullone stringe le orecchie sulla nocca
ORECCHIA = 9.0             # spessore di ogni orecchia
Y_IN = NOCCA / 2 + GIOCO_NOCCA          # 15,2
Y_OUT = Y_IN + ORECCHIA                 # 24,2
TASCA = 3.0                # profondità della sede della testa nell'orecchia

# base
B_L, B_W, B_T, B_R = 175.0, 90.0, 7.0, 12.0
AX_A = (30.0, 17.5)        # asse della cerniera bassa (x, z): il braccio piegato sta 0,5 sopra la base
R_ORECCHIA_A = 10.0
PIEDINI = [(15, 32), (15, -32), (160, 32), (160, -32)]
D_PIEDINO, H_PIEDINO = 10.5, 1.0

# braccio: guaina (P02) e slitta (P03)
G_L, G_T = 100.0, 20.0     # lunghezza dall'asse, spessore (la larghezza è NOCCA)
CANALE_Y, CANALE_V, CANALE_U0 = 24.0, 15.0, 12.0
GIOCO_SLITTA = 0.3         # per lato
S_Y, S_V = CANALE_Y - 2 * GIOCO_SLITTA, CANALE_V - 2 * GIOCO_SLITTA   # 23,4 × 14,4
S_U0 = 15.0                # fondo della barra a braccio chiuso
TESTA_L = 12.0             # testa della slitta sopra la guaina
AX_C_V = (10.0 - S_V / 2) / 2           # 1,4: centro della nocca alta (testa da -7,2 a +10)
R_NOCCA_C = (10.0 + S_V / 2) / 2        # 8,6
AX_C_U = G_L + TESTA_L                   # 112: asse della cerniera alta a braccio chiuso
BLOCCO_U, BLOCCO_V = 85.0, 3.0          # vite di blocco sul fianco +y della guaina
PAD = (78.0, 92.0, 4.0)                  # rinforzo sul fianco: da u, a u, sporgenza
SCANALATURA = (45.0, 98.0, 5.2, 1.0)     # sulla slitta: da u, a u, larghezza, profondità
E_MAX = BLOCCO_U - SCANALATURA[0]        # 40: oltre, la vite batte in fondo alla scanalatura

# piatto (P04) e appoggio (P05), nel riferimento del piatto
P_X0, P_X1, P_W, P_T, P_R = -25.0, 125.0, 80.0, 6.0, 8.0
P_DIST = 14.0              # dall'asse al dorso del piatto
R_ORECCHIA_C = 9.0
TELEFONO_MAX = 14.0        # spessore massimo del telefono con cover
FORI_APPOGGIO = [(-20.0, 26.0), (-20.0, -26.0)]

# pomello (P06)
K_R, K_LOBI, K_A, K_H = 10.3, 12, 0.7, 11.0

# pose della scena
ALFA_USO, E_USO, TILT_USO = 95.0, 20.0, 20.0     # braccio da +X, sfilo, inclinazione del piatto dalla verticale
TELEFONO = (160.0, 75.0, 9.0, 200.0)              # alto, largo, spesso, grammi (per il baricentro)

if bpy.app.background:
    bpy.ops.wm.read_factory_settings(use_empty=True)
else:                                               # nel Blender aperto: svuota senza ricaricare (l'addon MCP resta vivo)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    for blocks in (bpy.data.meshes, bpy.data.materials, bpy.data.collections):
        for b in list(blocks):
            blocks.remove(b)
sc = bpy.context.scene
sc.unit_settings.scale_length = 0.001
sc.unit_settings.length_unit = 'MILLIMETERS'


def coll(name, hide=False):
    c = bpy.data.collections.new(name)
    sc.collection.children.link(c)
    c.hide_viewport = c.hide_render = hide
    return c


C_STAMPA, C_MONT, C_PIEG = coll("PEZZI_STAMPA", True), coll("PEZZI_MONTATI"), coll("PIEGATO", True)
C_TMP = coll("TMP")


def obj_from_bm(bm, name, c):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    c.objects.link(o)
    return o


def boolean(target, tool, op, tolerant=False):
    m = target.modifiers.new("b", 'BOOLEAN')
    m.operation, m.object, m.solver = op, tool, 'EXACT'
    m.use_hole_tolerant = tolerant
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(tool)


def arc(cx, cy, r, a0, a1, n=None, ends=True):
    """Punti di un arco (gradi). ends=False toglie gli estremi (già nel poligono)."""
    n = n or max(4, int(abs(a1 - a0) / 5))
    a = np.linspace(a0, a1, n + 1)
    if not ends:
        a = a[1:-1]
    return [(cx + r * math.cos(math.radians(t)), cy + r * math.sin(math.radians(t))) for t in a]


def circ(cx, cy, r, n=64):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def hexa(cx, cy, af):
    """Esagono (chiave af) con un vertice in alto: nelle sedi orizzontali il cielo si stampa senza supporti."""
    r = af / math.sqrt(3)
    return [(cx + r * math.cos(math.radians(90 + 60 * k)), cy + r * math.sin(math.radians(90 + 60 * k))) for k in range(6)]


def rrect(x0, x1, y0, y1, r):
    p = []
    for cx, cy, a in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        p += arc(cx, cy, r, a, a + 90, 6)
    return p


def box(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def extrude(poly, a0, a1, axis, name, c=None):
    """Poligono (p, q) estruso da a0 ad a1 lungo l'asse: Z → (p, q, h); Y → (p, h, q); X → (h, p, q)."""
    bm = bmesh.new()
    def V(p, q, h):
        return bm.verts.new({"Z": (p, q, h), "Y": (p, h, q), "X": (h, p, q)}[axis])
    bot = [V(p, q, a0) for p, q in poly]
    top = [V(p, q, a1) for p, q in poly]
    bm.faces.new(bot[::-1]); bm.faces.new(top)
    for i in range(len(poly)):
        j = (i + 1) % len(poly)
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(bm, name, c or C_TMP)


def radial_solid(rfun, z0, z1, name, c, seg=SEG, dz=0.1):
    """Solido chiuso con raggio r(theta, z)."""
    bm = bmesh.new()
    nz = max(2, int(round((z1 - z0) / dz)) + 1)
    rings = []
    for k in range(nz):
        z = z0 + (z1 - z0) * k / (nz - 1)
        rings.append([bm.verts.new((rfun(t, z) * math.cos(t), rfun(t, z) * math.sin(t), z))
                      for t in (2 * math.pi * i / seg for i in range(seg))])
    for k in range(nz - 1):
        a, b = rings[k], rings[k + 1]
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new((a[i], a[j], b[j], b[i]))
    cb = bm.verts.new((0, 0, z0)); ct = bm.verts.new((0, 0, z1))
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((cb, rings[0][j], rings[0][i]))
        bm.faces.new((ct, rings[-1][i], rings[-1][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(bm, name, c)


def mat(name, rgb, metal=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs[0].default_value = (*rgb, 1)
    for inp in bsdf.inputs:
        if inp.identifier == "Metallic":
            inp.default_value = metal
        elif inp.identifier == "Roughness":
            inp.default_value = 0.35
    return m


def paint(o, m):
    o.data.materials.clear(); o.data.materials.append(m)


def move_to(o, c):
    for cc in list(o.users_collection):
        cc.objects.unlink(o)
    c.objects.link(o)


def info(o):
    bm = bmesh.new(); bm.from_mesh(o.data)
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    vol = bm.calc_volume(signed=True)
    bm.free()
    co = [o.matrix_world @ v.co for v in o.data.vertices]
    mn = [min(c[i] for c in co) for i in range(3)]; mx = [max(c[i] for c in co) for i in range(3)]
    return {"min": [round(a, 2) for a in mn], "max": [round(a, 2) for a in mx],
            "size": [round(b - a, 2) for a, b in zip(mn, mx)], "volume_mm3": round(vol),
            "peso_PETG_g": round(vol * 1.27e-3, 1), "non_manifold_edges": nm}


def interference(a, b):
    """Volume (mm³) dell'intersezione fra due oggetti nella loro posa: deve essere 0."""
    c = a.copy(); c.data = a.data.copy(); sc.collection.objects.link(c)
    d = b.copy(); d.data = b.data.copy(); sc.collection.objects.link(d)
    boolean(c, d, 'INTERSECT')
    bm = bmesh.new(); bm.from_mesh(c.data); v = abs(bm.calc_volume()); bm.free()
    me = c.data
    bpy.data.objects.remove(c); bpy.data.meshes.remove(me)
    return round(v, 2)


def write_stl(o, mp, path):
    """STL binario scritto dalla mesh con la matrice di stampa mp (funziona anche col Blender aperto)."""
    import struct
    me = o.data
    me.calc_loop_triangles()
    rot = mp.to_3x3()
    with open(path, "wb") as f:
        f.write(os.path.basename(ROOT).encode("ascii", "replace")[:80].ljust(80, b" "))
        f.write(struct.pack("<I", len(me.loop_triangles)))
        for t in me.loop_triangles:
            f.write(struct.pack("<3f", *(rot @ t.normal).normalized()))
            for vi in t.vertices:
                f.write(struct.pack("<3f", *(mp @ me.vertices[vi].co)))
            f.write(b"\0\0")


def T(x, y, z):
    return Matrix.Translation((x, y, z))


def Ry(deg):
    return Matrix.Rotation(math.radians(deg), 4, 'Y')


def Rx(deg):
    return Matrix.Rotation(math.radians(deg), 4, 'X')


def forcella(name, poly_xz, ax_xz):
    """Due orecchie (y da Y_IN a Y_OUT e simmetrica) con il foro M4 e, sull'orecchia -y, la sede della testa."""
    o = extrude(poly_xz, Y_IN, Y_OUT, "Y", name)
    boolean(o, extrude(poly_xz, -Y_OUT, -Y_IN, "Y", "o2"), 'UNION')
    return o


def fora_cerniera(o, ax_xz):
    boolean(o, extrude(circ(*ax_xz, D_M4 / 2, 32), -Y_OUT - 1, Y_OUT + 1, "Y", "foro"), 'DIFFERENCE')
    boolean(o, extrude(hexa(*ax_xz, AF_M4_TESTA), -Y_OUT - 1, -Y_OUT + TASCA, "Y", "testa"), 'DIFFERENCE')


# --- pezzi ------------------------------------------------------------------
geo = {"misure": {}, "pezzi": {}, "controlli": {}}
pieces = {}                                          # nome -> (oggetto nel suo riferimento, matrice di stampa)
M = {"P01": mat("M_P01", (0.86, 0.86, 0.88)), "P02": mat("M_P02", (0.55, 0.64, 0.74)),
     "P03": mat("M_P03", (0.93, 0.93, 0.93)), "P04": mat("M_P04", (0.30, 0.55, 0.78)),
     "P05": mat("M_P05", (0.95, 0.55, 0.20)), "P06": mat("M_P06", (0.20, 0.20, 0.23)),
     "VITE": mat("M_viteria", (0.62, 0.62, 0.65), metal=0.9)}

# P01 · base
base = extrude(rrect(0, B_L, -B_W / 2, B_W / 2, B_R), 0, B_T, "Z", "P01_Base")
ear_a = [(AX_A[0] - R_ORECCHIA_A, 0.5), (AX_A[0] + R_ORECCHIA_A, 0.5)] + arc(*AX_A, R_ORECCHIA_A, 0, 180, 36)
boolean(base, forcella("forcA", ear_a, AX_A), 'UNION')
fora_cerniera(base, AX_A)
# incavo sotto il pomello della cerniera (lato +y): il pomello scende sotto il piano della base
boolean(base, extrude(circ(*AX_A, K_R + K_A + 0.6, 64), Y_OUT + 0.2, B_W, "Y", "incavo"), 'DIFFERENCE')
cut = None
for x, y in PIEDINI:
    t = extrude(circ(x, y, D_PIEDINO / 2, 48), -1, H_PIEDINO, "Z", "piede")
    if cut:
        boolean(cut, t, 'UNION')
    else:
        cut = t
boolean(base, cut, 'DIFFERENCE')
pieces["P01_Base"] = (base, Matrix())

# P02 · guaina del braccio (riferimento braccio: u = X, y = Y, v = Z)
gp = [(0, -G_T / 2), (G_L, -G_T / 2), (G_L, G_T / 2), (0, G_T / 2)] + arc(0, 0, G_T / 2, 90, 270, 36, ends=False)
guaina = extrude(gp, -NOCCA / 2, NOCCA / 2, "Y", "P02_Guaina")
boolean(guaina, extrude(box(PAD[0], PAD[1], -G_T / 2 + 0.5, G_T / 2 - 0.5), NOCCA / 2 - 0.1, NOCCA / 2 + PAD[2], "Y", "pad"), 'UNION')
boolean(guaina, extrude(box(CANALE_U0, G_L + 1, -CANALE_V / 2, CANALE_V / 2), -CANALE_Y / 2, CANALE_Y / 2, "Y", "canale"), 'DIFFERENCE')
boolean(guaina, extrude(circ(0, 0, D_M4 / 2, 32), -NOCCA, NOCCA, "Y", "foro"), 'DIFFERENCE')
boolean(guaina, extrude(circ(BLOCCO_U, BLOCCO_V, D_M4 / 2, 32), 0, NOCCA, "Y", "foro_blocco"), 'DIFFERENCE')
Y_PAD = NOCCA / 2 + PAD[2]
boolean(guaina, extrude(hexa(BLOCCO_U, BLOCCO_V, AF_M4_DADO), Y_PAD - H_DADO_M4, Y_PAD + 1, "Y", "dado"), 'DIFFERENCE')
pieces["P02_Guaina"] = (guaina, T(0, 0, G_T / 2))

# P03 · slitta (stesso riferimento, braccio chiuso)
VB = -S_V / 2
slitta = extrude(box(S_U0, G_L + 1, VB, S_V / 2), -S_Y / 2, S_Y / 2, "Y", "P03_Slitta")
tp = [(G_L, VB), (AX_C_U, VB)] + arc(AX_C_U, AX_C_V, R_NOCCA_C, -90, 90, 36, ends=False) + [(AX_C_U, 10.0), (G_L, 10.0)]
boolean(slitta, extrude(tp, -NOCCA / 2, NOCCA / 2, "Y", "testa"), 'UNION')
su0, su1, sw, sd = SCANALATURA
boolean(slitta, extrude(box(su0, su1, BLOCCO_V - sw / 2, BLOCCO_V + sw / 2), S_Y / 2 - sd, S_Y / 2 + 1, "Y", "scanalatura"), 'DIFFERENCE')
boolean(slitta, extrude(circ(AX_C_U, AX_C_V, D_M4 / 2, 32), -NOCCA, NOCCA, "Y", "foro"), 'DIFFERENCE')
pieces["P03_Slitta"] = (slitta, T(0, 0, -VB))

# P04 · piatto (riferimento piatto)
PZ0, PZ1 = P_DIST, P_DIST + P_T
piatto = extrude(rrect(P_X0, P_X1, -P_W / 2, P_W / 2, P_R), PZ0, PZ1, "Z", "P04_Piatto")
ear_c = [(R_ORECCHIA_C, PZ0 + 0.5), (-R_ORECCHIA_C, PZ0 + 0.5), (-R_ORECCHIA_C, 0)] + \
        arc(0, 0, R_ORECCHIA_C, 180, 360, 36, ends=False) + [(R_ORECCHIA_C, 0)]
boolean(piatto, forcella("forcC", ear_c, (0, 0)), 'UNION')
fora_cerniera(piatto, (0, 0))
for x, y in FORI_APPOGGIO:
    boolean(piatto, extrude(circ(x, y, D_M3 / 2, 32), PZ0 - 1, PZ1 + 1, "Z", "f3"), 'DIFFERENCE')
    boolean(piatto, extrude(circ(x, y, D_TESTA_M3 / 2, 48), PZ1 - H_TESTA_M3, PZ1 + 1, "Z", "svaso"), 'DIFFERENCE')
pieces["P04_Piatto"] = (piatto, T(0, 0, PZ1) @ Rx(180))

# P05 · appoggio: mensola sotto il bordo del piatto, sponda davanti, due linguette avvitate dietro
SX0, SX1 = P_X0 - 4.0, P_X0                   # mensola: 4 mm sotto il bordo
Z_SPONDA = PZ1 + TELEFONO_MAX
lp = [(SX0, PZ0 - 0.1), (SX1, PZ0 - 0.1), (SX1, Z_SPONDA), (SX0 + 12, Z_SPONDA), (SX0 + 12, Z_SPONDA + 4), (SX0, Z_SPONDA + 4)]
LY = 35.0
appoggio = extrude(lp, -LY, LY, "Y", "P05_Appoggio")
for s in (1, -1):
    ys = sorted((s * 17.0, s * (LY - 0.2)))
    boolean(appoggio, extrude(box(SX0, -13.0, PZ0 - P_T, PZ0), ys[0], ys[1], "Y", "linguetta"), 'UNION')
for x, y in FORI_APPOGGIO:
    boolean(appoggio, extrude(circ(x, y, D_M3 / 2, 32), PZ0 - P_T - 1, PZ0 + 1, "Z", "f3"), 'DIFFERENCE')
    boolean(appoggio, extrude(hexa(x, y, AF_M3), PZ0 - P_T - 1, PZ0 - P_T + H_DADO_M3, "Z", "dado3"), 'DIFFERENCE')
boolean(appoggio, extrude(box(-8, 8, PZ1 + 2, Z_SPONDA - 2), SX0 - 1, SX1 + 1, "X", "cavo"), 'DIFFERENCE')
pieces["P05_Appoggio"] = (appoggio, T(0, 0, -SX0) @ Ry(-90))


# P06 · pomello: dado M4 (cerniere) o testa M4 (blocco) nella sede esagonale
def k_r(t, z):
    r = K_R + K_A * math.cos(K_LOBI * t)
    r -= max(0.0, z - (K_H - 1.5)) * 1.0          # smusso in cima
    r -= max(0.0, 0.4 - z)                        # niente zampa d'elefante
    return r


pomello = radial_solid(k_r, 0, K_H, "P06_Pomello", C_TMP, seg=144, dz=0.25)
boolean(pomello, extrude(hexa(0, 0, AF_M4_DADO), -1, H_DADO_M4, "Z", "sede"), 'DIFFERENCE')
boolean(pomello, extrude(circ(0, 0, 2.3, 32), H_DADO_M4 - 0.1, K_H - 2.0, "Z", "foro"), 'DIFFERENCE')
pieces["P06_Pomello"] = (pomello, Matrix())

for n, (o, mp) in pieces.items():
    move_to(o, C_STAMPA)
    paint(o, M[n[:3]])


# --- viteria (solo per la scena) ---------------------------------------------
def vite(name, L, dado_a=None, m=4):
    """Vite lungo +Z dalla battuta della testa (Z = 0): M4 a testa esagonale, M3 a testa cilindrica."""
    v = extrude(circ(0, 0, m / 2, 24), -0.01, L, "Z", name)
    testa = hexa(0, 0, 7.0) if m == 4 else circ(0, 0, 2.75, 24)
    boolean(v, extrude(testa, -2.8 if m == 4 else -3.0, 0.0, "Z", "t"), 'UNION')
    if dado_a is not None:
        af, h = (7.0, 3.2) if m == 4 else (5.5, 2.4)
        boolean(v, extrude(hexa(0, 0, af), dado_a, dado_a + h, "Z", "d"), 'UNION')
    paint(v, M["VITE"]); move_to(v, C_STAMPA)
    return v


L_CERNIERA = 50
SPESSORE_PACCO = 2 * Y_OUT
vite_cern = vite("M4x50_cerniera", L_CERNIERA, dado_a=SPESSORE_PACCO - TASCA)
vite_blocco = vite("M4x12_blocco", 12)
dado_blocco = extrude(hexa(0, 0, 7.0), 0, 3.2, "Z", "M4_dado_blocco"); paint(dado_blocco, M["VITE"]); move_to(dado_blocco, C_STAMPA)
vite_app = vite("M3x10_appoggio", 10, dado_a=2 * P_T - H_TESTA_M3 - H_DADO_M3, m=3)   # dado in fondo alla sede


# --- pose ----------------------------------------------------------------------
def pose(alfa, e, gamma):
    """Matrici dei pezzi: alfa = braccio da +X (gradi), e = sfilo, gamma = piatto rispetto al braccio."""
    braccio = T(AX_A[0], 0, AX_A[1]) @ Ry(-alfa)
    sl = braccio @ T(e, 0, 0)
    pia = sl @ T(AX_C_U, 0, AX_C_V) @ Ry(gamma) @ Rx(180)
    to_y = Rx(-90)                                       # Z del pomello → +Y
    gap_bl = S_Y / 2 - SCANALATURA[3] + 12 + 0.05        # faccia del pomello di blocco a vite in battuta
    return {
        "P01_Base": Matrix(), "P02_Guaina": braccio, "P03_Slitta": sl, "P04_Piatto": pia, "P05_Appoggio": pia,
        "P06_Pomello": T(AX_A[0], Y_OUT + 0.05, AX_A[1]) @ to_y,
        "P06_Pomello.2": pia @ T(0, Y_OUT + 0.05, 0) @ to_y,
        "P06_Pomello.3": braccio @ T(BLOCCO_U, gap_bl, BLOCCO_V) @ to_y,
        "M4x50_cerniera": T(AX_A[0], -Y_OUT + TASCA, AX_A[1]) @ to_y,
        "M4x50_cerniera.2": pia @ T(0, -Y_OUT + TASCA, 0) @ to_y,
        "M4x12_blocco": braccio @ T(BLOCCO_U, gap_bl, BLOCCO_V) @ Rx(90),
        "M4_dado_blocco": braccio @ T(BLOCCO_U, Y_PAD - H_DADO_M4 + 0.1, BLOCCO_V) @ to_y,
        "M3x10_appoggio": pia @ T(*FORI_APPOGGIO[0], PZ1 - H_TESTA_M3) @ Rx(180),
        "M3x10_appoggio.2": pia @ T(*FORI_APPOGGIO[1], PZ1 - H_TESTA_M3) @ Rx(180),
    }


def gamma_per(alfa, tilt):
    return -(90 + tilt - alfa)          # il piatto a (90 + tilt)° da +X, il braccio ad alfa


src = {**{n: o for n, (o, _) in pieces.items()},
       "M4x50_cerniera": vite_cern, "M4x12_blocco": vite_blocco, "M4_dado_blocco": dado_blocco, "M3x10_appoggio": vite_app}


def monta(c, mats, suffix):
    out = {}
    for k, mw in mats.items():
        o = bpy.data.objects.new(k.split(".")[0] + ("_" + k.split(".")[1] if "." in k else "") + suffix, src[k.split(".")[0]].data)
        o.matrix_world = mw
        c.objects.link(o)
        out[k] = o
    return out


G_USO = gamma_per(ALFA_USO, TILT_USO)
uso = monta(C_MONT, pose(ALFA_USO, E_USO, G_USO), "_montato")
pieg = monta(C_PIEG, pose(0.0, 0.0, 180.0), "_piegato")
bpy.context.view_layer.update()

# --- controlli -------------------------------------------------------------------
stampati = ["P01_Base", "P02_Guaina", "P03_Slitta", "P04_Piatto", "P05_Appoggio", "P06_Pomello", "P06_Pomello.2", "P06_Pomello.3"]
coppie = [("P01_Base", "P02_Guaina"), ("P02_Guaina", "P03_Slitta"), ("P03_Slitta", "P04_Piatto"),
          ("P04_Piatto", "P05_Appoggio"), ("P02_Guaina", "P04_Piatto"), ("P02_Guaina", "P05_Appoggio"),
          ("P03_Slitta", "P05_Appoggio"), ("P01_Base", "P06_Pomello"), ("P02_Guaina", "P06_Pomello"),
          ("P04_Piatto", "P06_Pomello.2"), ("P03_Slitta", "P06_Pomello.2"), ("P02_Guaina", "P06_Pomello.3"),
          ("P04_Piatto", "P06_Pomello.3"), ("P05_Appoggio", "P06_Pomello.3"), ("P06_Pomello.2", "P06_Pomello.3"),
          ("P01_Base", "P04_Piatto"), ("P01_Base", "P05_Appoggio"), ("P01_Base", "P06_Pomello.2"),
          ("P01_Base", "P06_Pomello.3"), ("P01_Base", "P03_Slitta")]
viti = [("P01_Base", "M4x50_cerniera"), ("P02_Guaina", "M4x50_cerniera"), ("P04_Piatto", "M4x50_cerniera.2"),
        ("P03_Slitta", "M4x50_cerniera.2"), ("P02_Guaina", "M4x12_blocco"), ("P03_Slitta", "M4x12_blocco"),
        ("P02_Guaina", "M4_dado_blocco"), ("P04_Piatto", "M3x10_appoggio"), ("P05_Appoggio", "M3x10_appoggio"),
        ("P06_Pomello", "M4x50_cerniera")]
ctrl = geo["controlli"]
ctrl["interferenze_uso_mm3"] = {f"{a}+{b}": interference(uso[a], uso[b]) for a, b in coppie}
ctrl["interferenze_piegato_mm3"] = {f"{a}+{b}": interference(pieg[a], pieg[b]) for a, b in coppie}
ctrl["viti_contro_pezzi_uso_mm3"] = {f"{a}+{b}": interference(uso[a], uso[b]) for a, b in viti}


def zmin(objs):
    return min((o.matrix_world @ v.co).z for o in objs for v in o.data.vertices)


def bounds(objs):
    co = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    return [[round(min(c[i] for c in co), 1), round(max(c[i] for c in co), 1)] for i in range(3)]


ctrl["piegato_ingombro_mm"] = bounds([pieg[k] for k in stampati])
ctrl["uso_ingombro_mm"] = bounds([uso[k] for k in stampati])
ctrl["sopra_il_piano_uso"] = round(zmin([uso[k] for k in stampati]), 2)
ctrl["sopra_il_piano_piegato"] = round(zmin([pieg[k] for k in stampati]), 2)

# baricentro del telefono appoggiato sulla mensola (a sfilo e angoli della scena)
mp = pose(ALFA_USO, E_USO, G_USO)["P04_Piatto"]
h, w, s, g = TELEFONO
com = mp @ Vector((P_X0 + h / 2, 0, PZ1 + s / 2))
ctrl["telefono_baricentro_x_mm"] = round(com.x, 1)
ctrl["telefono_margine_dal_bordo_dietro_mm"] = round(com.x, 1)
ctrl["mensola_altezza_dal_piano_mm"] = round((mp @ Vector((P_X0, 0, PZ1))).z, 1)
ctrl["sfilo_massimo_mm"] = E_MAX
ctrl["altezza_asse_alto_chiuso_dritto_mm"] = round(AX_A[1] + AX_C_U, 1)
ctrl["altezza_asse_alto_aperto_dritto_mm"] = round(AX_A[1] + AX_C_U + E_MAX, 1)
ctrl["pacco_cerniera_mm"] = round(SPESSORE_PACCO, 2)
ctrl["vite_cerniera_filetto_oltre_il_dado_mm"] = round(L_CERNIERA - (SPESSORE_PACCO - TASCA) - 3.2, 2)
ctrl["parete_guaina_sopra_canale_mm"] = round(G_T / 2 - CANALE_V / 2, 2)
ctrl["parete_tra_dado_blocco_e_canale_mm"] = round(Y_PAD - H_DADO_M4 - CANALE_Y / 2, 2)

# pose per la guida: rotazione dalla posa di stampa a quella d'uso, ingombro montato, viti come cilindri
p_uso = pose(ALFA_USO, E_USO, G_USO)
geo["montaggio"] = {}
for k in stampati:
    rot = (p_uso[k] @ pieces[k.split(".")[0]][1].inverted()).to_3x3()
    geo["montaggio"][k] = {"matrice": [[round(a, 6) for a in r] for r in rot], "bounds": bounds([uso[k]])}
geo["viti"] = {}
for k, L in (("M4x50_cerniera", L_CERNIERA), ("M4x50_cerniera.2", L_CERNIERA), ("M4x12_blocco", 12),
             ("M3x10_appoggio", 10), ("M3x10_appoggio.2", 10)):
    mw = p_uso[k]
    d = (mw.to_3x3() @ Vector((0, 0, 1))).normalized()
    c = mw @ Vector((0, 0, 0)) + d * (L / 2)
    geo["viti"][k] = {"centro": [round(a, 2) for a in c], "asse": [round(a, 4) for a in d], "lunghezza": L,
                      "diametro": 3.0 if k.startswith("M3") else 4.0}

geo["misure"] = {
    "base": [B_L, B_W, B_T], "asse_basso": AX_A, "nocca": NOCCA, "gioco_nocca_per_lato": GIOCO_NOCCA,
    "orecchia": ORECCHIA, "guaina": [G_L, NOCCA, G_T], "canale": [CANALE_Y, CANALE_V],
    "slitta": [round(G_L + 1 - S_U0, 1), S_Y, S_V], "gioco_slitta_per_lato": GIOCO_SLITTA,
    "piatto": [P_X1 - P_X0, P_W, P_T], "asse_piatto_dal_dorso": P_DIST, "telefono_max": TELEFONO_MAX,
    "pomello_diametro": round(2 * (K_R + K_A), 1), "pomello_altezza": K_H,
    "posa_uso": {"alfa": ALFA_USO, "sfilo": E_USO, "piatto_dalla_verticale": TILT_USO},
    "viteria": {"M4x50 testa esagonale (cerniere)": 2, "dado M4 (cerniere, nel pomello)": 2,
                "M4x12 testa esagonale (blocco)": 1, "dado M4 (blocco, nella guaina)": 1,
                "M3x10 testa cilindrica (appoggio)": 2, "dado M3 (appoggio)": 2},
}

# --- STL in posa di stampa ---------------------------------------------------
for n, (o, mp) in pieces.items():
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bm.to_mesh(o.data); bm.free()
    o.matrix_world = mp
    bpy.context.view_layer.update()
    geo["pezzi"][n] = info(o)
    write_stl(o, mp, os.path.join(STL, n + ".stl"))
    o.matrix_world = Matrix()

for o in list(C_TMP.objects):
    bpy.data.objects.remove(o)
bpy.data.collections.remove(C_TMP)

with open(os.path.join(ROOT, "dati", "geometria.json"), "w", encoding="utf-8") as f:
    json.dump(geo, f, indent=1, ensure_ascii=False)
print("GEOMETRIA", json.dumps(geo))

path = os.path.join(ROOT, "blender", "costruisci.py")
txt = bpy.data.texts.get("costruisci.py") or bpy.data.texts.new("costruisci.py")
txt.from_string(open(path, encoding="utf-8").read())
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blender", os.path.basename(ROOT).replace(" ", "_") + ".blend"))
