"""Read-only source verification and in-memory old/new native-guide regression."""
from pathlib import Path
from datetime import datetime, timezone
import contextlib
import hashlib
import io
import json
import sys
import types
from unittest.mock import patch
import numpy as np
from PIL import Image
sys.dont_write_bytecode = True
sys.path.insert(0,str(Path(__file__).parent))
import workflow
import prepare_north_core_east_frontier as partial
import prepare_native_east as current

BASELINE = json.loads(r'''"\"\"\"Prepare guide-only cells right-to-left, using exact north/east native context.\"\"\"\nfrom datetime import datetime,timezone\nfrom pathlib import Path\nimport argparse,json,re\nimport numpy as np\nfrom PIL import Image\nfrom workflow import OUTPUT_ROOT,safe_output,sha256,read_json,write_json,save_image\nfrom prepare_native_frontier import load_native,native_weights\n\ndef run(tile_name,row,col):\n    match=re.fullmatch(r'r(\\d{2})_c(\\d{2})',tile_name)\n    if not match or not (1<=row<=4 and 1<=col<=4):\n        raise ValueError('Invalid tile/cell')\n    tile_row,tile_col=map(int,match.groups())\n    if not (2<=tile_row<=16 and 1<=tile_col<16):raise ValueError('Tile requires valid north/east grid neighbors')\n    tile=safe_output(OUTPUT_ROOT/tile_name);cell=f'r{row:02d}_c{col:02d}'\n    if tile.parent!=OUTPUT_ROOT or tile.name!=tile_name:raise ValueError('Tile output identity mismatch')\n    def destination(relative):\n        path=safe_output(tile/relative)\n        if not path.is_relative_to(tile):raise ValueError('Output escapes requested tile')\n        return path\n    gp=destination(f'guides/{cell}.layout-only.png');pf=destination(f'prompts/{cell}.prompt.txt');jp=destination(f'jobs/{cell}.json')\n    protected_paths=[gp,pf,jp,destination(f'native/{cell}.png')]\n    if any(p.exists() for p in protected_paths):raise FileExistsError(cell)\n    cp=tile/'regional/context.json';ctx=read_json(cp)\n    if ctx.get('nativeTraversal')!='right_to_left_top_to_bottom':raise ValueError('Incorrect traversal context')\n    if ctx.get('tile')!=tile_name or ctx.get('pixelRectXYWH')!=[(tile_col-1)*4096,(tile_row-1)*4096,4096,4096]:\n        raise ValueError('Context tile geometry mismatch')\n    rp=tile/'regional/regional.png';rr=read_json(tile/'regional/generation.json')\n    regional=load_native(rp,(1254,1254),rr['sha256'],'regional')\n    x,y=(col-1)*1024,(row-1)*1024\n    guide=regional.resize((4326,4326),Image.Resampling.BICUBIC).crop((x,y,x+1254,y+1254))\n    bands=[]\n    def add(side,path,digest,size,box,target):\n        im=load_native(path,size,digest,side).crop(box)\n        if im.size!=(target[2]-target[0],target[3]-target[1]):raise ValueError('Band size')\n        bands.append((im,{'side':side,'file':str(Path(path).resolve()),'sha256':digest,\n            'sourceBox':box,'targetBox':target,'nativeSourceResampling':'none'}))\n    if col==4:\n        meta=ctx['eastExtended'];add('external_east',meta['file'],meta['sha256'],(4326,4326),[0,y,230,y+1254],[1024,0,1254,1254])\n    else:\n        p=tile/f'native/r{row:02d}_c{col+1:02d}.png'\n        rec=read_json(Path(str(p)+'.generation.json'))\n        add('east',p,rec['sha256'],(1254,1254),[0,0,230,1254],[1024,0,1254,1254])\n    if row==1:\n        meta=ctx['northExtended'];add('external_north',meta['file'],meta['sha256'],(4326,4326),[x,4096,x+1254,4326],[0,0,1254,230])\n    else:\n        p=tile/f'native/r{row-1:02d}_c{col:02d}.png'\n        rec=read_json(Path(str(p)+'.generation.json'))\n        add('north',p,rec['sha256'],(1254,1254),[0,1024,1254,1254],[0,0,1254,230])\n    weights=native_weights(True)\n    a=np.array(bands[0][0].crop((115,0,230,115)),dtype=np.int16)\n    b=np.array(bands[1][0].crop((1139,0,1254,115)),dtype=np.int16)\n    diff=a-b\n    constraints=[]\n    for im,meta in bands:\n        top='north' in meta['side'];box=meta['targetBox']\n        alpha=np.broadcast_to(weights[:,None],(230,1254)).copy() if top else np.broadcast_to(weights[::-1][None,:],(1254,230)).copy()\n        if top:alpha[115:,1139:]=0\n        old=np.array(guide.crop(box),dtype=np.float32);src=np.array(im,dtype=np.float32)\n        guide.paste(Image.fromarray(np.rint(src*alpha[:,:,None]+old*(1-alpha[:,:,None])).astype('uint8')),tuple(box[:2]))\n        meta.update(guideOnly=True,compositionMode='soft_context',northHasCornerPriority=True)\n        constraints.append(meta)\n    right_exact=guide.crop((1139,115,1254,1254)).tobytes()==bands[0][0].crop((115,115,230,1254)).tobytes()\n    north_exact=guide.crop((0,0,1254,115)).tobytes()==bands[1][0].crop((0,0,1254,115)).tobytes()\n    if not (right_exact and north_exact):raise ValueError('Strict native core reference changed')\n    constraints[0].update(guaranteedExactFirst115TargetBox=[1139,115,1254,1254],guaranteedExactFirst115PixelsVerified=True)\n    constraints[1].update(guaranteedExactFirst115TargetBox=[0,0,1254,115],guaranteedExactFirst115PixelsVerified=True,\n                           alphaZeroOverrideTargetBox=[1139,115,1254,230])\n    prompt=(f'Use case: precise-object-edit. Produce one opaque full-bleed native1254-square game-map detail for {tile_name}/{cell}. '\n        'Image1 gives exact framing, scale and existing object footprints. The TOP115 rows and RIGHTMOST115 columns are native neighbor references: '\n        'preserve existing contours, grooves, materials and shadow endpoints at their exact coordinates; north wins the shared top-right corner. '\n        'Rows115..229 and columns1024..1138 contain guide-only soft transitions into regional context. Rebuild those into continuous painting; '\n        'never copy guide bounds as walls, steps, dark bars, abrupt texture changes or truncated grooves. Reconstruct the soft interior as crisp native detail. '\n        'Image2 is the user-approved primary painting/material style: bright, clean, rounded, full-bodied Daoist chibi fantasy with smooth readable bevels '\n        'and restrained low-contrast surfaces. Copy no UI, text, symbols, floral ornaments, characters, lighting or objects from Image2. '\n        'Keep ONLY objects and materials already present in Image1; no additions, recropping, repositioning, rotation or enlargement. '\n        'Quiet ivory stone: no grit, cracks, veins, stains, bright scored scratches, harsh brush patches, blur or sharpening halos. '\n        'Rounded clean existing leaves. No new buildings, stairs, medallions, frames, labels or watermark. Return only this single native detail image.')\n    style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')\n    refs=[{'path':str(gp),'role':'Guide-only geometry with exact top/right native core context and soft halo'},\n          {'path':str(style),'role':'Approved primary painting/material style; copy no UI or objects'}]\n    if not style.is_file():raise FileNotFoundError(style)\n    config=read_json(Path('D:/work/image/config/image-generation.json'))\n    for p in (gp,pf,jp):destination(p.parent.relative_to(tile)).mkdir(parents=True,exist_ok=True)\n    if any(p.exists() for p in protected_paths):raise FileExistsError('Output appeared during preparation')\n    save_image(destination(gp.relative_to(tile)),guide);destination(pf.relative_to(tile)).write_text(prompt,encoding='utf-8')\n    job={'tileDir':str(tile),'cell':cell,'prompt':prompt,'promptFile':str(pf),'references':refs,\n        'configSnapshot':config,\n        'generatedAt':datetime.now(timezone.utc).isoformat(),'constraints':constraints,\n        'submittedParameters':{'model':None,'quality':None,'transparent_background':False,\n                               'referenced_image_paths':[r['path'] for r in refs]},\n        'guideDerivation':{'regional':str(rp),'regionalSha256':sha256(rp),'context':str(cp),'contextSha256':sha256(cp),\n            'guide':str(gp),'guideSha256':sha256(gp),'guideOnly':True,'cropInExtended':[x,y,x+1254,y+1254],\n            'nativeTraversal':'right_to_left_top_to_bottom','nativeSourceResampling':'none',\n            'regionalResampling':'BICUBIC to4326; guide only, never final art',\n            'contextProfile':{'mode':'smoothstep_halo','northWeights':weights.tolist(),'eastWeights':weights[::-1].tolist(),\n                'formula':'Native alpha1 in115px outside-core band, then smoothstep to0 over115px inside core; round-to-nearest uint8',\n                'northAlphaOverride':'zero in rows115..229,columns1139..1253 to retain east strict source'},\n            'cornerHandling':{'priority':'north','differingPixelCount':int(np.any(diff!=0,axis=2).sum()),\n                              'maximumAbsoluteChannelDifference':int(np.abs(diff).max())},\n            'finalPixelRestriction':'All final artwork must come from actual builtin native generation, never the composited guide.'}}\n    write_json(destination(jp.relative_to(tile)),job);print(json.dumps({'job':str(jp),'references':refs}))\n\nif __name__=='__main__':\n    p=argparse.ArgumentParser();p.add_argument('tile');p.add_argument('row',type=int);p.add_argument('col',type=int)\n    a=p.parse_args();run(a.tile,a.row,a.col)\n\r\n"''')
BASELINE=BASELINE.removesuffix('\r\n')  # Remove only Get-Content's added output terminator.
assert hashlib.sha256(BASELINE.encode()).hexdigest()=='d627d12968e62812447f4627419c57e6886059ab1c97aaf338d3e8229c0edd75'
old = types.ModuleType('historical_native_east')
exec(compile(BASELINE,'historical_native_east','exec'),old.__dict__)
root = workflow.OUTPUT_ROOT
aud = root/'preflight/r09_c08-source-audit.json'
band, known, north_core, north_meta, mappings, audit_meta = partial.audited_north_band('r09_c08',aud)
assert band.size == (4326,115)
assert all(m['pixelIdentityVerified'] for m in mappings)
assert np.all(np.asarray(known)[:115] == 255) and np.all(np.asarray(known)[115:] == 0)

def pattern(width,height,offset):
    yy,xx=np.indices((height,width),dtype=np.uint16)
    return Image.fromarray(np.stack(((xx+offset)%256,(yy+offset*2)%256,(xx//13+yy//19+offset*3)%256),axis=2).astype('uint8'))
images = {'regional':pattern(1254,1254,5),'native':pattern(1254,1254,37),
          'extended':pattern(4326,4326,79)}
tile_name='r16_c14'
tile=root/tile_name
meta={'file':str(root/'tools/in_memory_extended.png'),'sha256':'extended-hash'}
context={'nativeTraversal':'right_to_left_top_to_bottom','tile':tile_name,
         'pixelRectXYWH':[13*4096,15*4096,4096,4096],
         'eastExtended':meta,'northExtended':meta}
mask_path=root/'tools/in_memory_known_mask.png'
partial_context=dict(context)
partial_context.pop('northExtended')
partial_context.update(northContextKind='partial_core_band',
    northCoreBand={'file':str(root/'tools/in_memory_north_band.png'),'sha256':'band-hash',
                   'pixels':[4326,115],'sourceMappings':mappings},
    northKnownMask={'file':str(mask_path),'sha256':'mask-hash','pixels':[4326,230],
                    'knownBoxXYXY':[0,0,4326,115],'unknownBoxXYXY':[0,115,4326,230]})
real_open=Image.open
def mocked_open(path,*args,**kwargs):
    if Path(path)==mask_path:
        copy=known.copy();copy.format='PNG'
        return copy
    return real_open(path,*args,**kwargs)

def simulate(module,row,col,ctx):
    captured={}
    def read_json(path):
        p=str(path)
        if p.endswith('context.json'):return ctx
        if p.endswith('image-generation.json'):return {'model':'test-target','quality':'test'}
        return {'sha256':'native-hash'}
    def load_native(path,size,digest,label):
        if size==(4326,115):return band.copy()
        if size==(4326,4326):return images['extended'].copy()
        return images['regional' if label=='regional' else 'native'].copy()
    def save_image(path,image):
        captured['guide']=image.copy()
        return {'file':str(path),'sha256':hashlib.sha256(image.tobytes()).hexdigest()}
    def write_json(path,value):captured['job']=value
    def fake_hash(path):return 'mask-hash' if Path(path)==mask_path else 'test-file-hash'
    with patch.object(module,'read_json',read_json),patch.object(module,'load_native',load_native), \
         patch.object(module,'save_image',save_image),patch.object(module,'write_json',write_json), \
         patch.object(module,'sha256',fake_hash),patch.object(Path,'exists',return_value=False), \
         patch.object(Path,'mkdir'),patch.object(Path,'write_text'), \
         patch.object(Path,'resolve',lambda self,*args,**kwargs:self.absolute()), \
         patch.object(Image,'open',mocked_open),contextlib.redirect_stdout(io.StringIO()):
        module.run(tile_name,row,col)
    return captured

regressions=[]
for row,col in [(1,1),(1,2),(1,3),(1,4),(2,4),(4,1)]:
    before,after=simulate(old,row,col,context),simulate(current,row,col,context)
    assert before['guide'].tobytes()==after['guide'].tobytes()
    for record in (before['job'],after['job']):record.pop('generatedAt')
    assert before['job']==after['job']
    regressions.append({'cell':f'r{row:02d}_c{col:02d}','guidePixelsIdentical':True,'jobMetadataIdenticalExceptTimestamp':True,
                        'rawGuideRgbSha256':hashlib.sha256(after['guide'].tobytes()).hexdigest()})
partial_checks=[]
for col in range(1,5):
    new=simulate(current,1,col,partial_context)
    x=(col-1)*1024
    assert new['guide'].crop((0,0,1254,115)).tobytes()==band.crop((x,0,x+1254,115)).tobytes()
    east=images['extended'].crop((0,0,230,1254)) if col==4 else images['native'].crop((0,0,230,1254))
    assert new['guide'].crop((1139,115,1254,1254)).tobytes()==east.crop((115,115,230,1254)).tobytes()
    guide_before=images['regional'].resize((4326,4326),Image.Resampling.BICUBIC).crop((x,0,x+1254,1254))
    assert new['guide'].crop((0,115,1024,230)).tobytes()==guide_before.crop((0,115,1024,230)).tobytes()
    weights=new['job']['guideDerivation']['contextProfile']['northWeights']
    assert weights==[1.0]*115+[0.0]*115
    assert 'ZERO north native weight' in new['job']['prompt']
    partial_checks.append({'cell':f'r01_c{col:02d}','north115Exact':True,'eastStrictBelow115Exact':True,
                           'missingNorthHaloPreservesRegionalGuideOutsideEastBand':True,'missingNorthAlphaExactlyZero':True})
# All rows beyond the first reuse generated north cells, irrespective of external north kind.
full=simulate(current,2,4,context)
part=simulate(current,2,4,partial_context)
assert full['guide'].tobytes()==part['guide'].tobytes()
for record in (full['job'],part['job']):record.pop('generatedAt')
assert full['job']==part['job']
for invalid in ('../r09_c08','r09_c01','r01_c08','r09_c16'):
    try:partial.tile_coordinates(invalid)
    except ValueError:pass
    else:raise AssertionError('Invalid tile accepted')
# Missing production east input must fail before writing any output directory.
args=types.SimpleNamespace(tile='r09_c08',north_source_audit=str(aud),
                           east_extended=str(root/'tools/definitely_missing_east.png'),
                           east_core=str(root/'tools/definitely_missing_east_core.png'))
with patch.object(Path,'mkdir') as mkdir:
    try:partial.run(args)
    except FileNotFoundError:pass
    else:raise AssertionError('Missing source accepted')
    assert not mkdir.called
# Existing regional path must reject before input loading or mutation.
with patch.object(Path,'exists',return_value=True),patch.object(Path,'mkdir') as mkdir:
    try:partial.run(args)
    except FileExistsError:pass
    else:raise AssertionError('Existing output accepted')
    assert not mkdir.called

result={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
    'scope':'Tools only: read-only source inspection and in-memory guide validation. No r09_c08 directory or production image created.',
    'sourceAudit':audit_meta,'northBand':{'pixels':[4326,115],'rawRgbPixelSha256':partial.rgb_hash(band),
        'mappings':mappings,'written':False},'knownMask':{'pixels':[4326,230],'first115':255,'last115':0,'written':False},
    'historicalNativeToolSha256':hashlib.sha256(BASELINE.encode()).hexdigest(),
    'legacyRegression':regressions,'partialFirstRowChecks':partial_checks,'laterRowsBehaviorUnchanged':True,
    'inputFailureBeforeWritesVerified':True,'noOverwriteBeforeWritesVerified':True,'invalidTileNamesRejected':True,
    'productionTileCreated':False,'nativeGenerationPerformed':False,
    'toolFiles':[{ 'file':str(p),'sha256':workflow.sha256(p)} for p in (
        root/'tools/prepare_north_core_east_frontier.py',root/'tools/prepare_native_east.py',root/'tools/verify_north_core_east.py')],
    'productionExecutionStatus':'Not run; await qualified r09_c09 selected east pair and root review.',
    'invocation':['prepare_north_core_east_frontier.py','r09_c08','--north-source-audit','preflight/r09_c08-source-audit.json',
        '--east-extended','r09_c09/selected/extended4326.png','--east-core','r09_c09/selected/core4096.png'],
    'limitations':['Read-only real core pixel construction was verified in memory; no regional or native AI generation or visual seam acceptance performed.',
        'Known mask deliberately records all lower115 north rows as unknown, even where independent east context exists.'] }
workflow.write_json(root/'preflight/north-core-east-tool-audit.json',result)
print(json.dumps({'audit':str(root/'preflight/north-core-east-tool-audit.json'),'legacyCases':len(regressions),
                  'partialCases':len(partial_checks),'createdProductionTile':False}))

