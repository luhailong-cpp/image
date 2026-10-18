"""Restart worker evidence and exact-pixel QA only. Does not generate artwork."""
import sys, json, base64, hashlib, importlib.util, types, shutil
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode=True
ALLOWED = {f'r{r:02d}_c{c:02d}' for r in range(9, 13) for c in range(1, 5)}
def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path, obj):
    path = Path(path).resolve()
    assert path.is_relative_to(ROOT) and path.relative_to(ROOT).parts[0] in ALLOWED
    assert not path.exists(), path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def check_file(path):
    path=Path(path)
    assert path.is_file()
    return {'file': str(path), 'sha256': digest(path)}

mode=sys.argv[1]
data=json.loads(sys.argv[2])
tile=data['tile']; assert tile in ALLOWED
t=ROOT/tile
if mode=='submission':
    req=Path(data['request']).resolve();q=json.loads(req.read_text(encoding='utf-8-sig'));assert q['tile']==tile
    for ref in q['references']:assert digest(ref['file'])==ref['sha256']
    rules=Path('D:/work/image/AGENTS.md');split=Path('D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json')
    rule_text=rules.read_text(encoding='utf-8-sig');split_text=split.read_text(encoding='utf-8-sig');assert rule_text and json.loads(split_text)
    name=req.name.removesuffix('.request.json')
    obj={'tile':tile,'patch':q['coordinates']['id'],'request':check_file(req),'startedAtUtc':datetime.now(timezone.utc).isoformat(),
         'status':'submitting_builtin_imagegen','route':'builtin','actualModel':None,'actualQuality':None,'paidApiUsed':False,
         'rulesActuallyReread':[check_file(rules),check_file(split)],'actualReferences':q['references']}
    out=t/'pipeline/receipts'/(name+'.submission.json');write(out,obj);print(json.dumps(obj,ensure_ascii=False))
elif mode=='review':
    p=data['patch']; a=data['attempt']
    source=t/'refinement/versions'/a/(p+'.returned-native.png')
    with Image.open(source) as im: pixels=list(im.size)
    assert pixels==[1254,1254]
    obj={'tile':tile,'patch':p,'attempt':a,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
         'actualReturnedImageViewed':True,'selectedProvisionally':data.get('selectedProvisionally',True),
         'formalAccepted':False,'internalAccepted':False,'externalAccepted':False,
         'source':str(source),'sourceSha256':digest(source),'nativePixels':pixels,
         'findings':data['findings'],'propagationDecision':data['propagationDecision']}
    if 'preservationCorrection' in data: obj['preservationCorrection']=data['preservationCorrection']
    out=t/'pipeline/receipts'/(p+'.'+a+'.restart20261016.review.json')
    write(out,obj); print(json.dumps({'review':str(out),'sha256':digest(out)},ensure_ascii=False))
elif mode=='prepare-independent':
    spec=importlib.util.spec_from_file_location('left_restart_native_pipeline',ROOT/'native_pipeline.py')
    np=importlib.util.module_from_spec(spec);spec.loader.exec_module(np)
    pipe=np.Pipeline(tile); old_neighbor=pipe.neighbor; missing=[]
    def optional_neighbor(row,col,side):
        try:
            result=old_neighbor(row,col,side)
            if side in data.get('excludeNativeSides',[]):
                missing.append({'side':side,'reason':data['exclusionReason'],'excludedCurrentSource':result[1] if result else None,'acceptance':False})
                return None
            return result
        except ValueError as error:
            if not str(error).startswith('Missing required selected native neighbor:'): raise
            missing.append({'side':side,'reason':str(error),'acceptance':False})
            return None
    pipe.neighbor=optional_neighbor
    bottom_ref=None
    if data.get('bottomNeighborPatch'):
        br,bc=map(int,data['bottomNeighborPatch'].removeprefix('p').split('_'))
        assert br==data['row']+1 and bc==data['col']
        selection=pipe.selected_record(tile,br,bc)
        bottom_image,entry=pipe.native_record(tile,br,bc,selection)
        crop=[0,0,1254,230];context=entry['coordinates']['contextWorldBox']
        bottom_ref={'file':entry['nativeFile'],'sha256':entry['nativeSha256'],'role':'exact selected lower native strip; bottom context priority',
                    'generationRecord':entry['recordFile'],'generationRecordSha256':entry['recordSha256'],'sourceTile':tile,'sourcePatch':entry['id'],
                    'selectionEvidence':entry['selectionEvidence'],'sourceCrop':crop,'sourceWorldBox':[context[0],context[1],context[2],context[1]+230],
                    'sourceResampling':False,'targetBox':[0,1024,1254,1254],'effectiveTargetBox':[0,1024,1254,1254]}
        old_image_save=pipe.save_image
        def image_with_bottom(path,im):
            if str(path).endswith('.continuity-seed.png'):im.paste(bottom_image.crop(crop),(0,1024))
            old_image_save(path,im)
        pipe.save_image=image_with_bottom
    old_save=pipe.save_json
    def save_with_missing(path,obj):
        if str(path).endswith('.request.json'):
            obj['missingNativeNeighbors']=missing
            if bottom_ref:
                obj['neighborSources'].append(bottom_ref)
                obj['cornerTreatment']['additionalBottomStripPriority']=True
            if data.get('quietReference'):
                f=Path(data['quietReference']).resolve()
                obj['references'].append({'file':str(f),'sha256':digest(f),'role':'quiet native grey stone MATERIAL ONLY; no geometry or framing'})
                obj['referenced_image_paths'].append(str(f))
        elif str(path).endswith('.derivation.json') and bottom_ref:
            if bottom_ref not in obj['neighbors']:obj['neighbors'].append(bottom_ref)
            obj['cornerTreatment']['additionalBottomStripPriority']=True
        old_save(path,obj)
    pipe.save_json=save_with_missing
    args=types.SimpleNamespace(row=data['row'],col=data['col'],attempt=data['attempt'],anchor_left=None,anchor_top=None,content_prefix=None,content_prefix_file=data['prefixFile'])
    result=pipe.prepare(args);result['missingNativeNeighbors']=missing
    print(json.dumps(result,ensure_ascii=False))
elif mode=='refine-ingest':
    spec=importlib.util.spec_from_file_location('left_restart_native_pipeline',ROOT/'native_pipeline.py')
    np=importlib.util.module_from_spec(spec);spec.loader.exec_module(np)
    pipe=np.Pipeline(tile);p=data['patch'];r,c=map(int,p.removeprefix('p').split('_'));a=data['attempt']
    version=t/'refinement/versions'/a
    old_target=pipe.write_target;old_selected=pipe.selected_record
    def versioned_target(path):
        path=Path(path).resolve()
        if path==(t/'native'/(p+'.png')).resolve(): path=version/(p+'.png')
        return old_target(path)
    pipe.write_target=versioned_target
    def target_unselected(stile,row,col,optional=False):
        if stile==tile and row==r and col==c:return None
        return old_selected(stile,row,col,optional)
    pipe.selected_record=target_unselected
    args=types.SimpleNamespace(row=r,col=c,attempt=a,source=data['source'],receipt=data['receipt'],request=data['request'])
    result=pipe.ingest(args)
    active=t/'refinement/selection.json'
    before=json.loads(active.read_text(encoding='utf-8-sig')) if active.exists() else {}
    write(version/(p+'.selection.before.json'),before)
    after=dict(before);after[p]=str((version/(p+'.png.generation.json')).relative_to(t)).replace('\\','/')
    write(version/(p+'.selection.after.json'),after)
    active.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(version/(p+'.selection.after.json'),active)
    result['selection']=str(active);result['selectionSha256']=digest(active)
    print(json.dumps(result,ensure_ascii=False))
elif mode=='select-existing':
    spec=importlib.util.spec_from_file_location('left_restart_native_pipeline',ROOT/'native_pipeline.py')
    np=importlib.util.module_from_spec(spec);spec.loader.exec_module(np)
    pipe=np.Pipeline(tile);p=data['patch'];r,c=map(int,p.removeprefix('p').split('_'));a=data['attempt']
    version=t/'refinement/versions'/a;record=version/(p+'.png.generation.json')
    image,entry=pipe.native_record(tile,r,c,(record,None));pipe.stable()
    active=t/'refinement/selection.json';before=json.loads(active.read_text(encoding='utf-8-sig')) if active.exists() else {}
    write(version/(p+'.selection.before.json'),before)
    after=dict(before);after[p]=str(record.relative_to(t)).replace('\\','/')
    write(version/(p+'.selection.after.json'),after);shutil.copyfile(version/(p+'.selection.after.json'),active)
    print(json.dumps({'selected':p,'selection':str(active),'sourceSha256':entry['nativeSha256']},ensure_ascii=False))
elif mode=='native-edit-seed':
    spec=importlib.util.spec_from_file_location('left_restart_native_pipeline',ROOT/'native_pipeline.py')
    np=importlib.util.module_from_spec(spec);spec.loader.exec_module(np)
    pipe=np.Pipeline(tile);rp=Path(data['sourceRequest']);q=json.loads(rp.read_text(encoding='utf-8-sig'))
    p=q['coordinates']['id'];r,c=map(int,p.removeprefix('p').split('_'));a=data['attempt']
    actual=Path(data['actual']);assert actual.resolve().is_relative_to(t.resolve())
    with Image.open(actual) as im:seed=im.convert('RGB')
    assert seed.size==(1254,1254)
    neighbors=[]
    for side in ['left','top']:
        n=pipe.neighbor(r,c,side)
        if n:
            seed.paste(n[0],(0,0));n[1].update({'targetBox':[0,0,230,1254] if side=='left' else [0,0,1254,230],
                   'effectiveTargetBox':[0,230,230,1254] if side=='left' else [0,0,1254,230]})
            neighbors.append(n[1])
    out=t/'pipeline/guides'/(p+'.'+a+'.native-edit-seed.png');assert not out.exists();seed.save(out)
    write(str(out)+'.derivation.json',{'actualTarget':check_file(actual),'neighbors':neighbors,
          'operation':'exact native strip paste onto actual native edit target; no resampling; not final art','seed':check_file(out)})
    dest=t/'pipeline/prompts'/(p+'.'+a+'.request.json');pp=dest.with_name(p+'.'+a+'.prompt.txt');assert not pp.exists()
    pp.write_text(data['prompt'],encoding='utf-8')
    refs=[{'file':str(out),'sha256':digest(out),'role':'actual native edit target with exact current native neighboring overlaps pasted; preserve all object geometry except specified repair'}]+q['references'][1:4]
    extra=Path(data['extraReference']).resolve();refs.append({'file':str(extra),'sha256':digest(extra),'role':data['extraRole']})
    q.update({'prompt':data['prompt'],'promptFile':str(pp),'promptSha256':digest(pp),'references':refs,
              'referenced_image_paths':[x['file'] for x in refs],'neighborSources':neighbors,
              'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'actualModel':None,'actualQuality':None})
    write(dest,q);print(json.dumps({'request':str(dest),'seed':str(out)},ensure_ascii=False))
elif mode=='edit-request':
    old=Path(data['sourceRequest']);q=json.loads(old.read_text(encoding='utf-8-sig'))
    assert q['tile']==tile
    p=q['coordinates']['id'];a=data['attempt']
    src=Path(data['target']).resolve()
    assert src.is_relative_to(t.resolve())
    with Image.open(src) as im: assert im.size==(1254,1254)
    refs=[{'file':str(src),'sha256':digest(src),'role':'actual native edit target; keep all object geometry and exact crop'}]+q['references'][1:4]
    if data.get('quietReference'):
        quiet=Path(data['quietReference']).resolve()
        refs.append({'file':str(quiet),'sha256':digest(quiet),'role':'quiet grey MATERIAL ONLY; no geometry or framing'})
    if data.get('extraReference'):
        extra=Path(data['extraReference']).resolve()
        refs.append({'file':str(extra),'sha256':digest(extra),'role':data['extraRole']})
    rp=t/'pipeline/prompts'/(p+'.'+a+'.request.json')
    pp=rp.with_name(p+'.'+a+'.prompt.txt');assert not pp.exists()
    pp.write_text(data['prompt'],encoding='utf-8')
    q.update({'prompt':data['prompt'],'promptFile':str(pp),'promptSha256':digest(pp),'references':refs,
              'referenced_image_paths':[r['file'] for r in refs],'preparedAtUtc':datetime.now(timezone.utc).isoformat(),
              'actualModel':None,'actualQuality':None,'localEditOf':check_file(src),'sourceRequest':check_file(old)})
    write(rp,q);print(json.dumps({'request':str(rp),'target':str(src)},ensure_ascii=False))
elif mode=='build-full-qa':
    assembly=Path(data['assembly']).resolve();doc=json.loads(assembly.read_text(encoding='utf-8-sig'))
    assert doc['tile']==tile and doc['verifiedNativeCount']==16
    src=Path(doc['output']['file']);assert digest(src)==doc['output']['sha256']
    with Image.open(src) as im: im=im.convert('RGB')
    assert im.size==(4096,4096)
    out=assembly.parent/data['version'];assert not out.exists();out.mkdir()
    views=[]
    for axis in ['V','H']:
      for boundary in range(1,4):
       for pair in range(2):
        panel=Image.new('RGB',(1024,1024));regions=[]
        for j in range(2):
          segment=pair*2+j;center=boundary*1024
          box=[center-256,segment*1024,center+256,(segment+1)*1024] if axis=='V' else [segment*1024,center-256,(segment+1)*1024,center+256]
          panel.paste(im.crop(box),(j*512,0) if axis=='V' else (0,j*512))
          regions.append({'formalCoreBox':box,'placement':[j*512,0] if axis=='V' else [0,j*512]})
        name=f'{axis}{boundary}-segments{pair*2+1}-{pair*2+2}';dest=out/(name+'.png');panel.save(dest)
        views.append({'id':name,'file':str(dest),'sha256':digest(dest),'regions':regions,'sourceResampling':False,'viewed':False})
    panel=Image.new('RGB',(768,768));regions=[]
    for r in range(1,4):
     for c in range(1,4):
      box=[c*1024-128,r*1024-128,c*1024+128,r*1024+128]
      panel.paste(im.crop(box),((c-1)*256,(r-1)*256));regions.append({'formalCoreBox':box,'placement':[(c-1)*256,(r-1)*256]})
    dest=out/'nine-intersections.png';panel.save(dest);views.append({'id':'nine-intersections','file':str(dest),'sha256':digest(dest),'regions':regions,'sourceResampling':False,'viewed':False})
    for side,ap in data.get('neighborAssemblies',{}).items():
      other=json.loads(Path(ap).read_text(encoding='utf-8-sig'));otherfile=Path(other['output']['file']);assert digest(otherfile)==other['output']['sha256']
      with Image.open(otherfile) as n:n=n.convert('RGB')
      for pair in range(2):
       panel=Image.new('RGB',(1024,1024));regions=[]
       for j in range(2):
        seg=pair*2+j
        if side=='top':
         nb=[seg*1024,4096-256,(seg+1)*1024,4096];tb=[seg*1024,0,(seg+1)*1024,256]
         panel.paste(n.crop(nb),(0,j*512));panel.paste(im.crop(tb),(0,j*512+256))
        elif side=='left':
         nb=[4096-256,seg*1024,4096,(seg+1)*1024];tb=[0,seg*1024,256,(seg+1)*1024]
         panel.paste(n.crop(nb),(j*512,0));panel.paste(im.crop(tb),(j*512+256,0))
        else: raise ValueError(side)
        regions.append({'neighborBox':nb,'targetBox':tb,'segment':seg+1})
       dest=out/(f'external-{side}-segments{pair*2+1}-{pair*2+2}.png');panel.save(dest)
       views.append({'id':dest.stem,'file':str(dest),'sha256':digest(dest),'regions':regions,'neighborAssembly':check_file(ap),'sourceResampling':False,'viewed':False})
    manifest={'tile':tile,'assembly':check_file(assembly),'core':doc['output'],'context':doc['contextOutput'],'views':views,
              'internalPassed':False,'externalPassed':False,'formalAccepted':False,'rightAndBottomNeighborStatus':'native complete adjacent tile unavailable; pending root review','reviewStatus':'constructed_pending_visual_inspection'}
    write(out/'manifest.json',manifest);print(json.dumps({'qa':str(out),'manifest':str(out/'manifest.json'),'viewCount':len(views)},ensure_ascii=False))
elif mode=='finalize-qa':
    manifest=Path(data['manifest']);doc=json.loads(manifest.read_text(encoding='utf-8-sig'))
    assert doc['tile']==tile
    if data.get('additionalManifest'):
        additional=json.loads(Path(data['additionalManifest']).read_text(encoding='utf-8-sig'))
        doc['views']+=additional['views'];doc['additionalManifest']=check_file(data['additionalManifest'])
    for view in doc['views']:
        assert digest(view['file'])==view['sha256']
        assert view['id'] in data['viewFindings']
        view.update({'viewed':True,'findings':data['viewFindings'][view['id']],'accepted':False})
    if doc.get('priorAssembly'):
        prior=json.loads(Path(doc['priorAssembly']['file']).read_text(encoding='utf-8-sig'))
        with Image.open(prior['output']['file']) as im:oi=im.convert('RGB')
        with Image.open(doc['core']['file']) as im:ni=im.convert('RGB')
        verification={}
        for side,box in {'top':[0,0,4096,256],'left':[0,0,256,4096]}.items():
            oh=hashlib.sha256(oi.crop(box).tobytes()).hexdigest();nh=hashlib.sha256(ni.crop(box).tobytes()).hexdigest()
            changed_segments=[]
            if oh!=nh:
                for segment in range(1,5):
                    s=(segment-1)*1024;b=[s,0,s+1024,256] if side=='top' else [0,s,256,s+1024]
                    if oi.crop(b).tobytes()!=ni.crop(b).tobytes():
                        changed_segments.append(segment)
                        assert f'external-{side}-segment{segment}' in data['viewFindings'],'Changed external band not visually reviewed'
            verification[side]={'formalCoreBox':box,'oldRgbPixelsSha256':oh,'newRgbPixelsSha256':nh,'byteIdentical':oh==nh,'changedSegmentsRechecked':changed_segments}
        doc['externalReuseVerification']=verification
        doc['externalReuse']='Only byte-identical outer band pixels reuse prior external QA. Changed external segments are actually rechecked in appended native views.'
    doc.update({'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewStatus':'actual_native_views_reviewed_open_issues',
                'issues':data['issues'],'internalPassed':False,'externalPassed':False,'formalAccepted':False,
                'actualModel':None,'actualQuality':None,'modelEvidence':'Built-in did not return actual model or quality. Historical configSnapshot is not model evidence.'})
    out=manifest.parent/data.get('filename','worker-review-and-repair-queue.json');write(out,doc)
    print(json.dumps({'review':str(out),'sha256':digest(out)},ensure_ascii=False))
elif mode=='build-external-changed':
    old=json.loads(Path(data['oldAssembly']).read_text(encoding='utf-8-sig'));new=json.loads(Path(data['newAssembly']).read_text(encoding='utf-8-sig'))
    with Image.open(old['output']['file']) as im:oi=im.convert('RGB')
    with Image.open(new['output']['file']) as im:ni=im.convert('RGB')
    out=Path(data['qa']);assert out.is_relative_to(t.resolve()) and out.is_dir()
    views=[]
    for side,ap in data['neighborAssemblies'].items():
        n=json.loads(Path(ap).read_text(encoding='utf-8-sig'));assert digest(n['output']['file'])==n['output']['sha256']
        with Image.open(n['output']['file']) as im:neighbor=im.convert('RGB')
        for segment in range(1,5):
            s=(segment-1)*1024;tb=[s,0,s+1024,256] if side=='top' else [0,s,256,s+1024]
            if oi.crop(tb).tobytes()==ni.crop(tb).tobytes():continue
            if side=='top':
                nb=[s,3840,s+1024,4096];panel=Image.new('RGB',(1024,512));panel.paste(neighbor.crop(nb),(0,0));panel.paste(ni.crop(tb),(0,256))
            elif side=='left':
                nb=[3840,s,4096,s+1024];panel=Image.new('RGB',(512,1024));panel.paste(neighbor.crop(nb),(0,0));panel.paste(ni.crop(tb),(256,0))
            else:raise ValueError(side)
            name=f'external-{side}-segment{segment}';dest=out/(name+'.png');assert not dest.exists();panel.save(dest)
            views.append({'id':name,'file':str(dest),'sha256':digest(dest),'neighborAssembly':check_file(ap),'neighborBox':nb,'targetBox':tb,'sourceResampling':False,'viewed':False,'reason':'quilt seam path changed assembled outer pixels despite unchanged outer native source'})
    write(out/'external-changes-manifest.json',{'tile':tile,'oldAssembly':check_file(data['oldAssembly']),'newAssembly':check_file(data['newAssembly']),'views':views})
    print(json.dumps({'manifest':str(out/'external-changes-manifest.json'),'views':[v['id'] for v in views]},ensure_ascii=False))
elif mode=='build-changed-qa':
    old_path=Path(data['oldAssembly']);new_path=Path(data['newAssembly'])
    old=json.loads(old_path.read_text(encoding='utf-8-sig'));new=json.loads(new_path.read_text(encoding='utf-8-sig'))
    om={s['id']:s['nativeSha256'] for s in old['nativeSources']};nm={s['id']:s['nativeSha256'] for s in new['nativeSources']}
    changed=[p for p in om if om[p]!=nm[p]];assert set(changed)==set(data['expectedChanged'])
    src=Path(new['output']['file']);assert digest(src)==new['output']['sha256']
    with Image.open(src) as im:im=im.convert('RGB')
    out=new_path.parent/data['version'];assert not out.exists();out.mkdir()
    v=set();h=set();corners=set()
    for p in changed:
        r,c=map(int,p.removeprefix('p').split('_'))
        for boundary in [c-1,c]:
            if 1<=boundary<=3:v.add((boundary,r))
        for boundary in [r-1,r]:
            if 1<=boundary<=3:h.add((boundary,c))
        for rr in [r-1,r]:
            for cc in [c-1,c]:
                if 1<=rr<=3 and 1<=cc<=3:corners.add((rr,cc))
    views=[]
    for axis,items in [('V',v),('H',h)]:
      for boundary,segment in sorted(items):
        center=boundary*1024;start=(segment-1)*1024
        box=[center-256,start,center+256,start+1024] if axis=='V' else [start,center-256,start+1024,center+256]
        dest=out/(f'{axis}{boundary}-segment{segment}.png');im.crop(box).save(dest)
        views.append({'id':dest.stem,'file':str(dest),'sha256':digest(dest),'formalCoreBox':box,'sourceResampling':False,'viewed':False})
    panel=Image.new('RGB',(256*len(corners),256));regions=[]
    for i,(r,c) in enumerate(sorted(corners)):
        box=[c*1024-128,r*1024-128,c*1024+128,r*1024+128];panel.paste(im.crop(box),(i*256,0));regions.append({'formalCoreBox':box,'placement':[i*256,0]})
    dest=out/'changed-intersections.png';panel.save(dest);views.append({'id':dest.stem,'file':str(dest),'sha256':digest(dest),'regions':regions,'sourceResampling':False,'viewed':False})
    doc={'tile':tile,'assembly':check_file(new_path),'priorAssembly':check_file(old_path),'core':new['output'],'context':new['contextOutput'],
         'changedNativeIds':changed,'unchangedNativeIds':[p for p in om if p not in changed],'unchangedQaEvidence':check_file(data['oldReview']),
         'views':views,'internalPassed':False,'externalPassed':False,'formalAccepted':False,'reviewStatus':'constructed_pending_visual_inspection',
         'externalReuse':'top and left candidate pixels and hashes unchanged; prior actual external QA reused. Right/bottom adjacent complete tiles absent.'}
    write(out/'manifest.json',doc);print(json.dumps({'qa':str(out),'manifest':str(out/'manifest.json'),'views':[v['id'] for v in views]},ensure_ascii=False))
elif mode=='prefix':
    out=t/'pipeline/prompts'/(data['patch']+'.'+data['attempt']+'.prefix.txt')
    assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(data['prefix'],encoding='utf-8');print(str(out))
elif mode=='compare':
    req=Path(data['request']);q=json.loads(req.read_text(encoding='utf-8-sig'))
    assert q['tile']==tile
    src=Path(data['source'])
    with Image.open(src) as im: target=im.convert('RGB')
    assert target.size==(1254,1254)
    out=t/'pipeline/quick-qa'/data['version']; assert not out.exists()
    out.mkdir(parents=True)
    panels=[]
    for n in q['neighborSources']:
        with Image.open(n['file']) as im: crop=im.convert('RGB').crop(n['sourceCrop'])
        box=n['targetBox'];actual=target.crop(box)
        isleft=box[2]==230
        panel=Image.new('RGB',(460,1254) if isleft else (1254,460))
        panel.paste(crop,(0,0));panel.paste(actual,(230,0) if isleft else (0,230))
        side='left' if isleft else ('bottom' if box[1]==1024 else 'top')
        dest=out/(side+'-overlap-comparison.png')
        panel.save(dest)
        panels.append({'file':str(dest),'sha256':digest(dest),'neighbor':check_file(n['file']),
                       'target':check_file(src),'operation':'exact crops side by side; no resize, warp or artwork'} )
    write(out/'panels.json',{'tile':tile,'patch':q['coordinates']['id'],'panels':panels,'formalAccepted':False})
    print(json.dumps(panels,ensure_ascii=False))
else:
    raise ValueError(mode)
