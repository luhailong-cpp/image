"""Prepare guide-only north/east regional references for westward map growth."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,re
import numpy as np
from PIL import Image
from workflow import OUTPUT_ROOT,safe_output,sha256,read_json,write_json,save_image
from prepare_frontier import source_image

def run(a):
    m=re.fullmatch(r'r(\d{2})_c(\d{2})',a.tile)
    if not m:raise ValueError('Invalid tile')
    row,col=map(int,m.groups())
    if not (2<=row<=16 and 1<=col<16):raise ValueError('North/east neighbors must exist in grid')
    tile=safe_output(OUTPUT_ROOT/a.tile)
    if tile.parent!=OUTPUT_ROOT or tile.name!=a.tile:raise ValueError('Tile output identity mismatch')
    def destination(relative):
        path=safe_output(tile/relative)
        if not path.is_relative_to(tile):raise ValueError('Output escapes requested tile')
        return path
    out=destination('regional')
    output_paths=[destination('regional/'+f) for f in
        ('context.json','target-layout-only.png','east-context-preview.png','north-context-preview.png')]
    protected_paths=output_paths+[destination('regional/regional.png')]
    if any(p.exists() for p in protected_paths):
        raise FileExistsError('Refusing to replace existing regional work')
    handoff=read_json(OUTPUT_ROOT/'handoff.json');queue=read_json(OUTPUT_ROOT/'production-queue.json')
    entries=[v for v in queue['tiles'] if v['id']==a.tile]
    rect=[(col-1)*4096,(row-1)*4096,4096,4096]
    if len(entries)!=1 or entries[0]['pixelRectXYWH']!=rect:raise ValueError('Queue geometry mismatch')
    if queue['planSha256']!=handoff['plan']['sha256']:raise ValueError('Plan mismatch')
    if handoff['targetCityPixels']!=[65536,65536] or handoff['targetTilePixels']!=[4096,4096]:raise ValueError('City/tile geometry mismatch')
    layout,lmeta=source_image(handoff['layout']['file'])
    if lmeta['sha256']!=handoff['layout']['sha256'] or lmeta['pixels']!=handoff['layout']['pixels']:raise ValueError('Layout changed')
    neighbors={}
    for side in ('east','north'):
        ext,em=source_image(getattr(a,side+'_extended'),(4326,4326))
        core,cm=source_image(getattr(a,side+'_core'),(4096,4096))
        if ext.crop((115,115,4211,4211)).tobytes()!=core.tobytes():raise ValueError(side+' core mismatch')
        expected=f'r{row:02d}_c{col+1:02d}' if side=='east' else f'r{row-1:02d}_c{col:02d}'
        if expected not in Path(em['file']).parts:raise ValueError(side+' source tile identity mismatch')
        em.update(tile=expected,role=side+' native extended context')
        cm.update(tile=expected,role=side+' effective core preview source')
        neighbors[side]=(ext,core,em,cm)
    x,y,_,_=rect;extent=[x-115,y-115,x+4211,y+4211]
    scaled=[extent[0]*layout.width/65536,extent[1]*layout.height/65536,
            extent[2]*layout.width/65536,extent[3]*layout.height/65536]
    guide=layout.transform((4326,4326),Image.Transform.EXTENT,scaled,Image.Resampling.BICUBIC)
    east=neighbors['east'][0].crop((0,0,230,4326))
    north=neighbors['north'][0].crop((0,4096,4326,4326))
    corner_a=np.array(east.crop((0,0,230,230)),dtype=np.int16)
    corner_b=np.array(north.crop((4096,0,4326,230)),dtype=np.int16)
    diff=corner_a-corner_b
    guide.paste(east,(4096,0));guide.paste(north,(0,0))
    assert guide.crop((0,0,4326,230)).tobytes()==north.tobytes()
    assert guide.crop((4096,230,4326,4326)).tobytes()==east.crop((0,230,230,4326)).tobytes()
    for sub in ('regional','native','guides','jobs','prompts','qa'):destination(sub).mkdir(parents=True,exist_ok=True)
    if any(p.exists() for p in protected_paths):raise FileExistsError('Output appeared during preparation')
    target=save_image(destination('regional/target-layout-only.png'),guide.resize((1254,1254),Image.Resampling.LANCZOS))
    target.update(guideOnly=True,finalArt=False)
    refs=[{'path':target['file'],'role':'Guide-only framing with native north/east overlap; north wins shared corner'}]
    outputs={'targetLayout':target}
    context={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':a.tile,
        'pixelRectXYWH':rect,'worldRect':entries[0].get('worldRect'),'wholeCityPixels':[65536,65536],
        'guideOnly':True,'finalArt':False,'formalAccepted':False,'layout':lmeta,
        'extentInWholeCityPixels':extent,'extentInLayoutPixels':scaled,
        'nativeTraversal':'right_to_left_top_to_bottom','guideCanvasPixels':[4326,4326],
        'exportedRegionalGuidePixels':[1254,1254],
        'cornerHandling':{'priority':'north','differingPixelCount':int(np.any(diff!=0,axis=2).sum()),
                          'maximumAbsoluteChannelDifference':int(np.abs(diff).max()),
                          'notBothSourcesExactWhenConflicting':True},
        'overlapMappings':{'east':{'source':[0,0,230,4326],'destination':[4096,0,4326,4326],
                                  'exactRegionExcludesNorthCorner':[4096,230,4326,4326],
                                  'pixelIdentityVerifiedBeforePreviewDownsample':True},
                           'north':{'source':[0,4096,4326,4326],'destination':[0,0,4326,230],
                                    'pixelIdentityVerifiedBeforePreviewDownsample':True}},
        'operation':'Layout BICUBIC extent used only as guide; integer native east paste then north paste; LANCZOS guide downsample. No final art generated.',
        'queue':{'file':str(OUTPUT_ROOT/'production-queue.json'),'sha256':sha256(OUTPUT_ROOT/'production-queue.json')},
        'handoff':{'file':str(OUTPUT_ROOT/'handoff.json'),'sha256':sha256(OUTPUT_ROOT/'handoff.json')}}
    for side,(_,core,em,cm) in neighbors.items():
        context[side+'Extended']=em;context[side+'Core']=cm
        preview=save_image(destination(f'regional/{side}-context-preview.png'),core.resize((1254,1254),Image.Resampling.LANCZOS))
        preview.update(guideOnly=True,finalArt=False);outputs[side+'Preview']=preview
        refs.append({'path':preview['file'],'role':side+' matching core preview; continuity only'})
    refs.append({'path':'D:/work/image/designs/gameplay-ui/04-guild.png','role':'Approved primary painting/material style; no copied UI or objects'})
    context.update(outputs=outputs,references=refs)
    write_json(destination('regional/context.json'),context)
    print(json.dumps({'context':str(out/'context.json'),'references':refs}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('tile')
    for side in ('east','north'):
        p.add_argument('--'+side+'-extended',required=True);p.add_argument('--'+side+'-core',required=True)
    run(p.parse_args())
