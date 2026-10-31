# Supporto Telefono

Supporto pieghevole da scrivania per telefono, ispirato a quello delle foto in `originale/`: base, braccio telescopico a tratti, prolunghe da aggiungere quante se ne vuole, piatto con appoggio regolabile. Le due cerniere sono viti M4 strette da pomelli zigrinati (frizione regolabile a mano); ogni tratto del braccio ha una morsa a pomello; l'appoggio scorre su una guida a T nel piatto e si blocca col suo pomello.

**Guida di stampa e montaggio:** [guida.html](guida.html)

## Pezzi

| Sigla | File | Ingombro di stampa, mm | Copie |
|---|---|---|---|
| P01 | `stl/P01_Base.stl` | 185 × 90 × 27,5 | 1 |
| P02 | `stl/P02_Guaina.stl` | 110 × 34 × 20 | 1 |
| P03 | `stl/P03_Slitta.stl` | 107 × 30 × 20 | 1 |
| P04 | `stl/P04_Piatto.stl` | 150 × 80 × 32 | 1 |
| P05 | `stl/P05_Appoggio.stl` | 35,5 × 20,3 × 70 | 1 |
| P06 | `stl/P06_Pomello.stl` | Ø22 × 11 | 4 + 1 per prolunga |
| P07 | `stl/P07_Prolunga.stl` | 185 × 34 × 20 | quante ne vuoi (anche 0) |

Viteria, tutta M4 a testa esagonale: 2 × M4×50 (cerniere), 2 × M4×12 (morsa della guaina, appoggio), 4 dadi M4; per ogni prolunga 1 × M4×12 e 1 dado in più. Facoltativi: 4 piedini adesivi Ø10.

Tutti i pezzi si stampano senza supporti (PETG, 0,2 mm; parametri proposti nella guida, da verificare).

## Misure principali

- Mensola dal tavolo, braccio dritto: 123–232 mm senza prolunghe, 223–372 con una, 323–512 con due, 423–652 con tre (dal tutto chiuso al tutto sfilato con l’appoggio in alto). Nella guida si sceglie il numero di prolunghe (di solito 1).
- Ogni tratto (guaina o prolunga) sfila fino a 40 mm; la vite della morsa corre in una scanalatura che fa da fermo.
- Barre con una nervatura davanti che corre nella fessura del canale: arriva a filo, così prolunghe e slitta si stampano coricate senza supporti.
- Appoggio: corsa di 73 mm lungo il piatto; telefono fino a 14 mm con la cover; asola per il cavo.
- Chiuso (senza prolunghe): 185 × 90 × 58 mm.

## Rigenerare

```
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python blender/costruisci.py
"C:/Program Files/Blender Foundation/Blender 5.2/5.2/python/bin/python.exe" dati/scrivi_spec.py
"C:/Program Files/Blender Foundation/Blender 5.2/5.2/python/bin/python.exe" "%USERPROFILE%/.claude/skills/guida-stampa-3d/scripts/build_guide.py" dati/guida_spec.json
```

`costruisci.py` scrive gli STL, `blender/Supporto_Telefono.blend` (collezioni PEZZI_MONTATI; nascoste CON_PROLUNGHE, PIEGATO e PEZZI_STAMPA) e `dati/geometria.json` con pesi, spigoli aperti e i controlli: nessuna interferenza fra pezzi e viti aperto, con due prolunghe e chiuso; altezze della mensola; baricentro del telefono rispetto alla base.

## Note

- Non ancora stampato: giochi di cerniere e barre (`GIOCO_NOCCA`, `GIOCO_SLITTA`) e sedi a pressione dei dadi sono valori di partenza.
- Con le prolunghe, o con l'appoggio tutto in alto, tieni il braccio dritto: con il braccio a 95° e l'appoggio in alto il baricentro di un telefono da 200 g cade 4 mm fuori dalla base.
