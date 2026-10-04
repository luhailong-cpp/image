import json,sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
root=Path(__file__).resolve().parents[2]
passed={int(x) for x in sys.argv[1:]}
ip=root/'inventory-cast.json';inv=json.loads(ip.read_text(encoding='utf-8'))
qp=root/'records/cast-qa-20261003.json';qa=json.loads(qp.read_text(encoding='utf-8'))
known=set(range(6,13))|{14}
stamp=datetime.now(ZoneInfo('America/New_York')).isoformat()
reason='当前图实际逐张检查：侧身近侧解剖右肩经前方袖肘腕接五张红符；远侧左肩经后方袖接铜铃；总共两臂两袖。两鞋跟到尖轴均朝右，未见相反方向或V字外撇；保留自然膝弯与透视。单帧通过，整段动态/客户端仍待验。'
for f in inv['frames']:
 if f['direction']=='E' and f['frame'] in passed:
  rp=root/f['source_record'];r=json.loads(rp.read_text(encoding='utf-8-sig'))
  if 'arm-chain' not in str(rp):raise RuntimeError('not new arm repair '+str(rp))
  r['visualQA']={'status':'single_frame_reviewed_sequence_pending','reviewedAt':stamp,'handOwnershipPassed':True,'sleeveCount':2,'cardCount':5,'footAxisPassed':True,'findings':reason,'fullSequencePassed':False}
  rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  f['visual_status']=r['visualQA']['status']
  for q in qa['frames']:
   if q['direction']=='E' and q['frame']==f['frame']:
    q.update(sha256=f['sha256'],source_record=f['source_record'],status=f['visual_status'],findings=reason,armOwnershipRepaired=True)
    with Image.open(root/f['path']) as im:q['bounds_alpha_gt16']=im.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox()
done={f['frame'] for f in qa['frames'] if f['direction']=='E' and f.get('armOwnershipRepaired')}
failures=['E'+str(n).zfill(2) for n in sorted(known-done)]
inv.setdefault('qa_summary',{})['knownHandOwnershipFailures']=failures
inv['qa_summary']['armOwnershipRepairedFrames']=['E'+str(n).zfill(2) for n in sorted(done)]
qa['knownHandOwnershipFailures']=failures;qa['summary']['reviewedAt']=stamp
qa['armChainRepair']={'completedFrames':['E'+str(n).zfill(2) for n in sorted(done)],'remainingFrames':failures,'pastCorrection':'旧E06–12曾归属反转，旧E14三袖；历史SHA记录保留，当前按新图独立验。','fullSequencePassed':False}
for path,obj in [(ip,inv),(qp,qa)]:path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'repaired':sorted(done),'remaining':failures}))
