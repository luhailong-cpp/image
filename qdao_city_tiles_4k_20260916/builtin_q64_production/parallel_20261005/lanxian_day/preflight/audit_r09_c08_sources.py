from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image

root=Path(__file__).resolve().parent.parent
assert root.name=='lanxian_day' and root.parent.name=='parallel_20261005'
prod=root.parent.parent; project=prod.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def meta(p):
 p=Path(p);d={'file':str(p),'exists':p.is_file()}
 if p.is_file():
  d.update(sha256=sha(p),bytes=p.stat().st_size)
  if p.suffix.lower()=='.png':
   with Image.open(p) as im:d.update(pixels=list(im.size),mode=im.mode)
 return d
handoff=read(root/'handoff.json');queue=read(root/'production-queue.json');progress=read(root/'progress.json')
baseline=next(x for x in handoff['baselineCandidates'] if x['tile']=='r08_c08')
core=Path(baseline['file']);coremeta=meta(core);assert coremeta['sha256']==baseline['sha256'] and coremeta['pixels']==[4096,4096]
assembly=prod/'lanxian_day/triple_r08_c06_c08/output_v2/assembly.json';legacy=next(x for x in read(assembly)['candidates'] if x['tile']=='r08_c08')
ext=core.with_name('r08_c08.extended.png');extmeta=meta(ext);extmeta.update(historicalExpectedSha256=legacy['extendedContextSha256'],historicalExpectedPixels=[4326,4326],historicalPath=legacy['extendedContext'])
oldbase=prod/'lanxian_day/r08_c08';oldnative=[]
for col in range(1,5):
 rp=oldbase/f'native/r04_c{col:02d}.record.json';r=read(rp)
 oldnative.append({'cell':r['id'],'record':meta(rp),'native':meta(oldbase/f'native/r04_c{col:02d}.png'),'hostSource':meta(r['sourceOutputPath']),'expectedSha256':r['sourceOutputSha256']})
deletion=project/'cleanup-current-assets/deleted-files.jsonl';deleted=[{'lineOneBased':i,'entry':json.loads(line)} for i,line in enumerate(deletion.read_text(encoding='utf-8-sig').splitlines(),1) if 'lanxian_day' in line and 'output_v2' in line and 'r08_c08.extended.png' in line]
c07=prod/'lanxian_day/triple_r08_c06_c08/output_v2/r08_c07.png';c09=root/'r08_c09/selected/core4096.png';c09ext=root/'r08_c09/selected/extended4326.png'
with Image.open(core) as im:im8=im.convert('RGB')
with Image.open(c07) as im:im7=im.convert('RGB')
with Image.open(c09) as im:im9=im.convert('RGB')
with Image.open(c09ext) as im:ex9=im.convert('RGB')
assert ex9.crop((115,115,4211,4211)).tobytes()==im9.tobytes()
parts=[(c07,im7,(3981,3981,4096,4096),[0,0,115,115]),(core,im8,(0,3981,4096,4096),[115,0,4211,115]),(c09,im9,(0,3981,115,4096),[4211,0,4326,115])]
first115=[]
for p,im,box,target in parts:
 crop=im.crop(box);first115.append({'source':meta(p),'sourceBoxXYXY':list(box),'destinationBoxInNorthBandXYXY':target,'pixels':list(crop.size),'rawRgbPixelSha256':hashlib.sha256(crop.tobytes()).hexdigest(),'sourceResampling':'none; legal integer crop/paste','written':False})
context_overlap_a=np.array(im8.crop((3981,3981,4096,4096)),dtype=np.int16);context_overlap_b=np.array(ex9.crop((0,4096,115,4211)),dtype=np.int16);diff=context_overlap_a-context_overlap_b
wrongbase=prod/'resume_single_city_20260921/next_tile_r08_c08';wrongplan=read(wrongbase/'plan.json');wrong=[]
for col in range(1,5):
 v=3 if col==4 else 2;p=wrongbase/f'native/r04_c{col:02d}.v{v}.png';rpath=p.with_suffix('.generation.json');r=read(rpath)
 d=meta(p);d.update(generationRecord=meta(rpath),generationHashMatches=sha(p)==r['sha256']);wrong.append(d)
entry_index=next(i for i,x in enumerate(queue['tiles']) if x['id']=='r09_c08');entry=queue['tiles'][entry_index]
actualnext=list((root/'r09_c09/native').glob('*.png'))
report={
 'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'auditor':'westward_row03','tile':'r09_c08','scope':'Read-only source and coordinate audit; no image was generated, modified or reconstructed.',
 'controlFiles':{name:meta(root/name) for name in ('handoff.json','production-queue.json','progress.json','current-work.json')},
 'handoff':{'readyForProduction':handoff['readyForProduction'],'baselineCurrent':handoff['baselineCurrent'],'northTile':'r08_c08','northBaselineHashMatches':True,'baselineFormalAccepted':False},
 'queue':{'indexZeroBased':entry_index,'positionOneBased':entry_index+1,'entry':entry,'provisionalQueue':True,'queueNote':queue.get('note'),'planSha256MatchesHandoff':queue['planSha256']==handoff['plan']['sha256'],'geometryVerified':entry['pixelRectXYWH']==[28672,32768,4096,4096]},
 'progressSnapshot':{'updatedAtUtc':progress['updatedAtUtc'],'currentTile':progress['currentTile'],'phase':progress['currentPhase'],'currentTileNativeCountRecorded':progress['currentTileNativeCount'],'r09c09NativePngActualCountAtAudit':len(actualnext),'r09c09SelectedCoreExists':(root/'r09_c09/selected/core4096.png').exists(),'warning':'Progress counters are stale relative to live r09_c09 files; this audit does not edit shared progress.'},
 'northCore':coremeta,'historicalMatchingExtended':extmeta,'historicalAssembly':meta(assembly),
 'coreEqualsExtendedCenterCrop':{'verified':False,'result':None,'reason':'Historical expected extended PNG is missing. Core is hash-bound to assembly, but current pixel identity cannot be retested against absent data.'},
 'deletionEvidence':{'file':meta(deletion),'matchingDeletedEntries':deleted,'receipt':meta(project/'cleanup-current-assets/deletion-receipt.json')},
 'originalBottomRowNativeSources':oldnative,
 'wrongAppearanceRejected':{'plan':meta(wrongbase/'plan.json'),'cityAppearance':wrongplan['cityAppearance'],'reason':'Directory name next_tile_r08_c08 is ambiguous; actual plan is tianyong_festival, not lanxian_day. Its native images cannot supply the north halo for this map.','images':wrong},
 'requiredNorthBand':{'pixels':[4326,230],'wholeCityRectXYXY':[28557,32653,32883,32883],'sourceIfExtendedPresent':[0,4096,4326,4326],'first115RowsMeaning':'Actual last115 rows inside row08 cores; native strict external north context.','second115RowsMeaning':'South halo beyond row08 core; future row09 area. Not derivable by stretching or repeating row08 edge.'},
 'legalFirst115RowsConstruction':{'available':True,'fullBandPixels':[4326,115],'parts':first115,'northCoreWinsAtSharedCorners':True,'needsNoUpscale':True,'imageWritten':False},
 'knownSouthHaloRightCorner':{'source':meta(c09ext),'sourceCore':meta(c09),'coreEqualsExtendedCenterCropVerified':True,'sourceBoxXYXY':[0,4211,230,4326],'destinationBoxInNorthBandXYXY':[4096,115,4326,230],'pixelMappingNoResampling':True,'notTheDeletedC08ExtendedVersion':True,'status':'Optional neighboring selected halo evidence only; not proof that whole c08 south halo exists.'},
 'cornerVersionDifference':{'comparison':'r08_c08 core [3981,3981,4096,4096] against r08_c09 selected extended [0,4096,115,4211]','differingPixels':int(np.any(diff!=0,axis=2).sum()),'maxAbsoluteChannelDifference':int(np.abs(diff).max()),'implication':'Use inherited c08 core for strict north pixels; do not overwrite it with neighboring c09 halo or claim both versions are identical.'},
 'missingNativeHalo':{'missingMainBandBoxXYXY':[0,115,4096,230],'pixels':[4096,115],'pixelCount':4096*115,'native230BandComplete':False,'full4326ExtendedAvailable':False,'duplicatingMirroringStretchingOrUpscalingCorePermitted':False},
 'currentPrepareNorthEastFrontier':{'script':meta(root/'tools/prepare_north_east_frontier.py'),'directlyUsable':False,'reasons':['Requires northExtended4326 and exact center crop to supplied core; matching northExtended is absent.','Requires expected tile name as a directory path component for ext; any legitimate new local adapter output must be identified as r08_c08.','East r09_c09 selected candidate is not yet available at this audit snapshot.'],'doNotFakeNativeExtended':True},
 'recommendedNextSteps':['Finish and qualify current r09_c09 east neighbor first.','Adapt the preparation path to accept a north core plus exact partial native band and a coverage mask. Use the three legal core crops for known first115 rows; keep absent south halo as explicitly guide-only layout/region pixels with zero native weight. Do not falsely label an all-native4326 image.','If retaining strict complete230 native overlap, generate the missing halo as new builtin native image(s) guided by the baseline; record it as new derived context and inspect its joins. This is a future action, not performed by this audit.','Record corner precedence and inspect both final native north/east seams before qualification.'],
 'visualEvidence':{'northCoreActuallyViewed':True,'viewMethod':'view_image whole4096 core displayed downsampled1600; used for source identification only, not native seam acceptance.'},
 'formalAccepted':False,'wholeCityComplete':False,'noNewImagesGenerated':True,'noSourcePngModified':True}
dest=root/'preflight/r09_c08-source-audit.json';assert not dest.exists();dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'audit':str(dest),'sha256':sha(dest),'northCore':coremeta,'coreCropDirectlyVerified':False,'requiredNativeBandComplete':False,'missingHalo':[4096,115],'queuePosition':entry_index+1,'r09c09NativeActualCount':len(actualnext),'cornerDelta':report['cornerVersionDifference']}))
