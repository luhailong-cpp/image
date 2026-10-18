import os,sys,subprocess
os.environ['ISLAND_PROGRESS_FILE']='progress-wall-oct16.json'
from workflow import *
for q,note in [(ROOT/'qa'/'wall-oct17'/'r10_c10_h32_roi'/'review.json','Native subset avoids the shifted top insertion boundary. Center and all four actual subset edges viewed; paving geometry continuous. No filtering or RGB changes.'),(ROOT/'qa'/'wall-oct16'/'r10_c10_ov_h33_v01'/'review.json','Two central paving joint endpoints repaired. Native center and all four actual replacement boundaries viewed and continuous; preserve repaired post shape.')]:
 d=read(q);d.update(status='passed_local_repair',note=note,reviewedAt=now(),reviewer='wall_oct17')
 for e in d['entries']:assert sha(Path(e['file']))==e['sha256'];e['status']='passed_actual_native_visual'
 write(q,d)
q=ROOT/'qa'/'wall-oct16'/'r10_c10_ov_h32_v01'/'review.json';d=read(q);d.update(status='not_passed_full_core',note='Full1024 insertion introduces a small stair-step at top edge; only the separately reviewed native subset is adopted.',reviewedAt=now());write(q,d)
m=read(ROOT/'adopted-overlay-r10_c10-wall-oct17-v02.json');roi=read(ROOT/'qa'/'wall-oct17'/'r10_c10_h32_roi'/'review.json');m['overlays'].append({'file':roi['source'],'sha256':roi['sourceSha256'],'sourceCrop':roi['sourceCrop'],'destinationBox':roi['destinationBox'],'review':str(ROOT/'qa'/'wall-oct17'/'r10_c10_h32_roi'/'review.json')})
k='r10_c10_ov_h33_v01';g=read(ROOT/'prompts'/f'{k}.overlay.json');f=ROOT/'native'/f'{k}.png';m['overlays'].append({'file':str(f),'sha256':sha(f),'sourceCrop':g['coreCrop'],'destinationBox':g['destinationBox'],'review':str(ROOT/'qa'/'wall-oct16'/k/'review.json')})
mf=ROOT/'adopted-overlay-r10_c10-wall-oct17-v03.json';write(mf,m);sp=read(ROOT/'wall-oct17-r10c10-v02.spec.json');sp['overlayManifests']=[str(mf)];sf=ROOT/'wall-oct17-r10c10-v03.spec.json';write(sf,sp)
subprocess.run([sys.executable,str(ROOT/'assemble_native_overlay_candidate_20261012.py'),str(sf),'wall-oct17-v03'],check=True)
subprocess.run([sys.executable,str(ROOT/'qa_from_candidate.py'),str(sf),'wall-oct17-v03'],check=True)
