from pathlib import Path
import json,hashlib
D=Path(__file__).parent;p=D.parent/'r02_c04-v1/pending-review-addendum.json';a=json.loads(p.read_text());m=D/'final-v2/manifest.json';a.update({'status':'closed by mandatory subsequent r02c03 whole-side and rounded-tip coupled return','resolutionManifest':{'file':str(m),'sha256':hashlib.sha256(m.read_bytes()).hexdigest()},'nativeQA':['whole-left-side.png','tip-right-return-edge.png','main1254.png'],'openInternalFindings':[]});p.write_text(json.dumps(a,indent=2))
