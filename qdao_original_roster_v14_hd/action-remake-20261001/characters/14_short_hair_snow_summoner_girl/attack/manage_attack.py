import json, sys, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
BASE = Path(__file__).resolve().parent.parent
OLD = Path('D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/14_short_hair_snow_summoner_girl')
REPO = Path('D:/work/image')
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path, value): Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2),encoding='utf-8')
if sys.argv[1]=='prepare':
    direction, number = sys.argv[2], int(sys.argv[3])
    label = f'attack-{direction}-{number:02d}-v3'
    prior = OLD/'prompts'/f'attack-{direction}-{number:02d}-v1.txt'
    old = prior.read_text(encoding='utf-8-sig')
    pose = old[old.index('ATTACK frame'):].strip()
    orient = 'screen RIGHT (E), far anatomical LEFT hairpin mostly occluded' if direction=='E' else 'screen LEFT (W), anatomical LEFT hairpin visibly on near side'
    root = 563
    prompt = f'Use case: stylized-concept. Paint ONE original full-body 1024x1024 transparent animation frame of the exact snow summoner girl in reference 1; reference 2 is the approved bright rounded hand-painted finish only. Face {orient}. Preserve silver bob, furry ears, purple eyes, white/lilac fur-trimmed short robe, silver fox-face buckle, blue crystals, fluffy boots. Her anatomical LEFT arm cradles ONE small white fox; RIGHT palm supports ONE blue snowflake crystal. Never swap hands. No girl tail. Match reference 1 camera and fixed scale. Virtual floor y=942 and root x={root}; upright ear top around80; keep real crouch and lean. Entire body inside canvas, do not scale to pose bbox. No shadow, scene, particles, projectile, text, UI or grid. True transparent alpha. A changed anatomical pose, never mirror/copy/interpolate. '+pose
    refs = [str(REPO/f'qdao_original_roster_v14_hd/recovery-20260921/14-delivery-preview/assets/idle/{direction}.png'), str(REPO/'designs/jubaozhai-ui/02-characters.png')]
    (BASE/'prompts'/f'{label}.txt').write_text(prompt, encoding='utf-8')
    request = {'label':label,'status':'prepared','generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'prompt':prompt,'referenced_image_paths':refs,'transparent_background':True},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具没有model/quality选择器；实际返回尚未披露','priorPrompt':str(prior),'priorPromptSha256':sha(prior),'references':[{'path':p,'sha256':sha(p),'role':r} for p,r in zip(refs,['identity-and-direction-camera','approved-primary-painting-style'])]}
    save(BASE/'provenance'/f'{label}.request.json',request)
    print(json.dumps({'label':label, 'args':{k:v for k,v in request['submittedParameters'].items() if k not in ['model','quality']}},ensure_ascii=False))
elif sys.argv[1]=='ingest':
    label, source, direction, number = sys.argv[2:6]
    source=Path(source); im=Image.open(source); im.load()
    if min(im.size)<1024: raise ValueError('native too small')
    native={'path':str(source),'sha256':sha(source),'width':im.width,'height':im.height,'mode':im.mode}
    outdir=BASE/'attack'/direction; outdir.mkdir(parents=True,exist_ok=True)
    dest=outdir/f'{int(number):02d}.png'
    if dest.exists(): raise FileExistsError(dest)
    im=im.convert('RGBA')
    if im.size!=(1024,1024): im=im.resize((1024,1024),Image.Resampling.LANCZOS)
    im.save(dest)
    rec={'label':label,'file':str(dest.relative_to(BASE)),'sha256':sha(dest),'generatedAt':datetime.now(timezone.utc).isoformat(),'native':native,'export':{'width':1024,'height':1024,'format':'PNG','mode':'RGBA'},'operation':'full-canvas proportional LANCZOS to1024; no per-bbox transform, no foot realignment','tool':'image_gen.imagegen','route':'builtin','request':f'provenance/{label}.request.json','actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具只返回image_url与output_hint，未披露型号或质量','visualStatus':'pending-individual-and-sequence-review','alphaExtrema':im.getchannel('A').getextrema(),'bbox':im.getbbox()}
    save(BASE/'provenance'/f'{label}.generation.json',rec)
    print(json.dumps(rec,ensure_ascii=False))

