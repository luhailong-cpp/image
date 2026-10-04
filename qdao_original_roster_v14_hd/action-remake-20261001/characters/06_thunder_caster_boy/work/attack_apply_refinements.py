import hashlib,json,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
root=Path(__file__).resolve().parents[1]
host=Path('C:/Users/luyua/.codex/generated_images/01a0fc40-bf23-7373-8f11-758f04744182')
items=[
 ('E',1,'exec-3051e99b-7beb-4768-ad6d-d79b92596f09.png','2026-10-02T20:07:31.572246524Z','attack_E_00_v1.png','初始蓄力收肘，减少00到01直接大幅后摆'),
 ('W',8,'exec-7f805bfb-6295-4ea4-af1a-1d92e025c72b.png','2026-10-02T20:09:47.911627406Z','attack_W_07_v1.png','回收初段保留宽步和前倾，避免07到08立刻站直收脚')]
for d,f,n,at,ref,reason in items:
 stem=f'attack_{d}_{f:02d}_v2';out=root/'runtime/attack'/d/f'{f:02d}.png';op=out.with_name(out.name+'.generation.json')
 old=json.loads(op.read_text(encoding='utf-8'))
 if old['derivedFrom'][0]['file']==f'work/{stem}.png': continue
 (root/'records'/f'attack_{d}_{f:02d}_superseded_export_v1.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 subprocess.run([sys.executable,'-B',str(root/'tools/record_frame.py'),str(host/n),stem,f'prompts/{stem}.txt','--review',reason+'；动态复验待完成','--generated-at',at],check=True)
 raw=root/'work'/f'{stem}.png';gp=raw.with_name(raw.name+'.generation.json');g=json.loads(gp.read_text(encoding='utf-8'))
 q=root/'work'/ref;g['references'].append({'path':str(q).replace('\\','/'),'role':'precise prior animation pose edit target','sha256':hashlib.sha256(q.read_bytes()).hexdigest()})
 g['submittedParameters']['referenced_image_paths']=[x['path'] for x in g['references']]
 g['generationTimeEvidence']='C2PA embedded creation timestamp recovered from returned PNG; prior-turn result not consumed before interruption'
 g['exported']=True;g['exportPath']=out.relative_to(root).as_posix()
 im=Image.open(raw);assert im.mode=='RGBA' and im.width>=1024 and im.width==im.height
 im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
 new=dict(old);new['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();new['derivedFrom']=[{'file':raw.relative_to(root).as_posix(),'sha256':g['sha256'],'generationRecord':gp.relative_to(root).as_posix()}];new['generatedAt']=at;new['visualReview']=reason+'；动态复验待完成';new['replaces']={'record':f'records/attack_{d}_{f:02d}_superseded_export_v1.json','sha256':old['sha256'],'reason':reason}
 op.write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');gp.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 oldgp=root/old['derivedFrom'][0]['generationRecord']; og=json.loads(oldgp.read_text(encoding='utf-8'));og['supersededBy']=gp.relative_to(root).as_posix();og['visualReview']='已替换：'+reason;oldgp.write_text(json.dumps(og,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.relative_to(root).as_posix())
