from pathlib import Path
import sys, json, subprocess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import production as p
ROOT=p.ROOT
cmd,stem=sys.argv[1:3]
if cmd=='configure':
    config=json.loads(Path(sys.argv[3]).read_text(encoding='utf-8-sig'))
    reqpath=ROOT/'prompts'/f'{stem}.request.json'; req=p.load(reqpath)
    pp=ROOT/'prompts'/f'{stem}.prompt.txt'
    assert not pp.exists()
    pp.write_text(config['prompt'],encoding='utf-8')
    req.update(stem=stem,prompt=config['prompt'],promptPath=str(pp),promptSha256=p.hashfile(pp),refs=[r['path'] for r in req['references']])
    p.dump(reqpath,req)
    print(json.dumps(req))
elif cmd=='receipt-ingest':
    raw=json.loads(Path(sys.argv[3]).read_text(encoding='utf-8-sig'))
    receipt=ROOT/'receipts'/f'{stem}.tool.json'
    assert not receipt.exists()
    raw.update(recordedAtUtc=p.now(),tool='image_gen.imagegen',route='builtin',actualModel=None,actualQuality=None,modelEvidence='not returned by builtin tool')
    p.dump(receipt,raw)
    subprocess.run([sys.executable,str(ROOT/'qa'/'expansion-west-worker.py'),'ingest',stem,raw['sourceToolPath']],check=True)
    subprocess.run([sys.executable,str(ROOT/'qa'/'finalize-central-native-evidence.py'),stem],check=True)
    index=ROOT/'qa'/'expansion-west-worker-map.json'; d=p.load(index)
    if d.get('currentError'):
        d.setdefault('networkFailureHistory',[]).append(d.pop('currentError'))
    d['status']='generating'; d['updatedAtUtc']=p.now();p.dump(index,d)
elif cmd=='review':
    val=json.loads(Path(sys.argv[3]).read_text(encoding='utf-8-sig'))
    p.dump(ROOT/'qa'/f'{stem}-review.json',val)
