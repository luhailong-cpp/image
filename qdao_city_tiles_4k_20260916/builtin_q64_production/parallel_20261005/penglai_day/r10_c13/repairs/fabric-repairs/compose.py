import repair_helper as h
from PIL import Image,ImageDraw
import numpy as np,json

specs={
 'stripe1024-v1':{'input':'stripe1024-input.png','origin':[397,2842],'polygon':[(427,425),(527,368),(627,310),(727,260),(827,207),(827,1253),(427,1253)]},
 'stripe2048-v1':{'input':'stripe2048-input.png','origin':[1421,2842],'polygon':[(427,355),(527,420),(627,485),(727,540),(827,595),(827,1030),(700,1120),(540,1160),(480,1100),(427,1010)]}
}
for name,spec in specs.items():
    src=h.O/spec['input'];gen=h.O/(name+'-generated.png')
    a=Image.open(src).convert('RGB');b=Image.open(gen).convert('RGB');assert a.size==b.size==(1254,1254)
    mask=Image.new('L',a.size,0);ImageDraw.Draw(mask).polygon(spec['polygon'],fill=255)
    maskp=h.O/(name+'-mask.png');mask.save(maskp)
    h.derived(maskp,[src],{'method':'exact binary polygon ownership mask','points':spec['polygon'],'resize':False,'feather':False})
    out=h.O/(name+'-composite.png');Image.composite(b,a,mask).save(out)
    h.derived(out,[src,gen,maskp],{'method':'binary pixel ownership composite only','originTileXY':spec['origin'],'resize':False,'registration':False,'blur':False,'colorField':False,'pixelsOutsideMaskUnchanged':True})
    spec.update({'replacement':str(gen),'mask':str(maskp),'composite':str(out),'inputSha256':h.sha(src),'replacementSha256':h.sha(gen),'maskSha256':h.sha(maskp),'status':'pending_native_composite_visual_review'})
(h.O/'fabric-merge-manifest.json').write_text(json.dumps({'rawTile':str(h.R/'tiles/r10_c13-candidate.png'),'rawSha256':h.sha(h.R/'tiles/r10_c13-candidate.png'),'repairs':specs},ensure_ascii=False,indent=2),encoding='utf8')
