"""Deterministic delivery from accepted image_gen NPCs; never generates artwork."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib, re, datetime, zipfile
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write_json(p, value): p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding="utf-8")
def rel(p): return p.relative_to(ROOT).as_posix()
roster=json.loads((ROOT/"roster.json").read_text(encoding="utf-8-sig"))
all_npcs=roster["npcs"]+roster.get("supplemental",[])
sources={}
raw_paths=list((ROOT/"characters").glob("*.png"))+list((ROOT/"supplemental").glob("*.png"))
for p in raw_paths:
    m=re.match(r"(\d\d)[-_]",p.name)
    if m:
        if m[1] in sources: raise RuntimeError("Duplicate accepted NPC "+m[1])
        sources[m[1]]=p
missing=[n["id"] for n in all_npcs if n["id"] not in sources]
if missing: raise RuntimeError("Still missing NPCs: "+",".join(missing))
entries=[]
for npc in all_npcs:
    p=sources[npc["id"]]
    recs=[p.with_name(p.name+".generation.json"),p.with_suffix(".generation.json")]
    rec=next((q for q in recs if q.exists()),None)
    if rec is None: raise RuntimeError("Missing generation record: "+str(p))
    raw=Image.open(p)
    if raw.mode!="RGBA": raise RuntimeError("Missing true alpha: "+str(p))
    a=raw.getchannel("A")
    if a.getextrema()!=(0,255): raise RuntimeError("Unexpected alpha extrema: "+str(p))
    rawhash=sha(p)
    record=json.loads(rec.read_text(encoding="utf-8-sig"))
    if record.get("sha256") != rawhash: raise RuntimeError("Generation hash mismatch: "+str(rec))
    # Remove only nearly invisible alpha (<=3/255) from export copies.
    cleaned=raw.copy()
    cleaned.putalpha(a.point(lambda v:0 if v<=3 else v))
    bbox=cleaned.getchannel("A").getbbox()
    cropped=cleaned.crop(bbox)
    exports=[]
    for size in (1024,2048):
        folder=ROOT/("transparent-"+str(size))
        folder.mkdir(exist_ok=True)
        limit=round(size*.76)
        scale=min(limit/cropped.width,limit/cropped.height)
        dims=(max(1,round(cropped.width*scale)),max(1,round(cropped.height*scale)))
        resized=cropped.resize(dims,Image.Resampling.LANCZOS)
        frame=Image.new("RGBA",(size,size))
        x=round((size-resized.width)/2)
        bottom=round(size*.88)
        y=bottom-resized.height
        frame.alpha_composite(resized,(x,y))
        dst=folder/p.name
        frame.save(dst,optimize=True)
        ea=frame.getchannel("A")
        eb=ea.getbbox()
        assert eb and eb[0]>0 and eb[1]>0 and eb[2]<size and eb[3]<size
        deriv={"file":dst.name,"sha256":sha(dst),"width":size,"height":size,"format":"PNG","mode":"RGBA",
            "createdAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "derivedFrom":[{"file":rel(p),"sha256":rawhash,"generationRecord":rel(rec)}],
            "operation":{"type":"alpha_cleanup_crop_uniform_resize_and_pad","removeAlphaAtOrBelow":3,
                "sourceCrop":bbox,"uniformScale":scale,"interpolation":"LANCZOS",
                "pasteTopLeft":[x,y],"visibleBBox":eb,"canvasBottomAnchor":[size/2,bottom],
                "notes":"Transparent static export; canvas alignment uses silhouette bottom, not a verified skeleton foot pivot. Upsampling is not new native detail."},
            "nativeSourceSize":list(raw.size),"actualModel":record.get("actualModel"),"actualQuality":record.get("actualQuality")}
        drec=dst.with_name(dst.name+".derivation.json"); write_json(drec,deriv)
        exports.append({"size":size,"file":rel(dst),"sha256":sha(dst),"derivation":rel(drec),"visibleBBox":eb,
                        "pivotBottomLeftNormalized":[.5,.12]})
    entries.append({"id":npc["id"],"name":npc["name"],"source_image":npc["source_image"],
        "raw":rel(p),"rawSha256":rawhash,"nativeSize":list(raw.size),"generationRecord":rel(rec),
        "actualModel":record.get("actualModel"),"actualQuality":record.get("actualQuality"),
        "export":exports,"alphaZeroFraction":a.histogram()[0]/(raw.width*raw.height),
        "referenceCompleteness":npc.get("referenceCompleteness","complete_or_mostly_complete"),"designInterpretation":npc.get("designInterpretation"),"status":"delivered_static"})
fontfile="C:/Windows/Fonts/msyh.ttc"
font=ImageFont.truetype(fontfile,26)
small=ImageFont.truetype(fontfile,19)
title=ImageFont.truetype(fontfile,45)
for filename,bg,fg in [("overview.jpg","#f6f1e6","#284b43"),("qa-dark.jpg","#293535","#e9e4d6")]:
    canvas=Image.new("RGB",(2000,170+485*((len(entries)+4)//5)),bg); d=ImageDraw.Draw(canvas)
    d.text((60,30),"五行奇谈 · 主城 NPC",font=title,fill=fg)
    d.text((62,94),str(len(entries))+" 位独立透明站立素材 / 21—23 为局部参考的职业补全稿",font=small,fill=fg)
    for i,e in enumerate(entries):
        col=i%5; row=i//5; x=col*400; y=145+row*485
        im=Image.open(ROOT/e["export"][0]["file"]); im.thumbnail((390,420),Image.Resampling.LANCZOS)
        canvas.paste(im,(x+(400-im.width)//2,y),im)
        label=e["id"]+"  "+e["name"]
        w=d.textbbox((0,0),label,font=font)[2]
        d.text((x+(400-w)//2,y+425),label,font=font,fill=fg)
    canvas.save(ROOT/filename,quality=94,subsampling=0)
    write_json(ROOT/(filename+".derivation.json"),{"file":filename,"sha256":sha(ROOT/filename),
        "operation":"contact_sheet_of_accepted_exports_with_external_labels",
        "derivedFrom":[{"file":e["export"][0]["file"],"sha256":e["export"][0]["sha256"],
                        "derivation":e["export"][0]["derivation"]} for e in entries]})
manifest={"schema_version":1,"createdAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "scope":"20 reference-led NPCs plus 3 explicitly labeled profession-based completions; static artwork",
    "referenceStyle":"designs/team-ui-v2/team-ui-v2.png",
    "actualModelNote":"Host-managed builtin image generation did not disclose actual model or quality.",
    "npcCount":len(entries),"entries":entries,"referenceGaps":roster["deferred"]}
write_json(ROOT/"manifest.json",manifest)
write_json(ROOT/"validation.json",{"checkedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "expectedNpcCount":len(all_npcs),"actualNpcCount":len(entries),"allSourcePNGsRGBA":True,
    "allExportPNGsRGBA":True,"allExportsHaveTransparentMargins":True,"allSourceHashesMatchRecords":True,
    "allDerivedImagesTraceable":True,"automatedStatus":"passed",
    "visualStatus":"pending_final_review","notValidated":["animation","client scene placement","runtime foot pivots"]})
for n in all_npcs: n["asset_status"]="delivered_static"
roster["status"]="static_assets_delivered"; roster["counts"]={"main_completed":20,"supplemental_completed":len(roster.get("supplemental",[])),"total_completed":len(all_npcs),"reference_gaps":3}
roster["completion_note"]="20张主体NPC及3张职业补全静态透明图已交付。21—23不可见细节为原创补全，仍标明参考缺口；未接入客户端或制作动画。"
write_json(ROOT/"roster.json",roster)
print(json.dumps({"accepted":len(entries),"exports":len(entries)*2,"overview":str(ROOT/"overview.jpg")},ensure_ascii=False))
