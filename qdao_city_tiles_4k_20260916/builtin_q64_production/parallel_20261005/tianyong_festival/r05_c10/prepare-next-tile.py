from pathlib import Path
from PIL import Image
import numpy as np
import json,hashlib,datetime
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10"); B.mkdir(exist_ok=True)
B6=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r06_c10")
ROOT=Path(r"D:/work/image")
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{"file":str(p),"sha256":sha(p)}
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding="utf-8")
master=ROOT/"tianyong_festival_hd_20260910/tianyong_city_master_6144.png"
assert sha(master)=="aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428"
im=Image.open(master).convert("RGB")
im.crop((3456,1536,3840,1920)).save(B/"canonical-native384-layout-only.png")
im.resize((1254,1254),Image.Resampling.BICUBIC,box=(3456,1536,3840,1920)).save(B/"canonical-full-layout-guide-only.png")
final=B6/"r01_c04-v1/final-v1/r06_c10-fragment.png"
assert sha(final)=="13ecc290a82ad4efb949d2287cd56d06393f2c98fbc84aee279d93259c3688eb"
a=np.array(Image.open(final).convert("RGBA"))
halo=np.zeros((115,4096,4),dtype=np.uint8); sources=[]
for c,fv in [(1,1),(2,1),(3,2),(4,1)]:
 mp=B6/f"r01_c{c:02}-v1/final-v{fv}/manifest.json"
 m=json.loads(mp.read_text(encoding="utf-8-sig")); jp=Path(m["joined"]["file"])
 assert sha(jp)==m["joined"]["sha256"]
 j=np.array(Image.open(jp).convert("RGBA")); sources.append({"manifest":ref(mp),"joined":ref(jp)})
 for p in m["patches"]:
  if p["name"] not in ["new-core","left-return"]:continue
  l,_,r,_=p["cropFromJoinedLTRB"]; x,_,z,_=p["destinationTileLTRB"]
  halo[:,x:z]=j[:115,l:r]
assert np.all(halo[:,:,3]==255)
Image.fromarray(halo).save(B/"r06-top-external-halo-native.png")
Image.fromarray(a[:115]).save(B/"r06-top115-current-native.png")
Image.fromarray(np.concatenate([halo,a[:115]],axis=0)).save(B/"r06-top-context230-native.png")
write(B/"native-context-provenance.json",{"preparedAtUTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"preparation-only-await-root-source-confirmation","source06":ref(final),"externalHalo":ref(B/"r06-top-external-halo-native.png"),"top115":ref(B/"r06-top115-current-native.png"),"combined230":ref(B/"r06-top-context230-native.png"),"externalHaloSources":sources,"externalHaloGlobalLTRB":[36864,20365,40960,20480],"combinedGlobalLTRB":[36864,20365,40960,20595],"operation":"Exact native top115 external halo composed by selected top-row manifests new-core and left-return ownership, followed by final tile top115. No resizing or warp.","nativeScale":1,"doesNotClaimR05Coverage":True,"rootPublished":False})
windows=[]
for col in [4,3,2,1]:
 name=f"r04_c{col:02}-prepare";d=B/name;d.mkdir(exist_ok=True)
 x=(col-1)*1024-115;y=2957;world=[36864+x,16384+y,36864+x+1254,16384+y+1254]
 im.resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world)).save(d/"layout-reference-only.png")
 c=np.zeros((1254,1254,4),dtype=np.uint8);l=max(0,x);r=min(4096,x+1254)
 c[1024:1139,l-x:r-x]=halo[:,l:r];c[1139:1254,l-x:r-x]=a[:115,l:r]
 Image.fromarray(c).save(d/"bottom-context-only.png")
 windows.append({"patch":f"r04_c{col:02}","globalCropLTRB":world,"tileLocalCropLTRB":[x,y,x+1254,y+1254],"layout":ref(d/"layout-reference-only.png"),"bottomContext":ref(d/"bottom-context-only.png"),"knownBottomPixels":int((c[:,:,3]==255).sum()),"sideContextNotPreparedUntilPriorPatchExists":True})
write(B/"preparation-index.json",{"tile":"r05_c10","tileGlobalOrigin":[36864,16384],"tileGlobalLTRB":[36864,16384,40960,20480],"canonicalMaster":ref(master),"canonicalNativeCropLTRB":[3456,1536,3840,1920],"canonicalScaleNumerator":3,"canonicalScaleDenominator":32,"canonicalGuideOnly":True,"nativeContextProvenance":ref(B/"native-context-provenance.json"),"suggestedSequence":[f"r{row:02}_c{col:02}" for row in [4,3,2,1] for col in ([4,3,2,1] if row in [4,2] else [1,2,3,4])],"bottomWindows":windows,"imageGenerationCalls":0,"rootPublished":False,"formalAccepted":False})
print(json.dumps({"prepared":str(B),"windows":windows}))

