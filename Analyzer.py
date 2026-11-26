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

    # ── class 9/10  N-/N-  (animals, loanwords) ───────────────────────────────
    # In Swahili class 9/10, the nasal prefix fuses with the stem-initial
    # consonant (nasal assimilation), so the stem is stored WITH the nasal
    # already incorporated and the prefix is empty ("").
    # sg and pl surface forms are identical; number marked by verb agreement.
    {"stem": "nyumba",  "class_pair": "9/10", "sg_prefix": "",    "pl_prefix": "",
     "sg_form": "nyumba",   "pl_form": "nyumba",    "gloss": "house"},
    {"stem": "ndege",   "class_pair": "9/10", "sg_prefix": "",    "pl_prefix": "",
     "sg_form": "ndege",    "pl_form": "ndege",     "gloss": "bird/aeroplane"},
    {"stem": "mbwa",    "class_pair": "9/10", "sg_prefix": "",    "pl_prefix": "",
     "sg_form": "mbwa",     "pl_form": "mbwa",      "gloss": "dog"},
    {"stem": "nguo",    "class_pair": "9/10", "sg_prefix": "",    "pl_prefix": "",
     "sg_form": "nguo",     "pl_form": "nguo",      "gloss": "cloth/clothes"},
    {"stem": "ndizi",   "class_pair": "9/10", "sg_prefix": "",    "pl_prefix": "",
     "sg_form": "ndizi",    "pl_form": "ndizi",     "gloss": "banana"},
]

# ──────────────────────────────────────────────────────────────────────────────
# BUILD INDICES
# ──────────────────────────────────────────────────────────────────────────────

# surface word → lexical entry info
_SURFACE_INDEX: dict[str, dict] = {}

# stem string → lexicon entry
_STEM_INDEX: dict[str, dict] = {}


def _build_indices() -> None:
    _SURFACE_INDEX.clear()
    _STEM_INDEX.clear()
    for entry in LEXICON:
        sg, pl = entry["sg_form"], entry["pl_form"]
        if sg not in _SURFACE_INDEX:
            _SURFACE_INDEX[sg] = {
                "stem": entry["stem"], "class_pair": entry["class_pair"],
                "number": "sg",       "prefix": entry["sg_prefix"],
            }
        if pl not in _SURFACE_INDEX:
            _SURFACE_INDEX[pl] = {
                "stem": entry["stem"], "class_pair": entry["class_pair"],
                "number": "pl",       "prefix": entry["pl_prefix"],
            }
        _STEM_INDEX[entry["stem"]] = entry


_build_indices()

# All known prefixes, longest first (for greedy prefix-stripping in analyse)
_ALL_PREFIXES = sorted(
    {e["sg_prefix"] for e in LEXICON} | {e["pl_prefix"] for e in LEXICON},
    key=len, reverse=True,
)

# TASK 2 – ANALYSER  (surface → lexical)
# ──────────────────────────────────────────────────────────────────────────────

def analyse(word: str) -> dict:
    """
    Analyse a surface word form and return a structured lexical result.

    Strategy
    --------
    1. Exact look-up in the surface-form index (covers all stored forms).
    2. Prefix-stripping with re.match(), trying each known prefix
       longest-first; if the remainder matches a known stem, return
       the structured result.
    3. If neither step succeeds, return {"result": "no analysis found"}.

    Returns
    -------
    dict  with keys: prefix, stem, class_pair, number, result
          or {"result": "no analysis found"} for unrecognised words.
    """
    word = word.strip().lower()

    # Step 1 – exact surface-form lookup
    if word in _SURFACE_INDEX:
        entry = _SURFACE_INDEX[word]
        return {
            "prefix":     entry["prefix"],
            "stem":       entry["stem"],
            "class_pair": entry["class_pair"],
            "number":     entry["number"],
            "result":     "analysis found",
        }

    # Step 2 – prefix-stripping via re.match (longest-match first)
    for prefix in _ALL_PREFIXES:
        if prefix == "":
            continue  # skip empty prefix; can't strip nothing
        pattern = r"^" + re.escape(prefix) + r"(.+)$"
        m = re.match(pattern, word)
        if m:
            remainder = m.group(1)
            if remainder in _STEM_INDEX:
                entry  = _STEM_INDEX[remainder]
                number = "sg" if prefix == entry["sg_prefix"] else "pl"
                return {
                    "prefix":     prefix,
                    "stem":       remainder,
                    "class_pair": entry["class_pair"],
                    "number":     number,
                    "result":     "analysis found",
                }

    # Step 3 – unrecognised word
    return {"result": "no analysis found"}

# ──────────────────────────────────────────────────────────────────────────────
# TASK 3 – GENERATOR  (lexical → surface)
# ──────────────────────────────────────────────────────────────────────────────

def generate(stem: str, class_pair: str, number: str) -> str | None:
    """
    Generate the correct surface word form from a lexical triple.

    Parameters
    ----------
    stem       : noun stem string  (e.g. 'onto', 'tabu', 'yumba')
    class_pair : noun-class pair   (e.g. '1/2', '7/8', '9/10')
    number     : 'sg' (singular) or 'pl' (plural)

    Returns
    -------
    str  – surface form (prefix concatenated with stem)
    None – if the (stem, class_pair) pair is not in the lexicon

    Algorithm
    ---------
    1. Search LEXICON for an entry where entry['stem'] == stem
       and entry['class_pair'] == class_pair.
    2. Select sg_prefix (if number == 'sg') or pl_prefix (if number == 'pl').
    3. Concatenate prefix + stem and return the resulting surface form.

    Round-trip property
    -------------------
    For every lexicon entry E and number N in {'sg', 'pl'}:
        analyse(generate(E['stem'], E['class_pair'], N))['stem'] == E['stem']
    """
    stem   = stem.strip().lower()
    number = number.strip().lower()

    if number not in ("sg", "pl"):
        raise ValueError(f"number must be 'sg' or 'pl', got {number!r}")

    for entry in LEXICON:
        if entry["stem"] == stem and entry["class_pair"] == class_pair:
            # Return the pre-verified stored surface form directly,
            # which correctly handles all prefix–stem fusions (e.g. class 9/10
            # nasal assimilation: nd+dege is stored as 'ndege', not 'nddege').
            return entry["sg_form"] if number == "sg" else entry["pl_form"]

    return None  # (stem, class_pair) not found in lexicon


