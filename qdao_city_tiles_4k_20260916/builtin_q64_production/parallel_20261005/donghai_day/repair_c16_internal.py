"""Native-only localized c16 seam edits; never writes the assembled output."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json,shutil,sys
R=Path(__file__).resolve().parent
T=R/'r08_c16'
D=T/'repairs/internal-seams'
S=T/'output/r08_c16.png'
STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
EXPECTED='8c6871e74071f25997e4263bc21518f8b151a97c1b3408546e288f01867c3115'
SPECS={
'mast-1024':([397,397,1651,1651],[780,704,1250,1360]),
'mast-2048':([397,1421,1651,2675],[780,1720,1250,2360]),
'mast-3072':([397,2445,1651,3699],[780,2750,1250,3400]),
'hull-upper':([1421,2280,2675,3534],[1780,2580,2270,3370]),
'hull-lower':([1421,2842,2675,4096],[1780,3140,2270,4096]),
'water-upper':([2525,0,3779,1254],[2875,0,3425,1139]),
'water-lower':([2525,1024,3779,2278],[2875,1030,3425,1950]),
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def js(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prep(name):
 assert sha(S)==EXPECTED
 d=D/name;d.mkdir(parents=True,exist_ok=True);target=d/'input.png'
 assert not target.exists()
 box,roi=SPECS[name]
 with Image.open(S) as im:
  assert im.size==(4096,4096)
  im.crop(box).save(target)
 js(Path(str(target)+'.generation.json'),{'file':str(target),'sha256':sha(target),'source':{'file':str(S),'sha256':EXPECTED},'sourceRectXYXY':box,'rawSourceRGBSha256':hashlib.sha256(Image.open(target).convert('RGB').tobytes()).hexdigest(),'operation':'exact native crop, no resampling or color transform','pixels':[1254,1254]})
 if name.startswith('mast'):
  defect='The continuous vertical brown wooden mast/rib contains an artificial jagged HORIZONTAL color break near local y=627. It looks like a diagonal or sawtooth dark/light band across a single unbroken timber. Remove this false band by restoring continuous long vertical wood shading and grain. Keep the real mast edges, highlights, existing joints, rope and surrounding hull completely unchanged. Do not add a seam, ring, line, knot or decorative band in its place. The allowed change is only inside the existing mast/rib, around local x=380..855 and y=330..970; outer timber and background match the target.'
 elif name.startswith('hull'):
  defect='There is an artificial jagged VERTICAL color boundary around local x=520..750, crossing the continuous blue painted hull band and brown wooden hull. Remove this patch border by gently continuing the existing material tones from both sides. Preserve all legitimate horizontal/diagonal plank contours, blue bevel highlights, dark hull-contact strip, boat silhouette, net and waterline exactly. Do not add grain, more boards, scratches or shadows. The allowed change is only around this false material boundary; surrounding shape and exposure stay fixed.'
 else:
  defect='The target is blue open water'+(' with a small existing GOLDEN SPHERE/POST near the bottom that must remain unchanged' if name=='water-lower' else '')+'. An artificial jagged VERTICAL color/texture border around local x=600..720 divides otherwise calm blue water into two swatches. Smooth only this false border into a continuous quiet blue/cyan plane with extremely broad low-contrast soft color fields. Preserve the established blue/cyan colors and gradual variations. Do not add any new objects, boats, timber, ripple contours, lines, foam, wave blocks, caustic cells or fine grain. Do not erase the existing gold post if visible.'
 edge='The outer 200 pixels at left and right must match IMAGE 1 exactly. '
 if name not in ['hull-lower','water-upper']:edge+='The outer 200 pixels at top and bottom must also match IMAGE 1 exactly. '
 else:edge+='Where the false seam reaches a top/bottom canvas edge, continue the subtle repair through that edge without a cutoff; preserve all real silhouettes. '
 prompt='Use case: precise-object-edit. IMAGE 1 is an exact 1254x1254 native edit target. '+defect+' '+edge+'No overall recoloring, relighting, contrast change, sharpen/blur filter, crop, zoom or global repaint. All existing objects, perspective and locations remain exact. IMAGE 2 is the user-confirmed rounded clean hand-painted Q-style material reference only; do not copy its UI or objects. Return one opaque 1254x1254 corrected IMAGE 1, no resizing. The sole objective is to make the identified artificial material stitch disappear while everything else remains unchanged. Highest available finish.'
 (d/'prompt.txt').write_text(prompt,encoding='utf-8')
 refs=[{'file':str(target),'sha256':sha(target),'role':'exact native target; only localized material stitch may change'},{'file':str(STYLE),'sha256':sha(STYLE),'role':'confirmed style and materials only'}]
 js(d/'references.json',refs)
 js(d/'integration-plan.json',{'baselineSha256':EXPECTED,'sourceRectXYXY':box,'suggestedTargetRectXYXY':roi,'minimumAllowedTargetX':700,'nativePixelsOnly':True,'finalArtUpscaled':False,'assembledOutputWriter':'close_joint14','status':'suggested ROI; actual insertions need pixel-scale QA'})
 print(json.dumps({'name':name,'prompt':prompt,'references':[x['file'] for x in refs]}))
def record(name,src):
 d=D/name;out=d/'edited-native.png';src=Path(src)
 assert not out.exists()
 with Image.open(src) as im:assert im.size==(1254,1254)
 shutil.copyfile(src,out);refs=load(d/'references.json');meta=load(Path(str(d/'input.png')+'.generation.json'))
 js(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':load(Path('D:/work/image/config/image-generation.json')),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[x['file'] for x in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed tool exposes no model or quality selector or actual metadata.','evidence':{'toolResultSourcePath':str(src),'toolResultSha256':sha(src)},'prompt':str(d/'prompt.txt'),'promptSha256':sha(d/'prompt.txt'),'references':refs,'resizedAfterGeneration':False,'finalArtUpscaled':False,'baselineCandidate':meta['source'],'sourceRectXYXY':SPECS[name][0],'sourceRawRGBSha256':meta['rawSourceRGBSha256'],'formalAccepted':False})
 print(json.dumps({'file':str(out),'sha256':sha(out)}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prep(sys.argv[2])
 elif sys.argv[1]=='record':record(sys.argv[2],sys.argv[3])

