from pathlib import Path
import sys,json,os,uuid,time
sys.dont_write_bytecode=True
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(BASE));import production as p
p.ROOT=ROOT
STYLE='D:/work/image/designs/gameplay-ui/04-guild.png'
GX,GY=45056,40960
def setup():
    for d in ['native','references','prompts','guides','evidence','tiles','qa']:(ROOT/d).mkdir(parents=True,exist_ok=True)
    h=p.read(BASE/'handoff.json');layout=Path(h['layout']['file']);assert p.sha(layout)==h['layout']['sha256'];tile=next(x for x in p.read(h['plan']['file'])['tiles'] if x['id']=='r11_c12');assert tile['finalPixelRect']==[GX,GY,4096,4096]
    north=BASE/'tiles/current/region-v4/r10_c12-candidate.png';east=BASE/'r11_c13/repairs/north/joint-v3/r11_c13-candidate.png'
    assert p.sha(north)=='b7a40911d0e1bad2c8e79b5df2e5357674cb8a25f69d3cf819fcd1fbb1cc764a';assert p.sha(east)=='3a4c829df67312c37c9b25b390f0dc46b7e7a97308989fb3d2e62a0ca5f3fa8e'
    state={k:{'source':str(f),'sha256':p.sha(f),'stable':True} for k,f in [('north',north),('east',east)]};state['note']='North and east actual boundaries locked. r11c13 upper-right may change in r11c14 joint but its left627 is unaffected. West r11c11 is in progress and will be joined after its completion.'
    scale=1254/65536;box=[v*scale for v in [GX-115,GY-115,GX+4211,GY+4211]];im=Image.open(layout).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC)
    f=ROOT/'references/layout-only.png';im.save(f);p.derived(f,[layout],{'method':'layout-only geometry crop/resample','sourceBoxLTRB':box,'globalBoxLTRB':[GX-115,GY-115,GX+4211,GY+4211],'neverFinalArt':True})
    for k,fp in [('north',north),('east',east)]:
        src=Image.open(fp).convert('RGB');f=ROOT/'references'/f'{k}-preview.png';src.resize((1254,1254),Image.Resampling.LANCZOS).save(f);p.derived(f,[fp],{'method':'preview downscale only','neverFinalArt':True});crop=(0,3981,4096,4096) if k=='north' else (0,0,115,4096);anchor=ROOT/'references'/f'{k}-115-native.png';src.crop(crop).save(anchor);p.derived(anchor,[fp],{'method':'integer native boundary crop','boxLTRB':crop});state[k].update(anchor=str(anchor),anchorSha256=p.sha(anchor))
    im.paste(Image.open(state['north']['anchor']).resize((1188,33),Image.Resampling.LANCZOS),(33,0));im.paste(Image.open(state['east']['anchor']).resize((33,1188),Image.Resampling.LANCZOS),(1221,33));f=ROOT/'references/layout-anchors-only.png';im.save(f);p.derived(f,[ROOT/'references/layout-only.png',north,east],{'method':'layout reference with downscaled actual north/east115 anchors','neverFinalArt':True})
    p.write(ROOT/'evidence/boundary-state.json',state);p.write(ROOT/'plan.json',{'tile':tile,'core':1024,'halo':115,'nativePatch':[1254,1254],'grid':[4,4],'formalAccepted':False});p.write(ROOT/'evidence/model-verification.json',{'configSnapshot':p.read(p.REPO/'config/image-generation.json'),'batch':'continuation of builtin_q64 parallel20261005 same batch','inheritedVerification':str(BASE/'evidence/model-verification.json'),'inheritedVerificationSha256':p.sha(BASE/'evidence/model-verification.json'),'actualSelectorsExposed':False,'actualModel':None,'actualQuality':None});update('structure_pending')

def update(stage='native_details'):
    names=sorted(f.stem for f in (ROOT/'native').glob('p??.png'));p.write(ROOT/'progress.json',{'updatedAt':p.stamp(),'tile':'r11_c12','nativeDetailPatches':len(names),'expectedPatches':16,'completePixelCandidateTiles':int((ROOT/'tiles/r11_c12-candidate.png').exists()),'formalAccepted':0,'wholeCityComplete':False,'clientAccepted':False,'stage':stage});p.write(ROOT/'current-work.json',{'updatedAt':p.stamp(),'tile':'r11_c12','stage':stage,'completedPatches':names,'next':next((f'p{r}{c}' for r in range(1,5) for c in range(1,5) if f'p{r}{c}' not in names),'assemble_and_qa')})
    if names:
        im=Image.new('RGB',(4096,4096),(214,218,216));d=ImageDraw.Draw(im)
        for r in range(1,5):
            for c in range(1,5):
                n=f'p{r}{c}';f=ROOT/'native'/f'{n}.png'
                if f.exists():im.paste(Image.open(f).convert('RGB').crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
                else:d.text(((c-1)*1024+40,(r-1)*1024+40),n+' PENDING',fill=(60,60,60))
        dest=ROOT/f'current-preview-{len(names):02d}.png';temp=ROOT/(dest.stem+'.write-'+uuid.uuid4().hex+'.png');im.resize((1254,1254),Image.Resampling.LANCZOS).save(temp)
        for attempt in range(4):
            try:os.replace(temp,dest);break
            except OSError:
                if attempt==3:raise
                time.sleep(.5)
        p.derived(dest,[ROOT/'native'/f'{n}.png' for n in names],{'method':'review-only core montage downscale','containsMissingPlaceholders':len(names)<16})
        state=p.read(ROOT/'current-work.json');state['preview']=str(dest);p.write(ROOT/'current-work.json',state)
def savecall(name,call):
    (ROOT/'prompts'/f'{name}.prompt.txt').write_text(call['prompt'],encoding='utf8');p.write(ROOT/'prompts'/f'{name}.call.json',call)
def ingest(source,name,role='native_detail'):
    assert not (ROOT/('references' if role=='layout_only' else 'native')/f'{name}.png').exists()
    call=p.read(ROOT/'prompts'/f'{name}.call.json');p.write(ROOT/'evidence'/f'{name}.tool-result.json',{'sourcePath':str(source),'toolHint':'Generated images are saved under the Codex generated_images directory by default. The generated image is displayed in the tool result.','outputSha256':p.sha(source),'tool':'image_gen.imagegen','savedAt':p.stamp()});dest=p.ingest(source,name,ROOT/'prompts'/f'{name}.prompt.txt',call['referenced_image_paths'],role);rec=p.read(str(dest)+'.generation.json');rec['submittedParameters'].update(call);rec['evidence']['toolOutputHintFile']=str(ROOT/'evidence'/f'{name}.tool-result.json');rec['visualInspection']={'at':p.stamp(),'scope':'actual generated output inspected against native guide/style; whole seam review pending'};p.write(str(dest)+'.generation.json',rec);update();print(dest)
def guides():
    state=p.read(ROOT/'evidence/boundary-state.json');src=ROOT/'references/structure.png';im=Image.open(src).convert('RGB').resize((4326,4326),Image.Resampling.LANCZOS)
    for k,pos in [('north',(115,0)),('east',(4211,115))]:
        f=Path(state[k]['anchor']);assert p.sha(f)==state[k]['anchorSha256'];im.paste(Image.open(f).convert('RGB'),pos)
    dest=ROOT/'references/layout-canvas-only.png';im.save(dest);p.derived(dest,[src,state['north']['anchor'],state['east']['anchor']],{'method':'4326square layout-only upscale plus exact115 native north/east anchors','neverFinalArt':True});index=[]
    for r in range(1,5):
        for c in range(1,5):
            n=f'p{r}{c}';box=((c-1)*1024,(r-1)*1024,(c-1)*1024+1254,(r-1)*1024+1254);f=ROOT/'guides'/f'{n}.png';im.crop(box).save(f);p.derived(f,[dest],{'method':'integer layout-only guide crop','boxLTRB':box,'neverFinalArt':True});index.append({'id':n,'globalCoreXYWH':[GX+(c-1)*1024,GY+(r-1)*1024,1024,1024],'file':str(f)})
    p.write(ROOT/'guides/index.json',{'patches':index,'finalUseForbidden':True});update('guides_ready')

def prepare(name,scene):
    r,c=int(name[1]),int(name[2]);state=p.read(ROOT/'evidence/boundary-state.json');guide=ROOT/'guides'/f'{name}.png';refs=[guide.as_posix(),STYLE];notes=[]
    for dr,dc,direction,match in [(0,-1,'LEFT','left230px matches its right230px'),(-1,0,'UPPER','top230px matches its bottom230px'),(0,1,'RIGHT','right230px matches its left230px'),(1,0,'LOWER','bottom230px matches its top230px')]:
        nr,nc=r+dr,c+dc;f=ROOT/'native'/f'p{nr}{nc}.png'
        if 1<=nr<=4 and 1<=nc<=4 and f.exists():refs.append(f.as_posix());notes.append(f'Image{len(refs)} is completed {direction} neighbor; target {match}.')
    for key,active in [('north',r==1),('east',c==4)]:
        if active:
            fp=Path(state[key]['source']);assert p.sha(fp)==state[key]['sha256'];src=Image.open(fp).convert('RGB');start=(c-1)*1024 if key=='north' else (r-1)*1024;lo=max(0,start-115);hi=min(4096,start+1139);box=(lo,2957,hi,4096) if key=='north' else (0,lo,1139,hi);dest=ROOT/'references'/f'{key}-{name}-context.png';src.crop(box).save(dest);p.derived(dest,[fp],{'method':'exact native neighbor context','boxLTRB':box});refs.append(dest.as_posix());notes.append(f'Image{len(refs)} is {key.upper()} tile actual context. Its '+('bottom115px matches target top115px' if key=='north' else 'left115px matches target right115px')+'. Preserve real edge endpoints; guide pasted edge is artificial, never paint a straight pasted boundary.')
    prompt=f'Use case: sketch-to-render. Native detail patch {name} of r11_c12 for continuous isometric Taoist Q game map 五行奇谈. Image1 EXACT crop/geometry guide, never final pixels. Image2 approved PRIMARY bright clean rounded handpaint style only, no UI. '+' '.join(notes)+' Redraw only Image1 at identical camera, crop, scale and silhouettes with crisp native detail. Scene: '+scene+' Preserve exact object counts, arrangements, tile grooves, outlines and shadows. Neighbor images constrain overlap, never replace target composition. Warm daylight, clean cool shadows, rounded full forms, broad bevels, smooth delicate brushwork and restrained material detail. No new objects, added grooves, dense decoration, text, UI, border, noise, photorealism, blur, or halos. Keep cropped objects cropped. Same square crop.'
    call={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False};savecall(name,call);print(json.dumps(call))

def assemble():
    im=Image.new('RGB',(4096,4096));sources=[]
    for r in range(1,5):
        for c in range(1,5):
            fp=ROOT/'native'/f'p{r}{c}.png';src=Image.open(fp).convert('RGB');assert src.size==(1254,1254);im.paste(src.crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024));sources.append(fp)
    dest=ROOT/'tiles/r11_c12-candidate.png';im.save(dest);p.derived(dest,sources,{'method':'16native1024core integer assembly, no scaling','sourceCoreBoxLTRB':[115,115,1139,1139],'globalRectXYWH':[GX,GY,4096,4096],'candidateOnly':True});update('complete_pixel_candidate_pending_qa')
if __name__=='__main__':
    if sys.argv[1]=='setup':setup()
    elif sys.argv[1]=='guides':guides()
    elif sys.argv[1]=='prepare':prepare(sys.argv[2],sys.argv[3])
    elif sys.argv[1]=='ingest':ingest(sys.argv[2],sys.argv[3],sys.argv[4] if len(sys.argv)>4 else 'native_detail')
    elif sys.argv[1]=='assemble':assemble()
