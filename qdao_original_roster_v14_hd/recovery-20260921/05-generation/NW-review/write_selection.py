from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image,ImageSequence
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=json.loads((P/'snapshot.json').read_text(encoding='utf-8'))
phase={1:'Left planted / right rear toe, first contact',2:'Left support / right heel rise',3:'Left support / right lifted recoil',4:'Left support / right approaching passing',5:'Left support / right folded passing',6:'Left support / right small swing',7:'Right forward / left rear toe, pre-opposite contact',8:'Right forward / left trailing heel-up',9:'Right contact / left rear toe, opposite contact',10:'Right support / left heel rise',11:'Right support / left folded recovery',12:'Right support / left folded before passing',13:'Right support / left passing',14:'Right rear toe / left forward lowered swing',15:'Right rear toe / left forward lower swing',16:'Right rear toe / left almost-contact, loop approach'}
for row in s['rows']:
 row['visualReview']='static_reviewed_with_qualifications_root_loop_pending'
 row['staticPoseObservation']=phase[row['frame']]
 row['issues']=[]
 if row['frame'] in (1,7):row['issues'].append('Isolated purple background point remains visible only in 1:1 legs crop after AI cleanup retry; final cleanup decision required before claiming no residual pixels.')
 if row['frame']==12:row['issues'].append('Crown top rises 24px on 1024 canvas versus11; offline loop review must judge this visible bob.')
 if row['frame']==16:row['issues'].append('16-to01 visible-height difference13px on1024 canvas; axis and lowest-support anchor remain fixed.')
selected={r['slot']:r['output'] for r in s['rows']}
issues=[{'scope':'NW01/NW07','severity':'minor','status':'remaining','description':'AI cleanup removed large detached debris, but one tiny isolated purple point remains at edge of enlarged crop. Do not claim perfectly clean alpha.'},{'scope':'NW11→12','severity':'review','status':'root_loop_pending','description':'Visible height770→794px,24px crown/top change; both retain fixed support anchor y942. Requires 30ms playback judgement.'},{'scope':'NW16→01','severity':'review','status':'root_loop_pending','description':'Visible height787→774px,13px top difference; correct same boot assignment, fixed support anchor and no frame duplication.'},{'scope':'NW06→07 and13→14','severity':'review','status':'root_loop_pending','description':'Support transfer and boot orientation change more than adjacent recoil phases; real distinct phases and two alternating leg cycles are visible, full-speed judgement still needed.'}]
report={**s,'updatedAt':datetime.now(timezone.utc).isoformat(),'selected':selected,'rows':s['rows'],'status':'16_native_frames_static_reviewed_root_loop_pending','approval':False,'staticReview':{'normalLight':True,'normalDark':True,'enlargedLegsLight':True,'enlargedLegsDark':True,'seam15_16_01_02Light':True,'seam15_16_01_02Dark':True,'singleCharacterIdentityAndNwDirection':True,'twoAttachedLegsAndBoots':True,'alternatingSupportVisible':True,'largeGreyWhiteArtifactNW04Removed':True,'allAlphaResidualsCleared':False,'animatedPlaybackViewedByThisAgent':False},'issues':issues,'rejectedOrSuperseded':[{'archive':'NW04-single-v1','reason':'Detached grey-white triangle under left sleeve; visually corrected inNW04v2.'},{'archive':'NW01-single-v1','reason':'Purple point cleanup retry, selectedv2; residual tiny point still qualified.'},{'archive':'NW07-single-v2','reason':'Purple point cleanup retry, selectedv3; residual tiny point still qualified.'},{'archive':'NW09-single-v5','reason':'Purple point cleanup retry; v6 cleaner and selected.'},{'archive':'NW11-single-v1','reason':'Old prepared request only, no successful raw/tool result. Do not count as successful generation.'}],'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin tool did not expose model/quality selectors or verifiable response values.','cleanupPolicy':'No image deletions by this subagent; parent must verify final export and current references before authorized cleanup. Retain text provenance.','clientValidationPerformed':False}
for f in P.glob('*'):
 if f.suffix in ('.png','.gif','.webp'):
  data={'file':str(f),'sha256':sha(f),'operation':'offline-static-contact-or-loop-preview-only','derivedFrom':[{'file':r['output'],'sha256':r['sha256'],'generationRecord':r['generationRecord']} for r in s['rows']],'generationCalls':0,'paidApiCalls':0}
  if f.suffix=='.gif':
   im=Image.open(f);data['durationMs']=[frame.info.get('duration') for frame in ImageSequence.Iterator(im)];assert data['durationMs']==[30]*16
  write(f.with_name(f.name+'.generation.json'),data)
write(P.parent/'NW-selection.json',report)
print(json.dumps({'selection':str(P.parent/'NW-selection.json'),'frames':len(selected),'rawDistinct':len({r['rawSha256'] for r in s['rows']}),'pixelsDistinct':len({r['pixelSha256'] for r in s['rows']}),'heights':[r['visibleHeight'] for r in s['rows']],'issues':issues},ensure_ascii=False))
