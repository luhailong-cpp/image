from pathlib import Path
import json,hashlib,runpy
from datetime import datetime,timezone
from PIL import Image
folder=Path(__file__).resolve().parent
actor=folder.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sel=['01-v6','02-v2','03-v4','04-v3','05-v4','06-v2','08-v2','09-v2','07-v2','10-v1','11-v2','12-v2','15-v3','13-v2','14-v2','16-v2']
phase=['right_contact','right_loading','right_midstance','right_toeoff','flight_to_left_early','flight_to_left_apex','flight_to_left_descend','left_precontact','left_contact','left_loading','left_midstance','left_toeoff','flight_to_right_early','flight_to_right_apex','flight_to_right_descend','right_precontact']
notes=[
'原右落地母版；右脚支撑、左腿后折、右空臂后摆。',
'右膝承重，保住右支撑左后折；淘汰02-v1疑似换腿。',
'右中撑、左腿前通过，右空拳收腰侧；修复旧03后摆。',
'右蹬，使用03-v4同尺度局部踮脚；空右臂前摆遮挡，消除旧04-v2放大与伸脚过低。',
'从06-v2局部编辑右后腿，恢复头宽与画布尺度；双脚离地。',
'左前右后最高点；空右臂前摆遮挡。',
'复用本轮独立08-v2作为下降：左鞋边界1113，在06与下一帧之间。',
'复用独立09-v2作为接触前：左鞋边界1141，在下降1113与落地1149之间。',
'复用独立07-v2作为左落地：左鞋边界1149；相位按实际姿态重新归位。',
'左支撑压低，空右手向身侧回收。',
'左中撑，右腿收进远侧前方，和03右中撑已区分。',
'左鞋尖蹬地、右膝向前收，和04右蹬已区分；空右臂后摆。',
'复用独立15-v3作为初腾空：右腿前收鞋面可见、左腿后折、右臂后摆。',
'复用独立13-v2作为最高点：头顶约48，较前后帧身体位置更高；右前左后腿关系保持。',
'复用独立14-v2作为下降：头頂78，比14下降；右腿前、左腿后。',
'右腿接触前、左腿后折，右臂后摆；首尾鞋尖与根点仍需复核。']
issues={
1:['跨半周期与左落地的相机/根点水平位置尚需动态审核。'],
4:['右鞋尖踮地与根点需独立动态确认，未以最低像素做后处理。'],
9:['09→10最低边界1149→1140差9px；可能包含鞋姿变化，仍需接触点复核。'],
14:['头轮廓及根点与另一半周期存在小幅漂移，未做动态审核。'],
16:['接前最低边界1181比01落地1176低5px；首尾鞋尖接触与重心衔接未验收。']
}
inventory=[]
for p in sorted(folder.glob('*.png')):
    if not p.stem[:2].isdigit():continue
    im=Image.open(p); a=im.getchannel('A'); mask=a.point(lambda v:255 if v>16 else 0)
    meta=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
    r={'file':p.name,'sha256':sha(p),'width':im.width,'height':im.height,'mode':im.mode,'alphaExtrema':a.getextrema(),'alphaGt16Bounds':mask.getbbox(),'upper500RowsBounds':mask.crop((0,0,im.width,500)).getbbox(),'generationRecordShaMatches':meta['sha256']==sha(p),'promptExists':(actor/meta['prompt']).exists(),'requestExists':(actor/meta['evidence']['request']).exists(),'receiptExists':(actor/meta['evidence']['receipt']).exists(),'actualModel':meta.get('actualModel'),'actualQuality':meta.get('actualQuality'),'selectedCandidate':p.stem in sel}
    inventory.append(r)
by={x['file'][:-4]:x for x in inventory}
frames=[]
for i,s in enumerate(sel,1):
    r=by[s]; assert (r['width'],r['height'],r['mode'])==(1254,1254,'RGBA')
    frames.append({'frame':i,'source':'generation/run/NW/'+s+'.png','sha256':r['sha256'],'status':'recommended_after_targeted_limb_review_pending_independent_dynamic_review','phase':phase[i-1],'notes':notes[i-1],'issues':issues.get(i,[]),'nativeSize':[1254,1254],'generationRecord':'generation/run/NW/'+s+'.png.generation.json'})
selection={'direction':'NW','frameDurationMs':30,'reviewStatus':'targeted_limb_corrections_recommended_pending_independent_grounding_and_dynamic_review','exportApproved':False,'dynamicReviewed':False,'clientValidated':False,'frames':frames,'review':'generation/run/NW/static-review.json','contactSheet':'generation/run/NW/selected-contact.jpg','note':'文件名为生成目标，最终槽位按实际姿态选择。16槽16个不同SHA，不复制插值。'}
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save(folder/'selection.json',selection)
save(folder/'inventory.json',{'recordedAt':datetime.now(timezone.utc).isoformat(),'images':inventory,'note':'Bounds diagnostic only, no game asset postprocessing.'})
from PIL import ImageDraw,ImageFont
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
def contact(slots,cols,name):
    cell=314;labelh=46;canvas=Image.new('RGB',(cols*cell,((len(slots)+cols-1)//cols)*(cell+labelh)),(225,230,230));draw=ImageDraw.Draw(canvas)
    for k,s in enumerate(slots):
        im=Image.open(folder/(s+'.png')).convert('RGBA');im.thumbnail((cell,cell),Image.Resampling.LANCZOS)
        x=k%cols*cell;y=k//cols*(cell+labelh);tile=Image.new('RGB',(cell,cell),(238,240,238));tile.paste(im,((cell-im.width)//2,(cell-im.height)//2),im);canvas.paste(tile,(x,y))
        selectedindex=sel.index(s)+1 if s in sel else None
        draw.text((x+5,y+cell+2),('SLOT '+str(selectedindex).zfill(2)+' <- ' if selectedindex else '')+s,fill=(15,30,30),font=font)
        draw.text((x+5,y+cell+23),(phase[selectedindex-1] if selectedindex else 'NOT SELECTED'),fill=(105,30,30),font=font)
    canvas.save(folder/name,quality=94)
contact(sel,4,'selected-contact.jpg')
contact([x['file'][:-4] for x in inventory],6,'inventory-contact.jpg')
metrics=[{'frame':i+1,'source':s,'bounds':by[s]['alphaGt16Bounds'],'headEnvelopeUpper500':by[s]['upper500RowsBounds']} for i,s in enumerate(sel)]
save(folder/'recommended-metrics.json',metrics)
print(json.dumps({'total':len(inventory),'selected':len(frames),'distinctSha':len({f['sha256'] for f in frames}),'allRecordsValid':all(x['generationRecordShaMatches'] and x['promptExists'] and x['requestExists'] and x['receiptExists'] for x in inventory),'metrics':metrics},ensure_ascii=False,indent=2))


