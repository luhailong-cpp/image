from pathlib import Path
import json,sys
b=Path(__file__).resolve().parents[2]
n=int(sys.argv[1]);newkey=sys.argv[2];p=b/'run/W'/f'{n:02}.png.generation.json'
r=json.loads(p.read_text(encoding='utf-8'));r['review']['status']='rejected-identity-drift-replaced-by-'+newkey;r['review']['rejectionReason']='Native targeted identity repair restores canonical short bob and robe, preserves phase.'
p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
(b/'provenance'/Path(r['prompt']).with_suffix('.generation.json').name).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')

