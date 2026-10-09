from pathlib import Path
T=Path(__file__).resolve().parent
p=T/'helper.py';s=p.read_text(encoding='utf-8-sig')
start=s.index('def setup():');end=s.index('def update(',start)
s=s[:start]+"def setup():\n    raise RuntimeError('Already initialized with setup_tile.py; do not rerun setup.')\n\n"+s[end:]
s=s.replace("[src,state['north']['anchor'],state['east']['anchor']]","[src,state['north']['anchor']]")
s=s.replace("dest=ROOT/'current-preview.png';","dest=ROOT/'qa'/f'progress-{len(names):02d}.png';")
p.write_text(s,encoding='utf8')

