import datetime,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw

BASE=Path('D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001')
OUT=BASE/'review-all-actions-20261004/group-c'
sources=json.loads((OUT/'source-evidence.json').read_text(encoding='utf-8'))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
ids=['10_crimson_spear_girl','14_short_hair_snow_summoner_girl']
findings={
ids[0]:[
dict(kind='support_identity_and_phase_needs_owner_review',action='run',direction='E',frames=[4,5,12,13],confidence='tentative',note='04→05、12→13时伸向前方的鞋转为明显承重、另一鞋后收，静态画面疑似比8帧连续同足支撑更早交替。但不能只按画面最低脚或前后位置认定解剖换足；W04/05和E04/05原成品已经单张放大检查，髋部仍部分被裙遮挡。窗口需标注同一只解剖足并连播追踪，再决定改图/重排。不得据此直接强制重排正确帧。'),
dict(kind='support_identity_and_phase_needs_owner_review',action='run',direction='W',frames=[4,5,12,13],confidence='tentative',note='04/05单帧可见前伸足由伸腿变屈膝承重，原后侧足转后收。作为支撑足身份/阶段疑点送窗口，未把屏幕脚位变化等同解剖换足。'),
dict(kind='continuity_needs_playback_review',action='run',direction='NE',frames=[3,9,10],confidence='medium',note='03的头/上躯干视角与02/04有单帧偏移；09→10腿脚支撑轮廓与上身角度改变较大。需75ms正常尺寸连播并核对相邻来源，静态不能断言换足/错排。'),
dict(kind='continuity_needs_playback_review',action='run',direction='NW',frames=[10,11,12],confidence='medium',note='10→11髋下短支撑轮廓变成长斜腿并将脚点明显拉向画面右下。该腿膝踝鞋轴相对直，问题主要是足位推进突变待动态核验，不把正常后蹬伸腿单独判外翻。'),
],
ids[1]:[
dict(kind='possible_persistent_toe_out_needs_owner_review',action='run',direction='SE',frames=[2,3,4],confidence='tentative',note='支撑靴鞋头朝画面右侧，比当前膝向更接近E侧面；全表和3张单帧均检查过。存在正常SE透视可能，需沿髋膝踝鞋轴及相邻帧连播核定；若确实偏航外撇则定向局修。尚未确认必须重画，不宣称无外撇通过。'),
dict(kind='reviewed_normal_pitch_not_confirmed_yaw_error',action='run',direction='NW',frames=[11],confidence='medium',note='单帧复核后侧抬起鞋露底可由正常屈膝/抬跟解释；没有仅凭露底确认横扭错误，不建议因此机械把鞋底转回地面。'),
]}
reviews=[]
for cid in ids:
    src=[f for f in sources['frames'] if f['character']==cid]
    all_current=[];changed=[]
    for f in src:
        p=Path(f['path']);sha=hashlib.sha256(p.read_bytes()).hexdigest()
        row=dict(f,currentSHA256=sha,currentVerifiedAtUTC=now,changedSinceContact=sha!=f['sha256'])
        all_current.append(row)
        if row['changedSinceContact']:changed.append(row)
    cover=[]
    for a in ['run','hit','attack','cast']:
        dirs=['N','NE','E','SE','S','SW','W','NW'] if a=='run' else ['E','W']
        for d in dirs:
            cover.append(dict(action=a,direction=d,count=sum(f['action']==a and f['direction']==d for f in src),actuallyViewed=True,method='complete ordered full-frame contact sheet including enlarged shoulder-arm-hand crop',feetExtraViewed=(a=='run' or (cid==ids[0] and a=='attack') or (cid==ids[1] and a=='cast')),verdict='static_inspected_not_final_pass',contactFull=(OUT/cid/f'{a}-{d}-full.png').as_posix(),contactFeet=(OUT/cid/f'{a}-{d}-feet.png').as_posix()))
    for finding in findings[cid]:
        finding['files']=[next(f['path'] for f in all_current if f['action']==finding['action'] and f['direction']==finding['direction'] and f['frame']==n) for n in finding['frames']]
        finding['sha256']=[next(f['currentSHA256'] for f in all_current if f['action']==finding['action'] and f['direction']==finding['direction'] and f['frame']==n) for n in finding['frames']]
    singles=['runtime/run/W/04.png','runtime/run/W/05.png','runtime/run/E/04.png','runtime/run/E/05.png'] if cid==ids[0] else ['run/SE/02.png','run/SE/03.png','run/SE/04.png','run/NW/11.png','run/SW/06.png','attack/E/05.png','attack/E/06.png']
    review=dict(character=cid,reviewedAtUTC=now,scope='independent static sequence audit of current final files; no image editing; no browser playback in this audit',rosterAndHandoffRead=True,portraitActuallyViewed=True,runTiming='16 independent frames x75ms=1200ms; unchanged',coverage=cover,inspectedFrames=len(src),findings=findings[cid],hands='All14 groups inspected against portrait and roster. No confirmed swapped holding side, detached grip, missing hand or malformed shoulder/elbow chain found at displayed resolution. Occluded joints and finger count remain limited; this statement is not an artistic pass.',grounding='Every position should contain two independently drawn successive poses; support foot progresses front→under pelvis→rear→push-off. Static pose sequencing was inspected but physical ground contact duration/pivot requires playback/client confirmation.',limits=['No dynamic playback or client integration performed in this independent audit.','No blanket artistic pass from counts or manifest labels.','Natural knee bend, foot pitch and occlusion do not alone prove toe-out yaw.','Source PNGs were not modified. Only QA derivatives/evidence were written.'],singleFramesActuallyViewed=singles,changedSinceContact=changed,frames=all_current,userAccepted=False)
    if cid==ids[1]:
        review['latestChangedFramesActuallyViewed']=['run/SW/06','attack/E/05','attack/E/06']
        review['changedFrameNotes']='SW06、attack/E05、E06 were re-opened as current PNGs after SHA difference was detected. All3 current images have been seen; SW06 lower-leg/boot axis and attackE05/06 wrist, fox holding and footwear have no new confirmed hard error. Stale contact SHAs must not be reused as final acceptance.'
        sh=Image.new('RGB',(3*420,455),(244,240,225));dd=ImageDraw.Draw(sh)
        for j,f in enumerate(changed):
            if j>=3:break
            im=Image.open(f['path']).convert('RGBA').resize((420,420),Image.Resampling.LANCZOS)
            dd.text((j*420+8,5),f"{f['action']}/{f['direction']}/{f['frame']:02d} {f['currentSHA256'][:10]}",fill='black');sh.paste(im,(j*420,30),im)
        sh.save(OUT/cid/'latest-3-directly-reviewed.png')
    (OUT/cid/'static-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
    reviews.append(dict(character=cid,groupsInspected=len(cover),framesInspected=len(src),changedSinceContact=len(changed),findings=len(findings[cid]),report=(OUT/cid/'static-review.json').as_posix()))
(OUT/'review-summary.json').write_text(json.dumps(dict(reviewedAtUTC=now,reviews=reviews,delegatedElsewhere={'15':'root','17':'group-a','20':'root'},noClaimOfDynamicPass=True),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(reviews,ensure_ascii=False))
