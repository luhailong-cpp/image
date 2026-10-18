import sys
sys.dont_write_bytecode=True
import json,hashlib,re,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parent.parent;Q=Z/'qa';N=Z/'native';REPO=Z.parents[3];TILE='r12_c02'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p,role=None):
    d={'path':Path(p).as_posix(),'sha256':sha(p)}
    if role:d['role']=role
    return d
def save(p,d):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def rules():
    out=[]
    for name,known in [('AGENTS.md','57f1ad4f81fdb2256b843923d862308be228130917b99cfced375db256aff01a'),('docs/MAP_PARALLEL_SPLIT_20261013.json','929a52abdb55e6022f83abbe9b48718182bc33fc8a0bc2d50a14f6232dd4e850')]:
        p=REPO/name;content=p.read_text(encoding='utf-8-sig')
        if sha(p)!=known:print(content);raise SystemExit('Rules changed: review before continuing')
        out.append({**ref(p),'readAtUtc':datetime.now(timezone.utc).isoformat()})
    assert TILE not in [t for b in read(REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json')['batches'] if b['map']=='fishing-village-game-20261009' and b['status']=='allocated_root_reserved' for t in b['tiles']]
    return out
mode=sys.argv[1]
if mode=='prepare':
    patchid=sys.argv[2];version=sys.argv[3] if len(sys.argv)>3 else 'v1';stem=f'{TILE}_{patchid}_{version}'
    for ext in ['.request.json','.png','.receipt.json']:assert not (N/(stem+ext)).exists(),stem+' exists, recover rather than duplicate'
    guard=rules();tile=next(t for t in read(Z/'coordinate-plan.json')['tiles'] if t['tile']==TILE);patch=next(p for p in tile['patches'] if p['id']==patchid);box=patch['globalContextBox'];refs=read(Z/'references.json')
    with Image.open(refs[0]['path']) as im:
        for dest,gbox in [(Q/(TILE+'-layout-only-v1.png'),tile['globalCoreBox']),(Q/(stem+'-layout-only.png'),box)]:
            if not dest.exists():
                im.transform((1254,1254),Image.Transform.EXTENT,[v*1254/57344 for v in gbox],resample=Image.Resampling.NEAREST).save(dest)
                save(Path(str(dest)+'.derivation.json'),{'role':'coordinate layout guide only; not final game pixels','source':ref(refs[0]['path']),'globalBox':gbox,'operation':'nearest enlarged layout crop'})
    canvas=Image.open(Q/(stem+'-layout-only.png')).convert('RGB');sources=[];latest={}
    for rp in N.glob(TILE+'_p*_v*.png.generation.json'):
        m=re.fullmatch(TILE+r'_(p\d\d_\d\d)_v(\d+)\.png\.generation\.json',rp.name)
        if not m:continue
        r=read(rp)
        if any(s in r.get('status','') for s in ['superseded','rejected','frozen']):continue
        if m[1]==patchid:continue
        if m[1] not in latest or int(m[2])>latest[m[1]][0]:latest[m[1]]=(int(m[2]),r)
    for _,r in latest.values():sources.append({'path':r['file'],'sha256':r['sha256'],'box':r['coordinates']['globalContextBox'],'role':'current own native adjacent patch'})
    north=next(x for x in read(Z/'art-delivery-index.json')['artAccepted'] if x['tile']=='r11_c02')
    sources.append({**north['nativeContext'],'box':[3981,40845,8307,45171],'role':'accepted current north context','tile':'r11_c02','audit':north['artAudit'],'trace':north['sourceTrace']})
    overlaps=[]
    for s in sources:
        b=s['box'];i=[max(box[0],b[0]),max(box[1],b[1]),min(box[2],b[2]),min(box[3],b[3])]
        if i[2]<=i[0] or i[3]<=i[1]:continue
        assert i[2]-i[0]<=230 or i[3]-i[1]<=230
        assert sha(s['path'])==s['sha256']
        with Image.open(s['path']) as im:canvas.paste(im.crop((i[0]-b[0],i[1]-b[1],i[2]-b[0],i[3]-b[1])),(i[0]-box[0],i[1]-box[1]))
        overlaps.append({**s,'globalOverlapBox':i,'targetBox':[i[0]-box[0],i[1]-box[1],i[2]-box[0],i[3]-box[1]]})
    guide=Q/(stem+'-continuity.png');canvas.save(guide)
    save(Path(str(guide)+'.derivation.json'),{'role':'mixed guide with protected native overlap; enlarged layout only elsewhere','baseGuide':ref(Q/(stem+'-layout-only.png')),'overlaps':overlaps,'operation':'integer native crop/paste; no native resizing or drawing'})
    req={'stem':stem,'tile':TILE,'patch':patchid,'coordinates':patch,'references':[ref(guide,'edit target; exact coordinate layout and protected native overlap'),*refs],'overlaps':overlaps,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'guardrailRead':guard,'eastBoundary':'r12_c03 external reserved; no unaccepted unstable source used'}
    save(N/(stem+'.request.json'),req)
    print(json.dumps({'stem':stem,'guide':guide.as_posix(),'overlaps':[{'file':Path(s['path']).name,'targetBox':s['targetBox']} for s in overlaps],'rulesReRead':[s['sha256'] for s in guard]},ensure_ascii=False))
elif mode=='record':
    stem=sys.argv[2];src=Path(sys.argv[3]);p=N/(stem+'.png');assert not p.exists();assert src.is_file();shutil.copyfile(src,p)
    req=read(N/(stem+'.request.json'));prompt=N/(stem+'.prompt.txt');assert prompt.is_file()
    with Image.open(p) as im:
        assert im.size==(1254,1254);assert im.mode in ('RGB','RGBA')
        if im.mode=='RGBA':assert im.getextrema()[3]==(255,255)
        keys=list(im.info.keys())
    receipt={'finishedAtUtc':datetime.now(timezone.utc).isoformat(),'tool':'image_gen__imagegen','sourceSavedPath':src.as_posix(),'file':ref(p),'actualModel':None,'actualQuality':None,'modelEvidence':'Actual model not returned by built-in tool','paidApiUsed':False}
    save(N/(stem+'.receipt.json'),receipt)
    generation={'file':p.as_posix(),'sha256':sha(p),'generatedAt':receipt['finishedAtUtc'],'width':1254,'height':1254,'format':'PNG','tool':'image_gen__imagegen','route':'builtin','submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Tool did not return actual model or quality','prompt':prompt.as_posix(),'references':req['references'],'coordinates':req['coordinates'],'status':'candidate_pending_seam_qa','nativePixelsResampled':False,'receipt':ref(N/(stem+'.receipt.json')),'pngMetadataKeys':keys}
    save(Path(str(p)+'.generation.json'),generation);print(json.dumps({'file':p.as_posix(),'sha256':sha(p),'size':[1254,1254]}))
else:raise SystemExit('unknown mode')
