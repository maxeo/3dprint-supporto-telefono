# Supporto Telefono

Supporto pieghevole da scrivania per telefono, ispirato a quello delle foto in `originale/`: base, braccio telescopico, piatto con mensola. Le due cerniere sono viti M4 strette da pomelli zigrinati (frizione regolabile a mano), lo sfilo del braccio si blocca con un terzo pomello.

**Guida di stampa e montaggio:** [guida.html](guida.html)

## Pezzi

| Sigla | File | Ingombro di stampa, mm | Copie |
|---|---|---|---|
| P01 | `stl/P01_Base.stl` | 175 × 90 × 27,5 | 1 |
| P02 | `stl/P02_Guaina.stl` | 110 × 34 × 20 | 1 |
| P03 | `stl/P03_Slitta.stl` | 105,6 × 30 × 17,2 | 1 |
| P04 | `stl/P04_Piatto.stl` | 150 × 80 × 29 | 1 |
| P05 | `stl/P05_Appoggio.stl` | 30 × 70 × 16 | 1 |
| P06 | `stl/P06_Pomello.stl` | Ø22 × 11 | 3 |

Viteria da comprare: 2 × M4×50 testa esagonale, 1 × M4×12 testa esagonale, 3 dadi M4, 2 × M3×10 testa cilindrica, 2 dadi M3. Facoltativi: 4 piedini adesivi Ø10.

Tutti i pezzi si stampano senza supporti (PETG, 0,2 mm; parametri proposti nella guida, da verificare).

## Misure principali

- Chiuso: 175 × 90 × 57 mm (braccio sulla base, piatto sul braccio).
- Sfilo del braccio fino a 40 mm; la vite di blocco corre in una scanalatura che fa da fermo.
- Telefono fino a 14 mm di spessore con la cover; asola per il cavo nella mensola.
- Cerniere: nocca 30 mm fra orecchie da 9 mm, 0,2 mm di gioco per lato.

## Rigenerare

```
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python blender/costruisci.py
"C:/Program Files/Blender Foundation/Blender 5.2/5.2/python/bin/python.exe" dati/scrivi_spec.py
"C:/Program Files/Blender Foundation/Blender 5.2/5.2/python/bin/python.exe" "%USERPROFILE%/.claude/skills/guida-stampa-3d/scripts/build_guide.py" dati/guida_spec.json
```

`costruisci.py` scrive gli STL, `blender/Supporto_Telefono.blend` (collezioni PEZZI_MONTATI, PIEGATO nascosta, PEZZI_STAMPA nascosta) e `dati/geometria.json` con pesi, spigoli aperti e i controlli: nessuna interferenza fra pezzi e viti, aperto e chiuso; baricentro del telefono sopra la base.

## Note

- Non ancora stampato: giochi di cerniere e slitta (`GIOCO_NOCCA`, `GIOCO_SLITTA`) e sedi a pressione dei dadi sono valori di partenza.
- Con tablet pesanti non inclinare troppo indietro braccio e piatto: nella posa della scena il baricentro di un telefono da 200 g cade 21 mm dentro la base.
