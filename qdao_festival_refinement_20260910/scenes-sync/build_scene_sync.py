"""Bounded scene alias publication. Only 18 listed RGB images and current metadata may change."""
import argparse, copy, hashlib, json, shutil, subprocess, time
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageChops, ImageOps

RUN = Path(__file__).resolve().parent
ROOT = RUN.parent.parent
PLAN = RUN.parent / 'legacy-scene-sync-plan.json'
NODE = Path(r'C:\Users\luyua\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe')
SHARP = Path(r'C:\Users\luyua\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\sharp')
PREVIEW = 'qdao_chibi_game_pack_v4/preview-main-city_2560x1080.png'
HUD_SOURCE = 'qdao_ui_redesign_v5/source/04_main_city_hud.png'
HUD_EXPORT = 'qdao_ui_redesign_v5/04_main_city_hud_2560x1080.png'
HERO = 'qdao_chibi_game_pack_v4/hero-transparent_1024.png'
PLACEMENTS = 'qdao_chibi_game_pack_v4/placements.json'
HUD = 'qdao_ui_redesign_v5/hud/'
now = lambda: datetime.now(timezone.utc).isoformat()
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))

def write(p, value):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def safe(base, rel):
    p = (base / rel).resolve()
    if not p.is_relative_to(base.resolve()): raise ValueError('Unsafe path: ' + rel)
    return p

def snap(rel, destination):
    src, dst = safe(ROOT, rel), safe(RUN / destination, rel)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        if sha(dst) != sha(src): raise RuntimeError('Existing snapshot differs: ' + rel)
    else: shutil.copy2(src, dst)
    return {'path': rel, 'snapshot': dst.relative_to(RUN).as_posix(), 'sha256': sha(src)}

def info(p):
    with Image.open(p) as im:
        im.load()
        d = {'size': list(im.size), 'mode': im.mode, 'sha256': sha(p), 'bytes': Path(p).stat().st_size}
        if im.mode == 'RGBA':
            a = im.getchannel('A')
            d.update(alpha_sha256=hashlib.sha256(a.tobytes()).hexdigest(), alpha_range=list(a.getextrema()))
        return d

def outside_same(a, b, alpha):
    zero = alpha.point(lambda x: 255 if x == 0 else 0).convert('RGB')
    return ImageChops.multiply(ImageChops.difference(a.convert('RGB'), b.convert('RGB')), zero).getbbox() is None

def stages():
    plan = read(PLAN)
    targets = [t['path'] for g in plan['copy_groups'] for t in g['targets']] + [PREVIEW, HUD_SOURCE, HUD_EXPORT]
    if len(targets) != 18 or len(set(targets)) != 18: raise RuntimeError('Unexpected target scope')
    return plan, targets

def stage():
    plan, targets = stages()
    if (RUN / 'publication.json').exists(): raise RuntimeError('Already published; use verify')
    for g in plan['copy_groups']:
        if sha(ROOT / g['copy_source']['path']) != g['copy_source']['sha256']: raise RuntimeError('Runtime source changed')
        for t in g['targets']:
            if sha(ROOT / t['path']) != t['sha256']: raise RuntimeError('Target changed since mapping: ' + t['path'])
    before = [{'path': p, **info(ROOT / p), 'backup': snap(p, 'before')['snapshot']} for p in targets]
    sources = []
    for p in [g['copy_source']['path'] for g in plan['copy_groups']] + [HERO, PLACEMENTS] + [HUD+x for x in ('hud_overlay.png','hud_skin.png','hud_labels.png','hud_overlay.svg','hud_skin.svg','hud_labels.svg','placement.json')]:
        sources.append(snap(p, 'current-inputs'))
    protected = [c['path'] for c in plan['alpha_assets']['clouds']] + [plan['alpha_assets']['dim_overlay']['path']] + [x['path'] for x in plan['protected_original_sources']] + plan['protected_world_archive']['paths']
    protected += [HERO, PLACEMENTS] + [HUD+x for x in ('hud_overlay.png','hud_skin.png','hud_labels.png','hud_overlay.svg','hud_skin.svg','hud_labels.svg')]
    protected += [p.relative_to(ROOT).as_posix() for p in (ROOT/'qdao_ui_style_recut_v10/contracts').rglob('*') if p.is_file()]
    protected = sorted(set(protected))
    guards = [{'path': p, 'sha256': sha(ROOT/p)} for p in protected]
    write(RUN/'before-index.json', {'created_at_utc':now(),'files':before,'protected':guards,'excluded_concurrent_work':['v5 01/03 full-screen art','v11','monitor-state','inventory','client filesystem']})
    write(RUN/'current-inputs.json', {'created_at_utc':now(),'kind':'new task-specific snapshot of current accepted inputs; frozen v10 contracts untouched','files':sources,'recipes':{p:sha(ROOT/p) for p in ('qdao_chibi_game_pack_v4/build_pack.py','qdao_ui_style_recut_v10/tools/build_composites.mjs')}})
    for g in plan['copy_groups']:
        source = RUN/'current-inputs'/g['copy_source']['path']
        for t in g['targets']:
            dst=safe(RUN/'staged',t['path']);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dst)
    placements=read(RUN/'current-inputs'/PLACEMENTS);actor=placements['actors'][0]
    hero=Image.open(RUN/'current-inputs'/HERO).convert('RGBA')
    city=Image.open(RUN/'staged/qdao_chibi_game_pack_v4/main-city_2560x1080.png').convert('RGB')
    sprite=hero.resize(tuple(actor['display_size']),Image.Resampling.LANCZOS)
    preview=city.convert('RGBA');preview.alpha_composite(sprite,tuple(actor['top_left']))
    dst=RUN/'staged'/PREVIEW;dst.parent.mkdir(parents=True,exist_ok=True);preview.convert('RGB').save(dst)
    # The new preview becomes the current HUD background snapshot, not a frozen v10 input.
    hud_bg=RUN/'current-inputs'/PREVIEW;hud_bg.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,hud_bg)
    input_index=read(RUN/'current-inputs.json')
    input_index['generated_current_background']={'path':PREVIEW,'snapshot':hud_bg.relative_to(RUN).as_posix(),'sha256':sha(hud_bg),'recipe':'Existing v4 actor placement and LANCZOS 160x160 sprite, unchanged feet_at and top_left.'}
    write(RUN/'current-inputs.json',input_index)
    hud_target=RUN/'staged'/HUD_SOURCE;hud_target.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run([str(NODE),str(RUN/'compose_hud.mjs'),str(SHARP),str(hud_bg),str(RUN/'current-inputs'/HUD/'hud_overlay.png'),str(hud_target)],check=True)
    shutil.copy2(hud_target,RUN/'staged'/HUD_EXPORT)
    checks=[]
    def check(name, ok): checks.append({'check':name,'passed':bool(ok)})
    files=[]
    for p in targets:
        i=info(RUN/'staged'/p);check('RGB 2560x1080: '+p,i['mode']=='RGB' and i['size']==[2560,1080])
        files.append({'path':p,**i,'staged':'staged/'+p,'before':next(b for b in before if b['path']==p)})
    for g in plan['copy_groups']:
        for t in g['targets']:check('Exact accepted runtime source: '+t['path'],sha(RUN/'staged'/t['path'])==g['copy_source']['sha256'])
    hero_mask=Image.new('L',(2560,1080),0);hero_mask.paste(sprite.getchannel('A'),tuple(actor['top_left']))
    check('Preview identical outside unchanged hero alpha',outside_same(preview,city,hero_mask))
    check('Existing actor feet and top-left retained',actor['feet_at']==[1240,680] and actor['top_left']==[1160,529])
    visible=sprite.getchannel('A').getbbox()
    transformed_anchor=[actor['top_left'][i]+actor['source_feet_anchor'][i]*actor['display_size'][i]/actor['source_size'][i] for i in (0,1)]
    check('Existing source feet anchor transforms within half a pixel',all(abs(transformed_anchor[i]-actor['feet_at'][i])<=.5 for i in (0,1)))
    visible_body=sprite.getchannel('A').point(lambda x:255 if x>5 else 0).getbbox()
    check('Rendered solid boot baseline within one pixel',abs(actor['top_left'][1]+visible_body[3]-actor['feet_at'][1])<=1)
    overlay=Image.open(RUN/'current-inputs'/HUD/'hud_overlay.png').convert('RGBA')
    hud=Image.open(hud_target).convert('RGB')
    check('HUD identical to new preview outside existing overlay alpha',outside_same(hud,preview,overlay.getchannel('A')))
    check('HUD two public preview files byte-identical',sha(RUN/'staged'/HUD_SOURCE)==sha(RUN/'staged'/HUD_EXPORT))
    for g in guards:check('Protected input unchanged: '+g['path'],sha(ROOT/g['path'])==g['sha256'])
    qa=RUN/'qa';qa.mkdir(exist_ok=True)
    board=Image.new('RGB',(1536,648),'#e8e5dd')
    for i,g in enumerate(plan['copy_groups']):
        im=Image.open(RUN/'current-inputs'/g['copy_source']['path']).convert('RGB').resize((768,324),Image.Resampling.LANCZOS)
        board.paste(im,((i%2)*768,(i//2)*324))
    board.save(qa/'four-current-backgrounds.jpg',quality=94)
    before_hud=Image.open(RUN/'before'/HUD_EXPORT).convert('RGB')
    board=Image.new('RGB',(1536,648),'#e8e5dd')
    for i,im in enumerate([Image.open(RUN/'before'/PREVIEW),preview,before_hud,hud]):
        board.paste(im.convert('RGB').resize((768,324),Image.Resampling.LANCZOS),((i%2)*768,(i//2)*324))
    board.save(qa/'composites-before-after.jpg',quality=94)
    hud.crop((2090,115,2560,525)).save(qa/'hud-native-detail.png')
    preview.crop((1080,450,1410,760)).convert('RGB').save(qa/'hero-native-detail.png')
    errors=[c['check'] for c in checks if not c['passed']]
    write(RUN/'staged-validation.json',{'status':'ready_for_visual_review' if not errors else 'failed','checked_at_utc':now(),'files':files,'checks':checks,'errors':errors,'images_published':0,'preserved_actor':actor,'feet_evidence':{'transformed_anchor':transformed_anchor,'all_alpha_bbox':visible,'alpha_gt_5_bbox':visible_body,'note':'Unchanged LANCZOS sprite has 2-pixel low-alpha tail; feet contract uses original source anchor and solid visible boot baseline.'},'review_evidence':{p.name:sha(p) for p in qa.iterdir() if p.is_file()}})
    if errors:raise RuntimeError(str(errors))
    print(json.dumps({'status':'ready_for_visual_review','staged':len(files),'checks':len(checks),'errors':errors},ensure_ascii=True))

def merge_json(rel, transform):
    path=ROOT/rel
    for attempt in range(4):
        original=path.read_bytes() if path.exists() else None
        data=json.loads(original.decode('utf-8-sig')) if original else {}
        changed=transform(copy.deepcopy(data))
        rendered=(json.dumps(changed,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        if (path.read_bytes() if path.exists() else None)!=original:
            time.sleep(.1);continue
        backup=RUN/'before-metadata'/rel;backup.parent.mkdir(parents=True,exist_ok=True)
        if original is not None and not backup.exists():backup.write_bytes(original)
        path.write_bytes(rendered)
        return {'path':rel,'before_sha256':hashlib.sha256(original).hexdigest() if original else None,'after_sha256':sha(path),'backup':backup.relative_to(RUN).as_posix() if original else None}
    raise RuntimeError('Concurrent metadata edits: '+rel)

def publish():
    if (RUN/'publication.json').exists(): raise RuntimeError('Publication already exists; verify or review the journal before rerunning')
    plan,targets=stages();v=read(RUN/'staged-validation.json');approval=read(RUN/'visual-approval.json')
    if v['errors'] or approval['status']!='passed':raise RuntimeError('Validation/visual approval not ready')
    approved={r['path']:r['sha256'] for r in approval['files']}
    before=read(RUN/'before-index.json')
    for g in before['protected']:
        if sha(ROOT/g['path'])!=g['sha256']:raise RuntimeError('Protected file changed: '+g['path'])
    for s in read(RUN/'current-inputs.json')['files']:
        if sha(ROOT/s['path'])!=s['sha256']:raise RuntimeError('Current input changed: '+s['path'])
    records=[]
    lineage={t['path']:{'group':g['id'],'source_path':g['copy_source']['path'],'source_sha256':g['copy_source']['sha256'],'native_source':g['native_source'],'adaptation':g['source_adaptation']} for g in plan['copy_groups'] for t in g['targets']}
    for f in v['files']:
        p=f['path']
        if p not in targets or approved.get(p)!=f['sha256'] or sha(RUN/f['staged'])!=f['sha256']:raise RuntimeError('Unapproved staged target')
        if sha(ROOT/p) not in (f['before']['sha256'],f['sha256']):raise RuntimeError('Concurrent image edit: '+p)
    write(RUN/'publication-journal.json',{'status':'publishing','started_at_utc':now(),'allowed_targets':targets})
    for f in v['files']:
        p=f['path'];shutil.copyfile(RUN/f['staged'],ROOT/p)
        records.append({'path':p,'decision':'adopt_accepted_scene' if p not in (PREVIEW,HUD_SOURCE,HUD_EXPORT) else 'recompose_existing_layers','before_sha256':f['before']['sha256'],'after_sha256':sha(ROOT/p),'backup':f['before']['backup'],'size':f['size'],'mode':f['mode'],'bytes':f['bytes'],'visual_status':'passed','approval':'visual-approval.json','client_written':False,'lineage':lineage.get(p,{'recipe':'compose_hud.mjs' if p in (HUD_SOURCE,HUD_EXPORT) else 'Existing v4 actor composition using Pillow LANCZOS','current_inputs':'current-inputs.json','actor_feet_at':[1240,680]})})
    stage_manifest='../qdao_festival_refinement_20260910/scenes-sync/publication.json'
    runtime=read(ROOT/'qdao_festival_scenes_20260910/runtime/runtime-manifest.json')
    runtime_by={e['id']:e for e in runtime['outputs']}
    metadata=[]
    def v4(m):
        m.setdefault('scene_export_history',[]).append(m.get('scene_export',{}))
        e=runtime_by['01_main_city_wide']
        m['scene_export']={'source':'../qdao_festival_scenes_20260910/main_city_wide/scene-native.png','source_size':e['nativeSize'],'output_size':[2560,1080],'method':'Exact accepted runtime copy after recorded proportional crop/LANCZOS adaptation','runtime_source':'../qdao_festival_scenes_20260910/runtime/'+e['runtimeFile'],'source_crop_box_xyxy':e['sourceCropBox'],'resampled':True,'new_native_resolution':False}
        for f in m['files']:
            if f['path'] in ('main-city_2560x1080.png','preview-main-city_2560x1080.png'):
                f.update(info(ROOT/'qdao_chibi_game_pack_v4'/f['path']))
        m['festival_scene_sync']={'record':stage_manifest,'scope':'Background and actor preview only; hero and placement unchanged','client_written':False}
        return m
    metadata.append(merge_json('qdao_chibi_game_pack_v4/manifest.json',v4))
    def v5(m):
        unchanged={e['id']:copy.deepcopy(e) for e in m['screens'] if e['id'] not in ('04_main_city_hud','05_battle_scene','06_battle_entry_loading')}
        mapping={'05_battle_scene':('battle_forest_bridge','04_battle_forest_bridge'),'06_battle_entry_loading':('battle_entry','05_battle_entry')}
        for e in m['screens']:
            ident=e['id']
            if ident=='04_main_city_hud':
                for k in ('source','export'):
                    e[k].update(info(ROOT/'qdao_ui_redesign_v5'/e[k]['path']))
                e['creation_method']='accepted_festival_city_recomposed_with_unchanged_v10_HUD_and_current_v4_hero'
                e['recipe']='../qdao_festival_refinement_20260910/scenes-sync/compose_hud.mjs'
                e['current_input_snapshot']='../qdao_festival_refinement_20260910/scenes-sync/current-inputs.json'
            elif ident in mapping:
                scene,rid=mapping[ident];rt=runtime_by[rid]
                e.setdefault('source_history',[]).append({k:copy.deepcopy(e.get(k)) for k in ('source','recipe','resampling','source_crop_box_xyxy','creation_method')})
                native=ROOT/'qdao_festival_scenes_20260910'/scene/'scene-native.png'
                e['source']={'path':'../qdao_festival_scenes_20260910/'+scene+'/scene-native.png',**info(native)}
                e['recipe']='../qdao_festival_scenes_20260910/'+scene+'/scene.prompt.txt'
                e['export'].update(info(ROOT/'qdao_ui_redesign_v5'/e['export']['path']))
                e['creation_method']='adopt_accepted_image_gen_scene_runtime_export'
                e['resampling']='Exact accepted runtime copy; native art adapted by proportional source-box LANCZOS'
                e['source_crop_box_xyxy']=rt['sourceCropBox']
                e['native_2560x1080_generation']=False
                e['relative_aspect_error']=abs((rt['nativeSize'][0]/rt['nativeSize'][1])/(2560/1080)-1)
                e['current_export_provenance']=stage_manifest
        if any(unchanged[k]!=next(e for e in m['screens'] if e['id']==k) for k in unchanged):raise RuntimeError('Touched another screen')
        m['festival_scene_sync']={'record':stage_manifest,'screen_ids':['04_main_city_hud','05_battle_scene','06_battle_entry_loading'],'original_generated_sources_retained':True,'client_written':False}
        return m
    metadata.append(merge_json('qdao_ui_redesign_v5/manifest.json',v5))
    def hud(m):
        m['source_background'].update({'path':PREVIEW,'sha256':sha(ROOT/PREVIEW),'size':[2560,1080],'role':'current_festival_city_actor_preview'})
        m['source_builder']='qdao_festival_refinement_20260910/scenes-sync/compose_hud.mjs'
        m['current_input_snapshot']='qdao_festival_refinement_20260910/scenes-sync/current-inputs.json'
        m['validation']['exact_original_pixels_outside_overlay']=True
        m['staged_only']=False
        m['festival_scene_sync']={'record':'../../qdao_festival_refinement_20260910/scenes-sync/publication.json','only_preview_recomposed':True,'layers_labels_buttons_unchanged':True}
        return m
    metadata.append(merge_json('qdao_ui_redesign_v5/hud/placement.json',hud))
    def prepared(m):
        # Keep historical client status, records, failures and hashes verbatim.
        m['scene_prepared_refresh']={'status':'repository_prepared_copies_updated','checked_at_utc':now(),'record':stage_manifest,'client_checked':False,'client_written':False,'historical_client_status_unchanged':True,'records':[r for r in records if r['path'].startswith('client_ui_refresh_20260908/prepared/')]}
        return m
    metadata.append(merge_json('client_ui_refresh_20260908/assets_manifest.json',prepared))
    def additional(m):
        e=runtime_by['02_login_landscape']
        return {'status':'current_repository_background','output':'login_background.png','size':[2560,1080],'mode':'RGB','sha256':sha(ROOT/'client_ui_refresh_20260908/additional/login_background.png'),'native_source':'../../qdao_festival_scenes_20260910/login_landscape/scene-native.png','runtime_source':'../../qdao_festival_scenes_20260910/runtime/'+e['runtimeFile'],'source_crop_box_xyxy':e['sourceCropBox'],'uniformScale':e['uniformScale'],'historical_generation_record_retained':'login_background.generation.json','client_written':False,'publication':'../../qdao_festival_refinement_20260910/scenes-sync/publication.json'}
    metadata.append(merge_json('client_ui_refresh_20260908/additional/login_background.current.json',additional))
    write(RUN/'publication.json',{'status':'published_pending_final_file_check','published_at_utc':now(),'image_count':18,'files':records,'metadata_updates':metadata,'current_input_snapshot':'current-inputs.json','validation':'staged-validation.json','visual_approval':'visual-approval.json','client_written':False,'frozen_contracts_modified':False,'inventory_or_monitor_state_modified':False})
    verify()

def verify():
    pub=read(RUN/'publication.json');before=read(RUN/'before-index.json');errors=[]
    for f in pub['files']:
        p=ROOT/f['path'];i=info(p)
        if i['sha256']!=f['after_sha256'] or i['size']!=[2560,1080] or i['mode']!='RGB' or i['bytes']!=f['bytes']:errors.append('Final output: '+f['path'])
        if sha(RUN/f['backup'])!=f['before_sha256']:errors.append('Backup: '+f['path'])
    for g in before['protected']:
        if sha(ROOT/g['path'])!=g['sha256']:errors.append('Protected: '+g['path'])
    historical_prepared=read(RUN/'before-metadata/client_ui_refresh_20260908/assets_manifest.json')
    current_prepared=read(ROOT/'client_ui_refresh_20260908/assets_manifest.json')
    for k,value in historical_prepared.items():
        if k!='scene_prepared_refresh' and current_prepared.get(k)!=value:errors.append('Historical prepared metadata field changed: '+k)
    frozen_hud=read(RUN/'current-inputs'/HUD/'placement.json')
    current_hud=read(ROOT/HUD/'placement.json')
    for k in ('canvas','layout','text','buttons','artifacts','source_component'):
        if current_hud[k]!=frozen_hud[k]:errors.append('HUD contract metadata changed: '+k)
    write(RUN/'final-verification.json',{'status':'passed' if not errors else 'failed','verified_at_utc':now(),'image_files':18,'backup_files':18,'protected_files':len(before['protected']),'errors':errors,'metadata':[{'path':x['path'],'sha256':sha(ROOT/x['path'])} for x in pub['metadata_updates']],'client_written':False})
    if errors:raise RuntimeError(str(errors))
    pub['status']='published_and_verified';pub['final_verification']='final-verification.json';write(RUN/'publication.json',pub)
    write(RUN/'publication-journal.json',{'status':'complete','completed_at_utc':now(),'image_files':18})
    print(json.dumps({'status':pub['status'],'image_files':18,'protected_files':len(before['protected']),'errors':errors},ensure_ascii=True))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['stage','publish','verify'])
    action=parser.parse_args().action
    globals()[action]()
