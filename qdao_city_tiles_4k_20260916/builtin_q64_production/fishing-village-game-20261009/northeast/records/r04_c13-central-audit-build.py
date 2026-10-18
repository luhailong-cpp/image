from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parent.parent
T="r04_c13"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def rf(p): return {"path":str(Path(p).resolve()).replace("\\","/"),"sha256":sha(p)}
def wr(p,d):
 p=Path(p); assert not p.exists(),p; p.write_text(json.dumps(d,indent=2)+"\n")
v1=rd(Z/"qa"/(T+"-central-v1")/"manifest.json")
v2=rd(Z/"qa"/(T+"-central-v2")/"manifest.json")
S1=rd(Z/"records"/(T+".selection-central-v1.json"))["patches"]
S2=rd(Z/"records"/(T+".selection-central-v2.json"))["patches"]
q1=Z/"qa"/(T+"-central-v1"); q2=Z/"qa"/(T+"-central-v2")
# Every current candidate core/QA crop is independently checked against decoded source pixels.
can=Image.open(v2["candidate"]["file"]).convert("RGB")
rebuild=Image.new("RGB",(4096,4096))
proof=[]
for key,s in S2.items():
 p=Z/s["path"]; assert sha(p)==s["sha256"]
 im=Image.open(p).convert("RGB");assert im.size==(1254,1254)
 r,c=int(key[-2]),int(key[-1]);at=((c-1)*1024,(r-1)*1024)
 core=im.crop((115,115,1139,1139));rebuild.paste(core,at)
 proof.append({"patch":key,**rf(p),"coreRgbSha256":hashlib.sha256(core.tobytes()).hexdigest()})
assert rebuild.tobytes()==can.tobytes()
for e in v2["qa"]:
 assert sha(e["file"])==e["sha256"]
 assert Image.open(e["file"]).convert("RGB").tobytes()==can.crop(e["candidateCropBox"]).tobytes()
# Cache reuse is allowed only where exact native seam pixels and source hashes match.
reuse=[]
for e in v1["qa"]:
 if e["kind"] not in ("vertical_boundary","horizontal_boundary"):continue
 ids=e["neighborPatchIds"]; chosen=ids[1] if e["kind"]=="vertical_boundary" else ids[0]
 stem=Path(S1[chosen]["path"]).stem
 side="left" if e["kind"]=="vertical_boundary" else "bottom"
 old=Z/"qa"/f"{stem}-exact_native_{side}_230px.png"
 review=Z/"qa"/f"{stem}.central-resume-review.json"
 rr=rd(review);assert rr["native"]["sha256"]==S1[chosen]["sha256"]
 assert rr["fullNativeViewed"] and any(x["sha256"]==sha(old) for x in rr["nativeSeamsViewed"])
 di=rd(str(old)+".derived.json")
 assert {x["sha256"] for x in di["sources"]}=={S1[x]["sha256"] for x in ids}
 crop=(0,115,256,1139) if side=="left" else (115,0,1139,256)
 assert Image.open(old).convert("RGB").crop(crop).tobytes()==Image.open(e["file"]).convert("RGB").tobytes()
 reuse.append({"qa":rf(e["file"]),"review":rf(review),"previousNativeSeam":rf(old),"exactReviewCrop":crop,"sourceHashesUnchanged":True,"pixelEquality":True})
wr(q1/"central-reuse-proof.json",{"seams":reuse,"count":len(reuse),"note":"Exact pixel crops establish that previous native1to1 fast edge inspections cover these complete core seams; no blind status propagation."})
pending1={"core_p13.native-1to1.png":"Lower-left rectangular guide remnant; repaired in p13-v2.",
"v_p12_p13.native-1to1.png":"Same p13 interior guide remnant visible near edge bottom.",
"h_p13_p23.native-1to1.png":"Same p13 interior remnant near strip top-left.",
"junction_r1_c2.native-1to1.png":"Same p13 interior rectangular guide remnant.",
"h_p23_p33.native-1to1.png":"Outer upright silhouettes meet; fine wood face/grain change across seam around tile x2618..2648 remains visual pending, nonblocking geometry."}
entries=[]
for e in v1["qa"]:
 name=Path(e["file"]).name
 entries.append({"qa":rf(e["file"]),"kind":e["kind"],"status":"pending" if name in pending1 else "pass","note":pending1.get(name,"Native forms and current seams visually consistent; no blocking defect observed."),"method":"direct_native1to1_view" if e["kind"] not in ("vertical_boundary","horizontal_boundary") or name in ("h_p23_p33.native-1to1.png","h_p24_p34.native-1to1.png") else "exact_native_review_reuse_with_pixel_and_source_proof"})
wr(q1/"central-review-49.json",{"candidate":rf(v1["candidate"]["file"]),"reviewer":"/root/central_resume","qaItems":entries,"total":49,"pass":44,"pending":5,"formalAccepted":False,"sourceReuseProof":rf(q1/"central-reuse-proof.json")})
old={Path(x["file"]).name:x for x in v1["qa"]}
changed=[]; unchanged=[]
for e in v2["qa"]:
 name=Path(e["file"]).name
 (unchanged if e["sha256"]==old[name]["sha256"] else changed).append(name)
wr(q2/"central-mechanical-and-delta.json",{"candidate":rf(v2["candidate"]["file"]),"sourceCount":16,"nativeSizes":[1254,1254],"allCorePixelsIndependentlyRebuilt":True,"all49QAExactCandidateCrops":True,"sources":proof,"previousReview":rf(q1/"central-review-49.json"),"unchangedQA":unchanged,"changedQA":changed,"formalAccepted":False})
# Available external edges are candidate-to-candidate evidence, not global acceptance.
Q=q2/"external-native-QA";Q.mkdir(exist_ok=True)
sources={}
for key,s in S2.items():sources[key]=Z/s["path"]
southSel=Z/"records"/"r05_c13.selection-sol-v3.json"
south=rd(southSel)["patches"]
for key,s in south.items():
 if key[-2]=="1":
  p=Path(s["path"] if isinstance(s,dict) else s);p=p if p.is_absolute() else Z/p
  if isinstance(s,dict):assert sha(p)==s["sha256"]
  sources[key]=p
for tile in ["r04_c12","r04_c14"]:
 d=rd(Z/"records"/(tile+".working-selection.json"))
 for key,name in d.items():
  if (tile.endswith("12") and key[-1]=="4") or (tile.endswith("14") and key[-1]=="1"):sources[key]=Z/"native"/name
items=[]
def qa(name,size,pieces,role):
 out=Image.new("RGB",size);rr=[]
 for key,box,at in pieces:
  p=sources[key];im=Image.open(p).convert("RGB");assert im.size==(1254,1254);out.paste(im.crop(box),at);rr.append({"patch":key,**rf(p),"crop":box,"at":at})
 path=Q/(name+".png");assert not path.exists();out.save(path)
 items.append({"name":name,**rf(path),"role":role,"size":size,"sources":rr,"operation":"exact integer crop and opaque paste only","resized":False,"visualReview":"pending"})
for r in range(1,5):
 a=f"r04_c12_p{r}4";b=f"r04_c13_p{r}1"
 if a in sources:qa(f"west-r{r}",(256,1024),[(a,[1011,115,1139,1139],[0,0]),(b,[115,115,243,1139],[128,0])],"external segment")
for c in range(1,5):
 a=f"r04_c13_p4{c}";b=f"r05_c13_p1{c}"
 qa(f"south-c{c}",(1024,256),[(a,[115,1011,1139,1139],[0,0]),(b,[115,115,1139,243],[0,128])],"external segment")
for r in range(1,5):
 a=f"r04_c13_p{r}4";b=f"r04_c14_p{r}1"
 if b in sources:qa(f"east-r{r}",(256,1024),[(a,[1011,115,1139,1139],[0,0]),(b,[115,115,243,1139],[128,0])],"external segment")
def junction(name,keys):
 boxes=[[883,883,1139,1139],[115,883,371,1139],[883,115,1139,371],[115,115,371,371]]
 ats=[[0,0],[256,0],[0,256],[256,256]]
 if all(k in sources for k in keys):qa(name,(512,512),list(zip(keys,boxes,ats)),"external junction")
for r in range(1,4):
 junction(f"west-junction-r{r}",[f"r04_c12_p{r}4",f"r04_c13_p{r}1",f"r04_c12_p{r+1}4",f"r04_c13_p{r+1}1"])
 junction(f"east-junction-r{r}",[f"r04_c13_p{r}4",f"r04_c14_p{r}1",f"r04_c13_p{r+1}4",f"r04_c14_p{r+1}1"])
for c in range(1,4):junction(f"south-junction-c{c}",[f"r04_c13_p4{c}",f"r04_c13_p4{c+1}",f"r05_c13_p1{c}",f"r05_c13_p1{c+1}"])
# Southwest corner deferred because neighboring diagonal selection has not been pinned here.
wr(Q/"manifest.json",{"candidate":rf(v2["candidate"]["file"]),"southSelection":rf(southSel),"neighborStatus":"Pinned current sources; west/east working candidates, no formal neighbor acceptance implied","qa":items,"north":"missing","eastRemaining":"r3/r4 neighbor left column missing","southwestDiagonal":"pending pinned r05_c12 p14 source","formalAccepted":False})
print(json.dumps({"changedQA":changed,"unchangedQA":len(unchanged),"externalQA":len(items)}))

