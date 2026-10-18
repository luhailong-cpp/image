from pathlib import Path
from PIL import Image
import hashlib,json,datetime
T=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r13_c12")
j=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
active=j(T/"active-native-map.json")
evidence=[]
for patch,v in active.items():
 p=T/"native"/(v+".png"); r=j(T/"records"/(v+".receipt.json"))
 evidence.append({"patch":patch,"version":v,"size":list(Image.open(p).size),"sha256":sha(p),"receiptHashMatch":sha(p)==r["outputSha256"]})
v="p04_02_v20261017T024544_fe99be36"
prep=j(T/"records"/(v+".preparation.json"))
contract=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/production-contract.json")
report={"checkedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"scope":"root r13_c12 only; selected files and latest return checked, no history rescan","activeCount":len(active),"activeEvidence":evidence,"preparedVersion":v,"preparedReceiptExists":(T/"records"/(v+".receipt.json")).exists(),"preparedNativeExists":(T/"native"/(v+".png")).exists(),"contractPath":str(contract),"contractSha256":sha(contract),"latestReturnedAlreadyIngested":"exec-879f4482-980c-43cd-b4da-ab8af643e39f.png","formalAccepted":False}
out=T/"records"/("restart-recovery-"+datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")+".json")
with out.open("x",encoding="utf-8") as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps({"record":str(out),"sha256":sha(out),"result":report,"prepKeys":list(prep)},ensure_ascii=False))
