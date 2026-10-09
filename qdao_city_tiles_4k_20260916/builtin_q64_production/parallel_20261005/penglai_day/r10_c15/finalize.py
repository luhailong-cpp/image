from pathlib import Path
import sys,json,numpy as np,shutil,datetime
from PIL import Image
sys.dont_write_bytecode=True
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_day/r10_c15');O=R/'repairs/external';sys.path.insert(0,str(R/'repairs/internal'));import quilt as q
# Correct provenance to describe the actual already-saved computations.
for axis in ['north','west']:
 f=O/(axis+'-ai-strip-v2.png.generation.json');d=json.loads(f.read_text(encoding='utf8'));d['derivedFrom']=[v for v in d['derivedFrom'] if 'west-wall-clean' not in v['file']];f.write_text(json.dumps(d,indent=2),encoding='utf8')
 f=O/(axis+'-v2-replacement.png.generation.json');d=json.loads(f.read_text(encoding='utf8'));fields=np.load(O/(axis+'-v2-fields.npz'))
 d['operation'].update(perimeterFieldCap=24,protectedStartReturnFieldCap=32,totalTheoreticalCap=56,actualMaxCorrection=float(abs(fields['field']).max()),returnFieldFadePixels=220,fieldSmoothing='perimeter two49pxbox, first557return17pxcross-strip smoothing only')
 d['operation'].pop('cap',None)
 if axis=='west':
  p=O/'west/west-wall-clean-generated.png'
  if not any(v['file']==str(p) for v in d['derivedFrom']):d['derivedFrom'].append({'file':str(p),'sha256':q.sha(p),'generationRecord':str(p)+'.generation.json'})
  d['operation'].update(wallCleanupMaskField='wallCleanupMask',wallCleanupMethod='genuine AI wall-joint removal in exact recorded polygon')
 f.write_text(json.dumps(d,indent=2),encoding='utf8')
# Make script future reruns match this metadata.
f=O/'integrate_v2.py';s=f.read_text(encoding='utf-8-sig');s=s.replace("native+owners+([O/'west/west-wall-clean-generated.png'] if axis=='west' else [])","native+owners").replace("save(restore(rep),rp,[source,qp,mp],","save(restore(rep),rp,[source,qp,mp]+([O/'west/west-wall-clean-generated.png'] if axis=='west' else []),").replace("'cap':24,","'perimeterFieldCap':24,'protectedStartReturnFieldCap':32,'totalTheoreticalCap':56,'actualMaxCorrection':float(abs(f).max()),");f.write_text(s,encoding='utf8')
for name,src,box in [('pile-edge-long-review.png','r10_c15-candidate-review-v1.png',[300,600,650,1500]),('pile-edge-review.png','r10_c15-candidate-review-v1.png',[300,820,650,1180]),('pile-lip-full-final.png','r10_c15-candidate-review-v3.png',[270,780,650,1570])]:
 q.record(R/'qa'/name,[R/'tiles'/src],{'method':'native QA crop','boxLTRB':box})
src=R/'tiles/r10_c15-candidate-review-v3.png';dest=R/'tiles/r10_c15-candidate-final.png';shutil.copy2(src,dest);q.record(dest,[src],{'method':'byte-identical final local candidate export after native seam QA','globalRectXYWH':[57344,36864,4096,4096],'formalAccepted':False})
im=Image.open(dest).convert('RGB');a=np.asarray(im);p=R/'preview-final.png';im.resize((1254,1254),Image.Resampling.LANCZOS).save(p);q.record(p,[dest],{'method':'preview only downscale','neverFinalArt':True})
manifest=json.loads((O/'handoff-review-v1.json').read_text(encoding='utf8'))
for label,base in [('external',Path(manifest['selfBase']['file'])),('all',R/'tiles/r10_c15-candidate.png')]:
 di=np.any(a!=np.asarray(Image.open(base).convert('RGB')),axis=2);p=O/'proposals'/('r10_c15-'+label+'-final-actual-diff-mask.png');mask=Image.fromarray(di.astype('uint8')*255);mask.save(p);q.record(p,[base,dest],{'method':'exact binary RGB difference mask','outsideMaskChanges':0})
 val={'file':str(p),'sha256':q.sha(p),'bbox':mask.getbbox(),'changedPixels':int(di.sum()),'base':str(base),'baseSha256':q.sha(base),'outsideMaskChanges':0}
 manifest['selfMaskFromCornerBase' if label=='external' else 'allChangesFromRaw']=val
manifest['selfCandidate']={'file':str(dest),'sha256':q.sha(dest),'dimensions':[4096,4096],'globalRectXYWH':[57344,36864,4096,4096]}
manifest['lastLocalContourRepair']={'replacement':str(R/'repairs/internal/pile-lip-final-replacement.png'),'mask':str(R/'repairs/internal/pile-lip-final-mask.png'),'origin':[0,397],'source':str(R/'repairs/internal/pile-lip-generated.png'),'note':'Existing pile contour straightened between natural beam intersections, small brace underside step removed with real AI pixels. Exact binary mask and bounded field, no warp.'}
manifest['pixelConstruction']={'nativePatches':16,'nativePatchDimensions':[1254,1254],'core':[115,115,1139,1139],'finalDimensions':[4096,4096],'finalUpscaling':False,'AIImageCount':33,'approvedStyleActuallyAttached':str(Path('D:/work/image/designs/gameplay-ui/04-guild.png'))}
qa={'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'local tile and north/west native joint strips; global root integration pending','internalSeams':['x1024','x2048','x3072','y1024','y2048','y3072'],'nativeIntersections':9,'boundaryReturnPositions':[557,1139,2163,3072],'boundaryAxes':['north','west'],'findingsResolved':['deck groove and rail steps','left and right pile paint splits','sail spar highlight join','shared stone face and foliage','blue wall false subdivision','north protected-corner plank return','left-pile contour residual lip'],'nativeImageCounts':16,'native1254Verified':True,'outsideNeighborMasksChanged':0,'formalAccepted':False,'wholeCityComplete':False}
(R/'qa/final-review.json').write_text(json.dumps(qa,indent=2),encoding='utf8');manifest['qa']=str(R/'qa/final-review.json');manifest['preview']=str(R/'preview-final.png')
# Required three properties for generated sources.
records=[]
for png in sorted(R.rglob('*.png')):
 recpath=Path(str(png)+'.generation.json');assert recpath.exists(),png
 d=json.loads(recpath.read_text(encoding='utf-8-sig'));assert d['sha256']==q.sha(png),png
 if d.get('tool')=='image_gen.imagegen':
  assert d.get('actualModel') is None and d.get('actualQuality') is None
  refs=d.get('references',[]);assert any('04-guild.png' in v.get('file','') for v in refs),png
 if png.parent.name=='native':assert Image.open(png).size==(1254,1254)
 records.append({'file':str(png),'sha256':d['sha256'],'record':str(recpath),'generated':d.get('tool')=='image_gen.imagegen'})
(R/'generation-record-index.json').write_text(json.dumps({'records':records,'formalAccepted':False},indent=2),encoding='utf8');manifest['generationRecordIndex']=str(R/'generation-record-index.json')
(R/'handoff-final.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
for fn in ['progress.json','current-work.json']:
 p=R/fn;d=json.loads(p.read_text(encoding='utf8'));d.update(stage='ready_for_root_integration',updatedAt=qa['reviewedAt'],finalCandidate=str(dest),finalSha256=q.sha(dest),formalAccepted=0);p.write_text(json.dumps(d,indent=2),encoding='utf8')
print(json.dumps({'final':str(dest),'sha256':q.sha(dest),'records':len(records),'generated':sum(v['generated'] for v in records),'manifest':str(R/'handoff-final.json')},indent=2))
