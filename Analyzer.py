"""
analyser.py  –  Swahili morphological transducer  (Tasks 1–3)
==============================================================
Lexical type  : (stem, class_pair, number)
Surface type  : prefixed word form

Task 1  – Lexicon (Swahili noun stems across 5 class-pairs)
Task 2  – analyse(word)            surface → lexical
Task 3  – generate(stem, cp, num)  lexical → surface
"""

import re

# ──────────────────────────────────────────────────────────────────────────────
# TASK 1 – LEXICON
# ──────────────────────────────────────────────────────────────────────────────
# Each entry: stem, class_pair, sg_prefix, pl_prefix, sg_form, pl_form, gloss
#
# Noun-class pairs (Bantu numbering):
#   1/2   – human (sg / pl)
#   3/4   – trees, plants, rivers
#   5/6   – body parts, natural objects, fruits
#   7/8   – general objects / implements
#   9/10  – animals, loanwords
#
# Sources: self-elicited + Ashton (1944), cross-checked against
#          Mohamed (2001) and TUKI Standard Swahili Dictionary (2004).
# ──────────────────────────────────────────────────────────────────────────────

LEXICON = [
    # ── class 1/2  m-/wa-  (human nouns) ─────────────────────────────────────
    {"stem": "tu",      "class_pair": "1/2",  "sg_prefix": "m",   "pl_prefix": "wa",
     "sg_form": "mtu",      "pl_form": "watu",       "gloss": "person"},
    {"stem": "toto",    "class_pair": "1/2",  "sg_prefix": "m",   "pl_prefix": "wa",
