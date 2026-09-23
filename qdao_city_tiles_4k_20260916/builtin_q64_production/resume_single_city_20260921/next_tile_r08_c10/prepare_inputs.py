"""Prepare r08_c10 reference-only inputs. No image generation, assembly or shared writes.

Single-source geometry guides are never composited with neighbor rectangles.
Neighbor pixels are separate, SHA-bound reference images so guide paste lines
cannot become invented stone joints. This script cannot submit an image call.
"""
from pathlib import Path
from datetime import datetime, timezone
from io import BytesIO
import hashlib
import json
from PIL import Image, ImageDraw

P = Path(__file__).resolve().parent
SESSION = P.parent
ART = SESSION.parents[1]
REPO = ART.parent
ROW, COLUMN = 8, 10
TILE, CORE, HALO = 4096, 1024, 115
NATIVE, EXTENT = CORE + 2 * HALO, TILE + 2 * HALO
G0 = [(COLUMN-1)*TILE, (ROW-1)*TILE]
GLOBAL_CORE = [*G0, G0[0]+TILE, G0[1]+TILE]
GLOBAL_EXTENDED = [G0[0]-HALO,G0[1]-HALO,G0[0]+TILE+HALO,G0[1]+TILE+HALO]
FIRST = (3, 1)  # r04_c02: bottom-constrained interior seed, away from provisional left edge.


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def record(path, raw=None):
    p = Path(path).resolve()
    return {"file":str(p),"sha256":sha(p.read_bytes() if raw is None else raw)}


def load(path, expected=None):
    p = Path(path).resolve()
    raw = p.read_bytes()
    if expected is not None and sha(raw) != expected:
        raise ValueError(f"Input SHA mismatch: {p}")
    return raw


def read_json(path):
    return json.loads(load(path).decode("utf-8-sig"))


def json_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(value,f,ensure_ascii=False,indent=2)
        f.write("\n")


def image_new(image, path, *, sources, operation, **extra):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("xb") as f:
        image.save(f,format="PNG")
    d = {"createdAtUtc":now(),"output":record(path),"pixels":list(image.size),
         "derivedFrom":sources,"operation":operation,"role":"reference_or_review_only",
         "notNativeGeneratedArtwork":True,"notCandidate":True,"notFormalTile":True,
         "actualModel":None,"actualQuality":None,"generationToolCalled":False,**extra}
    json_new(path.with_suffix(".derived.json"),d)
    return record(path)


def decoded(raw, size=None):
    with Image.open(BytesIO(raw)) as im:
        im.load()
        if size and im.size != size:
            raise ValueError(f"Wrong image size {im.size}; expected {size}")
        return im.convert("RGB")


def scaled_box(box, scale, offset=0):
    return [v*scale-offset for v in box]


def prepare():
    existing = [x.name for x in P.iterdir() if x.name not in ("prepare_inputs.py", "__pycache__")]
    if existing:
        raise RuntimeError(f"Directory already has prepared/work files; audit only, never overwrite: {existing}")
    audit_path = SESSION / "tools/layout-source-audit.json"
    audit_raw = load(audit_path)
    audit = json.loads(audit_raw.decode("utf-8-sig"))
    entry = next(x for x in audit["nextTiles"] if x["tile"] == "r08_c10")
    if entry["globalCoreLTRB"] != GLOBAL_CORE or entry["globalExtendedLTRB"] != GLOBAL_EXTENDED:
        raise ValueError("Coordinate formulas disagree with retained source audit")
    master_box = scaled_box(GLOBAL_EXTENDED,3/32)
    plaza_box = scaled_box(GLOBAL_EXTENDED,3/16,4096)
    if master_box != entry["master6144ExtendedLTRB"] or plaza_box != entry["plaza4096NominalExtendedLTRB"]:
        raise ValueError("Source transforms disagree with retained source audit")
    ledger_path = SESSION / "current-coverage-ledger.json"
    ledger_raw = load(ledger_path)
    ledger = json.loads(ledger_raw.decode("utf-8-sig"))
    by_tile = {x["tile"]:x for x in ledger["tiles"]}
    if by_tile["r08_c10"]["candidateExists"]:
        raise RuntimeError("r08_c10 now has a candidate; do not prepare over concurrent work")
    bottom = by_tile["r09_c10"]["candidate"]
    if bottom["sha256"] != "f5a45f15f69104c6f3dfe9f7a855e71f5d142d896cc78ffadbf12b3a57f813e4":
        raise ValueError("Selected bottom changed; review the new neighbor first")
    left = by_tile["r08_c09"]["candidate"]
    clean = by_tile["r08_c07"]["candidate"]
    sources = {
        "master":audit["canonicalSources"]["wholeCity"],
        "plaza":audit["canonicalSources"]["localPlaza"],
        "bottom":bottom,"leftProvisional":left,"cleanMaterialCandidate":clean,
        "designs":{"file":str(REPO / "designs/gameplay-ui/04-guild.png"),
                   "sha256":"85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6"},
    }
    raws, images = {}, {}
    for name, source in sources.items():
        p = Path(source["file"])
        if not p.is_absolute():
            p = ART / p
        raw = load(p,source["sha256"])
        raws[str(p.resolve())] = raw
        sources[name] = {**source,"file":str(p.resolve())}
        images[name] = decoded(raw, (6144,6144) if name == "master" else (4096,4096) if name != "designs" else None)
    config_path = REPO / "config/image-generation.json"
    config_raw = load(config_path)
    nav_path = REPO / "tianyong_festival_hd_20260910/runtime/navigation.json"
    nav_raw = load(nav_path)
    nav = json.loads(nav_raw.decode("utf-8-sig"))
    mask_path = REPO / "tianyong_festival_hd_20260910/runtime/walkmask_150.png"
    mask_raw = load(mask_path)
    with Image.open(BytesIO(mask_raw)) as im:
        im.load()
        mask = im.convert("L")
    if mask.size != (150,150) or nav["coordinate_canvas"] != 896:
        raise ValueError("Unexpected navigation coordinate sizes")
    for name in ("references","guides","requests","prompts","review","native"):
        (P/name).mkdir(exist_ok=False)
    for name, raw in (("config-snapshot.json",config_raw),("layout-source-audit.snapshot.json",audit_raw)):
        with (P/name).open("xb") as f:
            f.write(raw)
    master_core = [int(v) for v in scaled_box(GLOBAL_CORE,3/32)]
    plaza_core = [int(v) for v in scaled_box(GLOBAL_CORE,3/16,4096)]
    master_crop = images["master"].crop(master_core)
    plaza_crop = images["plaza"].crop(plaza_core)
    image_new(master_crop,P/"references/master-core-native384.png",sources=[sources["master"]],operation="Unresampled authoritative master crop",sourceBoxLTRB=master_core,resampled=False)
    image_new(plaza_crop,P/"references/plaza-core-native768.png",sources=[sources["plaza"]],operation="Unresampled local redraw nominal crop; geometric identity with master unestablished",sourceBoxLTRB=plaza_core,resampled=False)
    master_canvas = images["master"].resize((EXTENT,EXTENT),Image.Resampling.BICUBIC,box=master_box)
    plaza_canvas = images["plaza"].resize((EXTENT,EXTENT),Image.Resampling.BICUBIC,box=plaza_box)
    image_new(master_crop.resize((768,768),Image.Resampling.BICUBIC),P/"review/master-core-layout-review768.png",sources=[sources["master"]],operation="Reference-only 2x enlargement, not final detail",sourceBoxLTRB=master_core,resampled=True)
    # Review overlay is kept separate and never inserted into imagegen inputs.
    overlay = master_crop.resize((768,768),Image.Resampling.BICUBIC).convert("RGBA")
    draw = ImageDraw.Draw(overlay)
    nav_box = scaled_box(GLOBAL_CORE,896/65536)
    overlay_items = []
    for group,color in (("regions",(20,170,70,255)),("obstacles",(225,35,45,255))):
        for ident,points in nav[group].items():
            if max(x[0] for x in points) < nav_box[0] or min(x[0] for x in points) > nav_box[2] or max(x[1] for x in points) < nav_box[1] or min(x[1] for x in points) > nav_box[3]:
                continue
            local=[((x-nav_box[0])*768/(nav_box[2]-nav_box[0]),(y-nav_box[1])*768/(nav_box[3]-nav_box[1])) for x,y in points]
            draw.line(local+[local[0]],fill=color,width=3)
            overlay_items.append({"group":group,"id":ident,"pointsOn896Canvas":points})
    image_new(overlay.convert("RGB"),P/"review/master-navigation-polygons-review-only.png",sources=[sources["master"],record(nav_path,nav_raw)],operation="Diagnostic overlay only; never a generation input",globalCoreLTRB=GLOBAL_CORE,reviewPolygons=overlay_items,resampled=True)
    # A crop from an already reviewed clean candidate supplies real native-pixel material.
    # No old noisy guide texture or reference composition is made authoritative.
    material_box=[1152,1280,1920,2048]
    material_ref=image_new(images["cleanMaterialCandidate"].crop(material_box),P/"references/clean-stone-native768.png",sources=[sources["cleanMaterialCandidate"]],operation="Unresampled original-pixel material reference crop only",sourceBoxLTRB=material_box,resampled=False,geometryImportAllowed=False)
    first_r,first_c=FIRST
    first_box=[first_c*CORE,first_r*CORE,first_c*CORE+NATIVE,first_r*CORE+NATIVE]
    first_master_ref=image_new(master_canvas.crop(first_box),P/"guides/r04_c02.master-layout-only.png",sources=[sources["master"]],operation="Pure single-source master layout resampling then crop; no compositing, no pasted neighbor",sourceMasterExtendedLTRB=master_box,extendedCanvasCropLTRB=first_box,resampled=True,artificialPasteBoundaries=[])
    first_plaza_ref=image_new(plaza_canvas.crop(first_box),P/"guides/r04_c02.plaza-layout-review-only.png",sources=[sources["plaza"]],operation="Pure single-source local redraw layout resampling then crop; alternative for layout review, not approved geometry",sourcePlazaExtendedLTRB=plaza_box,extendedCanvasCropLTRB=first_box,resampled=True,artificialPasteBoundaries=[])
    # This seed's x span lies fully inside the selected bottom tile. Only y>=0
    # in that tile is known: exactly 115px of actual bottom-neighbor halo exists.
    bottom_x=first_c*CORE-HALO
    bottom_box=[bottom_x,0,bottom_x+NATIVE,512]
    bottom_ref=image_new(images["bottom"].crop(bottom_box),P/"references/r04_c02.bottom-neighbor-native-context.png",sources=[sources["bottom"]],operation="Unresampled separate bottom-neighbor context; never pasted into guide",sourceBoxLTRB=bottom_box,resampled=False,targetPatchBoundaryY=1139,targetPatchKnownBottomHaloLTRB=[0,1139,1254,1254],referenceOverlapBoxLTRB=[0,0,1254,115],notAll230pxAvailable=True)
    left_ref=image_new(images["leftProvisional"].crop((3584,0,4096,4096)).resize((128,1024),Image.Resampling.LANCZOS),P/"review/left-provisional-edge-preview.png",sources=[sources["leftProvisional"]],operation="Preview of provisional left neighbor; not a generation input or final boundary constraint",sourceBoxLTRB=[3584,0,4096,4096],resampled=True,provisional=True)
    patches=[]
    for r in range(4):
        for c in range(4):
            ident=f"r{r+1:02}_c{c+1:02}"
            global_patch=[G0[0]+c*CORE-HALO,G0[1]+r*CORE-HALO,G0[0]+(c+1)*CORE+HALO,G0[1]+(r+1)*CORE+HALO]
            patches.append({"id":ident,"row":r,"column":c,"nativePixels":[NATIVE,NATIVE],
                "coreCropLTRB":[HALO,HALO,HALO+CORE,HALO+CORE],"pasteCoreXY":[c*CORE,r*CORE],
                "globalNativeContextLTRB":global_patch,"masterSourceContextLTRB":scaled_box(global_patch,3/32),
                "plazaNominalContextLTRB":scaled_box(global_patch,3/16,4096),
                "internalOverlapPixels":230,"plannedOutput":f"native/{ident}.png",
                "neighborContextPolicy":"Separate explicit original-pixel reference inputs; never paste rectangles into geometry guide",
                "leftExternalConstraint":"provisional_pending_r08_c09_repair" if c==0 else "not_on_external_left_edge",
                "bottomExternalConstraint":"selected_r09_c10_external_v8_known115px_inside_neighbor" if r==3 else "not_on_external_bottom_edge",
                "status":"first_patch_draft_prepared_layout_review_required" if (r,c)==FIRST else "plan_only_not_generated"})
    prompt="""Use case: precise-object-edit. DRAFT FOR REVIEW ONLY. Produce exactly one opaque square native 1254x1254 terrain crop for patch r04_c02 of Tianyong festival city tile r08_c10. Image 1 is the ORIGINAL WHOLE-CITY MASTER layout crop at the exact target camera, scale, orientation and global coordinates. It is enlarged for layout reference only, never final pixels. Keep its actual road/slab/stone-carving geometry, curves, structural joint locations and open walkable surface. Repaint all surfaces as crisp newly generated native hand-painted detail.
Image 2 is ONLY the clean original-pixel stone rendering/material example: calm warm ivory, broad sparse shading, restrained rounded bevels and crisp clean joints. Do not copy its composition, slab count, lines, gold inlay, stair-like forms or ornaments into image 1. Image 3 is the primary user-confirmed project painting/finish reference: clean bright rounded Daoist Q/chibi style; do not import its UI, lettering, characters or props. Image 4 is a SEPARATE exact native strip of selected bottom neighbor r09_c10 external-v8. Its top 115 rows align with the target image's bottom 115 rows, starting at target y=1139. Its existing crossing positions and material are comparison constraints; compatibility with this target crop is pending regional layout review. Do not copy the bottom of that reference as a new step.
The geometry guide contains NO pasted-neighbor rectangles and NO grid. Reference-image edges and algorithmic coordinates x=115, x=1024, x=1139, y=115, y=1024, y=1139 are not stone divisions. Never invent a horizontal or vertical stone joint to explain a rectangular crop boundary. Preserve actual structural lines visible in the original master; never infer a joint from a color patch or old sampling discontinuity. If bottom-neighbor structure conflicts with the original master, do not improvise a new edge: this draft must be resolved by regional layout review before submission.
Keep quiet smooth stone faces, original traversable areas and gentle sculpted depth. No flakes, cloudy blotches, marble veins, cracks, speckles, gritty grain, white frosting, thick halos, plastic shine or blur. Keep blank ground blank. No new ornament, object, building, stairs, lantern, vegetation, text, UI, border, collage or watermark. Output the exact image-1 crop, not the whole city, not the material reference. Native detail must be newly painted, never an enlarged or sharpened old guide."""
    prompt_path=P/"prompts/r04_c02.draft.prompt.txt"
    with prompt_path.open("x",encoding="utf-8",newline="\n") as f:f.write(prompt+"\n")
    draft={"prompt":prompt,"referenced_image_paths":[first_master_ref["file"],material_ref["file"],sources["designs"]["file"],bottom_ref["file"]]}
    json_new(P/"requests/r04_c02.draft.request.json",draft)
    inputs=[{"index":i+1,**record(Path(p)),"role":role} for i,(p,role) in enumerate(zip(draft["referenced_image_paths"],["original master geometry guide only","native clean stone material only","primary confirmed designs style only","separate selected native bottom context only"]))]
    layout={"schemaVersion":1,"preparedAtUtc":now(),"tile":"r08_c10","globalCoreLTRB":GLOBAL_CORE,
        "globalExtendedLTRB":GLOBAL_EXTENDED,"worldRect":entry["worldRect"],"masterCoreLTRB":master_core,
        "masterExtendedLTRB":master_box,"plazaNominalCoreLTRB":plaza_core,"plazaNominalExtendedLTRB":plaza_box,
        "navigation150FractionalBoxLTRB":scaled_box(GLOBAL_CORE,150/65536),"navigation896BoxLTRB":nav_box,
        "sourceAudit":record(audit_path,audit_raw),"ledgerObserved":record(ledger_path,ledger_raw),"sources":sources,
        "navigation":{**record(nav_path,nav_raw),"mask":record(mask_path,mask_raw),"polygonsIntersectingTileBounds":overlay_items},
        "geometryAuthority":"original 6144 master; local redraw supplied for comparison only until reconciliation",
        "masterToPlazaGeometryIdentityEstablished":False,"navigationArtApprovalEstablished":False,
        "bottomNeighbor":"selected external-v8; immutable during this preparation",
        "leftNeighbor":"provisional under active repair; never final or fixed",
        "guidePixelsMayEnterFinalArtwork":False,"nativeGenerationCount":0,"formalAccepted":False}
    json_new(P/"layout-record.json",layout)
    plan={"schemaVersion":1,"preparedAtUtc":now(),"tile":"r08_c10","appearance":"tianyong_festival",
        "globalCoreLTRB":GLOBAL_CORE,"targetPixels":[4096,4096],"nativeGrid":[4,4],"nativePixels":[1254,1254],
        "core":1024,"halo":115,"internalAdjacentOverlap":230,"extendedPixels":[4326,4326],
        "extendedFinalCoreCropLTRB":[115,115,4211,4211],"patches":patches,"firstPatch":"r04_c02",
        "configSnapshot":json.loads(config_raw.decode("utf-8-sig")),"actualModel":None,"actualQuality":None,
        "submittedParameters":{"model":None,"quality":None},"toolCallMade":False,"actualRequestSubmitted":None,
        "generationReady":False,"generationReadinessReason":"root must inspect master/plaza geometry and bottom edge; left stays provisional",
        "draftRequest":record(P/"requests/r04_c02.draft.request.json"),"draftInputs":inputs,
        "layoutRecord":record(P/"layout-record.json"),"guideCompositingAllowed":False,
        "firstPatchAlternatePlazaForReview":first_plaza_ref,"sourceArtUpscaledIntoFinal":False,
        "finalCandidateCount":0,"formalAccepted":False,"runtimeAccepted":False,
        "requiredBeforeActualGeneration":["inspect chosen regional layout and required native references",
            "recheck actual builtin tool capability","save per-call preflight/config/request/reference SHA",
            "keep undisclosed actual model and quality null","record actual receipt and observed completion time"]}
    json_new(P/"plan.json",plan)
    # Validate arithmetic/overlap plans, without claiming visual seam acceptance.
    assert len(patches)==16 and len({tuple(x['pasteCoreXY']) for x in patches})==16
    for r in range(4):
        for c in range(4):
            a=patches[r*4+c]['globalNativeContextLTRB']
            if c<3:assert a[2]-patches[r*4+c+1]['globalNativeContextLTRB'][0]==230
            if r<3:assert a[3]-patches[(r+1)*4+c]['globalNativeContextLTRB'][1]==230
    for file,raw in raws.items():
        if Path(file).read_bytes()!=raw:raise RuntimeError(f"Source changed during preparation: {file}")
    if load(ledger_path)!=ledger_raw:raise RuntimeError("Shared ledger changed during preparation; review observation before use")
    json_new(P/"preparation-validation.json",{"checkedAtUtc":now(),"plan":record(P/"plan.json"),
        "coordinateArithmeticPassed":True,"internalOverlapRelationsChecked":24,"actualFirstGuidePixels":[1254,1254],
        "guidePastedRectangles":0,"sourceFilesUnchanged":True,"sharedJSONWritten":False,"toolCalls":0,
        "notGeometryArtApproval":True,"allOutputImagesAreReferences":True})
    print(json.dumps({"directory":str(P),"plan":record(P/"plan.json"),"firstPatch":"r04_c02",
        "nativeGenerations":0,"layoutReviewRequired":True,"bottomKnownHaloPixels":115}))


if __name__=="__main__":
    prepare()
