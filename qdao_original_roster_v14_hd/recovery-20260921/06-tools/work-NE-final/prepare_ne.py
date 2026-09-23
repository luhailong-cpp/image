from pathlib import Path
import argparse, importlib.util, json
HERE=Path(__file__).resolve().parent
TOOLS=HERE.parent
REC=TOOLS.parent
ROOT=REC.parents[1]
spec=importlib.util.spec_from_file_location('archive06',TOOLS/'archive_generation.py')
archive=importlib.util.module_from_spec(spec);spec.loader.exec_module(archive)
p=argparse.ArgumentParser();p.add_argument('frame',type=int);p.add_argument('--version',default='v2');p.add_argument('--extra',default='');p.add_argument('--reference',action='append',default=[]);a=p.parse_args()
prompt=(REC/'work-N-NE/plans/NE'/f'{a.frame:02d}.prompt.txt').read_text(encoding='utf-8-sig')
if a.extra: prompt+='\n'+a.extra+'\n'
refs=[ROOT/'qdao_original_roster_v13/references/06_thunder_caster_boy/original-identity-1024.png',ROOT/'qdao_original_roster_v13/candidate/06_thunder_caster_boy/idle/NE.png',ROOT/'designs/jubaozhai-ui/02-characters.png']+[Path(p).resolve() for p in a.reference]
request=archive.prepare(f'NE{a.frame:02d}-final-{a.version}',prompt,refs)
print(json.dumps(request,ensure_ascii=False))
