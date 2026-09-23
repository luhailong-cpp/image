"""Retain four genuinely returned old patches at their existing plan paths."""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util, json, os, re
P=Path(__file__).resolve().parent.parent
RECOVERY=P/'recovery-20260923T064157485825Z'
identifiers=['r02_c02.v2','r02_c03.v2','r02_c04.v2','r03_c01.v2']
spec=importlib.util.spec_from_file_location('saver',P/'native_tools.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rawsha,rawwrite=m.sha,m.write
canonical=P.parents[3]/'designs/gameplay-ui/04-guild.png'
designsha='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
assert rawsha(canonical)==designsha
plan_before=(P/'plan.json').read_bytes()
state={}
for ident in identifiers:
    recpath=RECOVERY/(ident+'.generation.json');gen=m.read(recpath)
    receipt=m.read(P/'requests'/(ident+'.receipt.json'))
    source=Path(re.search(r' as (.+?\.png) by default\.',receipt['response']['output_hint'],re.S).group(1))
    recovered=RECOVERY/(ident+'.png');destination=P/'native'/(ident+'.png')
    assert not destination.exists() and not destination.with_suffix('.record.json').exists()
    assert not destination.with_suffix('.png.generation.json').exists()
    assert recovered.resolve().is_relative_to(P.resolve()) and destination.resolve().is_relative_to(P.resolve())
    assert source.read_bytes()==recovered.read_bytes()
    assert rawsha(recovered)==gen['sha256']
    assert rawsha(P/'requests'/(ident+'.receipt.json'))==gen['originalReceipt']['sha256']
    state[ident]={'generation':gen,'generationPath':recpath,'source':source,'recovered':recovered,'destination':destination}

entries=[]
for ident in identifiers:
    entry=state[ident];gen=entry['generation']
    expected={x['file']:x['sha256'] for x in gen['references']}
    def checked_sha(path):
        path=Path(path)
        if path.exists():
            value=rawsha(path)
            if str(path) in expected:assert value==expected[str(path)]
            return value
        assert str(path).endswith('designs\\guild-ui-v2\\source\\guild-overview.png')
        assert expected[str(path)]==designsha
        return designsha
    def checked_retain(source,destination):
        assert Path(source)==entry['source'] and Path(destination)==entry['destination']
        assert not Path(destination).exists()
        assert entry['recovered'].read_bytes()==Path(source).read_bytes()
        os.rename(entry['recovered'],destination)
        return str(destination)
    def checked_write(path,record):
        record['recoveryEvidence']={'file':str(entry['generationPath']),'sha256':rawsha(entry['generationPath'])}
        record['historicalRecoveredAt']=gen['recoveredAt']
        record['nativePlanPathRetainedAtUtc']=datetime.now(timezone.utc).isoformat()
        record['nativePlanPathRetentionMeaning']='Moved verified recovered PNG from temporary recovery location into pre-existing plan path; no new generation, resizing, or source replacement'
        record['historicalReferenceCurrentLocation']={'historicalPath':gen['references'][2]['file'],'currentlyRetainedByteIdenticalPath':str(canonical),'sha256':designsha}
        return rawwrite(path,record)
    m.sha=checked_sha;m.shutil.copyfile=checked_retain;m.write=checked_write
    m.save(ident)
    entries.append({'id':ident,'historicalRecoveryFile':str(entry['recovered']),'currentNativeFile':str(entry['destination']),'sha256':rawsha(entry['destination']),'generationEvidence':str(entry['generationPath']),'historicalToolSource':str(entry['source']),'pngWasMovedNotCopied':True})

assert (P/'plan.json').read_bytes()==plan_before
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'newImageGenerationCalls':0,'planUnchanged':True,'planSha256':rawsha(P/'plan.json'),'currentCanonicalDesign':{'file':str(canonical),'sha256':designsha},'images':entries}
rawwrite(RECOVERY/'native-path-relocation.json',report)
print(json.dumps({'retainedAtPlanPaths':len(entries),'relocationReport':str(RECOVERY/'native-path-relocation.json')}))
