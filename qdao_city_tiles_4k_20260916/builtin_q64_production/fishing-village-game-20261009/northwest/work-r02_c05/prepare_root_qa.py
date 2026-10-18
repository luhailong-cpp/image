from pathlib import Path
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest');W=B/'work-r02_c05'
s=(B/'qa_native_overlap.py').read_text().replace("B=Path(__file__).resolve().parent","B=Path(__file__).resolve().parent.parent")
s=s.replace("B/'native'/(name+'.png')","w/'native'/(name+'.png')")
s=s.replace("w/'guides'/(name+'.authoritative.png')","Path(json.loads((w/'receipts'/(name+'.request.json')).read_text())['referenced_image_paths'][0])")
(W/'qa_native_local.py').write_text(s)

