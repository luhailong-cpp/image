"""Local wall batch receipt/QA bookkeeping. Only native integer crop/paste."""
import os
os.environ['ISLAND_PROGRESS_FILE']='progress-wall-oct16.json'
from workflow import *
import sys, shutil, subprocess
Q=ROOT/'qa'/'wall-oct16'
Q.mkdir(exist_ok=True)
PROG=ROOT/'progress-wall-oct16.json'
if not PROG.exists():
    write(PROG,{'agent':'wall_oct16','tiles':['r09_c10','r10_c10','r11_c10','r12_c10'],'generatedNativeCount':0,'selected':{},'notPassed':{},'inFlight':[],'actualModel':None,'formalAccepted':False})
cmd=sys.argv[1] if len(sys.argv)>1 else ''
if cmd=='prepare':
    pid,v,desc,*neighbors=sys.argv[2:]
    assert pid[:7] in ['r09_c10','r10_c10','r11_c10','r12_c10']
    assert not (ROOT/'native'/f'{pid}_{v}.png').exists()
    p=patch(pid);box=p['nativeGlobalBox'];base=ROOT/'guides'/f'{pid}.layout-only.png'
    im=Image.open(base).convert('RGB');parts=[{'file':str(base),'sha256':sha(base),'role':'layout only, never final pixels'}]
    for name in neighbors:
        src=ROOT/'native'/name;rec=read(Path(str(src)+'.generation.json'));nb=rec['coordinate']['nativeGlobalBox']
        core=rec['coordinate']['coreGlobalBox']
        inter=[max(box[0],core[0]),max(box[1],core[1]),min(box[2],core[2]),min(box[3],core[3])]
        assert inter[0]<inter[2] and inter[1]<inter[3]
        crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-box[0],inter[1]-box[1]]
        im.paste(Image.open(src).convert('RGB').crop(crop),dest)
        parts.append({'file':str(src),'sha256':sha(src),'sourceCrop':crop,'destination':dest})
    guide=ROOT/'guides'/f'{pid}.native-core-context-wall16-{v}.png';assert not guide.exists();im.save(guide)
    write(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sha(guide),'derivedFrom':parts,'nativeGlobalBox':box,'usableAsFinalArt':False,'operation':'native integer overlapping crop/paste context only'})
    refs=[{'file':str(guide),'sha256':sha(guide),'role':'EXACT edit target; keep canvas framing; sharp positioned overlap immutable; redraw blurry area'}]+read(ROOT/'references.json')
    prompt=f'''Use case: precise-object-edit. Output exactly one 1254 x 1254 opaque square CLOSE-UP game-art crop. Image 1 is the edit target and exact camera crop. Preserve the framing, scale and every sharp edge-overlap. Redraw all blurred central pixels as genuinely crisp hand-painted native detail. Continue shapes seamlessly across sharp/blur transition without reproducing a rectangular guide boundary. Never zoom out or change object size. This target shows only about 27 x 27 pixels of the full map. All content must remain tightly cropped.
LOCAL CONTENT: {desc}
All sharp top/bottom/left/right strips in image 1 are positioned native adjacent art and are the geometric authority; preserve the exact object contours, stone-joint endpoints, spacing, thickness and shade at those strips. Continue them into the blurry area with identical perspective and materials. No extra scene, building, object or foreground framing. No composite panels. Full square output.
Images 2,3,4 are ONLY full-map layout, material, approved Q Daoist painting-style references; they must NEVER cause any of their surrounding scene or buildings to be added into this tiny crop. Daylight, clean natural pale grey/blue-grey stone, soft hand-painted shading, rounded graceful forms, restrained gold. No photoreal grain, blur, excessive scratches, plastic, text, UI, people, animals, watermark. Exact patch {pid}, core local [115,115,1139,1139).'''
    pf=ROOT/'prompts'/f'{pid}_{v}.prompt.txt';pf.write_text(prompt,encoding='utf-8')
    write(ROOT/'prompts'/f'{pid}_{v}.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
    args={'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}
    write(ROOT/'prompts'/f'{pid}_{v}.args.json',args)
    print(json.dumps({'pid':pid,'guide':str(guide),'args':str(ROOT/'prompts'/f'{pid}_{v}.args.json')}))
elif cmd=='repair':
    pid,v,target,desc=sys.argv[2:]
    f=ROOT/'native'/target;assert f.exists()
    assert not (ROOT/'native'/f'{pid}_{v}.png').exists()
    prompt=f'Use case: precise-object-edit. Output one opaque 1254 x 1254 image. Image 1 is the exact edit target. Keep its canvas framing and scale completely fixed. Make only this local correction: {desc} Preserve every other contour, color, material and small detail. No zoom out, no new objects, no panels, no text or UI. Seamless clean Q Daoist hand-painted daylight game map close-up.'
    refs=[{'file':str(f),'sha256':sha(f),'role':'exact edit target; preserve all except specified correction'}]
    pf=ROOT/'prompts'/f'{pid}_{v}.prompt.txt';pf.write_text(prompt,encoding='utf-8')
    write(ROOT/'prompts'/f'{pid}_{v}.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
    write(ROOT/'prompts'/f'{pid}_{v}.args.json',{'prompt':prompt,'referenced_image_paths':[str(f)],'transparent_background':False})
    print(json.dumps({'args':str(ROOT/'prompts'/f'{pid}_{v}.args.json')}))
elif cmd=='repair_anchored':
    pid,v,target,desc,*neighbors=sys.argv[2:]
    assert pid[:7] in ['r09_c10','r10_c10','r11_c10','r12_c10']
    src=ROOT/'native'/target;im=Image.open(src).convert('RGB');box=patch(pid)['nativeGlobalBox']
    parts=[{'file':str(src),'sha256':sha(src),'role':'existing generated edit target, preserve except requested correction'}]
    for name in neighbors:
        nf=ROOT/'native'/name;rec=read(Path(str(nf)+'.generation.json'));nb=rec['coordinate']['nativeGlobalBox'];cb=rec['coordinate']['coreGlobalBox']
        inter=[max(box[0],cb[0]),max(box[1],cb[1]),min(box[2],cb[2]),min(box[3],cb[3])]
        assert inter[0]<inter[2] and inter[1]<inter[3]
        crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-box[0],inter[1]-box[1]]
        im.paste(Image.open(nf).convert('RGB').crop(crop),dest);parts.append({'file':str(nf),'sha256':sha(nf),'sourceCrop':crop,'destination':dest})
    guide=ROOT/'guides'/f'{pid}.repair-anchor-wall16-{v}.png';assert not guide.exists();im.save(guide)
    write(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sha(guide),'derivedFrom':parts,'usableAsFinalArt':False,'operation':'integer native crop/paste context only'})
    prompt=f'''Use case: precise-object-edit. Output one opaque 1254 x 1254 crop with identical framing, scale and perspective to image 1. It is the exact edit target. Its outer 115px anchor strips come from the true already-selected neighboring cores. Preserve those strips and their exact contour/joint endpoints. Correct the main region so it connects to those strips with NO rectangular boundary. LOCAL CORRECTION: {desc} Preserve all other scene objects and features. Do not shift, zoom or redraw a different scene. Do not fit a whole post/scene into this cropped view. Bright clean Q Daoist hand-painted stone and plant materials, no text, people, UI or watermark.'''
    pf=ROOT/'prompts'/f'{pid}_{v}.prompt.txt';pf.write_text(prompt,encoding='utf-8')
    refs=[{'file':str(guide),'sha256':sha(guide),'role':'exact repair target; true 115px neighboring core anchors immutable; guide never final source'}]
    write(ROOT/'prompts'/f'{pid}_{v}.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
    write(ROOT/'prompts'/f'{pid}_{v}.args.json',{'prompt':prompt,'referenced_image_paths':[str(guide)],'transparent_background':False})
    print(guide)
elif cmd=='receive':
    pid,v,src,hint=sys.argv[2:]
    a=read(ROOT/'prompts'/f'{pid}_{v}.args.json')
    receipt=ROOT/'receipts'/f'{pid}_{v}.wall-oct16.tool.json'
    assert not receipt.exists(),str(receipt)
    write(receipt,{'tool':'image_gen.imagegen','route':'builtin','submittedArguments':a,'output_hint':hint,'actualModel':None,'actualQuality':None,'imageDataOmitted':True,'receivedAt':now()})
    subprocess.run([sys.executable,str(ROOT/'ingest_native_only_20261013.py'),pid,v,src,str(receipt)],check=True)
    d=read(PROG);d['inFlight']=[x for x in d.get('inFlight',[]) if x!=pid+'_'+v];d['updatedAt']=now();d['lastReceived']=pid+'_'+v;write(PROG,d)
elif cmd=='select':
    pid,v,status,note=sys.argv[2:]
    f=ROOT/'native'/f'{pid}_{v}.png'
    assert Image.open(f).size==(1254,1254)
    d=read(PROG)
    d['selected'][pid]={'version':v,'file':str(f),'sha256':sha(f),'status':status,'note':note,'reviewedAt':now()}
    if status!='quick_layout_and_edges_passed':d['notPassed'][pid+'_'+v]=note
    d['updatedAt']=now();d['generatedNativeCount']=len(d['selected']);write(PROG,d)
    qa=Q/f'{pid}-{v}-review.json'
    if not qa.exists():
        prior=ROOT/'qa'/'wall-resume-20261013'/f'{pid}-{v}-review.json'
        if prior.exists():write(qa,{**read(prior),'reusedEvidenceFrom':str(prior)})
    if qa.exists():
        review=read(qa);review['status']=status;review['note']=note;review['reviewedAt']=now();review['reviewer']='wall_oct16'
        if status=='quick_layout_and_edges_passed':
            for edge in review['edges']:
                for src in edge.get('sources',edge.get('source',[])):assert sha(Path(src['file']))==src['sha256']
                edge['status']='passed_actual_native_core_join_visual_review'
        write(qa,review)
    print(json.dumps({'pid':pid,'version':v,'status':status}))
elif cmd=='seam':
    pid,v,*neigh=sys.argv[2:]
    src=ROOT/'native'/f'{pid}_{v}.png';im=Image.open(src).convert('RGB');b=patch(pid)['coreGlobalBox'];out=[]
    for name in neigh:
        ns=ROOT/'native'/name;ni=Image.open(ns).convert('RGB');nb=read(Path(str(ns)+'.generation.json'))['coordinate']['coreGlobalBox']
        if nb[0]==b[2] and nb[1]==b[1]:
            direction='E';e=Image.new('RGB',(512,1024));e.paste(im.crop((883,115,1139,1139)),(0,0));e.paste(ni.crop((115,115,371,1139)),(256,0))
        elif nb[2]==b[0] and nb[1]==b[1]:
            direction='W';e=Image.new('RGB',(512,1024));e.paste(ni.crop((883,115,1139,1139)),(0,0));e.paste(im.crop((115,115,371,1139)),(256,0))
        elif nb[3]==b[1] and nb[0]==b[0]:
            direction='N';e=Image.new('RGB',(1024,512));e.paste(ni.crop((115,883,1139,1139)),(0,0));e.paste(im.crop((115,115,1139,371)),(0,256))
        elif nb[1]==b[3] and nb[0]==b[0]:
            direction='S';e=Image.new('RGB',(1024,512));e.paste(im.crop((115,883,1139,1139)),(0,0));e.paste(ni.crop((115,115,1139,371)),(0,256))
        else:continue
        dest=Q/f'{pid}-{v}-{direction}.png';assert not dest.exists();e.save(dest)
        out.append({'direction':direction,'file':str(dest),'sha256':sha(dest),'sources':[{'file':str(src),'sha256':sha(src)},{'file':str(ns),'sha256':sha(ns)}],'operation':'unscaled adjacent native core crops, 256px on each side','status':'pending_visual_review'})
    write(Q/f'{pid}-{v}-review.json',{'native':str(src),'sha256':sha(src),'edges':out,'status':'pending_visual_review','actualModel':None})
    print(json.dumps(out))
