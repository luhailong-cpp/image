from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,argparse
ROOT=Path(__file__).resolve().parents[3]
GEN=ROOT/'qdao_original_roster_v14_hd/recovery-20260921/05-generation'
p=argparse.ArgumentParser();p.add_argument('--frame',type=int,required=True);p.add_argument('--version',type=int,required=True);p.add_argument('--target',required=True);p.add_argument('--phase',required=True);a=p.parse_args()
d=GEN/f'SW{a.frame:02d}-single-v{a.version}';d.mkdir(exist_ok=True);assert not (d/'request.json').exists()
refs=[GEN/a.target/'raw.png',ROOT/'designs/jubaozhai-ui/02-characters.png']
prompt=f'''Use case: identity-preserve. Edit IMAGE 1 into the very next SOUTHWEST walking animation frame SW{a.frame:02d}. Output only ONE complete full character sprite at native1254x1254 or larger, minimum1024 each side, genuine transparent RGBA background.
IMAGE 1 IS THE EDIT TARGET AND AUTHORITATIVE CHARACTER. IMAGE 2 is the confirmed PRIMARY STYLE REFERENCE only, for its bright clean rounded hand-painted finish, not its UI, characters, or poses.
Keep image1 camera, entire upper body, purple hair and lotus bun crown, smile, face, white-purple embroidered robes, green waist knot, purple-gold zither position, hands, ribbons, and large-head short-body proportions. She faces screen lower-left in front-left three-quarter view. Maintain image1 framing: crown near3%, lowest support sole near97%. No translation or resizing of existing pose. Genuinely newly draw the indicated leg movement while leaving identity steady.
ACTION: {a.phase}
Exactly two attached legs and two boots; no crossing lanes, no floating unsupported body. Small natural walking motion. True transparent background, no floor, shadow, text, labels, checkerboard, blue or magenta matte; preserve real purple fabric and ribbon translucency. No copying, mirroring, interpolation, warping or sprite sheets. Highest polished painted fidelity.'''
request={'schema':1,'tool':'built-in image_gen','actual_model':'host-managed-unverified','configSnapshot':json.loads((ROOT/'config/image-generation.json').read_text()),'actual_request':{'prompt':prompt,'referenced_image_paths':[str(x).replace('\\','/') for x in refs],'started_at':datetime.now(timezone.utc).isoformat()},'reference_bindings_at_start':[{'path':str(x).replace('\\','/'),'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in refs],'paid_api_calls':0,'status':'request_prepared_not_yet_submitted'}
(d/'request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(d/'prompt.txt').write_bytes(prompt.encode());print(json.dumps(request['actual_request']))
