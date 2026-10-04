from pathlib import Path
import json,hashlib,datetime
b=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/20_star_formation_master_girl")
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
obj={'schemaVersion':1,'role':'20_star_formation_master_girl','createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'requirement':'同一支撑脚连续8帧，4个沿跑向相对空间段，每段两张独立真实承重姿态；另一脚后续8帧交替。','timing':{'frameCount':16,'frameMs':75,'cycleMs':1200,'positionPairMs':150},'configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8')),'actualModel':None,'actualQuality':None,'modelQualityEvidence':'内置image_gen无model/quality参数，返回未披露；配置目标不能充当实测。','transform':'AI返回1254方形仅整画布缩至1024；未使用922+offset二次缩放、bbox、最低点对齐、镜像、插值或复制凑帧。','status':'static_reviewed_pending_root_normal_preview','clientIntegration':'not_integrated','userAccepted':False,'integrationWarning':'先缓存旧runtime来源再覆盖：W/SW原04用于新07；SW原12用于新15。原SHA及sidecar快照见selected。','directions':{}}
for direction,first,second in [('W','left','right'),('SW','right','left')]:
 rows=json.loads((b/f'grounding4/{direction}/selected.json').read_text(encoding='utf-8'))
 assert len(rows)==16
 for r in rows:
  p=b/r['exportFile'];g=b/r['generationRecord'];assert p.exists() and g.exists() and sha(p)==r['sha256'];r['generationRecordSha256']=sha(g);r['exportFileAbsolute']=str(p).replace('\\','/');r['generationRecordAbsolute']=str(g).replace('\\','/');r['anatomicalSupportFoot']=r['supportFoot'];r['actualModel']=None;r['actualQuality']=None
  if r['exportFile'].startswith('runtime/'):
   r['priorGenerationRecordSnapshot']=json.loads(g.read_text(encoding='utf-8'));r['nativeKind']='existing_runtime_reuse_not_new_generation'
  else:
   r['nativeKind']='builtin_imagegen_native';record=json.loads(g.read_text(encoding='utf-8'));r['nativeSha256']=record['native']['sha256'];assert sha(Path(record['native']['file']))==r['nativeSha256'];assert record['receipt_sha256']==sha(Path(record['receipt']))
 positions=[]
 for start,foot in [(1,first),(9,second)]:
  for k,label in enumerate(['前侧直脚着地及缓冲','髋下承重经过','后侧承重推进','更后侧前掌接地并蹬离准备']):
   frames=[start+2*k,start+2*k+1]
   spatial=['支撑靴在髋的前方，朝跑向；膝踝接住重心','支撑靴接近髋下；身体经过支撑脚，另一腿抬起','支撑靴位于髋后；膝逐渐伸展，另一腿前摆','支撑靴更后，前掌仍压地、后跟自然抬起，另一脚准备下次落地'][k]
   positions.append({'frames':frames,'supportFoot':foot,'durationMs':150,'position':label,'spatialReading':spatial,'toeAxis':'向画面左的W侧向，保持膝踝靴轴一致' if direction=='W' else '向画面左下的SW透视，脚尖朝下略左，保持膝踝靴轴一致','twoDistinctImages':rows[frames[0]-1]['sha256']!=rows[frames[1]-1]['sha256'],'staticContactReviewed':True})
 obj['directions'][direction]={'selected':rows,'positionPairs':positions,'supportSegments':[{'foot':first,'frames':list(range(1,9)),'durationMs':600},{'foot':second,'frames':list(range(9,17)),'durationMs':600}],'replacements':[r for r in rows if r['mode']!='retain'],'retainedFrames':[r['frame'] for r in rows if r['mode']=='retain'],'contactSheet':f'grounding4/{direction}/selected-contact.jpg','normalApng':f'grounding4/{direction}/selected-normal.png','staticReviewed':True,'dynamicReviewed':False,'dynamicReviewPending':'主根合入后在当前预览1×/慢放/逐帧检查；子代理仅完成静态全16及相邻pair复核。','unresolvedStaticItems':[],'notes':'W15-v1落点过低、SW早期03/04落点偏前、05/06与13/14过长支撑胫已针对性重试；被替代稿未计入选择。'}
(b/'provenance/grounding-pairs-W-SW.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({d:{'total':len(v['selected']),'retained':v['retainedFrames'],'replaceCount':len(v['replacements'])} for d,v in obj['directions'].items()},ensure_ascii=False))

