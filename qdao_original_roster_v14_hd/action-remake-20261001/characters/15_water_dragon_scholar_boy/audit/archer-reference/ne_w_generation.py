import argparse, hashlib, json, shutil
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

B = Path(__file__).resolve().parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,d):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()

p=argparse.ArgumentParser(); p.add_argument('mode',choices=['prepare','finish']); p.add_argument('key'); p.add_argument('--slot'); p.add_argument('--reason'); p.add_argument('--host'); p.add_argument('--edit'); p.add_argument('--extra',action='append'); p.add_argument('--no-selection',action='store_true')
a=p.parse_args(); key=a.key
req=B/'provenance/requests'/f'{key}.json'
if a.mode=='prepare':
    d=load(B/'provenance/derived'/f'{a.slot.replace("/","-")}.json')
    native=Path(a.edit) if a.edit else Path(d['originalGenerationRecord']['evidence']['hostOutput'])
    assert native.is_file(), native
    if not a.edit: assert sha(native)==d['derivedFrom']['sha256'], native
    direction,frame=a.slot.split('/')[1:]
    refs=[native,B.parent/'09_bamboo_archer_girl/runtime/run'/direction/f'{frame}.png',Path('D:/work/image/q_daoist_character_pack_4096/15_water_dragon_scholar_boy_transparent_4096.png'),Path('D:/work/image/designs/jubaozhai-ui/02-characters.png')]
    prompt=(B/'prompts'/f'{key}.txt').read_text(encoding='utf-8')
    r={'slot':a.slot,'key':key,'startedAt':now(),'configSnapshot':load('D:/work/image/config/image-generation.json'),'supersedes':d['derivedFrom'],'reason':a.reason,'references':[{'file':str(x).replace('\\','/'),'sha256':sha(x),'purpose':v} for x,v in zip(refs,['原生编辑目标；角色15当前选帧的宿主原图','用户指定09同方向同槽跑步相位参考；仅参考运动解剖，不复制角色','角色15身份','已确认主要画法参考'])],'submittedParameters':{'prompt':prompt,'referenced_image_paths':[str(x).replace('\\','/') for x in refs],'transparent_background':True,'model':None,'quality':None}}
    for extra_arg in a.extra or []:
        extra=Path(extra_arg)
        r['references'].append({'file':str(extra).replace('\\','/'),'sha256':sha(extra),'purpose':'图5局部连续性参考，具体角色及用途见实际prompt'})
        r['submittedParameters']['referenced_image_paths'].append(str(extra).replace('\\','/'))
    if a.edit:
        r['editingFrom']={'path':native.relative_to(B).as_posix(),'sha256':sha(native),'generationRecord':f'provenance/generation/{native.stem}.json'}
    dump(req,r); print(json.dumps(r['submittedParameters'],ensure_ascii=False))
else:
    r=load(req); host=Path(a.host); dst=B/'sources/new'/f'{key}.png'
    assert not dst.exists(), dst
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(host,dst)
    im=Image.open(dst); assert im.size==(1254,1254) and im.mode=='RGBA',(im.size,im.mode)
    rec={'file':dst.relative_to(B).as_posix(),'sha256':sha(dst),'generatedAt':now(),'recordedAt':now(),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'alphaExtrema':im.getchannel('A').getextrema(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':r['configSnapshot'],'submittedParameters':r['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未开放型号/质量选择器，返回未披露实际型号与质量。','prompt':f'prompts/{key}.txt','references':r['references'],'editSource':r['supersedes'],'evidence':{'hostOutput':str(host).replace('\\','/'),'toolResult':f'provenance/receipts/{key}.tool.json','request':f'provenance/requests/{key}.json'},'acceptance':'candidate_pending_parent_sequence_review'}
    if r.get('editingFrom'): rec['editSource']=r['editingFrom']
    gen=f'provenance/generation/{key}.json'; dump(B/gen,rec)
    if a.no_selection:
        print(json.dumps({'source':str(dst),'generationRecord':gen,'sha256':rec['sha256']},ensure_ascii=False))
        raise SystemExit(0)
    selection=B/'audit/archer-reference/ne-w-selection.json'
    data=load(selection) if selection.exists() else {'schemaVersion':1,'character':'15_water_dragon_scholar_boy','scope':'NE/W局部候选；不覆盖正式selection/manifest/runtime','status':'pending_parent_sequence_review','frames':[]}
    data['updatedAt']=now(); data['frames'].append({'slot':r['slot'],'source':rec['file'],'generationRecord':gen,'sha256':rec['sha256'],'supersedes':r['supersedes'],'reason':r['reason'],'review':'pending_visual_review'})
    dump(selection,data); print(json.dumps({'source':str(dst),'size':im.size,'mode':im.mode,'sha256':rec['sha256']},ensure_ascii=False))
