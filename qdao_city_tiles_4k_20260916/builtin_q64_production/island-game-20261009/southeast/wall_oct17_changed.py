from workflow import *
old=read(ROOT/'qa/r10_c10-wall-oct16-v01/seams.json');new=read(ROOT/'qa/r10_c10-wall-oct17-v03/seams.json');hashes={x['id']:x['sha256'] for x in old['entries']}
print('changed seams:',[x['id'] for x in new['entries'] if x['sha256']!=hashes[x['id']]])
print('changed junctions:',[p.name for p in (ROOT/'qa/r10_c10-wall-oct17-v03').glob('junction_*.png') if sha(p)!=sha(ROOT/'qa/r10_c10-wall-oct16-v01'/p.name)])
