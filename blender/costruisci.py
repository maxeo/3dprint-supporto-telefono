"""Supporto Telefono · supporto pieghevole da scrivania con braccio telescopico, prolunghe e cerniere a frizione.

Uso (dalla cartella del progetto):
    blender -b --factory-startup --python blender/costruisci.py
oppure nel Blender aperto, via MCP: exec(open(r"D:\\3D Print\\Supporto Telefono\\blender\\costruisci.py", encoding="utf-8").read())

Scrive blender/Supporto_Telefono.blend, gli STL in stl/ (già orientati per la stampa) e dati/geometria.json.
Coordinate di montaggio: base sul piano Z = 0, X verso chi guarda il telefono (davanti), Y da sinistra a destra.
Ogni pezzo è costruito nel suo riferimento:
  base       = mondo;
  braccio    = asse della cerniera bassa, u (X) lungo il braccio, v (Z) verso il dietro quando è in piedi;
               guaina, prolunghe e slitta sono disegnate a braccio chiuso; ogni prolunga sta 100 mm più su;
  piatto     = asse della cerniera alta, X lungo il piatto verso l'alto, Z dall'asse verso la faccia del telefono;
  appoggio   = sulla faccia del piatto (Z = 0), con la vite nella guida a T del piatto;
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
# viteria (si compra): tutto M4 a testa esagonale (chiave 7)
D_M4 = 4.4                 # foro passante M4
AF_M4_TESTA = 7.3          # sede esagonale della testa nella forchetta: non gira
AF_M4_DADO = 7.1           # dado (o testa) M4 nel pomello: entra un po' forzato
H_DADO_M4 = 3.4

# cerniere: forchetta (due orecchie) + nocca larga 30 in mezzo
NOCCA = 30.0               # larghezza della nocca (braccio e testa della slitta)
GIOCO_NOCCA = 0.2          # per lato: il bullone stringe le orecchie sulla nocca
ORECCHIA = 9.0             # spessore di ogni orecchia
Y_IN = NOCCA / 2 + GIOCO_NOCCA          # 15,2
Y_OUT = Y_IN + ORECCHIA                 # 24,2
TASCA = 3.0                # profondità della sede della testa nell'orecchia
R_NOCCA = 10.0             # metà spessore del braccio: raggio di nocche e orecchie

# base
B_L, B_W, B_T, B_R = 185.0, 90.0, 7.0, 12.0
AX_A = (30.0, 17.5)        # asse della cerniera bassa (x, z): il braccio piegato sta 0,5 sopra la base
PIEDINI = [(15, 32), (15, -32), (170, 32), (170, -32)]
D_PIEDINO, H_PIEDINO = 10.5, 1.0

# braccio: guaina (P02), slitta (P03), prolunga (P07)
TRATTO = 100.0             # lunghezza di guaina e prolunga (dall'asse o dalla battuta)
G_T = 2 * R_NOCCA          # spessore del braccio (la larghezza è NOCCA)
CANALE_Y, CANALE_V, CANALE_U0 = 24.0, 15.0, 12.0    # canale; parte 12 mm sopra la battuta
GIOCO_SLITTA = 0.3         # per lato
S_Y, S_V = CANALE_Y - 2 * GIOCO_SLITTA, CANALE_V - 2 * GIOCO_SLITTA   # barra 23,4 × 14,4
FESSURA_Y = 14.0           # fessura nella parete davanti del canale
NERV_Y = FESSURA_Y - 2 * GIOCO_SLITTA   # nervatura sotto la barra: arriva a filo della faccia davanti,
                                        # così barra e tratto largo poggiano sul piatto di stampa insieme
S_U0, S_U1 = 15.0, TRATTO + 1.0         # barra a braccio chiuso (entra 1 mm nel tratto largo)
TESTA_L = 12.0             # testa della slitta sopra la guaina
AX_C_U = TRATTO + TESTA_L  # 112: asse della cerniera alta a braccio chiuso, senza prolunghe
BLOCCO_U, BLOCCO_V = 85.0, 3.0          # morsa sul fianco +y: vite di blocco
PAD = (78.0, 92.0, 4.0)                  # rinforzo sul fianco: da u, a u, sporgenza
SCANALATURA = (45.0, 98.0, 5.2, 1.0)     # sulla barra: da u, a u, larghezza, profondità
E_MAX = BLOCCO_U - SCANALATURA[0]        # 40: oltre, la vite batte in fondo alla scanalatura

# piatto (P04) e appoggio (P05), nel riferimento del piatto
P_X0, P_X1, P_W, P_T, P_R = -35.0, 115.0, 80.0, 8.0, 8.0
P_DIST = 14.0              # dall'asse al dorso del piatto
TELEFONO_MAX = 14.0        # spessore massimo del telefono con cover
# guida a T per la vite dell'appoggio, dentro lo spessore del piatto, aperta sul bordo basso
T_Y = 22.0                 # fuori asse: la vite e il pomello non stanno sotto l'asola del cavo
T_FESSURA, T_LABBRO = 4.6, 2.0          # fessura sulla faccia e spessore del labbro davanti
T_CAVA, T_CAVA_H = 7.4, 3.6             # cava della testa: la testa non gira (7 sui piani)
T_X1 = 45.0                # fine della fessura
A_FLANGIA = (-12.0, 15.5, 3.0)          # flangia dell'appoggio: da x, a x (cima della mensola), spessore
A_MENSOLA, A_SPONDA, A_LARGO = 4.0, 8.0, 35.0
XB_MIN = P_X0 + 4.5        # vite più in basso possibile (testa tutta nella cava)
XB_MAX = T_X1 - T_FESSURA / 2

# pomello (P06)
K_R, K_LOBI, K_A, K_H = 10.3, 12, 0.7, 11.0

# pose della scena
ALFA_USO, E_USO, TILT_USO = 95.0, 20.0, 20.0     # braccio da +X, sfilo, inclinazione del piatto dalla verticale
ALFA_PRO, N_PRO = 90.0, 2                        # con le prolunghe il braccio sta dritto
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


C_STAMPA, C_MONT = coll("PEZZI_STAMPA", True), coll("PEZZI_MONTATI")
C_PRO, C_PIEG = coll("CON_PROLUNGHE", True), coll("PIEGATO", True)
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


def forcella(name, poly_xz):
    """Due orecchie (y da Y_IN a Y_OUT e simmetrica)."""
    o = extrude(poly_xz, Y_IN, Y_OUT, "Y", name)
    boolean(o, extrude(poly_xz, -Y_OUT, -Y_IN, "Y", "o2"), 'UNION')
    return o


def fora_cerniera(o, ax_xz):
    """Foro M4 attraverso le orecchie e, sull'orecchia -y, la sede della testa."""
    boolean(o, extrude(circ(*ax_xz, D_M4 / 2, 32), -Y_OUT - 1, Y_OUT + 1, "Y", "foro"), 'DIFFERENCE')
    boolean(o, extrude(hexa(*ax_xz, AF_M4_TESTA), -Y_OUT - 1, -Y_OUT + TASCA, "Y", "testa"), 'DIFFERENCE')


def barra(o, u):
    """Barra che scorre nel canale (con nervatura davanti e scanalatura per la vite di blocco), unita a o.
    u = spostamento lungo il braccio rispetto alla slitta della guaina."""
    boolean(o, extrude(box(u + S_U0, u + S_U1, -S_V / 2, S_V / 2), -S_Y / 2, S_Y / 2, "Y", "barra"), 'UNION')
    boolean(o, extrude(box(u + S_U0, u + S_U1, -R_NOCCA, -S_V / 2 + 0.2), -NERV_Y / 2, NERV_Y / 2, "Y", "nerv"), 'UNION')
    su0, su1, sw, sd = SCANALATURA
    boolean(o, extrude(box(u + su0, u + su1, BLOCCO_V - sw / 2, BLOCCO_V + sw / 2), S_Y / 2 - sd, S_Y / 2 + 1, "Y", "scan"), 'DIFFERENCE')


Y_PAD = NOCCA / 2 + PAD[2]


def canale(o, u):
    """Canale con fessura davanti e morsa sul fianco +y in un tratto che parte (battuta) a u."""
    boolean(o, extrude(box(u + PAD[0], u + PAD[1], -R_NOCCA + 0.5, R_NOCCA - 0.5), NOCCA / 2 - 0.1, Y_PAD, "Y", "pad"), 'UNION')
    boolean(o, extrude(box(u + CANALE_U0, u + TRATTO + 1, -CANALE_V / 2, CANALE_V / 2), -CANALE_Y / 2, CANALE_Y / 2, "Y", "canale"), 'DIFFERENCE')
    boolean(o, extrude(box(u + CANALE_U0, u + TRATTO + 1, -R_NOCCA - 1, -CANALE_V / 2 + 0.1), -FESSURA_Y / 2, FESSURA_Y / 2, "Y", "fessura"), 'DIFFERENCE')
    boolean(o, extrude(circ(u + BLOCCO_U, BLOCCO_V, D_M4 / 2, 32), 0, NOCCA, "Y", "foro_blocco"), 'DIFFERENCE')
    boolean(o, extrude(hexa(u + BLOCCO_U, BLOCCO_V, AF_M4_DADO), Y_PAD - H_DADO_M4, Y_PAD + 1, "Y", "dado"), 'DIFFERENCE')


# --- pezzi ------------------------------------------------------------------
geo = {"misure": {}, "pezzi": {}, "controlli": {}}
pieces = {}                                          # nome -> (oggetto nel suo riferimento, matrice di stampa)
M = {"P01": mat("M_P01", (0.86, 0.86, 0.88)), "P02": mat("M_P02", (0.55, 0.64, 0.74)),
     "P03": mat("M_P03", (0.93, 0.93, 0.93)), "P04": mat("M_P04", (0.30, 0.55, 0.78)),
     "P05": mat("M_P05", (0.95, 0.55, 0.20)), "P06": mat("M_P06", (0.20, 0.20, 0.23)),
     "P07": mat("M_P07", (0.45, 0.70, 0.55)), "VITE": mat("M_viteria", (0.62, 0.62, 0.65), metal=0.9)}

# P01 · base
base = extrude(rrect(0, B_L, -B_W / 2, B_W / 2, B_R), 0, B_T, "Z", "P01_Base")
ear_a = [(AX_A[0] - R_NOCCA, 0.5), (AX_A[0] + R_NOCCA, 0.5)] + arc(*AX_A, R_NOCCA, 0, 180, 36)
boolean(base, forcella("forcA", ear_a), 'UNION')
fora_cerniera(base, AX_A)
# incavo sotto il pomello della cerniera (lato +y): il pomello scende sotto il piano della base
boolean(base, extrude(circ(*AX_A, K_R + K_A + 0.6, 64), Y_OUT + 0.2, B_W, "Y", "incavo"), 'DIFFERENCE')
# da chiuso il pomello della cerniera alta (lato -y) scende allo stesso modo
boolean(base, extrude(circ(AX_A[0] + AX_C_U, AX_A[1], K_R + K_A + 0.6, 64), -B_W, -Y_OUT - 0.2, "Y", "incavo2"), 'DIFFERENCE')
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
gp = [(0, -R_NOCCA), (TRATTO, -R_NOCCA), (TRATTO, R_NOCCA), (0, R_NOCCA)] + arc(0, 0, R_NOCCA, 90, 270, 36, ends=False)
guaina = extrude(gp, -NOCCA / 2, NOCCA / 2, "Y", "P02_Guaina")
canale(guaina, 0.0)
boolean(guaina, extrude(circ(0, 0, D_M4 / 2, 32), -NOCCA, NOCCA, "Y", "foro"), 'DIFFERENCE')
pieces["P02_Guaina"] = (guaina, T(0, 0, R_NOCCA))

# P03 · slitta (braccio chiuso, senza prolunghe)
tp = [(TRATTO, -R_NOCCA), (AX_C_U, -R_NOCCA)] + arc(AX_C_U, 0, R_NOCCA, -90, 90, 36, ends=False) + \
     [(AX_C_U, R_NOCCA), (TRATTO, R_NOCCA)]
slitta = extrude(tp, -NOCCA / 2, NOCCA / 2, "Y", "P03_Slitta")
barra(slitta, 0.0)
boolean(slitta, extrude(circ(AX_C_U, 0, D_M4 / 2, 32), -NOCCA, NOCCA, "Y", "foro"), 'DIFFERENCE')
pieces["P03_Slitta"] = (slitta, T(0, 0, R_NOCCA))

# P07 · prolunga: barra sotto, tratto con canale e morsa sopra (si impilano)
prolunga = extrude(box(TRATTO, 2 * TRATTO, -R_NOCCA, R_NOCCA), -NOCCA / 2, NOCCA / 2, "Y", "P07_Prolunga")
barra(prolunga, 0.0)
canale(prolunga, TRATTO)
pieces["P07_Prolunga"] = (prolunga, T(0, 0, R_NOCCA))

# P04 · piatto (riferimento piatto) con la guida a T per l'appoggio
PZ0, PZ1 = P_DIST, P_DIST + P_T
piatto = extrude(rrect(P_X0, P_X1, -P_W / 2, P_W / 2, P_R), PZ0, PZ1, "Z", "P04_Piatto")
ear_c = [(R_NOCCA, PZ0 + 0.5), (-R_NOCCA, PZ0 + 0.5), (-R_NOCCA, 0)] + \
        arc(0, 0, R_NOCCA, 180, 360, 36, ends=False) + [(R_NOCCA, 0)]
boolean(piatto, forcella("forcC", ear_c), 'UNION')
fora_cerniera(piatto, (0, 0))
boolean(piatto, extrude(box(P_X0 - 1, T_X1, T_Y - T_FESSURA / 2, T_Y + T_FESSURA / 2), PZ1 - T_LABBRO - 0.1, PZ1 + 1, "Z", "fessura"), 'DIFFERENCE')
boolean(piatto, extrude(box(P_X0 - 1, T_X1 + T_CAVA / 2, T_Y - T_CAVA / 2, T_Y + T_CAVA / 2),
                        PZ1 - T_LABBRO - T_CAVA_H, PZ1 - T_LABBRO, "Z", "cava"), 'DIFFERENCE')
pieces["P04_Piatto"] = (piatto, T(0, 0, PZ1) @ Rx(180))

# P05 · appoggio (riferimento: faccia del piatto a Z = 0, vite a x = 0, y = T_Y)
fx0, fx1, ft = A_FLANGIA
Z_SP = TELEFONO_MAX + 0.5
lp = [(fx0, 0), (fx1, 0), (fx1, Z_SP), (fx1 + A_SPONDA, Z_SP), (fx1 + A_SPONDA, Z_SP + 4),
      (fx1 - A_MENSOLA, Z_SP + 4), (fx1 - A_MENSOLA, ft), (fx0, ft)]       # flangia, mensola, sponda
appoggio = extrude(lp, -A_LARGO, A_LARGO, "Y", "P05_Appoggio")
# chiavetta che corre nella fessura: l'appoggio non gira attorno all'unica vite
boolean(appoggio, extrude(box(-10, 10, T_Y - (T_FESSURA - 0.4) / 2, T_Y + (T_FESSURA - 0.4) / 2), -T_LABBRO + 0.2, 0.5, "Z", "chiavetta"), 'UNION')
boolean(appoggio, extrude(circ(0, T_Y, D_M4 / 2, 32), -3, ft + 1, "Z", "foro"), 'DIFFERENCE')
boolean(appoggio, extrude(box(-8, 8, 2, Z_SP - 2), fx1 - A_MENSOLA - 1, fx1 + 1, "X", "cavo"), 'DIFFERENCE')
pieces["P05_Appoggio"] = (appoggio, T(0, 0, A_LARGO) @ Rx(90))


# P06 · pomello: dado M4 (cerniere, appoggio) o testa M4 (morse) nella sede esagonale
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
def vite(name, L, dado_a=None):
    """Vite M4 lungo +Z dalla battuta della testa (Z = 0), testa esagonale sotto Z = 0, dado facoltativo."""
    v = extrude(circ(0, 0, 2.0, 24), -0.01, L, "Z", name)
    boolean(v, extrude(hexa(0, 0, 7.0), -2.8, 0.0, "Z", "t"), 'UNION')
    if dado_a is not None:
        boolean(v, extrude(hexa(0, 0, 7.0), dado_a, dado_a + 3.2, "Z", "d"), 'UNION')
    paint(v, M["VITE"]); move_to(v, C_STAMPA)
    return v


L_CERNIERA = 50
SPESSORE_PACCO = 2 * Y_OUT
vite_cern = vite("M4x50_cerniera", L_CERNIERA, dado_a=SPESSORE_PACCO - TASCA)
vite_blocco = vite("M4x12_blocco", 12)
dado_blocco = extrude(hexa(0, 0, 7.0), 0, 3.2, "Z", "M4_dado_blocco"); paint(dado_blocco, M["VITE"]); move_to(dado_blocco, C_STAMPA)
vite_app = vite("M4x12_appoggio", 12, dado_a=T_LABBRO + ft + 0.05)


# --- pose ----------------------------------------------------------------------
def pose(alfa, e, gamma, npro=0, xb=XB_MIN):
    """Matrici dei pezzi: alfa = braccio da +X (gradi), e = sfilo della slitta, gamma = piatto rispetto al braccio,
    npro = prolunghe (chiuse), xb = posizione della vite dell'appoggio lungo il piatto."""
    braccio = T(AX_A[0], 0, AX_A[1]) @ Ry(-alfa)
    sl = braccio @ T(TRATTO * npro + e, 0, 0)
    pia = sl @ T(AX_C_U, 0, 0) @ Ry(gamma) @ Rx(180)
    to_y = Rx(-90)                                       # Z del pomello → +Y
    gap_bl = S_Y / 2 - SCANALATURA[3] + 12 + 0.05        # faccia del pomello di blocco a vite in battuta
    m = {"P01_Base": Matrix(), "P02_Guaina": braccio, "P03_Slitta": sl, "P04_Piatto": pia,
         "P05_Appoggio": pia @ T(xb, 0, PZ1),
         "P06_Pomello": T(AX_A[0], Y_OUT + 0.05, AX_A[1]) @ to_y,
         "P06_Pomello.2": pia @ T(0, Y_OUT + 0.05, 0) @ to_y,
         "P06_Pomello.3": pia @ T(xb, T_Y, PZ1 + ft + 0.05) @ Matrix.Rotation(math.radians(30), 4, 'Z'),
         "M4x50_cerniera": T(AX_A[0], -Y_OUT + TASCA, AX_A[1]) @ to_y,
         "M4x50_cerniera.2": pia @ T(0, -Y_OUT + TASCA, 0) @ to_y,
         "M4x12_appoggio": pia @ T(xb, T_Y, PZ1 - T_LABBRO) @ Matrix.Rotation(math.radians(30), 4, 'Z')}   # piani contro la cava
    for j in range(npro + 1):                            # una morsa per la guaina e per ogni prolunga
        u = TRATTO * j
        if j:
            m["P07_Prolunga" + ("" if j == 1 else f".{j}")] = braccio @ T(TRATTO * (j - 1), 0, 0)
        s = "" if j == 0 else f".{j + 1}"
        m[f"P06_Pomello.{4 + j}"] = braccio @ T(u + BLOCCO_U, gap_bl, BLOCCO_V) @ to_y
        m["M4x12_blocco" + s] = braccio @ T(u + BLOCCO_U, gap_bl, BLOCCO_V) @ Rx(90)
        m["M4_dado_blocco" + s] = braccio @ T(u + BLOCCO_U, Y_PAD - H_DADO_M4 + 0.1, BLOCCO_V) @ to_y
    return m


def gamma_per(alfa, tilt):
    return -(90 + tilt - alfa)          # il piatto a (90 + tilt)° da +X, il braccio ad alfa


src = {**{n: o for n, (o, _) in pieces.items()},
       "M4x50_cerniera": vite_cern, "M4x12_blocco": vite_blocco, "M4_dado_blocco": dado_blocco, "M4x12_appoggio": vite_app}


def monta(c, mats, suffix):
    out = {}
    for k, mw in mats.items():
        b, _, i = k.partition(".")
        o = bpy.data.objects.new(b + (f"_{i}" if i else "") + suffix, src[b].data)
        o.matrix_world = mw
        c.objects.link(o)
        out[k] = o
    return out


G_USO = gamma_per(ALFA_USO, TILT_USO)
G_PRO = gamma_per(ALFA_PRO, TILT_USO)
P_USO = pose(ALFA_USO, E_USO, G_USO)
P_PRO = pose(ALFA_PRO, E_USO, G_PRO, N_PRO)
P_PIEG = pose(0.0, 0.0, 180.0)
uso = monta(C_MONT, P_USO, "_montato")
pro = monta(C_PRO, P_PRO, "_prolunghe")
pieg = monta(C_PIEG, P_PIEG, "_piegato")
bpy.context.view_layer.update()


# --- controlli -------------------------------------------------------------------
def bounds(objs):
    co = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    return [[round(min(c[i] for c in co), 2), round(max(c[i] for c in co), 2)] for i in range(3)]


def stampati(objs):
    return [k for k in objs if k.split(".")[0] in pieces]


def tocca(a, b):
    ba, bb = bounds([a]), bounds([b])
    return all(ba[i][0] < bb[i][1] and bb[i][0] < ba[i][1] for i in range(3))


def interferenze(objs):
    """Tutte le coppie di pezzi stampati, e ogni vite contro i pezzi: solo dove gli ingombri si toccano."""
    ks = stampati(objs)
    viti = [k for k in objs if k not in ks]
    out = {}
    for i, a in enumerate(ks):
        for b in ks[i + 1:] + viti:
            if tocca(objs[a], objs[b]):
                out[f"{a}+{b}"] = interference(objs[a], objs[b])
    return out


ctrl = geo["controlli"]
for nome, objs in (("uso", uso), ("prolunghe", pro), ("piegato", pieg)):
    r = interferenze(objs)
    ctrl[f"interferenze_{nome}_mm3"] = {k: v for k, v in r.items() if v > 0.05}
    ctrl[f"coppie_controllate_{nome}"] = len(r)
    ctrl[f"ingombro_{nome}_mm"] = bounds([objs[k] for k in stampati(objs)])


def mensola(npro, e, xb, alfa=90.0, tilt=TILT_USO):
    """Altezza dal tavolo della cima della mensola (dove appoggia il telefono)."""
    mp = pose(alfa, e, gamma_per(alfa, tilt), npro, xb)["P04_Piatto"]
    return round((mp @ Vector((xb + fx1, 0, PZ1))).z, 1)


def baricentro_x(mats, xb):
    h, w, s, g = TELEFONO
    return round((mats["P04_Piatto"] @ Vector((xb + fx1 + h / 2, 0, PZ1 + s / 2))).x, 1)


ctrl["mensola_dal_tavolo_mm"] = {f"{n}_prolunghe": [mensola(n, 0, XB_MIN), mensola(n, E_MAX * (n + 1), XB_MAX)] for n in range(4)}
ctrl["mensola_uso_mm"] = round((P_USO["P04_Piatto"] @ Vector((XB_MIN + fx1, 0, PZ1))).z, 1)
ctrl["corsa_appoggio_mm"] = round(XB_MAX - XB_MIN, 1)
ctrl["telefono_baricentro_x_uso_mm"] = baricentro_x(P_USO, XB_MIN)
ctrl["telefono_baricentro_x_uso_appoggio_in_alto_mm"] = baricentro_x(pose(ALFA_USO, E_USO, G_USO, 0, XB_MAX), XB_MAX)
ctrl["telefono_baricentro_x_prolunghe_mm"] = baricentro_x(P_PRO, XB_MIN)
ctrl["telefono_baricentro_x_dritto_appoggio_in_alto_mm"] = baricentro_x(pose(90.0, E_USO, gamma_per(90.0, TILT_USO), 0, XB_MAX), XB_MAX)
ctrl["sfilo_massimo_per_tratto_mm"] = E_MAX
ctrl["pacco_cerniera_mm"] = round(SPESSORE_PACCO, 2)
ctrl["vite_cerniera_filetto_oltre_il_dado_mm"] = round(L_CERNIERA - (SPESSORE_PACCO - TASCA) - 3.2, 2)
ctrl["parete_sopra_canale_mm"] = round(G_T / 2 - CANALE_V / 2, 2)
ctrl["parete_tra_dado_blocco_e_canale_mm"] = round(Y_PAD - H_DADO_M4 - CANALE_Y / 2, 2)
ctrl["piatto_dietro_la_cava_mm"] = round(P_T - T_LABBRO - T_CAVA_H, 2)
ctrl["pomello_appoggio_sotto_la_mensola_mm"] = round(fx1 - A_MENSOLA - (K_R + K_A), 2)
ctrl["appoggio_vite_filetto_oltre_il_dado_mm"] = round(12 - (T_LABBRO + ft + 0.05) - 3.2, 2)

geo["misure"] = {
    "base": [B_L, B_W, B_T], "asse_basso": AX_A, "nocca": NOCCA, "gioco_nocca_per_lato": GIOCO_NOCCA,
    "orecchia": ORECCHIA, "tratto": TRATTO, "braccio": [NOCCA, G_T], "canale": [CANALE_Y, CANALE_V],
    "barra": [round(S_U1 - S_U0, 1), S_Y, S_V], "nervatura": NERV_Y, "fessura": FESSURA_Y, "gioco_slitta_per_lato": GIOCO_SLITTA,
    "piatto": [P_X1 - P_X0, P_W, P_T], "asse_piatto_dal_dorso": P_DIST, "telefono_max": TELEFONO_MAX,
    "guida_appoggio": {"fessura": T_FESSURA, "cava": T_CAVA, "lunga": round(T_X1 - P_X0, 1)},
    "pomello_diametro": round(2 * (K_R + K_A), 1), "pomello_altezza": K_H,
    "posa_uso": {"alfa": ALFA_USO, "sfilo": E_USO, "piatto_dalla_verticale": TILT_USO},
    "posa_prolunghe": {"alfa": ALFA_PRO, "sfilo": E_USO, "prolunghe": N_PRO},
    "viteria_base": {"M4x50 (cerniere)": 2, "M4x12 (morsa guaina, appoggio)": 2, "dadi M4": 4},
    "viteria_per_prolunga": {"M4x12": 1, "dadi M4": 1, "pomelli": 1},
}

# pose per la guida (configurazione con le prolunghe): rotazione stampa → montaggio, ingombro, viti come cilindri
geo["montaggio"] = {}
for k in stampati(pro):
    rot = (P_PRO[k] @ pieces[k.split(".")[0]][1].inverted()).to_3x3()
    geo["montaggio"][k] = {"matrice": [[round(a, 6) for a in r] for r in rot], "bounds": bounds([pro[k]])}
geo["viti"] = {}
for k in pro:
    b = k.split(".")[0]
    if b.startswith("M4x"):
        mw = P_PRO[k]
        L = int(b[3:].split("_")[0])
        d = (mw.to_3x3() @ Vector((0, 0, 1))).normalized()
        c = mw @ Vector((0, 0, 0)) + d * (L / 2)
        geo["viti"][k] = {"centro": [round(a, 2) for a in c], "asse": [round(a, 4) for a in d], "lunghezza": L, "diametro": 4.0}

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
