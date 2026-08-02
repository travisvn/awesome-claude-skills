"""
Fixture classification for the ZIA MTA basemap.

Design: LAYER FIRST, block name as fallback.

The layer is the drafter's statement of intent and is right almost everywhere.
It is unreliable in exactly two situations, both enumerated below:

  1. The layer is not an asset-type layer at all - the default layer `0`, a circuit
     name (`LTCC8`), an annotation line layer (`EL-IHP-LINE`), a scratch layer
     (`ADB_TO CHECK`), or an attribute layer (`*-AT`).
  2. There is no layer rule for it.

In those cases the block name carries the fixture type and is used instead.

The reverse rule - block first - was tried and rejected: generic block names
(`Pit` is used for both handholes and transformer pits; `Base 8` for two base
types) destroy information the layer had.
"""
import re

# Layers whose name does not describe an asset type. Trust the block here.
UNRELIABLE_LAYERS = {
    "0", "Defpoints", "ADB_TO CHECK", "LTCC8", "TRP",
    "EL-IHP-LINE", "EL-APC-LINE", "ADB_SBC-LINE", "EL-SIGN-LINE", "EL-STB LINE",
    "ADB_STB LINE", "EL-SBC-LINE", "EL-ANNO-LINE", "EL-TAXIED",
}

# Block-name patterns -> fixture type. First match wins.
# Only patterns that uniquely identify a fixture type belong here. Generic
# block names (`Pit`, `Base 8`) are deliberately absent.
BLOCK_RULES = [
    (r"^TCL[-_]",                      "Taxiway centreline light"),
    (r"^TWE[-_]",                      "Taxiway edge light"),
    (r"^STB[-_]|^STOP-BAR-LT$",        "Stop bar light"),
    (r"^IHP[-_]",                      "Holding position light"),
    (r"^LIL[-_]|^STL$",                "Lead-in light"),
    (r"^RCL[-_]",                      "Runway centreline light"),
    (r"^RWE[-_]|^REL[-_]",             "Runway edge light"),
    (r"^TDZ",                          "Touchdown zone light"),
    (r"^APP[-_]|^ASR[-_]",             "Approach light"),
    (r"^SFL[-_]",                      "Sequenced flashing light"),
    (r"^RGL[-_]",                      "Runway guard light"),
    (r"^RRM$",                         "Runway guard light / RRM"),
    (r"^RETIL|^RTI[-_]",               "RETIL"),
    (r"^THR[-_]",                      "Threshold / end light"),
    (r"^PAP",                          "PAPI"),
    (r"^FCU",                          "Flashing control unit"),
    (r"^FLP$",                         "Floodlight (non-AGL)"),
    (r"^ADB_NBASE$",                   "New light base"),
    (r"^ADB_EBASE$",                   "Existing light base"),
    (r"^E_MH|^N_MH|^E_OLD MH",         "Manhole"),
    (r"^EA_Pit$",                      "Earthing pit"),
    (r"^EARTHING$|^Grounding$|^GRR$",  "Earthing point"),
    (r"^CRBLK$",                       "Cable route marker"),
    (r"^Seg_Arrow$",                   "Segmentation annotation"),
    (r"Gatehouse Island|tig-teeth",    "Non-AGL basemap"),
]

# Leaf-layer name -> fixture type.
LAYER_RULES = {
    # lights
    "EL-TAXICL": "Taxiway centreline light", "ADB_TAXICL": "Taxiway centreline light",
    "EL_TAXICL": "Taxiway centreline light", "ADB_TCL PROPOSED": "Taxiway centreline light",
    "EL-TAXIWAY EDGE": "Taxiway edge light", "ADB_TAXIWAY EDGE": "Taxiway edge light",
    "EL_TAXIWAY EDGE": "Taxiway edge light",
    "EL-STOPBAR": "Stop bar light", "ADB_STOPBAR": "Stop bar light",
    "STOP-BAR-LIGHT": "Stop bar light",
    "EL-LEAD-IN": "Lead-in light", "ADB_LEAD-IN": "Lead-in light",
    "ADB_LEAD-IN Omni": "Lead-in light",
    "EL-HOLDING": "Holding position light", "ADB_HOLDING": "Holding position light",
    "EL-RUNWAY CL": "Runway centreline light", "ADB_RUNWAY CL": "Runway centreline light",
    "EL-RUNWAY EDGE": "Runway edge light", "ADB_RUNWAY EDGE": "Runway edge light",
    "EL-TDZ": "Touchdown zone light", "ADB_TDZ": "Touchdown zone light",
    "EL-APPROACH": "Approach light", "ADB_APPROACH": "Approach light",
    "EL-RRM": "Runway guard light / RRM",
    "EL-RUNWAY GUARD": "Runway guard light", "ADB_RUNWAY GUARD": "Runway guard light",
    "EL-RETils": "RETIL", "ADB_RETils": "RETIL",
    "EL-THRESHOLDEND": "Threshold / end light", "ADB_THRESHOLDEND": "Threshold / end light",
    "EL-PAPI": "PAPI", "ADB_PAPI": "PAPI",
    "EL-FLASHING": "Sequenced flashing light", "ADB_FLASHING": "Sequenced flashing light",
    "EL-ADD-LIGHT": "Additional light", "ADB_New_Light": "Additional light",
    "EL-New_Light": "Additional light",
    # signs
    "EL-SIGNS": "Guidance sign", "ADB_SIGNS": "Guidance sign", "EL_SIGNS": "Guidance sign",
    "ADB-Existing Sign": "Guidance sign", "EL-SGN-EX": "Guidance sign",
    "AGL-SIGN": "Guidance sign",
    "EL-SGN-FNDTN": "Sign foundation", "CV-SGN-FNDTN": "Sign foundation",
    "CV-SGN-FNDTN-IHP": "Sign foundation", "CV_Sign Location in Layout": "Sign foundation",
    "EL-SGN-N": "Sign foundation",
    # bases
    "EL-NBASE": "New light base", "ADB_NBASE": "New light base",
    "ADB-New Base": "New light base",
    "EL-EBASE": "Existing light base", "ADB_EBASE": "Existing light base",
    "ADB_BASE": "Light base", "EL-BASE-8": "Light base", "ADB_SENSOR LOOP": "Sensor loop",
    # civil
    "CV_HH": "Handhole", "CV-HH": "Handhole",
    "CV-EX-HH": "Existing handhole", "CV_EX-HH": "Existing handhole",
    "CV_ETRANS HH": "Existing transformer handhole", "CV_TRANSFO HH": "Transformer handhole",
    "CV_EX_TRANSFO PIT": "Existing transformer pit",
    "CV_E_TRANSFO PIT": "Existing transformer pit",
    "CV_TRANSFO PIT": "Transformer pit",
    "CV_MH": "Manhole", "CV-EX-MH": "Existing manhole", "CV_EX-MH": "Existing manhole",
    "CV_ETRANS MH": "Existing transformer manhole", "CV-ZONE2-MANHOLE": "Manhole",
    "CV_GRND": "Earthing point", "CV-GRND": "Earthing point", "CV-EX-GRND": "Earthing point",
    "CV_NEW GROUNDING": "Earthing point", "CV_GROUNDING ROD": "Earthing point",
    "CV_GRND PIT": "Earthing pit",
    "CV-EX SEC CONDUIT": "Existing secondary conduit",
    "CV_EX-SECONDARY": "Existing secondary conduit",
    "CV_SECONDARY_100MM (SIGN)": "Existing secondary conduit",
    "EL-AGLS-PITS": "AGLAS pit",
    "EL-TRAFFIC LIGHT": "Traffic light", "ADB_TRAFFIC LIGHT": "Traffic light",
    # non-AGL basemap
    "AUH_Service Road": "Non-AGL basemap", "AUH_MTB Gate House": "Non-AGL basemap",
    "AUH_Runway Threshold Marking": "Non-AGL basemap",
    "AUH_MTB Floodlight": "Floodlight (non-AGL)",
}

# Types that are not AGL/civil assets and must be excluded from any asset count.
NON_ASSET_TYPES = {
    "Non-AGL basemap", "Segmentation annotation", "Floodlight (non-AGL)", "Unclassified",
}

_COMPILED = [(re.compile(p), t) for p, t in BLOCK_RULES]


def _by_block(block: str):
    b = (block or "").strip()
    for rx, t in _COMPILED:
        if rx.search(b):
            return t
    return None


def classify(block: str, layer_leaf: str) -> str:
    """Return the fixture type for one INSERT.

    Layer wins unless the layer is known to be uninformative, in which case the
    block name is used. Falls back to the base name for `*-AT` layers.
    """
    leaf = (layer_leaf or "").strip()

    if leaf not in UNRELIABLE_LAYERS and not leaf.endswith("-AT"):
        if leaf in LAYER_RULES:
            return LAYER_RULES[leaf]

    hit = _by_block(block)
    if hit:
        return hit

    if leaf.endswith("-AT"):
        base = leaf[:-3]
        if base in LAYER_RULES:
            return LAYER_RULES[base]
    return LAYER_RULES.get(leaf, "Unclassified")
