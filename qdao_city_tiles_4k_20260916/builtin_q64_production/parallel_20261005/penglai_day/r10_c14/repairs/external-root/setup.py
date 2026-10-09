from pathlib import Path
from PIL import Image
import numpy as np,sys
R=Path(__file__).resolve().parent;B=R.parents[2];sys.path.insert(0,str(B));import production as p
for d in ['native','references','prompts','evidence','qa']:(R/d).mkdir(parents=True,exist_ok=True)
def a(f):return np.asarray(Image.open(f).convert('RGB'))
internal=B/'r10_c14/repairs/internal/r10_c14-internal-candidate-v2.png';assert p.sha(internal)=='54b22ddc98d20fc9d625229a098daf9650c89b5ea2789becdf182bac32d6bf37'
base=a(internal).copy();corner=p.read(B/'repairs/corner-r09c13/integration-v1.json')['pendingSoutheast'];old=a(corner['sourceNative'])[115:742,115:742]
assert np.array_equal(base[:627,:627],old)
base[:627,:627]=a(corner['file']);stage=R/'references/r10_c14-internal-v2-with-corner.png';Image.fromarray(base).save(stage);p.derived(stage,[internal,corner['file']],{'method':'exact top-left627 native corner composite over unchanged p11 core','formalAccepted':False})
ov=p.read(B/'tiles/current/current-overrides.json')['tiles'];north=Path(ov['r09_c14']['file']);west=Path(ov['r10_c13']['file'])
for name,path in [('north',north),('west',west)]:assert p.sha(path)==ov['r09_c14'if name=='north'else'r10_c13']['sha256']
nj=np.concatenate([a(north)[3469:],base[:627]],axis=0);wj=np.concatenate([a(west)[:,3469:],base[:,:627]],axis=1)
Image.fromarray(nj).save(R/'references/north-joint-input.png');Image.fromarray(wj).save(R/'references/west-joint-input.png')
records=[]
for direction,arr in [('north',nj),('west',wj)]:
    for i,start in enumerate([0,1024,2048,2842],1):
        name=direction[0]+str(i);part=arr[:,start:start+1254]if direction=='north'else arr[start:start+1254]
        f=R/'references'/f'{name}-input.png';Image.fromarray(part).save(f)
        sources=[north,stage]if direction=='north'else[west,stage]
        p.derived(f,sources,{'method':'native shared627+627 joint crop','direction':direction,'start':start,'sharedCoordinate':627,'resampling':False})
        prompt='Use case: precise-object-edit. Image1 is native1254 continuous game-art context across a '+('HORIZONTAL seam at y627'if direction=='north'else'VERTICAL seam at x627')+'. Remove the artificial straight stitch line: unify the original material color and brush texture through the line, reconnect every existing stone bevel, timber edge, rope, slab groove and shadow that crosses it into a smooth continuous original shape. Preserve exact object counts, geometry, crop, camera, scale, sunlight, shadows, widths and edge endpoints. Do not invent new tile joints or objects. Image2 is approved PRIMARY style only: bright clean full rounded Taoist Q handpainted game map, never UI. Preserve outermost150px as closely as possible while blending naturally through the middle. Keep meaningful natural texture, no blur or duplicate contours. No text, UI, labels, border or watermark. Repaint sufficient central native detail to eliminate the splice rather than retaining it as a material edge. Same1254 square pixel size.'
        call={'prompt':prompt,'referenced_image_paths':[f.as_posix(),'D:/work/image/designs/gameplay-ui/04-guild.png'],'transparent_background':False}
        (R/'prompts'/f'{name}.prompt.txt').write_text(prompt,encoding='utf8');p.write(R/'prompts'/f'{name}.call.json',call);records.append({'name':name,'direction':direction,'start':start,'file':str(f),'sha256':p.sha(f)})
p.write(R/'evidence/inputs.json',{'internal':{'file':str(internal),'sha256':p.sha(internal)},'withCorner':{'file':str(stage),'sha256':p.sha(stage)},'north':{'file':str(north),'sha256':p.sha(north)},'west':{'file':str(west),'sha256':p.sha(west)},'northGlobalOriginXY':[53248,36237],'westGlobalOriginXY':[52621,36864],'patches':records,'cornerPreservation':'Final merge must preserve accepted central corner within557px of both new shared-edge starts, then inspect return to new joints.','formalAccepted':False})
print({'jointInputs':len(records),'stage':str(stage)})
