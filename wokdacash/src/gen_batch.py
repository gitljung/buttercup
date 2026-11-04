import sys, os, concurrent.futures as cf
sys.path.insert(0, os.path.expanduser("~/.hermes/skills/creative/image-gen-with-references/scripts"))
from codex_image_with_refs import generate_with_references

D = os.path.dirname(os.path.abspath(__file__))
STYLE = os.path.expanduser("~/code/buttercup/wokdafok/art/gm_v3.png")
BASE = ("Image 1 is the EXACT style reference: a poppy cartoon sticker illustration — thick even chili-red (#C8340A) "
        "outlines, flat bright colours, glossy white highlight streaks, perfectly upright front view, plain white "
        "background, NOTHING around it. Image 2 is the subject reference. Redraw the subject in EXACTLY the same "
        "illustration style and line weight, matching the subject's REAL proportions and silhouette, upright and "
        "symmetrical, no tilt, object fills ~85% of the frame height. ")
END = (" Draw ONLY the object: NO stars, NO sparks, NO speed lines, NO splashes, NO hands, no ground shadow. Fully "
       "visible with generous margin, perfectly plain solid white background.")
JOBS = {
 "namprikpao": ("namprikpao.png", "Subject: Chua Hah Seng brand NAM PRIK PAO chilli paste jar — squat round glass jar "
            "with a gold metal screw lid, dark glossy red-brown chilli paste with a reddish oil layer visible through the "
            "glass, a deep royal-blue label with a gold Chinese lattice pattern border, red Thai title text on top, the "
            "yellow triangle logo with red characters in the middle, and a red band at the bottom reading 'ORIGINAL CHILLI "
            "PASTE'. Keep the blue label, the yellow triangle and the gold lid recognisable."),
 "palmsugar": (STYLE, "Subject (no photo — invent it): a small stack of three round Thai PALM SUGAR cakes (nam tan pip), "
            "each a flat golden-caramel disc with a slightly domed top and soft ridged edge, warm light-brown with "
            "darker amber shading, plus one disc broken in half leaning in front showing the crumbly golden inside."),
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
    os.makedirs(os.path.join(D, "..", "art"), exist_ok=True)
    keys = sys.argv[1:] or list(JOBS)
    with cf.ThreadPoolExecutor(2) as ex:
        for k, r in ex.map(run, keys): print(k, r, flush=True)
