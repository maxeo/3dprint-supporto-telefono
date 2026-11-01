"""Pomelli di prova con la madrevite passante: stessa forma di P06/P10, per provare il filetto sulle viti.

Usa le costanti e gli helper di costruisci.py (eseguito fino a "pieces = {}") e scrive gli STL in stl/prove/.
"""
import os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "costruisci.py")
codice = open(SRC, encoding="utf-8").read()
exec(compile(codice[:codice.index("\npieces = {}")], SRC, "exec"))
codice_k = codice[codice.index("def k_r("):codice.index("\n\ndef pomello(")]
exec(compile(codice_k, SRC, "exec"))

dir_prove = os.path.join(ROOT, "stl", "prove")
os.makedirs(dir_prove, exist_ok=True)
esito = {}
for nome, d in (("P06_Pomello_Passante", D_CERN), ("P10_Pomello_Appoggio_Passante", D_MORSA)):
    o = radial_solid(k_r, 0, K_H, nome, C_TMP, seg=144, dz=0.25)
    boolean(o, madrevite(d, -0.5, K_H + 0.5, "mv", invito=(True, True)), 'DIFFERENCE')
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    bm.to_mesh(o.data); bm.free()
    write_stl(o, Matrix(), os.path.join(dir_prove, nome + ".stl"))
    esito[nome] = info(o)
print("PROVA_POMELLI", esito)
