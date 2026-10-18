"""Read current metadata and four selected4096PNG files only. Run after root final selection."""
from pathlib import Path
from PIL import Image
import argparse,datetime,hashlib,json,sys

Z=Path(__file__).resolve().parents[3]
TILES=['r15_c15','r15_c16','r16_c15','r16_c16']
BASE_R16_C16_SHA='fa9ff5a51638c2664c2ffe690d93fd7fc5ca8bfc911867cdb532c13069f7fc5e'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def path_value(v):
 if isinstance(v,str):return v
 if isinstance(v,dict):return v.get('path')
 return None
def eq_path(a,b):return Path(a).resolve()==Path(b).resolve()
def is_current_detail(k):
 s=k.lower()
 if any(x in s for x in ['previous','initial','baseassembly','history']):return False
 return any(x in s for x in ['qa','review','remaining','pending','finding','nextstep','status','verification','manifest','watch','formal'])
def collect_evidence(details):
 found={}
 def walk(obj):
  if isinstance(obj,dict):
   p=obj.get('path');expected=obj.get('sha256')
   if isinstance(p,str) and expected and Path(p).suffix.lower()=='.json':
    if p not in found:
     exists=Path(p).is_file();actual=sha(p) if exists else None
     found[p]={'path':p,'recordedSha256':expected,'actualSha256':actual,'hashMatches':actual==expected,'exists':exists}
   else:
    for v in obj.values():walk(v)
  elif isinstance(obj,list):
   for v in obj:walk(v)
 walk(details);return list(found.values())

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--expected-r16-c16-sha',required=True,help='Final root-selected r16_c16 SHA256; current base fa9ff5a5 is rejected.')
ap.add_argument('--output',type=Path,help='New JSON output path; default is new timestamped file in batch-checkpoints.')
args=ap.parse_args()
expected=args.expected_r16_c16_sha.lower()
if len(expected)!=64 or any(c not in '0123456789abcdef' for c in expected):ap.error('Expected a64-character SHA256.')
if expected==BASE_R16_C16_SHA:ap.error('Root final selection is not yet specified; refuse the pre-repair base SHA.')
now=datetime.datetime.now(datetime.timezone.utc)
out=args.output or Z/'batch-checkpoints'/('four-tile-delivery-'+now.strftime('%Y%m%dT%H%M%SZ')+'.json')
if out.exists():ap.error('Output exists; use a new version path.')

# Guard before loading any other selected images or writing a report.
guard=read(Z/'r16_c16/candidate/latest-assembly.json')['candidate']
if guard.get('sha256')!=expected:raise SystemExit('r16_c16 current wrapper SHA differs from expected final SHA. No report written.')
rows=[];errors=[]
for tile in TILES:
 d=Z/tile;p=d/'progress.json';w=d/'candidate/latest-assembly.json';progress=read(p);wrapper=read(w)
 candidate=wrapper.get('candidate');assert isinstance(candidate,dict) and candidate.get('path') and candidate.get('sha256'),tile
 imagepath=Path(candidate['path']);actualsha=sha(imagepath)
 with Image.open(imagepath) as im:
  size=list(im.size);fmt=im.format
  opaque='A' not in im.getbands() or im.getextrema()[-1]==(255,255)
 pp=path_value(progress.get('candidate'));pathmatch=bool(pp) and eq_path(pp,imagepath)
 progress_sha=progress.get('candidateSha256')
 checks={'wrapperCandidateShaMatches':actualsha==candidate['sha256'],'progressCandidatePathMatches':pathmatch,'progressCandidateShaMatches':None if progress_sha is None else progress_sha==actualsha,'dimensions4096':size==[4096,4096],'formatPNG':fmt=='PNG','opaque':opaque}
 if tile=='r16_c16':checks['expectedFinalShaMatches']=actualsha==expected
 details={'wrapper':{k:v for k,v in wrapper.items() if is_current_detail(k)},'progress':{k:v for k,v in progress.items() if is_current_detail(k)}}
 evidence=collect_evidence(details)
 selectedfail=[k for k,v in checks.items() if v is False]
 evidencefail=[e['path'] for e in evidence if not e['hashMatches']]
 if selectedfail or evidencefail:errors.append({'tile':tile,'selectionChecksFailed':selectedfail,'currentEvidenceHashMismatch':evidencefail})
 rows.append({'tile':tile,'candidate':{'path':str(imagepath),'sha256':actualsha,'recordedSha256':candidate['sha256'],'size':size,'format':fmt,'opaque':opaque},'selectionMetadata':{'wrapper':ref(w),'progress':ref(p)},'checks':checks,'currentQAAndUnpassedIssues':details,'currentEvidenceHashChecks':evidence,'activeNativeCount':wrapper.get('activeNativeCount',progress.get('activeNativeCount')),'actualNativeOutputCount':wrapper.get('actualNativeOutputCount',progress.get('actualNativeOutputCount')),'formalAccepted':wrapper.get('formalAccepted',False),'actualImageModel':None,'actualImageModelEvidence':'Built-in generation receipts do not return the actual model; no2.5 claim.'})

report={'schemaVersion':1,'createdAtUtc':now.isoformat(),'scope':'Current four-tile selected files and current wrapper/progress only; no historical image scan, no overview rebuild, no image copy or full package.','status':'current_metadata_and_selected_pngs_verified' if not errors else 'metadata_inconsistency_requires_root_check','expectedR16C16FinalSha256':expected,'tileCount':4,'tiles':rows,'errors':errors,'formalAcceptanceInferred':False,'notes':['4块实际4096成图与选源SHA分别核实；QA通过和未过问题分别沿用当前记录，不把文件齐全当作整区验收。','本批所有图片均来自现有内置入口，实际型号未返回，未使用付费API，不将未知型号标为2.5。','本批制作/收尾未操作共享Git的HEAD、index或refs，未声称提交或推送。']}
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':ref(out),'status':report['status'],'tileCount':4,'errors':errors},ensure_ascii=False))
sys.exit(1 if errors else 0)
