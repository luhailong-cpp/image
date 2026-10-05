from pathlib import Path
import datetime,hashlib,json
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,d):
    Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

overrides={
 ('lanxian_day','r08_c06'):R/'lanxian_day/umbrella-repair/candidate-v1/r08_c06.png',
 ('lanxian_spring','r08_c06'):R/'lanxian_spring/grout-x2048-repair/candidate-v1/r08_c06.png',
 ('lanxian_spring','r08_c07'):R/'lanxian_spring/c07-north-grout-repair/candidate-v1/r08_c07.png'
}
jobs={
 ('lanxian_day','r08_c06'):['umbrella-repair'],
 ('lanxian_spring','r08_c06'):['upper-umbrella-repair','grout-x2048-repair'],
 ('lanxian_spring','r08_c07'):['c07-north-grout-repair']
}
changed=[]
for city in ('lanxian_day','lanxian_spring'):
    baseline=[t for t in read(R/'sources.json')['tiles'] if t['city']==city]
    C=R/city/'current-qa';C.mkdir(exist_ok=True)
    tiles=[];images=[];originals=[]
    for b in baseline:
        tile=b['tile'];source=Path(b['source']['file']);assert sha(source)==b['source']['sha256']
        p=overrides.get((city,tile),source);im=Image.open(p).convert('RGB');original=Image.open(source).convert('RGB')
        assert im.size==(4096,4096)
        images.append(im);originals.append(original)
        Q=C/tile;Q.mkdir(exist_ok=True);qa=[]
        for v in b['qa']:
            old=Image.open(v['file']).convert('RGB')
            if v['kind']=='nine_junctions_row_major':
                board=Image.new('RGB',(960,960))
                for i,box in enumerate(v['cropBoxes']):board.paste(im.crop(box),((i%3)*320,(i//3)*320))
            else:
                board=Image.new('RGB',(1024,1024))
                rotate=v.get('axis')=='x' or v.get('side') in ('west','east')
                for i,box in enumerate(v['cropBoxes']):
                    patch=im.crop(box)
                    if rotate:patch=patch.transpose(Image.Transpose.ROTATE_90)
                    board.paste(patch,(0,i*256))
            identical=board.tobytes()==old.tobytes()
            f=Path(v['file']) if identical else Q/Path(v['file']).name
            if not identical:board.save(f);changed.append(str(f))
            qa.append({**v,**info(f),'baselineQa':info(v['file']),'pixelIdenticalToViewedBaseline':identical,'status':'passed_inherited_exact_pixels' if identical else 'pending_actual_view','currentCandidate':info(p)})
        edges={}
        for side,box in {'north':(0,0,4096,1),'south':(0,4095,4096,4096),'west':(0,0,1,4096),'east':(4095,0,4096,4096)}.items():
            edgeqa=next(v for v in qa if v.get('side')==side)
            edges[side]={'rawRgbBoundarySha256':hashlib.sha256(im.crop(box).tobytes()).hexdigest(),'candidateSha256':sha(p),'boundaryUnchangedFromBaseline':im.crop(box).tobytes()==original.crop(box).tobytes(),'qa':info(edgeqa['file']),'neighbor':None,'adjacencyStatus':'pending_neighbor_not_in_current_scope'}
        repairRecords=[]
        for job in jobs.get((city,tile),[]):
            J=R/city/job;A=J/'candidate-v1/assembly.json';assembly=read(A)
            before=np.array(Image.open(assembly['derivedFrom'][0]['file']).convert('RGB'));after=np.array(Image.open(assembly['candidate']['file']).convert('RGB'))
            x0,y0,x1,y1=assembly['cropLTRB'];mask=np.array(Image.open(assembly['mask']['file']))
            allowed=np.zeros((4096,4096),bool);allowed[y0:y1,x0:x1]=mask>0
            assert np.array_equal(before[~allowed],after[~allowed])
            repairRecords.append({'job':job,'assembly':info(A),'nativeGeneration':info(J/'native.png.generation.json'),'candidateGeneration':info(J/'candidate-v1'/(tile+'.png.generation.json')),'outsideMaskPixelEqualityReverified':True,'cropLTRB':assembly['cropLTRB'],'returnQa':[info(J/'candidate-v1'/(n+'.png')) for n in ('context-after','top','bottom','left','right')],'returnQaActuallyViewed':True,'returnQaResult':'pass: continuous single outlines and material boundaries; no newly observed double edge','assemblyPendingReviewSupersededByThisRecord':True})
        tiles.append({'tile':tile,'candidate':{**info(p),'pixels':[4096,4096]},'baselineSource':b['source'],'baselineSourceUnchanged':True,'historicalAssembly':info(b['sourceAssembly']),'historicalPathRelocation':{'from':'E:/work/image','to':'D:/work/image','mode':'resolve references only; historical record not rewritten'},'repairs':repairRecords,'qa':qa,'fourEdges':edges,'internalSixFullSeamsStatus':'pending_current_qa','nineJunctionsStatus':'pending_current_qa','formalCityAccepted':False})
    pairs=[]
    for i in range(2):
        f=R/city/f'baseline/common-c0{i+6}-c0{i+7}-all4096.png';old=Image.open(f).convert('RGB');board=Image.new('RGB',(1024,1024))
        for seg in range(4):
            y0=seg*1024;y1=y0+1024;v=Image.new('RGB',(256,1024));v.paste(images[i].crop((3968,y0,4096,y1)),(0,0));v.paste(images[i+1].crop((0,y0,128,y1)),(128,0));board.paste(v.transpose(Image.Transpose.ROTATE_90),(0,seg*256))
        identical=board.tobytes()==old.tobytes();assert identical
        pair={'left':tiles[i]['candidate'],'right':tiles[i+1]['candidate'],'qa':info(f),'fullLengthPixels':4096,'widthEachSide':128,'pixelIdenticalToViewedBaseline':identical,'status':'passed_inherited_exact_pixels','resized':False}
        pairs.append(pair)
        tiles[i]['fourEdges']['east'].update({'neighbor':tiles[i+1]['candidate'],'adjacencyStatus':'passed_current_sha_pair','commonEdgeQa':info(f)})
        tiles[i+1]['fourEdges']['west'].update({'neighbor':tiles[i]['candidate'],'adjacencyStatus':'passed_current_sha_pair','commonEdgeQa':info(f)})
    preview=Image.new('RGB',(1536,512))
    for i,im in enumerate(images):preview.paste(im.resize((512,512),Image.Resampling.LANCZOS),(i*512,0))
    preview.save(C/'triple-overview-only.png')
    result={'city':city,'preparedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Existing r08_c06,r08_c07,r08_c08 only. Three 4096-square native-scale candidates; not a completed 65536-square city.','status':'pending_actual_final_qa','tiles':tiles,'commonEdges':pairs,'overview':{**info(C/'triple-overview-only.png'),'displayOnly':True,'resized':True},'baselineVisualReview':'All 33 per-tile native QA boards and 2 common-edge native QA boards actually viewed earlier in this task. Updated views require renewed visual review.','crossAppearanceExactGeometryStatus':'not established for inherited historical day/spring drawings; this repair batch preserves existing building locations and does not redesign layouts.','globalSelectionChanged':False,'cleanupPerformed':False}
    write(C/'prepared.json',result)
write(R/'current-qa-to-view.json',{'changedQa':changed})
print(json.dumps({'changedQa':changed},ensure_ascii=False,indent=2))
