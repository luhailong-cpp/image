from pathlib import Path
import json,sys
d=Path(sys.argv[1]);r=json.loads((d/'request.json').read_text(encoding='utf-8-sig'));r['payload']['prompt']+='\n'+Path(sys.argv[2]).read_text(encoding='utf-8-sig');(d/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(d/'prompt.txt').write_text(r['payload']['prompt'],encoding='utf-8');print(json.dumps(r))
