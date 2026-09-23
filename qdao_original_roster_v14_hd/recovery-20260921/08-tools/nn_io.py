"""Private N/NE evidence writer. Receives exact host request and receipt JSON."""
import json,sys,shutil
from pathlib import Path
from process import GEN,write,process
data=json.load(sys.stdin)
for row in data:
    name=row['attempt']
    if not name.startswith(('walk-N-','walk-NE-')): raise ValueError(name)
    p=GEN/name
    if 'request' in row:
        if (p/'request.json').exists(): raise ValueError('Existing request '+name)
        write(p/'request.json',row['request'])
        (p/'prompt.txt').write_text(row['request']['parameters']['prompt'],encoding='utf-8')
    if 'receipt' in row:
        if (p/'raw.png').exists(): raise ValueError('Existing raw '+name)
        write(p/'receipt.json',row['receipt'])
        shutil.copy2(row['source'],p/'raw.png')
        print(json.dumps(process(name)))
