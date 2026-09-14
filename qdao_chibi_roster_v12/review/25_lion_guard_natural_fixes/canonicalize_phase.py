from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,shutil
R=Path(r'E:\work\image\qdao_chibi_roster_v12\review\25_lion_guard_natural_fixes');C=R.parent.parent/'candidate-stable-body/25_lion_drum_guard';B=R/'precanonical-source';B.mkdir(exist_ok=True)
D=['N','NE','E','SE','S','SW','W','NW'];ORDER=[5,6,7,8,1,2,3,4]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgba(im):return hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
def js(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
reasons={
'N':'01 right arm advances and right calf/sole trails; left thigh supplies leading contact. 05 swaps thighs and advancing arm.',
'NE':'01 near anatomical right arm advances while far left thigh is the leading phase; 05 reverses near-arm swing and thigh overlap. Shoe screen-side alone was not used.',
'E':'01 near right arm advances, far left thigh leads; 05 near right thigh leads and near arm is back.',
'SE':'01 right near arm advances and far left leg leads; 05 near right leg leads with opposite arm.',
'S':'01 screen-right anatomical left leg leads and screen-left right arm advances; 05 reverses both.',
'SW':'01 near left thigh leads with far right arm forward; 05 far right thigh leads with left arm forward.',
'W':'01 near left thigh leads while near left arm is back; 05 far right thigh leads and near left arm advances. Drum remains near left hip.',
'NW':'01 near left thigh leads with opposite far right arm advancing; 05 swaps thigh overlap and arm swing; not inferred solely from shoe depth.'}
plan={'character_id':C.name,'canonical_first_contact':'anatomical_RIGHT','status':'whole-cycle_rotation_only','new_to_old_frame_order':ORDER,'directions':{},'no_mirror':True,'no_pixel_edit':True,'source_label_note':'Prior 04/08 repair files retain authored old numbering; canonical new04=old08 and new08=old04.'}
allcells={};evidence=Image.new('RGB',(886,3544),'#ff00ff')
for n,d in enumerate(D):
 p=C/f'source/walk-{d}-final.png'; backup=B/p.name
 if not backup.exists():shutil.copy2(p,backup)
 orig=Image.open(backup).convert('RGBA');old=[orig.crop((i%2*443,i//2*443,(i%2+1)*443,(i//2+1)*443)) for i in range(8)];new=[old[i-1] for i in ORDER]
 out=Image.new('RGBA',(886,1772));maps=[]
 for i,im in enumerate(new):out.paste(im,(i%2*443,i//2*443));maps.append({'new_phase':i+1,'old_phase':ORDER[i],'rgba_sha256':rgba(im)})
 out.save(p);js(p.with_suffix('.assembly.json'),{'version':12,'operation':'whole-cycle integer grid rearrangement 05..08,01..04; exact raw cells, no image modification','output_path':str(p),'output_sha256':sha(p),'original_sheet':str(backup),'original_sha256':sha(backup),'frame_map':maps,'canonical_first_contact':'anatomical_RIGHT'})
 assert sorted(rgba(x) for x in old)==sorted(rgba(x) for x in new)
 plan['directions'][d]={'old_first_contact':'anatomical_LEFT','evidence':reasons[d],'source_before':str(backup),'source_before_sha256':sha(backup),'source_after':str(p),'source_after_sha256':sha(p),'frame_map':maps}
 allcells[d]=new;evidence.paste(old[0],(0,n*443));evidence.paste(old[4],(443,n*443));ImageDraw.Draw(evidence).text((5,n*443+5),d+' OLD01 LEFT / OLD05 RIGHT',fill='white')
for name,ds in [('s-e',['S','E']),('n-w',['N','W']),('ne-sw',['NE','SW']),('nw-se',['NW','SE'])]:
 out=Image.new('RGBA',(1772,1772));cells=allcells[ds[0]]+allcells[ds[1]]
 for i,cell in enumerate(cells):out.paste(cell,(i%4*443,i//4*443))
 p=C/f'source/paired-{name}.png';out.save(p);js(p.with_suffix('.assembly.json'),{'version':12,'operation':'exact canonical directional cells, row-major grid assembly','output_path':str(p),'output_sha256':sha(p),'direction_order':ds,'canonical_first_contact':'anatomical_RIGHT','phase_plan_path':str(R/'phase-plan.json'),'sources':[{'path':str(C/f'source/walk-{d}-final.png'),'sha256':sha(C/f'source/walk-{d}-final.png')} for d in ds]})
js(R/'phase-plan.json',plan);evidence.save(R/'phase-contact-01-vs05.png');print('25 all eight dirs rotated 05..08,01..04; exact cell hash multiset preserved')
