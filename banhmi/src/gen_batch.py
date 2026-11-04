import sys, os, concurrent.futures as cf

D = os.path.dirname(os.path.abspath(__file__))
STYLE = os.path.expanduser("~/code/buttercup/wokdafok/art/gm_v3.png")
BASE = ("Image 1 is the EXACT style reference: a poppy cartoon sticker illustration — thick even chili-red (#C8340A) "
        "outlines, flat bright colours, glossy white highlight streaks, front view, plain white background, NOTHING "
        "around it. Image 2 is the subject reference photo. Redraw the subject in EXACTLY the same illustration style "
        "and line weight, upright, centered, REAL proportions, object fills ~85% of the frame height. ")
END = (" Draw ONLY the object: NO stars, NO sparks, NO speed lines, NO splashes, NO hands, NO gloves, NO cutting board, "
       "no ground shadow, no text except what is described. Fully visible with generous margin, perfectly plain solid white background.")
BOWL = ("a round brushed-steel prep bowl (light grey with chili-red outline, simple flat shading), seen from the front, "
        "slightly from above so the contents are visible")
JOBS = {
 "rawpork": ("rawpork.jpg", "Subject: one thick rectangular slab of RAW SKIN-ON PORK BELLY standing upright on its short end, "
          "front shows the layered side: smooth pale-pink skin on top edge, white fat layers alternating with pink meat."),
 "lechon": ("lechon.jpg", "Subject: a finished LECHON BELLY: a rolled-up stuffed pork belly roast tied shut, standing upright, "
          "deep golden-brown blistered, puffy airy CRACKLING skin, with a few thick slices cut off in front showing "
          "white-pink juicy meat, fat layers and a ring of crackling."),
 "salt": (None, "Subject (no photo, invent it): a red-and-white cardboard box of coarse KOSHER SALT (red top with a pour "
          "spout flap, white body; label just says 'KOSHER SALT'), with a small pile of coarse salt flakes in front."),
 "paprika": (None, f"Subject (no photo, invent it): {BOWL}, heaped with bright brick-red ground PAPRIKA powder, a small spoon in it."),
 "garlicpowder": (None, f"Subject (no photo, invent it): {BOWL}, heaped with fine pale beige-yellow GARLIC POWDER, "
          "with one whole white garlic bulb leaning against the bowl."),
 "pepper": (None, f"Subject (no photo, invent it): {BOWL}, filled with whole and coarsely cracked BLACK PEPPERCORNS."),
 "bay": ("bay.jpg", "Subject: three dried BAY LEAVES (olive-green, glossy, pointed oval with a pale central vein), "
          "fanned out upright."),
 "cilantro": ("cilantro.jpg", "Subject: a fresh bunch of CILANTRO / CORIANDER standing upright: thin green stems, "
          "bright-green flat lobed parsley-like leaves, a few white root ends at the bottom."),
 "calamansi": ("calamansi.jpg", "Subject: a small plastic bottle of CALAMANSI JUICE (orange-amber juice inside, "
          "green label with sliced calamansi pictures, label text 'pure calamansi'), with three small round green-and-orange "
          "CALAMANSI fruits in front, one cut in half showing orange flesh."),
 "rocksugar": (None, "Subject (no photo, invent it): a small heap of yellowish translucent ROCK SUGAR lumps (irregular "
          "crystal chunks, pale gold, glossy), on a small white saucer."),
 "baguette": ("baguette.jpg", "Subject: one Vietnamese BÁNH MÌ BAGUETTE, short and airy with a thin crackly golden "
          "crust, standing upright at a slight angle, split open lengthwise along one side showing fluffy white crumb."),
 "pate": ("pate.jpg", "Subject: a small round open tin of PORK LIVER PÂTÉ (silver tin, lid peeled back), filled with smooth "
          "pinkish-brown pâté, a butter knife with a smear of pâté leaning in it. Plain unbranded tin."),
 "mayo": ("baguette.jpg", f"Subject: a small white ceramic bowl of rich yellow BUTTER-EGG MAYONNAISE (bơ, glossy, pale "
          "butter-yellow, thick, swirled top), a small spoon in it."),
 "dochua": ("fill.jpg", "Subject: a glass jar of Vietnamese ĐỒ CHUA pickles: matchstick strips of ORANGE CARROT and "
          "WHITE DAIKON in clear brine, jar open, a few strips piled in front."),
 "cucumber": ("fill.jpg", "Subject: a small green CUCUMBER standing upright plus three long cucumber spears cut "
          "lengthwise in front, showing pale green flesh and seeds."),
 "jeow": ("calamansi.jpg", "Subject: a small white bowl of LAO JEOW SOM dipping sauce: thin amber-orange sauce with "
          "red chili flakes, minced garlic and lots of chopped green cilantro, a spoon resting in it."),
}


import base64, httpx
KEY = open(os.path.expanduser("~/.config/openai/api_key")).read().strip()


def run(k):
    """OpenAI Images API (edits) – Codex-vägen i codex_image_with_refs är trasig efter Hermes-uppdatering."""
    sub, desc = JOBS[k]
    out = os.path.join(D, "..", "art", k + ".png")
    if os.path.exists(out):
        return k, "skip"
    files = [("image[]", ("style.png", open(STYLE, "rb"), "image/png"))]
    if sub:
        files.append(("image[]", (sub, open(os.path.join(D, sub), "rb"), "image/jpeg")))
    prompt = BASE + desc + END
    if not sub:
        prompt = prompt.replace("Image 2 is the subject reference photo. ", "")
    for attempt in range(2):
        try:
            r = httpx.post("https://api.openai.com/v1/images/edits", headers={"Authorization": "Bearer " + KEY},
                           data={"model": "gpt-image-2", "prompt": prompt, "size": "1024x1536", "quality": "high", "n": "1"},
                           files=files, timeout=400)
            if r.status_code != 200:
                err = "ERR %d %s" % (r.status_code, r.text[:300])
                continue
            open(out, "wb").write(base64.b64decode(r.json()["data"][0]["b64_json"]))
            return k, "ok"
        except Exception as e:
            err = "ERR " + str(e)[:200]
    return k, err


if __name__ == "__main__":
    keys = sys.argv[1:] or list(JOBS)
    with cf.ThreadPoolExecutor(4) as ex:
        for k, r in ex.map(run, keys):
            print(k, r, flush=True)
