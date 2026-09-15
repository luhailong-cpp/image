from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
R=Path(__file__).resolve().parent;ROOT=R.parent.parent;C=ROOT/'candidate-stable-body/26_osmanthus_healer';O=ROOT/'26_osmanthus_healer';D=['N','NE','E','SE','S','SW','W','NW'];EV=R/'export-evidence';EV.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def tile(im,label,size=512):
 b=Image.new('RGBA',(size,size+24),'#e8e5da');b.alpha_composite(im if size==512 else im.resize((size,size),Image.Resampling.LANCZOS),(0,24));ImageDraw.Draw(b).text((8,6),label,fill='#26383a');return b.convert('RGB')
for d in D:
 fs=[Image.open(C/f'idle/{d}.png').convert('RGBA')]+[Image.open(C/f'walk/{d}/{i:02}.png').convert('RGBA') for i in range(1,9)];sheet=Image.new('RGB',(1536,1608),'#e8e5da')
 for i,f in enumerate(fs):sheet.paste(tile(f,f'{d} '+('IDLE' if i==0 else f'{i:02}')),(i%3*512,i//3*536))
 sheet.save(EV/f'{d}-all-nine.png');sheet.resize((768,804),Image.Resampling.LANCZOS).save(EV/f'{d}-all-nine.jpg',quality=88)
seq=[]
for phase in range(9):
 b=Image.new('RGB',(1024,560),'#e8e5da')
 for n,d in enumerate(D):
  p=C/f'idle/{d}.png' if phase==0 else C/f'walk/{d}/{phase:02}.png';b.paste(tile(Image.open(p).convert('RGBA'),f'{d} '+('IDLE' if phase==0 else f'{phase:02}'),256),(n%4*256,n//4*280))
 seq.append(b)
seq[1].save(EV/'eight-direction-walk.gif',save_all=True,append_images=seq[2:],duration=60,loop=0,disposal=2)
seq[0].save(EV/'idle-to-walk.gif',save_all=True,append_images=seq[1:],duration=[600]+[60]*8,loop=0,disposal=2)
ret=json.loads((R/'source-retention.json').read_text());assert all(sha(O/p)==v for p,v in ret['baseline_files_sha256'].items());assert sha(C/'portrait.png')==sha(O/'portrait.png')
val=json.loads((C/'validation.json').read_text());qc=json.loads((C/'qc.json').read_text());man=json.loads((C/'manifest.json').read_text());assert not qc['errors'];assert val['status']=='passed_exports_pending_visual'
s={'character_id':C.name,'status':'passed_exports_pending_visual','published':False,'sealed':False,'candidate_path':str(C),'alignment_version':3,'canonical_first_contact':'anatomical_RIGHT','common_scale':1.0120481927710843,'movement_frames':64,'neutral_idle_frames':8,'portrait_unchanged':True,'unchanged_raw_cells':42,'repainted_cells':30,'manifest_sha256':sha(C/'manifest.json'),'validation_sha256':sha(C/'validation.json'),'qc_sha256':sha(C/'qc.json'),'provenance_sha256':sha(R/'generation-provenance.json'),'retention_sha256':sha(R/'source-retention.json'),'phase_plan_sha256':sha(R/'phase-plan.json'),'qc_status':qc['status'],'verifier_status':val['status'],'original_directory_files_unchanged':True,'evidence':[{'path':str(p),'sha256':sha(p)} for p in sorted(EV.glob('*')) if p.is_file()]}
(R/'candidate-validation-summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(s,ensure_ascii=False,indent=2))
