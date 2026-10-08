from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
D=ROOT/'r08_c15/repairs/approved-integration'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(D/'candidate.png')=='70ce623a54fb8419b951b7372a88e95db2c8b5ae9e04845c2af2c1fd18312585'
names=['overview-preview-1024','corner-nw','corner-ne','corner-sw','corner-se','west-c14-c15-common-edge-full']
record={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','candidateSha256':sha(D/'candidate.png'),'actualVisualInspection':True,'inspectionScope':'downsampled overview plus four native 512 corners and full-length native common west edge','result':'pass for this scope','observations':['Cabin, hull, rope and lantern composition preserved; right hull-waterline step removed.','All four corners contain continuous native material or water without new rectangular discontinuities.','Full 4096-pixel c14/c15 common edge remains continuous in timber, rope and water.'],'limitations':['Internal six seams and nine crossings are reviewed separately.','Not full-city, navigation or client acceptance.'],'formalAccepted':False,'sheets':[{'file':str(D/'qa/assembly'/f'{n}.png'),'sha256':sha(D/'qa/assembly'/f'{n}.png'),'nativePixelQA':not n.startswith('overview')} for n in names]}
(D/'root-external-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
src=(ROOT/'assembly_r07_c16.py').read_text(encoding='utf-8')
src=src.replace('r07_c16','r07_c15').replace('r08_c16','r08_c15').replace('GLOBAL_ORIGIN = (61440, 24576)','GLOBAL_ORIGIN = (57344, 24576)')
out=ROOT/'assembly_r07_c15.py'
assert not out.exists(),'Do not overwrite assembly tools'
out.write_text(src,encoding='utf-8')
print('Saved external review and r07_c15 assembly helper.')
