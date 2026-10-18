from pathlib import Path
from PIL import Image
import hashlib,json,datetime,numpy as np
R=Path(__file__).resolve().parent;T=R.parent.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def write(p,j):assert not p.exists();p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
def png(p,im):assert not p.exists();im.save(p)
Q=read(T/'review/independent-20261016/visual-qa.json');B=Image.open(Q['candidate']['path']).convert('RGB');W=Image.open(Q['neighborInputs']['west']['path']).convert('RGB')
N=Image.open(Q['neighborInputs']['north']['path']).convert('RGB');NWref=read(T.parent/'r15_c15/candidate/latest-assembly.json')['candidate'];NW=Image.open(NWref['path']).convert('RGB')
sources={'child':Q['candidate'],'west':Q['neighborInputs']['west'],'north':Q['neighborInputs']['north'],'northwest':NWref}
for s in sources.values():assert sha(s['path'])==s['sha256']
refs=read(T/'records/p03_04_v20261016T041829_894fc41e.reference-evidence.json')[:3]
for key,box,region in [('W01-v1',[-400,-200,854,1054],[0,0,400,600]),('W02-v1',[-400,2100,854,3354],[0,2380,650,3110])]:
 d=R/key;d.mkdir(exist_ok=False);x0,y0,x1,y1=box;target=Image.new('RGB',(1254,1254))
 if key.startswith('W01'):
  target.paste(NW.crop((3696,3896,4096,4096)),(0,0));target.paste(N.crop((0,3896,854,4096)),(400,0))
  target.paste(W.crop((3696,0,4096,1054)),(0,200));target.paste(B.crop((0,0,854,1054)),(400,200))
  goal='The real tile seam is vertical target x400, and horizontal target y200. ALL pixels LEFT of x400 and ALL pixels ABOVE y200 are immutable neighboring cores. Edit ONLY child x400..800,y200..800. At x400,y305..405 the old left stone coping arrives but the child abruptly has plain stone. Complete this short projecting stone coping into the child with matching bevel and clean closed END / return before it reaches immutable top y200. The real north image above y200 has NO coping continuation, so do NOT extend a band through the top boundary. A closed, physically plausible short dressed-stone end is required, not a floating grout stub or chopped rectangular piece. Keep the existing child diagonal slab pattern beyond x800 and below y800 exactly fixed. Do not create a new pillar, column, rail, ornament, object or additional belt. Preserve all true long grout and the existing north-wall geometry. Match pale stone in the small repaired area without a visible vertical material cut.'
 else:
  target.paste(W.crop((3696,2100,4096,3354)),(0,0));target.paste(B.crop((0,2100,854,3354)),(400,0))
  goal='The actual west tile seam is vertical target x400. ALL LEFT x0..400 are immutable west core. Edit ONLY child x400..1050,y280..1010. The same diagonal projecting stone coping reaches x400 at approximately target y700 from the LEFT, while the child incorrectly starts its top about170 pixels higher. Rebuild only child-side transition so this ONE existing projecting coping joins the old left anchor at the correct height and thickness, then meets the unchanged existing coping and joints at target x1050. Remove the duplicated/too-high start on the child. Give it one coherent beveled top plane and front stone face, with clean believable perspective. No disconnected parallel ledge, abrupt step, floating end, or duplicate rail. Preserve bottom masonry and all true surrounding grout wherever not required for this reconnection. Keep every pixel outside the child edit box fixed. Match existing warm pale stone into grey child stone without a hard material seam; no gold, no new ornaments, plants or extra architecture.'
 prompt='Use case: precise-object-edit. Native opaque1254x1254 PNG. Inputs1/2/3 are approved Taoist chibi hand-painted STYLE ONLY; LAST input4 is the sole edit target, an exact1:1 collage of actual4096neighbor cores at their real coordinates. Preserve scale, camera, perspective, cropped framing and all unaffected pixels. '+goal+' No text, labels, UI, watermarks, bokeh, blur, rescale or whole-scene redraw. Return exactly1254x1254.'
 png(d/'target-native-1254.png',target);a=np.zeros((1254,1254),dtype=np.uint8);rx0,ry0,rx1,ry1=region;a[ry0-y0:ry1-y0,rx0-x0:rx1-x0]=255;png(d/'requested-mask-1254.png',Image.fromarray(a))
 (d/'prompt.txt').write_text(prompt,encoding='utf-8');request={'prompt':prompt,'referenced_image_paths':[r['path'] for r in refs]+[str(d/'target-native-1254.png')],'transparent_background':False};write(d/'request.json',request)
 write(d/'preparation.json',{'tile':'r16_c16','repair':key,'preparedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':sources,'cropBoxInChildCoordinates':box,'editRegionInChildCoordinates':region,'target':ref(d/'target-native-1254.png'),'requestedMask':ref(d/'requested-mask-1254.png'),'request':ref(d/'request.json'),'prompt':ref(d/'prompt.txt'),'styleReferences':refs,'route':'builtin','actualModel':None,'formalAccepted':False,'allowedChildX':[0,650],'immutableOtherWorkers':'x>=1050 north and right-side whole block'})
 print(json.dumps({'key':key,'request':str(d/'request.json'),'target':str(d/'target-native-1254.png')}))
