from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
HERE=Path(__file__).resolve().parent; GEN=HERE.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
doc=json.loads((HERE/'snapshot.json').read_text());assert doc['frameCount']==doc['sourceDistinctCount']==doc['pixelDistinctCount']==16
for row in doc['rows']:
 assert sha(row['output'])==row['sha256'] and sha(row['raw'])==row['rawSha256']
 assert row['outputSize']==[1024,1024] and min(row['nativeSize'])>=1024 and row['anchor']==[512.,942]
 row['visualReview']='selected_after_static_review_pending_root_30ms_loop';row['selected']=True
doc.update(at=datetime.now(timezone.utc).isoformat(),approval=False,status='selected_static_complete_pending_root_30ms_loop',canonicalModified=False,clientValidated=False)
doc['staticReview']={'normalSize':256,'legCropNativePixels':True,'darkAndLightReviewed':True,'seamOrder':[15,16,1,2],'seamReviewSize':512,'fullSizeChecks':['SW14-dark','SW15-light','SW10-dark','SW11-light','SW12-dark','SW16-light'],'observations':['16 separately generated source images with one output slot each; exact prompts, receipts, native dimensions and SHA records preserved.','Purple hair, translucent ribbons, robe and zither identity remain consistent; no obvious magenta/blue matte fringes found on inspected exported dark/light sheets.','First passing SW05 raises screen-right boot; second passing SW13 raises screen-left boot. No foot lane crossing or extra limbs observed.','All export anchors are x512/y942. Visible height is824–845px; SW16→SW01 increases15px at fixed sole. Small face/crown/cloth drawing variations remain and must be judged during root loop review.','SW10v2/v3 wrongly used screen-left support and were rejected; selected SW10v4 keeps screen-right support.'],'notPerformed':['Real-time browser playback observation by this subagent','Unity or formal game-client acceptance']}
doc['rejected']=[{'archive':'SW09-single-v1','reason':'prior wrong-leg rejection retained from handoff'},{'archive':'SW10-single-v2','reason':'wrong support leg, screen-left foot lowest'},{'archive':'SW10-single-v3','reason':'wrong support leg, screen-left foot lowest'}]
doc['noResultRequests']=['SW04-single-v1','SW10-single-v1','SW11-single-v1','SW12-single-v1']
doc['retention']='Parent performs final cleanup after final exports and current references are verified; preserve text provenance even when raw/intermediate image files are removed.'
previews=[]
for p in sorted(HERE.glob('*.png'))+sorted(HERE.glob('*.gif'))+sorted(HERE.glob('*.webp')):
 metadata={'file':str(p),'sha256':sha(p),'operation':'offline-review-preview-derived-only','derivedFrom':[{'file':r['output'],'sha256':r['sha256'],'generationRecord':r['generationRecord']} for r in doc['rows']],'generationCalls':0,'actualModel':None,'actualQuality':None,'unverifiedReason':'Derived review preview only; source-image model and quality remain host-managed/unverified.'}
 with Image.open(p) as im:
  metadata['size']=list(im.size);metadata['frameCount']=getattr(im,'n_frames',1)
  if p.suffix=='.gif':
   durations=[]
   for n in range(im.n_frames):im.seek(n);durations.append(im.info.get('duration'))
   assert len(durations)==16 and durations==[30]*16
   metadata['frameDurationsMs']=durations;metadata['loopDurationMs']=sum(durations);metadata['loop']=0
 write(p.with_name(p.name+'.generation.json'),metadata);previews.append({'file':str(p),'sha256':sha(p)})
doc['previewFiles']=previews
write(GEN/'SW-selection.json',doc)
print(json.dumps({'selection':str(GEN/'SW-selection.json'),'frames':len(doc['rows']),'gif16x30msVerified':True,'newFinalHashes':[{k:r[k] for k in ('frame','sha256','rawSha256')} for r in doc['rows'] if r['frame']in[10,11,12,14,15,16]]},ensure_ascii=False))
