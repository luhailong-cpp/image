import sys
sys.dont_write_bytecode=True
from pathlib import Path
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest')
s=(z/'qa/full-tile-assemble.py').read_text(encoding='utf-8-sig')
s=s.replace('p = Path(rec["file"])','p = Path(rec["file"])\n            if args.tile=="r08_c04" and (r,c)==(3,3):\n                p=QA/"west-corner-r08r09c04c05-v3-r08_c04-context-native.png"\n                rec=dict(rec, file=p.as_posix(), sha256="c2c59645d633ad978eee215a4b5a7f8411b8feb71214bcb0c3a7883fa7042e83")')
s=s.replace('prefix = "full-tile-"+args.tile','prefix = "full-tile-"+args.tile+"-1016-v1"')
s=s.replace('p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)', 'p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)')
s=s.replace('"script":{"path":Path(__file__).as_posix()', '"nativeCornerOverride":{"patch":"p04_04","trace":(QA/"west-corner-r08r09c04c05-v3-export-trace.json").as_posix(),"traceSha256":"015bbf27d6fcbcad638e3ee1131b70424fb5bdb3bd512de7bf1e09d1874f5f8e","originalGenerationSha256":"1164e0cab46036479a0aa4298c7ee6091a70f53e38227a3ba750a90291f2a95f","method":"Previously audited native pixel selection only; partial 1254 context replaces base source, not a new AI generation"},\n      "script":{"path":Path(__file__).as_posix()')
p=z/'qa/full-tile-r08c04-assemble-1016-v1.py'
assert not p.exists()
p.write_text(s,encoding='utf-8')

