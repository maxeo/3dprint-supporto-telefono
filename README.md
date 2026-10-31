# Supporto Telefono

Supporto pieghevole da scrivania per telefono, ispirato a quello delle foto in `originale/`: base, braccio telescopico a tratti, prolunghe da aggiungere quante se ne vuole, piatto con appoggio regolabile. Le due cerniere sono viti stampate strette da pomelli zigrinati filettati (frizione regolabile a mano); ogni tratto del braccio ha una morsa a pomello; l'appoggio scorre su una guida a T nel piatto e si blocca col suo pomello. Tutto stampato, viti e dadi compresi: non serve viteria.

**Guida di stampa e montaggio:** [guida.html](guida.html)

## Pezzi

| Sigla | File | Ingombro di stampa, mm | Copie |
|---|---|---|---|
| P01 | `stl/P01_Base.stl` | 185 × 90 × 27,5 | 1 |
| P02 | `stl/P02_Guaina.stl` | 110 × 35 × 20 | 1 |
| P03 | `stl/P03_Slitta.stl` | 107 × 30 × 20 | 1 |
| P04 | `stl/P04_Piatto.stl` | 150 × 80 × 32 | 1 |
| P05 | `stl/P05_Appoggio.stl` | 35,5 × 20,3 × 70 | 1 |
| P06 | `stl/P06_Pomello.stl` (cerniere, madrevite Ø10) | Ø22 × 11 | 2 |
| P07 | `stl/P07_Prolunga.stl` | 185 × 35 × 20 | quante ne vuoi (anche 0) |
| P08 | `stl/P08_Vite_Cerniera.stl` (Ø10 × 57, testa tonda e collo quadro) | Ø18 × 61 | 2 |
| P09 | `stl/P09_Vite_Appoggio.stl` (Ø8, testa quadra) | 12,6 × 12,6 × 16,9 | 1 |
| P10 | `stl/P10_Pomello_Appoggio.stl` (madrevite Ø8) | Ø22 × 11 | 1 |
| P11 | `stl/P11_Pomello_Morsa.stl` (pomello con vite Ø8 × 12) | Ø22 × 23 | 1 + 1 per prolunga |
| P12 | `stl/P12_Dado_Morsa.stl` (dado esagonale 13, madrevite Ø8) | 13 × 15 × 5 | 1 + 1 per prolunga |

Filetti trapezoidali passo 2,5 (come le palline), 0,35 mm di gioco radiale; viti e pomelli si stampano in piedi senza supporti. Viti e dadi pieni, strato 0,16 mm. Facoltativi: 4 piedini adesivi Ø10.

Tutti i pezzi si stampano senza supporti (PETG, 0,2 mm; parametri proposti nella guida, da verificare).

## Misure principali

- Mensola dal tavolo, braccio dritto: 125–230 mm senza prolunghe, 225–370 con una, 325–510 con due, 425–650 con tre (dal tutto chiuso al tutto sfilato con l’appoggio in alto). Nella guida si sceglie il numero di prolunghe (di solito 1).
- Ogni tratto (guaina o prolunga) sfila fino a 40 mm; la vite del pomello della morsa (P11, nel dado P12) corre in una scanalatura che fa da fermo.
- Barre con una nervatura davanti che corre nella fessura del canale: arriva a filo, così prolunghe e slitta si stampano coricate senza supporti.
- Appoggio: corsa di 69 mm lungo il piatto; telefono fino a 14 mm con la cover; asola per il cavo.
- Chiuso (senza prolunghe): 185 × 90 × 58 mm.

## Rigenerare

```
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python blender/costruisci.py
"C:/Program Files/Blender Foundation/Blender 5.2/5.2/python/bin/python.exe" dati/scrivi_spec.py
"C:/Program Files/Blender Foundation/Blender 5.2/5.2/python/bin/python.exe" "%USERPROFILE%/.claude/skills/guida-stampa-3d/scripts/build_guide.py" dati/guida_spec.json
```

`costruisci.py` scrive gli STL, `blender/Supporto_Telefono.blend` (collezioni PEZZI_MONTATI; nascoste CON_PROLUNGHE, PIEGATO e PEZZI_STAMPA) e `dati/geometria.json` con pesi, spigoli aperti e i controlli: nessuna interferenza fra i pezzi (viti comprese, coi filetti in fase) aperto, con tre prolunghe e chiuso; altezze della mensola; baricentro del telefono rispetto alla base.

## Note

- Non ancora stampato: giochi di cerniere e barre (`GIOCO_NOCCA`, `GIOCO_SLITTA`) e il gioco dei filetti (`F_GIOCO`) sono valori di partenza.
- Con le prolunghe, o con l'appoggio tutto in alto, tieni il braccio dritto: con il braccio a 95° e l'appoggio in alto il baricentro di un telefono da 200 g cade 3 mm fuori dalla base.
