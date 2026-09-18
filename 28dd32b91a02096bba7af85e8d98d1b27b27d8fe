from pathlib import Path
TOP=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
src=(TOP/'lanxian_day/r08_c06/prepare_layout.py').read_text(encoding='utf-8-sig')
src=src.replace('ref=TOP/"builtin_q64_all_city_references"/VARIANT/"map-native-layout-reference.png"','ref=TOP/"builtin_q64_all_city_references"/"lanxian_day"/"map-native-layout-reference.png"')
src=src.replace('g=im.transform((1254,1254),Image.Transform.EXTENT,box,resample=Image.Resampling.BICUBIC)','g=im.transform((4326,4326),Image.Transform.EXTENT,expanded,resample=Image.Resampling.BICUBIC)\n        left=Image.open(ROOT.parent/"r08_c06/output/extended-context-v4.png").convert("RGB")\n        g.paste(left.crop((4096,0,4326,4326)),(0,0))\n        g=g.crop((115,115,4211,4211)).resize((1254,1254),Image.Resampling.BICUBIC)')
src=src.replace('canvas.save(ROOT/"guides"/"layout-canvas-only.png")','left=Image.open(ROOT.parent/"r08_c06/output/extended-context-v4.png").convert("RGB")\n        canvas.paste(left.crop((4096,0,4326,4326)),(0,0))\n        canvas.save(ROOT/"guides"/"layout-canvas-only.png")')
src=src.replace('savej(ROOT/"plan.json",plan)','plan["sharedGeometrySource"]="lanxian_day whole-city layout; style variants share this regional footprint"\n    plan["leftNeighborBoundary"]={"tile":"r08_c06","file":str(ROOT.parent/"r08_c06/output/extended-context-v4.png"),"sha256":sha(ROOT.parent/"r08_c06/output/extended-context-v4.png"),"pixels":230,"guideOnly":True}\n    plan["crossAppearancePixelAlignmentAccepted"]=False\n    savej(ROOT/"plan.json",plan)')
for variant in ['lanxian_day','lanxian_spring']:
 p=TOP/variant/'r08_c07';p.mkdir(exist_ok=True)
 (p/'prepare_layout.py').write_text(src,encoding='utf8')
print('prepared scripts')

