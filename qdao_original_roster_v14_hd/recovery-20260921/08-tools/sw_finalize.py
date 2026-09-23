from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
from PIL import Image
base=Path(__file__).resolve().parent.parent
gen=base/'08-generation'; processed=base/'08-delivery-preview/processed'
selection=json.loads((base/'08-tools/SW-selection.json').read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
notes={1:'Far anatomical RIGHT / screen-left foot contact, near LEFT trails. Original prompt retained, actual anatomy recorded here.',2:'Far RIGHT loading with forward boot flatter.',3:'Far RIGHT mid-support; v2 restores original head/body scale.',4:'Far RIGHT support, near LEFT begins recovery.',5:'Near LEFT low passing beside far RIGHT support.',6:'Near LEFT early low swing, almost aligned boot depths.',7:'Near LEFT advances and becomes the lower/leading foot.',8:'Near LEFT terminal swing approaching contact without outward kick.',9:'Opposite contact: near anatomical LEFT / screen-right boot leads; far RIGHT retreats. Hip ownership and thigh occlusion reverse from01.',10:'Near LEFT loading and far RIGHT toe-off.',11:'Near LEFT support, far RIGHT low recovery.',12:'Near LEFT support with far RIGHT drawing toward passing.',13:'Far RIGHT passes behind near LEFT support.',14:'Far RIGHT begins advancing after passing.',15:'Far RIGHT forward swing toward contact01.',16:'Far RIGHT terminal forward swing before01; independent generated source, no duplicated frame.'}
selected=[]
for slot,attempt in selection.items():
    source=processed/attempt/'source.json';meta=json.loads(source.read_text())
    assert sha(gen/attempt/'raw.png')==meta['raw']['sha256']
    assert sha(processed/attempt/'frame.png')==meta['output_sha256']
    assert meta['raw']['size']==[1254,1254] and meta['anchor_px']==[512.0,942]
    with Image.open(processed/attempt/'frame.png') as im:
        assert im.size==(1024,1024) and im.mode=='RGBA' and im.getextrema()[3][0]==0
    review={'status':'accepted_static','reviewedAt':datetime.now(timezone.utc).isoformat(),'slot':slot,'attempt':attempt,'observedPhase':notes[int(slot.split('/')[-1])] if slot.startswith('walk/') else 'Independent SW idle, same identity and equipped-hand ownership.', 'checks':{'complete_character':True,'fixed_SW_camera':True,'identity_costume_equipment':True,'two_connected_legs':True,'support_and_swing_readable':True,'light_dark_alpha_edges':True,'source_scale_and_proportions':True,'no_mirror_or_pose_synthesis':True},'source_sha256':meta['raw']['sha256'],'output_sha256':meta['output_sha256'],'dynamic_browser_review':'pending_root_review','unity_validation':False,'formal_client_validation':False}
    save(gen/attempt/'review.json',review)
    selected.append({'slot':slot,'attempt':attempt,'raw_sha256':meta['raw']['sha256'],'output_sha256':meta['output_sha256']})
assert len({r['raw_sha256'] for r in selected})==17
assert len({r['output_sha256'] for r in selected})==17
attempts=[]
for d in sorted(gen.iterdir()):
    if d.is_dir() and (d.name.startswith('walk-SW-') or d.name=='idle-SW-v1'):
        raw=d/'raw.png'; rr=processed/d.name/'raw.png.generation.json'
        if raw.exists():
            assert rr.exists(),d
            shutil.copy2(rr,d/'raw.png.generation.json')
            rec=json.loads((d/'receipt.json').read_text(encoding='utf-8-sig'))
            assert rec.get('actualModel') is None and rec.get('actualQuality') is None
        review=json.loads((d/'review.json').read_text()) if (d/'review.json').exists() else {}
        attempts.append({'attempt':d.name,'rawExists':raw.exists(),'raw_sha256':sha(raw) if raw.exists() else None,'status':review.get('status','interrupted_without_observed_return')})
summary={'scope':'08_alchemy_prodigy_boy/SW only','selected_walk':16,'selected_idle':1,'raw_attempts':sum(x['rawExists'] for x in attempts),'rejected_raw_attempts':sum(x['status']=='rejected' for x in attempts),'interrupted_without_observed_return':sum(not x['rawExists'] for x in attempts),'selected':selected,'attempts':attempts,'actualModel':None,'actualQuality':None,'unverifiedReason':'host-managed; builtin tool exposes no model/quality selector and returned no actual model/quality metadata','paid_api_calls':0,'staticReview':'passed_after_rejecting_and_redrawing03v1_06v2_06v3_07v1_08v1','checkedSeam':'15->16->01->02: same camera, far RIGHT forward leg, intact gear and proportions; distinct generated poses','dynamic_browser_review':'pending_root_review','unity_validation':False,'formal_client_validation':False,'source_cleanup':'deferred_until_root_final_selection_and_reference_audit'}
save(base/'08-tools/SW-REVIEW.json',summary)
print(json.dumps({k:summary[k] for k in ('selected_walk','selected_idle','raw_attempts','rejected_raw_attempts','interrupted_without_observed_return','staticReview')},ensure_ascii=False))
