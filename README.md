# På Ljungen – bildarkiv

Perceptuella bildhashar (dHash, 64 bitar) för bilderna i tidskriften
"På Ljungen" (Kulturföreningen Calluna). Används för att snabbt kontrollera
om en bild redan har publicerats i något nummer.

Repot innehåller bara hashkoder och skript – inga bilder eller texter ur tidskriften.

## Filer
- `pljungen_bildhashar.csv` – sökarkivet: 1 606 bilder, rensat från logotyper,
  annonser och vinjetter som förekommer i fler än fyra nummer.
- `pljungen_aterkommande.csv` – hashar för de 33 grupperna av återkommande
  logotyper/annonser/vinjetter, med kolumnen `antal_nummer`.
- `jamfor_bild.py` – räknar ut hashen för en ny bild och jämför mot arkivet.
  Kräver Python 3 och Pillow.

## Användning
```
git clone https://github.com/<användarnamn>/pljungen-bildarkiv
pip install pillow
python pljungen-bildarkiv/jamfor_bild.py <bildfil>
```

## Tolkning av avståndet (antal olika bitar av 64)
- **0–5**: mycket sannolikt samma bild
- **6–10**: möjlig träff – kontrollera visuellt
- **över 10**: sannolikt inte publicerad förut

Skriver skriptet "OBS: liknar en återkommande bild" är bilden troligen en
logotyp, annons eller vinjett som finns i många nummer.

## Begränsningar
Metoden hittar samma eller nästan samma bildfil (samma skanning, omkomprimerad
eller lätt beskuren). Den hittar inte samma motiv fotograferat vid ett annat
tillfälle, kraftigt beskurna eller roterade varianter. Mycket enkla bilder
(enfärgade ytor, text på vit bakgrund) kan ge falska träffar. Bildjämförelsen
är algoritmisk och ingen garanti.

## Uppdatera med nya nummer
Räkna fram hasharna för det nya numrets bilder med samma `dhash()`-funktion
som i `jamfor_bild.py` och lägg till raderna i `pljungen_bildhashar.csv`.
Ladda sedan upp den nya filen här (Add file → Upload files), så ersätts den gamla.
