import sys,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
ROOT=Path(__file__).resolve().parent
T=ROOT/'r08_c13';R=T/'repairs/west-common-edge'
WEST=ROOT/'r08_c12/output/r08_c12.png'
EAST=T/'output/r08_c13.png';STYLE=ROOT.parents[3]/'designs/gameplay-ui/04-guild.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def prep(i):
 R.mkdir(parents=True,exist_ok=True);start=[0,1024,2048,2842][i-1]
 pair=Image.new('RGB',(8192,4096));pair.paste(Image.open(WEST),(0,0));pair.paste(Image.open(EAST),(4096,0))
 guide=pair.crop((3469,start,4723,start+1254));path=R/f's{i}-input.png';guide.save(path)
 # Narrow overlap from previous repaired patch ensures longitudinal consistency.
 prev=R/f's{i-1}.png'
 if prev.exists():
  prior=[0,1024,2048,2842][i-2];overlap=prior+1254-start
  guide.paste(Image.open(prev).crop((0,1254-overlap,1254,1254)),(0,0));guide.save(path)
 refs=[{'file':str(path),'sha256':sha(path),'role':'edit target, true native pixels at joint c12/c13 seam; center x627 is the faulty join'},{'file':str(STYLE),'sha256':sha(STYLE),'role':'primary confirmed rendering style, no UI'}]
 prompt='''Use case: precise-object-edit. Edit IMAGE 1, a native-pixel close crop spanning the common vertical boundary of two neighboring tiles in a bright clean rounded Daoist chibi fishing-village map for 五行奇谈. The artificial cut is near x=627. Repair ONLY the discontinuous stone/pavement joints, timber contours, rope edges and red banner folds and light/shadow continuity across that cut. Preserve exact existing objects, scales, composition, camera, existing timber and fabric masses and daylight. The center is NOT a wall or stripe. Connect forms naturally, remove clipped/doubled pavement and banner contours and abrupt material/light changes. Do not invent objects or move the main contours. Preserve the outer 150 pixels at left and right as exactly as possible and maintain the whole top/bottom field of view; any already-sharp top overlap is previous repaired native context. Image 2 is PRIMARY user-confirmed style, use its controlled hand-painted rounded volume and clean materials only; no UI. Keep faithful original warm golden timber, red fabric and cream ropes, warm ivory paving, blue-gray stones and soft blue daylight shadows. Do not globally alter exposure. No text, frame, characters, plastic, fine noise, cracks, blur or artificial sharpening. One opaque square image, native1254 target, highest available visual finish, return only edited image 1.'''
 (R/f's{i}.txt').write_text(prompt,encoding='utf-8');js(R/f's{i}.references.json',refs)
 js(R/f's{i}-input.png.generation.json',{'file':str(path),'sha256':sha(path),'operation':'native-pixel joint crop with previous native overlap','sourceBoxInPair':[3469,start,4723,start+1254],'derivedFrom':[{'file':str(WEST),'sha256':sha(WEST)},{'file':str(EAST),'sha256':sha(EAST)}]+([{'file':str(prev),'sha256':sha(prev)}] if prev.exists() else []),'resized':False})
 print(json.dumps({'name':f's{i}','prompt':prompt,'references':[e['file'] for e in refs]}))
def record(i,src):
 src=Path(src);out=R/f's{i}.png';assert not out.exists();shutil.copyfile(src,out)
 im=Image.open(out);assert im.size==(1254,1254)
 js(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'width':im.width,'height':im.height,'format':'PNG','generatedAt':datetime.now(timezone.utc).isoformat(),'timestampMeaning':'locally observed tool completion','tool':'image_gen.imagegen','route':'builtin','configSnapshot':load(ROOT.parents[3]/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[x['file'] for x in load(R/f's{i}.references.json')]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; tool exposes no model/quality selectors or returned evidence.','evidence':{'toolResultSourcePath':str(src),'toolResultSha256':sha(src)},'prompt':str(R/f's{i}.txt'),'promptSha256':sha(R/f's{i}.txt'),'references':load(R/f's{i}.references.json'),'resizedAfterGeneration':False,'finalArtUpscaled':False})
 print(json.dumps({'file':str(out),'sha256':sha(out)}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prep(int(sys.argv[2]))
 elif sys.argv[1]=='record':record(int(sys.argv[2]),sys.argv[3])


