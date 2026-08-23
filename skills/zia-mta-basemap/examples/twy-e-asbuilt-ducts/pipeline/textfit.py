"""Arial-metric text measurement for PowerPoint text boxes (Liberation Sans)."""
from PIL import ImageFont

REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
BLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
EMU_PT = 12700
_cache = {}


def _font(pt, bold):
    key = (round(pt * 4), bold)
    if key not in _cache:
        # measure at 4x for sub-point accuracy
        _cache[key] = ImageFont.truetype(BLD if bold else REG, int(round(pt * 4)))
    return _cache[key]


def text_w_pt(s, pt, bold=False):
    f = _font(pt, bold)
    return f.getlength(s) / 4.0


def wrap_lines(text, width_pt, pt, bold=False):
    """Greedy word wrap, matching PowerPoint's behaviour closely enough for layout."""
    lines = 0
    for raw in text.split("\n"):
        raw = raw.rstrip()
        if not raw:
            lines += 1
            continue
        words = raw.split(" ")
        cur = ""
        n = 1
        for w in words:
            cand = w if not cur else cur + " " + w
            if text_w_pt(cand, pt, bold) <= width_pt or not cur:
                cur = cand
            else:
                n += 1
                cur = w
        lines += n
    return lines


def frame_height(paras, box_w_emu, l_ins=91440, r_ins=91440, t_ins=45720, b_ins=45720,
                 line_factor=1.21):
    """paras: list of (text, pt, bold, space_after_emu). Returns needed EMU height."""
    width_pt = (box_w_emu - l_ins - r_ins) / EMU_PT
    total = t_ins + b_ins
    for text, pt, bold, sa in paras:
        n = wrap_lines(text, width_pt, pt, bold)
        total += int(n * pt * line_factor * EMU_PT) + (sa or 0)
    return total
