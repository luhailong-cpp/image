from pathlib import Path
import json,hashlib,datetime,re
H=Path(__file__).resolve().parent;R=H.parents[1]
S=json.loads((R/'10-work/selection-current.json').read_text(encoding='utf-8-sig'))
S={k:v for k,v in S.items() if re.fullmatch(r'(N|S|W|NW)([0-9]{2}|idle)',k)}
S.update(json.loads((H/'selection-W-review.json').read_text()))
S.update(json.loads((H/'selection-NW-review.json').read_text()))
chosen={'N16':('N16-v5','N15/16/01/02 static comparison removes old26px head jump'),'S16':('S16-v2','N/S seam repair: removes old15->16 torso drop'),'NW01':('NW01-v4','Correct NW left contact with head/torso matched to02'),'NW16':('NW16-v2','Distinct near-left low precontact; far-right toe support, upper body matched to01v4'),'W06':('W06-v7','Far-right low forward swing with near-left grounded behind; upper body remains closer to09 half. Requires dynamic judgment of shoulder change from05'),'W14':('W14-v5','Near-left low forward swing and far-right planted; profile and chest match13 with small turn. Requires dynamic judgment14->15')}
for k,(a,note) in chosen.items():S[k]={'archive':a,'review':'Actual static review2026-09-28: '+note+'; dynamic full30ms loop pending'}
for k,v in S.items():
 d=re.match(r'(NW|N|S|W)',k).group();n=k[len(d):]
 v['nativeRootY']=1195
 v['nativeRootX']={'N':635,'S':605,'NW':620}.get(d,540 if n=='idle' or n in ['01','02','03','04','05','15','16'] else 500)
 v['registrationEvidence']='Manual pelvis projection/virtual ground on native1254cell; fixed finalroot; not minfoot flattening, not pose synthesis. W groups originate at distinct native horizontal placement.'
 p=R/'10-generation'/v['archive']/'raw.png'
 v['rawSHA256']=hashlib.sha256(p.read_bytes()).hexdigest()
out=H/'selection-updates-20260928.json'
out.write_text(json.dumps(S,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for d in ['W','NW']:
 (H/f'selection-{d}-review.json').write_text(json.dumps({k:v for k,v in S.items() if re.fullmatch(d+r'(\d\d|idle)',k)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
reviews={'W06-v3':('tool_error','Connection failed, no raw'),'W06-v4':('rejected','Far right boot stayed behind; repeats passing, wrong slot06'),'W06-v5':('rejected','Near left foreground leg swings instead of far right; wrong06 leg topology'),'W14-v2':('rejected','Turned toward camera/openmouth'),'W14-v3':('superseded','Correct gait but usev4 refinements'),'N10-v4':('rejected','Oversized left sole and alteredfar support length; unneeded exaggerated articulation; retainN10v3')}
for a,(status,note) in reviews.items():
 (R/'10-generation'/a/'visual-review.json').write_text(json.dumps({'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':status,'reason':note,'counted':False},indent=2)+'\n')
print({'slots':len(S),'walk':sum(not k.endswith('idle') for k in S),'idle':sum(k.endswith('idle') for k in S),'file':str(out)})
