from pathlib import Path
import sys,json,hashlib
from PIL import Image
REPO=Path(__file__).resolve().parents[2]; PACK=REPO/"qdao_chibi_game_pack_v4"
sys.path.insert(0,str(PACK))
from build_pack import inspect_png
hero=Image.open(PACK/"hero-transparent_1024.png").convert("RGBA")
city=Image.open(PACK/"main-city_2560x1080.png").convert("RGBA")
bbox=hero.getchannel("A").getbbox(); anchor=[(bbox[0]+bbox[2])/2,bbox[3]]
scale=160/1024; feet=[1240,680]; xy=[round(feet[0]-anchor[0]*scale),round(feet[1]-anchor[1]*scale)]
city.alpha_composite(hero.resize((160,160),Image.Resampling.LANCZOS),xy)
city.convert("RGB").save(PACK/"preview-main-city_2560x1080.png")
placements=json.loads((PACK/"placements.json").read_text(encoding="utf-8-sig"))
placements["actors"][0].update(source_feet_anchor=anchor,feet_at=feet,top_left=xy)
(PACK/"placements.json").write_text(json.dumps(placements,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
manifest=json.loads((PACK/"manifest.json").read_text(encoding="utf-8-sig")); manifest["updated"]="2026-09-07"; manifest["refresh"]="GPT Image 2 v7"
manifest["files"]=[inspect_png(PACK/p) for p in ["main-city_2560x1080.png","hero-transparent_1024.png","preview-main-city_2560x1080.png"]]
manifest["generation"].update(model="gpt-image-2",quality_parameter_exposed=False,provenance="../qdao_gpt_image2_refresh_v7/README.md")
manifest["scene_export"].update(source="../qdao_gpt_image2_refresh_v7/scenes/main-city.raw.png",source_size=list(Image.open(REPO/"qdao_gpt_image2_refresh_v7/scenes/main-city.raw.png").size))
(PACK/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("New city + new hero preview and manifest rebuilt.")
