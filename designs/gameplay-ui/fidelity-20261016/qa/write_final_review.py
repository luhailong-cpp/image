from pathlib import Path
import json,hashlib,datetime,xml.etree.ElementTree as ET
from PIL import Image
ROOT=Path(__file__).resolve().parent
PACKAGE=ROOT.parent
EVIDENCE=Path('E:/work/image/docs/ui-fidelity-20261016')
NATIVE=EVIDENCE/'native'
CLIENT=Path('E:/work/mmorpg-client')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def image_evidence(p):
    return dict(path=str(p),sha256=sha(p),native_size=list(Image.open(p).size),mtime_utc=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat())
prior_batch=ROOT/'post-visual-fixes'
final_batch=ROOT/'post-final-polish'
final_seen=['07-bag-error_1920x1080.png','07-bag-error_2560x1080.png','05-missions-empty_1920x1080.png','05-missions-empty_2560x1080.png','10-mission-claim_1920x1080.png','10-mission-claim_2560x1080.png']
equipment_seen={
 'equipment':['06-long-attributes_2560x1080.png','06-long-attributes_1920x1080.png','06-long-attributes_1280x720.png','04-boots-detail_1920x1080.png','01-wish-weapon_2560x1080.png','01-wish-weapon_1920x1080.png','02-wish-armour_1280x720.png','05-pool-unavailable_1280x720.png'],
 'equipment-integration':['01-bag-equipment-detail_2560x1080.png','01-bag-equipment-detail_1920x1080.png','02-worn-equipment-detail_1280x720.png','03-equipment-more_1280x720.png','04-wish-pool-unavailable_1920x1080.png'],
 'equipment-forge/screenshots':['01-ready_2560x1080.png','01-ready_1920x1080.png','04-enhance-confirm_1280x720.png','06-loading_1280x720.png','02-gem-picker_2560x1080.png','03-inlay-busy_1920x1080.png','05-materials-insufficient_1280x720.png']}
status_details={
 'V01':('post-visual-fixes','Activity empty state has no repeated gold short lines or stale cards.'),
 'V02':('post-visual-fixes','Disabled native gameplay actions retain their painted shape; the gray crop-sized rectangle is absent.'),
 'V03':('post-visual-fixes','Capacity and Refresh sit inside the footer paper and clear the lower gold frame in both resolutions.'),
 'V04':('post-visual-fixes','Mission objective and activity description masks end after complete displayed lines; no next-line fragments observed.'),
 'V05':('post-final-polish','Empty bag left paper and empty mission reward paper have smooth tonal transitions; previous distinct bands/rectangular color joins are no longer visible in the reviewed 1920 and 2560 states. Natural paper texture and the source mountain ornament remain.'),
 'V06':('post-visual-fixes','Completed and incomplete objectives have distinct painted check/empty-box sprites; claimable state visibly shows checks.'),
 'V07':('post-final-polish','All five characters of the claimable status fit inside the gold badge with visible left/right padding; no ellipsis or border contact in 1920 and 2560 captures.'),
 'V08':('post-visual-fixes','Selected square item icon ends above the first horizontal divider in both reviewed filled bag captures.'),
 'V09':('post-visual-fixes','Empty bag/mission detail panels do not retain blank action plates; unused activity reward outlines do not sit behind schedule/reason text.')}
issues=[dict(id=k,status='resolved_in_reviewed_states',verified_batch=v[0],observation=v[1]) for k,v in status_details.items()]
modules=[]
for directory,names in equipment_seen.items():
    folder=NATIVE/directory
    verification=folder/'verification.txt' if directory!='equipment-forge/screenshots' else folder.parent/'verification.txt'
    modules.append(dict(directory=str(folder),captured_pngs=len(list(folder.glob('*.png'))),representative_images_directly_viewed=[image_evidence(folder/n) for n in names],verification=dict(path=str(verification),sha256=sha(verification),text=verification.read_text(encoding='utf-8-sig'))))
tests=[]
for filename in ('editmode-results.xml','playmode-results.xml'):
    p=EVIDENCE/filename;run=ET.parse(p).getroot()
    tests.append(dict(path=str(p),sha256=sha(p),summary=run.attrib))
install=json.loads((PACKAGE/'final-polish-20261017/install-manifest.json').read_text(encoding='utf-8'))
installed=[]
for row in install['files']:
    if row['path'].endswith('.meta'):continue
    p=CLIENT/row['path'];installed.append(dict(path=str(p),sha256=sha(p),matches_final_payload=sha(p)==row['sha256']))
assert all(x['matches_final_payload'] for x in installed)
inventory=NATIVE/'corrected-inventory.json'
report=dict(schema='qdao.gameplay-equipment.final-visual-review.v1',reviewed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),result='prior_nine_observed_defects_resolved',client_or_payload_modified_during_final_review=False,unity_started_by_reviewer=False,scope=['Gameplay bag, missions and activities','Equipment detail/wish, integration and forge representative captures'],capture_inventory_reference=dict(path=str(inventory),sha256=sha(inventory),note='Inventory is under native/, and describes its capture sweep; per-directory completion evidence and actual PNGs establish the later final polish capture.'),gameplay=dict(previous_corrected_batch=dict(directory=str(prior_batch),pngs=26,directly_viewed_all_26=True,images=[image_evidence(p) for p in sorted(prior_batch.glob('*.png'))]),final_polish_batch=dict(directory=str(final_batch),captured_pngs=len(list(final_batch.glob('*.png'))),directly_viewed_representatives=[image_evidence(final_batch/n) for n in final_seen],completion_text=(final_batch/'capture-status.txt').read_text(encoding='utf-8')),prior_issues=issues),equipment=dict(modules=modules,total_captured_pngs=54,directly_viewed_representatives=20,resolutions=['2560x1080','1920x1080','1280x720'],observation='No overlapping live detail cards, duplicate equipment action buttons, displaced modal action rows or material text overflow observed in the selected representatives. Wish unavailable state, forge loading/busy/shortage/confirmation are readable and reflect the documented control permissions.',action_uniqueness_evidence='EquipmentUiVerification completion includes strict activeInHierarchy control-count checks. Integration and forge use named activeInHierarchy + Single interaction lookups and completed all fixture action assertions. Static review also confirmed standalone card fixtures hide GameplayWindow before opening their own card.',long_attributes='Thirty-row hint and masked scroll viewport are visible at all three resolutions. Fourteen-row boots detail shows all fourteen rows. Static screenshots show the current scroll position; they do not independently demonstrate the last long row after pointer scrolling.'),test_evidence=tests,installed_final_payload=installed,limits=['Visual review establishes resolution of the listed observed defects in fixture renders; it is not a claim of byte/pixel identity of every dynamic UI state to the approved illustrations.','Fixture item names, quantities, icons, rewards absent from the protocol, schedules and progress are not live server configuration.','No live account, authoritative server trade/equipment mutation, real battle, or physical mouse/touch hit testing was performed by this reviewer.','Gameplay final polish was checked in six targeted images after the earlier complete 26-image review; equipment was sampled in twenty images, with all fifty-four capture completion records read.','Other modules, including skills, are outside this review.'])
(ROOT/'final-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(result=report['result'],issues_resolved=len(issues),gameplay_previous_viewed=26,gameplay_final_targeted_viewed=6,equipment_representatives_viewed=20,test_summaries=[r['summary']['result'] for r in tests],installed_final_payload_matches=True)))
