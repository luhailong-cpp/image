#!/usr/bin/env python3
"""Normalize the one official image_gen login plate; all processing stays in image."""
import hashlib,json,shutil,sys
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parent
RAW=ROOT/"login_background.raw.png"
TARGET=ROOT/"login_background.png"
REFERENCE=ROOT/"login_background.reference.png"
CACHE=Path("C:/Users/luyua/.codex/generated_images/01a0818d-8345-75e1-879d-17c1ef3db666/exec-ad2e2a0e-7a7c-47f2-9eec-5829beba6afd.png")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if not RAW.exists():shutil.copyfile(CACHE,RAW)
with Image.open(RAW) as source:
    source.load()
    native_size=list(source.size);native_mode=source.mode
    sw,sh=source.size;ratio=2560/1080
    if sw/sh>ratio:
        cw=sh*ratio;crop=[(sw-cw)/2,0,(sw+cw)/2,sh]
    else:
        ch=sw/ratio;crop=[0,(sh-ch)/2,sw,(sh+ch)/2]
    final=ImageOps.fit(source.convert("RGB"),(2560,1080),method=Image.Resampling.LANCZOS,centering=(.5,.5))
    final.save(TARGET,optimize=True)
record={
    "schema":"qdao.login-clean-background.v1",
    "recorded_at":datetime.now(timezone.utc).isoformat(),
    "asset":"login_background.png",
    "map_mode":"baked_scene_mode",
    "visual_model":"baked_raster",
    "runtime_object_model":"none; separate client hero/pet sprites are overlaid by the game",
    "generator":"official built-in image_gen",
    "requested_model":"gpt-image-2",
    "model_parameter_exposed":False,
    "quality_parameter_exposed":False,
    "external_api_used":False,
    "successful_generated_image_count":1,
    "reference":{"file":REFERENCE.name,"size":[2560,1080],"sha256":sha(REFERENCE)},
    "reference_transport":"Conversation-visible 1280x540 in-memory preview; num_last_images_to_include=1",
    "transport_issue":"view_image and referenced_image_paths could not read the local reference because Windows sandbox helper failed with apply deny-read ACLs. Approved read-only exec emitted the preview; the subsequent official built-in image_gen call succeeded.",
    "failed_before_generation":{"mechanism":"referenced_image_paths","reason":"apply deny-read ACLs","image_produced":False},
    "raw":{"file":RAW.name,"cache_file":str(CACHE),"size":native_size,"mode":native_mode,"sha256":sha(RAW)},
    "output":{"file":TARGET.name,"size":[2560,1080],"mode":"RGB","sha256":sha(TARGET),
              "method":"Pillow ImageOps.fit proportional centered cover with LANCZOS",
              "source_crop_box_xyxy":crop,"native_2560x1080_generation":False},
    "prompt":"login_background.prompt.txt",
    "visual_review":{
        "completed":True,"no_people_or_pets":True,"no_text_or_ui":True,
        "left_lotus_pond_and_jade_sanctuary_style_preserved":True,
        "large_clear_lower_right_stone_terrace":True,
        "standing_zones_normalized":[[.56,.88],[.76,.86]],
        "standing_zones_clear_of_roofs_water_stairs_and_props":True,
        "notes":"Scene visually inspected from the actual official tool output. Decorative distant bird retained in the sky; no foreground animal or pet. This is a menu environment plate, not a new playable map/collision delivery."},
    "engine_validation":"Pending root task native client composition; this record claims source/output image checks only."
}
(ROOT/"login_background.generation.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"native_size":native_size,"export":[2560,1080],"raw_sha256":sha(RAW),"export_sha256":sha(TARGET)}))
