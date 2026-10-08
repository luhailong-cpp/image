"""Native AI correction for two visible paving contour steps at c13 west-strip insertion."""
from pathlib import Path
import sys, json, shutil
import numpy as np
from PIL import Image
import assembly as n
import integrate_leaf02 as local
ROOT=Path(__file__).resolve().parent
R=ROOT/'r08_c13/repairs/right-insertion-stone-03'
STYLE=ROOT.parents[3]/'designs/gameplay-ui/04-guild.png'
TILE=ROOT/'tiles/r08_c13.png'
# Coordinates are local to c13, equivalent to pair x 4014..5268.
CROP=(-82,1950,1172,3204)
PAIR_CROP=(4014,1950,5268,3204)
RECT=(575,520,940,1135)
EXPECTED='169a05f863b8a45b4e9f815a82b1ecc1440b778b79e0ece7af87606888640240'
def ref(p):return {'file':str(p),'sha256':n.sha(p)}
def pair():return np.concatenate([local.rgb(ROOT/f'tiles/r08_c{i}.png',(4096,4096)) for i in (12,13)],axis=1)
def prepare():
 n.require(n.sha(TILE)==EXPECTED,'Unexpected input c13')
 R.mkdir(parents=True,exist_ok=True)
 p=pair(); x,y,xx,yy=PAIR_CROP
 n.save_image(R/'input.png',Image.fromarray(p[y:yy,x:xx]))
 refs=[dict(ref(R/'input.png'),role='exact current native crop; edit target'),dict(ref(STYLE),role='confirmed rendering style only, no UI')]
 n.save_json(R/'references.json',refs)
 n.save_json(R/'input.png.generation.json',dict(ref(R/'input.png'),operation='native crop without resampling',pairRectXYXY=list(PAIR_CROP),derivedFrom=[ref(ROOT/f'tiles/r08_c{i}.png') for i in (12,13)]))
 old=Path(str(TILE)+'.generation.json'); shutil.copyfile(old,R/'previous-current-c13.generation.json')
 n.save_json(R/'provenance.json',{'baseline':ref(TILE),'previousRecord':ref(R/'previous-current-c13.generation.json'),'previousManifest':ref(ROOT/'tiles/west-integration-r08_c13-manifest.json')})
 prompt='''Use case: precise-object-edit. Image 1 is the exact native crop of current Daoist chibi fishing-village paving. Repair ONLY the two small abrupt gray-to-brown rectangular shading switches on diagonal paving grout lines in the central-right area, approximately x=675,y=685 and x=690,y=1010. Blend the gray LEFT grout and beige-brown RIGHT grout through short gradual painterly color transitions around these two x=690 cut points. Do NOT recolor either whole grout line. At x less than 580 and x greater than 935 keep every pixel as exactly unchanged as possible; only edit the two small color junctions near the center-right. Preserve existing line geometry and overall shading exactly. Preserve all existing paving stone shapes, scale, perspective, warm ivory color, gray grout and soft blue painted shading; preserve the entire composition and outer edges. Do not redesign the stone pattern or introduce anything. Image 2 is the user-confirmed rendering style only, never its UI content. Keep clean rounded hand-painted materials. No extra objects, text, cracks, blur, sharpening or global exposure change. Opaque square native 1254 image; return only the locally corrected image 1.'''
 (R/'prompt.txt').write_text(prompt,encoding='utf-8')
 print(json.dumps({'prompt':prompt,'references':[r['file'] for r in refs]}))
def record(src):
 src=Path(src); dest=R/'edited-native.png';n.require(not dest.exists(),'Already recorded')
 shutil.copyfile(src,dest);local.rgb(dest,(1254,1254))
 refs=n.load_json(R/'references.json');n.save_json(Path(str(dest)+'.generation.json'),dict(ref(dest),width=1254,height=1254,format='PNG',generatedAt=n.utc_now(),timestampMeaning='locally observed completion',tool='image_gen.imagegen',route='builtin',configSnapshot=n.load_json(ROOT.parents[3]/'config/image-generation.json'),submittedParameters={'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[r['file'] for r in refs]},actualModel=None,actualQuality=None,unverifiedReason='Host managed; no selector or returned evidence.',evidence={'toolResultSourcePath':str(src),'toolResultSha256':n.sha(src)},references=refs,prompt=str(R/'prompt.txt'),promptSha256=n.sha(R/'prompt.txt'),resizedAfterGeneration=False,finalArtUpscaled=False))
 print(json.dumps(ref(dest)))
def integrate():
 n.require(n.sha(TILE)==EXPECTED,'Concurrent c13 change')
 p=pair(); source=local.rgb(R/'input.png',(1254,1254));edit=local.rgb(R/'edited-native.png',(1254,1254));x,y,xx,yy=PAIR_CROP
 n.require(np.array_equal(p[y:yy,x:xx],source),'Input stale')
 a,b,c,d=RECT; old=source[b:d,a:c];new=edit[b:d,a:c]
 alpha=np.full(old.shape[:2],255,dtype=np.uint8); masks=[];local.MASKS=R/'masks';local.OVERLAP=32
 for name,sl,t,inv in [('left',(slice(None),slice(0,32)),False,False),('right',(slice(None),slice(-32,None)),False,True),('top',(slice(0,32),slice(None)),True,False),('bottom',(slice(-32,None),slice(None)),True,True)]:
  left,right=(new[sl],old[sl]) if inv else (old[sl],new[sl]);part,info=local.save_mask(name,left,right,t,inv);alpha[sl]=np.minimum(alpha[sl],part);masks.append(info)
 n.require(all(np.all(z==0) for z in [alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]]),'Mask outside nonzero')
 result=p.copy(); result[y+b:y+d,x+a:x+c]=n.blend(old,new,alpha)
 ex=np.ones(p.shape[:2],bool);ex[y+b:y+d,x+a:x+c]=False;n.require(np.array_equal(p[ex],result[ex]),'Exterior changed')
 n.require(np.array_equal(result[:,:4096],p[:,:4096]),'c12 changed')
 n.require(n.sha(TILE)==EXPECTED,'Concurrent write');out=n.save_image(TILE,Image.fromarray(result[:,4096:]));n.require(np.array_equal(local.rgb(TILE,(4096,4096)),result[:,4096:]),'Saved pixel mismatch')
 n.save_image(R/'masks/combined.png',Image.fromarray(alpha))
 qa=n.save_image(R/'qa/context.png',Image.fromarray(result[2400:3150,4350:5030]))
 manifest=R/'integration-manifest.json';n.save_json(manifest,{'createdAt':n.utc_now(),'issue':'C13-RIGHT-INSERTION-STONE-03','baseline':n.load_json(R/'provenance.json'),'generatedEdit':ref(R/'edited-native.png'),'generationRecord':ref(R/'edited-native.png.generation.json'),'output':out,'pairRepairRectXYXY':[x+a,y+b,x+c,y+d],'localC13RepairRectXYXY':[x+a-4096,y+b,x+c-4096,y+d],'outsideRepairExactlyIdentical':True,'outsideChangedPixels':0,'c12ExactlyUnchanged':True,'masks':masks,'transitionPartialPixels':2,'noUpscaling':True,'colorCorrection':False,'registration':False,'qa':qa,'formalAccepted':False,'wholeCityComplete':False})
 n.save_json(Path(str(TILE)+'.generation.json'),dict(out,tile='r08_c13',operation='native AI correction of two small grout contour steps',integrationManifest=ref(manifest),actualModel=None,actualQuality=None,formalAccepted=False,noUpscaling=True))
 print(json.dumps({'output':out,'qa':qa,'outsideChangedPixels':0}))
if __name__=='__main__':
 {'prepare':prepare,'record':lambda:record(sys.argv[2]),'integrate':integrate}[sys.argv[1]]()



