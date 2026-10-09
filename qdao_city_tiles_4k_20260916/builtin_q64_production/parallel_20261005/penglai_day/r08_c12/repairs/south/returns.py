from helper import *
from PIL import Image
import sys
A=R/'output/r08_c12-south-candidate-v1.png';D=R/'output/r09_c12-north-candidate-v1.png'
BOXES={'return-trim':[1500,3000,2754,4254],'return-curb':[880,3900,2134,5154],'return-wood':[1800,3900,3054,5154]}
def setup():
 a=Image.open(A).convert('RGB');d=Image.open(D).convert('RGB');full=Image.new('RGB',(4096,8192));full.paste(a,(0,0));full.paste(d,(0,4096))
 for name,box in BOXES.items():
  dest=R/'references'/f'{name}-input.png';full.crop(box).save(dest);p.derived(dest,[A,D],{'method':'exact native crop across derived two-tile candidates','combinedBoxLTRB':box,'globalOriginXY':[45056+box[0],28672+box[1]],'sourceScaling':False})
def prepare(name,scene):
 refs=[(R/'references'/f'{name}-input.png').as_posix(),STYLE]
 prompt='Edit Image1 only at the same exact square native crop. Image2 is the approved primary painting style, never UI. This target has an accidental pasted transition with broken contours around the lower middle. '+scene+' Repair only the stated local transition into one clean coherent illustrated object surface. Outside the stated region preserve composition, shapes, painted texture, color, shadows and geometry as closely as possible. No blur, no duplication, no new objects, no added seams, no text or UI. Bright clean rounded Taoist Q painting; preserve camera and native scale.'
 (R/'prompts'/f'{name}.prompt.txt').write_text(prompt,encoding='utf8');call={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False};p.write(R/'prompts'/f'{name}.call.json',call);print(json.dumps(call))
def ingest(source,name):
 p.ROOT=R;assert not (R/'native'/f'{name}.png').exists();call=p.read(R/'prompts'/f'{name}.call.json');dest=p.ingest(source,name,R/'prompts'/f'{name}.prompt.txt',call['referenced_image_paths'],'native_local_return_repair');assert Image.open(dest).size==(1254,1254)
 rec=p.read(str(dest)+'.generation.json');rec['evidence']['toolOutputHintFile']=str(R/'evidence'/f'{name}.tool-result.json');rec['submittedParameters'].update(call);rec['sourceBoxLTRBCombined']=BOXES[name];p.write(str(dest)+'.generation.json',rec);print(dest)
if __name__=='__main__':
 if sys.argv[1]=='setup':setup()
 elif sys.argv[1]=='prepare':prepare(sys.argv[2],sys.argv[3])
 elif sys.argv[1]=='ingest':ingest(sys.argv[2],sys.argv[3])

