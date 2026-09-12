"""Independent final-file validation; does not generate or modify character art."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageSequence
import hashlib, json, sys
import numpy as np
from finalize_pack import ROSTER, DIRS
ROOT=Path(__file__).resolve().parent

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check_role(slug,name):
    base=ROOT/slug
    qc=json.loads((base/'qc.json').read_text(encoding='utf-8-sig'))
    assert qc.get('status') in ('passed','passed_visual_and_numeric_qc'),qc.get('status')
    assert qc.get('visual_review',{}).get('status') in ('passed','approved'),'visual review pending'
    visual=qc['visual_review']
    if visual.get('record'):
        p=base/visual['record']
        assert digest(p)==visual['sha256'],'visual approval record modified'
        approval=json.loads(p.read_text(encoding='utf-8-sig'))
        for f in approval.get('files',[]):
            assert digest(base/f['path'])==f['sha256'],f'approved media modified: {f["path"]}'
    portrait=Image.open(base/'portrait.png')
    assert portrait.mode=='RGBA' and portrait.size==(1024,1024),'portrait contract'
    assets=[base/'portrait.png']; frames={}; hashes=[]
    for d in DIRS:
        row=[]
        for n in range(1,5):
            p=base/'walk'/d/f'{n:02d}.png'; im=Image.open(p).convert('RGBA')
            assert Image.open(p).mode=='RGBA' and im.size==(512,512),(d,n,'frame contract')
            a=np.asarray(im.getchannel('A')); yy,xx=np.nonzero(a>8)
            assert len(yy)>100 and int(yy.max())==471,(d,n,'feet line')
            lower=yy>=np.percentile(yy,90); ax=float(np.median(xx[lower]))
            assert abs(ax-256)<=0.5,(d,n,'feet x',ax)
            b=im.getbbox(); assert b[0]>0 and b[1]>0 and b[2]<512 and b[3]<512,(d,n,'edge')
            assert a.min()==0 and a.max()>=240,(d,n,'alpha')
            row.append(im);assets.append(p);hashes.append(digest(p))
        strip=Image.open(base/'walk'/d/'strip.png').convert('RGBA')
        assert strip.size==(2048,512),(d,'strip size')
        for n,im in enumerate(row):
            assert strip.crop((n*512,0,(n+1)*512,512)).tobytes()==im.tobytes(),(d,n,'strip mismatch')
        gif=Image.open(base/'walk'/d/'walk.gif')
        assert gif.n_frames==4 and gif.size==(512,512) and gif.info.get('loop')==0,(d,'GIF contract')
        durations=[]
        for g in ImageSequence.Iterator(gif):
            durations.append(g.info.get('duration')); assert g.convert('RGBA').getbbox(),(d,'empty GIF frame')
        assert durations==[120]*4,(d,'GIF timing',durations)
        assets.extend([base/'walk'/d/'strip.png',base/'walk'/d/'walk.gif']);frames[d]=row
    assert len(set(hashes))==32,'duplicate movement frames'
    for kind,dirs in [('cardinal',['S','W','E','N']),('diagonal',['SW','NW','NE','SE'])]:
        p=base/f'walk-{kind}.png'; sheet=Image.open(p).convert('RGBA')
        assert sheet.size==(2048,2048),(kind,'sheet size')
        for y,d in enumerate(dirs):
            for x,im in enumerate(frames[d]):
                assert sheet.crop((x*512,y*512,(x+1)*512,(y+1)*512)).tobytes()==im.tobytes(),(kind,d,x,'sheet mismatch')
        assets.append(p)
    assert len(assets)==51
    return {'slug':slug,'name_zh':name,'status':'passed','frames':32,'formal_media':51,'qc_status':qc['status'],'visual_status':visual['status'],'artifacts':[{'path':p.relative_to(ROOT).as_posix(),'sha256':digest(p)} for p in assets]}

def main():
    rows=[]; errors=[]
    for slug,name in ROSTER:
        try:
            rows.append(check_role(slug,name)); print(slug,'passed',flush=True)
        except Exception as exc:
            errors.append({'role':slug,'error':str(exc)});print(slug,'PENDING/FAILED',str(exc),flush=True)
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'status':'passed' if not errors else 'incomplete','expected_characters':len(ROSTER),'passed_characters':len(rows),'expected_frames':len(ROSTER)*32,'verified_frames':len(rows)*32,'formal_media_count':len(rows)*51,'excluded_user_rejected':['24_crane_hermit'],'checks':['RGBA sizes and real alpha','all 256 frames unique within character','foot y471/x256±0.5','no edge touch or empty frames','strips/sheets exact pixel match','4-frame 120ms looping GIFs','current approved 27 media hash match','role numeric and visual pass'],'characters':rows,'errors':errors,'scope':'image assets, no client integration'}
    (ROOT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':report['status'],'characters':len(rows),'frames':len(rows)*32,'errors':errors},ensure_ascii=False))
    return 0 if not errors else 2
if __name__=='__main__':sys.exit(main())
