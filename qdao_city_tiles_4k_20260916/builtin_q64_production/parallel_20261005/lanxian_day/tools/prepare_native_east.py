"""Prepare guide-only cells right-to-left, using exact north/east native context."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,re
import numpy as np
from PIL import Image
from workflow import OUTPUT_ROOT,safe_output,sha256,read_json,write_json,save_image
from prepare_native_frontier import load_native,native_weights

def run(tile_name,row,col):
    match=re.fullmatch(r'r(\d{2})_c(\d{2})',tile_name)
    if not match or not (1<=row<=4 and 1<=col<=4):
        raise ValueError('Invalid tile/cell')
    tile_row,tile_col=map(int,match.groups())
    if not (2<=tile_row<=16 and 1<=tile_col<16):raise ValueError('Tile requires valid north/east grid neighbors')
    tile=safe_output(OUTPUT_ROOT/tile_name);cell=f'r{row:02d}_c{col:02d}'
    if tile.parent!=OUTPUT_ROOT or tile.name!=tile_name:raise ValueError('Tile output identity mismatch')
    def destination(relative):
        path=safe_output(tile/relative)
        if not path.is_relative_to(tile):raise ValueError('Output escapes requested tile')
        return path
    gp=destination(f'guides/{cell}.layout-only.png');pf=destination(f'prompts/{cell}.prompt.txt');jp=destination(f'jobs/{cell}.json')
    protected_paths=[gp,pf,jp,destination(f'native/{cell}.png')]
    if any(p.exists() for p in protected_paths):raise FileExistsError(cell)
    cp=tile/'regional/context.json';ctx=read_json(cp)
    if ctx.get('nativeTraversal')!='right_to_left_top_to_bottom':raise ValueError('Incorrect traversal context')
    if ctx.get('tile')!=tile_name or ctx.get('pixelRectXYWH')!=[(tile_col-1)*4096,(tile_row-1)*4096,4096,4096]:
        raise ValueError('Context tile geometry mismatch')
    rp=tile/'regional/regional.png';rr=read_json(tile/'regional/generation.json')
    regional=load_native(rp,(1254,1254),rr['sha256'],'regional')
    x,y=(col-1)*1024,(row-1)*1024
    guide=regional.resize((4326,4326),Image.Resampling.BICUBIC).crop((x,y,x+1254,y+1254))
    bands=[]
    def add(side,path,digest,size,box,target):
        im=load_native(path,size,digest,side).crop(box)
        if im.size!=(target[2]-target[0],target[3]-target[1]):raise ValueError('Band size')
        bands.append((im,{'side':side,'file':str(Path(path).resolve()),'sha256':digest,
            'sourceBox':box,'targetBox':target,'nativeSourceResampling':'none'}))
    if col==4:
        meta=ctx['eastExtended'];add('external_east',meta['file'],meta['sha256'],(4326,4326),[0,y,230,y+1254],[1024,0,1254,1254])
    else:
        p=tile/f'native/r{row:02d}_c{col+1:02d}.png'
        rec=read_json(Path(str(p)+'.generation.json'))
        add('east',p,rec['sha256'],(1254,1254),[0,0,230,1254],[1024,0,1254,1254])
    if row==1:
        meta=ctx['northExtended'];add('external_north',meta['file'],meta['sha256'],(4326,4326),[x,4096,x+1254,4326],[0,0,1254,230])
    else:
        p=tile/f'native/r{row-1:02d}_c{col:02d}.png'
        rec=read_json(Path(str(p)+'.generation.json'))
        add('north',p,rec['sha256'],(1254,1254),[0,1024,1254,1254],[0,0,1254,230])
    weights=native_weights(True)
    a=np.array(bands[0][0].crop((115,0,230,115)),dtype=np.int16)
    b=np.array(bands[1][0].crop((1139,0,1254,115)),dtype=np.int16)
    diff=a-b
    constraints=[]
    for im,meta in bands:
        top='north' in meta['side'];box=meta['targetBox']
        alpha=np.broadcast_to(weights[:,None],(230,1254)).copy() if top else np.broadcast_to(weights[::-1][None,:],(1254,230)).copy()
        if top:alpha[115:,1139:]=0
        old=np.array(guide.crop(box),dtype=np.float32);src=np.array(im,dtype=np.float32)
        guide.paste(Image.fromarray(np.rint(src*alpha[:,:,None]+old*(1-alpha[:,:,None])).astype('uint8')),tuple(box[:2]))
        meta.update(guideOnly=True,compositionMode='soft_context',northHasCornerPriority=True)
        constraints.append(meta)
    right_exact=guide.crop((1139,115,1254,1254)).tobytes()==bands[0][0].crop((115,115,230,1254)).tobytes()
    north_exact=guide.crop((0,0,1254,115)).tobytes()==bands[1][0].crop((0,0,1254,115)).tobytes()
    if not (right_exact and north_exact):raise ValueError('Strict native core reference changed')
    constraints[0].update(guaranteedExactFirst115TargetBox=[1139,115,1254,1254],guaranteedExactFirst115PixelsVerified=True)
    constraints[1].update(guaranteedExactFirst115TargetBox=[0,0,1254,115],guaranteedExactFirst115PixelsVerified=True,
                           alphaZeroOverrideTargetBox=[1139,115,1254,230])
    prompt=(f'Use case: precise-object-edit. Produce one opaque full-bleed native1254-square game-map detail for {tile_name}/{cell}. '
        'Image1 gives exact framing, scale and existing object footprints. The TOP115 rows and RIGHTMOST115 columns are native neighbor references: '
        'preserve existing contours, grooves, materials and shadow endpoints at their exact coordinates; north wins the shared top-right corner. '
        'Rows115..229 and columns1024..1138 contain guide-only soft transitions into regional context. Rebuild those into continuous painting; '
        'never copy guide bounds as walls, steps, dark bars, abrupt texture changes or truncated grooves. Reconstruct the soft interior as crisp native detail. '
        'Image2 is the user-approved primary painting/material style: bright, clean, rounded, full-bodied Daoist chibi fantasy with smooth readable bevels '
        'and restrained low-contrast surfaces. Copy no UI, text, symbols, floral ornaments, characters, lighting or objects from Image2. '
        'Keep ONLY objects and materials already present in Image1; no additions, recropping, repositioning, rotation or enlargement. '
        'Quiet ivory stone: no grit, cracks, veins, stains, bright scored scratches, harsh brush patches, blur or sharpening halos. '
        'Rounded clean existing leaves. No new buildings, stairs, medallions, frames, labels or watermark. Return only this single native detail image.')
    style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
    refs=[{'path':str(gp),'role':'Guide-only geometry with exact top/right native core context and soft halo'},
          {'path':str(style),'role':'Approved primary painting/material style; copy no UI or objects'}]
    if not style.is_file():raise FileNotFoundError(style)
    config=read_json(Path('D:/work/image/config/image-generation.json'))
    for p in (gp,pf,jp):destination(p.parent.relative_to(tile)).mkdir(parents=True,exist_ok=True)
    if any(p.exists() for p in protected_paths):raise FileExistsError('Output appeared during preparation')
    save_image(destination(gp.relative_to(tile)),guide);destination(pf.relative_to(tile)).write_text(prompt,encoding='utf-8')
    job={'tileDir':str(tile),'cell':cell,'prompt':prompt,'promptFile':str(pf),'references':refs,
        'configSnapshot':config,
        'generatedAt':datetime.now(timezone.utc).isoformat(),'constraints':constraints,
        'submittedParameters':{'model':None,'quality':None,'transparent_background':False,
                               'referenced_image_paths':[r['path'] for r in refs]},
        'guideDerivation':{'regional':str(rp),'regionalSha256':sha256(rp),'context':str(cp),'contextSha256':sha256(cp),
            'guide':str(gp),'guideSha256':sha256(gp),'guideOnly':True,'cropInExtended':[x,y,x+1254,y+1254],
            'nativeTraversal':'right_to_left_top_to_bottom','nativeSourceResampling':'none',
            'regionalResampling':'BICUBIC to4326; guide only, never final art',
            'contextProfile':{'mode':'smoothstep_halo','northWeights':weights.tolist(),'eastWeights':weights[::-1].tolist(),
                'formula':'Native alpha1 in115px outside-core band, then smoothstep to0 over115px inside core; round-to-nearest uint8',
                'northAlphaOverride':'zero in rows115..229,columns1139..1253 to retain east strict source'},
            'cornerHandling':{'priority':'north','differingPixelCount':int(np.any(diff!=0,axis=2).sum()),
                              'maximumAbsoluteChannelDifference':int(np.abs(diff).max())},
            'finalPixelRestriction':'All final artwork must come from actual builtin native generation, never the composited guide.'}}
    write_json(destination(jp.relative_to(tile)),job);print(json.dumps({'job':str(jp),'references':refs}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('tile');p.add_argument('row',type=int);p.add_argument('col',type=int)
    a=p.parse_args();run(a.tile,a.row,a.col)
