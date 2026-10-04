from pathlib import Path
from PIL import Image
import json,sys,hashlib,shutil,datetime
B=Path(__file__).resolve().parents[2]
j=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'));src=Path(sys.argv[2])
dest=B/j['dest'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(dest);assert min(im.size)>=1024 and im.mode=='RGBA'
out=B/j['exportFile']
im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
refs=[{'path':p,'role':role,'sha256':h(Path(p))} for p,role in zip(j['refs'],j['roles'])]
rec={'file':j['dest'],'sha256':h(dest),'generatedAt':datetime.datetime.now().astimezone().isoformat(),'generatedAtMeaning':'本地接收时间，服务端未披露','tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':j['refs']},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理入口无型号质量选择器，回执未披露','prompt':j['prompt'],'promptSha256':h(B/j['prompt']),'references':refs,'evidence':{'output_path':str(src),'receipt':j['receipt'],'result_type':'image_url + output_hint; no model/quality metadata'},'nativeSize':im.size,'mode':im.mode,'export':{'file':j['exportFile'],'size':[1024,1024],'sha256':h(out),'transform':'仅完整画布等比缩放至1024，无裁切/补边/整图平移，不使用922+offset'},'review':{'status':'pending_visual_review','note':j['note'],'dynamicAcceptance':False},'requestedPhase':j.get('phase'),'requestedSupportLeg':j.get('supportLeg'),'editSource':{'path':j['refs'][0],'sha256':h(Path(j['refs'][0]))}}
rp=Path(str(dest)+'.generation.json');rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
er={'file':j['exportFile'],'sha256':h(out),'derivativeOf':j['dest'],'generationRecord':str(rp.relative_to(B)).replace('\\','/'),'nativeSha256':h(dest),'transform':rec['export']['transform'],'actualModel':None,'actualQuality':None}
Path(str(out)+'.generation.json').write_text(json.dumps(er,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':j['exportFile'],'native':im.size,'sha256':h(out)},ensure_ascii=False))

