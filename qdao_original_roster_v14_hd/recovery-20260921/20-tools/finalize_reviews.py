"""Bind completed visual inspections to the exact delivered character-20 files."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

R=Path(__file__).resolve().parent.parent
T=R/'20-tools'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
at=datetime.now(timezone.utc).isoformat()
audit=read(T/'all-final-checks.json')
assert audit['allPass'] and audit['rawFilesChecked'] and audit['count']==136
observations={
 'E':{
  'gait':'全部16帧及05/13原尺寸复查；05远靴后抬位于近支撑靴后侧，13另一只靴从后方抬起，前后遮挡关系换腿。接触、负重、后抬、通过和前伸均有独立姿态。',
  'identity':'固定右向侧视，星冠、长发、黑红象牙金袍、星盘与三卡保持；未镜像换手。',
  'seam':'实际启动15→16→01→02接缝播放，并在512深底逐一暂停复查四帧，前伸到接触与负重衔接通过。'},
 'SE':{
  'gait':'05–08修订后近侧星盘侧腿通过并前伸，远侧持卡侧腿保持支撑；09–13近侧腿支撑，14–16远侧腿前伸返回01。06 v3高踢腿拒用，06 v4恢复低幅短步。',
  'identity':'固定前右三分之四视角，解剖右手星盘、左手三卡，星冠及黑红象牙金袍稳定。',
  'seam':'修订后全圈及15→16→01→02接缝实际播放，四帧逐一暂停，未见明显首尾方向、装备或步幅跳变。'},
 'SW':{
  'gait':'08–13已重新生成相反支撑腿；09前伸远腿从中央黑金衣片左侧出现，近腿位于右后。05远抬靴在近支撑靴后方，13近抬靴覆盖远支撑靴，确认交替。06 v3为低幅通过姿态，07原独立稿保持。',
  'identity':'固定前左三分之四视角，保持原肖像头身和左右手装备。',
  'seam':'实际播放全圈与接缝，并逐一暂停15/16/01/02复查，前伸、落地、负重顺序通过。',
  'proportions':'冠顶alpha范围36–80，小幅步态与冠发变化；深浅底256/512动态观察未见整身比例突变，最低有效alpha统一y942。'}
}
for name,ds in [('E-SE',['E','SE']),('SW',['SW'])]:
 rows=[r for r in audit['rows'] if r['slot'].split('/')[1].removesuffix('.png') in ds]
 assert len(rows)==17*len(ds)
 for d in ds:
  observations[d].update(edges='全部16格深浅底及256/512循环已查看，轮廓完整、透明边缘无明显残底或裁切。',idle='独立双脚着地站立，深浅底、256及512四种组合均实际查看。')
 review={'schema':f'character20-{name}-visual-review-v1','reviewer':'/root','at':at,
  'character':'20_star_formation_master_girl','scope':{'directions':ds,'walk':16*len(ds),'idle':len(ds),'clientValidation':False},
  'status':'visual-assets-and-preview-passed','observations':{d:observations[d] for d in ds},
  'performed':{'currentFileHashes':rows,'currentGifChecks':[g for g in audit['gifs'] if g['file'].split('-')[0] in ds],
   'contactSheets':{'directions':ds,'framesPerDirection':16,'backgrounds':['dark','light']},
   'browserPreview':{'url':'http://127.0.0.1:8820/20-delivery-preview/index.html','tool':'mcp__cua_repl.js','directions':ds,
    'backgrounds':['dark','light'],'sizes':[256,512],'fullCyclePlayback':True,'observedFrameChanges':True,
    'seamPlayback':True,'seamPausedInspection':True,'seamFrames':[15,16,1,2],'independentIdleAtBothSizesAndBackgrounds':True,
    'continuousVideoCapture':False,'note':'实际启动播放，观察截图与帧号变化，并查看全部16格与关键帧；未测量显示器刷新时序。'},
   'fileTiming':{'allFrameMs':30,'gifFrames':16,'cycleMs':480,'browserDisplayCadenceMeasured':False}},
  'acceptance':{k:True for k in ['sourceAndDimensions','alphaAnchorsAndClipping','alternatingGaitAndSupport','proportionsAndEquipment','seam','visualApproval','previewClockRefresh']}}
 review['acceptance']['clientValidation']=False
 write(T/f'{name}-visual-review.json',review)

bound={};reports=[]
for name in ['N-NE','E-SE','S','SW','W-NW']:
 p=T/f'{name}-visual-review.json';v=read(p)
 assert v['acceptance']['visualApproval'] and not v['acceptance']['clientValidation']
 for row in v['performed']['currentFileHashes']:
  slot=row.get('slot',row.get('path'))
  assert slot not in bound,slot
  bound[slot]=row['sha256']
 reports.append({'path':f'../20-tools/{p.name}','sha256':sha(p),'directions':v['scope']['directions']})
assert bound=={r['slot']:r['sha256'] for r in audit['rows']}
approval={'schema':'character20-offline-acceptance-v1','at':at,'character':'20_star_formation_master_girl',
 'walkCount':128,'idleCount':8,'missingSlots':[],'unprocessedSelectedOriginals':[],
 'materialProduction':'passed','offlineVisualAcceptance':'passed','clientIntegration':'not-performed',
 'visualApproval':True,'clientValidation':False,'directions':{d:{'walk':16,'idle':1,'passed':True} for d in ['N','NE','E','SE','S','SW','W','NW']},
 'reviewReports':reports,'files':audit['rows'],'gifChecks':audit['gifs'],
 'technicalEvidenceBeforeRetention':{'path':'../20-tools/all-final-checks.json','sha256':sha(T/'all-final-checks.json'),'nativeRawBytesActuallyChecked':True},
 'nativeSources':{'uniqueCount':136,'size':[1254,1254],'completeSingleFrame':True,'explanation':'实际原图尺寸、逐图独立来源及1×1导出记录已核查，并逐图检查完整人物；早期原始记录的未确认标志原样保留。'},
 'generation':{'route':'built-in image_gen','actualModel':None,'actualQuality':None,'status':'host-managed/unverified','paidApiCalls':0},
 'preview':{'frameMs':30,'frames':16,'cycleMs':480,'backgrounds':['dark','light'],'reviewSizes':[256,512],
  'seamFrames':[15,16,1,2],'fileTimingVerified':True,'continuousVideoCapture':False,'displayRefreshMeasured':False},
 'scope':'Only character20 new movement assets; existing old actions and other characters left unchanged.'}
write(T/'offline-acceptance.json',approval)
print(json.dumps({'walk':128,'idle':8,'shaBoundVisualReviews':len(bound),'directionsPassed':8,'clientValidation':False}))
