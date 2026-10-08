"""Explicit opt-in production adapter. Builtin image generation remains tool-driven."""
from pathlib import Path
import argparse
import json
import re
import shutil
import sys
import numpy as np
from PIL import Image
import engine

ROOT=engine.ROOT
sys.path.insert(0,str(ROOT))
from production import REPO, read, write, sha, now, deriv

KEYS={'north':'northCandidate','west':'westCandidate','east':'eastCandidate','south':'southCandidate',
      'northwest':'northWestCandidate','northeast':'northEastCandidate','southwest':'southWestCandidate','southeast':'southEastCandidate'}


def setup(tile):
    if not re.fullmatch(r'r\d{2}_c\d{2}',tile):raise ValueError('Invalid tile ID')
    r,c=int(tile[1:3]),int(tile[5:7])
    if not 1<=r<=16 or not 1<=c<=16:raise ValueError('Tile outside16x16')
    folder=ROOT/tile;plan=read(folder/'plan.json');workflow=plan.get('nativeWorkflow',{})
    if not isinstance(workflow,dict) or workflow.get('engine')!='multi_edge_v1':raise ValueError('Plan must explicitly opt in to nativeWorkflow.engine=multi_edge_v1')
    name=workflow['wavefront'];v,h,corner=engine.orientation(name)
    if plan['tile']['id']!=tile or plan['tile']['finalPixelRect']!=[(c-1)*4096,(r-1)*4096,4096,4096]:raise ValueError('Wrong tile coordinates')
    if plan['core']!=1024 or plan['halo']!=115 or plan['nativeGrid']!=[4,4] or plan['nativePatchPixels']!=[1254,1254]:raise ValueError('Unsupported native dimensions')
    neighbors={}
    for role,key in KEYS.items():
        if not plan.get(key):continue
        if role not in [v,h,corner]:raise ValueError('Unsupported extra/opposite neighbor; choose an order with at most two adjacent incoming sides: '+role)
        dr,dc=engine.ROLES[role]
        if not 1<=r+dr<=16 or not 1<=c+dc<=16:raise ValueError('External source beyond map boundary: '+role)
        path=Path(plan[key]);frozen=plan.get(key+'Sha256')
        if not frozen or sha(path)!=frozen:raise ValueError('Missing or changed frozen neighbor hash: '+role)
        neighbors[role]=dict(path=path,reference=engine.base.ref(path),pixels=engine.base.load_native(path,4096))
    return folder,plan,name,neighbors


def workflow_record(name):
    return dict(engine='multi_edge_v1',wavefront=name,aiInputsTransformed=False,
                tools=[engine.base.ref(Path(__file__)),engine.base.ref(Path(engine.__file__)),engine.base.ref(ROOT/'native_assemble.py')])


def prepare(tile,row,col):
    folder,plan,name,neighbors=setup(tile);layout=engine.Layout()
    if not 1<=row<=4 or not 1<=col<=4:raise ValueError('Patch coordinate outside4x4')
    ident=f'p{row}{col}';out=folder/'native';out.mkdir(exist_ok=True)
    protected=[out/(ident+suffix) for suffix in ['.png','.request.json','.call.json','.prompt.txt','-context.png','-edit-target.png']]
    if any(p.exists() for p in protected):raise ValueError('Refuse existing or in-flight patch artifacts')
    guide=folder/'guides'/(ident+'.png')
    if Image.open(guide).size!=(1254,1254):raise ValueError('Guide must be1254; it is planning only')
    ops=engine.context_operations(layout,row-1,col-1,name,neighbors)
    images={role:d['pixels'] for role,d in neighbors.items()};paths={role:d['path'] for role,d in neighbors.items()}
    for op in ops:
        source=op['source']
        if source in images:continue
        path=out/(source+'.png');rec=read(str(path)+'.generation.json')
        if rec['sha256']!=sha(path) or rec.get('nativeWorkflow',{}).get('wavefront')!=name:raise ValueError('Changed or differently oriented native predecessor: '+source)
        images[source]=engine.base.load_native(path,1254);paths[source]=path
    pixels,known=engine.materialize_context(layout,ops,images)
    context=out/(ident+'-context.png');rgba=np.dstack((pixels,known.astype(np.uint8)*255));Image.fromarray(rgba).save(context)
    regions=[dict(**op,file=str(paths[op['source']]),sha256=sha(paths[op['source']])) for op in ops]
    deriv(context,list(dict.fromkeys(paths[op['source']] for op in ops)),dict(kind='actual_native_context_directional',regions=regions,notProductionPixels=True,sourceUpscaling=False,AIInputsTransformed=False))
    edit=out/(ident+'-edit-target.png');target=Image.open(guide).convert('RGBA');target.alpha_composite(Image.fromarray(rgba));target.convert('RGB').save(edit)
    deriv(edit,[guide,context],dict(kind='same_physical_frame_planning_target_with_actual_native_context',guidePixelsNotProduction=True,sourceUpscaling=False,AIInputsTransformed=False,regions=regions))
    sides=', '.join(engine.active_edges(layout,row-1,col-1,name,neighbors)) or 'any documented corner'
    prompt=f'''Use case: detail restoration with strict composition preservation. Edit Image1, exact1254x1254 game-map {tile} micro-patch {ident}. Return a fully opaque square with EXACTLY the same crop, camera, scale, object outlines and positions.
Image1 is the complete intended picture. Its documented {sides} strips contain real native neighbors. Preserve their exact contour endpoints, silhouettes, colors and brushwork. Freshly paint crisp native detail in the remaining soft planning area, naturally connecting these contours. Heal temporary straight composite boundaries without keeping a rectangular ridge, line or band. Never invent a different architectural continuation.
Image2 reinforces the SAME physical framing. This is a cropped fragment of a larger scene; objects deliberately exit the frame. Never complete cropped objects, zoom out, reveal eave ends, add foliage, or widen the view. Preserve roof/tile seams, beams, road grout, furniture and crate footprints. Real native Image1 boundary endpoints take precedence over small planning discrepancies.
Image3 supplies only the approved clean, bright, rounded Daoist chibi hand-painted style, ivory/jade/gold materials and controlled highlights. No UI, text or characters. Preserve the scene's Mid-Autumn blue-violet evening stone, cobalt water, amber light and jade foliage. Smooth objects remain smooth. Do not add noise, blur, sharpening halos, photographic grain, decorations, grout branches, borders or watermarks. Do not rotate or mirror the picture. Generate real native detail at the exact Image1 framing.'''
    constraint=plan.get('nativePatchConstraints',{}).get(ident)
    if constraint:prompt+='\nSpecific local geometry constraint: '+constraint
    pp=out/(ident+'.prompt.txt');pp.write_text(prompt,encoding='utf-8')
    refs=[edit,guide,REPO/'designs/gameplay-ui/04-guild.png'];call=dict(prompt=prompt,referenced_image_paths=[str(p) for p in refs],transparent_background=False)
    write(out/(ident+'.call.json'),call);rect=plan['tile']['finalPixelRect']
    request=dict(id=ident,tile=tile,startedAt=now(),plan=engine.base.ref(folder/'plan.json'),configSnapshot=read(REPO/'config/image-generation.json'),nativeWorkflow=workflow_record(name),prompt=str(pp),promptSha256=sha(pp),references=[dict(file=str(p),sha256=sha(p),role=role) for p,role in zip(refs,['exact physical-frame target and actual native context','planning geometry only','approved style'])],submittedParameters=dict(model=None,quality=None,**call),globalPatchXYWH=[rect[0]-115+(col-1)*1024,rect[1]-115+(row-1)*1024,1254,1254],core=1024,halo=115,contextRegions=regions)
    write(out/(ident+'.request.json'),request);print(json.dumps(call,ensure_ascii=False))


def save(tile,row,col,source):
    folder,plan,name,neighbors=setup(tile);out=folder/'native';ident=f'p{row}{col}';dst=out/(ident+'.png')
    if dst.exists() or Path(str(dst)+'.generation.json').exists():raise ValueError('Refuse existing native output')
    req=read(out/(ident+'.request.json'))
    if req['nativeWorkflow']['wavefront']!=name:raise ValueError('Plan orientation changed')
    if sha(folder/'plan.json')!=req['plan']['sha256']:raise ValueError('Plan changed while generation was in flight')
    for item in req['references']+req['contextRegions']:
        if sha(item['file'])!=item['sha256']:raise ValueError('Input changed while generation was in flight')
    src=Path(source);engine.base.load_native(src,1254);shutil.copy2(src,dst)
    record=dict(file=str(dst),sha256=sha(dst),generatedAt=now(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=req['configSnapshot'],nativeWorkflow=req['nativeWorkflow'],submittedParameters=req['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host-managed; no exposed model/quality selectors or returned metadata.',evidence=dict(sourceOutputPath=str(src),sourceOutputSha256=sha(src),resultId=src.stem),prompt=req['prompt'],promptSha256=req['promptSha256'],references=req['references'],globalPatchXYWH=req['globalPatchXYWH'],sourceUpscaled=False,resizedAfterGeneration=False,status='native_detail_pending_full_seam_QA',formalAccepted=False)
    write(str(dst)+'.generation.json',record);print(str(dst))


def assemble(tile,preflight=False):
    folder,plan,name,neighbors=setup(tile);layout=engine.Layout();sources=[]
    for r,c in engine.order(layout,name):
        path=folder/'native'/f'p{r+1}{c+1}.png';gp=Path(str(path)+'.generation.json');rec=read(gp);x,y=layout.origin(r,c)
        expected=[plan['tile']['finalPixelRect'][0]-115+x,plan['tile']['finalPixelRect'][1]-115+y,1254,1254]
        if rec['sha256']!=sha(path) or rec['globalPatchXYWH']!=expected or rec.get('sourceUpscaled') or rec.get('resizedAfterGeneration'):raise ValueError('Invalid native source: '+str(path))
        if rec.get('nativeWorkflow',{}).get('wavefront')!=name or rec.get('nativeWorkflow',{}).get('engine')!='multi_edge_v1':raise ValueError('Native wavefront provenance mismatch')
        sources.append(dict(row=r,col=c,path=path,reference=engine.base.ref(path),generation=engine.base.ref(gp),pixels=engine.base.load_native(path,1254)))
    if preflight:print(json.dumps(dict(tile=tile,nativeCount=len(sources),wavefront=name,neighbors=list(neighbors),writesPerformed=False)));return
    output=folder/'output';qa=folder/'qa/multi-edge-candidate';fields=output/'multi-edge-fields';final=output/(tile+'-candidate.png');mp=output/'multi-edge-assembly.json'
    if any(p.exists() for p in [fields,final,mp,qa,Path(str(final)+'.generation.json')]):raise ValueError('Refuse existing candidate/fields/QA/records')
    canvas,covered,seeds=engine.seed_neighbors(layout,{k:v['pixels'] for k,v in neighbors.items()});fields.mkdir(parents=True);reports=[]
    for source in sources:
        r,c=source['row'],source['col'];x,y=layout.origin(r,c);s=layout.patch;patch=source['pixels'];context=canvas[y:y+s,x:x+s].copy();known=covered[y:y+s,x:x+s].copy()
        edges=engine.active_edges(layout,r,c,name,neighbors);owner=engine.owner_mask(known,edges,layout)
        if known.any() and edges:
            merged,flow,tone,report=engine.register_native(context,patch,known,owner,edges,layout,max_shift=6.,tone_cap=18.,return_depth=256)
        else:
            merged=np.where(owner[:,:,None],patch,context);flow=np.zeros((s,s,2),np.float32);tone=np.zeros((s,s,3),np.float32)
            report=dict(kind='native_binary_ownership_only',sourceUpscaling=False,sourceResampling=False,foldedAppliedPixels=0)
        if report['foldedAppliedPixels']:raise RuntimeError('Folded registration; no final candidate will be written')
        saved={};label=f'p{r+1}{c+1}'
        for kind,value in [('mask',owner.astype(np.uint8)*255),('support-mask',known.astype(np.uint8)*255),('flow',flow),('colorCorrection',tone)]:
            p=fields/(label+'.'+kind+('.png' if kind.endswith('mask') else '.npy'))
            if kind.endswith('mask'):Image.fromarray(value).save(p)
            else:np.save(p,value)
            saved[kind]=engine.base.ref(p)
        report.update(id=label,source=source['reference'],generation=source['generation'],canvasXY=[x,y],fields=saved);reports.append(report)
        canvas[y:y+s,x:x+s]=merged;covered[y:y+s,x:x+s]=True
    for src in sources:
        if sha(src['path'])!=src['reference']['sha256']:raise ValueError('Native changed during assembly')
    for data in neighbors.values():
        if sha(data['path'])!=data['reference']['sha256']:raise ValueError('Neighbor changed during assembly')
    if not covered[115:4211,115:4211].all():raise ValueError('Incomplete final coverage')
    Image.fromarray(canvas[115:4211,115:4211]).save(final);qa.mkdir(parents=True);qa_records=[];refs={'current':engine.base.ref(final),**{k:v['reference'] for k,v in neighbors.items()}}
    for label,image,operation,roles in engine.qa_images(Image.open(final).convert('RGB'),{k:Image.fromarray(v['pixels']) for k,v in neighbors.items()},name):
        path=qa/(label+'.png');image.save(path);rec=dict(**engine.base.ref(path),pixels=list(image.size),nativeScale=1,actuallyViewed=False,verdict='pending_visual_QA',operation=operation,sources=[refs[k] for k in roles]);write(str(path)+'.generation.json',rec);qa_records.append(rec)
    vertical,horizontal,corner=engine.orientation(name)
    manifest=dict(createdAt=now(),tile=tile,file=str(final),sha256=sha(final),pixels=[4096,4096],globalPixelRectXYWH=plan['tile']['finalPixelRect'],plan=engine.base.ref(folder/'plan.json'),nativeWorkflow=workflow_record(name),sourceCount=16,patchPixels=[1254,1254],stride=1024,halo=115,extendedPixels=[4326,4326],finalCropLTRB=[115,115,4211,4211],seedRegions=seeds,neighbors={k:v['reference'] for k,v in neighbors.items()},trueCornerSupportAvailable=corner in neighbors,missingDiagonalSupport=([corner] if vertical in neighbors and horizontal in neighbors and corner not in neighbors else []),patches=reports,qa=qa_records,completePixelCoverage=True,sourcePixelScale=1,sourceUpscaling=False,geometryFeather=False,automaticSceneDrawing=False,status='candidate_pending_original_pixel_visual_QA',scopedLocalSeamsPassed=False,formalAccepted=False,navigationVerified=False,clientVerified=False,missingExternalNeighbors=[s for s in ['north','east','south','west'] if s not in neighbors],acceptanceNote='No automated visual acceptance. Inspect all actual shared edges, finite returns and four-tile corner; preserve missing interior edges as pending.')
    write(mp,manifest);write(str(final)+'.generation.json',dict(file=str(final),sha256=sha(final),createdAt=now(),width=4096,height=4096,format='PNG',derivedFrom=[s['reference'] for s in sources],operation=engine.base.ref(mp),actualModel=None,actualQuality=None,modelEvidence='Mechanical derivative; source sidecars retain model evidence and actual unknowns.',productionPixels=True,formalAccepted=False,navigationVerified=False,clientVerified=False))
    print(json.dumps(dict(candidate=str(final),sha256=sha(final),wavefront=name,qaCount=len(qa_records),automaticVisualAcceptance=False)))


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    for command in ['prepare','save']:
        p=sub.add_parser(command);p.add_argument('--tile',required=True);p.add_argument('--row',required=True,type=int);p.add_argument('--col',required=True,type=int)
        if command=='save':p.add_argument('--source',required=True)
    p=sub.add_parser('assemble');p.add_argument('--tile',required=True);p.add_argument('--preflight',action='store_true')
    args=parser.parse_args()
    if args.command=='prepare':prepare(args.tile,args.row,args.col)
    elif args.command=='save':save(args.tile,args.row,args.col,args.source)
    else:assemble(args.tile,args.preflight)


if __name__=='__main__':main()
