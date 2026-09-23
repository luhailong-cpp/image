"""Preserve already returned root-owned results without selecting them for delivery."""
import json,re,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
for folder in sorted((HERE.parent/'09-generation').iterdir()):
    if not folder.is_dir() or not re.fullmatch(r'((S|SE)(\d\d|-idle)-v\d+|N(\d\d|idle)-heel-v\d+)',folder.name): continue
    result=folder/'tool-result.json'
    if not result.exists() or (folder/'generation.json').exists(): continue
    hint=json.loads(result.read_text(encoding='utf-8-sig'))['output_hint']
    original=re.search(r' as (.+?\.png) by default\.',hint).group(1)
    subprocess.run([sys.executable,'-B',str(HERE/'archive_generation.py'),'--archive',str(folder),'--original',original,'--tool-result',str(result)],check=True)
