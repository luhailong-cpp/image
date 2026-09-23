from pathlib import Path
import argparse, json, hashlib
from datetime import datetime,timezone
p=argparse.ArgumentParser();p.add_argument('direction');p.add_argument('frame');p.add_argument('--version',default='v1');p.add_argument('--anchor',required=True);p.add_argument('--pose',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[3];rec=root/'qdao_original_roster_v14_hd/recovery-20260921'
out=rec/'14-generation'/f'{a.direction}{a.frame}-{a.version}';out.mkdir(parents=True,exist_ok=False)
refs=[str(rec/'14-reference/identity-1024.png'),str(root/'designs/jubaozhai-ui/02-characters.png'),str(Path(a.anchor).resolve())]
view='strict left profile facing screen LEFT' if a.direction=='W' else 'rear-left three-quarter view facing diagonally away toward upper left'
prompt=f'''Use case: identity-preserve. Draw one new complete game WALK frame {a.frame}/16 for the snow summoner girl.
Input image 1 locks her original identity and costume; image 2 is approved main rendering style, clean bright rounded Daoist chibi hand-painted finish. Image 3 locks this direction, size, proportions, and clothing. Change only gait pose as below, independently redraw the new pose.
Keep {view}, 2.3-head chibi proportions, silver bob and ears, anatomical LEFT temple snowflake ornament, LEFT arm carrying white fox, RIGHT palm snowflake. Keep anatomical sides unchanged, naturally occluded details stay hidden. Rear sash is a bow, front fox buckle must not appear on back. Boots point in walking direction.
POSE: {a.pose}
Natural short-step walking, with at least one foot contacting ground, never jumping, running, skating or repeated same-leg step. Stable head/body/arms, subtle hem and tassel response. No extra limbs.
One full character only, native square at least 1024x1024 with genuinely transparent RGBA background, all parts inside margins. Ear tips near y80 and grounded sole y942 on 1024 canvas; preserve image3 scale. No labels, sheets, floor, shadow or checkerboard. Clean antialiased alpha edges without white, blue or magenta fringe. Highest visual finish.'''
(out/'prompt.txt').write_text(prompt,encoding='utf-8')
r={'tool':'image_gen__imagegen','route':'builtin','started_at':datetime.now(timezone.utc).isoformat(),'slot':{'kind':'walk','direction':a.direction,'frame':int(a.frame)},'actual_request':{'prompt':prompt,'referenced_image_paths':refs},'submittedParameters':{'model':None,'quality':None},'configSnapshot':json.loads((root/'config/image-generation.json').read_text(encoding='utf-8-sig')),'referenceBindings':[{'path':s,'sha256':hashlib.sha256(Path(s).read_bytes()).hexdigest()} for s in refs]}
(out/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'archive':str(out),'request':r['actual_request']},ensure_ascii=False))
