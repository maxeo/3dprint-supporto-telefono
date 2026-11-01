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
# viteria stampata: filetto trapezoidale passo 2,5 (quello delle palline), viti stampate in piedi
F_P, F_H = 2.5, 0.9        # passo, profondità del filetto
F_GIOCO = 0.35             # gioco radiale della madrevite
D_CERN, D_MORSA = 10.0, 8.0                # viti delle cerniere; viti di morse e appoggio
FORO = 0.8                 # foro passante = diametro + 0,8
Q_COLLO, Q_SEDE = 10.4, 10.8               # collo quadro sotto la testa della vite di cerniera, e la sua sede nell'orecchia
TESTA_CERN = (18.0, 4.0)   # testa tonda della vite di cerniera: Ø, alto (fuori dall'orecchia)
L_CERN = 57.0              # vite di cerniera dalla testa alla punta
TESTA_APP, L_APP = (12.6, 3.4), 13.5       # testa quadra della vite dell'appoggio (lato, alto), lunghezza
L_PERNO = 12.0             # vite della morsa, unita al suo pomello
DADO_AF, DADO_H, SEDE_DADO = 13.0, 5.0, 13.3   # dado della morsa e la sua sede esagonale nel rinforzo
FONDO_POMELLO = 1.6        # pieno sopra la madrevite cieca dei pomelli

# cerniere: forchetta (due orecchie) + nocca larga 30 in mezzo
NOCCA = 30.0               # larghezza della nocca (braccio e testa della slitta)
GIOCO_NOCCA = 0.2          # per lato: il bullone stringe le orecchie sulla nocca
ORECCHIA = 9.0             # spessore di ogni orecchia
Y_IN = NOCCA / 2 + GIOCO_NOCCA          # 15,2
Y_OUT = Y_IN + ORECCHIA                 # 24,2
R_NOCCA = 10.0             # metà spessore del braccio: raggio di nocche e orecchie
# cerniera bassa a scatti: denti radiali fra la nocca della guaina (lato del pomello) e la rondella P14,
# che col piede appoggia sulla base e non gira; la vite deve solo tenere i denti in presa
DENTI_N, DENTI_H = 36, 0.65                # scatti da 10°, denti a 90° sul raggio medio
DENTI_R = (5.9, 9.5)                       # corona dei denti
R_INCASSO = 10.5                           # incasso sulle facce della nocca bassa (rondella e piede)
YN_V = 12.85                               # fondo dei denti della nocca (lato +y); punte a YN_V + DENTI_H
GIOCO_DENTI = 0.15                         # fra punte e fondi, a denti in presa
GIOCO_SGANCIO = 0.65                       # lato della testa della vite: allentando il pomello i denti si staccano

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
BLOCCO_U, BLOCCO_V = 85.0, 0.0          # morsa sul fianco +y: vite di blocco
PAD = (76.0, 94.0, 5.0)                  # rinforzo sul fianco con la sede del dado: da u, a u, sporgenza
E_MAX = 40.0               # sfilo per tratto: oltre, la vite batte in fondo alla scanalatura
SCANALATURA = (BLOCCO_U - E_MAX - (D_MORSA + 1) / 2, 98.0, D_MORSA + 1, 1.0)   # sulla barra: da u, a u, larghezza, profondità

# piatto (P04) e appoggio (P05), nel riferimento del piatto
P_X0, P_X1, P_W, P_T, P_R = -35.0, 115.0, 80.0, 8.0, 8.0
P_DIST = 14.0              # dall'asse al dorso del piatto
TELEFONO_MAX = 14.0        # spessore massimo del telefono con cover
# guida a T per la vite dell'appoggio, dentro lo spessore del piatto, aperta sul bordo basso
T_Y = 22.0                 # fuori asse: la vite e il pomello non stanno sotto l'asola del cavo
T_FESSURA, T_LABBRO = D_MORSA + FORO, 2.0          # fessura sulla faccia e spessore del labbro davanti
T_CAVA, T_CAVA_H = TESTA_APP[0] + 0.6, TESTA_APP[1] + 0.4   # cava della testa quadra: la testa non gira
T_X1 = 45.0                # fine della fessura
A_FLANGIA = (-12.0, 15.5, 3.0)          # flangia dell'appoggio: da x, a x (cima della mensola), spessore
A_MENSOLA, A_SPONDA, A_LARGO = 4.0, 8.0, 35.0
XB_MIN = P_X0 + TESTA_APP[0] / 2 + 0.7   # vite più in basso possibile (testa tutta nella cava)
XB_MAX = T_X1 - T_FESSURA / 2

# pomello (P06)
K_R, K_LOBI, K_A, K_H = 10.3, 12, 0.7, 11.0
K_H_MV = 13.0              # pomelli con la madrevite (P06, P10): più alti, ~2,5 mm liberi sul fondo oltre la punta della vite

# pose della scena
ALFA_USO, E_USO, TILT_USO = 100.0, 20.0, 20.0     # braccio da +X, sfilo, inclinazione del piatto dalla verticale
ALFA_PRO, N_PRO = 90.0, 3                        # con le prolunghe il braccio sta dritto (la guida ne toglie da 3 a 0)
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


def thread_r(t, z, r_out):
    """Profilo trapezoidale, filetto destro: cresta 0,24 p, fianchi 0,29 p (come le palline)."""
    u = (z - F_P * t / (2 * math.pi)) % F_P / F_P
    crest, flank = 0.24, 0.29
    if u < crest:
        f = 1.0
    elif u < crest + flank:
        f = 1 - (u - crest) / flank
    elif u < 1 - flank:
        f = 0.0
    else:
        f = (u - (1 - flank)) / flank
    return r_out - F_H + F_H * f


def vite_stampata(d, z0, z1, name, punta=True):
    """Gambo filettato Ø d lungo Z da z0 a z1, con la punta smussata in z1 (e in z0 se punta == 'due')."""
    rc = d / 2 - F_H
    def r(t, z):
        v = thread_r(t, z, d / 2)
        if punta:
            v = min(v, rc + 0.15 + (z1 - z))
        if punta == "due":
            v = min(v, rc + 0.15 + (z - z0))
        return v
    return radial_solid(r, z0, z1, name, C_TMP, seg=72, dz=0.1)


def madrevite(d, z0, z1, name, invito=(True, False)):
    """Solido da sottrarre per la madrevite di una vite Ø d (gioco F_GIOCO), con l'invito a 45° alle estremità scelte."""
    fm = d / 2 + F_GIOCO
    def r(t, z):
        v = thread_r(t, z, fm)
        if invito[0]:
            v = max(v, fm + 0.6 - (z - z0 - 0.5))
        if invito[1]:
            v = max(v, fm + 0.6 - (z1 - 0.5 - z))
        return v
    return radial_solid(r, z0, z1, name, C_TMP, seg=72, dz=0.1)


def fase(dz):
    """Rotazione (attorno all'asse) che allinea il filetto di un pezzo spostato di dz lungo l'asse rispetto all'altro."""
    return Matrix.Rotation(2 * math.pi * dz / F_P, 4, 'Z')


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


def dente(t):
    """1 sulle punte dei denti (multipli del passo), 0 sui fondi."""
    f = (t * DENTI_N / (2 * math.pi)) % 1.0
    return abs(2 * f - 1)


def corona(r0, r1, zb, zfun, name):
    """Anello da r0 a r1 col fondo a zb e la cima zfun(theta): denti radiali, due campioni per dente."""
    bm = bmesh.new()
    ang = [math.pi * j / DENTI_N for j in range(2 * DENTI_N)]
    def ring(r, top):
        return [bm.verts.new((r * math.cos(t), r * math.sin(t), zfun(t) if top else zb)) for t in ang]
    it, ot, ib, ob = ring(r0, True), ring(r1, True), ring(r0, False), ring(r1, False)
    for j in range(len(ang)):
        i = (j + 1) % len(ang)
        bm.faces.new((it[j], ot[j], ot[i])); bm.faces.new((it[j], ot[i], it[i]))
        bm.faces.new((ib[j], ib[i], ob[i], ob[j]))
        bm.faces.new((ot[j], ob[j], ob[i], ot[i]))
        bm.faces.new((it[j], it[i], ib[i], ib[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(bm, name, C_TMP)


def forcella(name, poly_xz):
    """Due orecchie (y da Y_IN a Y_OUT e simmetrica)."""
    o = extrude(poly_xz, Y_IN, Y_OUT, "Y", name)
    boolean(o, extrude(poly_xz, -Y_OUT, -Y_IN, "Y", "o2"), 'UNION')
    return o


def fora_cerniera(o, ax_xz):
    """Foro della vite di cerniera attraverso le orecchie e, nell'orecchia -y, la sede del collo quadro
    (girata di 45°: col vertice in alto il cielo si stampa senza supporti)."""
    boolean(o, extrude(circ(*ax_xz, (D_CERN + FORO) / 2, 48), -Y_OUT - 1, Y_OUT + 1, "Y", "foro"), 'DIFFERENCE')
    boolean(o, extrude(circ(*ax_xz, Q_SEDE / math.sqrt(2), 4), -Y_OUT - 1, -Y_IN + 1, "Y", "collo"), 'DIFFERENCE')


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
    boolean(o, extrude(circ(u + BLOCCO_U, BLOCCO_V, (D_MORSA + FORO) / 2, 48), 0, NOCCA, "Y", "foro_blocco"), 'DIFFERENCE')
    boolean(o, extrude(hexa(u + BLOCCO_U, BLOCCO_V, SEDE_DADO), Y_PAD - DADO_H - 0.2, Y_PAD + 1, "Y", "dado"), 'DIFFERENCE')


# --- pezzi ------------------------------------------------------------------
geo = {"misure": {}, "pezzi": {}, "controlli": {}}
pieces = {}                                          # nome -> (oggetto nel suo riferimento, matrice di stampa)
M = {"P01": mat("M_P01", (0.86, 0.86, 0.88)), "P02": mat("M_P02", (0.55, 0.64, 0.74)),
     "P03": mat("M_P03", (0.93, 0.93, 0.93)), "P04": mat("M_P04", (0.30, 0.55, 0.78)),
     "P05": mat("M_P05", (0.95, 0.55, 0.20)), "P06": mat("M_P06", (0.20, 0.20, 0.23)),
     "P07": mat("M_P07", (0.45, 0.70, 0.55)), "P08": mat("M_P08", (0.62, 0.64, 0.68)),
     "P09": mat("M_P09", (0.62, 0.64, 0.68)), "P10": mat("M_P10", (0.20, 0.20, 0.23)),
     "P11": mat("M_P11", (0.20, 0.20, 0.23)), "P12": mat("M_P12", (0.62, 0.64, 0.68)),
     "P14": mat("M_P14", (0.85, 0.35, 0.20))}

# P01 · base
base = extrude(rrect(0, B_L, -B_W / 2, B_W / 2, B_R), 0, B_T, "Z", "P01_Base")
ear_a = [(AX_A[0] - R_NOCCA, 0.5), (AX_A[0] + R_NOCCA, 0.5)] + arc(*AX_A, R_NOCCA, 0, 180, 36)
boolean(base, forcella("forcA", ear_a), 'UNION')
fora_cerniera(base, AX_A)
# incavo sotto il pomello della cerniera (lato +y): il pomello scende sotto il piano della base
boolean(base, extrude(circ(*AX_A, K_R + K_A + 0.6, 64), Y_OUT + 0.2, B_W, "Y", "incavo"), 'DIFFERENCE')
# da chiuso il pomello della cerniera alta (lato -y) scende allo stesso modo
boolean(base, extrude(circ(AX_A[0] + AX_C_U, AX_A[1], K_R + K_A + 0.6, 64), -B_W, -Y_OUT - 0.2, "Y", "incavo2"), 'DIFFERENCE')
# e quello della morsa della guaina (lato +y)
boolean(base, extrude(circ(AX_A[0] + BLOCCO_U, AX_A[1] + BLOCCO_V, K_R + K_A + 0.6, 64), Y_PAD + 0.5, B_W, "Y", "incavo3"), 'DIFFERENCE')
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
# nocca: lato +y incassato con la corona di denti, lato -y accorciato per il gioco di sgancio
boolean(guaina, extrude(circ(0, 0, R_INCASSO, 96), YN_V, NOCCA, "Y", "incasso"), 'DIFFERENCE')
dn = corona(*DENTI_R, YN_V - 0.5, lambda t: YN_V + DENTI_H * dente(t), "denti")
dn.data.transform(Rx(-90))                       # Z della corona → +y della guaina
boolean(guaina, dn, 'UNION')
boolean(guaina, extrude(circ(0, 0, R_INCASSO, 96), -NOCCA, -(Y_IN - GIOCO_SGANCIO), "Y", "sgancio"), 'DIFFERENCE')
boolean(guaina, extrude(circ(0, 0, (D_CERN + FORO) / 2, 48), -NOCCA, NOCCA, "Y", "foro"), 'DIFFERENCE')
pieces["P02_Guaina"] = (guaina, T(0, 0, R_NOCCA))

# P03 · slitta (braccio chiuso, senza prolunghe)
tp = [(TRATTO, -R_NOCCA), (AX_C_U, -R_NOCCA)] + arc(AX_C_U, 0, R_NOCCA, -90, 90, 36, ends=False) + \
     [(AX_C_U, R_NOCCA), (TRATTO, R_NOCCA)]
slitta = extrude(tp, -NOCCA / 2, NOCCA / 2, "Y", "P03_Slitta")
barra(slitta, 0.0)
boolean(slitta, extrude(circ(AX_C_U, 0, (D_CERN + FORO) / 2, 48), -NOCCA, NOCCA, "Y", "foro"), 'DIFFERENCE')
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
boolean(appoggio, extrude(circ(0, T_Y, (D_MORSA + FORO) / 2, 48), -3, ft + 1, "Z", "foro"), 'DIFFERENCE')
boolean(appoggio, extrude(box(-8, 8, 2, Z_SP - 2), fx1 - A_MENSOLA - 1, fx1 + 1, "X", "cavo"), 'DIFFERENCE')
pieces["P05_Appoggio"] = (appoggio, T(0, 0, A_LARGO) @ Rx(90))


# P06 · pomelli zigrinati: madrevite cieca (cerniere Ø10, appoggio Ø8) o vite unita (morse Ø8)
def k_r(t, z, h=K_H):
    r = K_R + K_A * math.cos(K_LOBI * t)
    r -= max(0.0, z - (h - 1.5)) * 1.0            # smusso in cima
    r -= max(0.0, 0.4 - z)                        # niente zampa d'elefante
    return r


def pomello(name, d):
    o = radial_solid(lambda t, z: k_r(t, z, K_H_MV), 0, K_H_MV, name, C_TMP, seg=144, dz=0.25)
    boolean(o, madrevite(d, -0.5, K_H_MV - FONDO_POMELLO, "mv"), 'DIFFERENCE')
    return o


pieces["P06_Pomello"] = (pomello("P06_Pomello", D_CERN), Matrix())
pieces["P10_Pomello_Appoggio"] = (pomello("P10_Pomello_Appoggio", D_MORSA), Matrix())
# morsa: pomello pieno con la vite sotto la faccia (z < 0); si stampa con la cima sul piatto e la vite in su
pm = radial_solid(k_r, 0, K_H, "P11_Pomello_Morsa", C_TMP, seg=144, dz=0.25)
boolean(pm, vite_stampata(D_MORSA, -L_PERNO, 0.4, "perno"), 'UNION')
pieces["P11_Pomello_Morsa"] = (pm, T(0, 0, K_H) @ Rx(180))

# P08 · vite di cerniera: testa tonda, collo quadro (non gira nell'orecchia), gambo filettato; Z = 0 alla battuta della testa
th, tt = TESTA_CERN
vc = radial_solid(lambda t, z: th / 2 - max(0.0, -z - (tt - 1.0)), -tt, 0, "P08_Vite_Cerniera", C_TMP, seg=72, dz=0.25)
boolean(vc, extrude(circ(0, 0, Q_COLLO / math.sqrt(2), 4), -0.3, ORECCHIA - 0.4, "Z", "collo"), 'UNION')
boolean(vc, vite_stampata(D_CERN, ORECCHIA - 0.7, L_CERN, "gambo"), 'UNION')
pieces["P08_Vite_Cerniera"] = (vc, T(0, 0, tt))

# P09 · vite dell'appoggio: testa quadra nella cava, gambo filettato; Z = 0 alla battuta della testa
ta, tah = TESTA_APP
va = extrude(box(-ta / 2, ta / 2, -ta / 2, ta / 2), -tah, 0, "Z", "P09_Vite_Appoggio")
boolean(va, vite_stampata(D_MORSA, -0.3, L_APP, "gambo"), 'UNION')
pieces["P09_Vite_Appoggio"] = (va, T(0, 0, tah))

# P12 · dado della morsa, nella sede esagonale del rinforzo
dado = extrude(hexa(0, 0, DADO_AF), 0, DADO_H, "Z", "P12_Dado_Morsa")
boolean(dado, madrevite(D_MORSA, -0.5, DADO_H + 0.5, "mv", (True, True)), 'DIFFERENCE')
pieces["P12_Dado_Morsa"] = (dado, Matrix())

# P14 · rondella dentata fra la nocca bassa e l'orecchia destra: il piede appoggia sulla base e non la lascia girare
# riferimento: Z = 0 sulla faccia contro l'orecchia, Z verso la nocca; X = x e Y = z del mondo, asse in 0
Y_RON = Y_IN - 0.05
ZR_V = Y_RON - (YN_V + DENTI_H + GIOCO_DENTI)    # fondi dei denti della rondella
ron = extrude(circ(0, 0, DENTI_R[1], 96), 0, ZR_V, "Z", "P14_Rondella_Dentata")
boolean(ron, extrude(box(-7.5, 3.0, B_T + 0.1 - AX_A[1], 0), 0, ZR_V, "Z", "piede"), 'UNION')
boolean(ron, corona(*DENTI_R, ZR_V - 0.5, lambda t: ZR_V + DENTI_H * (1 - dente(t)), "denti"), 'UNION')
boolean(ron, extrude(circ(0, 0, (D_CERN + FORO) / 2, 48), -1, ZR_V + DENTI_H + 1, "Z", "foro"), 'DIFFERENCE')
pieces["P14_Rondella_Dentata"] = (ron, Matrix())

for n, (o, mp) in pieces.items():
    move_to(o, C_STAMPA)
    paint(o, M[n[:3]])


# --- pose ----------------------------------------------------------------------
def pose(alfa, e, gamma, npro=0, xb=XB_MIN):
    """Matrici dei pezzi: alfa = braccio da +X (gradi), e = sfilo della slitta, gamma = piatto rispetto al braccio,
    npro = prolunghe (chiuse), xb = posizione della vite dell'appoggio lungo il piatto."""
    braccio = T(AX_A[0], 0, AX_A[1]) @ Ry(-alfa)
    sl = braccio @ T(TRATTO * npro + e, 0, 0)
    pia = sl @ T(AX_C_U, 0, 0) @ Ry(gamma) @ Rx(180)
    to_y = Rx(-90)                                       # Z di viti e pomelli → +Y
    y_k = Y_OUT + 0.05                                   # faccia del pomello di cerniera
    y_bl = S_Y / 2 - SCANALATURA[3] + 0.05 + L_PERNO      # faccia del pomello della morsa a vite in battuta
    y_dado = Y_PAD - DADO_H - 0.1
    z_vb, z_kb = PZ1 - T_LABBRO, PZ1 + ft + 0.05         # battuta della vite dell'appoggio e faccia del suo pomello
    # i pezzi che girano (pomelli) prendono la fase del filetto di quello fermo: nella scena i filetti combaciano
    m = {"P01_Base": Matrix(), "P02_Guaina": braccio, "P03_Slitta": sl, "P04_Piatto": pia,
         "P05_Appoggio": pia @ T(xb, 0, PZ1),
         "P06_Pomello": T(AX_A[0], y_k, AX_A[1]) @ to_y @ fase(y_k + Y_OUT),
         "P06_Pomello.2": pia @ T(0, y_k, 0) @ to_y @ fase(y_k + Y_OUT),
         "P08_Vite_Cerniera": T(AX_A[0], -Y_OUT, AX_A[1]) @ to_y,
         "P14_Rondella_Dentata": T(AX_A[0], Y_RON, AX_A[1]) @ Rx(90),
         "P08_Vite_Cerniera.2": pia @ T(0, -Y_OUT, 0) @ to_y,
         "P09_Vite_Appoggio": pia @ T(xb, T_Y, z_vb),
         "P10_Pomello_Appoggio": pia @ T(xb, T_Y, z_kb) @ fase(z_kb - z_vb)}
    for j in range(npro + 1):                            # una morsa per la guaina e per ogni prolunga
        u = TRATTO * j
        if j:
            m["P07_Prolunga" + ("" if j == 1 else f".{j}")] = braccio @ T(TRATTO * (j - 1), 0, 0)
        s = "" if j == 0 else f".{j + 1}"
        m["P11_Pomello_Morsa" + s] = braccio @ T(u + BLOCCO_U, y_bl, BLOCCO_V) @ to_y @ fase(y_bl - y_dado)
        m["P12_Dado_Morsa" + s] = braccio @ T(u + BLOCCO_U, y_dado, BLOCCO_V) @ to_y
    return m


def gamma_per(alfa, tilt):
    return -(90 + tilt - alfa)          # il piatto a (90 + tilt)° da +X, il braccio ad alfa


src = {n: o for n, (o, _) in pieces.items()}


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
    """Tutte le coppie di pezzi (viti comprese): solo dove gli ingombri si toccano."""
    ks = stampati(objs)
    out = {}
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
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
ctrl["pacco_cerniera_mm"] = round(2 * Y_OUT, 2)
ctrl["vite_cerniera_in_presa_nel_pomello_mm"] = round(L_CERN - 2 * Y_OUT - 0.05, 2)
ctrl["vite_cerniera_spazio_in_fondo_al_pomello_mm"] = round(K_H_MV - FONDO_POMELLO - (L_CERN - 2 * Y_OUT - 0.05), 2)
ctrl["denti_gioco_per_sganciarli_mm"] = round(GIOCO_SGANCIO + GIOCO_DENTI + 0.05, 2)
ctrl["denti_altezza_mm"] = DENTI_H
ctrl["rondella_spessore_mm"] = round(ZR_V, 2)
ctrl["parete_sede_collo_orecchia_mm"] = round(R_NOCCA - Q_SEDE / math.sqrt(2), 2)
ctrl["parete_nocca_attorno_al_foro_mm"] = round(R_NOCCA - (D_CERN + FORO) / 2, 2)
ctrl["parete_sopra_canale_mm"] = round(G_T / 2 - CANALE_V / 2, 2)
ctrl["parete_tra_dado_morsa_e_canale_mm"] = round(Y_PAD - DADO_H - 0.2 - CANALE_Y / 2, 2)
ctrl["pomello_morsa_staccato_dal_rinforzo_mm"] = round(S_Y / 2 - SCANALATURA[3] + 0.05 + L_PERNO - Y_PAD, 2)
ctrl["piatto_dietro_la_cava_mm"] = round(P_T - T_LABBRO - T_CAVA_H, 2)
ctrl["pomello_appoggio_sotto_la_mensola_mm"] = round(fx1 - A_MENSOLA - (K_R + K_A), 2)
ctrl["vite_appoggio_in_presa_nel_pomello_mm"] = round(L_APP - (T_LABBRO + ft + 0.05), 2)
ctrl["vite_appoggio_spazio_in_fondo_al_pomello_mm"] = round(K_H_MV - FONDO_POMELLO - (L_APP - (T_LABBRO + ft + 0.05)), 2)

geo["misure"] = {
    "base": [B_L, B_W, B_T], "asse_basso": AX_A,
    "denti": {"numero": DENTI_N, "scatto_gradi": round(360 / DENTI_N, 1), "altezza": DENTI_H, "raggi": DENTI_R}, "nocca": NOCCA, "gioco_nocca_per_lato": GIOCO_NOCCA,
    "orecchia": ORECCHIA, "tratto": TRATTO, "braccio": [NOCCA, G_T], "canale": [CANALE_Y, CANALE_V],
    "barra": [round(S_U1 - S_U0, 1), S_Y, S_V], "nervatura": NERV_Y, "fessura": FESSURA_Y, "gioco_slitta_per_lato": GIOCO_SLITTA,
    "piatto": [P_X1 - P_X0, P_W, P_T], "asse_piatto_dal_dorso": P_DIST, "telefono_max": TELEFONO_MAX, "telefono": list(TELEFONO[:3]),
    "guida_appoggio": {"fessura": T_FESSURA, "cava": T_CAVA, "lunga": round(T_X1 - P_X0, 1)},
    "pomello_diametro": round(2 * (K_R + K_A), 1), "pomello_altezza": K_H_MV, "pomello_morsa_altezza": K_H,
    "posa_uso": {"alfa": ALFA_USO, "sfilo": E_USO, "piatto_dalla_verticale": TILT_USO},
    "posa_prolunghe": {"alfa": ALFA_PRO, "sfilo": E_USO, "prolunghe": N_PRO},
    "filetto": {"passo": F_P, "profondita": F_H, "gioco_radiale": F_GIOCO, "cerniere": D_CERN, "morse_appoggio": D_MORSA},
    "vite_cerniera": {"lunga": L_CERN, "testa": TESTA_CERN, "collo": Q_COLLO},
    "vite_appoggio": {"lunga": L_APP, "testa": TESTA_APP}, "vite_morsa": L_PERNO, "dado_morsa": [DADO_AF, DADO_H],
}

# pose per la guida (configurazione con le prolunghe): rotazione stampa → montaggio, ingombro
geo["montaggio"] = {}
for k in stampati(pro):
    rot = (P_PRO[k] @ pieces[k.split(".")[0]][1].inverted()).to_3x3()
    geo["montaggio"][k] = {"matrice": [[round(a, 6) for a in r] for r in rot], "bounds": bounds([pro[k]])}

# --- telefono di riferimento (non si stampa) -----------------------------------------
# sul piatto, col lato corto sulla mensola dell'appoggio (vite in basso): nella scena aperto e con le prolunghe,
# e per la guida in dati/accessori.json (voce "accessories", agganciato al piatto)
C_RIF = coll("RIFERIMENTI")
M_TEL, M_SCHERMO = mat("M_Telefono", (0.09, 0.09, 0.10)), mat("M_Schermo", (0.01, 0.02, 0.04))
M_TASTI = mat("M_Telefono_Tasti", (0.22, 0.22, 0.24), 0.6)
HOME = "blender/homescreen.webp"                 # schermata di prova (generata con Codex, WebP 640 × 1384, 13 KB)
TASTI = ((40, 58, -1), (32, 44, 1), (47, 59, 1))  # da, a (mm dalla cima); -1 = destra (accensione), +1 = sinistra (volume)
if os.path.exists(os.path.join(ROOT, HOME)):
    nt = M_SCHERMO.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(ROOT, HOME), check_existing=True)
    nt.links.new(tex.outputs["Color"], next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"])


def uv_schermo(co, x0, x1, y0, y1):
    """Alto dell'immagine verso la cima del telefono (+x); la destra di chi guarda lo schermo è -y."""
    return ((y1 - co.y) / (y1 - y0), (co.x - x0) / (x1 - x0))


def stadio(w, h, n=12):
    """Contorno a stadio (USB-C) largo w e alto h, centrato in (0, 0)."""
    r, pts = h / 2, []
    for cx, a0 in ((w / 2 - r, -90), (-w / 2 + r, 90)):
        pts += [(cx + r * math.cos(math.radians(a0 + 180 * k / n)), r * math.sin(math.radians(a0 + 180 * k / n))) for k in range(n + 1)]
    return pts


def telefono(mp, c, suffix):
    h, w, s_, _ = TELEFONO
    x0, z0 = XB_MIN + fx1 + 0.2, PZ1 + 0.1
    zc = z0 + s_ / 2
    out = []
    for nome, poly, za, zb, m in (("RIF_Telefono", rrect(x0, x0 + h, -w / 2, w / 2, 9.0), z0, z0 + s_, M_TEL),
                                  ("RIF_Telefono_Schermo", rrect(x0 + 2, x0 + h - 2, -w / 2 + 2, w / 2 - 2, 7.5), z0 + s_ - 0.1, z0 + s_ + 0.25, M_SCHERMO)):
        o = extrude(poly, za, zb, "Z", nome + suffix, c)
        if nome == "RIF_Telefono":                # presa USB-C nel lato corto in basso, sopra l'asola dell'appoggio
            boolean(o, extrude([(p, zc + q) for p, q in stadio(8.4, 2.6)], x0 - 1, x0 + 7, "X", "usbc"), 'DIFFERENCE')
        o.data.materials.clear(); o.data.materials.append(m)   # il booleano lascia uno slot vuoto
        o.matrix_world = mp
        out.append(o)
    me = out[1].data
    uv = me.uv_layers.new(name="UV").data
    for li, lp in enumerate(me.loops):
        uv[li].uv = uv_schermo(me.vertices[lp.vertex_index].co, x0 + 2, x0 + h - 2, -w / 2 + 2, w / 2 - 2)
    bm = bmesh.new()                              # tasti laterali, a metà spessore
    for a, b, lato in TASTI:
        ya, yb = (-w / 2 - 0.8, -w / 2 + 0.3) if lato < 0 else (w / 2 - 0.3, w / 2 + 0.8)
        r = bmesh.ops.create_cube(bm, size=1)
        for v in r["verts"]:
            v.co = Vector((x0 + h - (a + b) / 2 + v.co.x * (b - a), (ya + yb) / 2 + v.co.y * (yb - ya), z0 + s_ / 2 + v.co.z * 2.6))
    o = obj_from_bm(bm, "RIF_Telefono_Tasti" + suffix, c)
    o.data.materials.append(M_TASTI)
    o.matrix_world = mp
    out.append(o)
    spina = extrude([(p, zc + q) for p, q in stadio(8.2, 2.4)], x0 - 1.0, x0 + 6.5, "X", "RIF_Cavo_Spina" + suffix, c)
    boolean(spina, extrude([(p, zc + q) for p, q in stadio(10.0, 5.0)], x0 - 5.0, x0 - 0.1, "X", "corpo"), 'UNION')
    spina.data.materials.clear(); spina.data.materials.append(M_CAVO)   # guscio nella presa + corpo in gomma nell'asola dell'appoggio
    spina.matrix_world = mp
    return out, spina


# cavo USB-C: esce dall'asola dell'appoggio davanti al braccio, scende sulla base dal lato della testa della vite
# (a sinistra), la attraversa e cade dal bordo dietro sul tavolo
M_CAVO = mat("M_Cavo", (0.85, 0.85, 0.83))
R_CAVO = 1.6
Z_CAVO = 7 + R_CAVO + 0.3                         # sopra la piastra della base
CODA_CAVO = [Vector(p) for p in ((54, -4, 14), (52, -10, Z_CAVO + 0.3), (48, -20, Z_CAVO), (41, -33, Z_CAVO), (30, -39, Z_CAVO),
             (12, -40, Z_CAVO), (1, -40, Z_CAVO), (-4, -40, 5.5), (-9, -40, R_CAVO + 0.05), (-50, -40, R_CAVO + 0.05))]
# con le prolunghe il cavo scende dritto davanti al braccio fra queste quote: la guida accorcia solo questo tratto
# quando toglie le prolunghe (voce "stretch" in dati/accessori.json)
CAVO_DRITTO = (50.0, 375.0)


def cavo(ap, giu, nome, c, dritto=None):
    """Tubo lungo una Bezier: due punti nell'asola (riferimento dell'appoggio), poi giu e la coda sulla base.
    dritto = indice del punto da cui parte un tratto verticale: maniglie verticali, così resta una retta."""
    pts = [ap @ Vector((10.6, 0, 4.9)), ap @ Vector((-15, 0, 4.9))] + [Vector(p) for p in giu] + CODA_CAVO
    cu = bpy.data.curves.new(nome, 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    if dritto is not None:
        a, b = sp.bezier_points[dritto], sp.bezier_points[dritto + 1]
        L = (a.co.z - b.co.z) / 3
        for bp, su, giu_ in ((a, 10, L), (b, L, 10)):
            bp.handle_left_type = bp.handle_right_type = 'ALIGNED'
            bp.handle_left, bp.handle_right = bp.co + Vector((0, 0, su)), bp.co - Vector((0, 0, giu_))
    cu.bevel_depth, cu.bevel_resolution, cu.resolution_u, cu.use_fill_caps = R_CAVO, 3, 10, True
    tmp = bpy.data.objects.new("tmp_" + nome, cu); c.objects.link(tmp)
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tmp); bpy.data.curves.remove(cu)
    o = bpy.data.objects.new(nome, me); c.objects.link(o)
    me.materials.append(M_CAVO)
    return o


tel_uso, spina_uso = telefono(P_USO["P04_Piatto"], C_RIF, "")
tel_pro, spina_pro = telefono(P_PRO["P04_Piatto"], C_PRO, "_prolunghe")
cavo_uso = cavo(P_USO["P05_Appoggio"], ((52, 0, 95), (55, 0, 50), (55, -1, 26)), "RIF_Cavo", C_RIF)
cavo_pro = cavo(P_PRO["P05_Appoggio"], ((55, 0, CAVO_DRITTO[1]), (55, 0, CAVO_DRITTO[0]), (55, -1, 26)), "RIF_Cavo_prolunghe", C_PRO, dritto=2)
bpy.context.view_layer.update()
ctrl["telefono_tocca_mm3"] = {f"{o.name}+{k}": v for o in tel_uso[:1] for k in ("P04_Piatto", "P05_Appoggio", "P10_Pomello_Appoggio")
                             for v in [interference(o, uso[k])] if v > 0.05}
ctrl["cavo_tocca_mm3"] = {f"{o.name}+{k}": v for o, pz_ in ((spina_uso, uso), (cavo_uso, uso), (spina_pro, pro), (cavo_pro, pro))
                          for k in stampati(pz_) if tocca(o, pz_[k]) for v in [interference(o, pz_[k])] if v > 0.05}
ctrl["cavo_tocca_mm3"].update({f"{a.name}+{b.name}": v for a, b in ((spina_uso, tel_uso[0]), (spina_pro, tel_pro[0]))
                               for v in [interference(a, b)] if v > 0.05})
acc_out = []
for o in tel_pro + [spina_pro, cavo_pro]:
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    nome = "Cavo" if o.name.startswith("RIF_Cavo") else "Telefono"
    a = {"id": o.name, "label": nome, "piece": nome,
         "color": [round(255 * c ** (1 / 2.2)) for c in o.data.materials[0].diffuse_color[:3]],
         "vertices": [[round(c, 2) for c in o.matrix_world @ v.co] for v in bm.verts],
         "triangles": [[v.index for v in f.verts] for f in bm.faces]}
    if o is cavo_pro:
        a["stretch"] = list(CAVO_DRITTO)
    if o.name.startswith("RIF_Telefono_Schermo") and os.path.exists(os.path.join(ROOT, HOME)):
        xs, ys = [v.co.x for v in bm.verts], [v.co.y for v in bm.verts]   # bordo dello schermo = estremi della mesh
        a.update(uv=[[round(q, 4) for q in uv_schermo(v.co, min(xs), max(xs), min(ys), max(ys))] for v in bm.verts], image=HOME)
    acc_out.append(a)
    bm.free()
with open(os.path.join(ROOT, "dati", "accessori.json"), "w", encoding="utf-8") as f:
    json.dump(acc_out, f, separators=(",", ":"))

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
