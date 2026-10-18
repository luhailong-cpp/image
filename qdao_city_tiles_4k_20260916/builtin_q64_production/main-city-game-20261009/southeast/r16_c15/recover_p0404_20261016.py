from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, subprocess, sys
from PIL import Image
T=Path(__file__).resolve().parent
V='p04_04_v20261014T035144_86a707ac'
S=Path('C:/Users/luyua/.codex/generated_images/01a12574-41dd-7d81-a4ed-b0121666894d/exec-8e7d3c93-55d0-4bf2-a596-12a77b7dbe59.png')
P=T/'records'/f'{V}.receipt.json'
assert S.is_file() and not P.exists()
im=Image.open(S); assert im.size==(1254,1254)
stamp=datetime.fromtimestamp(S.stat().st_mtime,timezone.utc).isoformat()
record={'status':'succeeded_pending_native_seam_review','tool':'image_gen.imagegen','route':'builtin','generatedAt':None,'recoveredAt':datetime.now(timezone.utc).isoformat(),'originalOutput':str(S),'outputSha256':hashlib.sha256(S.read_bytes()).hexdigest(),'actualSize':list(im.size),'actualModel':None,'actualQuality':None,'resizedAfterGeneration':False,'finalArtUpscaled':False,'sourceFileModifiedAtUtc':stamp,'timestampBasis':'Filesystem modification time only; exact service generation time unavailable','evidence':'Recovered existing PNG from previous south_production builtin generation directory after interruption. Last prior ingested file at 03:12 UTC, sole subsequent output at 04:02 UTC follows 03:51 p04_04 preparation. Visually compared full native against saved last edit target: matching upper limestone course, buttress geometry, left foundation joints and lower foliage. No fresh generation and no reconstructed tool result/output_hint is claimed.','sourceAttribution':'strong local provenance and visual match; original tool-result text unavailable in resumed child context','formalAccepted':False}
P.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(subprocess.check_output([sys.executable,str(T/'local_workflow.py'),'ingest','r16_c15',V,str(S),str(P)],text=True))
