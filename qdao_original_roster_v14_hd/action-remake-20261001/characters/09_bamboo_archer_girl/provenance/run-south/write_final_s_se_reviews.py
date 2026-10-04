from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,os,uuid
R=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,data):
 t=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');t.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8');os.replace(t,p)
notes={
'S':[
'左支撑脚在前，鞋面与膝胫同轴，另一右腿后屈回收。','左脚前位继续加载，支撑膝轻屈，右脚折在身体之后。',
'左脚移至身下偏前承重，右膝开始经过身体。','同一左支撑继续，右膝高抬；持弓左手和空右手清楚。',
'左支撑位于身体之后的中后段，右脚前摆露底；已局部修正支撑小腿和靴。','同一左脚中后位承重，右摆脚进一步展开且鞋底可见；与05独立成图。',
'左支撑足在更后方，透视较短，右靴前摆抬起；本轮已拉开末段纵深。','左脚继续后位承重，右靴准备下一次接触；空手回前，左手完整握弓。',
'换为右脚前位承重，左腿折起，双脚身份可区分。','右脚前位加载，支撑膝缓冲，左脚回收。',
'右支撑逐步进入身下，左膝开始前摆。','右腿同一支撑，左膝抬起；双手分工与完整长弓保持。',
'右支撑在中后方，左腿向相机展开，鞋尖沿纵深；小支撑靴已独立修正。','右支撑继续中后位，左摆脚鞋底明显；与13为不同膝踝姿态。',
'右支撑更后，左前摆靴抬起、鞋底可读；脚尖未向两侧外撇。','右脚后位末段承重，左摆脚准备接下一循环；鞋长轴与膝胫一致。'],
'SE':[
'远侧左脚前位承重，近侧右腿后屈；完整弓固定于左手。','远侧左脚继续前位加载，右腿回收，鞋轴朝右下运动方向。',
'左支撑进入身下，近侧右膝向前经过；本轮按髋连接和遮挡独立重画。','同一左支撑继续，右膝抬起；支撑链不凭裤口屏幕位置单独认定。',
'左支撑移动到身后中段，近侧右腿前摆遮挡上段支撑腿，右鞋底可见。','左支撑仍在身后中段，右摆脚已抬高并露底，消除双脚像同时落地的读感。',
'左支撑继续向后侧延伸，近侧右腿在前方抬起；两个髋到膝的遮挡有连续性。','左后位支撑继续，右摆腿前伸更开、鞋底可见；与07独立姿态。',
'换为近侧右腿前位承重，左腿折后；鞋尖保持右下轴。','右脚前位加载，左腿回收，右手空拳开始反向回摆。',
'右腿进入身体下方支撑，左腿抬起，髋膝踝链可追踪。','右腿同一支撑到中位，远侧左膝前摆；本轮已替换旧腾空稿。',
'右支撑向身后中段延伸，左摆腿抬起，非两脚腾空。','右脚继续中后位，左摆脚展开并露鞋底；完整长弓不缺端。',
'右支撑进入后位，左摆脚抬起，空手与持弓手方向关系保持。','右后位支撑末段，左脚前伸准备下一循环，弓和箭筒方向一致。']}
selection={x['file']:x for x in read(R/'selection/run-south.json')['frames']}
now=datetime.now(timezone.utc).isoformat();allrows=[];seqs=[];verification=[]
for d in ['S','SE']:
 rows=[];hashes=[]
 for f in range(1,17):
  p=R/f'runtime/run/{d}/{f:02}.png';h=sha(p);hashes.append(h);im=Image.open(p)
  assert im.size==(1024,1024) and im.mode=='RGBA',(d,f,im.size,im.mode)
  assert im.getchannel('A').getextrema()==(0,255)
  sel=selection[p.relative_to(R).as_posix()];assert sel['sha256']==h
  gp=R/sel['generationRecord'];assert gp.exists()
  assert sha(gp)==sel['generationRecordSha256']
  rec=read(gp);assert rec['sha256']==h
  ns=rec.get('nativeSize') or rec.get('nativeCellSize') or sel.get('sourceNativeSize')
  assert ns and min(ns)>=1024
  row={'slot':f'run/{d}/{f:02}','frame':f,'file':p.relative_to(R).as_posix(),'sha256':h,'status':'passed','staticAnatomy':'passed','dynamicApproval':False,'evidence':notes[d][f-1],'footOrientation':'支撑/摆动鞋长轴随膝胫与运动纵深，未见双脚向左右横撇；不以最低像素判断承重。','visualEvidence':f'preview/qa/run-{d}-contact.png','reviewBasis':'当前16帧接触表及本轮局部修改原生图实际查看；只确认静态解剖和分组，未声明实播动态通过。'}
  rows.append(row)
 assert len(set(hashes))==16
 sources=read(R/f'preview/qa/run-{d}-preview.sources.json')
 assert [x['sha256'] for x in sources['sources']]==hashes
 assert sources['intendedMsPerFrame']==75
 for speed,ms in [('normal',75),('slow',300)]:
  apng=Image.open(R/f'preview/qa/run-{d}-{speed}.apng');assert apng.n_frames==16
  dur=[]
  for i in range(16):apng.seek(i);dur.append(apng.info.get('duration'))
  assert dur==[float(ms)]*16,(d,speed,dur)
 seg=[]
 for start,side in [(1,'left'),(9,'right')]:
  pos=[]
  labels=['前位落地和加载','身下偏前承重','身体经过后的中后支撑','后侧延伸与下一步准备']
  for k,label in enumerate(labels):
   fs=[start+2*k,start+2*k+1]
   pos.append({'frames':fs,'position':label,'evidence':'；'.join(notes[d][x-1] for x in fs),'independentPoses':True,'durationMs':150})
  seg.append({'foot':side,'continuousFrames':list(range(start,start+8)),'positions':pos})
 limits=['尚未完成正常速度和慢速整段实播视觉验收；本审阅不是游戏内无滑步保证。']
 if d=='S':limits.append('正面纵深的相邻两组投影距离较小，尤其13/14至15/16；结合膝胫姿态和足底承重判断，不宣称按提示词精确像素锁定。')
 else:limits.append('斜视下两腿交叉遮挡随摆动改变，按裆部/髋膝连接和前后层次追踪，不仅凭裤口屏左/右位置或最低脚像素。')
 audit={'reviewedAtUtc':now,'reviewer':'finish_south','action':'run','direction':d,'latestRequirement':'同脚连续8帧承重，四个逐步改变地面位置的阶段，每阶段两张独立姿态；左右交替。','staticPairedGroundStatus':'passed_with_perspective_limits','frameMs':75,'cycleMs':1200,'positionMs':150,'segments':seg,'frames':rows,'method':'当前原图/修图原生输出与完整16帧接触表实看；脚尖轴、髋膝踝、承重底及同脚遮挡联合判断。坐标用于指导和复核，不作为生成成功证据。','remainingIssues':limits,'dynamicVisualAcceptance':False,'clientIntegration':'not_integrated','technicalVerification':{'rgba1024':16,'uniqueFrameHashes':16,'selectionAndGenerationShaMatch':16,'nativeMin1024':16,'previewSourceShaMatch':16,'normalFrameDurationsMs':[75]*16,'slowFrameDurationsMs':[300]*16}}
 ap=R/f'audit/run-{d}-paired-ground-review.json';write(ap,audit)
 seqs.append({'sequence':f'run/{d}','status':'needs_review','staticPairedGroundStatus':audit['staticPairedGroundStatus'],'frameSha256':hashes,'evidence':'当前静态解剖及两段同脚支撑分组已实看；逐帧依据见'+ap.relative_to(R).as_posix(),'segments':seg,'remainingIssues':limits,'dynamicApproval':False,'currentTiming':{'frameMs':75,'cycleMs':1200,'frameDurationsMs':[75]*16,'extraLoopPauseMs':0,'clientTimingConfirmed':False},'previews':{'contact':f'preview/qa/run-{d}-contact.png','normal':f'preview/qa/run-{d}-normal.apng','slow':f'preview/qa/run-{d}-slow.apng'},'pairedGroundReview':ap.relative_to(R).as_posix()})
 allrows.extend(rows);verification.append({'direction':d,'frames':16,'verification':'passed','audit':ap.relative_to(R).as_posix(),'sha256':sha(ap)})
rp=R/'review-parts/run-south.json';old=read(rp)
old['frames']=[x for x in old.get('frames',[]) if not x['slot'].startswith(('run/S/','run/SE/'))]+allrows
old['sequences']=[x for x in old.get('sequences',[]) if x['sequence'] not in ['run/S','run/SE']]+seqs
old['reviewedAtUtc']=now;old['reviewer']='finish_south';old['updatedDirections']=['S','SE'];old['preservedDirections']=['W'];old['automaticApproval']=False
old['reviewMethod']='S/SE current static image audit; W previous records preserved for root merge with independent W reviewer.'
old['pairedGroundReviews']=[x['audit'] for x in verification];write(rp,old)
out={'completedAtUtc':now,'directions':['S','SE'],'frameCount':32,'checks':verification,'reviewPart':rp.relative_to(R).as_posix(),'reviewPartSha256':sha(rp),'runtimeWritesFinished':True,'dynamicApproval':False}
write(R/'provenance/run-south/final-current-verification.json',out)
print(json.dumps(out,ensure_ascii=False))

