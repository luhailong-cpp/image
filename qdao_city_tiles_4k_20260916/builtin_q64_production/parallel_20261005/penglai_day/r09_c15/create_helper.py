from pathlib import Path
B=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_day');O=B/'r09_c15'
s=(B/'r10_c14/helper.py').read_text(encoding='utf8').replace('r10_c14','r09_c15').replace('GX,GY=53248,36864','GX,GY=57344,32768')
a=s.index('def setup():');b=s.index('def update(',a)
setup='''def setup():
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
'''
s=s[:a]+setup+s[b:]
s=s.replace("for k,pos in [('north',(115,0)),('west',(0,115))]:","for k,pos in [('west',(0,115))]:")
s=s.replace("[src,state['north']['anchor'],state['west']['anchor']]","[src,state['west']['anchor']]")
s=s.replace("for key,active in [('north',r==1),('west',c==1)]:","for key,active in [('west',c==1)]:")
s=s.replace("call=p.read(ROOT/'prompts'/f'{name}.call.json');dest=p.ingest", "call=p.read(ROOT/'prompts'/f'{name}.call.json');p.write(ROOT/'evidence'/f'{name}.tool-result.json',{'sourcePath':str(source),'toolHint':'Generated images are saved under the Codex generated_images directory by default. The generated image is displayed in the tool result.','outputSha256':p.sha(source),'tool':'image_gen.imagegen','savedAt':p.stamp()});dest=p.ingest")
(O/'helper.py').write_text(s,encoding='utf8')
