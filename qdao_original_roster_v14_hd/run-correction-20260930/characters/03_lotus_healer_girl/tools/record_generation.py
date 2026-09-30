import argparse, hashlib, json, shutil, struct, sys
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT.parents[3]/"config"/"image-generation.json"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def contained(p):
    p=Path(p).resolve()
    if not p.is_relative_to(ROOT): raise ValueError("output outside role directory")
    return p
def write_json(path,data):
    path=contained(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def record(args):
    job=json.loads(contained(args.job).read_text(encoding="utf-8-sig"))
    source=Path(args.source).resolve()
    dest=contained(ROOT/job["output"])
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists(): raise ValueError("will not overwrite image")
    shutil.copy2(source,dest)
    with Image.open(dest) as im:
        dims=list(im.size); fmt=im.format; mode=im.mode
        alpha=im.getchannel("A") if "A" in im.getbands() else None
        extrema=alpha.getextrema() if alpha else None
        bounds=alpha.point(lambda a:255 if a>8 else 0).getbbox() if alpha else None
        text_meta={k:str(v) for k,v in im.info.items() if isinstance(v,(str,int,float))}
    meta={"schemaVersion":1,"file":job["output"],"sha256":sha(dest),
      "generatedAt":datetime.now(timezone.utc).isoformat(),
      "generatedAtMeaning":"local receipt time after tool completed; exact server generation timestamp not exposed",
      "native":{"width":dims[0],"height":dims[1],"format":fmt,"mode":mode},
      "tool":"image_gen.imagegen","route":"builtin",
      "configSnapshot":json.loads(CONFIG.read_text(encoding="utf-8-sig")),
      "submittedParameters":{"model":None,"quality":None,"promptFile":job["prompt"],
          "referenced_image_paths":[r["path"] for r in job["references"]],"transparent_background":True},
      "actualModel":None,"actualQuality":None,
      "unverifiedReason":"宿主管理，工具未披露模型或质量；提示词目标不能代替真实参数。",
      "evidence":{"hostOutputPath":str(source),"copiedShaMatches":sha(source)==sha(dest),
          "toolOutputHint":args.hint,"pngTextMetadata":text_meta},
      "references":[dict(r,sha256=sha(r["path"])) for r in job["references"]],
      "prompt":job["prompt"],"promptSha256":sha(ROOT/job["prompt"]),
      "alphaExtrema":extrema,"alphaGt8Bounds":bounds,
      "status":job.get("status","unreviewed"),"review":job.get("review",{}),
      "officialVerification":{"verifiedOn":"2026-09-30","modelPage":"https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst","finding":"Official model page describes most capable image model; lists max quality. Builtin selector unavailable; shared configuration unchanged."}}
    write_json(Path(str(dest)+".generation.json"),meta)
    print(json.dumps({"file":str(dest),"native":dims,"mode":mode,"sha256":meta["sha256"],"bounds":bounds},ensure_ascii=False))
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("job");p.add_argument("source");p.add_argument("--hint",default="Builtin generated image result supplied the host output path.")
    record(p.parse_args())

