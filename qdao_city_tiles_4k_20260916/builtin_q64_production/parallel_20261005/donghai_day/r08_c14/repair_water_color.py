"""Bookkeeping for the targeted built-in water-color edits. No image processing."""
import sys,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
T=Path(__file__).resolve().parent
ROOT=T.parent
STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare(name):
 target=T/'native'/(name+'.png')
 d=T/'repairs/water-color'/name;d.mkdir(parents=True,exist_ok=True)
 ref=T/'native/r01_c02.png'
 refs=[{'file':str(target),'sha256':sha(target),'role':'edit target: exact frame and object geometry; replace only gray-green water color with reference blue'}, {'file':str(ref),'sha256':sha(ref),'role':'exact adjacent water palette and quiet broad water-block rendering reference; no transplant of objects'}, {'file':str(T/'native/r03_c04.png'),'sha256':sha(T/'native/r03_c04.png'),'role':'additional approved saturated cyan-blue water with soft broad shapes, no white mesh'}, {'file':str(STYLE),'sha256':sha(STYLE),'role':'primary user-confirmed rounded hand-painted materials style only; no UI content'}]
 prompt='''Use case: precise-object-edit. Edit IMAGE 1 only. This is a native square patch of an existing finished hand-painted Q-style fishing village map. Change ONLY the WATER BACKGROUND in image 1: replace the dull desaturated gray-green teal water with the vivid clear CYAN-BLUE palette and quietly painted broad low-contrast shapes in image 2 and image 3. It must belong to exactly the same water surface as those references. Image 2 is the immediately adjacent blue-water patch and is the exact color target. Image 3 confirms calm clear blue water material. Image 4 is the user-approved art rendering style, not scene content. Preserve image 1's exact camera, framing, all rope strands and knots, every wooden post and rail, red fabric and gold ornament silhouette and all object locations and colors. Keep every existing object pixel appearance as close as possible. Change water right up to the image edges, evenly across the whole visible water; do not leave gray-green edge strips or a green stripe. Water should be rich clear azure and cyan with soft broad painterly wave blocks, subtly graded like image 2. Do not add bright white or pale yellow mesh, lattice, foam, web-shaped caustics, shiny glare, noise or sharp small waves. No new objects, no object from other images, no labels, no UI, no border. Output only the edited image 1, opaque native 1254x1254 square, no resize, crop or rotation.'''
 (d/'prompt.txt').write_text(prompt,encoding='utf-8');save(d/'references.json',refs)
 save(d/'before.json',{'file':str(target),'sha256':sha(target),'recordSha256':sha(str(target)+'.generation.json')})
 print(json.dumps({'name':name,'prompt':prompt,'references':[x['file'] for x in refs]}))
def apply(name,src):
 src=Path(src);target=T/'native'/(name+'.png');d=T/'repairs/water-color'/name
 before=read(d/'before.json');assert sha(target)==before['sha256']
 im=Image.open(src);im.load();assert im.size==(1254,1254) and im.format=='PNG'
 rec=read(str(target)+'.generation.json');rej=T/'rejected/water-graygreen-20261008';rej.mkdir(parents=True,exist_ok=True)
 oldrec=rej/(name+'-'+before['sha256'][:12]+'.generation.json');shutil.copyfile(str(target)+'.generation.json',oldrec)
 refs=read(d/'references.json');refs[0].update(availability='superseded',historicalRecord=str(oldrec),historicalRecordSha256=sha(oldrec),pixelValidation='historical-record-only-not-current-pixels')
 record={**rec,'sha256':sha(src),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'prompt':str(d/'prompt.txt'),'promptSha256':sha(d/'prompt.txt'),'references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[x['file'] for x in refs]},'evidence':{'toolResultSourcePath':str(src),'toolResultSha256':sha(src),'responseMetadata':'Local output path returned by built-in imagegen; no model/quality disclosed.'},'editScope':'Water color and quiet broad water shading only; scene geometry preserved visually.'}
 shutil.copyfile(src,target);save(str(target)+'.generation.json',record)
 save(d/'replacement.json',{'beforeSha256':before['sha256'],'afterSha256':sha(target),'historicalRecord':str(oldrec),'oldCanonicalPixelsReplaced':True,'oldSourcePixelsCleanup':'pending reference audit'})
 print(json.dumps({'file':str(target),'sha256':sha(target)}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(sys.argv[2])
 elif sys.argv[1]=='apply':apply(sys.argv[2],sys.argv[3])
