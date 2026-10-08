from pathlib import Path
import sys,json
from PIL import Image
B=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(B));import production as p
R=Path(__file__).resolve().parent
STYLE='D:/work/image/designs/gameplay-ui/04-guild.png'

def setup(south):
    for d in ['references','prompts','native','evidence','qa']:(R/d).mkdir(parents=True,exist_ok=True)
    h=p.read(B/'handoff.json')
    paths=[Path(h['baselineCandidates'][1]['file']),B/'tiles/current/r09_c12-candidate.png',B/'tiles/current/r09_c13-candidate-v4b.png',Path(south),B/'r10_c12/native/p11.png',B/'r10_c13/native/p11.png']
    a=[Image.open(f).convert('RGB') for f in paths]
    canvas=Image.new('RGB',(4326,1254))
    canvas.paste(a[0].crop((3981,3469,4096,4096)),(0,0))
    canvas.paste(a[1].crop((0,3469,4096,4096)),(115,0))
    canvas.paste(a[2].crop((0,3469,115,4096)),(4211,0))
    canvas.paste(a[3].crop((0,0,4096,627)),(115,627))
    canvas.paste(a[4].crop((0,115,115,742)),(0,627))
    canvas.paste(a[5].crop((115,115,230,742)),(4211,627))
    full=R/'references/north-joint-input-native.png';canvas.save(full)
    p.derived(full,paths,{'method':'Integer native crops, no resampling. 627px above and below boundary. Horizontal115px halos from actual neighboring source pixels.','globalOriginXY':[44941,36237],'jointLineY':627,'sourceOrder':list(map(str,paths))})
    for i in range(4):
        name=f's{i+1}';dest=R/'references'/f'{name}-input.png';canvas.crop((i*1024,0,i*1024+1254,1254)).save(dest)
        p.derived(dest,[full],{'method':'native joint segment crop','boxLTRB':[i*1024,0,i*1024+1254,1254]})
    p.write(R/'evidence/input-lock.json',{'sources':[{'file':str(f),'sha256':p.sha(f)} for f in paths],'southCandidate':str(south),'jointLineY':627,'core':1024,'halo':115,'formalAccepted':False})

def prepare(name):
    refs=[(R/'references'/f'{name}-input.png').as_posix(),STYLE]
    extra=''
    i=int(name[1])
    if i>1:
        neighbor=R/'native'/f's{i-1}.png'
        if neighbor.exists():
            refs.append(neighbor.as_posix());extra='Image3 is the already repaired LEFT joint segment. Its right230px equals the same world area as target left230px; preserve that overlap while keeping Image1 crop. '
    scene='Clear turquoise blue water, broad clean rounded ripple cells and restrained bright caustics; keep exact existing ripple geometry and density.' if i<3 else 'Rounded golden yellow roof tiles, ochre ridge tiles and warm wood; preserve every tile seam, bevel and silhouette exactly.'
    prompt='Use case: precise-object-edit. Asset: native seam repair of continuous Taoist Q fantasy game map 五行奇谈. Image1 is EDIT TARGET, an exact native joint crop from two adjacent map tiles. Image2 is approved PRIMARY PAINTING STYLE, not UI content. '+extra+'The horizontal line at y627 (middle) is an accidental painting seam, not a real scene edge. Repair ONLY the local material/paint transition in a band around the middle, approximately y420..840, so there is one continuous clean hand-painted surface across y627. '+scene+' Keep camera, scale, cropping, every object, contours and structural endpoints fixed. Preserve top320px and bottom320px and all corner geometry. Make the center match both existing sides with natural material texture, not a straight boundary, blur or extra objects. Bright clean full rounded Q handpainting, delicate restrained surface strokes. Remove tonal bands and abrupt texture-density changes. Do not shift roof seams or invent cracks, ripples, foliage, ornament or new shapes. No UI, writing, labels, border or watermark. Return the exact square crop.'
    (R/'prompts'/f'{name}.prompt.txt').write_text(prompt,encoding='utf8')
    call={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False};p.write(R/'prompts'/f'{name}.call.json',call);print(json.dumps(call))

def ingest(source,name):
    call=p.read(R/'prompts'/f'{name}.call.json');p.ROOT=R
    dest=p.ingest(source,name,R/'prompts'/f'{name}.prompt.txt',call['referenced_image_paths'],'native_joint_repair')
    rec=p.read(str(dest)+'.generation.json');rec['evidence']['toolOutputHintFile']=str(R/'evidence'/f'{name}.tool-result.json');rec['globalJointOriginXY']=[44941+(int(name[1])-1)*1024,36237];rec['formalAccepted']=False;p.write(str(dest)+'.generation.json',rec);print(dest)

if __name__=='__main__':
    if sys.argv[1]=='setup':setup(sys.argv[2])
    elif sys.argv[1]=='prepare':prepare(sys.argv[2])
    elif sys.argv[1]=='ingest':ingest(sys.argv[2],sys.argv[3])
