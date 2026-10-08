from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
from PIL import Image
R=Path(__file__).resolve().parent;T=R.parent
sys.path.insert(0,str(T));import helper as h
N=T.parent/'tiles/current/r09_c13-candidate-v4b.png'
RAW=T/'tiles/r10_c13-candidate.png'
STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
def prepare():
    out=R/'north-table-target.png';im=Image.new('RGB',(1254,1254));im.paste(Image.open(N).crop((1152,3469,2406,4096)),(0,0));im.paste(Image.open(RAW).crop((1152,0,2406,627)),(0,627));im.save(out)
    h.p.derived(out,[N,RAW],{'method':'native crop joint context','northBoxLTRB':[1152,3469,2406,4096],'southBoxLTRB':[1152,0,2406,627],'resampling':None,'finalUseForbidden':True})
    prompt='Use case: precise-object-edit. Image 1 is the exact native-size EDIT TARGET, a 1254-square patch across a horizontal map tile seam at y627. Image 2 is the approved PRIMARY PAINTING STYLE, never copy its UI. Repair only the accidental horizontal splice: reconnect the golden wooden tabletop at the right half and its dark brown front apron, preserve one single smooth rounded tabletop edge with its existing endpoints; reconnect existing foliage leaf silhouettes and tree trunk across the same seam. Remove the horizontal tint jump so each material continues naturally. Keep the exact camera, crop, scale, all objects, their position, count, outline design, topology and density. Restrict changes to a narrow band around y627, returning exactly to original pixels by y470 and y790 and preserving the outer 150px image frame. All other pixels unchanged. Crisp clean bright full rounded Taoist Q game painting matching the target and style; delicate warm wood and ceramic bevels, clean highlights, restrained brush texture and cool shadows. Do not add leaves, beams, panels, subdivisions, seams or lines. No blur, halos, noise, text, UI, borders or watermark. Output exact same square crop.'
    call={'prompt':prompt,'referenced_image_paths':[out.as_posix(),STYLE.as_posix()],'transparent_background':False}
    h.p.write(R/'north-table.call.json',call);(R/'north-table.prompt.txt').write_text(prompt,encoding='utf8')
    print(json.dumps(call))
if __name__=='__main__':prepare()
