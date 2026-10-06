"""Prepare native outpainting requests in dependency order; builtin calls remain tool-driven."""
from pathlib import Path
import sys,json,shutil
from production import ROOT,REPO,read,write,sha,now,deriv
from PIL import Image

def prepare(tile,row,col):
    assert 1<=row<=4 and 1<=col<=4
    folder=ROOT/tile;plan=read(folder/'plan.json');rect=plan['tile']['finalPixelRect']
    ident=f'p{row}{col}';out=folder/'native';out.mkdir(exist_ok=True)
    if (out/(ident+'.png')).exists():raise RuntimeError('Immutable native output already exists; do not overwrite it.')
    guide=folder/'guides'/(ident+'.png');assert Image.open(guide).size==(1254,1254)
    canvas=Image.new('RGBA',(1254,1254),(0,0,0,0));sources=[];regions=[]
    def place(path,box,xy,role):
        path=Path(path);im=Image.open(path).convert('RGBA');piece=im.crop(box);canvas.paste(piece,xy)
        sources.append(path);regions.append(dict(file=str(path),sha256=sha(path),cropLTRB=list(box),pasteXY=list(xy),role=role,scale=1))
    # Internal dependencies are mandatory; diagonal wavefronts permit parallel calls.
    if col>1:
        left=out/f'p{row}{col-1}.png';assert left.is_file(),'Generate left neighbour first'
        place(left,(1024,0,1254,1254),(0,0),'native western overlap')
    if row>1:
        top=out/f'p{row-1}{col}.png';assert top.is_file(),'Generate northern neighbour first'
        place(top,(0,1024,1254,1254),(0,0),'native northern overlap')
    if row>1 and col>1:
        diagonal=out/f'p{row-1}{col-1}.png';assert diagonal.is_file()
        place(diagonal,(1024,1024,1254,1254),(0,0),'authoritative shared native corner')
    if row==1 and plan.get('northCandidate'):
        x0=(col-1)*1024-115;lo=max(0,x0);hi=min(4096,x0+1254)
        place(plan['northCandidate'],(lo,3981,hi,4096),(lo-x0,0),'actual northern tile bottom115')
    if col==1 and plan.get('westCandidate'):
        y0=(row-1)*1024-115;lo=max(0,y0);hi=min(4096,y0+1254)
        place(plan['westCandidate'],(3981,lo,4096,hi),(0,lo-y0),'actual western tile right115')
    if row==1 and col==1 and plan.get('northWestCandidate'):
        place(plan['northWestCandidate'],(3981,3981,4096,4096),(0,0),'actual north-west tile common corner')
    target=out/(ident+'-context.png');canvas.save(target)
    deriv(target,sources,dict(kind='transparent_outpaint_context_from_native_pixels',regions=regions,notProductionPixels=True,sourceUpscaling=False))
    full=Image.open(guide).convert('RGBA');full.alpha_composite(canvas)
    edit=out/(ident+'-edit-target.png');full.convert('RGB').save(edit)
    deriv(edit,[guide,target],dict(kind='same_frame_planning_target_with_actual_native_context',guidePixelsNotProduction=True,contextRegions=regions,sourceUpscaling=False))
    refs=[edit,guide,REPO/'designs/gameplay-ui/04-guild.png']
    prompt=f'''Use case: detail restoration with strict composition preservation. Edit Image1, the exact1254x1254 game map {tile} micro-patch {ident}. Return a fully opaque square with EXACTLY the same crop, camera, scale, object outlines and object positions.
Image1 already contains the complete intended picture. Keep its composition. Its top and/or left strips are real native neighboring pixels; preserve their line endpoints, silhouettes, colors and brushwork. Its remaining soft area needs freshly painted crisp native detail at this1254 resolution. Naturally connect the existing native contours into that area. Heal the temporary straight composite boundary without retaining any rectangular line, ridge or band. Do not change architecture or invent a different continuation.
Image2 reinforces the exact SAME framing and geometry. This is a tightly cropped fragment of a much larger scene; objects intentionally exit the frame. NEVER complete an object inside this square if it is cut off in the reference. Do not zoom out, reveal extra eave ends, add foliage or widen the view. Keep every roof/tile seam, support, road grout line, furniture and crate footprint at the reference positions; actual native Image1 boundary endpoints take precedence for small alignment discrepancies.
Image3 is only the approved art style: clean, bright, rounded Daoist chibi hand painting, ivory/jade/gold materials, controlled highlights and organized subtle brushwork. No UI, writing or characters. Preserve the Mid-Autumn blue-violet evening stones, cobalt water, amber light and jade foliage in Images1/2. Smooth goods stay smooth, fabric stays fabric, foliage stays foliage. Do not add fine noise, blur, sharpening halos, photographic grain, extra decorations, grout branches, text, border or watermark. Generate real native paint detail, retaining the exact Image1 composition.'''
    constraint=plan.get('nativePatchConstraints',{}).get(ident)
    if constraint:prompt+='\nSpecific local geometry constraint: '+constraint
    pp=out/(ident+'.prompt.txt');pp.write_text(prompt,encoding='utf-8')
    call=dict(prompt=prompt,referenced_image_paths=[str(p) for p in refs],transparent_background=False)
    write(out/(ident+'.call.json'),call)
    request=dict(id=ident,tile=tile,startedAt=now(),configSnapshot=read(REPO/'config/image-generation.json'),prompt=str(pp),promptSha256=sha(pp),references=[dict(file=str(p),sha256=sha(p),role=r) for p,r in zip(refs,['exact-frame layout target plus native context','structure guide only','approved style'])],submittedParameters=dict(model=None,quality=None,**call),globalPatchXYWH=[rect[0]-115+(col-1)*1024,rect[1]-115+(row-1)*1024,1254,1254],core=1024,halo=115,contextRegions=regions)
    write(out/(ident+'.request.json'),request);print(json.dumps(call,ensure_ascii=True))

def save(tile,row,col,source):
    out=ROOT/tile/'native';ident=f'p{row}{col}';dst=out/(ident+'.png');assert not dst.exists(),'Refuse to overwrite an existing generated image'
    src=Path(source);im=Image.open(src);im.load();assert im.size==(1254,1254),im.size
    req=read(out/(ident+'.request.json'));shutil.copy2(src,dst)
    rec=dict(file=str(dst),sha256=sha(dst),generatedAt=now(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=req['configSnapshot'],submittedParameters=req['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host-managed; no exposed model/quality selectors or returned metadata.',evidence=dict(sourceOutputPath=str(src),sourceOutputSha256=sha(src),resultId=src.stem),prompt=req['prompt'],promptSha256=req['promptSha256'],references=req['references'],globalPatchXYWH=req['globalPatchXYWH'],sourceUpscaled=False,resizedAfterGeneration=False,status='native_detail_pending_full_seam_QA',formalAccepted=False)
    write(str(dst)+'.generation.json',rec);print(str(dst))

if __name__=='__main__':
    mode,tile,row,col=sys.argv[1:5];row=int(row);col=int(col)
    if mode=='prepare':prepare(tile,row,col)
    elif mode=='save':save(tile,row,col,sys.argv[5])
    else:raise ValueError(mode)
