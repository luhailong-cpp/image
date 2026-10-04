from pathlib import Path
from PIL import Image
import hashlib, json
from datetime import datetime, timezone

A=Path(__file__).resolve().parent; B=A.parents[1]
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=read(A/'ne-w-selection.json'); chosen={f['slot']:f for f in s['frames']}
retained_notes={
'NE':{
1:'左前支撑靴侧面可读，脚掌长轴朝右上；右后腿自然回收，保留。',
2:'左支撑屈膝缓冲与01连贯；鞋轴未横向外扭，保留。',
3:'左承重腿与前送右膝区分可读；足掌仍顺NE，保留。',
4:'左脚蹬地、右腿开始前送；鞋掌可读，与05之间身体/手位变化需整组播放复核，未为此全画。',
5:'双脚短腾空并开始右腿前送；脚轴未明显外撇。连接新06时前送加大，保留原相位作前导。',
11:'右腿承重，左腿后收；鞋尖朝NE，扇手由后摆回前的肩臂变化需主窗口实播。',
12:'右脚抬跟蹬地、左后腿开始回收；掌轴与胫骨方向相符，保留。',
13:'第二短飞起始，左鞋朝NE；保留作为新14的前导，不把旧early_flight标签当自动通过。',
15:'左前腿下降，侧面鞋掌方向正确，右腿回收自然，与新14形状连续，保留。',
16:'左脚落地前与01同一鞋掌长轴，腿侧未交换，保留。'},
'W':{
1:'左向前掌与膝踝一致，另一腿折回；持扇手正确，左空手张开但手指清楚，保留该既有姿态。',
2:'缓冲腿与01连续且鞋尖朝左；空手指形清楚。接新03时躯干前侧转为侧后变化仍应重点播放复核。',
5:'短腾空起始，鞋尖均朝左；保留作为新06较低飞最高点前导。',
8:'前腿向前下方伸出，脚轴朝左；后腿屈膝回收，与新07连接，保留。',
9:'异侧接触，前足侧面轮廓清楚，掌轴朝左，保留。',
10:'接触后屈膝缓冲，鞋掌方向保持；与11手臂过渡保留供实播，未出现新增持物交换。',
11:'中间相位扇手靠近身前、空手靠近髋，鞋向左；新12收臂可减轻旧11→12幅度，保留。',
13:'第二短飞中前腿已前送，鞋向左且非外撇；按实图看是本半圈较高飞行点，旧early_flight标签未必准确。',
16:'前腿下降接近下一接触，鞋向左，后腿仍回收；保留并检查16→01实际播放。'}
}
retained=[]; allframes=[]; errors=[]
for z in ['NE','W']:
  for n in range(1,17):
    slot=f'run/{z}/{n:02d}'; d=read(B/'provenance/derived'/f'run-{z}-{n:02d}.json')
    if slot in chosen:
      f=chosen[slot]; p=B/f['source']; g=read(B/f['generationRecord']); req=read(B/g['evidence']['request'])
      checks={'sourceSha':sha(p)==f['sha256']==g['sha256'],'native1254RGBA':Image.open(p).size==(1254,1254) and Image.open(p).mode=='RGBA','promptExact':(B/g['prompt']).read_text(encoding='utf-8').strip()==req['submittedParameters']['prompt'].strip(),'receiptExists':(B/g['evidence']['toolResult']).is_file(),'actualModelNull':g['actualModel'] is None,'actualQualityNull':g['actualQuality'] is None,'submittedSelectorsNull':g['submittedParameters']['model'] is None and g['submittedParameters']['quality'] is None,'referenceSHAs':all(Path(r['file']).is_file() and sha(r['file'])==r['sha256'] for r in g['references'])}
      if not all(checks.values()): errors.append({'slot':slot,'checks':checks})
      runtime=A/'candidate-runtime'/f'{z}-{n:02d}.png'; box=Image.open(runtime).getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()
      allframes.append({'slot':slot,'decision':'use_local_edit_candidate','source':f['source'],'sha256':f['sha256'],'generationRecord':f['generationRecord'],'checks':checks,'lowestOpaquePixelRuntime':box[3]-1,'note':f['reason']})
    else:
      p=B/d['file']; r={'slot':slot,'decision':'retain_existing_pixels','runtime':d['file'],'runtimeSha256':sha(p),'originalSource':d['derivedFrom'],'note':retained_notes[z][n]}
      retained.append(r); allframes.append(r)
s['retained']=retained;s['selectedCount']=len(chosen);s['retainedCount']=len(retained);s['visualScope']='逐张原图/全部contact静态复核；当前子窗口浏览器不可用，主窗口需实际播放完整组，不代表动态通过'
s['sequenceReviewNotes']=['NE06→09前腿伸展与接触可读；NE10压缩后的鞋底比09上移约8个runtime像素，需正常速度观察承重。','W05→06→07→08低飞高度顺接；W13是本半圈实际较高飞行点，W14/15为近似同高度下降，不建议机械使用旧apex标签。','W03→04肩臂已接近，W02→03躯干转侧仍明显，请主审正常/慢速播放判断是否需最后过渡修图。','各方向仍保留自身相机/膝踝/道具身份，未镜像、复制、插值或逐图贴地。']
save(A/'ne-w-selection.json',s)
history=read(A/'ne-w-candidate-history.json')
selected_names={Path(x['source']).name for x in s['frames']}
for f in history['frames']:
  f['review']='selected_static_candidate' if Path(f['source']).name in selected_names else 'not_selected_retry_or_rejected'
history['note']='历史调用流水，未选条目不进入最终候选selection；每个模型回执及SHA原样保留。'
save(A/'ne-w-candidate-history.json',history)
report={'reviewedAt':datetime.now(timezone.utc).isoformat(),'scope':'NE/W32槽与09对应实图对照，局部13槽新候选，其余19保留','method':'view_image原图/全部contact/固定下肢对照；统计不是美术通过','reference':'09_bamboo_archer_girl current runtime as specified by user','oldAcceptanceNotReused':True,'selectedEdits':len(chosen),'retained':len(retained),'technicalErrors':errors,'browserAttempt':{'getState':'apps=[],browsers=[]','createIab':'Browser is not available: iab','playbackVerified':False},'clientIntegrated':False,'userAccepted':False,'timing':{'cycleMs':1200,'frameDurationsMs':[75]*16},'frames':allframes,'remainingSequenceChecks':s['sequenceReviewNotes']}
save(A/'ne-w-review.json',report)
print(json.dumps({'selected':len(chosen),'retained':len(retained),'technicalErrors':errors},ensure_ascii=False))
