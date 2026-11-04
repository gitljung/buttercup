import sys, os, concurrent.futures as cf
sys.path.insert(0, os.path.expanduser("~/.hermes/skills/creative/image-gen-with-references/scripts"))
from codex_image_with_refs import generate_with_references

D = os.path.dirname(os.path.abspath(__file__))
STYLE = os.path.join(D, "..", "art", "gm_v3.png")
BASE = ("Image 1 is the EXACT style reference: a poppy cartoon sticker illustration of a sauce bottle — thick even "
        "chili-red (#C8340A) outlines, flat bright colours, glossy white highlight streaks, perfectly upright front view, "
        "plain white background, NOTHING around it. Image 2 is the subject. Redraw the subject in EXACTLY the same "
        "illustration style and line weight, matching the subject's REAL proportions and silhouette, perfectly upright and "
        "symmetrical, no tilt, same scale in frame as image 1 (object fills ~90% of the height). ")
END = (" Draw ONLY the object: NO stars, NO sparks, NO speed lines, NO splashes or marks around it, no ground shadow, "
       "no other text than on the label. Single object centered, fully visible with generous margin, perfectly plain "
       "solid white background.")

JOBS = {
 "oyster": ("oyster1.jpg", "Subject: Maekrua (Mae Krua) Thai oyster sauce bottle — tall dark glass bottle, gold/yellow cap, "
            "red and gold label with the round portrait emblem of the lady chef. Keep the label recognisable: red/gold, "
            "'OYSTER SAUCE' readable, the portrait medallion."),
 "thinsoy": ("thinsoy2.jpg", "Subject: Healthy Boy brand THIN SOY SAUCE bottle — dark brown sauce in a bottle with "
            "diamond-textured shoulders, white cap, bright yellow label with the chubby Healthy Boy mascot in a red/green "
            "oval. Keep 'THIN SOY SAUCE' and 'HEALTHY BOY BRAND' readable on the yellow label."),
 "fish": ("fish1.jpg", "Subject: Megachef PREMIUM FISH SAUCE bottle — clear glass with reddish-amber fish sauce, gold "
            "cap, black/dark label with the gold 'Megachef' chef-hat logo and a big golden anchovy fish drawing. Keep "
            "'Megachef' and 'FISH SAUCE' readable."),
 "darksweet": ("darksweet2.jpg", "Subject: Healthy Boy BLACK SWEET SOY SAUCE bottle — thick almost-black syrupy "
            "sauce, white cap, GREEN label with the Healthy Boy mascot. Keep 'BLACK SWEET SOY SAUCE' readable. Show "
            "the sauce as very thick and glossy."),
 "sugar": ("../art/sugar.png", "Subject: this cream bowl heaped with WHITE SUGAR. Keep the bowl and sugar mound, but remove all jumping cubes, flying grains, sparkles and stars: just the bowl of sugar, calm and still."),
 "water": ("../art/water.png", "Subject: this clear glass measuring jug of light blue WATER with the ML scale. Keep the jug, scale and '100 ML' marking, but the water surface is calm and flat: no splash, no droplets, no stars."),
}

def run(k):
    sub, desc = JOBS[k]
    out = os.path.join(D, "..", "art2", k + ".png")
    if os.path.exists(out):
        return k, "skip"
    try:
        generate_with_references(style_path=STYLE, subject_path=os.path.join(D, sub),
                                 prompt=BASE + desc + END, output_path=out,
                                 quality="high", size="1024x1536")
        return k, "ok" if os.path.exists(out) else "noimg"
    except Exception as e:
        return k, "ERR " + str(e)[:200]

if __name__ == "__main__":
    os.makedirs(os.path.join(D, "..", "art2"), exist_ok=True)
    keys = sys.argv[1:] or list(JOBS)
    with cf.ThreadPoolExecutor(3) as ex:
        for k, r in ex.map(run, keys):
            print(k, r, flush=True)
