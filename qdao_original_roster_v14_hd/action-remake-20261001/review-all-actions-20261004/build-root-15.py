from pathlib import Path

root = Path(__file__).resolve().parent
source = (root / 'group-c' / 'build_audit.py').read_text(encoding='utf-8')
old_ids = "IDS=['10_crimson_spear_girl','14_short_hair_snow_summoner_girl','15_water_dragon_scholar_boy','17_ghost_script_calligrapher_boy','20_star_formation_master_girl']"
old_out = "OUT=BASE/'review-all-actions-20261004/group-c'"
assert source.count(old_ids) == 1 and source.count(old_out) == 1
source = source.replace(old_ids, "IDS=['15_water_dragon_scholar_boy']")
source = source.replace(old_out, "OUT=BASE/'review-all-actions-20261004/root-15'")
exec(compile(source, str(root / 'group-c' / 'build_audit.py'), 'exec'))
