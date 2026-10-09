from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(BASE));import production as p
p.ROOT=ROOT
STYLE='D:/work/image/designs/gameplay-ui/04-guild.png'
GX,GY=57344,32768
def setup():
    for d in ['native','references','prompts','guides','evidence','tiles','qa']:(ROOT/d).mkdir(parents=True,exist_ok=True)
    h=p.read(BASE/'handoff.json');layout=Path(h['layout']['file']);assert p.sha(layout)==h['layout']['sha256']
    plan=Path(h['plan']['file']);assert p.sha(plan)==h['plan']['sha256']
    tile=next(x for x in p.read(plan)['tiles'] if x['id']=='r09_c15');assert tile['finalPixelRect']==[GX,GY,4096,4096]
    west=BASE/'tiles/current/region-v1/r09_c14-candidate.png';assert p.sha(west)=='21cf56bc1c52e49fb025d02f68f445855b268f694c0e690b0a1527da4c8c11d8'
    state={'west':{'source':str(west),'sha256':p.sha(west),'stable':True,'confirmation':'Root assigned immutable west edge on2026-10-08; no north source available'}}
    scale=1254/65536;box=[v*scale for v in [GX-115,GY-115,GX+4211,GY+4211]];im=Image.open(layout).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC)
    dest=ROOT/'references/layout-only.png';im.save(dest);p.derived(dest,[layout],{'method':'layout geometry crop/resample only','sourceBoxLTRB':box,'globalBoxLTRB':[GX-115,GY-115,GX+4211,GY+4211],'neverFinalArt':True})
    src=Image.open(west).convert('RGB');dest=ROOT/'references/west-preview.png';src.resize((1254,1254),Image.Resampling.LANCZOS).save(dest);p.derived(dest,[west],{'method':'preview downscale only','neverFinalArt':True})
    crop=(3981,0,4096,4096);anchor=ROOT/'references/west-115-native.png';src.crop(crop).save(anchor);p.derived(anchor,[west],{'method':'exact integer boundary crop','boxLTRB':crop});state['west'].update(anchor=str(anchor),anchorSha256=p.sha(anchor))
    im.paste(Image.open(anchor).resize((33,1188),Image.Resampling.LANCZOS),(0,33));dest=ROOT/'references/layout-anchors-only.png';im.save(dest);p.derived(dest,[ROOT/'references/layout-only.png',west],{'method':'layout reference with downscaled native west115px strip','neverFinalArt':True})
    p.write(ROOT/'evidence/boundary-state.json',state);p.write(ROOT/'plan.json',{'tile':tile,'core':1024,'halo':115,'nativePatch':[1254,1254],'grid':[4,4],'formalAccepted':False});p.write(ROOT/'evidence/model-verification.json',{'configSnapshot':p.read(p.REPO/'config/image-generation.json'),'batch':'continuation of builtin_q64 parallel20261005 same batch','inheritedVerification':str(BASE/'evidence/model-verification.json'),'inheritedVerificationSha256':p.sha(BASE/'evidence/model-verification.json'),'actualSelectorsExposed':False,'actualModel':None,'actualQuality':None});update('structure_pending')
def update(stage='native_details'):
    names=sorted(f.stem for f in (ROOT/'native').glob('p??.png'));p.write(ROOT/'progress.json',{'updatedAt':p.stamp(),'tile':'r09_c15','nativeDetailPatches':len(names),'expectedPatches':16,'completePixelCandidateTiles':int((ROOT/'tiles/r09_c15-candidate.png').exists()),'formalAccepted':0,'wholeCityComplete':False,'clientAccepted':False,'stage':stage});p.write(ROOT/'current-work.json',{'updatedAt':p.stamp(),'tile':'r09_c15','stage':stage,'completedPatches':names,'next':next((f'p{r}{c}' for r in range(1,5) for c in range(1,5) if f'p{r}{c}' not in names),'assemble_and_qa')})
    if names:
        im=Image.new('RGB',(4096,4096),(214,218,216));d=ImageDraw.Draw(im)
        for r in range(1,5):
            for c in range(1,5):
                n=f'p{r}{c}';f=ROOT/'native'/f'{n}.png'
                if f.exists():im.paste(Image.open(f).convert('RGB').crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
                else:d.text(((c-1)*1024+40,(r-1)*1024+40),n+' PENDING',fill=(60,60,60))
        dest=ROOT/f'current-preview-{len(names):02d}.png';im.resize((1254,1254),Image.Resampling.LANCZOS).save(dest);p.derived(dest,[ROOT/'native'/f'{n}.png' for n in names],{'method':'review-only core montage downscale','containsMissingPlaceholders':len(names)<16})
        state=p.read(ROOT/'current-work.json');state['preview']=str(dest);p.write(ROOT/'current-work.json',state)
def savecall(name,call):
    (ROOT/'prompts'/f'{name}.prompt.txt').write_text(call['prompt'],encoding='utf8');p.write(ROOT/'prompts'/f'{name}.call.json',call)
def ingest(source,name,role='native_detail'):
    assert not (ROOT/('references' if role=='layout_only' else 'native')/f'{name}.png').exists()
    call=p.read(ROOT/'prompts'/f'{name}.call.json');p.write(ROOT/'evidence'/f'{name}.tool-result.json',{'sourcePath':str(source),'toolHint':'Generated images are saved under the Codex generated_images directory by default. The generated image is displayed in the tool result.','outputSha256':p.sha(source),'tool':'image_gen.imagegen','savedAt':p.stamp()});dest=p.ingest(source,name,ROOT/'prompts'/f'{name}.prompt.txt',call['referenced_image_paths'],role);rec=p.read(str(dest)+'.generation.json');rec['submittedParameters'].update(call);rec['evidence']['toolOutputHintFile']=str(ROOT/'evidence'/f'{name}.tool-result.json');rec['visualInspection']={'at':p.stamp(),'scope':'actual generated output inspected against native guide/style; whole seam review pending'};p.write(str(dest)+'.generation.json',rec);update();print(dest)
def guides():
    state=p.read(ROOT/'evidence/boundary-state.json');src=ROOT/'references/structure.png';im=Image.open(src).convert('RGB').resize((4326,4326),Image.Resampling.LANCZOS)
    for k,pos in [('west',(0,115))]:
        fp=Path(state[k]['anchor']);assert p.sha(fp)==state[k]['anchorSha256'];im.paste(Image.open(fp).convert('RGB'),pos)
    dest=ROOT/'references/layout-canvas-only.png';im.save(dest);p.derived(dest,[src,state['west']['anchor']],{'method':'4326 square layout-only upscale with exact115 native edge anchors','neverFinalArt':True})
    index=[]
    for r in range(1,5):
        for c in range(1,5):
            n=f'p{r}{c}';box=((c-1)*1024,(r-1)*1024,(c-1)*1024+1254,(r-1)*1024+1254);fp=ROOT/'guides'/f'{n}.png';im.crop(box).save(fp);p.derived(fp,[dest],{'method':'integer geometry guide crop','boxLTRB':box,'neverFinalArt':True});index.append({'id':n,'globalCoreXYWH':[GX+(c-1)*1024,GY+(r-1)*1024,1024,1024],'file':str(fp)})
    p.write(ROOT/'guides/index.json',{'patches':index,'finalUseForbidden':True});update('guides_ready')
def prepare(name,scene):
    r,c=int(name[1]),int(name[2]);state=p.read(ROOT/'evidence/boundary-state.json');guide=Path(state.get('guideOverrides',{}).get(name,str(ROOT/'guides'/f'{name}.png')));refs=[guide.as_posix(),STYLE];notes=[]
    for dr,dc,direction,match in [(0,-1,'LEFT','left230px matches its right230px'),(-1,0,'UPPER','top230px matches its bottom230px'),(0,1,'RIGHT','right230px matches its left230px'),(1,0,'LOWER','bottom230px matches its top230px')]:
        nr,nc=r+dr,c+dc;f=ROOT/'native'/f'p{nr}{nc}.png'
        if 1<=nr<=4 and 1<=nc<=4 and f.exists():refs.append(f.as_posix());notes.append(f'Image{len(refs)} is completed {direction} neighbor; target {match}.')
    for key,active in [('west',c==1)]:
        if active:
            fp=Path(state[key]['source']);assert p.sha(fp)==state[key]['sha256'];src=Image.open(fp).convert('RGB');start=(c-1)*1024 if key=='north' else (r-1)*1024;lo=max(0,start-115);hi=min(4096,start+1139);box=(lo,2957,hi,4096) if key=='north' else (2957,lo,4096,hi);dest=ROOT/'references'/f'{key}-{name}-context.png';src.crop(box).save(dest);p.derived(dest,[fp],{'method':'exact neighbor native context','boxLTRB':box});refs.append(dest.as_posix());notes.append(f'Image{len(refs)} is {key.upper()} TILE actual native context. Its '+('bottom115px corresponds to target top115px' if key=='north' else 'right115px corresponds to target left115px')+'; maintain those true endpoints and materials. Guide paste boundary is artificial, not an object.')
    prompt=f'Use case: sketch-to-render. Native detail patch {name} of r09_c15 for continuous isometric Taoist Q fantasy map 五行奇谈. Image1 EXACT geometry/crop guide, never final pixels. Image2 approved PRIMARY painting style only, never UI. '+' '.join(notes)+' REDRAW ONLY Image1 at identical camera, scale and crop with crisp native detail. Scene: '+scene+' Keep exact object counts, position, silhouettes, edge endpoints, tile groove arrangement and shadows. Neighbor inputs constrain overlap only, never replace target composition. Bright clean rounded full Taoist Q handpainting, restrained delicate brushwork, warm daylight, cool soft shadows. Smooth clean materials and clear bevels. No extra objects, denser foliage, added grooves, text, UI, grain, photorealism, blur or sharpening halos. Keep cropped objects cropped. Output exactly1254x1254 pixels, same square crop.'
    call={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False};savecall(name,call);print(json.dumps(call))
def assemble():
    im=Image.new('RGB',(4096,4096));sources=[]
    for r in range(1,5):
        for c in range(1,5):
            fp=ROOT/'native'/f'p{r}{c}.png';src=Image.open(fp).convert('RGB');assert src.size==(1254,1254);im.paste(src.crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024));sources.append(fp)
    dest=ROOT/'tiles/r09_c15-candidate.png';im.save(dest);p.derived(dest,sources,{'method':'16native1024core integer assembly, no scaling','sourceCoreBoxLTRB':[115,115,1139,1139],'globalRectXYWH':[GX,GY,4096,4096],'candidateOnly':True});update('complete_pixel_candidate_pending_qa')
if __name__=='__main__':
    if sys.argv[1]=='setup':setup()
    elif sys.argv[1]=='guides':guides()
    elif sys.argv[1]=='prepare':prepare(sys.argv[2],sys.argv[3])
    elif sys.argv[1]=='ingest':ingest(sys.argv[2],sys.argv[3],sys.argv[4] if len(sys.argv)>4 else 'native_detail')
    elif sys.argv[1]=='assemble':assemble()

