from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,datetime
root=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
choices=['01-v1','02-v2','03-v2','04-v3','05-v5','06-v1','07-v1','08-v2','09-v5','10-v2','11-v1','12-v2','13-v3','14-v1','15-v1','16-v1']
phases=['right_contact','right_down','right_midstance','right_push','right_to_left_early_flight','right_to_left_flight_apex','right_to_left_flight_fall','left_precontact','left_contact','left_down','left_midstance','left_push','left_to_right_early_flight','left_to_right_flight_apex','left_to_right_flight_fall','right_precontact']
notes={
'01-v1':'沿用已存在独立原生帧；右脚落地、左脚后折，右空手后摆，左葫芦及NE方向清楚。',
'02-v2':'右承重腿关系正确，原生AI修正大头比例；头顶比01低约70像素，压低幅度偏大，需序列审查。',
'03-v2':'右支撑、左腿回收中撑可辨；原生AI修正比例后头身下移，髋/头竖向轨迹待总序列复核，右臂中间摆幅偏小。',
'04-v3':'定向修正后右腿后蹬、左腿前摆及右空手前摆可辨；鞋尖朝向/右脚尖接地、头身比例和骨盆位置需重点复核。',
'05-v5':'左右腿与右空手前摆关系保持；原生AI修正尺度后两脚离地，但左前腿略内收，需观察04-06连续性。',
'06-v1':'双脚离地、右腿后折右鞋底朝观众、右空手前摆；左小腿内收较多，腾空最高点的头部高度未完全达到提示词坐标。',
'07-v1':'保留左步下降、右腿后折；与06的高度及前腿伸展差异需动态核对。',
'08-v2':'修复08-v1错误右腿领步，当前左鞋接地前、右腿后折，右空手前摆。',
'09-v5':'修复错误支撑腿和反向左鞋；当前左脚落地、右腿后折，右空手前摆。头部较01略大。',
'10-v2':'修复10-v1错误支撑腿，当前左脚承重、右腿后折；头/髋下沉幅度偏大，需序列审查。',
'11-v1':'左脚中撑、右腿回收、右空手摆向中间可辨；头部较01略大。',
'12-v2':'左腿后蹬和右膝前送可辨、右空手后摆；原生AI缩回尺度，鞋尖触地是否稳定需检查。',
'13-v3':'右腿前送初腾空、左腿后伸、右空手后摆；修复13-v1换手与13-v2放大问题。',
'14-v1':'右步双脚离地轮廓清楚；最高点头部位置反而稍低于13，需修正重心轨迹或按序列确认。',
'15-v1':'右腿前伸准备落地、左腿后折；头部位置稍下移，需核对14-16连续性。',
'16-v1':'右脚接地前、左腿后折、右空手后摆；首尾衔接待动态检查。'
}
entries=[]
for i,slot in enumerate(choices,1):
    image=root/(slot+'.png'); gen=root/(slot+'.png.generation.json')
    im=Image.open(image); md=json.loads(gen.read_text(encoding='utf-8-sig'))
    assert im.size==(1254,1254) and im.mode=='RGBA'
    assert sha(image)==md['sha256']
    req=root/(slot+'.request.json'); receipt=root/(slot+'.tool-result.json'); prompt=root/(slot+'.prompt.txt')
    for f in [gen,req,receipt,prompt]: assert f.exists(),f
    entries.append({'slot':f'run/NE/{i:02d}','frame':i,'selectedVersion':slot,'path':image.as_posix(),'sha256':sha(image),'generationRecord':gen.as_posix(),'phase':phases[i-1],'durationMs':30,'nativeSize':[1254,1254],'mode':'RGBA','alphaExtrema':list(im.getchannel('A').getextrema()),'actualModel':None,'actualQuality':None,'reviewStatus':'selected_candidate_requires_sequence_review','runtimeReady':False,'notes':notes[slot]})
record={'schemaVersion':1,'direction':'NE','actor':'00_reference_topright_boy','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'generatedSlots':16,'frameDurationMs':30,'loopDurationMs':480,'status':'all_slots_have_independent_native_candidates_not_dynamic_accepted','visualPass':False,'dynamicReview':{'performed':False,'passed':False},'exportedByThisAgent':False,'fixedCanvas':{'width':1254,'height':1254,'rule':'No deterministic per-frame resizing, bounding-box fitting, minimum-pixel grounding, copying, interpolation or mirroring. Generated candidates retain native bytes.'},'configurationTarget':{'model':'gpt-image-2.5-sunburst','quality':'max'},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；无model/quality选择器，工具未披露实际版本与质量。','remainingIssues':['02/03/10的头/髋压低幅度偏大；04头身较大；跨帧尺度和固定根点仍需复核。','04/12的鞋尖接地与方向、05-07左前腿伸展和14最高点重心轨迹需序列审查。','本文件选择的是当前最佳独立候选，不能据16个不同SHA推断动作通过；尚未进行正常30ms/帧与慢速动态验收。'],'frames':entries}
(root/'selection.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
w,h,cell=1280,1400,320
sheet=Image.new('RGB',(w,h),'#e8eceb'); draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for i,e in enumerate(entries):
    x=(i%4)*cell;y=(i//4)*350
    im=Image.open(e['path']).resize((320,320),Image.Resampling.LANCZOS)
    sheet.paste(im,(x,y),im)
    draw.text((x+8,y+320),e['selectedVersion']+'  '+str(e['frame'])+'/16',font=font,fill='#173631')
    draw.line((x,y+349,x+320,y+349),fill='#a9bfba')
contact=root/'NE-candidate-contact.png';sheet.save(contact)
derivation={'file':contact.as_posix(),'sha256':sha(contact),'operation':'QA contact only: each complete native canvas uniformly reduced to 320x320, alpha-composited on neutral background, 4x4 grid. No PNG candidate modified.','derivedFrom':[{'file':e['path'],'sha256':e['sha256'],'generationRecord':e['generationRecord']} for e in entries]}
(root/'NE-candidate-contact.png.derivation.json').write_text(json.dumps(derivation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(root/'REVIEW.md').write_text('# NE 跑步候选交接\n\n16槽均有独立1254×1254透明RGBA候选，逐槽版本和SHA见 selection.json，联系表见 NE-candidate-contact.png。16槽齐全不等于动作通过。\n\n'+'\n'.join('- '+e['selectedVersion']+'：'+e['notes'] for e in entries)+'\n\n每帧实际model/quality均未披露，已保存真实prompt/request/tool-result/png.generation.json。原生PNG未做裁切、缩放、镜像、插值或最低脚贴地。尺寸纠正为独立内置AI编辑，保留各次请求与回执。当前较好候选仍需root统一尺度/根点/动态验收；不写frames、selected-new、manifest或全局review。旧候选暂留为当前编辑来源，正式导出及引用复核后由root按保留规则清理，保留所有文字记录。\n',encoding='utf-8')
print(json.dumps({'selected':len(entries),'uniqueSha':len(set(e['sha256'] for e in entries)),'contact':str(contact),'selection':str(root/'selection.json'),'allNativeRGBA':True,'dynamicAccepted':False},ensure_ascii=False))

