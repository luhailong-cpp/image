import sys,json,shutil,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parent;T=R/'r08_c15';D=T/'repairs/wood-horizontal';P=T/'output/r08_c15.png'
STYLE=R.parents[3]/'designs/gameplay-ui/04-guild.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare(i):
 D.mkdir(parents=True,exist_ok=True);x=[0,1024,2048,2842][i-1];y=397
 assert not (D/f's{i}.png').exists()
 original=Image.open(P).convert('RGB').crop((x,y,x+1254,y+1254));guide=original.copy()
 source={'file':str(P),'sha256':sha(P),'role':'actual current 4096 candidate, native pixel crop'}
 refs0=[source]
 if i>1:
  prev=D/f's{i-1}.png';px=[0,1024,2048,2842][i-2];overlap=px+1254-x
  guide.paste(Image.open(prev).crop((1254-overlap,0,1254,1254)),(0,0))
  refs0.append({'file':str(prev),'sha256':sha(prev),'role':'previous horizontal repair native overlap'})
 path=D/f's{i}-input.png';guide.save(path)
 save(str(path)+'.generation.json',{'file':str(path),'sha256':sha(path),'operation':'native pixel crop with preceding repair context','derivedFrom':refs0,'sourceRectXYXY':[x,y,x+1254,y+1254],'rawSourceRGBSha256':hashlib.sha256(original.tobytes()).hexdigest(),'resized':False})
 refs=[{'file':str(path),'sha256':sha(path),'role':'native joint crop edit target'},{'file':str(STYLE),'sha256':sha(STYLE),'role':'primary confirmed rounded hand-painted material style, no UI'}]
 prompt="""Edit IMAGE 1 only. This is a native-pixel crop from a bright clean rounded hand-painted Daoist chibi fishing boat. Correct the artificial horizontal image-assembly join near y627: the same timber boards and blue painted hull have abrupt stepped or jagged changes in brightness, texture and contour at that cut. Restore continuous material lighting and wood grain through that horizontal band. Match the existing colors on BOTH sides through natural continuous shading. This cut is not a physical plank edge or cast shadow; remove its rectangular/jagged tonal boundary while retaining all real plank joints, rope strands, posts, hull silhouettes, curved edges, tarp and daylight shadows. Preserve the exact geometry, every object and their existing sizes and coordinates. Do not repaint the whole scene, add seams or invent anything. The outer 150 pixels on all four sides should stay as close as possible to the input; the left overlap may be an already repaired region, preserve it. Keep the same warm golden timber, blue hull and calm cyan-blue water if present. No added water texture, caustic nets, tiny waves, grain noise, text, frame or UI. Image 2 is the primary confirmed style reference only. Return only corrected image 1, opaque native1254 square, unchanged camera, no resizing or zoom."""
 prompt += ' IMPORTANT: preserve every broad real DIAGONAL CAST SHADOW on the lower timber wall and behind posts at the exact existing location and opacity; do not remove or brighten any physical cast shadow. Only the irregular horizontal jagged brightness/grain discontinuity around y627 is an assembly fault.'
 (D/f's{i}.txt').write_text(prompt,encoding='utf-8');save(D/f's{i}.references.json',refs)
 print(json.dumps({'name':f's{i}','prompt':prompt,'references':[q['file'] for q in refs]}))
def record(i,source):
 source=Path(source);out=D/f's{i}.png';assert not out.exists();im=Image.open(source);im.load();assert im.size==(1254,1254);shutil.copyfile(source,out)
 refs=load(D/f's{i}.references.json');prompt=D/f's{i}.txt'
 save(str(out)+'.generation.json',{'file':str(out),'sha256':sha(out),'width':1254,'height':1254,'format':'PNG','generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':load(R.parents[3]/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[e['file'] for e in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host tool has no model/quality selector or return metadata.','evidence':{'toolResultSourcePath':str(source),'toolResultSha256':sha(source)},'prompt':str(prompt),'promptSha256':sha(prompt),'references':refs,'resizedAfterGeneration':False,'finalArtUpscaled':False})
 print(json.dumps({'file':str(out),'sha256':sha(out)}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(int(sys.argv[2]))
 elif sys.argv[1]=='record':record(int(sys.argv[2]),sys.argv[3])
