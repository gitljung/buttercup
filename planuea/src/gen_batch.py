import sys, os, concurrent.futures as cf
sys.path.insert(0, os.path.expanduser("~/.hermes/skills/creative/image-gen-with-references/scripts"))
from codex_image_with_refs import generate_with_references

D = os.path.dirname(os.path.abspath(__file__))
STYLE = os.path.expanduser("~/code/buttercup/wokdafok/art/gm_v3.png")
BASE = ("Image 1 is the EXACT style reference: a poppy cartoon sticker illustration — thick even chili-red (#C8340A) "
        "outlines, flat bright colours, glossy white highlight streaks, front view, plain white background, NOTHING "
        "around it. Image 2 is the subject reference photo. Redraw the subject in EXACTLY the same illustration style "
        "and line weight, upright, centered, object fills ~85% of the frame height. ")
END = (" Draw ONLY the object: NO stars, NO sparks, NO speed lines, NO splashes, NO hands, NO gloves, NO cutting board, "
       "no ground shadow, no text. Fully visible with generous margin, perfectly plain solid white background.")
BOWL = ("a round brushed-steel prep bowl (light grey with chili-red outline, simple flat shading), seen from the front, "
        "slightly from above so the contents are visible")
JOBS = {
 "beef": ("beef.jpg", "Subject: a small white plate piled with thick slices of GRILLED BEEF with a thick fat cap: each slice "
          "has a pink-brown medium-rare meat part, a charred grill-striped edge and a wide pale creamy-white fat strip."),
 "lime": (None, "Subject (no photo, invent it): two bright green Thai LIMES, one whole and one cut in half showing the "
          "juicy pale-green segmented inside, leaning together upright."),
 "chiliflakes": ("flakes.jpg", f"Subject: {BOWL}, heaped with coarse dried red CHILI FLAKES (Thai prik pon: rusty red flakes "
          "with pale seeds), a small spoon resting in it."),
 "shallot": ("shallot.jpg", "Subject: three small purple-pink Thai SHALLOTS standing upright (glossy purple skin, little "
          "root tufts), plus a few thin purple-and-white shallot slices in front."),
 "lemongrass": (None, "Subject (no photo, invent it): two LEMONGRASS stalks standing upright (pale yellow-green bulbous "
          "base, green fibrous tops trimmed), plus a small pile of thin pale lemongrass rings in front."),
 "kaffirlime": ("kaffir.jpg", "Subject: three glossy dark-green KAFFIR LIME LEAVES, each a distinctive double leaf (one "
          "leaf on top of another like a figure 8), standing upright, plus a little heap of very finely shredded leaf "
          "threads in front."),
 "mint": ("mint.jpg", "Subject: a fresh sprig of MINT standing upright: square green stem with pairs of bright-green "
          "wrinkled, serrated oval leaves, small leaves at the top."),
}


def run(k):
    sub, desc = JOBS[k]
    out = os.path.join(D, "..", "art", k + ".png")
    if os.path.exists(out):
        return k, "skip"
    try:
        generate_with_references(style_path=STYLE, subject_path=os.path.join(D, sub) if sub else STYLE,
                                 prompt=BASE + desc + END, output_path=out, quality="high", size="1024x1536")
        return k, "ok" if os.path.exists(out) else "noimg"
    except Exception as e:
        return k, "ERR " + str(e)[:200]


if __name__ == "__main__":
    keys = sys.argv[1:] or list(JOBS)
    with cf.ThreadPoolExecutor(3) as ex:
        for k, r in ex.map(run, keys):
            print(k, r, flush=True)
