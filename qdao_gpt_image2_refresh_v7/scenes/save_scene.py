"""Save already generated scenes and same-size compatibility exports; no generation calls."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess
from io import BytesIO
from PIL import Image, ImageOps
REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/"qdao_gpt_image2_refresh_v7/scenes"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--id",required=True); ap.add_argument("--generated",required=True); ap.add_argument("--target",action="append",default=[]); args=ap.parse_args()
    raw=ROOT/(args.id+".raw.png"); shutil.copy2(args.generated,raw)
    with Image.open(raw) as im:
        im.load(); native=list(im.size); source_mode=im.mode; rows=[]
        for target in args.target:
            path=REPO/target
            baseline=subprocess.check_output(["git","show","HEAD:"+target],cwd=REPO)
            with Image.open(BytesIO(baseline)) as old: size=old.size; mode=old.mode
            # Existing canvas sizes are an asset contract, the exact native result stays above.
            out=ImageOps.fit(im.convert(mode),size,method=Image.Resampling.LANCZOS)
            out.save(path,optimize=True)
            rows.append({"path":target,"size":list(size),"mode":mode,"old_sha256":hashlib.sha256(baseline).hexdigest(),"new_sha256":sha(path),"source":raw.relative_to(REPO).as_posix(),"method":"proportional centered cover from newly image-generated source"})
    data={"generator":"built-in image_gen","model":"gpt-image-2","model_evidence":"OpenAI built-in image generation documentation; https://learn.chatgpt.com/docs/image-generation","quality_parameter_exposed":False,"native_size":native,"native_mode":source_mode,"source_cache_file":Path(args.generated).name,"source_sha256":sha(raw),"prompt":args.id+".prompt.txt","files":rows}
    (ROOT/(args.id+".exports.json")).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"id":args.id,"native_size":native,"exports":len(rows)}))
if __name__=="__main__": main()
