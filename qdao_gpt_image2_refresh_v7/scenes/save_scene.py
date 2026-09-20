"""Save already generated scenes and same-size compatibility exports; no generation calls."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess
from io import BytesIO
from PIL import Image, ImageOps
REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/"qdao_gpt_image2_refresh_v7/scenes"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def generation_metadata(receipt):
    evidence = json.loads(receipt.read_text(encoding='utf-8-sig')) if receipt else {}
    request = evidence.get('request')
    request = request if isinstance(request, dict) else {}
    return {'model': evidence.get('model_actual', evidence.get('actual_model', 'unknown')),
            'model_requested': next((evidence[k] for k in ('model_requested', 'requested_model', 'requestedModel') if evidence.get(k)), request.get('model', 'unknown')),
            'quality_requested': next((evidence[k] for k in ('quality_requested', 'requested_quality', 'requestedQuality') if evidence.get(k)), request.get('quality', 'unknown')),
            'model_evidence': 'Original receipt; model is not independently verified by this exporter' if receipt else 'unknown; no original generation receipt supplied',
            'generation_receipt': {'path': str(receipt.resolve()), 'sha256': sha(receipt)} if receipt else None,
            'current_preference_config': '../../config/image-generation.json',
            'model_policy': '../../docs/IMAGE_MODEL_POLICY.md'}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--id",required=True); ap.add_argument("--generated",required=True); ap.add_argument("--target",action="append",default=[]); ap.add_argument("--receipt",type=Path,help="Original generation receipt; omitted evidence stays unknown"); args=ap.parse_args()
    metadata=generation_metadata(args.receipt)
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
    data={"generator":"built-in image_gen",**metadata,"quality_parameter_exposed":False,"native_size":native,"native_mode":source_mode,"source_cache_file":Path(args.generated).name,"source_sha256":sha(raw),"prompt":args.id+".prompt.txt","files":rows}
    (ROOT/(args.id+".exports.json")).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"id":args.id,"native_size":native,"exports":len(rows)}))
if __name__=="__main__": main()
