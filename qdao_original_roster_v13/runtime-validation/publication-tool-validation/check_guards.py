from pathlib import Path
import importlib.util,sys,json,datetime
from types import SimpleNamespace
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
script=ROOT/'tools/publish_original_roster_v13.py'
spec=importlib.util.spec_from_file_location('publisher_guard_check',script);publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)
main=Path('E:/work/mmorpg-client');isolated=Path('E:/work/tmp/qdao-original-verify-20260917')
protected=list((main/'Assets/Resources/World/Characters/QdaoRosterV12').glob('*/appearance.json'))+list((main/'Assets/Resources/World/Characters/QdaoRosterV13').glob('*/appearance.json'))
before={str(path):publisher.sha(path) for path in protected};family=main/publisher.FAMILY;family_before=family.exists();cases=[]
def rejects(name,action):
 try:action()
 except ValueError as error:cases.append({'name':name,'passed':True,'rejection':str(error)})
 else:raise AssertionError(name+' unexpectedly accepted')
audit,code=publisher.main([])
assert code==1 and audit['writesPerformed'] is False and len(audit['blocked'])==23 and not audit['candidates']
Path(__file__).with_name('default-dry-run.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
cases.append({'name':'real23IncompleteCandidatesRejectedByDefault','passed':True,'rejectedCharacters':23,'writesPerformed':False})
for identity in ('24_lu_dongbin','../00_reference_topright_boy','q_daoist_topright_character_full_uncropped'):
 report,code=publisher.main(['--character',identity]);assert code==1 and report['writesPerformed'] is False
 cases.append({'name':'rejectNonOriginalOrUnsafeId','input':identity,'passed':True,'rejection':report['error']})
rejects('relativePathCannotLeaveRoot',lambda:publisher.safe_child(ROOT,'../escape'))
rejects('absolutePathCannotReplaceRoot',lambda:publisher.safe_child(ROOT,Path('E:/work/mmorpg-client')))
rejects('stageCannotTargetMainProject',lambda:publisher.target_project(main,True))
assert publisher.target_project(isolated,True)==isolated.resolve();cases.append({'name':'independentUnityProjectRecognized','passed':True})
args=SimpleNamespace(runtime_report=ROOT/'runtime-validation/contract-run1/city-captures/runtime-observed-appearances.json',input_snapshot=ROOT/'runtime-validation/input-snapshot-run1-playmode.json')
rejects('realV12OnlyReportCannotPublishOriginalV13',lambda:publisher.runtime_acceptance([],main,args))
assert before=={str(path):publisher.sha(path) for path in protected} and family_before==family.exists()
report={'createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tool':str(script),'toolSha256':publisher.sha(script),'python':sys.version,'validationScope':'Syntax/import, actual current incomplete-candidate dry run, exact-ID/path boundaries, and rejection of the real V12-only observation. No synthetic PNGs, fake completed candidates, stage or publish execution. Positive publication remains unexecuted until genuinely complete accepted art exists.','cases':cases,'protectedActivationHashes':before,'originalResourceDirectoryBefore':family_before,'originalResourceDirectoryAfter':family.exists(),'allPassed':True,'writesToGameResources':False}
Path(__file__).with_name('summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'cases':len(cases),'allPassed':True,'originalResourceDirectoryExists':family.exists(),'protectedActivations':len(before),'toolSha256':report['toolSha256']},ensure_ascii=False))
