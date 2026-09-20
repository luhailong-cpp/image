from pathlib import Path
from datetime import datetime, timezone
import argparse, json, hashlib, shutil
import numpy as np
from PIL import Image
TOP=Path("E:/work/image/qdao_city_tiles_4k_20260916")
ROOT=Path(__file__).resolve().parent
VARIANT=ROOT.parent.name
TILE=ROOT.name
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def savej(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
    mode=argparse.ArgumentParser()
    mode.add_argument("mode",choices=["direct","patches"])
    args=mode.parse_args()
    gridfile=TOP/"q64_production_plans"/(VARIANT+".json")
    prod=json.loads(gridfile.read_text(encoding="utf-8-sig"))
    entry=next(t for t in prod["tiles"] if t["id"]==TILE)
    ref=TOP/"builtin_q64_all_city_references"/"lanxian_day"/"map-native-layout-reference.png"
    for name in ["direct-attempt","guides","prompts","native","output","qa"]:
        (ROOT/name).mkdir(parents=True,exist_ok=True)
    x,y,w,h=entry["finalPixelRect"]
    im=Image.open(ref).convert("RGB")
    sx,sy=im.width/65536,im.height/65536
    box=[x*sx,y*sy,(x+w)*sx,(y+h)*sy]
    expanded=[(x-115)*sx,(y-115)*sy,(x+w+115)*sx,(y+h+115)*sy]
    plan={
        "schemaVersion":1,"status":"direct_native_4096_attempt_prepared",
        "route":"builtin_image_gen","userSelectedModel":"GPT Image 2.0 (host builtin)",
        "requestedQuality":"highest available host quality, no explicit selector",
        "backendModelVerified":False,"backendSelectorAvailable":False,
        "wholeCityPixels":[65536,65536],"wholeCityGrid":{"rows":16,"columns":16},
        "deliveryTilePixels":[4096,4096],"worldRect":prod["worldRect"],
        "sampleTile":{"id":TILE,"row":entry["row"],"column":entry["column"],"worldRect":entry["worldRect"]},
        "samplePixelRectInWholeCity":[x,y,x+w,y+h],
        "samplePixelRectConvention":"left,top,right,bottom; endpoint-exclusive",
        "productionPlan":str(gridfile),"productionPlanSha256":sha(gridfile),
        "layoutSource":str(ref),"layoutSourceSha256":sha(ref),"layoutSourcePixels":list(im.size),
        "sampleSourceCrop":box,"extendedLayoutSourceBox":expanded,
        "nativeGrid":{"rows":4,"columns":4},"rows":4,"columns":4,"core":1024,"halo":115,
        "nativeTarget":[1254,1254],"assembledBeforeOuterCrop":[4326,4326],
        "guidePreparation":{"status":"direct_attempt_not_yet_returned"},
        "externalAdjacent4kSeamsAccepted":False,"runtimePublished":False,
        "finalArtUpscaled":False,"formalTileAcceptance":False,
    }
    if args.mode=="direct":
        g=im.transform((4326,4326),Image.Transform.EXTENT,expanded,resample=Image.Resampling.BICUBIC)
        left=Image.open(ROOT.parent/"r08_c06/output/extended-context-v4.png").convert("RGB")
        g.paste(left.crop((4096,0,4326,4326)),(0,0))
        g=g.crop((115,115,4211,4211)).resize((1254,1254),Image.Resampling.BICUBIC)
        gp=ROOT/"direct-attempt"/"layout-only.png"; g.save(gp)
        g.save(ROOT/"direct-attempt"/"layout-input.jpg",quality=65)
        plan["directAttemptGuide"]={"file":"direct-attempt/layout-only.png","sha256":sha(gp),"role":"resampled geometric reference only"}
    else:
        old=json.loads((ROOT/"plan.json").read_text(encoding="utf-8-sig"))
        plan["directAttemptGuide"]=old["directAttemptGuide"]
        motherfile=ROOT/"direct-attempt"/"native.png"
        mother=Image.open(motherfile).convert("RGB")
        canvas=im.transform((4326,4326),Image.Transform.EXTENT,expanded,resample=Image.Resampling.BICUBIC)
        canvas.paste(mother.resize((4096,4096),Image.Resampling.BICUBIC),(115,115))
        left=Image.open(ROOT.parent/"r08_c06/output/extended-context-v4.png").convert("RGB")
        canvas.paste(left.crop((4096,0,4326,4326)),(0,0))
        canvas.save(ROOT/"guides"/"layout-canvas-only.png")
        patches=[]; arrays={}
        for r in range(4):
            for c in range(4):
                ident=f"r{r+1:02d}_c{c+1:02d}"
                rect=[c*1024,r*1024,c*1024+1254,r*1024+1254]
                g=canvas.crop(rect); p=ROOT/"guides"/(ident+".layout-only.png");g.save(p)
                arrays[(r,c)]=np.asarray(g)
                patches.append({"id":ident,"row":r,"column":c,"guide":str(p),"guideSha256":sha(p),"fullCanvasBox":rect,"guideOnly":True})
        checked=0
        for r in range(4):
            for c in range(4):
                if c<3:
                    assert np.array_equal(arrays[(r,c)][:,-230:],arrays[(r,c+1)][:,:230]);checked+=1
                if r<3:
                    assert np.array_equal(arrays[(r,c)][-230:],arrays[(r+1,c)][:230]);checked+=1
        plan["status"]="sixteen_native_detail_patches_required"
        plan["directAttemptActualPixels"]=list(mother.size)
        plan["directAttemptRole"]="regional layout/detail mother only; returned below4096; not final art"
        plan["guidePreparation"]={"status":"ready_unified_style_reference","guideCount":16,
            "motherSource":str(motherfile),"motherSha256":sha(motherfile),"motherPixels":list(mother.size),
            "canvasPixels":[4326,4326],"sharedOverlapChecks":checked,"allSharedOverlapPixelsIdentical":True,
            "method":"Center4096 layout only resampled from generated exact-tile mother; outside115 context from exact-coordinate whole-city layout source. Final art must be newly generated; no guide pixels used.",
            "finalArtResampling":False}
        plan["patches"]=patches
    plan["sharedGeometrySource"]="lanxian_day whole-city layout; style variants share this regional footprint"
    plan["leftNeighborBoundary"]={"tile":"r08_c06","file":str(ROOT.parent/"r08_c06/output/extended-context-v4.png"),"sha256":sha(ROOT.parent/"r08_c06/output/extended-context-v4.png"),"pixels":230,"guideOnly":True}
    plan["crossAppearancePixelAlignmentAccepted"]=False
    savej(ROOT/"plan.json",plan)
    assembly=(TOP/"builtin_q64_r10_c07"/"assemble_builtin.py").read_text(encoding="utf-8")
    assembly=assembly.replace('HELPERS = ROOT.parents[1] / "tianyong_festival_hd_20260910" / "seam_helpers.py"',
        'HELPERS = Path("E:/work/image/tianyong_festival_hd_20260910/seam_helpers.py")')
    assembly=assembly.replace("Tianyong r10_c07",VARIANT+" "+TILE)
    assembly=assembly.replace("tianyong_r10_c07_q64_4k_candidate.png",VARIANT+"_"+TILE+"_q64_4k_candidate.png")
    assembly=assembly.replace("Tianyong festival r10_c07",VARIANT+" "+TILE)
    assembly=assembly.replace('"tree_upper_left_100pct"','"detail_upper_left_100pct"').replace('"garden_lower_left_100pct"','"detail_lower_left_100pct"').replace('"garden_stairs_lower_right_100pct"','"detail_lower_right_100pct"')
    assembly=assembly.replace("    save_png(image, ART)\n", '    save_png(image, ART)\n    save_png(Image.fromarray(combined), OUTPUT / "extended-context.png")\n')
    assembly=assembly.replace('        "output": {"file": relative(ART)', '        "extendedContext": {"file": "output/extended-context.png", "pixels": [4326, 4326], "sha256": sha256(OUTPUT / "extended-context.png")},\n        "externalAdjacent4kSeamsAccepted": False,\n        "output": {"file": relative(ART)')
    assembly=assembly.replace('def validate_saved(manifest: dict, entries: list[dict]) -> dict:\n',
        'def validate_saved(manifest: dict, entries: list[dict]) -> dict:\n    extended = ROOT / manifest["extendedContext"]["file"]\n    if sha256(extended) != manifest["extendedContext"]["sha256"]:\n        raise ValueError("Extended-context hash differs")\n    with Image.open(extended) as ext, Image.open(ART) as art:\n        if ext.size != (4326, 4326) or not np.array_equal(np.asarray(ext.crop((115,115,4211,4211))), np.asarray(art)):\n            raise ValueError("Extended-context crop differs from candidate")\n')
    (ROOT/"assemble_builtin.py").write_text(assembly,encoding="utf-8")
    print(json.dumps({"root":str(ROOT),"tile":TILE,"sourceBox":box,"worldRect":entry["worldRect"],"mode":args.mode},ensure_ascii=False))
if __name__=="__main__":main()
