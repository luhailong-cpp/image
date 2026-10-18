"""Two reserved island tiles: exact native guides, ingestion and pixel assembly."""
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime, timezone
import sys, json, hashlib, argparse, shutil
sys.dont_write_bytecode = True
from PIL import Image
import numpy as np

B = Path(__file__).resolve().parent
ROOT = B.parents[3]
MAP = ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009'
NW = MAP/'northwest'
sys.path.insert(0, str(NW))
import prepare_zone_patch as prep
import assemble_connected_tiles as connected
import assemble_tile as assembly

def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p): return {'path':Path(p).as_posix(),'sha256':sha(p)}
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
    p=Path(p); assert p.resolve().is_relative_to(B)
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f: json.dump(d,f,ensure_ascii=False,indent=2); f.write('\n')
    return info(p)
def save(p,im):
    p=Path(p); assert p.resolve().is_relative_to(B)
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f: im.save(f,format='PNG')
    return {**info(p),'nativeSize':list(im.size)}
def progress():
    data=read(B/'selected.json');sources=data['sources'];tiles={}
    for tile in ['r04_c01','r05_c01']:
        items={k:v for k,v in sources.items() if k.startswith(tile)}
        eligible=[k for k,v in items.items() if v['quickQA'] in ('layout_and_edges_passed','layout_passed_seams_pending')]
        tiles[tile]={'requiredCores':16,'rawVersions':len(items),'nativeSlotsWithAnyVersion':len(set(k.rsplit('_',1)[0] for k in items)),'layoutSelectedUniqueCores':len(set(k.rsplit('_',1)[0] for k in eligible)),'pendingInternalRepairs':[k for k,v in items.items() if v['quickQA']=='layout_passed_seams_pending'],'candidate4096':str(B/'tiles'/f'{tile}-candidate-v1-4096.png') if (B/'tiles'/f'{tile}-candidate-v1-4096.png').exists() else None,'internalQAPassed':False,'formalAccepted':False}
    (B/'progress.json').write_text(json.dumps({'updatedAtUtc':now(),'scope':'two reserved tiles only','status':'native_production_in_progress','builtinOnly':True,'actualModel':'not returned','extraPaidApiUsed':False,'rawVersionCount':len(sources),'tiles':tiles,'formalAcceptedCount':0},indent=2)+'\n',encoding='utf8')
def check():
    rules=ROOT/'AGENTS.md'; rule_text=rules.read_text(encoding='utf-8-sig'); assert '2.0' in rule_text and 'allocated_root_reserved' in rule_text
    split=read(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json')
    mine=[x for x in split['batches'] if x['key']=='island_more_20261016']; assert len(mine)==1
    assert mine[0]['tiles']==['r04_c01','r05_c01'] and mine[0]['status']=='allocated_root_reserved'
    assert (ROOT/mine[0]['outputDirectory']).resolve()==B
    conflicts=[str(p) for p in B.rglob('*CONFLICT*') if p.is_file()]; assert not conflicts, conflicts
    return {'rules':info(rules),'allocation':info(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json'),'checkedAtUtc':now(),'conflictFiles':[]}

def anchors():
    audit=check(); records=[]
    for tr,ver,expected in [(4,9,'2c846183dfad3630e5640d54b606e1e8e3353f3d0f8dd2a3c1689d93f09368de'),(5,5,'b528be1523f24174a0c940fcbfaa2b54ddf21adcc7ff36768ff7e3cd05142a98')]:
        image=NW/f'tiles/r{tr:02d}_c02_candidate-v{ver}_4096.png'; record=image.with_suffix('.native-repair.json')
        assert sha(image)==expected
        padded,proof=connected.reconstruct_padded(image,record)
        for sr in range(1,5):
            box=[0,(sr-1)*1024,1254,(sr-1)*1024+1254]
            out=B/f'references/east_r{tr:02d}_c02_v{ver}_s{sr:02d}_01.png'
            value=save(out,Image.fromarray(padded[box[1]:box[3],box[0]:box[2]]))
            value.update({'tile':f'r{tr:02d}_c01','subrow':sr,'role':'east neighbor current formal core115px; original verified halo only outside formal core','sourceProof':proof,'paddedCropBox':box,'resized':False,'isAiGeneration':False})
            write(out.with_suffix('.derivation.json'),value); records.append(value)
    write(B/'references/east-anchors.json',{'anchors':records,'preflight':audit})
    print(json.dumps({'status':'eight east anchors verified and saved','count':len(records)}))

def selected(slot):
    data=read(B/'selected.json') if (B/'selected.json').exists() else {'sources':{}}
    values=[k for k,v in data['sources'].items() if k.rsplit('_',1)[0]==slot and v['quickQA'] in ('layout_and_edges_passed','layout_passed_seams_pending')]
    assert len(values)==1, (slot,values)
    return values[0]

def prepare(tile,sr,sc,attempt,note=''):
    audit=check(); tr=int(tile[1:3]); assert tile in ('r04_c01','r05_c01')
    stem=f'{tile}_s{sr:02d}_{sc:02d}_{attempt}'
    prep.ZONE=B; prep.MAP_ROOT=MAP
    orig_read=prep.read
    def current_contract(p):
        value=orig_read(p)
        if Path(p)==MAP/'production-contract.json': value['primaryStyleReference']=str(ROOT/'designs/mail-ui-v1/01-mail-event.png')
        return value
    prep.read=current_contract
    orig_zone=prep.source_zone
    prep.source_zone=lambda contract,r,c: B if (r,c) in [(4,1),(5,1)] else orig_zone(contract,r,c)
    orig_load=prep.load_neighbor
    def load(name,direction,target,contract):
        if name!='fixed-east': return orig_load(name,direction,target,contract)
        record=next(x for x in read(B/'references/east-anchors.json')['anchors'] if x['tile']==tile and x['subrow']==sr)
        assert sha(record['path'])==record['sha256']; b=target['globalBox']
        record={**record,'direction':'right','sourceZone':'northwest','sourceCrop':[115,0,230,1254],'destination':[1139,0],'targetLocalBox':[1139,0,1254,1254],'globalOverlapBox':[b[0]+1139,b[1],b[2],b[3]],'resized':False,'sameTile':False}
        return record,Image.open(record['path']).convert('RGB')
    prep.load_neighbor=load
    # Column-by-column east to west, each column north to south across both tiles.
    right='fixed-east' if sc==4 else selected(f'{tile}_s{sr:02d}_{sc+1:02d}')
    if sr>1: top=selected(f'{tile}_s{sr-1:02d}_{sc:02d}')
    elif tr==5: top=selected(f'r04_c01_s04_{sc:02d}')
    else: top=f'r03_c01_s04_{sc:02d}_a01'
    for name in (right,top):
        if name!='fixed-east':
            owner=B if name.startswith(('r04_c01','r05_c01')) else NW
            assert (owner/'native'/f'{name}.png').is_file(), name
    result=prep.prepare(SimpleNamespace(tile_row=tr,tile_col=1,subrow=sr,subcol=sc,attempt=attempt,left=None,right=right,top=top,bottom=None,output_dir=str(B/'guides')))
    inputs=read(result['input']['path'])
    guide=Image.open(result['guide']['path']).convert('RGB')
    boundary=save(B/'guides'/f'{stem}.right-boundary-only.png',guide.crop((1139 if sc==4 else 1024,0,1254,1254)))
    boundary.update({'role':'right native boundary strip ONLY, unresized crop of image1; never copy other neighbor context','isAiGeneration':False,'derivedFrom':result['guide'],'cropBox':[1139 if sc==4 else 1024,0,1254,1254]})
    actual_inputs=inputs['inputs'][:4]+[boundary]
    write(B/'guides'/f'{stem}.submitted-references.json',actual_inputs)
    prompt=('Use case: stylized-concept. Generate one opaque native 1254x1254 PNG. Image1 is the EXACT coordinate/framing guide: redraw its blurred layout center into crisp genuine hand-painted native detail, preserve the sharp RIGHT and TOP native strips at their exact pixel placement, scale, silhouette, color, lighting, and intersecting geometry. Image2 is approved global island layout ONLY; image3 is approved independent material/detail reference ONLY; image4 is Daoist Q hand-painted style ONLY (no UI/night/characters); image5 contains the unresized native neighbors, left panel=right and right panel=top. Maintain the SAME fixed isometric camera and world scale. This patch is at the far WEST outer coast of the approved island. Follow image1 exactly for ocean, rock, foam, foliage and any wall boundary: do not invent structures, extra rocks, land, trees or decorative items in open water. Ocean is bright turquoise with softly painted layered ripples and white foam only where the existing shore demands. Existing rocks stay rounded natural pale grey/cyan with painterly forms; existing plants stay jade-green, pink and warm golden accents only where present. Daylight, refined rounded Daoist Q illustration, consistent with adjacent natives. No NPC, person, lettering, UI, grid, watermark, artificial rectangular boundaries, photo realism, plastic toy highlight, blur, enlarged guide pixels or procedural repeated texture. Every new center pixel must be truly rendered native detail. Preserve the approved coast silhouette and do not enlarge the island. Output exact1254 square; 1024 central core plus115 halo all around.')
    prompt=prompt.replace('image5 contains the unresized native neighbors, left panel=right and right panel=top.','image5 is ONLY the unresized right boundary strip already located at the far right of image1. No surrounding neighbor scene is part of this patch.')
    prompt=prompt.replace('preserve the sharp RIGHT and TOP native strips at their exact pixel placement, scale, silhouette, color, lighting, and intersecting geometry.','retain the precise geometry, silhouettes, world scale, colors and lighting of the sharp TOP and RIGHT reference edges. The outer115px top and right halos anchor the neighbor. Repaint the inner115px of those strips as necessary to make individual leaves, branches, foam or rock shapes flow continuously into the new center; do NOT paste a rectangular reference panel. The transition at y230 and x1024/1139 is NOT an object edge and must be invisible. Render the whole image as one coherent painting.')
    prompt += ' The center layout shapes and land/water occupancy in image1 override surrounding context in every other reference. Do not extend sea into green/yellow blurred land regions or repeat nearby architecture. ' + note
    write(B/'prompts'/f'{stem}.prompt.json',{'prompt':prompt,'preflight':audit})
    p=B/'prompts'/f'{stem}.txt'
    with p.open('x',encoding='utf8') as f:f.write(prompt+'\n')
    out={'stem':stem,'prompt':prompt,'promptFile':str(p),'references':info(B/'guides'/f'{stem}.submitted-references.json'),'input':result['input'],'paths':[i['path'] for i in actual_inputs],'guide':result['guide']['path']}
    write(B/'requests'/f'{stem}.json',out)
    print(json.dumps(out,ensure_ascii=False))

def ingest(stem,source):
    request=read(B/'requests'/f'{stem}.json'); inputs=read(request['input']['path']); source=Path(source)
    with Image.open(source) as im: assert im.size==(1254,1254) and im.format=='PNG',(im.size,im.format)
    dest=B/'native'/f'{stem}.png'; dest.parent.mkdir(parents=True,exist_ok=True)
    with source.open('rb') as r,dest.open('xb') as w:shutil.copyfileobj(r,w)
    assert sha(dest)==sha(source)
    receipt=write(B/'receipts'/f'{stem}.json',{'tool':'image_gen.imagegen','route':'builtin','savedAtUtc':now(),'submitted':{'promptFile':request['promptFile'],'prompt':request['prompt'],'referenced_image_paths':request['paths'],'transparent_background':False},'returnedSource':info(source),'actualModel':None,'actualQuality':None,'modelEvidence':'not returned by built-in tool','rawReceiptFile':str(B/'receipts'/f'{stem}.tool.json')})
    gen={'file':str(dest),'sha256':sha(dest),'generatedAt':now(),'nativeWidth':1254,'nativeHeight':1254,'format':'PNG','sourceOutputPath':str(source),'sourceOutputSha256':sha(source),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':None,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Built-in tool did not return model/quality; free2.5 preferred or existing2.0 allowed.','prompt':request['promptFile'],'promptSha256':sha(request['promptFile']),'references':read(request['references']['path']),'globalBox':inputs['globalBox'],'coreBox':inputs['coreBox'],'resizedAfterGeneration':False,'finalArtUpscaled':False,'evidence':{'receipt':receipt['path']},'status':'candidate_pending_quick_visual_check'}
    write(dest.with_suffix('.png.generation.json'),gen)
    selection_path=B/'selected.json'; selection=read(selection_path) if selection_path.exists() else {'sources':{},'formalAccepted':False}
    assert stem not in selection['sources']; selection['sources'][stem]={**info(dest),'generationRecord':info(dest.with_suffix('.png.generation.json')),'quickQA':'pending'}
    if selection_path.exists():
        history=B/'selections'/f'selected-before-{stem}.json'; write(history,selection)
        selection_path.write_text(json.dumps(selection,indent=2)+'\n',encoding='utf8')
    else:write(selection_path,selection)
    progress()
    print(json.dumps({'saved':str(dest),'size':[1254,1254],'rawVersionCount':len(selection['sources']),'uniqueNativeSlots':len(set(k.rsplit('_',1)[0] for k in selection['sources'])),'selectedUsableCoreCount':sum(v['quickQA']=='layout_and_edges_passed' for v in selection['sources'].values())}))

def review(stem,status,note):
    data=read(B/'selected.json');assert stem in data['sources']
    assert status in ['layout_and_edges_passed','layout_passed_seams_pending','rejected_layout','pending_repairs']
    data['sources'][stem]['quickQA']=status;data['sources'][stem]['note']=note
    write(B/'qa'/f'{stem}-quick-review.json',{'stem':stem,'image':info(B/'native'/f'{stem}.png'),'status':status,'note':note,'checkedAtUtc':now(),'internalSeamQA':'not_yet_performed','formalAccepted':False})
    (B/'selected.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf8')
    progress()
    print(json.dumps({'stem':stem,'status':status,'selectedUsableCoreCount':sum(v['quickQA']=='layout_and_edges_passed' for v in data['sources'].values())}))

def note_request(stem,note):
    p=B/'requests'/f'{stem}.json';data=read(p)
    assert not (B/'native'/f'{stem}.png').exists()
    marker='Do not extend sea into green/yellow blurred land regions or repeat nearby architecture. '
    data['prompt']=data['prompt'].split(marker)[0]+marker+'CRITICAL LOCAL CONTENT: '+note
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    Path(data['promptFile']).write_text(data['prompt']+'\n',encoding='utf8')
    write(B/'prompts'/f'{stem}-local-note.json',{'prompt':data['prompt'],'note':note})

def assemble(tile):
    check(); matrix=[]
    for sr in range(1,5):
        row=[]
        for sc in range(1,5):
            p=B/'native'/f'{selected(f"{tile}_s{sr:02d}_{sc:02d}")}.png'
            row.append({**info(p),'generationRecord':str(p.with_suffix('.png.generation.json'))})
        matrix.append(row)
    manifest=B/'manifests'/f'{tile}-v1.json'
    write(manifest,{'schemaVersion':1,'tileId':tile,'nativePixels':1254,'corePixels':1024,'haloPixels':115,'patchMatrix':matrix})
    assembly.ZONE=B;assembly.NATIVE=B/'native'
    sys.argv=['assemble_tile.py','--manifest',str(manifest),'--output',str(B/'tiles'/f'{tile}-candidate-v1-4096.png')]
    assembly.main()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['anchors','prepare','ingest','assemble','review','note']);p.add_argument('--tile');p.add_argument('--row',type=int);p.add_argument('--col',type=int);p.add_argument('--attempt',default='a01');p.add_argument('--stem');p.add_argument('--source');p.add_argument('--note',default='');p.add_argument('--status');a=p.parse_args()
    if a.command=='anchors':anchors()
    elif a.command=='prepare':prepare(a.tile,a.row,a.col,a.attempt,a.note)
    elif a.command=='ingest':ingest(a.stem,a.source)
    elif a.command=='review':review(a.stem,a.status,a.note)
    elif a.command=='note':note_request(a.stem,a.note)
    else:assemble(a.tile)
