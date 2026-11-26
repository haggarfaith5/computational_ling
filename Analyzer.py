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
     "sg_form": "mtoto",    "pl_form": "watoto",     "gloss": "child"},
    {"stem": "zee",     "class_pair": "1/2",  "sg_prefix": "m",   "pl_prefix": "wa",
     "sg_form": "mzee",     "pl_form": "wazee",      "gloss": "elder/old person"},
    {"stem": "alimu",   "class_pair": "1/2",  "sg_prefix": "mw",  "pl_prefix": "wa",
     "sg_form": "mwalimu",  "pl_form": "walimu",     "gloss": "teacher"},
    {"stem": "ana",     "class_pair": "1/2",  "sg_prefix": "mw",  "pl_prefix": "wa",
     "sg_form": "mwana",    "pl_form": "wana",       "gloss": "son/child"},

    # ── class 3/4  m-/mi-  (trees, rivers, body parts) ───────────────────────
    {"stem": "ti",      "class_pair": "3/4",  "sg_prefix": "m",   "pl_prefix": "mi",
     "sg_form": "mti",      "pl_form": "miti",       "gloss": "tree"},
    {"stem": "to",      "class_pair": "3/4",  "sg_prefix": "m",   "pl_prefix": "mi",
     "sg_form": "mto",      "pl_form": "mito",       "gloss": "river"},
    {"stem": "kono",    "class_pair": "3/4",  "sg_prefix": "m",   "pl_prefix": "mi",
     "sg_form": "mkono",    "pl_form": "mikono",     "gloss": "hand/arm"},
    {"stem": "lango",   "class_pair": "3/4",  "sg_prefix": "m",   "pl_prefix": "mi",
     "sg_form": "mlango",   "pl_form": "milango",    "gloss": "door"},
    {"stem": "mea",     "class_pair": "3/4",  "sg_prefix": "m",   "pl_prefix": "mi",
     "sg_form": "mmea",     "pl_form": "mimea",      "gloss": "plant"},

    # ── class 5/6  Ø|ji-/ma-  (fruits, paired body parts) ────────────────────
    # ji- prefix: used for some class-5 nouns; Ø: others have no overt prefix
    {"stem": "cho",     "class_pair": "5/6",  "sg_prefix": "ji",  "pl_prefix": "ma",
     "sg_form": "jicho",    "pl_form": "macho",      "gloss": "eye"},
    {"stem": "tunda",   "class_pair": "5/6",  "sg_prefix": "",    "pl_prefix": "ma",
     "sg_form": "tunda",    "pl_form": "matunda",    "gloss": "fruit"},
    {"stem": "gari",    "class_pair": "5/6",  "sg_prefix": "",    "pl_prefix": "ma",
     "sg_form": "gari",     "pl_form": "magari",     "gloss": "vehicle/car"},
    {"stem": "ina",     "class_pair": "5/6",  "sg_prefix": "j",   "pl_prefix": "ma",
     "sg_form": "jina",     "pl_form": "majina",     "gloss": "name"},
    {"stem": "bavu",    "class_pair": "5/6",  "sg_prefix": "",    "pl_prefix": "ma",
     "sg_form": "bavu",     "pl_form": "mabavu",     "gloss": "rib/side"},

    # ── class 7/8  ki-/vi-  (implements, languages, diminutives) ─────────────
    {"stem": "tabu",    "class_pair": "7/8",  "sg_prefix": "ki",  "pl_prefix": "vi",
     "sg_form": "kitabu",   "pl_form": "vitabu",     "gloss": "book"},
    {"stem": "su",      "class_pair": "7/8",  "sg_prefix": "ki",  "pl_prefix": "vi",
     "sg_form": "kisu",     "pl_form": "visu",       "gloss": "knife"},
    {"stem": "kapu",    "class_pair": "7/8",  "sg_prefix": "ki",  "pl_prefix": "vi",
     "sg_form": "kikapu",   "pl_form": "vikapu",     "gloss": "basket"},
    {"stem": "chwa",    "class_pair": "7/8",  "sg_prefix": "ki",  "pl_prefix": "vi",
     "sg_form": "kichwa",   "pl_form": "vichwa",     "gloss": "head"},
    {"stem": "azi",     "class_pair": "7/8",  "sg_prefix": "ki",  "pl_prefix": "vi",
     "sg_form": "kiazi",    "pl_form": "viazi",      "gloss": "potato"},