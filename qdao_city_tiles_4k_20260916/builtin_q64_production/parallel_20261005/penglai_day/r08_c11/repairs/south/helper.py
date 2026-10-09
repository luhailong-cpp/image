from pathlib import Path
from PIL import Image
import sys,json
R=Path(__file__).resolve().parent;B=R.parents[2];sys.path.insert(0,str(B));import production as p
N=R.parent/'internal/r08_c11-internal-candidate-v5.png'
S=B/'tiles/current/region-v6/r09_c11-candidate.png'
STYLE='D:/work/image/designs/gameplay-ui/04-guild.png'
STARTS=[0,947,1895,2842]
def setup():
 for d in ['references','native','prompts','evidence','qa','output']:(R/d).mkdir(parents=True,exist_ok=True)
 assert p.sha(S)=='149ca13e45f84edb2b69e1a637b56e765af821d209e11e953708a9d05ce5fc8f'
 n=Image.open(N).convert('RGB');s=Image.open(S).convert('RGB');assert n.size==s.size==(4096,4096)
 full=Image.new('RGB',(4096,1254));full.paste(n.crop((0,3469,4096,4096)),(0,0));full.paste(s.crop((0,0,4096,627)),(0,627))
 dest=R/'references/joint-input-native.png';full.save(dest);p.derived(dest,[N,S],{'method':'exact native joint assembly; no scale','globalOriginXY':[40960,32141],'sharedGlobalY':32768,'sharedLocalY':627,'northBoxLTRB':[0,3469,4096,4096],'southBoxLTRB':[0,0,4096,627]})
 for i,x in enumerate(STARTS):
  dest=R/'references'/f's{i+1}-input.png';full.crop((x,0,x+1254,1254)).save(dest);p.derived(dest,[R/'references/joint-input-native.png'],{'method':'native crop','sourceBoxLTRB':[x,0,x+1254,1254],'globalOriginXY':[40960+x,32141]})
 p.write(R/'evidence/input-lock.json',{'sources':[{'file':str(f),'sha256':p.sha(f)} for f in [N,S]],'nativeSize':[1254,1254],'segmentStarts':STARTS,'sharedGlobalY':32768,'globalJointOriginXY':[40960,32141],'nativeScale':1,'sourceOverwrite':False,'formalAccepted':False})
def prepare(name,scene):
 i=int(name[1])-1;refs=[(R/'references'/f'{name}-input.png').as_posix(),STYLE];neighbor=''
 if i>0:
  overlap=STARTS[i-1]+1254-STARTS[i];refs.append((R/'native'/f's{i}.png').as_posix());neighbor=f'Image3 is the already repaired LEFT neighbor. Its right{overlap}px is the same world area as target left{overlap}px. Continue exactly those overlapping objects. '
 prompt='Edit Image1 at its exact square crop, native joint repair for continuous isometric Taoist Q fantasy map äº”è¡Œå¥‡è°ˆ. Image1 is an unscaled crop spanning two map tiles with an ARTIFICIAL HORIZONTAL SEAM at y627. Image2 is PRIMARY approved painting style only; no UI. '+neighbor+'REMOVE the artificial straight seam by coherently repainting both sides. The two halves may show incompatible shifted or duplicated geometry; those mismatched contours MUST change into one coherent structure. '+scene+' Preserve the overall camera, world scale, crop and the real objects. Top and bottom120px are native return context, keep their endpoints and texture near-identical. Preserve the real outer left/right endpoints where possible but remove a visible horizontal seam all the way to image edge. No artificial rectangular boundaries, ghosting, duplicate rims, duplicate trunks, blurry smoothing, new objects, text, labels or UI. Bright clean rounded full Taoist Q handpainting, smooth clean materials, gentle controlled highlights, cool soft shadows. Redraw incompatible pigment strokes to remove the straight cut instead of merely keeping contradictory texture.'
 (R/'prompts'/f'{name}.prompt.txt').write_text(prompt,encoding='utf8');call={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False};p.write(R/'prompts'/f'{name}.call.json',call);print(json.dumps(call))
def ingest(source,name):
 p.ROOT=R;assert not (R/'native'/f'{name}.png').exists()
 call=p.read(R/'prompts'/f'{name}.call.json');dest=p.ingest(source,name,R/'prompts'/f'{name}.prompt.txt',call['referenced_image_paths'],'native_joint_repair')
 assert Image.open(dest).size==(1254,1254)
 rec=p.read(str(dest)+'.generation.json');rec['submittedParameters'].update(call);rec['globalOriginXY']=[40960+STARTS[int(name[1])-1],32141];rec['evidence']['toolOutputHintFile']=str(R/'evidence'/f'{name}.tool-result.json');p.write(str(dest)+'.generation.json',rec);print(dest)
if __name__=='__main__':
 if sys.argv[1]=='setup':setup()
 elif sys.argv[1]=='prepare':prepare(sys.argv[2],sys.argv[3])
 elif sys.argv[1]=='ingest':ingest(sys.argv[2],sys.argv[3])
