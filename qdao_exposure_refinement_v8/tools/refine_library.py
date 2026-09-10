"""Audit-driven local grading, immutable backups, staged outputs, safe publish.

No generation calls, external applications, or client writes. The original
audit hashes are the source of truth. Re-running never grades a graded image.
"""
from __future__ import annotations
import argparse, hashlib, json, os, shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from PIL import Image, PngImagePlugin
from grade_core import VERSION, PRESETS, grade_png_bytes, grade_image, grade_rgb, metrics
from svg_grade import grade_svg_bytes
from gif_grade import grade_gif_bytes

ROOT=Path(__file__).resolve().parents[2]
V8=ROOT/'qdao_exposure_refinement_v8'
PROCESSING=V8/'processing.json'

def sha(data):return hashlib.sha256(data).hexdigest()
def file_sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def safe(base,p):
    out=(base/p).resolve()
    if not out.is_relative_to(base.resolve()):raise ValueError(f'Path outside workspace: {p}')
    return out
def write_json(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    temp=p.with_suffix(p.suffix+'.tmp')
    temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    os.replace(temp,p)
def prepared_sources():
    result={}
    for a in json.loads((ROOT/'client_ui_refresh_20260908/assets_manifest.json').read_text('utf8'))['records']:
        if a.get('staged') and a.get('source'):
            result['client_ui_refresh_20260908/'+a['staged']]=a['source']
    return result
SOURCE_MAP=prepared_sources()

def classify(path):
    original=path
    path=SOURCE_MAP.get(path,path).lower()
    name=Path(path).name
    if path.startswith('tianyong_city_6x6/'):
        return 'preserve','map','All 40 map artworks inspected: stable midtones, no significant veiling highlights'
    if any(t in path for t in ('dim_overlay','walkmask','hud_labels','/labels.svg')):
        return 'preserve','technical','Functional mask or text layer; preserve exact pixels and semantics'
    if any(t in name for t in ('disabled','status_gray')) or name=='muted.png':
        return 'preserve','ui_disabled','Intentional subdued state; preserve state contrast'
    if any(t in path for t in ('qstyle_redrawn_600x600/','/icons/source/','/icons_weapon/')):
        return 'item','item','Deep jade and object shading are sound; only gently roll off the brightest surfaces'
    if ('characters/' in path or 'q_daoist_character_pack_' in path or path.startswith('character_move_8dir/')
        or '/pet/' in path or '/pets/' in path or 'qdao_chibi_pets_' in path or any(t in name for t in
        ('hero','lidazui_hair_daoist','companion','lingyue','hutuantuan','fuxiaohu','yunjiujiu'))):
        return 'character','character','Preserve skin, fur color and dark clothing; mild, fixed highlight rolloff across all frames'
    if 'clouds_fg' in name or name=='battle_clouds.png':
        return 'cloud','cloud','Keep alpha and cloud softness; gently reduce white RGB highlights'
    if path.startswith('designs/attribute-panels/v2-painted/'):
        return 'ui_soft','painted_ui','Already warm paper; soften remaining bright paper gently while protecting dark labels'
    if path.startswith('designs/attribute-panels/') and '/assets/' not in path:
        return 'ui','ui_preview','Large bright paper surfaces; maintain dark text and existing layout'
    if 'login_background' in name:
        return 'scene','scene','Large sunlight, pale stone and mist are the main exposure problem'
    if any(t in name for t in ('01_login','02_server_select','03_character_select')):
        return 'screen','screen','Selective middle/high-light compression across baked UI and environment'
    if '/scenes/' in path or '/source/' in path and path.startswith('qdao_ui_redesign_v5/'):
        return 'scene','scene','Scene highlight rolloff with unchanged shadow tones'
    if path.startswith('qdao_ui_redesign_v5/') and (name.startswith('05_') or name.startswith('06_')):
        return 'scene','scene','Bright stone, sky and mist; preserve foreground texture'
    if any(t in name for t in ('main-city','main_city','battle_arena','battle_entry_loading','scene_bg')):
        return 'scene','scene','Bright landscape or composite scene; preserve the original arrangement'
    if any(t in path for t in ('/ui/','/components/','exact_qdao_slices/','redrawn_atomic/','final_layers/','/hud/','/assets/')):
        if any(t in name for t in ('emblems','badge','icon_','status_','flower','corner','divider','logo','check','lock','recommend')):
            return 'item','ui_symbol','Small functional symbol: only tame peak reflection, retain signal colors'
        return 'ui','ui','Reduce large ivory highlights, preserve dark text, geometry and state contrast'
    if 'login' in name or 'ugui_' in name:
        return 'screen','screen','Legacy screen alias: control paper and daylight highlights'
    return 'ui_soft','misc','Conservative high-light-only correction after full-library visual review'

def choose_path(paths):
    def priority(p):
        if p.startswith('qdao_ui_redesign_v5/'):return 0
        if p.startswith(('qdao_chibi_game_pack_v4/','character_move_8dir/','q_daoist_character_pack_')):return 1
        if p.startswith('qdao_gpt_image2_refresh_v7/'):return 2
        if '/prepared/' in p or '/assets/' in p:return 5
        return 3
    return min(paths,key=lambda p:(priority(p),len(p),p))

def make_plan():
    inventory=json.loads((V8/'inventory.json').read_text('utf8'))
    included=[a for a in inventory['assets'] if a['treatment_included'] or a['classification']=='technical_preserve']
    groups=defaultdict(list)
    for a in included:groups[a['sha256']].append(a)
    rows=[]
    for original_sha,assets in groups.items():
        canonical=choose_path([a['path'] for a in assets])
        preset,kind,reason=classify(canonical)
        if any(a['classification']=='technical_preserve' for a in assets):
            preset,kind,reason='preserve','technical','Preserve functional text, masks and diagnostics'
        protect=any(a.get('metrics',{}).get('magenta_chroma_fraction',0)>.03 for a in assets)
        for a in assets:
            rows.append(dict(path=a['path'],original_sha256=original_sha,output_sha256=original_sha,
                backup='backups/'+original_sha+a['extension'],changed=False,kind=kind,preset=preset,
                reason=reason,canonical_path=canonical,protect_chroma=protect,
                classification=a['classification'],before_metrics=a.get('metrics'),
                expected_size=a.get('size'),expected_mode=a.get('mode'),
                status='planned'))
    return dict(schema_version=1,workspace_root=ROOT.as_posix(),created_utc=datetime.now(timezone.utc).isoformat(),
        status='planned',algorithm=VERSION,presets=PRESETS,records=sorted(rows,key=lambda r:r['path']),
        scanned_visual_files=inventory['summary']['total_visual_files'],
        excluded_counts=inventory['summary']['by_classification'],
        authorization='User confirmed repair of all exposure/washed-out assets after the proposed categorized local selective-grading workflow',
        expect_highlight_reduction=False,validation_policy={'shadow_max_mean_drop':.04,'shadow_retention_min':.60})

def load_plan():
    if PROCESSING.exists():
        plan=json.loads(PROCESSING.read_text('utf8'))
        if plan['algorithm']!=VERSION or plan['presets']!=PRESETS:
            raise RuntimeError('Preset/version differs from frozen plan. Review rather than grading an existing output twice.')
        return plan
    plan=make_plan();write_json(PROCESSING,plan);return plan

def backup(plan):
    for i,r in enumerate(plan['records']):
        src=safe(ROOT,r['path']); dest=safe(V8,r['backup'])
        if dest.exists():
            if file_sha(dest)!=r['original_sha256']:raise RuntimeError(f'Corrupt original backup: {dest}')
        else:
            if file_sha(src)!=r['original_sha256']:raise RuntimeError(f'Asset changed after audit: {src}')
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
        if i%100==0:print(f'Original backups verified {i}/{len(plan["records"])}',flush=True)

def specialized_png(data,path,preset,protect):
    # Preserve intentional disabled/gray cells in shared UI source sheets.
    if path.endswith('/ui/source/ui-skins-native.png'):
        with Image.open(BytesIO(data)) as src:
            out=src.copy()
            for i in range(9):
                x,y=i%3,i//3;box=(round(src.width*x/3),round(src.height*y/3),round(src.width*(x+1)/3),round(src.height*(y+1)/3))
                cell=src.crop(box);out.paste(grade_image(cell,'preserve' if i==2 else 'ui'),box)
            b=BytesIO();out.save(b,format='PNG',compress_level=6,**({'icc_profile':src.info['icc_profile']} if src.info.get('icc_profile') else {}));return b.getvalue()
    if path.endswith('/ui/source/ui-emblems-native.png'):
        with Image.open(BytesIO(data)) as src:
            out=src.copy()
            for i in range(16):
                x,y=i%4,i//4;box=(round(src.width*x/4),round(src.height*y/4),round(src.width*(x+1)/4),round(src.height*(y+1)/4))
                out.paste(grade_image(src.crop(box),'preserve' if i==15 else 'item'),box)
            b=BytesIO();out.save(b,format='PNG',compress_level=6,**({'icc_profile':src.info['icc_profile']} if src.info.get('icc_profile') else {}));return b.getvalue()
    return grade_png_bytes(data,preset,protect)

def stage(plan):
    backup(plan)
    groups=defaultdict(list)
    for r in plan['records']:groups[r['original_sha256']].append(r)
    ordered=sorted(groups.values(),key=lambda group:(Path(group[0]['path']).suffix=='.svg',group[0]['path']))
    png_outputs={}
    class OnDiskPngIndex:
        def __contains__(self,key):return key in png_outputs
        def __getitem__(self,key):return png_outputs[key].read_bytes()
        def get(self,key,default=None):return self[key] if key in self else default
    index=OnDiskPngIndex()
    for number,group in enumerate(ordered,1):
        r=group[0];ext=Path(r['path']).suffix
        target=V8/'staged'/f'{r["original_sha256"]}{ext}'
        data=safe(V8,r['backup']).read_bytes()
        extra={}
        if target.exists() and all(x['status'] in ('staged','published') for x in group):
            result=target.read_bytes()
            if sha(result)!=r['output_sha256']:raise RuntimeError(f'Staged file altered: {target}')
        else:
            if r['preset']=='preserve':result=data
            elif ext=='.png':result=specialized_png(data,r['canonical_path'],r['preset'],r['protect_chroma'])
            elif ext=='.gif':result,extra=grade_gif_bytes(data,lambda rgb:grade_rgb(rgb,r['preset']))
            elif ext=='.svg':
                def missing(_data):raise RuntimeError(f'Embedded PNG not found in graded originals: {r["path"]}')
                result,extra=grade_svg_bytes(data,missing,png_sha256_index=index)
            else:raise ValueError(f'Unhandled extension: {ext}')
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(result)
        if ext=='.png':png_outputs[r['original_sha256']]=target
        out_sha=sha(result)
        for item in group:
            item.update(output_sha256=out_sha,changed=out_sha!=item['original_sha256'],staged=target.relative_to(V8).as_posix(),
                        status='staged',expect_highlight_reduction=False)
            if extra:item['format_validation']=extra
        if number%20==0:
            plan['status']='staging';write_json(PROCESSING,plan)
            print(f'Staged {number}/{len(ordered)} unique sources',flush=True)
    plan['status']='staged';plan['summary']=dict(total_records=len(plan['records']),changed=sum(r['changed'] for r in plan['records']),
        by_preset=dict(Counter(r['preset'] for r in plan['records'])))
    write_json(PROCESSING,plan);print(json.dumps(plan['summary']),flush=True)

def publish(plan):
    if plan['status'] not in ('staged','publishing','published'):raise RuntimeError('Stage all outputs before publishing')
    # First validate every target to avoid overwriting another task's changes.
    for r in plan['records']:
        current=file_sha(safe(ROOT,r['path']))
        if current not in (r['original_sha256'],r['output_sha256']):raise RuntimeError(f'Concurrent asset change: {r["path"]}')
        if file_sha(safe(V8,r['staged']))!=r['output_sha256']:raise RuntimeError('Staged hash mismatch')
    for i,r in enumerate(plan['records'],1):
        dest=safe(ROOT,r['path'])
        if r['changed'] and file_sha(dest)!=r['output_sha256']:
            temp=dest.with_name(dest.name+'.exposure-v8.tmp')
            shutil.copyfile(safe(V8,r['staged']),temp);os.replace(temp,dest)
        r['status']='published'
        if i%100==0:
            plan['status']='publishing';write_json(PROCESSING,plan);print(f'Published {i}/{len(plan["records"])} files',flush=True)
    plan['status']='published';plan['published_utc']=datetime.now(timezone.utc).isoformat();write_json(PROCESSING,plan)
    print(json.dumps(plan['summary']),flush=True)

def restore(plan):
    for r in plan['records']:
        dest=safe(ROOT,r['path']);current=file_sha(dest)
        if current not in (r['original_sha256'],r['output_sha256']):raise RuntimeError(f'Changed since grading; restore refused: {dest}')
    for r in plan['records']:
        shutil.copyfile(safe(V8,r['backup']),safe(ROOT,r['path']))
    plan['status']='staged'
    for r in plan['records']:r['status']='staged'
    write_json(PROCESSING,plan)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['plan','stage','publish','restore']);a=ap.parse_args()
    plan=load_plan()
    if a.action=='plan':print(json.dumps(dict(records=len(plan['records']),by_preset=dict(Counter(r['preset'] for r in plan['records']))),indent=2))
    elif a.action=='stage':stage(plan)
    elif a.action=='publish':publish(plan)
    else:restore(plan)
if __name__=='__main__':main()
