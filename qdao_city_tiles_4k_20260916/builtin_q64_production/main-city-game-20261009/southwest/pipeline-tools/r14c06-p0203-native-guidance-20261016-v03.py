from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[1];T=B/'r14_c06'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=T/'pipeline/returned-native/p02_03.resume-20261016-v02.returned.png'
seed=T/'pipeline/guides/p02_03.recover-20261013c-v01.continuity-seed.png'
out=T/'pipeline/guides/p02_03.resume-20261016-v03.native-anchor-guidance.png'
dis=T/'pipeline/returned-native/p02_03.resume-20261016-v02.disposition.json'
assert not out.exists() and not dis.exists()
def put(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
put(dis,dict(recordedAtUtc=now,source=str(src),sourceSha256=sha(src),selected=False,formalAccepted=False,visualReview='actual native image viewed',improved=['invented upper frame removed'],blockingIssues=['invented diagonal paving seams in top native anchor area','red paper is clipped at y230 input-strip boundary instead of continuing below the strip','left anchor paving outlines do not match original quiet gray native strip'],decision='preserve unselected; one focused native-anchor edit'))
im=Image.open(src).convert('RGB');s=Image.open(seed).convert('RGB');assert im.size==s.size==(1254,1254)
im.paste(s.crop((0,0,230,1254)),(0,0));im.paste(s.crop((0,0,1254,230)),(0,0));im.save(out)
put(out.with_suffix('.derivation.json'),dict(createdAtUtc=now,purpose='mechanical guidance only; not a generated final or selected native',source=str(src),sourceSha256=sha(src),nativeAnchorSource=str(seed),nativeAnchorSourceSha256=sha(seed),operations=['exact left 230px native strip pasted','exact top 230px native strip pasted; top owns corner'],resampling=False,programmaticArtwork=False,finalArtwork=False,outputSha256=sha(out)))
print(json.dumps(dict(guidance=str(out),sha256=sha(out),disposition=str(dis))))

