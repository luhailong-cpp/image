from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
REC = ROOT / 'qdao_original_roster_v14_hd/recovery-20260921'
OLD = REC / '07-tools/candidate/07_moon_shadow_assassin_girl/walk/NW'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def metrics(im):
    a = np.asarray(im.getchannel('A')); yy, xx = np.where(a > 8)
    top, bottom = int(yy.min()), int(yy.max()); height = bottom-top+1
    axis = float(np.median(xx[yy < top+int(height*.42)]))
    return {'size':list(im.size), 'alpha_min':int(a.min()), 'alpha_max':int(a.max()),
            'bbox_alpha_gt8':[int(xx.min()),top,int(xx.max())+1,bottom+1],
            'axis':[axis,bottom], 'subject_height':height}

for frame in ('09','10'):
    attempt=REC/'07-generation'/f'review-20260929-NW{frame}-v1'
    request=json.loads((attempt/'request.json').read_text(encoding='utf-8-sig'));result=json.loads((attempt/'result.json').read_text(encoding='utf-8-sig'))
    raw=attempt/'raw.png';source=Path(result['original_generated_file'])
    if not raw.exists(): shutil.copy2(source,raw)
    assert sha(raw)==sha(source)
    im=Image.open(raw); assert im.mode=='RGBA' and min(im.size)>=1024
    native=metrics(im); assert native['alpha_min']==0 and native['alpha_max']==255
    px=np.array(im);a=px[:,:,3]
    near=np.asarray(Image.fromarray(np.where(a>8,255,0).astype(np.uint8)).filter(ImageFilter.MaxFilter(7)))>0
    remote=(a>0)&(a<=8)&~near
    transparent_near=np.asarray(Image.fromarray(a).filter(ImageFilter.MinFilter(7)))==0
    hi=px[:,:,:3].max(2).astype(int);lo=px[:,:,:3].min(2).astype(int)
    fringe=(a>0)&(a<=8)&transparent_near&(hi>220)&(lo<32)&(hi-lo>180)
    a[remote|fringe]=0
    clean=Image.fromarray(px,'RGBA')
    factor=1024/max(im.size)
    resized=clean.resize(tuple(round(v*factor) for v in im.size),Image.Resampling.LANCZOS)
    sized=metrics(resized);shift=[round(512-sized['axis'][0]),942-sized['axis'][1]]
    box=resized.getchannel('A').getbbox();bounds=[box[0]+shift[0],box[1]+shift[1],box[2]+shift[0],box[3]+shift[1]]
    assert min(bounds[:2])>=0 and max(bounds[2:])<=1024,bounds
    out=Image.new('RGBA',(1024,1024));out.paste(resized,tuple(shift));dest=attempt/'candidate.png';out.save(dest)
    stamp=datetime.now(timezone.utc).isoformat()
    common={'generatedAt':stamp,'generatedAtScope':'post-return metadata recording time; exact tool server timestamp undisclosed',
            'tool':'image_gen.imagegen','route':'builtin','actualModel':None,'actualQuality':None,
            'unverifiedReason':'Host-managed tool did not disclose actual model or quality',
            'configSnapshot':request['configSnapshot'],'submittedParameters':request['submittedParameters'],
            'prompt':str(attempt/'prompt.txt'),'references':request['references'],
            'requestEvidence':{'path':str(attempt/'request.json'),'sha256':sha(attempt/'request.json')},
            'resultEvidence':{'path':str(attempt/'result.json'),'sha256':sha(attempt/'result.json')},
            'nativeMetrics':native,'formalApproval':False,'clientIntegration':False}
    rawrecord={**common,'file':str(raw),'sha256':sha(raw),'originalGeneratedPath':str(source)}
    Path(str(raw)+'.generation.json').write_text(json.dumps(rawrecord,indent=2)+'\n')
    record={**common,'file':str(dest),'sha256':sha(dest),'status':'unselected_candidate_pending_comparison',
            'derivedFrom':{'path':str(raw),'sha256':sha(raw),'generationRecord':str(raw)+'.generation.json'},
            'operation':'native alpha<=8 remote/fringe cleanup; complete canvas uniform downsample; integer translation only; no local geometry edit',
            'wholeCanvasScale':factor,'translationPx':shift,'anchorTarget':[512,942],
            'removedLowAlphaPixels':int((remote|fringe).sum()),'outputMetrics':metrics(out)}
    Path(str(dest)+'.generation.json').write_text(json.dumps(record,indent=2)+'\n')
    print(frame,json.dumps(record['outputMetrics']),sha(dest))

cols=[('08 original',OLD/'08.png'),('09 original',OLD/'09.png'),('09 candidate',REC/'07-generation/review-20260929-NW09-v1/candidate.png'),('10 original',OLD/'10.png'),('10 candidate',REC/'07-generation/review-20260929-NW10-v1/candidate.png'),('11 original',OLD/'11.png')]
for theme,bg,fg in [('light',(243,240,230),(25,25,25)),('dark',(30,34,43),(240,240,240))]:
    canvas=Image.new('RGB',(512*len(cols),548),bg);draw=ImageDraw.Draw(canvas)
    for i,(label,p) in enumerate(cols):
        im=Image.open(p).convert('RGBA').resize((512,512),Image.Resampling.LANCZOS)
        canvas.paste(im,(512*i,36),im);draw.text((512*i+12,10),label,fill=fg)
        draw.line((512*i,36+471,512*(i+1)-1,36+471),fill=(120,120,120))
    dest=REC/'07-generation/review-20260929-NW09-v1'/f'comparison-{theme}.png';canvas.save(dest)
    Path(str(dest)+'.generation.json').write_text(json.dumps({'file':str(dest),'sha256':sha(dest),'derivedFrom':[{'path':str(p),'sha256':sha(p)} for _,p in cols],'operation':'QA-only identical full-canvas downsample to512 and side-by-side composite; no pose synthesis'},indent=2)+'\n')
