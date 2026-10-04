from pathlib import Path
import json,hashlib,datetime
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parents[1]
selection_path=B/'run-SESW-selection.json'
selection=json.loads(selection_path.read_text(encoding='utf-8'))
assert len(selection['frames'])==16 and all(f['direction']=='SE' for f in selection['frames'])
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
repairs=[1,2,3,4,10,12,13,14,15,16]
kept=[5,6,7,8,9,11]
reviews=[]
newrecords=[]
for f in selection['frames']:
    n=f['frame']
    if n in repairs:
        job=json.loads((B/f'provenance/run-SE-foot-{n:02d}-v1-job.json').read_text(encoding='utf-8'))
        source=job['dest']; rp=B/(source+'.generation.json')
        rec=json.loads(rp.read_text(encoding='utf-8'))
        previous={'source':job['editSource'],'generationRecord':job['editSource']+'.generation.json','sourceSha256':h(B/job['editSource'])}
        rec['editSource']=previous
        note='已实看原图、竹弓SE实际同向图和新图：仅鞋头脚踝局部改向，保留原腿相位、盘卡手别、角色造型与上身画幅。'
        rec['review']={'status':'static_foot_direction_checked_sequence_pending','note':note,'dynamicAcceptance':False}
        newrecords.append((rp,rec))
        f.update({'source':source,'generationRecord':source+'.generation.json','sourceSha256':h(B/source),'nativeSize':[rec['width'],rec['height']],'status':'candidate','visualReview':'static_foot_direction_checked_sequence_pending','dynamicReview':'not_verified','previousSelection':previous,'correction':'短前掌朝画面下方略右的SE，支撑膝踝同向' if n in [1,2,3,4,10,16] else '保持悬空摆腿原相位，缩短长鞋底、放松上翘脚掌并收正SE鞋尖'})
    else:
        f['reuseReason']='实际原PNG已查看，鞋尖膝踝朝向和现有抬腿/承重相位可沿用；保留旧生成记录不改写'
        f['dynamicReview']='not_verified'
    reviews.append({'frame':n,'source':f['source'],'action':'局部鞋踝修正' if n in repairs else '原图审核沿用','staticReview':f.get('correction',f.get('reuseReason'))})
# Validate before selecting. Do not alter submitted prompt text or old provenance.
errors=[]
for f in selection['frames']:
    p=B/f['source']; rec=json.loads((B/f['generationRecord']).read_text(encoding='utf-8'))
    im=Image.open(p)
    if im.mode!='RGBA' or min(im.size)<1024: errors.append([f['frame'],'native_mode_or_size'])
    if h(p)!=f['sourceSha256'] or rec['sha256']!=h(p): errors.append([f['frame'],'source_sha'])
    if f['frame'] in repairs:
        if h(B/rec['prompt'])!=rec['promptSha256']: errors.append([f['frame'],'prompt_sha'])
        for ref in rec['references']:
            if h(Path(ref['path']))!=ref['sha256']: errors.append([f['frame'],'reference_sha',ref['path']])
        if not (B/rec['evidence']['receipt']).exists(): errors.append([f['frame'],'receipt_missing'])
        if rec['actualModel'] is not None or rec['actualQuality'] is not None: errors.append([f['frame'],'actual_must_be_unconfirmed'])
assert len({f['sourceSha256'] for f in selection['frames']})==16
assert not errors, errors
for p,rec in newrecords:p.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
selection.update({'review':'SE16完整候选：逐图实看后保留6帧旧源，10帧仅局部修鞋踝外撇/长前掌。与竹弓SE同向实际图对照，腿相位与手别沿用。静态检查完成，正常速度接地、脚锁、比例衔接待主预览实播。','updatedAt':datetime.datetime.now().astimezone().isoformat(),'frameDurationMs':75,'cycleDurationMs':1200,'timingAuthority':'主窗口最新用户反馈：正常16×75ms，移除旧快档','dynamicAcceptance':False,'remaining':['主窗口1200ms真实播放检查16到01和04到05、12到13衔接','地面接触与重心、脚锁和小尺寸手脚清楚程度需统一导出实播','本机客户端未接入'], 'readonlyMotionReference':{'character':'09_bamboo_archer_girl','viewed':['preview/qa/run-SE-contact.png','runtime/run/SE/01.png','runtime/run/SE/05.png','runtime/run/SE/13.png'],'use':'仅鞋尖膝踝几何和短前掌参考，不搬外形、武器、帧号'}})
selection_path.write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
audit={'direction':'SE','selectedFrames':16,'repairedFrames':repairs,'retainedFrames':kept,'nativeUniqueSha256Count':16,'validationErrors':errors,'configuredTarget':{'model':'gpt-image-2.5-sunburst','quality':'max'},'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'modelNote':'内置宿主管理入口未披露型号质量，目标不冒充实测','dynamicAcceptance':False,'frames':reviews}
(B/'provenance/run-SE-foot-static-review.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for mode in ['contact','feet']:
    cw,ch=(300,324) if mode=='contact' else (360,218)
    canvas=Image.new('RGB',(cw*4,ch*4),(225,228,231));d=ImageDraw.Draw(canvas)
    for i,f in enumerate(selection['frames']):
        im=Image.open(B/f['source']).convert('RGBA')
        if mode=='feet':im=im.crop((280,850,1120,1254))
        im.thumbnail((cw-12,ch-28))
        x=(i%4)*cw+(cw-im.width)//2;y=(i//4)*ch+24
        canvas.paste(im,(x,y),im)
        d.text(((i%4)*cw+8,(i//4)*ch+5),f"SE {f['frame']:02d} "+('foot fix' if f['frame'] in repairs else 'retain'),fill=(25,30,35))
    canvas.save(B/f'provenance/run-SE-foot-selected-{mode}.jpg',quality=94)
print(json.dumps({'selected':16,'repaired':repairs,'retained':kept,'unique':16,'errors':errors,'selection':str(selection_path)},ensure_ascii=False))

