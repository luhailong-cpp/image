"""Audit every baseline art file for coverage, same-size replacement and cleanup.

Run after all deliveries and cleanup. This does not generate or modify artwork.
"""
from pathlib import Path
import hashlib,json,re,sys
from collections import Counter
from urllib.parse import unquote
import xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
EXTENSIONS={'.png','.jpg','.jpeg','.webp','.gif','.svg'}

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def inspect(path):
    if path.suffix.lower()=='.svg':
        root=ET.parse(path).getroot()
        return {'mode':'SVG','xml_parsed':True,'sha256':digest(path)}
    with Image.open(path) as im: im.verify()
    with Image.open(path) as im:
        result={'size':list(im.size),'mode':im.mode,'sha256':digest(path)}
        if im.mode=='RGBA':
            alpha=im.getchannel('A')
            result['alpha_range']=list(alpha.getextrema())
        return result

def main():
    audit=json.loads((REPO/'docs/ART_ASSET_AUDIT.json').read_text(encoding='utf8'))
    rows=[]; errors=[]
    for asset in audit['assets']:
        name=asset['path']; path=REPO/name
        row={'path':name,'family':asset['family'],'planned_action':asset['action']}
        if not path.exists():
            if asset['action']!='delete_after_replacement': errors.append(f'Missing deliverable: {name}')
            row['result']='removed_process_image' if asset['action']=='delete_after_replacement' else 'missing'
        else:
            actual=inspect(path); row['actual']=actual
            if path.suffix.lower()!='.svg' and actual['size']!=asset['size']:
                errors.append(f'Pixel size changed: {name}')
            old_hash=asset.get('sha256',asset.get('baseline_sha256'))
            changed=actual['sha256']!=old_hash
            row['changed_from_baseline']=changed
            if asset['action'] in ('redraw_same_path','rebuild_same_layout') and not changed:
                errors.append(f'Unfinished old art: {name}')
            if asset['action']=='delete_after_replacement': errors.append(f'Process image still present: {name}')
            if asset.get('mode')=='RGBA' and actual['mode']!='RGBA': errors.append(f'Lost Alpha: {name}')
            row['result']='updated_same_size' if changed else 'preserved'
        rows.append(row)
    for directory in ('q_daoist_character_pack_4096/.work','character_move_8dir/.work','qdao_asset_refresh_v6/icons/.work','qdao_chibi_game_pack_v4/.work','qdao_asset_refresh_v6/pets/.work'):
        if (REPO/directory).exists(): errors.append(f'Temporary processing directory remains: {directory}')
    # Decode every new/updated visual in task directories as well.
    decoded=0
    for directory in ('qdao_asset_refresh_v6','qdao_ui_redesign_v5','exact_qdao_slices','character_move_8dir','q_daoist_character_pack_4096','qdao_chibi_pets_v1','q_daoist_login_ui_uncropped_highres_final_layers','q_daoist_login_ui_10240_redraw_clear_final_layers'):
        for p in (REPO/directory).rglob('*'):
            if p.is_file() and p.suffix.lower() in EXTENSIONS:
                inspect(p); decoded+=1
    # Check all project Markdown links (prompts, provenance strings and historic
    # audit path fields are records, not promises of current filesystem links).
    links=0
    for p in REPO.rglob('*.md'):
        rel=p.relative_to(REPO)
        if any(part in ('.git','.agents','.work','node_modules') for part in rel.parts): continue
        body=re.sub(r'```.*?```','',p.read_text(encoding='utf-8-sig'),flags=re.S)
        for raw in re.findall(r'\]\(([^)]+)\)',body):
            target=raw.strip().strip('<>').split('#')[0]
            if not target or re.match(r'^(https?:|app:|codex:|mailto:|data:)',target): continue
            target=unquote(target)
            if not (p.parent/target).exists(): errors.append(f'Broken document link {rel}: {raw}')
            links+=1
    result={'baseline_commit':'60134a6','status':'passed' if not errors else 'failed',
        'baseline_visual_count':len(rows),'result_counts':dict(Counter(r['result'] for r in rows)),
        'visual_files_decoded_in_delivery_directories':decoded,'markdown_local_links_checked':links,
        'errors':errors,'assets':rows,'engine_integration':False,
        'size_note':'Pixel dimensions preserved; native generated size recorded separately in per-asset records.'}
    (ROOT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='assets'},ensure_ascii=False,indent=2))
    if errors: sys.exit(1)

if __name__=='__main__': main()
