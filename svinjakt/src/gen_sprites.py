import os, sys, concurrent.futures as cf
sys.path.insert(0, os.path.expanduser("~/.hermes/skills/creative/image-gen-with-references/scripts"))
from codex_image_with_refs import generate_with_references

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, '..', 'art')
os.makedirs(OUT, exist_ok=True)
STYLE = os.path.expanduser('~/code/buttercup/wokdafok/art/gm_v3.png')
BASE = ("Image 1 is the EXACT illustration style reference: playful Buttercup cartoon sticker style, thick even chili-red "
        "#C8340A outlines, flat bright colours, subtle glossy highlights, warm cream/yellow palette, front view, plain "
        "solid white background. Image 2 is the person/animal reference. Make a cute game character sprite in exactly "
        "this style and line weight, simplified but recognizable by clothes, hat, glasses, hair/beard and vibe. Full body, "
        "standing 3/4 front, holding a comically oversized hunting rifle pointed upward at 30 degrees (safe cartoon pose), "
        "heroic Blommeröd estate game. No text, no logos, no background, no shadow, centered, fills 85% of frame. ")
JOBS = {
  'peter': ('foton/foto1.jpg', 'Draw ONLY the LEFT foreground man: straw cowboy hat, dark sunglasses, light shirt, grey beard. Name: Peter.'),
  'hugo': ('foton/foto1.jpg', 'Draw ONLY the RIGHT foreground man: white cowboy hat, glasses, red patterned shirt, bolo tie / western vibe, cheerful beard/stubble. Name: Hugo.'),
  'carl': ('foton/foto2.png', 'Draw the magazine-cover man: curly dark hair, beard, red jacket over black turtleneck, elegant fashion pose. Name: Carl.'),
  'jocke': ('foton/foto3.jpg', 'Draw the man in black baseball cap with text, gold glasses, black Yamay shirt/apron, beer-in-hand kitchen-service vibe. Replace beer with a tiny radio/controller. Name: Jocke.'),
  'borka': ('foton/foto4.jpg', 'Draw the man in a black cap with a star, rugged friend-of-the-estate vibe. Emphasize the black star cap. Name: Borka.'),
  'wille': ('foton/foto5_wille_s.jpg', 'Draw the young man: tousled wavy light-brown shoulder-length hair, big wide-eyed excited grin, light grey fuzzy crew-neck sweater, black wristband. Keep his euphoric party energy. Name: Wille.'),
  'peacock': ('foton/foto7_pafagel_s.jpg', 'No person. Draw THIS bird: a proud male Indian PEACOCK in side view facing right, iridescent royal-blue neck and breast, fan-shaped crest, white eye stripes, green scaled back, long green train with many blue/bronze eye-spots trailing behind, Buttercup sticker style, comic snooty expression.'),
  'kungsfasan': ('foton/foto6_kungsfasan_s.jpg', 'No person. Draw THIS bird exactly: a male Reeves pheasant (kungsfasan) in side view facing left, white crown and white neck, black eye mask, golden scaled body with black edges, chestnut belly, VERY long barred silver-and-black tail. Strutting, comic proud expression, Buttercup sticker style.'),
  'boar': (STYLE, 'No person. Draw a cute but angry WILD BOAR enemy sprite, side view running toward camera-left, dark bristly brown body, tusks, little red eyes, muddy hooves, Buttercup sticker style.'),
  'megaboar': (STYLE, 'No person. Draw a HUGE MEGA WILD BOAR boss sprite, three times bigger, dark bristly fur, giant tusks, small crown of oak leaves, red angry eyes, Buttercup sticker style, side view.'),
  'gate_plus': (STYLE, 'No person. Draw a glowing blue-green arcade gate sign shaped like a rustic wooden Blommeröd estate gate, with readable text exactly "+1" in chili red on a buttercup yellow panel.'),
  'gate_x2': (STYLE, 'No person. Draw a glowing purple arcade gate sign shaped like a rustic wooden Blommeröd estate gate, with readable text exactly "x2" in chili red on a buttercup yellow panel.'),
}

def run(k):
    sub, desc = JOBS[k]
    out = os.path.join(OUT, k + '.png')
    if os.path.exists(out): return k, 'skip'
    try:
        generate_with_references(style_path=STYLE, subject_path=os.path.join(D, sub) if not os.path.isabs(sub) else sub,
                                 prompt=BASE + desc, output_path=out, quality='high', size='1024x1024')
        return k, 'ok' if os.path.exists(out) else 'noimg'
    except Exception as e:
        return k, 'ERR ' + str(e)[:200]

if __name__ == '__main__':
    keys = sys.argv[1:] or list(JOBS)
    with cf.ThreadPoolExecutor(3) as ex:
        for k,r in ex.map(run, keys): print(k, r, flush=True)
