"""Native-only mechanical candidate assembly; no artwork resizing or QA pass implied."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,importlib.util,json
import numpy as np
P=Path(__file__).resolve().parent
R=P.parents[3]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
helper=P.parents[1]/'tianyong_festival/r09_c09/assemble_builtin.py'
spec=importlib.util.spec_from_file_location('existing_native_assembly',helper);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.HELPERS=R/'tianyong_festival_hd_20260910/seam_helpers.py'
seam=m.load_seam_helper()
plan=load(P/'plan.json');assert len(plan['patches'])==16
assert not (P/'output/r09_c10.candidate.png').exists(),'Never overwrite an existing candidate'
rows=[];entries=[];metrics=[]
for row in range(4):
 sources=[]
 for col in range(4):
  patch=next(x for x in plan['patches'] if x['row']==row and x['column']==col)
  f=P/patch['outputFile'];recfile=f.with_suffix('.record.json');rec=load(recfile)
  assert sha(f)==rec['nativeSha256']==rec['toolOutputSha256']==sha(rec['toolOutputPath'])
  assert sha(rec['promptFile'])==rec['promptSha256']
  assert rec['backendModelVerified'] is False and rec['actualModel'] is None
  assert rec['resampled'] is False and rec['finalArtUpscaled'] is False
  assert all(sha(r['path'])==r['sha256'] for r in rec['submittedImages'])
  assert [x['path'] for x in rec['submittedImages']]==patch['submittedImages']
  im=Image.open(f);im.load();assert im.size==(1254,1254);assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
  sources.append(np.array(im.convert('RGB')))
  entries.append({'id':patch['id'],'file':str(f),'sha256':sha(f),'pixels':list(im.size),'bytes':f.stat().st_size,'receipt':str(recfile),'receiptSha256':sha(recfile),'prompt':rec['promptFile'],'promptSha256':rec['promptSha256'],'toolSource':rec['toolOutputPath'],'exactToolBytesPreserved':True})
 strip=sources[0]
 for col in range(1,4):
  strip,metric=m.append_patch(strip,sources[col],seam,f'row{row+1}_col{col}_col{col+1}');metrics.append(metric)
 assert strip.shape==(1254,4326,3);rows.append(strip)
combined=rows[0].transpose(1,0,2)
for row in range(1,4):
 combined,metric=m.append_patch(combined,rows[row].transpose(1,0,2),seam,f'row{row}_row{row+1}');metrics.append(metric)
extended=Image.fromarray(combined.transpose(1,0,2));assert extended.size==(4326,4326)
tile=extended.crop((115,115,4211,4211));assert tile.size==(4096,4096)
extended.save(P/'output/extended-context.png');tile.save(P/'output/r09_c10.candidate.png')
tile.resize((1024,1024),Image.Resampling.LANCZOS).save(P/'qa/overview-preview-only.jpg',quality=96)
qa=[]
def saveqa(im,name,parts):
 f=P/'qa'/name;im.save(f);qa.append({'file':str(f),'sha256':sha(f),'pixels':list(im.size),'resampled':False,'parts':parts})
for axis in ('vertical','horizontal'):
 for index in range(1,4):
  out=Image.new('RGB',(920,1024) if axis=='vertical' else (1024,920));parts=[]
  for n in range(4):
   c=index*1024
   box=(c-115,n*1024,c+115,(n+1)*1024) if axis=='vertical' else (n*1024,c-115,(n+1)*1024,c+115)
   xy=(n*230,0) if axis=='vertical' else (0,n*230)
   out.paste(tile.crop(box),xy);parts.append({'tileBoxLTRB':box,'sheetPasteXY':xy})
  saveqa(out,f'internal-{axis}-{index}-100pct.png',parts)
out=Image.new('RGB',(690,690));parts=[]
for y in range(1,4):
 for x in range(1,4):
  box=(x*1024-115,y*1024-115,x*1024+115,y*1024+115);xy=((x-1)*230,(y-1)*230);out.paste(tile.crop(box),xy);parts.append({'tileBoxLTRB':box,'sheetPasteXY':xy})
saveqa(out,'all-nine-internal-intersections-100pct.png',parts)
check=load(P/'qa/left-neighbor-check.json');left=Image.open(check['leftCandidateSource']).convert('RGB').crop((115,115,4211,4211))
bottom=Image.open(P.parents[1]/'tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5/r10_c10.png').convert('RGB')
out=Image.new('RGB',(920,1024));parts=[]
for n in range(4):
 im=Image.new('RGB',(230,1024));im.paste(left.crop((3981,n*1024,4096,(n+1)*1024)),(0,0));im.paste(tile.crop((0,n*1024,115,(n+1)*1024)),(115,0));out.paste(im,(n*230,0));parts.append({'tileRowInterval':[n*1024,(n+1)*1024],'boundarySheetX':n*230+115})
saveqa(out,'external-left-r09_c09-100pct.png',parts)
out=Image.new('RGB',(1024,920));parts=[]
for n in range(4):
 im=Image.new('RGB',(1024,230));im.paste(tile.crop((n*1024,3981,(n+1)*1024,4096)),(0,0));im.paste(bottom.crop((n*1024,0,(n+1)*1024,115)),(0,115));out.paste(im,(0,n*230));parts.append({'tileColumnInterval':[n*1024,(n+1)*1024],'boundarySheetY':n*230+115})
saveqa(out,'external-bottom-r10_c10-100pct.png',parts)
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'candidate_pending_visual_review_not_delivery','tile':'r09_c10','cityAppearance':'tianyong_festival','pixels':[4096,4096],'globalPixelRectXYWH':[36864,32768,4096,4096],'worldRect':plan['tile']['worldRect'],'planSha256':sha(P/'plan.json'),'assemblyScriptSha256':sha(__file__),'reusedAssemblyHelper':{'path':str(helper),'sha256':sha(helper)},'seamHelper':{'path':str(m.HELPERS),'sha256':sha(m.HELPERS)},'sources':entries,'nativeSourcesCount':16,'nativeSourcePixels':[1254,1254],'referenceImagesAreNotDeliverySources':True,'modelRequested':plan['requestedModel'],'qualityRequested':plan['requestedQuality'],'actualModel':None,'actualQuality':None,'backendModelVerified':False,'composition':{'method':'Existing minimum error seam, row strips then vertical joins','overlapPixels':230,'featherRadiusPixels':2,'resampleSources':False,'globalBlur':False,'guidePixelsUsedInOutput':False,'upscaled':False,'outerCropPixels':115},'metrics':metrics,'output':{'path':str(P/'output/r09_c10.candidate.png'),'sha256':sha(P/'output/r09_c10.candidate.png')},'extendedContext':{'path':str(P/'output/extended-context.png'),'sha256':sha(P/'output/extended-context.png')},'qa':qa,'accepted':False,'runtimePublished':False,'externalBoundaryStatus':'left_and_bottom_pending_joint_repair_and_review','fullCityStatus':'incomplete'}
(P/'output/assembly.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'candidateSha256':record['output']['sha256'],'nativeSources':len(entries),'qaContactSheets':len(qa),'status':record['status']}))
