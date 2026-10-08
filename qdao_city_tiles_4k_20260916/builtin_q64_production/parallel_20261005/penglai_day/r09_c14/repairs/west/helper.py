from pathlib import Path
import sys,json
from PIL import Image
R=Path(__file__).resolve().parent
B=R.parents[2]
sys.path.insert(0,str(B));import production as p
W=B/'tiles/current/r09_c13-candidate-v4b.png'
E=B/'r09_c14/tiles/r09_c14-candidate.png'
STYLE='D:/work/image/designs/gameplay-ui/04-guild.png'
def setup():
    for d in ['references','native','prompts','evidence','qa','output']:(R/d).mkdir(parents=True,exist_ok=True)
    west=Image.open(W).convert('RGB');east=Image.open(E).convert('RGB')
    assert west.size==east.size==(4096,4096)
    full=Image.new('RGB',(1254,4326));full.paste(west.crop((3469,0,4096,4096)),(0,115));full.paste(east.crop((0,0,627,4096)),(627,115))
    halos=[B/'native/p14.png',B/'r09_c14/native/p11.png',B/'native/p44.png',B/'r09_c14/native/p41.png']
    full.paste(Image.open(halos[0]).convert('RGB').crop((512,0,1139,115)),(0,0));full.paste(Image.open(halos[1]).convert('RGB').crop((115,0,742,115)),(627,0))
    full.paste(Image.open(halos[2]).convert('RGB').crop((512,1139,1139,1254)),(0,4211));full.paste(Image.open(halos[3]).convert('RGB').crop((115,1139,742,1254)),(627,4211))
    dest=R/'references/joint-input-native.png';full.save(dest);p.derived(dest,[W,E]+halos,{'method':'integer source crops and assembly, no scaling','globalOriginXY':[52621,32653],'sharedGlobalX':53248,'sharedLocalX':627,'coreTileGlobalY':32768,'haloTopBottom':115,'warning':'top/bottom115 use unique native halo source; main4096 uses locked candidates'})
    for i in range(4):
        dest=R/'references'/f's{i+1}-input.png';full.crop((0,i*1024,1254,i*1024+1254)).save(dest);p.derived(dest,[R/'references/joint-input-native.png'],{'method':'native crop','sourceBoxLTRB':[0,i*1024,1254,i*1024+1254]})
    p.write(R/'evidence/input-lock.json',{'sources':[{'file':str(f),'sha256':p.sha(f)} for f in [W,E]+halos],'west':str(W),'east':str(E),'globalOriginXY':[52621,32653],'sharedGlobalX':53248,'r09_c13Rect':[49152,32768,4096,4096],'r09_c14Rect':[53248,32768,4096,4096],'noScaling':True,'formalAccepted':False})
def prepare(name,scene):
    i=int(name[1]);refs=[(R/'references'/f'{name}-input.png').as_posix(),STYLE]
    neighbor=''
    if i>1:
        refs.append((R/'native'/f's{i-1}.png').as_posix());neighbor='Image3 is the repaired UPPER neighboring segment. Its bottom230px is the same world area as target top230px; continue those shared objects and materials exactly while retaining Image1 crop. '
    prompt='Edit Image1: native shared-boundary repair for the continuous isometric Taoist Q fantasy game map 五行奇谈. Image1 is the exact edit target crop. Image2 is the approved PRIMARY painting style only, never copy the UI. '+neighbor+'REMOVE the accidental vertical rectangular image seam at x627 through the middle. It splits two separately painted halves of the same objects. Repaint a continuous shared local surface across both sides of the central line, roughly x360..880, with matching lighting and brushwork. The seam is NOT a real object edge. '+scene+' Material strokes MUST change where incompatible so the artificial straight line disappears. Preserve actual object counts, camera, perspective, scale, framing, silhouettes, true diagonal edges and endpoints; repair minor contour mismatches into one coherent contour. Preserve left200 and right200 pixels as return context and top/bottom120px near-match to supplied adjacent images; do not add rectangular boundaries around repaired regions. Bright clean rounded full Taoist Q handpainting, controlled brushwork, subtle bevels, soft shadows. No blur, duplication, extra objects, new cracks or grooves, grain, text, UI, labels, borders or watermark. Same exact square crop.'
    (R/'prompts'/f'{name}.prompt.txt').write_text(prompt,encoding='utf8');call={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False};p.write(R/'prompts'/f'{name}.call.json',call);print(json.dumps(call))
def ingest(source,name):
    p.ROOT=R;call=p.read(R/'prompts'/f'{name}.call.json');dest=p.ingest(source,name,R/'prompts'/f'{name}.prompt.txt',call['referenced_image_paths'],'native_joint_repair')
    rec=p.read(str(dest)+'.generation.json');rec['submittedParameters'].update(call);rec['globalOriginXY']=[52621,32653+(int(name[1])-1)*1024];rec['evidence']['toolOutputHintFile']=str(R/'evidence'/f'{name}.tool-result.json');rec['formalAccepted']=False;p.write(str(dest)+'.generation.json',rec);print(dest)
if __name__=='__main__':
    if sys.argv[1]=='setup':setup()
    elif sys.argv[1]=='prepare':prepare(sys.argv[2],sys.argv[3])
    elif sys.argv[1]=='ingest':ingest(sys.argv[2],sys.argv[3])
