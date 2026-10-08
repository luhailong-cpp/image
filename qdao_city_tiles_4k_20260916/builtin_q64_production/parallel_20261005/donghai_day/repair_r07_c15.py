from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,shutil
from PIL import Image
R=Path(__file__).resolve().parent;T=R/'r07_c15';D=T/'repairs/native-seams'
BASE=T/'output/r07_c15.png';SOUTH=R/'r08_c15/output/r08_c15.png'
BASE_SHA='3d6784d05e08447095081e0a2c425a1d11b2f7c461a7ff1dd74d9efa7644ea13'
SOUTH_SHA='70ce623a54fb8419b951b7372a88e95db2c8b5ae9e04845c2af2c1fd18312585'
STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
STARTS=[0,1024,2048,2842]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def geometry(name):
    if name[0] in 'hs':
        i=int(name[1:])-1;x=STARTS[i];y=1421 if name[0]=='h' else 3469
        return [x,y,x+1254,y+1254]
    if name=='panel':return [0,2600,1254,3854]
    raise ValueError(name)
def prepare(name):
    F=D/name;F.mkdir(parents=True,exist_ok=True);box=geometry(name)
    assert sha(BASE)==BASE_SHA and sha(SOUTH)==SOUTH_SHA
    with Image.open(BASE) as im:canvas=im.convert('RGB')
    refs=[{'file':str(BASE),'sha256':BASE_SHA,'role':'frozen full native candidate; crop source'}]
    if name[0]=='s':
        pair=Image.new('RGB',(4096,8192));pair.paste(canvas,(0,0))
        with Image.open(SOUTH) as im:pair.paste(im.convert('RGB'),(0,4096))
        canvas=pair;refs.append({'file':str(SOUTH),'sha256':SOUTH_SHA,'role':'frozen mandatory south neighboring geometry; never modify this 4K source'})
    im=canvas.crop(box);raw=hashlib.sha256(im.tobytes()).hexdigest()
    if name[0] in 'hs' and int(name[1:])>1:
        previous=f'{name[0]}{int(name[1:])-1}';src=D/previous/'edited-native.png'
        assert src.is_file(),'Generate prior overlapping repair first'
        pr=read(str(src)+'.generation.json');assert sha(src)==pr['sha256']
        b=geometry(previous);width=b[2]-box[0]
        with Image.open(src) as p:im.paste(p.crop((1254-width,0,1254,1254)),(0,0))
        refs.append({'file':str(src),'sha256':sha(src),'role':'actual already-generated left repair overlap','sourceRectXYXY':[1254-width,0,1254,1254],'destinationXY':[0,0],'resized':False})
    im.save(F/'input.png')
    save(F/'input.png.generation.json',{'file':str(F/'input.png'),'sha256':sha(F/'input.png'),'operation':'native crop and optional exact neighboring repair overlap','sourceRectXYXY':box,'derivedFrom':refs,'rawUnmodifiedCropRGBSha256':raw,'resized':False})
    prompt='Use case: precise-object-edit. Edit IMAGE 1 only. This is a native-pixel crop of an existing bright clean rounded Q-style fishing-village game map. IMAGE 2 is the approved hand-painted material/style reference only, no UI. Preserve the exact original camera, crop, object silhouettes and pixel positions; no new object, wood joint, rope, decoration or water feature. Keep every real cast shadow and white/cyan piling-water contact highlight. '
    if name[0]=='h':
        prompt+='Repair the artificial horizontal patch-color break around local y627. Across that line, the same wooden pilings must have continuous warm vertical grain and continuous shading, without a dark upper rectangular section or a jagged horizontal cut. The adjoining blue water must be continuous quiet broad soft fields, without a scalloped horizontal paint boundary. Preserve real broad diagonal cast shadows under the pier. Make only the image-patch tonal join seamless; never move a piling, plank, ladder or water contact rim. '
    elif name[0]=='s':
        prompt+='The scene is wrongly cut by a horizontal collage seam at local y627. Reconstruct ONLY the upper half (y0..627) so it joins EXACTLY onto the completed lower-half scene. The entire LOWER HALF y627..1254 is mandatory existing neighboring art: keep it fixed. Any barrel, blue canopy, blue roof trim, plank or rope entering from below must continue naturally upward into the upper half in the same geometry and perspective. Remove the horizontal cut and disconnected upper remnants; where upper and lower structures disagree, LOWER HALF is the authoritative footprint. Keep the uppermost150 pixels as close as possible to their original geometry and smoothly connect through the intervening upper region. '
    else:
        prompt+='Repair only the jagged horizontal color break in the blue glass panel. Continue its upper diagonal pale blue reflective facets naturally through the whole panel, inside the existing wooden frame, with consistent blue hue. Keep all surrounding timber, water and shadows fixed. '
    prompt+='Keep all already-sharp left overlap context continuous; do not draw a boundary at its edge. Calm water elsewhere, no added caustic nets, ripple streaks, foam or fine grain. No global relighting or blur filter. Opaque native1254x1254, identical crop, no resizing, text or border.'
    if name[0]=='s':
        prompt='IMAGE 1 is a BROKEN COLLAGE that must become ONE CONTINUOUS SCENE. The straight horizontal cut through local y627 is an error. Repaint the upper-middle area y150..627 to remove that cut: continue the exact lower-half blue roof trim, cabin timber, blue canopy, rope or board lines upward into the upper scene. The entire bottom half y627..1254 is the finished neighboring art and its shapes, colors and positions must remain FIXED. If upper and lower object geometry conflicts, change the UPPER region to match the lower-half footprint; do not preserve disconnected upper fragments or duplicate objects. Preserve the topmost150 pixels and the already-repaired left overlap as the contextual anchors. Build one coherent isometric boat structure. Do not simply polish the broken collage: the straight cut and line discontinuities must visibly disappear. Image2 is the approved clean bright rounded Q-style hand-painted material only. Exact1254 square crop, no global relighting, unrelated objects, text, blur or border.'
    inputs=[{'file':str(F/'input.png'),'sha256':sha(F/'input.png'),'role':'native joint/seam crop edit target'},{'file':str(STYLE),'sha256':sha(STYLE),'role':'confirmed bright rounded hand-painted material style; no UI'}]
    (F/'prompt.txt').write_text(prompt,encoding='utf-8');save(F/'references.json',inputs)
    print(json.dumps({'name':name,'prompt':prompt,'references':[r['file'] for r in inputs]}))
def record(name,source):
    F=D/name;src=Path(source);dst=F/'edited-native.png';assert not dst.exists()
    with Image.open(src) as im:im.load();assert im.size==(1254,1254)
    shutil.copyfile(src,dst);refs=read(F/'references.json');prompt=F/'prompt.txt'
    save(str(dst)+'.generation.json',{'file':str(dst),'sha256':sha(dst),'width':1254,'height':1254,'format':'PNG','generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(R.parents[3]/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[r['file'] for r in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin interface has no model/quality selectors or returned version metadata.','evidence':{'toolResultSourcePath':str(src),'toolResultSha256':sha(src)},'prompt':str(prompt),'promptSha256':sha(prompt),'references':refs,'resizedAfterGeneration':False,'finalArtUpscaled':False,'sourceRectXYXY':geometry(name),'intendedDestination':'r07_c15 only; r08_c15 remains unchanged'})
    print(json.dumps({'file':str(dst),'sha256':sha(dst)}))
def retry_s1():
    F=D/'s1';A=F/'rejected-unchanged-seam';A.mkdir(exist_ok=True)
    rec=read(F/'edited-native.png.generation.json')
    shutil.copyfile(F/'prompt.txt',A/'prompt.txt');rec['originalPromptPath']=rec['prompt'];rec['prompt']=str(A/'prompt.txt')
    rec['rejection']='Actual view: horizontal collage boundary remains essentially unchanged; not usable.'
    save(A/'generation.json',rec)
    p='IMAGE 1 is a BROKEN COLLAGE that must become ONE CONTINUOUS SCENE. The perfectly straight horizontal cut at the exact middle y627 is an error, not a real object edge. Completely REPAINT the upper-middle portion to repair it. The bottom half contains the correct barrel, rope railing, blue boat side and brown cabin wall. Complete the barrel upward into a whole rounded elliptical top: paint over the conflicting upper deck boards where needed. Continue the thick cream rope and blue boat side upward to the left, joining the same lower-half objects with zero cut, jump, duplicated edge or horizontal stripe. Extend the vertical cabin wall naturally behind the barrel. KEEP the bottom half geometry exactly fixed, and preserve the topmost150 pixels as the distant contextual frame. You MAY change upper-half objects that conflict with the bottom half, because correcting this exact structural mismatch is the goal. Do not merely polish or copy the broken collage. One continuous isometric boat corner, rounded clean bright hand-painted Q-style as IMAGE 2, warm timber, blue-painted trim and cream rope, exact same camera and1254 square crop. Do not introduce new unrelated objects, text, people, blur or a border.'
    (F/'prompt.txt').write_text(p,encoding='utf-8');refs=read(F/'references.json')
    print(json.dumps({'name':'s1','prompt':p,'references':[r['file'] for r in refs]}))
def replace_rejected(name,source):
    F=D/name;assert (F/'rejected-unchanged-seam/generation.json').is_file()
    old=F/'edited-native.png';assert old.resolve().is_relative_to(T.resolve())
    with Image.open(source) as im:im.load();assert im.size==(1254,1254)
    old.unlink();record(name,source)
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare(sys.argv[2])
    elif sys.argv[1]=='record':record(sys.argv[2],sys.argv[3])
    elif sys.argv[1]=='retry-s1':retry_s1()
    elif sys.argv[1]=='replace-rejected':replace_rejected(sys.argv[2],sys.argv[3])
