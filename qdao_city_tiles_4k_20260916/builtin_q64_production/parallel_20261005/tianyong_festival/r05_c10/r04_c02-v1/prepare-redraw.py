from pathlib import Path
import shutil,json,hashlib,datetime
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10/r04_c02-v1");R=D/'rejected-composition-v1';R.mkdir(exist_ok=True)
host=Path(r"C:/Users/luyua/.codex/generated_images/01a11b05-7488-7d11-bfe3-c3b64c8f7651/exec-561a8bc2-2ac0-4264-ad3a-b1592bfca3e0.png");shutil.copy2(host,R/'native.png')
ref=lambda p:{"file":str(p),"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest()}
req=json.loads((D/'request.json').read_text(encoding='utf-8')); prep=json.loads((D/'preparation.json').read_text(encoding='utf-8'))
(R/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'record.json').write_text(json.dumps({"status":"rejected-never-used","reason":"Output transplanted adjacent r06 reference layout and moved known bottom leaves and right stone joints rather than preserving target coordinates.","output":ref(R/'native.png'),"hostOutput":ref(host),"actualReturnedModel":None,"actualReturnedQuality":None,"configTarget":req['configSnapshot'],"references":prep['references']},ensure_ascii=False,indent=2),encoding='utf-8')
req['payload']['referenced_image_paths'][1]=str(D.parent/'r04_c03-v1/final-v1/joined.png')
req['payload']['prompt']+="\nStrict pixel-coordinate constraints: the right known strip has horizontal stone boundaries at y approximately350,620,960. The bottom strip has a pale wall at x50..180 and broad bush leaves at x150..400 in the bottom125 pixels; these must stay at the BOTTOM. Do not move that known lower-left foliage to the top or insert round rail caps copied from another image. Fill missing central-left content using the layout guide: one bush around x0..400,y450..1030, a narrow ivory wall continuing vertically near x80, cropped tan planter only where shown. Image4 is the exact single target to extend. Do not reproduce any entire reference image."
(D/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8');(D/'prompt.txt').write_text(req['payload']['prompt'],encoding='utf-8')
prep['references']=[ref(p) for p in req['payload']['referenced_image_paths']];(D/'preparation.json').write_text(json.dumps(prep,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(req['payload']))

