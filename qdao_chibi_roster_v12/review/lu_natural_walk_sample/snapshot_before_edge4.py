from pathlib import Path
import shutil,json,hashlib
root=Path(r'E:\work\image\qdao_chibi_roster_v12\candidate-stable-body\24_lu_dongbin');out=root/'review/edge-before';out.mkdir(parents=True,exist_ok=True)
files=[root/'idle'/f'{d}.png' for d in ['N','NE','E','SE','S','SW','W','NW']]+[root/'walk'/d/f'{i:02d}.png' for d in ['N','NE','E','SE','S','SW','W','NW'] for i in range(1,9)]
for p in files:
 t=out/p.relative_to(root);t.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,t)
for name in ['manifest.json','qc.json','validation.json','visual-review.json']:shutil.copyfile(root/name,out/name)
print('Saved 72 current RGBA frames for independent alpha/geometry comparison after the explicit edge cleanup')
