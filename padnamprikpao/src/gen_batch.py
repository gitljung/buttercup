import sys, os, concurrent.futures as cf
sys.path.insert(0, os.path.expanduser("~/.hermes/skills/creative/image-gen-with-references/scripts"))
from codex_image_with_refs import generate_with_references

D = os.path.dirname(os.path.abspath(__file__))
STYLE = os.path.expanduser("~/code/buttercup/wokdafok/art/gm_v3.png")
BASE = ("Image 1 is the EXACT style reference: a poppy cartoon sticker illustration — thick even chili-red (#C8340A) "
        "outlines, flat bright colours, glossy white highlight streaks, front view, plain white background, NOTHING "
        "around it. Image 2 is the subject reference photo. Redraw the subject in EXACTLY the same illustration style "
        "and line weight, upright, centered, object fills ~85% of the frame height. ")
END = (" Draw ONLY the object: NO stars, NO sparks, NO speed lines, NO splashes, NO hands, NO cutting board, no ground "
       "shadow, no text unless specified. Fully visible with generous margin, perfectly plain solid white background.")
BOWL = ("a round brushed-steel prep bowl (light grey with chili-red outline, simple flat shading), seen from the front, "
        "slightly from above so the contents are visible")
JOBS = {
 "pork": ("pork.jpg", f"Subject: {BOWL}, heaped with thin bite-size slices of raw PORK, a 50/50 mix of lean pink shoulder "
          "and pork belly with clear white fat stripes."),
 "onion": ("prep.jpg", "Subject: half a yellow-white ONION with papery golden skin standing upright cut side facing us, "
          "plus a little pile of onion 'petals' (separated wedge layers) in front of it."),
 "longchili": ("prep.jpg", "Subject: two whole LONG RED CHILLIES (Thai prik chee fa, ~15 cm, glossy bright red, green stem) "
          "standing diagonally crossed, plus a few angled diagonal slices in front showing pale seeds."),
 "springonion": ("prep.jpg", "Subject: a SPRING ONION (scallion) standing upright with white bulb and roots at the bottom "
          "and green tops, plus a small neat stack of 4 cm green-and-white sections in front."),
 "thaibasil": ("basil.jpg", "Subject: a fresh bunch of THAI SWEET BASIL (horapha): glossy smooth bright-green pointed "
          "oval leaves on PURPLE stems, with two small purple flower spikes on top, gathered upright in a loose bunch."),
 "namprikpao": ("npp.jpg", "Subject: a HOMEMADE glass jar of NAM PRIK PAO (Thai roasted chilli paste): straight-sided jar "
          "with a silver metal screw lid, dark almost-black red-brown chunky paste with a glossy red oil layer on top, and "
          "a plain white masking-tape label hand-written in blue marker reading exactly 'NAM PRIK' on line one and "
          "'PAO' on line two. No other text."),
}


def run(k):
    sub, desc = JOBS[k]
    out = os.path.join(D, "..", "art", k + ".png")
    if os.path.exists(out):
        return k, "skip"
    try:
        generate_with_references(style_path=STYLE, subject_path=os.path.join(D, sub),
                                 prompt=BASE + desc + END, output_path=out, quality="high", size="1024x1536")
        return k, "ok" if os.path.exists(out) else "noimg"
    except Exception as e:
        return k, "ERR " + str(e)[:200]


if __name__ == "__main__":
    keys = sys.argv[1:] or list(JOBS)
    with cf.ThreadPoolExecutor(3) as ex:
        for k, r in ex.map(run, keys):
            print(k, r, flush=True)
