# -*- coding: utf-8 -*-
"""Extract 100 benchmark pairs from downloaded FLORES-200 archive."""
import tarfile
from pathlib import Path

archive_path = Path("scratch/flores200_dataset.tar.gz")
assert archive_path.exists(), "flores200_dataset.tar.gz not found"

print(f"Reading {archive_path}...")
tf = tarfile.open(archive_path, "r:gz")

bn_lines = []
en_lines = []

for m in tf.getmembers():
    if m.name.endswith("devtest/ben_Beng.devtest"):
        f = tf.extractfile(m)
        bn_lines = [line.decode("utf-8").strip() for line in f.readlines()]
    elif m.name.endswith("devtest/eng_Latn.devtest"):
        f = tf.extractfile(m)
        en_lines = [line.decode("utf-8").strip() for line in f.readlines()]

print(f"Extracted {len(bn_lines)} Bengali and {len(en_lines)} English sentences.")
assert len(bn_lines) == len(en_lines) and len(bn_lines) >= 100

out_dir = Path("tests/mt_eval")
out_dir.mkdir(parents=True, exist_ok=True)
tsv_path = out_dir / "flores_bn_en_100.tsv"

with open(tsv_path, "w", encoding="utf-8") as out:
    out.write("# Source: FLORES-200 devtest (Meta AI / NLLB Team, CC-BY-SA-4.0)\n")
    out.write("# Commit/Source: https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz\n")
    out.write("# License: CC-BY-SA-4.0\n")
    out.write("# Description: 100 parallel sentence pairs ben_Beng <-> eng_Latn\n")
    out.write("id\tbn\ten\n")
    for i in range(100):
        b = bn_lines[i].replace("\t", " ")
        e = en_lines[i].replace("\t", " ")
        out.write(f"{i+1}\t{b}\t{e}\n")

print(f"Successfully generated {tsv_path} with 100 aligned benchmark pairs.")
