"""Keep old 4096 hero resource names while using the approved Q Daoist master."""
from pathlib import Path
import hashlib,json
from PIL import Image

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent

def main():
    current = Path(__file__).resolve().parents[1] / 'qdao_character_diversity_v9/festival_edge_refinement.json'
    if current.exists():
        import runpy
        runpy.run_path(str(current.parent.parent / 'qdao_festival_refinement_20260910/v9-edges/verify_current.py'), run_name='__main__')
        return
    audit=json.loads((REPO/'docs/ART_ASSET_AUDIT.json').read_text(encoding='utf8'))
    source=REPO/'qdao_chibi_game_pack_v4/hero-transparent_1024.png'
    hero=Image.open(source).convert('RGBA')
    names=[a['path'] for a in audit['assets'] if a['family']=='hero_variants_7']+[
        'q_daoist_character_pack_4096/00_reference_topright_boy_transparent_4096.png',
        'q_daoist_character_pack_4096/q_daoist_topright_character_full_uncropped_transparent_4096.png']
    records=[]
    for name in names:
        target=REPO/name
        hero.resize((4096,4096),Image.Resampling.LANCZOS).save(target,optimize=True)
        with Image.open(target) as im:
            assert im.size==(4096,4096) and im.mode=='RGBA'
            assert im.getchannel('A').getextrema()==(0,255)
        records.append({'path':name,'source':source.relative_to(REPO).as_posix(),
            'method':'approved identity reuse, RGBA LANCZOS compatibility export',
            'size':[4096,4096],'master_export_size':[1024,1024],
            'native_4096_generation':False,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'old_variant_identity_retired':True,'original_filename_retained_for_compatibility':True})
    result={'status':'art_assets_only','reason':'User requested all old art be unified with accepted gold-headband Q boy',
            'recipe':'build_hero_compat.py','source_manifest':'../qdao_chibi_game_pack_v4/manifest.json',
            'assets':records}
    (ROOT/'hero_compat_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(f'Verified {len(records)} same-size canonical hero compatibility exports')

if __name__=='__main__': main()
