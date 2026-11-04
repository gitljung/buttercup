import sys, os, concurrent.futures as cf
sys.path.insert(0, os.path.expanduser("~/.hermes/skills/creative/image-gen-with-references/scripts"))
from codex_image_with_refs import generate_with_references

D = os.path.dirname(os.path.abspath(__file__))
STYLE = os.path.expanduser("~/code/buttercup/wokdafok/art/gm_v3.png")
BASE = ("Image 1 is the EXACT style reference: a poppy cartoon sticker illustration — thick even chili-red (#C8340A) "
        "outlines, flat bright colours, glossy white highlight streaks, front view, plain white background, NOTHING "
        "around it. Image 2 is the subject reference photo. Redraw the subject in EXACTLY the same illustration style "
        "and line weight, upright, centered, object fills ~85% of the frame height. ")
END = (" Draw ONLY the object: NO stars, NO sparks, NO speed lines, NO splashes, NO hands, no ground shadow, no text "
       "unless specified. Fully visible with generous margin, perfectly plain solid white background.")
BOWL = "a round brushed-steel prep bowl (light grey with chili-red outline, simple flat shading), seen from the front, slightly from above so the contents are visible"
JOBS = {
 "garlic": ("garlic.jpg", f"Subject: {BOWL}, heaped with finely chopped GARLIC (pale cream-yellow minced garlic with little "
            "highlights), plus two whole garlic cloves leaning against the bowl's front."),
 "greenchili": ("greenchili.jpg", f"Subject: {BOWL}, heaped with finely chopped GREEN Thai chilies (bright green small "
            "rings and bits with pale seeds), plus one whole small green bird's-eye chili lying in front."),
 "redchili": ("redchili.jpg", f"Subject: {BOWL}, heaped with finely chopped RED Thai bird's-eye chilies (bright red rings "
            "and bits with pale seeds), plus one whole small red bird's-eye chili lying in front."),
 "basil": ("basil.jpg", "Subject: a big generous bunch of fresh Thai HOLY BASIL (kra pao): many smallish slightly serrated "
            "bright green leaves on thin green-purple stems, gathered into a loose fresh bundle, standing upright."),
 "wokdafok": (STYLE, "Subject: a cute glass mason JAR of dark glossy brown stir-fry sauce with a chili-red screw lid and a "
            "simple buttercup-yellow (#FCC222) label with red outline. Label text exactly: 'WOK DA FOK' on the first line "
            "and 'SÅS' on the second line, bold condensed poster lettering in chili red. Same sticker style, no other text."),
}

def run(k):
    sub, desc = JOBS[k]
    out = os.path.join(D, "..", "art", k + ".png")
    if os.path.exists(out): return k, "skip"
    try:
        generate_with_references(style_path=STYLE, subject_path=sub if os.path.isabs(sub) else os.path.join(D, sub),
                                 prompt=BASE + desc + END, output_path=out, quality="high", size="1024x1536")
        return k, "ok" if os.path.exists(out) else "noimg"
    except Exception as e:
        return k, "ERR " + str(e)[:200]

if __name__ == "__main__":
    keys = sys.argv[1:] or list(JOBS)
    with cf.ThreadPoolExecutor(3) as ex:
        for k, r in ex.map(run, keys): print(k, r, flush=True)
