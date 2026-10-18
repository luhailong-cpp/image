from pathlib import Path
import json,sys
z=Path(__file__).resolve().parents[1]
print(json.dumps([{'stem':s,'prompt':(z/'prompts'/f'{s}.txt').read_text(encoding='utf8'),'refs':[x['path'] for x in json.loads((z/'guides'/f'{s}.references.json').read_text())]} for s in sys.argv[1:]]))
