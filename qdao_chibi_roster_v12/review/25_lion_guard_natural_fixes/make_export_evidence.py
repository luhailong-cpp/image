from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
R=Path(__file__).resolve().parent;ROOT=R.parent.parent;C=ROOT/'candidate-stable-body/25_lion_drum_guard';O=ROOT/'25_lion_drum_guard';D=['N','NE','E','SE','S','SW','W','NW'];EV=R/'export-evidence';EV.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def tile(im,label,size=256):
 b=Image.new('RGBA',(size,size+24),'#28383a');b.alpha_composite(im.resize((size,size),Image.Resampling.LANCZOS),(0,24));dr=ImageDraw.Draw(b);dr.text((8,6),label,fill='#ebeadc');return b.convert('RGB')
for d in D:
 frames=[Image.open(C/f'idle/{d}.png').convert('RGBA')]+[Image.open(C/f'walk/{d}/{i:02}.png').convert('RGBA') for i in range(1,9)]
 sheet=Image.new('RGB',(768,840),'#28383a')
 for i,f in enumerate(frames):sheet.paste(tile(f,f'{d} '+('IDLE' if i==0 else f'{i:02}')),(i%3*256,i//3*280))
 sheet.save(EV/f'{d}-all-nine.png')
# Eight directions, original frame timing, plus a separate explicit idle/8walk transition loop.
sequences=[]
for phase in range(9):
 board=Image.new('RGB',(1024,560),'#28383a')
 for n,d in enumerate(D):
  p=C/f'idle/{d}.png' if phase==0 else C/f'walk/{d}/{phase:02}.png';board.paste(tile(Image.open(p).convert('RGBA'),f'{d} '+('IDLE' if phase==0 else f'{phase:02}')),(n%4*256,n//4*280))
 sequences.append(board)
sequences[1].save(EV/'eight-direction-walk.gif',save_all=True,append_images=sequences[2:],duration=60,loop=0,disposal=2)
sequences[0].save(EV/'idle-to-walk.gif',save_all=True,append_images=sequences[1:],duration=[600]+[60]*8,loop=0,disposal=2)
old_ret=json.loads((R/'source-retention.json').read_text());assert all(sha(O/p)==v for p,v in old_ret['baseline_files_sha256'].items());assert sha(C/'portrait.png')==sha(O/'portrait.png')
val=json.loads((C/'validation.json').read_text());qc=json.loads((C/'qc.json').read_text());man=json.loads((C/'manifest.json').read_text());
summary={'character_id':C.name,'status':'passed_exports_pending_visual','published':False,'sealed':False,'candidate_path':str(C),'alignment_version':3,'common_scale':1.024390243902439,'movement_frames':64,'neutral_idle_frames':8,'portrait_unchanged':True,'unchanged_raw_cells':59,'repainted_cells':13,'validation_sha256':sha(C/'validation.json'),'manifest_sha256':sha(C/'manifest.json'),'qc_sha256':sha(C/'qc.json'),'provenance_sha256':sha(R/'generation-provenance.json'),'retention_sha256':sha(R/'source-retention.json'),'qc_status':qc['status'],'verifier_status':val['status'],'original_directory_files_unchanged':True,'evidence':[{'path':str(p),'sha256':sha(p)} for p in sorted(EV.glob('*')) if p.is_file()]}
(R/'candidate-validation-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
