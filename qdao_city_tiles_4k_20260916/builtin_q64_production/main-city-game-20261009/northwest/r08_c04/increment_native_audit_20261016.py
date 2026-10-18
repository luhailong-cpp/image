"""Increment r08_c04 native candidates without regenerating unchanged QA crops.
Default: 18 -> 20 sources with the two independently approved native patches.
Additional batches may be passed through --config JSON. All geometry is same-world.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, copy, hashlib, json
import numpy as np
from PIL import Image

T=Path(__file__).resolve().parent
BASE="native-18-source-audit-20261014T025300734151Z-854bea01d277e120"
def read(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return {"file":str(p),"sha256":sha(p)}
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
def pixel_key(im):
    im=im.convert("RGB")
    return f"{im.width}x{im.height}:"+hashlib.sha256(im.tobytes()).hexdigest()
def verify(r):
    p=Path(r["file"]); assert sha(p)==r["sha256"],str(p)
    return p
def build(config):
    prev_manifest=Path(config["baseManifest"])
    old=read(prev_manifest)
    applied_overlays=[]
    for overlay_file in config.get("reviewOverlays",[]):
        overlay_file=Path(overlay_file)
        overlay=read(overlay_file)
        assert overlay["actuallyViewed"] is True
        byname={c["name"]:c for c in old["crops"]}
        for reviewed in overlay["crops"]:
            c=byname[reviewed["name"]]
            assert reviewed["actuallyViewed"] is True
            assert reviewed["status"] in {"passed","needs_repair"}
            assert reviewed["sha256"]==c["sha256"]
            assert reviewed.get("pixelKey",c["pixelKey"])==c["pixelKey"]
            verify(reviewed)
            c.update({"status":reviewed["status"],"actuallyViewed":True,
                      "finding":reviewed.get("finding"),"incrementalReviewOverlay":ref(overlay_file)})
        applied_overlays.append(ref(overlay_file))
    base_file=verify(old["candidate"])
    base_dir=base_file.parent
    old_registry_file=verify(old["sourceRegistry"])
    old_registry=read(old_registry_file)
    previous_proof=read(verify(old["pixelProof"]))
    assert previous_proof["status"]=="passed_exact_same_world_native_pixels"
    assert previous_proof["provedPixels"]==16777216
    owner_file=verify(old_registry["ownerIndex"])
    image=Image.open(base_file).convert("RGB")
    assert image.size==(4096,4096)
    baseline=np.array(image)
    owner=np.array(Image.open(owner_file))
    assert owner.shape==(4096,4096)
    registry=copy.deepcopy(old_registry["sources"])
    assert len(registry)==old_registry["sourceCount"]
    assert set(np.unique(owner))=={r["ownerIndex"] for r in registry}
    new_adoptions=[]
    changed_mask=np.zeros((4096,4096),bool)
    for item in config["patches"]:
        proposal_file=Path(item["proposal"])
        proposal=read(proposal_file)
        independent_file=Path(item["independentReview"])
        independent=read(independent_file)
        assert independent["actuallyViewed"] and independent["status"]=="passed_local_native_adoption"
        verify(independent["proposal"])
        assert Path(independent["proposal"]["file"]).resolve()==proposal_file.resolve()
        root_file=verify(independent["rootReview"])
        root=read(root_file)
        assert root["actuallyViewed"] and not root["formalAccepted"]
        source=Path(proposal["source"]);mask_file=Path(proposal["mask"])
        assert sha(source)==proposal["sourceSha256"]==independent["sourceSha256"]
        assert proposal["sourceSha256"] not in {r["sha256"] for r in registry},"Already registered source: use existingSourcePatches"
        assert sha(mask_file)==proposal["maskSha256"]==independent["maskSha256"]
        raw=Image.open(source).convert("RGB");mask_im=Image.open(mask_file)
        assert raw.size==mask_im.size==(1254,1254)
        mask=np.array(mask_im); assert set(np.unique(mask)).issubset({0,255})
        selected=mask==255
        count=int(selected.sum())
        assert count==proposal["selectedPixelCount"]==independent["pixelCount"]
        x,y=proposal["sourceOriginInTile"]
        assert proposal["sourceWorldBox"]==[12288+x,28672+y,12288+x+1254,28672+y+1254]
        x0,y0=max(0,x),max(0,y)
        x1,y1=min(4096,x+1254),min(4096,y+1254)
        assert x0<x1 and y0<y1
        source_box=(slice(y0-y,y1-y),slice(x0-x,x1-x))
        clipped_selection=selected[source_box]
        assert int(clipped_selection.sum())==count,"Selected pixels outside formal tile"
        baseline_target=Path(item.get("baselineTarget",str(source.parent/"edit-target.png")))
        target=Image.open(baseline_target).convert("RGB")
        assert np.array_equal(baseline[y0:y1,x0:x1][clipped_selection],np.array(target)[source_box][clipped_selection]),"Baseline pixels under mask changed"
        assert not changed_mask[y0:y1,x0:x1][clipped_selection].any(),"New repair masks overlap"
        idx=max(r["ownerIndex"] for r in registry)+1
        image.paste(raw,(x,y),mask_im)
        owner[y0:y1,x0:x1][clipped_selection]=idx
        changed_mask[y0:y1,x0:x1][clipped_selection]=True
        generation_file=Path(item.get("generationRecord",str(source.parent/"generation.json")))
        generation=read(generation_file)
        assert generation["sha256"]==proposal["sourceSha256"]
        host=Path(generation["hostPath"])
        if host.exists(): assert sha(host)==sha(source)
        r={"id":source.parent.name,"ownerIndex":idx,"file":str(source),
           "sha256":sha(source),"generationRecord":ref(generation_file),
           "request":ref(Path(item.get("request",str(source.parent/"request.json")))),
           "prompt":ref(Path(item.get("prompt",str(source.parent/"prompt.txt")))),
           "receipt":ref(Path(item.get("receipt",str(source.parent/"tool-receipt.json")))),
           "worldBoxWithHalo":proposal["sourceWorldBox"],"nativeOriginInTile":[x,y],
           "nativeMask":ref(mask_file),"sourcePixelCount":count,
           "sourceROI":proposal["sameWorldNativeROI"],"targetTileROI":proposal["targetTileROI"],
           "proposal":ref(proposal_file),"localApproval":ref(independent_file),
           "baselineTarget":ref(baseline_target),
           "rootReview":ref(root_file),"hostOutputPath":str(host),"hostAvailable":host.exists(),
           "hostBytesIdentical":True if host.exists() else None,"actualModel":generation.get("actualModel"),
           "actualQuality":generation.get("actualQuality")}
        registry.append(r)
        new_adoptions.append({"proposal":ref(proposal_file),"independentReview":ref(independent_file),
            "rootReview":ref(root_file),"ownerIndex":idx,"selectedPixelCount":count,
            "sameWorldBaselineUnderMaskVerified":True})
    for item in config.get("existingSourcePatches",[]):
        proposal_file=Path(item["proposal"]); proposal=read(proposal_file)
        review_file=Path(item["independentReview"]); review=read(review_file)
        assert review["actuallyViewed"] is True and review["status"]=="passed_local_native_adoption"
        assert verify(review["proposal"]).resolve()==proposal_file.resolve()
        root_file=verify(review["rootReview"])
        assert read(root_file)["actuallyViewed"] is True
        source=Path(proposal["source"]);mask_file=Path(proposal["mask"])
        assert sha(source)==proposal["sourceSha256"]==review["sourceSha256"]
        assert sha(mask_file)==proposal["maskSha256"]==review["maskSha256"]
        matches=[r for r in registry if r["sha256"]==proposal["sourceSha256"]]
        assert len(matches)==1,"Existing native source must be registered exactly once"
        existing=matches[0];idx=existing["ownerIndex"]
        assert idx==proposal["existingOwnerIndex"]
        assert existing["nativeOriginInTile"]==proposal["sourceOriginInTile"]
        assert existing["worldBoxWithHalo"]==proposal["sourceWorldBox"]
        raw=Image.open(source).convert("RGB");mask_image=Image.open(mask_file)
        assert raw.size==mask_image.size==(1254,1254)
        mask=np.array(mask_image);assert set(np.unique(mask)).issubset({0,255})
        selected=mask==255;pixel_count=int(selected.sum())
        assert pixel_count==proposal["selectedPixelCount"]==review["pixelCount"]
        ox,oy=proposal["sourceOriginInTile"]
        x0,y0=max(0,ox),max(0,oy);x1,y1=min(4096,ox+1254),min(4096,oy+1254)
        clipped=selected[y0-oy:y1-oy,x0-ox:x1-ox]
        assert int(clipped.sum())==pixel_count,"Selected existing-source pixels outside formal tile"
        expected=hashlib.sha256(baseline[y0:y1,x0:x1][clipped].tobytes()).hexdigest()
        assert expected==proposal["baselineSelectedPixelsSha256"],"Existing-source reselection baseline changed"
        assert not changed_mask[y0:y1,x0:x1][clipped].any(),"Native selection masks overlap"
        image.paste(raw,(ox,oy),mask_image)
        owner[y0:y1,x0:x1][clipped]=idx
        changed_mask[y0:y1,x0:x1][clipped]=True
        adoption={"proposal":ref(proposal_file),"independentReview":ref(review_file),
            "rootReview":ref(root_file),"ownerIndex":idx,"selectedPixelCount":pixel_count,
            "sameWorldBaselineUnderMaskVerified":True,"type":"existing_registered_native_source_reselection",
            "uniqueNativeSourceIncrement":0,"nativeMask":ref(mask_file)}
        existing.setdefault("additionalNativeSelections",[]).append(adoption)
        new_adoptions.append(adoption)
    arr=np.array(image)
    assert np.array_equal(arr[~changed_mask],baseline[~changed_mask])
    proved=0
    for item in registry:
        assert sha(item["file"])==item["sha256"]
        ox,oy=item["nativeOriginInTile"]
        x0,y0=max(0,ox),max(0,oy)
        x1,y1=min(4096,ox+1254),min(4096,oy+1254)
        mask=owner[y0:y1,x0:x1]==item["ownerIndex"]
        raw=np.array(Image.open(item["file"]).convert("RGB"))
        assert np.array_equal(arr[y0:y1,x0:x1][mask],raw[y0-oy:y1-oy,x0-ox:x1-ox][mask])
        item["sourcePixelCount"]=int(mask.sum()); proved+=int(mask.sum())
    assert proved==16777216 and not (owner==0).any()
    count=len(registry)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    fp=hashlib.sha256(json.dumps([(r["sha256"],r.get("nativeMask",{}).get("sha256"),
        [s["nativeMask"]["sha256"] for s in r.get("additionalNativeSelections",[])]) for r in registry]).encode()).hexdigest()[:16]
    version=f"native-{count}-source-incremental-{stamp}-{fp}"
    cdir=T/"candidate"/version;qdir=T/"qa"/version
    cdir.mkdir(parents=True,exist_ok=False);qdir.mkdir(parents=True,exist_ok=False)
    out=cdir/"candidate.png";own=cdir/"owner-index.png"
    image.save(out);Image.fromarray(owner).save(own)
    assert np.array_equal(np.array(Image.open(out).convert("RGB")),arr)
    assert np.array_equal(np.array(Image.open(own)),owner)
    registry_doc=copy.deepcopy(old_registry)
    registry_doc.update({"sourceCount":count,"sources":registry,"ownerIndex":ref(own),
         "baseCandidate":ref(base_file),"baseRegistry":ref(old_registry_file),
         "newApprovedRepairs":new_adoptions,"incrementalBuild":True,"sourceResampled":False,
         "sourceRecolored":False,"sourceBlended":False,"formalAccepted":False})
    reg=cdir/"source-registry.json";write(reg,registry_doc)
    proof={"candidate":ref(out),"ownerIndex":ref(own),"sourceRegistry":ref(reg),
        "status":"passed_exact_same_world_native_pixels","provedPixels":proved,"nativeSources":count,
        "baseSelectedCoreCount":16,"newRepairPixels":int(changed_mask.sum()),
        "changedRGBPixels":int(np.any(arr!=baseline,axis=2).sum()),"unownedPixels":0,
        "nativePixelScale":1,"savedCandidateAndOwnerIndexDecodedPixelsVerified":True,
        "outsideNewMasksPixelIdenticalToBase":True,"sourceResampled":False,"sourceRecolored":False,
        "sourceBlended":False,"formalAccepted":False}
    proof_file=cdir/"native-pixel-proof.json";write(proof_file,proof)
    north=Image.open(verify(old["actualNorthNeighbor"])).convert("RGB")
    strip=Image.new("RGB",(4096,320))
    strip.paste(north.crop((0,3936,4096,4096)),(0,0));strip.paste(image.crop((0,0,4096,160)),(0,160))
    crops=[];changed=[]
    for c in old["crops"]:
        pic=image.crop(c["location"]["candidateLTRB"]) if "candidateLTRB" in c["location"] else strip.crop(c["location"]["combinedStripLTRB"])
        key=pixel_key(pic)
        prev_file=verify(c)
        assert pixel_key(Image.open(prev_file))==c["pixelKey"]
        entry=copy.deepcopy(c)
        entry["previousManifest"]=ref(prev_manifest)
        entry["previousCrop"]={"file":str(prev_file),"sha256":c["sha256"],"pixelKey":c["pixelKey"],"status":c["status"]}
        if key==c["pixelKey"]:
            entry["reviewReusedByExactPixelIdentity"]=True
            entry["samePixelsAsPreviousCandidateCrop"]=True
            entry["incrementalCropWritten"]=False
        else:
            file=qdir/(c["name"]+".png");pic.save(file)
            entry.update(ref(file))
            entry.update({"pixelKey":key,"status":"pending","actuallyViewed":False,
                          "reviewReusedByExactPixelIdentity":False,"samePixelsAsPreviousCandidateCrop":False,
                          "incrementalCropWritten":True,"priorReviews":[]})
            changed.append(c["name"])
        crops.append(entry)
    counts={s:sum(c["status"]==s for c in crops) for s in sorted(set(c["status"] for c in crops))}
    manifest=copy.deepcopy(old)
    manifest.update({"candidate":ref(out),"sourceRegistry":ref(reg),"pixelProof":ref(proof_file),
        "crops":crops,"reviewStatusCounts":counts,"reusedReviews":40-len(changed),
        "incrementalParentManifest":ref(prev_manifest),"changedCropNames":changed,
        "unchangedCropFilesReused":40-len(changed),"newApprovedRepairs":new_adoptions,
        "appliedPriorReviewOverlays":applied_overlays,
        "actuallyViewedThisBuild":False,"fullTileInternalQAPassed":False,"formalAccepted":False,
        "createdAtUtc":datetime.now(timezone.utc).isoformat()})
    manifest_file=qdir/"manifest.json";write(manifest_file,manifest)
    assembly={"tile":"r08_c04","output":ref(out),"nativeSources":registry,"missingNativePatches":[],
        "qa":crops[:33],"qaManifest":ref(manifest_file),"ownerIndex":ref(own),"pixelProof":proof,
        "sourceResampled":False,"sourceUpscaled":False,"sourceRecolored":False,"sourceBlended":False,
        "baseSelectedCoreCount":16,"nativeSourceCount":count,"repairOverlaysIncluded":True,
        "newApprovedRepairs":new_adoptions,"baseAssembly":ref(base_dir/"assembly.json"),
        "formalAccepted":False}
    write(cdir/"assembly.json",assembly)
    summary={"status":"candidate_and_incremental_audit_ready_not_accepted","candidate":ref(out),
        "candidateDirectory":str(cdir),"qaManifest":str(manifest_file),"cropCount":40,
        "provedPixels":proved,"sourceCount":count,"statusCounts":counts,"changedCrops":changed,
        "reusedCropFiles":40-len(changed),"newRepairPixels":int(changed_mask.sum()),"formalAccepted":False}
    write(qdir/"build-summary.json",summary)
    return summary
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--config")
    a=ap.parse_args()
    cfg=read(a.config) if a.config else {"baseManifest":str(T/"qa"/BASE/"manifest.json"),"patches":[
        {"proposal":str(T/"repair-batches/row2-x3072-dangling-20261013/adoption-proposal.json"),
         "independentReview":str(T/"qa/independent-local-repair-20261013/row2-x3072-dangling-20261013.review.json")},
        {"proposal":str(T/"repair-batches/row3-x1024-step-20261013/adoption-proposal-v2.json"),
         "independentReview":str(T/"qa/independent-local-repair-20261013/row3-x1024-step-20261013.review.json")}]}
    print(json.dumps(build(cfg),ensure_ascii=False))

