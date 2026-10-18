from pathlib import Path
T=Path(__file__).resolve().parent
source=T.parent/'r14_c10/color_match_tile_finish_20261013.py'
dest=T/'color_match_tile_finish_20261016.py';assert not dest.exists()
code=source.read_text(encoding='utf-8-sig').replace('r14_c10','r09_c10').replace('finish-20261013-v1','finish-20261016-v1').replace("native-selected-before-color-finish-v1.json","qa/joint-20261016-v1/joint-candidate-selected.json")
code=code.replace('No color correction used to conceal geometry; all 24 seams and 9 crossings inspected; geometry reviewed; color and texture acceptance remains pending native visual review','All 33 internal native QA inspected. Local stone joint geometry improved in candidate, perimeter texture and west short roof joint still pending. Color processing does not certify or conceal geometry; candidate remains unaccepted.')
code=code.replace("role='geometry-reviewed selected input pixels'","role='selected native input candidate; unresolved geometry/material issues remain separately recorded'")
code=code.replace("role='geometry-reviewed source color bound anchor'","role='native source color bound anchor'")
dest.write_text(code,encoding='utf-8')
print(dest)
