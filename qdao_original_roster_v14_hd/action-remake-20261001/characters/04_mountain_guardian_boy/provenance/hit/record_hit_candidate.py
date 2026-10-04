from pathlib import Path
import json,hashlib,re,argparse
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
PROV=ROOT/"provenance"/"hit"
p=argparse.ArgumentParser();p.add_argument("--stem",required=True);p.add_argument("--review",required=True);p.add_argument("--note",required=True);a=p.parse_args()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
subpath=PROV/(a.stem+".submission.json");sub=json.loads(subpath.read_text(encoding="utf-8-sig"))
native=PROV/(a.stem+".native.png")
with Image.open(native) as im:
 im.load();size=list(im.size);mode=im.mode;alpha=list(im.getchannel("A").getextrema())
refs=[]
for i,s in enumerate(sub["submittedParameters"]["referenced_image_paths"],1):
 with Image.open(s) as im: dims=list(im.size)
 refs.append({"inputIndex":i,"path":s,"sha256":sha(s),"pixelDimensions":dims,"viewed":True,"passedToTool":True})
times=re.findall(rb"20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z",native.read_bytes())
record={"schemaVersion":1,"character":ROOT.name,"action":"hit","direction":sub["direction"],"frame":sub["frame"],"file":native.relative_to(ROOT).as_posix(),"sha256":sha(native),"generatedAt":times[0].decode() if times else None,"width":size[0],"height":size[1],"format":"PNG","mode":mode,"alphaExtrema":alpha,"tool":"image_gen.imagegen","route":"builtin","configSnapshot":sub["configTarget"],"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":sub["submittedParameters"]["referenced_image_paths"],"prompt":(PROV/(a.stem+".prompt.txt")).relative_to(ROOT).as_posix()},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露具体版本或质量；C2PA泛称不推断。","references":refs,"evidence":{"submission":str(subpath),"receipt":str(PROV/(a.stem+".receipt.json"))},"review":{"status":a.review,"note":a.note},"clientIntegration":"not_integrated"}
(PROV/(a.stem+".generation.json")).write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"stem":a.stem,"sha256":record["sha256"],"size":size,"review":a.review},ensure_ascii=False))

