"""Native north stone joint repairs only; canonical r09/r10 outputs remain untouched."""
from pathlib import Path
import hashlib,json,sys,shutil
from datetime import datetime,timezone
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent;D=R/'r10_c15/repairs/north-joint'
N=R/'r09_c15/output/r09_c15.png';NE=R/'r09_c15/output/extended-context.png';B=R/'r10_c15/output/r10_c15.png';STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
NS='33abbb4345add5b42b8020ce1c6dd4b40a44d4fdb7dd96fc3b37220006c5c6ff';NES='a1e579822cdc65b66be7549715388b7adb6b9feab17451c851a00fb5a8bd074f';BS='0b32765cd251e3fb0adb873d202035d4f66aed0d60ebef663f442df2ca8c0fa3'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p):return {'file':str(p),'sha256':sha(p)}
def prepare(name):
 x={'n2':896,'n3':2048}[name];f=D/name;f.mkdir(parents=True,exist_ok=True);assert not (f/'edited-native.png').exists()
 assert sha(N)==NS and sha(NE)==NES and sha(B)==BS
 north=Image.open(N).convert('RGB');base=Image.open(B).convert('RGB');ext=Image.open(NE).convert('RGB')
 before=Image.new('RGB',(1254,1254));before.paste(north.crop((x,3469,x+1254,4096)),(0,0));before.paste(base.crop((x,0,x+1254,627)),(0,627));before.save(f/'before-joint.png')
 guided=before.copy();guided.paste(ext.crop((x+115,4211,x+1369,4326)),(0,627));guided.save(f/'fixed-context.png')
 arr=np.array(guided.convert('RGBA'));arr[742:1147]=0;Image.fromarray(arr).save(f/'input.png')
 save(f/'input.png.generation.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'file':str(f/'input.png'),'sha256':sha(f/'input.png'),'sourceRectXYXY':[x,-627,x+1254,627],'rawBeforeJointRGBSha256':hashlib.sha256(np.array(before).tobytes()).hexdigest(),'sources':[ref(N),ref(NE),ref(B)],'operation':'Exact north627/core627 joint crop; true north south115 halo replaces core0..115 as geometry stencil; transparent gap core115..520','transparentGapLocalY':[742,1147],'immutableNorthLocalY':[0,627],'authoritativeNorthHaloLocalY':[627,742],'lowerCurrentAnchorLocalY':[1147,1254],'resized':False})
 detail={'n2':'This crop contains the LEFT CORNER of the existing pale warm stone wall/rim and its cool shaded side faces. Keep exactly the existing stone-block count, corner silhouette, existing wall thickness, and dark grout layout from the visible anchors. Continue the warm capstone bevel from the fixed upper stencil downward into the cool gray shaded face without any horizontal slab cutoff. The wall stone is one material under light and shade, not a new row or extra ledge. Preserve the floor, true cast shadow and the small visible wood post context.', 'n3':'This crop contains the LONG pale warm capstone row, cool gray stone faces beneath it, and a blue-gray upright stone plus existing timber at the right. Continue the exact capstone widths and grout endpoints visible in the fixed upper stencil into the existing lower faces. No extra narrow row, new slab seam, or redesigned right blue-gray block; retain the same existing blocks and their dimensions. Preserve the right timber outline and its real broad cast shadow.'}[name]
 prompt='Use case: precise-object-edit / missing-region continuation. IMAGE1 is the native1254 square edit target. It has one transparent horizontal gap local y742..1146 (only lower tile). The opaque top y0..741 is the TRUE immutable completed north tile plus its actual native115px south halo: every outline and color there is authoritative. The opaque bottom y1147..1254 is the actual current lower-tile material anchor. IMAGE2 shows that exact fixed context as an identity guide; its y742..1146 is lower-tile material context only, and its existing mismatch must not be copied. IMAGE3 is approved bright clean rounded Q-style reference only. Fill the gap by extending the fixed upper stone geometry downward and connecting naturally to the bottom anchor. '+detail+' Keep camera, crop, scale, object count, block count, true shadows and existing edge endpoints. Keep warm sunlit cap planes, softly cool side planes and restrained hand-painted stone facets. No new objects, fine texture noise, cracks, lettering, borders, extra decorative patterns, blur, or water grids. Preserve all opaque context pixel positions. Return opaque1254x1254 without resizing.'
 (f/'prompt.txt').write_text(prompt,encoding='utf-8');save(f/'references.json',[{**ref(p),'role':role} for p,role in [(f/'input.png','native target with actual immutable north and halo geometry'),(f/'fixed-context.png','actual context identity and lower material'),(STYLE,'approved Q style')]])
 print(json.dumps({'name':name,'prompt':str(f/'prompt.txt'),'refs':str(f/'references.json')}))
def record(name,source):
 f=D/name;src=Path(source);p=f/'edited-native.png';assert not p.exists()
 with Image.open(src) as im:im.load();assert im.size==(1254,1254)
 refs=read(f/'references.json')
 for v in refs:assert sha(v['file'])==v['sha256']
 shutil.copyfile(src,p);meta=read(f/'input.png.generation.json')
 rec={**ref(p),'width':1254,'height':1254,'format':'PNG','generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(R.parents[3]/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[v['file'] for v in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed built-in path; model/quality parameters and returned version metadata not disclosed.','evidence':{'toolResultSourcePath':str(src),'toolResultSha256':sha(src)},'prompt':str(f/'prompt.txt'),'promptSha256':sha(f/'prompt.txt'),'references':refs,'inputDerivationRecord':ref(f/'input.png.generation.json'),'sourceRectXYXY':meta['sourceRectXYXY'],'resizedAfterGeneration':False,'finalArtUpscaled':False,'intendedDestination':'r10_c15 core y0..627 only, actual north source never changed; fill16 integrates','generatedContextPixelIdentityNotAssumed':True,'integrationVisualReviewRequired':True}
 save(str(p)+'.generation.json',rec);assert sha(N)==NS and sha(NE)==NES and sha(B)==BS
 print(json.dumps(ref(p)))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(sys.argv[2])
 elif sys.argv[1]=='record':record(sys.argv[2],sys.argv[3])
