#!/usr/bin/env python3
"""
Jämför en eller flera bilder mot bildarkivet för tidskriften "På Ljungen"
(Kulturföreningen Calluna) med perceptuell hash (dHash, 64 bitar).

Sökarkivet (pljungen_bildhashar.csv) är rensat från logotyper, annonser och
andra bilder som återkommer i fler än fyra nummer. Liknar den nya bilden en
sådan återkommande bild sägs det separat.

Användning:
    python jamfor_bild.py bild.jpg [fler_bilder.jpg ...] [--topp 10]

Kräver: Pillow  (pip install pillow)
"""
import argparse
import csv
import os
import sys
import warnings
from collections import OrderedDict

from PIL import Image

warnings.filterwarnings("ignore", category=DeprecationWarning)

MAPP = os.path.dirname(os.path.abspath(__file__))


def dhash(img, hash_size=8):
    """Exakt samma funktion som användes när arkivets hashar räknades fram."""
    img = img.convert("L").resize((hash_size + 1, hash_size))
    pixels = list(img.getdata())
    bits = []
    for row in range(hash_size):
        row_pixels = pixels[row * (hash_size + 1):(row + 1) * (hash_size + 1)]
        for col in range(hash_size):
            bits.append(1 if row_pixels[col] > row_pixels[col + 1] else 0)
    val = 0
    for b in bits:
        val = (val << 1) | b
    return "%016x" % val


def hamming(a, b):
    return bin(a ^ b).count("1")


def bedomning(avstand):
    if avstand <= 5:
        return "mycket sannolikt samma bild"
    if avstand <= 10:
        return "möjlig träff - kontrollera visuellt"
    return "sannolikt inte publicerad"


def las_arkiv(csv_path):
    if not os.path.exists(csv_path):
        return []
    with open(csv_path, encoding="utf-8") as f:
        rader = list(csv.DictReader(f))
    for r in rader:
        r["_h"] = int(r["dhash"], 16)   # räkna om hex en gång, inte vid varje jämförelse
    return rader


def kort_nummer(issue_file):
    """'På Ljungen 07_low.pdf' / 'Pa-Ljungen-85_low.pdf' -> '07' / '85';
    'Pa_Ljungen_2025_03.pdf' -> '2025_03'"""
    namn = os.path.splitext(issue_file)[0]
    if namn.lower().endswith("_low"):
        namn = namn[:-4]
    for prefix in ("På Ljungen ", "Pa-Ljungen-", "På-Ljungen-", "Pa_Ljungen_", "pa_ljungen_"):
        if namn.startswith(prefix):
            return namn[len(prefix):]
    return issue_file


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("bilder", nargs="+", help="Bildfil(er) att kontrollera")
    p.add_argument("--csv", default=os.path.join(MAPP, "pljungen_bildhashar.csv"))
    p.add_argument("--aterkommande", default=os.path.join(MAPP, "pljungen_aterkommande.csv"))
    p.add_argument("--topp", type=int, default=10, help="Antal bästa träffar att visa (standard 10)")
    args = p.parse_args()

    arkiv = las_arkiv(args.csv)
    aterkommande = las_arkiv(args.aterkommande)

    for bild in args.bilder:
        try:
            with Image.open(bild) as im:
                h_hex = dhash(im)
                bredd, hojd = im.size
        except Exception as e:
            print(f"\n{bild}: kunde inte läsas ({e})", file=sys.stderr)
            continue
        h = int(h_hex, 16)

        print(f"\n=== {bild}  (dHash {h_hex}, {bredd}x{hojd}) ===")

        # 1. Återkommande logotyp/annons?
        if aterkommande:
            avst, rad = min(((hamming(h, r["_h"]), r) for r in aterkommande), key=lambda t: t[0])
            if avst <= 5:
                print(f"OBS: liknar en återkommande bild (logotyp/annons/vinjett) som finns i "
                      f"{rad['antal_nummer']} nummer, t.ex. nr {kort_nummer(rad['issue_file'])} "
                      f"{rad['image_file']} (avstånd {avst}).")
            else:
                print(f"Liknar ingen återkommande logotyp/annons (närmaste avstånd {avst}).")

        # 2. Sökarkivet. Identiska hashar slås ihop till en rad.
        traffar = sorted(((hamming(h, r["_h"]), r) for r in arkiv), key=lambda t: t[0])
        grupper = OrderedDict()
        for avst, rad in traffar:
            nyckel = rad["dhash"]
            if nyckel not in grupper:
                if len(grupper) >= args.topp:
                    break
                grupper[nyckel] = (avst, [])
            grupper[nyckel][1].append(rad)

        basta = traffar[0][0] if traffar else 99
        print(f"Slutsats: {bedomning(basta)} (bästa avstånd {basta})")
        print(f"{'Avst.':>5}  {'Nummer : bild':<44} {'Storlek':<10} Bedömning")
        for avst, rader in grupper.values():
            plats = ", ".join(f"{kort_nummer(r['issue_file'])}:{r['image_file']}" for r in rader)
            storlek = f"{rader[0]['width']}x{rader[0]['height']}"
            print(f"{avst:>5}  {plats:<44} {storlek:<10} {bedomning(avst)}")

    print("\nObs: algoritmisk bildjämförelse, ingen garanti. Kontrollera de bästa träffarna visuellt.")


if __name__ == "__main__":
    main()
