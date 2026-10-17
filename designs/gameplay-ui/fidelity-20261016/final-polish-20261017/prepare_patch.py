from pathlib import Path
import json,hashlib,re,datetime
import numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parent;PACKAGE=ROOT.parent;CLIENT=Path('E:/work/mmorpg-client');STAGED=ROOT/'staged'
ART='Assets/Resources/UI/Ugui/GameplayFidelity20261016/'
CS='Assets/Scripts/UI/Ugui/Gameplay/GameplayWindow.Fidelity.cs'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stage(path):
    p=STAGED/path;p.parent.mkdir(parents=True,exist_ok=True);return p
old=(CLIENT/CS).read_text(encoding='utf-8-sig')
new=old.replace('MissionStatus(detail.Status), badgeX + 2, 131, 122, 45, 25, Ink','MissionStatus(detail.Status), badgeX + 15, 131, 96, 45, 20, Ink')
new=new.replace('badgeText.fontSizeMin = 18; badgeText.fontSizeMax = 25;','badgeText.fontSizeMin = 16; badgeText.fontSizeMax = 20;')
assert new!=old
assert new.count('badgeX + 15, 131, 96, 45, 20')==1
stage(CS).write_text(new,encoding='utf-8');stage(CS+'.meta').write_bytes((CLIENT/(CS+'.meta')).read_bytes())
assets=[]
def smooth_paper(base,rect,paper):
    a=np.array(base).astype(np.float32);x0,y0,x1,y1=rect;pad=4
    l=max(0,x0-pad);r=min(base.width,x1+pad);t=max(0,y0-pad);b=min(base.height,y1+pad)
    fallback=np.median(np.array(paper).reshape(-1,3),axis=0)
    def edge(values):
        good=(values[:,0]>213)&(values[:,1]>200)&(values[:,2]>170)&((values[:,0]-values[:,1])<25)&((values[:,1]-values[:,2])<35)
        p=np.flatnonzero(good);v=np.empty_like(values)
        for channel in range(3):v[:,channel]=np.interp(np.arange(len(values)),p,values[p,channel]) if len(p)>2 else fallback[channel]
        return np.array(Image.fromarray(np.clip(v,0,255).astype('uint8')[None,:,:]).filter(ImageFilter.GaussianBlur(8)))[0].astype(np.float32)
    top=edge(a[t,l:r]);bottom=edge(a[b-1,l:r]);left=edge(a[t:b,l]);right=edge(a[t:b,r-1])
    # Harmonic paper interpolation: boundary variation decays locally rather than
    # extending as the horizontal/vertical bands produced by a Coons patch.
    gw=max(8,int(np.ceil((r-l)/10))+1);gh=max(8,int(np.ceil((b-t)/10))+1)
    def resample(e,n):return np.stack([np.interp(np.linspace(0,len(e)-1,n),np.arange(len(e)),e[:,c]) for c in range(3)],axis=1)
    top=resample(top,gw);bottom=resample(bottom,gw);left=resample(left,gh);right=resample(right,gh)
    corners=[(top[0]+left[0])/2,(top[-1]+right[0])/2,(bottom[0]+left[-1])/2,(bottom[-1]+right[-1])/2]
    top[0]=left[0]=corners[0];top[-1]=right[0]=corners[1];bottom[0]=left[-1]=corners[2];bottom[-1]=right[-1]=corners[3]
    field=np.empty((gh,gw,3),dtype=np.float32);field[:]=np.mean(np.concatenate((top,bottom,left,right)),axis=0)
    field[0]=top;field[-1]=bottom;field[:,0]=left;field[:,-1]=right
    iterations=0
    for iterations in range(4000):
        interior=(field[:-2,1:-1]+field[2:,1:-1]+field[1:-1,:-2]+field[1:-1,2:])*.25
        difference=float(np.max(np.abs(interior-field[1:-1,1:-1])))
        field[1:-1,1:-1]=interior
        if difference<.0008:break
    large=np.array(Image.fromarray(np.clip(field,0,255).astype('uint8')).resize((r-l,b-t),Image.Resampling.BICUBIC)).astype(np.float32)
    grain=np.array(paper).astype(np.float32)-np.array(paper.filter(ImageFilter.GaussianBlur(6))).astype(np.float32)
    grain=np.tile(grain,(int(np.ceil((b-t)/paper.height)),int(np.ceil((r-l)/paper.width)),1))[:b-t,:r-l]
    large=np.clip(large+grain*.8,0,255)
    xx=np.minimum(np.clip((np.arange(l,r)-l)/pad,0,1),np.clip((r-1-np.arange(l,r))/pad,0,1))
    yy=np.minimum(np.clip((np.arange(t,b)-t)/pad,0,1),np.clip((b-1-np.arange(t,b))/pad,0,1))
    mask=(yy[:,None]*xx[None,:])[:,:,None]
    a[t:b,l:r]=large*mask+a[t:b,l:r]*(1-mask)
    return Image.fromarray(np.clip(a,0,255).astype('uint8')),iterations+1
regions={'inventory-frame':[(175,166,1160,697)],'quests-frame':[(1101,124,1230,182),(843,475,1502,665),(1180,668,1786,753)]}
for key,rects in regions.items():
    source='inventory' if key.startswith('inventory') else 'quests'
    clean=PACKAGE/'assets'/f'{source}-clean-skin.png'
    paper=Image.open(clean).convert('RGB').crop((1290,100,1354,150))
    previous=CLIENT/(ART+key+'.png');base=Image.open(previous).convert('RGB');before=np.array(base);iterations=[]
    for rect in rects:base,count=smooth_paper(base,rect,paper);iterations.append(count)
    # Keep every pixel of the lower original frame, including its inner gold rule.
    lower=758 if source=='inventory' else 754
    base.paste(Image.fromarray(before).crop((0,lower,base.width,base.height)),(0,lower))
    allowed=np.zeros((base.height,base.width),dtype=bool)
    for x0,y0,x1,y1 in rects:allowed[max(0,y0-4):min(base.height,y1+4),max(0,x0-4):min(base.width,x1+4)]=True
    assert np.array_equal(before[~allowed],np.array(base)[~allowed])
    path=ART+key+'.png';base.save(stage(path))
    meta=(CLIENT/(path+'.meta')).read_text(encoding='utf-8-sig')
    meta=re.sub(r'maxTextureSize: \d+','maxTextureSize: 4096',meta)
    stage(path+'.meta').write_text(meta,encoding='utf-8')
    assets.append(dict(path=path,base_path=str(previous),base_sha256=sha(previous),clean_source=str(clean),clean_source_sha256=sha(clean),paper_rect=[1290,100,1354,150],regions=rects,harmonic_relaxation_iterations=iterations,sha256=sha(STAGED/path),native_size=list(base.size),pixels_outside_regions_and_feather_unchanged=True,new_ai_generation=False))
files=[];guard=[]
for p in sorted(STAGED.rglob('*')):
    if not p.is_file():continue
    r=p.relative_to(STAGED).as_posix();h=sha(CLIENT/r)
    files.append(dict(path=r,sha256=sha(p),action='replace',expected_target_sha256=h));guard.append(dict(path=r,sha256=h))
for r in ['Assets/Scripts/UI/Ugui/Gameplay/GameplayWindow.cs','Assets/Scripts/UI/Ugui/Gameplay/GameplayUiRoot.cs','Assets/Tests/EditMode/Battle/GameplayWindowTests.cs']:
    guard.append(dict(path=r,sha256=sha(CLIENT/r)))
(ROOT/'install-manifest.json').write_text(json.dumps(dict(staging_root=str(STAGED),client_root=str(CLIENT),source_guard='sourceguard.json',files=files),ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'sourceguard.json').write_text(json.dumps(dict(client_root=str(CLIENT),files=guard),ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'asset-manifest.json').write_text(json.dumps(dict(operation='Deterministic smoothing of prior derivative paper only; no AI edit or resize.',assets=assets),ensure_ascii=False,indent=2),encoding='utf-8')
# Confirm that the only code edits are the two badge geometry/size substitutions.
assert new==old.replace('MissionStatus(detail.Status), badgeX + 2, 131, 122, 45, 25, Ink','MissionStatus(detail.Status), badgeX + 15, 131, 96, 45, 20, Ink').replace('badgeText.fontSizeMin = 18; badgeText.fontSizeMax = 25;','badgeText.fontSizeMin = 16; badgeText.fontSizeMax = 20;')
(ROOT/'validation.json').write_text(json.dumps(dict(status='passed',files=len(files),source_guard_files=len(guard),code_change='badge inner padding and font only',public_api_and_business_unchanged=True,frame_outside_regions_pixel_identical=True,new_ai_generation=False,client_written=False,unity_started=False,post_polish_capture_pending=True),ensure_ascii=False,indent=2),encoding='utf-8')
print(len(files),len(guard))
