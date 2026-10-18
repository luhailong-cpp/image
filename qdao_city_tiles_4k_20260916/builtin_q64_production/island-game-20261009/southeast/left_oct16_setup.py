from workflow import ROOT, read, write, sha, now
from pathlib import Path
import os
os.environ['ISLAND_PROGRESS_FILE']='progress-left-oct16.json'

for tile in ['r13_c10','r14_c10']:
    dst=ROOT/f'selection-left-oct16-{tile}.json'
    if not dst.exists():
        src=ROOT/f'selection-{tile}.json'
        write(dst,read(src) if src.exists() else {'tile':tile,'patchVersions':{},'pendingFindings':[]})
    dst=ROOT/f'production-resume-left-oct16-{tile}.json'
    if not dst.exists():
        src=ROOT/f'production-resume-left-sol-{tile}-20261012.json'
        p=read(src) if src.exists() else {'tile':tile,'generatedNativeCount':0}
        p.update(agent='left_oct16',inFlightRequests=[],inFlight=False,activeImageGenCalls=0)
        write(dst,p)
pf=ROOT/'progress-left-oct16.json'
if not pf.exists():
    write(pf,{'agent':'left_oct16','createdAt':now(),'assignedTiles':['r13_c10','r14_c10','r14_c11'],'generatedNativeCount':0,'inFlightRequests':[],'actualModel':None,'paidApiUsed':False,'oldUnresolvedRequests':['r13_c10_p13_v01','r13_c10_p22_v01','r13_c10_p43_v01'],'status':'resume_audited'})
src=(ROOT/'left_c10_workflow_20261013.py').read_text(encoding='utf-8')
src=src.replace("PROGRESS=ROOT/f'progress-{TILE}.json'", "PROGRESS=ROOT/'progress-left-oct16.json'")
src=src.replace("RESUME=ROOT/f'production-resume-left-sol-{TILE}-20261012.json'", "RESUME=ROOT/f'production-resume-left-oct16-{TILE}.json'")
src=src.replace("SELECTION=ROOT/f'selection-{TILE}.json'", "SELECTION=ROOT/f'selection-left-oct16-{TILE}.json'")
src=src.replace("ROOT/f'selection-{NORTH}.json'", "ROOT/f'selection-left-oct16-{NORTH}.json'")
src=src.replace("    original.TILE=TILE;original.PROGRESS=PROGRESS;original.RESUME=RESUME", "    original.TILE=TILE;original.PROGRESS=PROGRESS;original.RESUME=RESUME")
dst=ROOT/'left_oct16_workflow.py'
if not dst.exists():dst.write_text(src,encoding='utf-8')
src=(ROOT/'left_c10_candidate_20261013.py').read_text(encoding='utf-8')
src=src.replace("ROOT/f'selection-{tile}.json'", "ROOT/f'selection-left-oct16-{tile}.json'")
src=src.replace("ROOT/f'progress-{tile}.json'", "ROOT/'progress-left-oct16.json'")
src=src.replace("ROOT/f'production-resume-left-sol-{tile}-20261012.json'", "ROOT/f'production-resume-left-oct16-{tile}.json'")
dst=ROOT/'left_oct16_candidate.py'
if not dst.exists():dst.write_text(src,encoding='utf-8')
write(ROOT/'left-oct16-resume-audit.json',{'createdAt':now(),'agent':'left_oct16','nativeCount':len(list((ROOT/'native').glob('r13_c10_*.png'))),'selected':read(ROOT/'selection-left-oct16-r13_c10.json')['patchVersions'],'oldGenerationDirectory':'C:/Users/luyua/.codex/generated_images/01a13459-5b6e-7bf2-9960-345e90675302','latestOldWorkerOutputUtc':'2026-10-16T06:53:30.3135526Z','unresolvedOldRequests':['13:v01','22:v01','43:v01'],'unrequestedMissing':['32','33'],'eastCandidate':'tiles/r13_c11.candidate-resume-20261013-v01.png','eastSha256':sha(ROOT/'tiles/r13_c11.candidate-resume-20261013-v01.png'),'sharedProgressOrGitChanged':False})
print('Independent left_oct16 workflow and records prepared.')
