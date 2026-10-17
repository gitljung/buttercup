"""Sprites via OpenAI Images API (edits med referensbilder) – reserv när Codex-vägen är nere.
~/.hermes/hermes-agent/venv/bin/python3 gen_api.py wille peacock kungsfasan
"""
import os, sys, base64, concurrent.futures as cf
import httpx

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, '..', 'art')
KEY = open(os.path.expanduser('~/.config/openai/api_key')).read().strip()
STYLE = os.path.expanduser('~/code/buttercup/wokdafok/art/gm_v3.png')
BASE = ("Image 1 is the EXACT illustration style reference: playful Buttercup cartoon sticker style, thick even chili-red "
        "#C8340A outlines, flat bright colours, subtle glossy highlights, warm cream/yellow palette. Image 2 is the subject "
        "reference. Make a cute game sprite in exactly this style and line weight, simplified but recognizable. No text, no "
        "logos, no background, no shadow, centered, fills 85% of frame, plain solid white background. ")
JOBS = {
    'wille': ('foton/foto5_wille_s.jpg', '1024x1536',
              'A young man: tousled wavy light-brown shoulder-length hair, big wide-eyed excited open-mouth grin, light grey '
              'fuzzy crew-neck sweater, black wristband, euphoric party energy. Full body, standing 3/4 front, holding a '
              'comically oversized hunting rifle pointed upward at 30 degrees (safe cartoon pose). Name: Wille.'),
    'peacock': ('foton/foto7_pafagel_s.jpg', '1536x1024',
                'No person. THIS bird: a proud male Indian PEACOCK in side view facing right, iridescent royal-blue neck and '
                'breast, fan-shaped crest, white eye stripes, green scaled back, long green train with many blue/bronze '
                'eye-spots trailing behind to the left. Comic snooty expression.'),
    'kungsfasan': ('foton/foto6_kungsfasan_s.jpg', '1536x1024',
                   "No person. THIS bird: a male Reeves's pheasant in side view facing left, white crown and white neck, black "
                   'eye mask, golden scaled body with black edges, chestnut belly, VERY long barred silver-and-black tail '
                   'streaming behind to the right. Strutting, comic proud expression.'),
}


def run(k):
    sub, size, desc = JOBS[k]
    out = os.path.join(OUT, k + '.png')
    if os.path.exists(out):
        return k, 'skip'
    files = [('image[]', ('style.png', open(STYLE, 'rb'), 'image/png')),
             ('image[]', (os.path.basename(sub), open(os.path.join(D, sub), 'rb'), 'image/jpeg'))]
    data = {'model': MODEL, 'prompt': BASE + desc, 'size': size, 'quality': 'high', 'n': '1'}
    r = httpx.post('https://api.openai.com/v1/images/edits', headers={'Authorization': 'Bearer ' + KEY},
                   data=data, files=files, timeout=300)
    if r.status_code != 200:
        return k, 'ERR %d %s' % (r.status_code, r.text[:300])
    open(out, 'wb').write(base64.b64decode(r.json()['data'][0]['b64_json']))
    return k, 'ok'


MODEL = os.environ.get('IMG_MODEL', 'gpt-image-2')
if __name__ == '__main__':
    keys = sys.argv[1:] or list(JOBS)
    with cf.ThreadPoolExecutor(3) as ex:
        for k, r in ex.map(run, keys):
            print(k, r, flush=True)
