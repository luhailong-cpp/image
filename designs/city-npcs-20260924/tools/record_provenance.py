from pathlib import Path
import json,importlib.util,hashlib
ROOT=Path(__file__).resolve().parents[1]
modpath=ROOT/"tools/inspect_image_provenance.py"
spec=importlib.util.spec_from_file_location("npc_provenance",modpath)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
count=0
for p in list((ROOT/"characters").rglob("*.png"))+list((ROOT/"supplemental").rglob("*.png")):
    rec=next((r for r in [p.with_name(p.name+".generation.json"),p.with_suffix(".generation.json")] if r.exists()),None)
    if rec is None: raise RuntimeError("Missing record "+str(p))
    d=json.loads(rec.read_text(encoding="utf-8-sig"))
    pr=mod.inspect_image(p)
    pp=p.with_name(p.name+".provenance.json")
    pp.write_text(json.dumps(pr,ensure_ascii=False,indent=2),encoding="utf-8")
    created=pr["created_actions"]
    versions=[x["software_agent"].get("version") for x in created if isinstance(x.get("software_agent"),dict)]
    d["actualModel"]=versions[0] if versions else None
    d["actualModelVersion"]=None
    d["actualQuality"]=None
    d["unverifiedReason"]="内嵌C2PA softwareAgent.version仅为gpt-image系列；宿主未披露2.5/2.0具体版本、API分支或质量。来源声明已解析但未验证数字签名。"
    d["evidence"]["embeddedProvenance"]=pp.name
    d["evidence"]["embeddedSoftwareAgents"]=[x["software_agent"] for x in created]
    d["evidence"]["c2paSignatureVerified"]=False
    d["officialAvailabilityCheckedOn"]="2026-09-24"
    d["sha256"]=pr["sha256"]
    if created: d["generatedAt"]=created[0]["when"]
    d["width"],d["height"]=pr["native_size"]
    d["format"]="PNG"
    rec.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
    count+=1
print("C2PA declarations recorded for",count,"generated images, including candidates.")
