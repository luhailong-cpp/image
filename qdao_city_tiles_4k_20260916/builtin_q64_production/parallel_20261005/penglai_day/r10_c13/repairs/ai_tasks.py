from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
from PIL import Image
R=Path(__file__).resolve().parent;T=R.parent
sys.path.insert(0,str(T));import helper as h
STYLE='D:/work/image/designs/gameplay-ui/04-guild.png'
RAW=T/'tiles/r10_c13-candidate.png'
def make(name,box,detail):
    out=R/(name+'-target.png');Image.open(RAW).crop(box).save(out);h.p.derived(out,[RAW],{'method':'integer native crop for repair','boxLTRB':box,'resampling':None,'finalUseForbidden':True})
    prompt='Use case: precise-object-edit. Image 1 is the exact native EDIT TARGET crop; image 2 is the approved PRIMARY PAINTING STYLE, never copy UI. '+detail+' Preserve exact camera, crop, scale, every object, boundary endpoints, silhouette, count, material identity and occlusion. Keep all pixels outside the narrow repair band unchanged, especially the outer100px frame. Repair only the identified accidental stitch; do not change intentional material joints. Bright clean full rounded Taoist Q handpaint game art; restrained native brush texture, clean highlights and cool shadows. No added objects, detail density, blur, sharpen halos, text, UI, watermark or frame. Exact same square crop.'
    call={'prompt':prompt,'referenced_image_paths':[out.as_posix(),STYLE],'transparent_background':False};h.p.write(R/(name+'.call.json'),call);(R/(name+'.prompt.txt')).write_text(prompt,encoding='utf8')
    print(json.dumps(call))
def ingest(source,name):
    (R/'native').mkdir(exist_ok=True);h.p.ROOT=R;call=h.p.read(R/(name+'.call.json'));dest=h.p.ingest(source,name,R/(name+'.prompt.txt'),call['referenced_image_paths'],'native_detail_repair')
    print(dest)
if __name__=='__main__':
    if sys.argv[1]=='ingest':ingest(sys.argv[2],sys.argv[3])
    elif sys.argv[1]=='prepare':
        make('roof-x1024',[397,0,1651,1254],'The vertical seam at x627 through the golden roof surface has a visible pigment/color change. Remove that accidental vertical strip, preserve and reconnect every roof rim and curved edge with the exact endpoints. Edit only x490..770 around the seam, feathering paint appearance back to the unaltered surfaces without actual blur.')
        make('paving-y3072',[0,2445,1254,3699],'At horizontal y627, the cream paving bevel diagonal at x800 has a tiny splice offset. Reconnect it as one clean continuous existing rounded bevel using original endpoints. Harmonize the slight paving tint across the same line. Edit only y520..735; retain the cropped blue awning and wooden knob.')
        make('wall-y3072',[2842,2445,4096,3699],'At horizontal y627, the grey-blue stone wall has an accidental pigment band. Harmonize that one band and reconnect the existing stone outlines without adding or shifting any edges. Edit only y520..735; preserve every diagonal bevel and rounded stone end.')
