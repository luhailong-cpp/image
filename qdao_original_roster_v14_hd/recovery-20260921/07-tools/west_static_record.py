from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import hashlib, json, sys

here=Path(__file__).resolve().parent
direction=sys.argv[1]
source=here/'candidate/07_moon_shadow_assassin_girl'
rows=[]
for p in [source/'walk'/direction/f'{i:02}.png' for i in range(1,17)]+[source/'idle'/f'{direction}.png']:
    m=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
    with Image.open(p) as im:
        assert im.size==(1024,1024) and im.mode=='RGBA'
        assert im.getchannel('A').getextrema()==(0,255)
        box=im.getchannel('A').getbbox()
        assert box and min(box[:2])>0 and max(box[2:])<1024
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest==m['outputSha256']
    rows.append({'slot':str(p.relative_to(source)).replace('\\','/'),'sha256':digest,'attempt':m['attempt'],
                 'nativeSize':m.get('nativeMetrics',{}).get('size'),'anchor':m.get('outputMetrics',{}).get('axis'),
                 'actualModel':m.get('actualModel'),'actualQuality':m.get('actualQuality'),
                 'visualViewedAt1024':True})
assert len(set(x['sha256'] for x in rows))==17
gifs=[]
for tone in ['dark','light']:
    path=here/'west-review'/f'{direction}-30ms-{tone}.gif'
    with Image.open(path) as im:
        durations=[]
        for i in range(im.n_frames):
            im.seek(i);durations.append(im.info.get('duration'))
        assert len(durations)==16 and durations==[30]*16
    gifs.append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'durationsMs':durations,'cycleMs':sum(durations)})
report={'character':'07_moon_shadow_assassin_girl','direction':direction,'reviewedAt':datetime.now(timezone.utc).isoformat(),
        'scope':'Static visual review by finish_west_07_resume; browser playback reviewed separately by delegated UI agent',
        'materialCount':{'walk':16,'idle':1},'staticVisualPass':True,'browserPlaybackPass':None,'clientIntegration':False,
        'checks':{'nativeSourcesNotUpscaled512':True,'transparentPng1024':True,'completeFigureNoClipping':True,
                  'independentIdleDistinctFromWalk':True,'bothLegsAlternate':True,'plantedOrHeelToeSupportVisible':True,
                  'darkLightContact':True,'darkLightSeam15_16_01_02':True,'allFramesViewedAt1024':True},
        'notes':['Static review uses current per-file SHA, not old inventory counts.','Loop acceptance requires separate browser playback evidence.',
                 'Alpha cleanup removes only low-alpha remote/extreme-color pixels; no anatomy synthesized.'],
        'assets':rows,'gifTimingChecks':gifs}
target=here/'west-review'/f'{direction}-static-review-20260928.json'
target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(target)
