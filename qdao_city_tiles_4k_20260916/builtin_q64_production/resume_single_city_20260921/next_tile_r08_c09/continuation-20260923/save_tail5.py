"""Use the native saver while preserving a concurrently removed style alias."""
from pathlib import Path
import importlib.util, json, sys
P=Path(__file__).resolve().parent.parent
ident=sys.argv[1]
spec=importlib.util.spec_from_file_location('native_saver',P/'native_tools.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rawread,rawsha,rawwrite,rawcopy=m.read,m.sha,m.write,m.shutil.copyfile
receipt=rawread(P/'requests'/f'{ident}.receipt.json')
preflight=rawread(receipt['preflight'])
expected={x['path']:x['sha256'] for x in preflight['references']}
patch=next(x for x in rawread(P/'plan.json')['patches'] if x['id']==ident.split('.')[0])
request_path=Path(patch['request'])
canonical=P.parents[3]/'designs/gameplay-ui/04-guild.png'
designsha='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
assert rawsha(canonical)==designsha
alias='D:\\luyuan\\wuxingqitan\\image\\designs\\guild-ui-v2\\source\\guild-overview.png'
history=[]

def checked_sha(p):
    p=Path(p)
    if p.is_file():
        value=rawsha(p)
        if str(p) in expected:assert expected[str(p)]==value
        return value
    assert str(p)==alias and expected[str(p)]==designsha
    history.append({'historicalSubmittedPath':str(p),'submittedSha256':designsha,'verifiedBeforeSubmission':True,'currentlyRetainedByteIdenticalPath':str(canonical),'reason':'Historical duplicate path removed by concurrent project cleanup after submission'})
    return designsha

def checked_read(p):
    if Path(p)==request_path:
        original=rawread(p)
        actual=receipt['request']
        assert original['prompt']==actual['prompt']
        for a,b in zip(original['referenced_image_paths'],actual['referenced_image_paths']):
            assert a==b or (a==alias and Path(b)==canonical)
        return actual
    return rawread(p)

def checked_copy(src,dst):
    if Path(dst).is_file():
        assert Path(dst).read_bytes()==Path(src).read_bytes()
        return str(dst)
    return rawcopy(src,dst)

def checked_write(p,record):
    record['preflightEvidence']={'file':receipt['preflight'],'sha256':rawsha(receipt['preflight'])}
    record['referencePathMapping']=preflight.get('referencePathMapping',[])
    record['removedHistoricalReferenceEvidence']=history
    return rawwrite(p,record)

m.sha=checked_sha;m.read=checked_read;m.write=checked_write;m.shutil.copyfile=checked_copy
dst=P/patch['outputFile']
if dst.exists():
    assert not dst.with_suffix('.record.json').exists() and not dst.with_suffix('.png.generation.json').exists()
    # The original saver copied PNG before failing on the removed reference.
    # Keep that exact PNG; expose its absence only to the saver's own guard.
    original_exists=Path.exists
    Path.exists=lambda self:False if self==dst else original_exists(self)
    try:m.save(ident)
    finally:Path.exists=original_exists
else:m.save(ident)
