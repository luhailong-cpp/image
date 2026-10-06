from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib,shutil
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf8')
def info(p):
 im=Image.open(p);return {'file':str(p),'sha256':sha(p),'pixels':list(im.size),'mode':im.mode,'bytes':p.stat().st_size}
out=Path('C:/Users/luyua/.codex/generated_images/01a1117d-169b-76c0-a92c-248983c1a1b7/exec-57ade4fe-169c-4de6-bd6e-8f790679a45b.png')
native=B/'native/northwest-cap1254.png';shutil.copy2(out,native)
target=B/'inputs/northwest1254.png'
a=np.array(Image.open(target).convert('RGB'));g=np.array(Image.open(native).convert('RGB'))
assert a.shape==g.shape==(1254,1254,3)
r,gr,bl=[a[:,:,i].astype('int16') for i in range(3)]
env=np.zeros(a.shape[:2],bool);env[0:72,495:575]=True
surface=env&(r>gr+30)&(r>bl+45)&(gr>bl+12)
alpha=surface.astype('uint8')*255
mix=a.copy();mix[surface]=g[surface]
Image.fromarray(alpha).save(B/'masks/northwest-alpha1254.png')
Image.fromarray(mix).save(B/'candidate/northwest-composite1254.png')
Image.fromarray(a).crop((475,0,603,128)).save(B/'qa/north-cap-before128.png')
Image.fromarray(mix).crop((475,0,603,128)).save(B/'qa/north-cap-after128.png')
write(B/'native/northwest-cap1254.png.generation.json',{**info(native),'generatedAt':datetime.fromtimestamp(out.stat().st_mtime,timezone.utc).isoformat(),'actualNativeWidth':1254,'actualNativeHeight':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads((B/'config-snapshot.json').read_text()),'submittedParameters':{'model':None,'quality':None,'referenced_image_paths':[str(target),'D:/work/image/designs/gameplay-ui/04-guild.png'],'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露／无可核实元数据','evidence':{'receipt':str(B/'northwest-cap.receipt.json'),'receiptSha256':sha(B/'northwest-cap.receipt.json'),'originalOutputPath':str(out),'originalOutputSha256':sha(out)},'prompt':str(B/'northwest-cap.prompt.txt'),'promptSha256':sha(B/'northwest-cap.prompt.txt'),'references':[{'file':str(target),'sha256':sha(target),'role':'Actually viewed native edit target from exact day extended [0,0,1254,1254]'}, {'file':'D:/work/image/designs/gameplay-ui/04-guild.png','sha256':sha('D:/work/image/designs/gameplay-ui/04-guild.png'),'role':'Actually viewed and attached primary approved style reference'}]})
base=np.array(Image.open(B/'shared-geometry/day/extended4326.png').convert('RGB'));result=base.copy();allmask=np.zeros(base.shape[:2],np.uint8)
south=np.array(Image.open(B/'candidate/southwest-composite1254.png').convert('RGB'));southmask=np.array(Image.open(B/'masks/southwest-alpha1254.png'))
x,y=815,2915
region=result[y:y+1254,x:x+1254];region[southmask>0]=south[southmask>0];allmask[y:y+1254,x:x+1254]=southmask
result[:1254,:1254][surface]=mix[surface];allmask[:1254,:1254][surface]=255
assert np.array_equal(result[allmask==0],base[allmask==0])
core=result[115:4211,115:4211]
sel=B/'selected';sel.mkdir(exist_ok=True)
Image.fromarray(result).save(sel/'extended4326.png');Image.fromarray(core).save(sel/'core4096.png');Image.fromarray(core).resize((1254,1254),Image.Resampling.LANCZOS).save(sel/'preview1254.png');Image.fromarray(allmask).save(sel/'surface-mask4326.png')
assert np.array_equal(np.array(Image.open(sel/'extended4326.png'))[115:4211,115:4211],np.array(Image.open(sel/'core4096.png')))
assert np.array_equal(core[:2680],np.array(Image.open(B/'shared-geometry/day/core4096.png'))[:2680])
north=np.array(Image.open(B/'shared-geometry/north-spring/core4096.png').convert('RGB'))
qa=[]
for i in range(4):
 xx=i*1024;join=np.concatenate((north[-128:,xx:xx+1024],core[:128,xx:xx+1024]),axis=0)
 p=B/f'qa/north-commonedge-{i+1}.png';Image.fromarray(join).save(p);qa.append({**info(p),'scope':'north last128 rows + current core first128 rows','xRange':[xx,xx+1024],'nativeScale':True})
for label,xx in [('northwest',0),('northeast',3840)]:
 join=np.concatenate((north[-256:,xx:xx+256],core[:256,xx:xx+256]),axis=0)
 p=B/f'qa/{label}-corner.png';Image.fromarray(join).save(p);qa.append({**info(p),'scope':'north last256 rows + current first256 rows','xRange':[xx,xx+256],'nativeScale':True})
for label,box in [('southwest-corner',(0,3840,256,4096)),('southeast-corner',(3840,3840,4096,4096))]:
 p=B/f'qa/{label}.png';Image.fromarray(core).crop(box).save(p);qa.append({**info(p),'scope':'own tile corner; adjacent tiles unverified','coreBox':box,'nativeScale':True})
for i,box in enumerate([(200,760,700,1170),(880,425,1100,745),(450,1000,540,1085)],1):
 p=B/f'qa/south-cap-detail{i}.png';Image.fromarray(south).crop(box).save(p);qa.append({**info(p),'scope':'southwest edited native crop','nativeCropBox':box,'nativeScale':True})
write(B/'qa/exported-scopes.json',qa)
write(B/'processing.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'base':info(B/'shared-geometry/day/extended4326.png'),'baseCore':info(B/'shared-geometry/day/core4096.png'),'sourceReuse':'Exact qualified shared day geometry. Not generated anew for Spring. No global recolor.','nativeEdits':[{'id':'southwest-cap','native':info(B/'native/southwest-cap1254.png'),'record':str(B/'native/southwest-cap1254.png.generation.json'),'targetCropCoreLTRB':[700,2800,1954,4054],'targetCropExtendedLTRB':[815,2915,2069,4169],'mask':info(B/'masks/southwest-alpha1254.png'),'recipe':str(B/'masks/southwest-mask-recipe.json'),'paste':'native1254 same pixel coordinates inside exact original cap mask; already composited pixels, no second alpha'}, {'id':'northwest-cap','native':info(native),'record':str(B/'native/northwest-cap1254.png.generation.json'),'targetCropExtendedLTRB':[0,0,1254,1254],'mask':info(B/'masks/northwest-alpha1254.png'),'predicate':'x495:575,y0:72 AND R>G+30 AND R>B+45 AND G>B+12','maskPixels':int(surface.sum()),'coreChanged':False,'paste':'Native same coordinates only source-orange cap pixels. No neighbor geometry copied.'}],'assemblyResampling':None,'warp':None,'translation':[0,0],'upscale':False,'previewOnlyResampling':'LANCZOS downsample 4096 to1254','coreInExtendedLTRB':[115,115,4211,4211],'combinedMask':info(sel/'surface-mask4326.png'),'outsideMaskByteEqual':True,'changedPixels':int(np.any(result!=base,axis=2).sum()),'maskPixels':int(np.count_nonzero(allmask)),'coreChangedPixels':int(np.any(core!=np.array(Image.open(B/'shared-geometry/day/core4096.png')),axis=2).sum()),'coreMatchesExtended':True,'allSavedPngRereadExact':np.array_equal(result,np.array(Image.open(sel/'extended4326.png'))),'geometryPreservedByUnchangedOutsideSourceEntityMasks':True,'protectedSurfaces':'white/gray stone, bridge, foliage, trunk, soil, water, paving, shadows outside original cap faces','formalAccepted':False,'clientValidated':False,'wholeCityComplete':False})
print(json.dumps({'northMaskPixels':int(surface.sum()),'outputs':[info(sel/n) for n in ['core4096.png','extended4326.png','preview1254.png']]}))
