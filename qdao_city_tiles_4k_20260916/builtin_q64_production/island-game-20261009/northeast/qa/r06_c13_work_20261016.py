from pathlib import Path
import sys,re
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
TID='r06_c13';PROGRESS=ZONE/'qa/r06_c13-progress-20261016.json'
def selection():return read(ZONE/f'selection-{TID}.json')
def fullpath(tid):
    s=read(ZONE/f'selection-{tid}.json');p=Path(s.get('candidatePath',ZONE/'tiles'/f'{tid}.png'));d=read(p.with_suffix('.png.derivation.json'))
    assert sha(p)==d['sha256'];assert d['internalReview'].startswith('passed');return p
def patched(ident):
    p=ZONE/'native'/f'{ident}.png';rec=read(p.with_suffix('.png.generation.json'));assert sha(p)==rec['sha256'];im=Image.open(p).convert('RGB');a=rec['nativeWorldBox'];tid='_'.join(ident.split('_')[:2]);ev={'file':p.as_posix(),'sha256':sha(p),'nativeWorldBox':a}
    if tid!=TID:
        f=fullpath(tid);d=read(f.with_suffix('.png.derivation.json'));b=d['worldBox'];box=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]
        crop=[box[0]-b[0],box[1]-b[1],box[2]-b[0],box[3]-b[1]];at=[box[0]-a[0],box[1]-a[1]];im.paste(Image.open(f).crop(crop),at);ev['currentFullTileOverride']={'file':f.as_posix(),'sha256':sha(f),'sourceCrop':crop,'targetPaste':at}
    return im,ev
def neighbors(r,c):
    s=selection();up=read(ZONE/'selection-r05_c13.json')['cores'][3][c-1] if r==1 else s['cores'][r-2][c-1]
    left=read(ZONE/'selection-r06_c12.json')['cores'][r-1][3] if c==1 else s['cores'][r-1][c-2]
    right=read(ZONE/'selection-r06_c14.json')['cores'][r-1][0] if c==4 else s['cores'][r-1][c]
    ns=[(i,d) for i,d in [(up,'upper'),(left,'left'),(right,'right')] if i]
    assert up and len(ns)>=2;return ns
mode=sys.argv[1]
if mode=='init':
    p=ZONE/f'selection-{TID}.json';assert not p.exists();write(p,{'tileId':TID,'cores':[[None]*4 for _ in range(4)],'overlays':[],'formalAccepted':False,'selectionIsPartialCandidate':True,'pendingIssues':[],'updatedAtUtc':now()})
    ev=[]
    for t in ['r05_c13','r06_c12','r06_c14']:
        p=fullpath(t);ev.append({'id':t,'file':p.as_posix(),'sha256':sha(p),'derivation':p.with_suffix('.png.derivation.json').as_posix()})
    write(PROGRESS,{'tileId':TID,'worker':'repair_recover16','status':'initialized','inFlight':None,'nativeCoreCount':0,'formalAccepted':False,'actualModel':None,'nativeSize':1254,'core':1024,'halo':115,'worldBox':[49152,20480,53248,24576],'conflictAudit':'No coordinate native/selection/prompts/receipts/guide files or current in-flight record before initialization; inventory mentions are historical missing targets. Not reserved in split.','neighbors':ev,'agentsSha256':sha(ROOT/'AGENTS.md'),'splitSha256':sha(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json'),'updatedAtUtc':now()})
    ref=current_references()[0];im=Image.open(ref['file']);box=[1050,425,1185,560];p=ZONE/'guides/r06_c13.layout-context-nearest.png';assert not p.exists();im.crop(box).resize((1080,1080),Image.Resampling.NEAREST).save(p);write(p.with_suffix('.png.derivation.json'),{'operation':'layout-only nearest context enlargement; never final art','source':ref,'crop':box})
    print(json.dumps({'neighbors':ev,'context':p.as_posix()}));sys.exit()
i=sys.argv[2];assert i.startswith(TID+'_p');r,c=map(int,i.split('_p')[1].split('_v')[0].split('_'));ns=neighbors(r,c)
if mode=='context':
    import math
    p=patch(i);box=[math.floor(p['layoutBox'][0])-8,math.floor(p['layoutBox'][1])-8,math.ceil(p['layoutBox'][2])+8,math.ceil(p['layoutBox'][3])+8];ref=current_references()[0];im=Image.open(ref['file']);out=im.crop(box);out=out.resize((out.width*20,out.height*20),Image.Resampling.NEAREST);dest=ZONE/'guides'/f'{i}.source-context-nearest.png';assert not dest.exists();out.save(dest);write(dest.with_suffix('.png.derivation.json'),{'operation':'layout context only nearest20x from original source, never final art','source':ref,'sourceBox':box,'patchLayoutBox':p['layoutBox']});print(json.dumps({'file':dest.as_posix(),'box':box,'patchBox':p['layoutBox']}))
elif mode=='guide':
    rules=(ROOT/'AGENTS.md').read_text(encoding='utf-8-sig');split=read(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json');assert not any(TID in b['tiles'] for b in split['batches'])
    p=patch(i);a=p['nativeWorldBox'];base=Path(p['guide']);out=Image.open(base).convert('RGB');anchors=[]
    for ident,direction in ns:
        im,e=patched(ident);b=e['nativeWorldBox'];box=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])];crop=[box[0]-b[0],box[1]-b[1],box[2]-b[0],box[3]-b[1]];at=[box[0]-a[0],box[1]-a[1]];out.paste(im.crop(crop),at);e.update(id=ident,direction=direction,sourceCrop=crop,targetPaste=at);anchors.append(e)
    dest=ZONE/'guides'/f'{i}.anchored-layout-only.png';assert not dest.exists();out.save(dest);write(dest.with_suffix('.png.derivation.json'),{'operation':'exact native neighbor overlap anchor copy, full-tile current selected artwork overrides legacy core; blurred region is layout only','base':{'file':base.as_posix(),'sha256':sha(base)},'patch':p,'anchors':anchors,'finalArt':False})
    refs=[{'file':dest.as_posix(),'sha256':sha(dest),'role':'edit target: sharp native top230/left230/right230 when present are invariant anchors; blurred remainder is layout only'},*current_references()[:2]]
    for name in ['designs/mail-ui-v1/01-mail-event.png','designs/team-ui-v2/team-ui-v2.png']:
        f=ROOT/name;refs.append({'file':f.as_posix(),'sha256':sha(f),'role':'approved Daoist Q painting style only; ignore UI/night/text/characters'})
    write(ZONE/'prompts'/f'{i}.inputs.json',refs);q=read(PROGRESS);q.update(status='guide_prepared',currentId=i,agentsSha256=sha(ROOT/'AGENTS.md'),splitSha256=sha(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json'),updatedAtUtc=now());write(PROGRESS,q);print(json.dumps({'guide':dest.as_posix(),'neighbors':ns,'rulesReread':True,'noReservationConflict':True}))
elif mode=='prompt':
    subject=sys.argv[3]
    prompt=f'''Use case: precise-object-edit. Complete Image1 into one native 1254x1254 crisp hand-painted Daoist Q game-map crop, with a 1024px central core and115px halo. Sharp top230,left230,and right230 if present are exact native overlap anchors to retain. Blurred remaining region is coordinate layout only. Repaint blurred content into original crisp details without shifting the composition, camera, object scale or cropped positions. {subject}
Image2 is sole full-map layout authority. Image3 is material and Spring Festival architecture style only, not a coordinate crop. Images4 and5 are approved Daoist Q painting style only; ignore UI, text, characters and night scenery. Keep every sharp native anchor, joint endpoint, object contour, lighting and texture scale; continue them smoothly across the entire crop without straight borders, rectangular panels, shifted joints, enlarged repeated objects or doubled contours. Gentle warm daylight, natural pale gray/cyan fitted stone where indicated; restrained gold/red architecture; lush hand-painted foliage. Equal clear focus throughout. No new buildings, no characters, pots, text, UI or watermark; no nighttime, distance blur or smeared upscaled pixels. Return only finished exact1254-square image.'''
    p=ZONE/'prompts'/f'{i}.prompt.txt';assert not p.exists();p.write_text(prompt,encoding='utf-8');refs=read(ZONE/'prompts'/f'{i}.inputs.json');q=read(PROGRESS);q.update(status='imagegen_prepared',inFlight={'id':i,'preparedAtUtc':now(),'tool':'image_gen.imagegen'},updatedAtUtc=now());write(PROGRESS,q);print(json.dumps({'prompt':prompt,'referenced_image_paths':[e['file'] for e in refs],'transparent_background':False}))
elif mode=='inspect':
    ns=[(v['id'],v['direction']) for v in read(ZONE/'guides'/f'{i}.anchored-layout-only.png.derivation.json')['anchors']]
    cur=Image.open(ZONE/'native'/f'{i}.png').convert('RGB');assert cur.size==(1254,1254);records=[];evidence=[]
    for ident,direction in ns:
        im,e=patched(ident)
        if direction=='upper':
            strip=Image.new('RGB',(1024,512));strip.paste(im.crop((115,883,1139,1139)),(0,0));strip.paste(cur.crop((115,115,1139,371)),(0,256))
        elif direction=='left':
            strip=Image.new('RGB',(512,1024));strip.paste(im.crop((883,115,1139,1139)),(0,0));strip.paste(cur.crop((115,115,371,1139)),(256,0))
        else:
            strip=Image.new('RGB',(512,1024));strip.paste(cur.crop((883,115,1139,1139)),(0,0));strip.paste(im.crop((115,115,371,1139)),(256,0))
        p=ZONE/'qa'/f'{i}.{direction}.png';assert not p.exists();strip.save(p);e.update(direction=direction);records.append(e);evidence.append(p.as_posix())
    write(ZONE/'qa'/f'{i}.joins.json',{'id':i,'nativeSha256':sha(ZONE/'native'/f'{i}.png'),'neighbors':records,'evidence':evidence,'status':'pending_visual_review','resized':False});print(json.dumps({'evidence':evidence}))
elif mode=='accept':
    note=sys.argv[3];p=ZONE/'qa'/f'{i}.joins.json';q=read(p);q.update(status='passed_native_and_recorded_joins_at100pct',reviewNote=note,reviewedAtUtc=now());write(p,q)
    p=ZONE/'native'/f'{i}.png.generation.json';q=read(p);q.update(status='passed_native_layout_and_recorded_joins',qa=(ZONE/'qa'/f'{i}.joins.json').as_posix());write(p,q)
    s=selection();s['cores'][r-1][c-1]=i;s['updatedAtUtc']=now();write(ZONE/f'selection-{TID}.json',s);q=read(PROGRESS);q.update(status='active_native_generation',inFlight=None,currentId=i,nativeCoreCount=sum(bool(v) for row in s['cores'] for v in row),selectedCoreIds=s['cores'],updatedAtUtc=now());write(PROGRESS,q);print(json.dumps({'selected':q['nativeCoreCount'],'id':i}))
