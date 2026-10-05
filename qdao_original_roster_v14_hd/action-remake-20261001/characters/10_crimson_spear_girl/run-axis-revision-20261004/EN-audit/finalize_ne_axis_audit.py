from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
R=Path(__file__).resolve().parents[2];W=R/'run-axis-revision-20261004';O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selected={'15':'15-v1','16':'16-v2','01':'01-v1'}
rows=[]
for direction in ['E','NE']:
 for n in range(1,17):
  f=f'{n:02d}';p=R/'runtime/run'/direction/f'{f}.png'
  status='acceptable perspective; no definite outward-yaw defect found'
  notes='Side-view toe remains screen-right. Heel rise and ankle flexion are normal running motion.' if direction=='E' else 'Back-oblique running plane; no definite shoe yaw reversal found.'
  if direction=='NE' and f in ['15','16','01']:
   status='definite original fault; corrected candidate selected'
   notes='LEFT swing shoe previously displayed front white toe toward camera, opposite the NE travel plane. Candidate restores rear heel/sole view, preserves RIGHT support and frame-specific knee bend.'
  if direction=='NE' and f in ['11','12']:
   status='uncertain lateral swing spread; retained'
   notes='Left swing leg spreads more laterally before recentering at13. Projection/overlap can explain this; no confident same-foot toe reversal, so no redraw.'
  rows.append({'slot':f'run/{direction}/{f}','reviewedRuntimeSHA256':sha(p),'classification':status,'notes':notes})
for slot,folder in selected.items():
 p=W/'NE'/folder/'native.png';meta_path=Path(str(p)+'.generation.json');m=json.loads(meta_path.read_text(encoding='utf-8'))
 im=Image.open(p).resize((1024,1024),Image.Resampling.LANCZOS);old=Image.open(R/'runtime/run/NE'/f'{slot}.png')
 m['status']='visually-reviewed-candidate-selected-awaiting-root-publication'
 m['axisReview']={'scope':'anatomical LEFT swing boot yaw only; RIGHT support preserved','sequence':'NE14→15→16→01→02','fullBodyReviewed':True,'bothHandsAndFullSpearVisible':True,'observedGlobalZoom':False,'technicalRegistrationApplied':False,'runtimeAlphaBBox':old.getchannel('A').point(lambda x:255 if x>=32 else 0).getbbox(),'candidateAt1024AlphaBBox':im.getchannel('A').point(lambda x:255 if x>=32 else 0).getbbox(),'independentlyGenerated':True,'actualModel':None,'actualQuality':None}
 meta_path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
reject=W/'NE/16-v1/native.png.generation.json';m=json.loads(reject.read_text(encoding='utf-8'));m['status']='rejected';m['rejectionReason']='Tool copied reference15 support-leg position and shortened right supporting-leg extension. This does not preserve runtime16 support point.';reject.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
selection={'slots':{f'run/NE/{s}':f'run-axis-revision-20261004/NE/{folder}/native.png' for s,folder in selected.items()},'review':'run-axis-revision-20261004/EN-audit/AXIS_AUDIT.md','timing':'16 frames x75ms; unchanged','publicationState':'not-published'}
(W/'NE/selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'axis-audit.json').write_text(json.dumps({'scope':'E+NE runtime32 review; 3 NE local boot edits selected','runtimeModified':False,'rows':rows,'selected':selection},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selection':str(W/'NE/selection.json'),'runtimeModified':False,'selectedSHA256':{s:sha(W/'NE'/f/'native.png') for s,f in selected.items()}}))

