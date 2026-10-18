from pathlib import Path
old=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c07/workflow_20261013.py');t=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r05_c08')
s=old.read_text(encoding='utf-8')
a=s.index('NEIGHBORS={');b=s.index('\ndef ref',a)
s=s[:a]+"NEIGHBORS={'r05_c07':('r05_c07/candidate/r05_c07-candidate-localcut-e280bcf6d4f6.png','75374335df252505edbb301d18c17bca9434b8ac74852bdafa698eaba41f10ec')}"+s[b:]
s=s.replace("TILE='r07_c07'","TILE='r05_c08'").replace('/root/continue_r07_c07','/root/continue_r07_c07')
(t/'workflow_20261016.py').write_text(s,encoding='utf-8')

