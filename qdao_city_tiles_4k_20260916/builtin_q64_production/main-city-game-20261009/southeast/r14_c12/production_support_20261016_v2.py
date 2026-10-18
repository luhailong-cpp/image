"""Owned r14_c12 production bookkeeping; no image generation or geometry edits."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,importlib.util,sys,hashlib
from PIL import Image
import numpy as np
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent
H=T.parent/'production_workflow_west_extension_20261016_v3_r14.py'
spec=importlib.util.spec_from_file_location('r14_workflow',H);w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
C=T/'native_correction_workflow_20261016_v1_r14.py'
assert hashlib.sha256(C.read_bytes()).hexdigest() == "11e40388fa53af80149171dcddedf2279d47154a950e710c745321648df7b91d"
cspec=importlib.util.spec_from_file_location('r14_native_correction',C);corr=importlib.util.module_from_spec(cspec);cspec.loader.exec_module(corr)
def dispatch_ingest(tile,version,source,receipt):
    if w.read(T/'records'/f'{version}.preparation.json').get('nativeCorrectionOf'):
        return corr.ingest(version,source,receipt)
    return w._ingest_plain(tile,version,source,receipt)
w.ingest=dispatch_ingest
def ingest(version,source):
    source=Path(source).resolve()
    with Image.open(source) as im:
        w.require(im.format=='PNG' and im.size==(1254,1254),'Wrong received native size')
        mode=im.mode
    receipt=T/'records'/f'{version}.receipt.json'
    r={'status':'succeeded_pending_layout_and_seam_review','tool':'image_gen.imagegen','route':'builtin','generatedAt':w.now(),
       'originalOutputPath':str(source),'sourceSha256':w.sha(source),'width':1254,'height':1254,'format':'PNG','mode':mode,
       'actualModel':None,'actualQuality':None,'modelEvidence':'Builtin returned no actual backend model/quality',
       'resizedAfterGeneration':False,'finalArtUpscaled':False}
    w.atomic_json(receipt,r,exclusive=True)
    result=w.ingest('r14_c12',version,source,receipt)
    state=T/'records'/f'{version}.inflight.json'
    if state.exists():
        d=w.read(state);d.update(status='completed_received_ingested_pending_quick_qa',completedAt=w.now());w.atomic_json(state,d)
    return result
def begin(version):
    rules=w.RULES.read_text(encoding='utf-8-sig');split=w.read(w.SPLIT)
    w.tile_parts('r14_c12')
    w.require(rules and not (T/'native'/f'{version}.png').exists(),'Missing rules or native already exists')
    w.validate_preparation(T,version)
    p=T/'records'/f'{version}.inflight.json'
    d={'status':'submitted_to_builtin_pending_result','version':version,'tile':'r14_c12','createdAt':w.now(),
       'tool':'image_gen.imagegen','actualModel':None,'actualQuality':None,
       'rootRulesSha256':w.sha(w.RULES),'splitSha256':w.sha(w.SPLIT),'request':str(T/'records'/f'{version}.request.json')}
    w.atomic_json(p,d,exclusive=True)
    return d
def crops(version):
    prep=w.validate_preparation(T,version)
    with Image.open(T/'native'/f'{version}.png') as im:n=im.convert('RGB')
    outputs=[]
    for a in prep['anchors']:
        with Image.open(a['path']) as im:other=im.convert('RGB')
        d=a['direction'];internal=a['sourceKind']=='active_native_context'
        if d in ('left','right'):
            y0,y1=(0,1254) if internal else (a['target'][1],a['target'][3])
            sy0,sy1=(0,1254) if internal else (a['sourceCrop'][1],a['sourceCrop'][3])
            child=n.crop((115,y0,435,y1)) if d=='left' else n.crop((819,y0,1139,y1))
            if d=='left':
                sx1=1139 if internal else 4096; adjacent=other.crop((sx1-320,sy0,sx1,sy1));parts=[adjacent,child]
            else:
                sx0=115 if internal else 0;adjacent=other.crop((sx0,sy0,sx0+320,sy1));parts=[child,adjacent]
            joined=Image.new('RGB',(640,y1-y0));joined.paste(parts[0],(0,0));joined.paste(parts[1],(320,0))
        else:
            x0,x1=(0,1254) if internal else (a['target'][0],a['target'][2])
            sx0,sx1=(0,1254) if internal else (a['sourceCrop'][0],a['sourceCrop'][2])
            child=n.crop((x0,115,x1,435)) if d=='top' else n.crop((x0,819,x1,1139))
            if d=='top':
                sy1=1139 if internal else 4096;adjacent=other.crop((sx0,sy1-320,sx1,sy1));parts=[adjacent,child]
            else:
                sy0=115 if internal else 0;adjacent=other.crop((sx0,sy0,sx1,sy0+320));parts=[child,adjacent]
            joined=Image.new('RGB',(x1-x0,640));joined.paste(parts[0],(0,0));joined.paste(parts[1],(0,320))
        p=T/'review'/f'{version}-{d}-true-core-join-100pct.png'
        w.write_png_exclusive(p,joined)
        outputs.append({'direction':d,'path':str(p),'sha256':w.sha(p),'size':list(joined.size),'resized':False,
                        'neighbor':a['neighbor'],'neighborSourceSha256':a['sha256']})
    p=T/'records'/f'{version}.quick-review-evidence.json';w.atomic_json(p,outputs,exclusive=True)
    return outputs
def record(version,verdict,notes):
    w.require(verdict in ['quick_pass_pending_block_review','failed_not_for_propagation','pending_nonblocking'],'Invalid quick verdict')
    p=T/'records'/f'{version}.quick-qa.json'
    d={'version':version,'tile':'r14_c12','reviewedAt':w.now(),'reviewer':'assembly_resume actual image inspection',
       'nativeSha256':w.sha(T/'native'/f'{version}.png'),'status':verdict,'notes':notes,'formalAccepted':False,
       'scope':'Actual native framing plus current true neighboring core joins only; full assembled internal review remains pending'}
    w.atomic_json(p,d,exclusive=True)
    return d
def main():
    a=argparse.ArgumentParser();subs=a.add_subparsers(dest='cmd',required=True)
    for name in ['begin','crops']:
        q=subs.add_parser(name);q.add_argument('version')
    q=subs.add_parser('ingest');q.add_argument('version');q.add_argument('source')
    q=subs.add_parser('record');q.add_argument('version');q.add_argument('verdict');q.add_argument('notes')
    args=vars(a.parse_args());cmd=args.pop('cmd');print(json.dumps(globals()[cmd](**args),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
