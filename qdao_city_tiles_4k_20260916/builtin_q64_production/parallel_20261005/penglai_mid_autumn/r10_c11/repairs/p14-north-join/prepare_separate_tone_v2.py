from pathlib import Path
import hashlib,json
P=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_mid_autumn/r10_c11/repairs/p14-north-join")
record=json.loads((P/"tone-diagnostic/sigma3-full256/diagnostic.json").read_text())
print("original_script_hash_matches", hashlib.sha256((P/"diagnose_local_tone.py").read_bytes()).hexdigest()==record["script"]["sha256"])
s=(P/"diagnose_separate_tone.py").read_text()
s=s.replace('D=HERE/"tone-diagnostic-separated"','D=HERE/"tone-diagnostic-separated-v2"')
s=s.replace('side_fields=[]','side_fields=[];edge_stats=[]')
s=s.replace('side_fields.append(np.clip(extended,-18,18))','edge_stats.append(dict(edge=edge,safeSupportPixels=int(side_safe.sum()),rawClippedSupportFraction=float(np.mean(np.any(np.abs(extended[side_safe])>18,axis=1))),rawMaximum=np.abs(extended[side_safe]).max(axis=0).tolist()))\n side_fields.append(np.clip(extended,-18,18))')
s=s.replace('for name,tone,depth in variants:\n out=', 'for name,tone,depth in variants:\n tone=np.clip(tone,-18.,18.)\n out=')
s=s.replace('toneRawClippedSupportFraction=float(np.mean(np.any(np.abs(local[safe])>18,axis=1)))','toneRawClippedSupportFraction=max(r["rawClippedSupportFraction"] for r in edge_stats),separateEdgeSupportStatistics=edge_stats')
(P/"diagnose_separate_tone_v2.py").write_text(s,encoding="utf-8",newline="")

