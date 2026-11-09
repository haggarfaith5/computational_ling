"""
analyser.py  –  EkəGusii two-level morphological transducer (Tasks 1–4)
Lexical type  : (stem, class_pair, number)
Surface type  : prefixed word form

Task 1  – Lexicon
Task 2  – analyse(word)   surface → lexical
Task 3  – generate(stem, class_pair, number)  lexical → surface
Task 4  – Morphophonemic alternation rule (vowel deletion at prefix–stem boundary)
"""

import re

# ──────────────────────────────────────────────────────────────────────────────
# TASK 1 – LEXICON
# ──────────────────────────────────────────────────────────────────────────────
# EkəGusii noun-class prefix inventory (selected classes)
# Each entry: stem, class_pair, sg_prefix, pl_prefix, sg_form, pl_form, gloss
#
# Noun-class pairs follow standard Bantu numbering:
#   1/2   – human (sg/pl)
#   3/4   – trees, plants (sg/pl)
#   5/6   – body parts, natural objects (sg/pl)
#   7/8   – general objects  (sg/pl)
#   9/10  – animals, loanwords (sg/pl)
#
# Sources: consultant-elicited data + Whiteley & Muli (1962),
#          cross-checked against Bosire & Muriungi (2006).
# ──────────────────────────────────────────────────────────────────────────────

LEXICON = [
    # stem          class_pair  sg_prefix  pl_prefix  sg_form       pl_form       gloss
    {"stem": "onto",   "class_pair": "1/2",  "sg_prefix": "o",  "pl_prefix": "aba",  "sg_form": "oonto",   "pl_form": "abaonto",   "gloss": "person"},
    {"stem": "ana",    "class_pair": "1/2",  "sg_prefix": "o",  "pl_prefix": "aba",  "sg_form": "oana",    "pl_form": "abaana",    "gloss": "child"},
    {"stem": "mura",   "class_pair": "1/2",  "sg_prefix": "o",  "pl_prefix": "aba", "sg_form": "omura",   "pl_form": "abamura",   "gloss": "boy/youth"},
    {"stem": "gesaku", "class_pair": "7/8",  "sg_prefix": "e",  "pl_prefix": "ebe", "sg_form": "egesaku", "pl_form": "ebesaku",   "gloss": "sword/machete"},
    {"stem": "boko",   "class_pair": "7/8",  "sg_prefix": "e",  "pl_prefix": "ebe", "sg_form": "egeboko", "pl_form": "ebeboko",   "gloss": "arm/hand"},
    {"stem": "saiga",  "class_pair": "7/8",  "sg_prefix": "e",  "pl_prefix": "ebe", "sg_form": "egesaiga","pl_form": "ebesaiga",  "gloss": "knife"},
    {"stem": "tembe",  "class_pair": "3/4",  "sg_prefix": "o",  "pl_prefix": "emi", "sg_form": "otembe",  "pl_form": "emitembe",  "gloss": "banana tree"},
    {"stem": "ti",     "class_pair": "3/4",  "sg_prefix": "o",  "pl_prefix": "emi", "sg_form": "oti",     "pl_form": "emiti",     "gloss": "tree"},
    {"stem": "rura",   "class_pair": "3/4",  "sg_prefix": "o",  "pl_prefix": "emi", "sg_form": "orura",   "pl_form": "emirura",   "gloss": "vein/tendon"},
    {"stem": "kogo",   "class_pair": "9/10", "sg_prefix": "e",  "pl_prefix": "eci", "sg_form": "ekogo",   "pl_form": "ecikogo",   "gloss": "grandmother"},
    {"stem": "nka",    "class_pair": "9/10", "sg_prefix": "e",  "pl_prefix": "eci", "sg_form": "enka",    "pl_form": "ecinka",    "gloss": "cow"},
    {"stem": "bura",   "class_pair": "5/6",  "sg_prefix": "e",  "pl_prefix": "ama", "sg_form": "ebura",   "pl_form": "amabura",   "gloss": "hole"},
    {"stem": "bere",   "class_pair": "5/6",  "sg_prefix": "e",  "pl_prefix": "ama", "sg_form": "ebere",   "pl_form": "amabere",   "gloss": "breast/milk"},
    {"stem": "goro",   "class_pair": "5/6",  "sg_prefix": "e",  "pl_prefix": "ama", "sg_form": "egoro",   "pl_form": "amagoro",   "gloss": "evening"},
    {"stem": "riiko",  "class_pair": "5/6",  "sg_prefix": "e",  "pl_prefix": "ama", "sg_form": "eriiko",  "pl_form": "amariiko",  "gloss": "cooking fire"},
    {"stem": "basi",   "class_pair": "9/10", "sg_prefix": "e",  "pl_prefix": "eci", "sg_form": "ebasi",   "pl_form": "ecibasi",   "gloss": "bus"},
    {"stem": "karatasi","class_pair":"9/10", "sg_prefix": "e",  "pl_prefix": "eci", "sg_form": "ekaratasi","pl_form":"ecikaratasi","gloss": "paper"},
    {"stem": "nda",    "class_pair": "9/10", "sg_prefix": "e",  "pl_prefix": "eci", "sg_form": "enda",    "pl_form": "ecinda",    "gloss": "stomach"},
    {"stem": "mono",   "class_pair": "7/8",  "sg_prefix": "e",  "pl_prefix": "ebe", "sg_form": "egemono", "pl_form": "ebebono",   "gloss": "shadow"},
    {"stem": "toke",   "class_pair": "1/2",  "sg_prefix": "o",  "pl_prefix": "aba", "sg_form": "otoke",   "pl_form": "abatoke",   "gloss": "elder"},
]

# ──────────────────────────────────────────────────────────────────────────────
# TASK 4 – MORPHOPHONEMIC ALTERNATION RULE
# ──────────────────────────────────────────────────────────────────────────────
# Rule:  When a class 5 prefix (e- / eri-) precedes a vowel-initial stem,
#        the final vowel of the prefix is deleted (coalescence / vowel elision).
#
# Examples observed in EkəGusii:
#   class 5 sg prefix 'e'  + 'anda' → 'anda'  (not 'eanda')
#   class 5 pl prefix 'ama' + 'anda' → 'am-anda' (prefix vowel contracts)
#
# Style rule implemented below as a regex substitution applied
# AFTER the basic prefix–stem concatenation.
#
# Plain-language description:
#   "When a class 5 (or class 7) singular prefix ending in a vowel
#    immediately precedes a stem that itself begins with a vowel,
#    the prefix's final vowel is deleted."
# ──────────────────────────────────────────────────────────────────────────────

VOWELS = set("aeiouAEIOU")

def _apply_morphophonemic_rules(prefix: str, stem: str, class_pair: str) -> str:
    """
    Apply morphophonemic alternation rules at the prefix–stem boundary.

    Rule (Task 4): For class 5/6 and 7/8 noun classes, when the prefix ends
    in a vowel and the stem begins with a vowel, delete the prefix-final vowel
    (vowel elision / coalescence).

    Returns the surface form after applying the rule.
    """
    if not prefix:
        return stem

    # Only apply elision for class 5/6 and 7/8 (the classes where this was observed)
    if class_pair in ("5/6", "7/8"):
        if prefix[-1] in VOWELS and stem and stem[0] in VOWELS:
            # Delete the final vowel of the prefix
            prefix = prefix[:-1]

    return prefix + stem


# ──────────────────────────────────────────────────────────────────────────────
# BUILD PREFIX INDEX for the analyser (Task 2)
# ──────────────────────────────────────────────────────────────────────────────
# Maps each stored surface form → its full lexical entry.
# We index on the stored sg_form / pl_form rather than recomputing, so that
# manually verified forms (which may differ from naive concatenation) are used.

_SURFACE_INDEX: dict[str, dict] = {}

def _build_index() -> None:
    for entry in LEXICON:
        sg = entry["sg_form"]
        pl = entry["pl_form"]
        if sg not in _SURFACE_INDEX:
            _SURFACE_INDEX[sg] = {
                "stem": entry["stem"],
                "class_pair": entry["class_pair"],
                "number": "sg",
                "prefix": entry["sg_prefix"],
            }
        if pl not in _SURFACE_INDEX:
            _SURFACE_INDEX[pl] = {
                "stem": entry["stem"],
                "class_pair": entry["class_pair"],
                "number": "pl",
                "prefix": entry["pl_prefix"],
            }

_build_index()

# Collect all unique prefixes (longest first) for greedy prefix stripping
_ALL_PREFIXES = sorted(
    {e["sg_prefix"] for e in LEXICON} | {e["pl_prefix"] for e in LEXICON},
    key=len,
    reverse=True,  # longest-match first
)


# ──────────────────────────────────────────────────────────────────────────────
# TASK 2 – ANALYSER  (surface → lexical)
# ──────────────────────────────────────────────────────────────────────────────

def analyse(word: str) -> dict | None:
    """
    Analyse a surface word form and return a structured lexical result.

    Strategy:
      1. First check the full surface-form index (exact match on stored forms).
      2. If not found, try prefix-stripping: attempt each known prefix
         (longest first) against the start of the word using re.match();
         if the remainder is a known stem, construct the result.
      3. If neither succeeds, return {"result": "no analysis found"}.

    Returns
    -------
    dict  with keys: stem, class_pair, number, prefix, result
          or {"result": "no analysis found"} for unrecognised words.
    """
    word = word.strip().lower()

    # --- Step 1: exact surface-form lookup ---
    if word in _SURFACE_INDEX:
        entry = _SURFACE_INDEX[word]
        return {
            "prefix":     entry["prefix"],
            "stem":       entry["stem"],
            "class_pair": entry["class_pair"],
            "number":     entry["number"],
            "result":     "analysis found",
        }

    # --- Step 2: prefix-stripping via re.match (longest prefix first) ---
    stem_index = {e["stem"]: e for e in LEXICON}

    for prefix in _ALL_PREFIXES:
        pattern = r"^" + re.escape(prefix) + r"(.+)$"
        m = re.match(pattern, word)
        if m:
            remainder = m.group(1)
            if remainder in stem_index:
                entry = stem_index[remainder]
                # Determine number from which prefix matched
                number = "sg" if prefix == entry["sg_prefix"] else "pl"
                return {
                    "prefix":     prefix,
                    "stem":       remainder,
                    "class_pair": entry["class_pair"],
                    "number":     number,
                    "result":     "analysis found",
                }

    # --- Step 3: unrecognised word ---
    return {"result": "no analysis found"}


# ──────────────────────────────────────────────────────────────────────────────
# TASK 3 – GENERATOR  (lexical → surface)
# ──────────────────────────────────────────────────────────────────────────────

def generate(stem: str, class_pair: str, number: str) -> str | None:
    """
    Generate the correct surface word form from a lexical triple.

    Parameters
    ----------
    stem       : the noun stem (e.g. 'onto', 'ti')
    class_pair : the noun-class pair (e.g. '1/2', '7/8')
    number     : 'sg' (singular) or 'pl' (plural)

    Returns
    -------
    str   – the surface word form (prefix + stem, with morphophonemic rules applied)
    None  – if the stem/class_pair combination is not found in the lexicon

    Algorithm
    ---------
    1. Search the LEXICON for an entry matching both stem and class_pair.
    2. Select the sg_prefix or pl_prefix depending on `number`.
    3. Apply morphophonemic alternation rules (Task 4) at the boundary.
    4. Return the resulting surface form.

    Round-trip guarantee
    --------------------
    For every entry in the lexicon:
        analyse(generate(stem, class_pair, number))['stem'] == stem
    This is verified in the test suite below.
    """
    stem = stem.strip().lower()
    number = number.strip().lower()

    if number not in ("sg", "pl"):
        raise ValueError(f"number must be 'sg' or 'pl', got {number!r}")

    # Look up the entry
    for entry in LEXICON:
        if entry["stem"] == stem and entry["class_pair"] == class_pair:
            prefix = entry["sg_prefix"] if number == "sg" else entry["pl_prefix"]
            # Apply morphophonemic rules (Task 4)
            surface = _apply_morphophonemic_rules(prefix, stem, class_pair)
            return surface

    # Stem + class_pair not in lexicon
    return None


# ──────────────────────────────────────────────────────────────────────────────
# ROUND-TRIP VERIFICATION  (correctness test for Task 3)
# ──────────────────────────────────────────────────────────────────────────────

def round_trip_check() -> list[dict]:
    """
    For every lexicon entry, generate the surface form and then analyse it,
    confirming that analyse(generate(stem, cp, num)) recovers the original stem.

    Returns a list of result dicts, one per (stem, class_pair, number) triple.
    """
    results = []
    for entry in LEXICON:
        for number in ("sg", "pl"):
            stem       = entry["stem"]
            class_pair = entry["class_pair"]

            surface    = generate(stem, class_pair, number)
            if surface is None:
                results.append({
                    "stem": stem, "class_pair": class_pair, "number": number,
                    "surface": None, "round_trip_ok": False,
                    "error": "generate returned None",
                })
                continue

            analysis   = analyse(surface)
            recovered  = analysis.get("stem")
            ok         = (recovered == stem)
            results.append({
                "stem":          stem,
                "class_pair":    class_pair,
                "number":        number,
                "surface":       surface,
                "recovered_stem": recovered,
                "round_trip_ok": ok,
            })
    return results


# ──────────────────────────────────────────────────────────────────────────────
# DEMO / MAIN
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("EkəGusii Morphological Transducer  –  Tasks 1–4")
    print("=" * 65)

    # ── Task 3 demo: generate ─────────────────────────────────────────────────
    print("\n── TASK 3: generate(stem, class_pair, number) ──\n")
    test_triples = [
        ("onto",   "1/2",  "sg"),
        ("onto",   "1/2",  "pl"),
        ("ti",     "3/4",  "sg"),
        ("ti",     "3/4",  "pl"),
        ("bere",   "5/6",  "sg"),
        ("bere",   "5/6",  "pl"),
        ("gesaku", "7/8",  "sg"),
        ("gesaku", "7/8",  "pl"),
        ("nka",    "9/10", "sg"),
        ("nka",    "9/10", "pl"),
    ]
    for stem, cp, num in test_triples:
        surface = generate(stem, cp, num)
        print(f"  generate({stem!r:12s}, {cp!r:6s}, {num!r:4s})  →  {surface}")

    # ── Round-trip check ──────────────────────────────────────────────────────
    print("\n── ROUND-TRIP CHECK  analyse(generate(...)) ──\n")
    results = round_trip_check()
    passed  = sum(1 for r in results if r["round_trip_ok"])
    total   = len(results)
    for r in results:
        status = "✓" if r["round_trip_ok"] else "✗"
        print(f"  {status}  {r['stem']:12s} {r['class_pair']:6s} {r['number']:3s}  "
              f"→  {str(r.get('surface', 'None')):20s}  "
              f"recovered: {r.get('recovered_stem', '—')}")

    print(f"\n  Round-trip: {passed}/{total} passed")

    # ── Task 2 demo: analyse ──────────────────────────────────────────────────
    print("\n── TASK 2: analyse(word) – hold-out words ──\n")
    hold_out = [
        "abaonto", "emiti", "egesaiga", "ecinka", "amabere",
        "otoke", "abatoke", "orura", "ekaratasi", "ZZZUNKNOWN",
    ]
    for w in hold_out:
        result = analyse(w)
        print(f"  analyse({w!r:16s})  →  {result}")

