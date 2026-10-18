from pathlib import Path
import json
W=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest/work-r06_c02')
s=(W/'apply_junction_1_2_v02.py').read_text()
s=s.replace("name='r06_c02_junction_1_2_v02';base=W/'joint-v1';O=W/'joint-v2'","name='r06_c02_ground_joint_v01';base=W/'joint-v2';O=W/'ground-v1'")
s=s.replace("x,y=1421,397;","x,y=2445,0;")
s=s.replace("old[y:y+1254,x:x+1254][mask]=new[mask];ids[y:y+1254,x:x+1254][mask]=sid","clip=mask[115:];old[:1139,x:x+1254][clip]=new[115:][clip];ids[:1139,x:x+1254][clip]=sid")
s=s.replace("Image.fromarray(old[y:y+1254,x:x+1254])","Image.fromarray(old[:1139,x:x+1254])")
s=s.replace("O.mkdir(exist_ok=True)","O.mkdir(exist_ok=False)")
(W/'apply_ground_joint_v01.py').write_text(s)

