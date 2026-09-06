"""Remove residual magenta matte from the jade/ivory/brown walking hero."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent

def main():
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf8'))
    records=[]
    for direction,entry in manifest['directions'].items():
        direction_rows=[]
        for frame in entry['frames']:
            path=ROOT/frame['file']; before=hashlib.sha256(path.read_bytes()).hexdigest()
            with Image.open(path) as im: pixels=np.array(im.convert('RGBA'))
            delta=pixels[:,:,:3].astype(np.int32)-np.array([255,0,255],np.int32)
            mask=(np.sum(delta*delta,axis=2)<=155**2)&(pixels[:,:,3]>0)
            count=int(mask.sum())
            assert count<0.01*1254*1254,'Unexpected key-color area; inspect manually'
            if count:
                pixels[mask]=[0,0,0,0]
                Image.fromarray(pixels).save(path,optimize=True)
            with Image.open(path) as final:
                alpha=final.getchannel('A'); bounds=list(alpha.getbbox())
                assert final.size==(1254,1254) and alpha.getextrema()==(0,255)
                assert bounds[3]==1179 and min(bounds[0],bounds[1],1254-bounds[2])>16
            frame.update(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),alpha_bbox=bounds)
            row={'file':frame['file'],'removed_key_pixels':count,'sha256_before':before,'sha256_after':frame['sha256']}
            records.append(row); direction_rows.append(row)
        record_path=ROOT/entry['qc']
        record=json.loads(record_path.read_text(encoding='utf8'))
        record['final_key_edge_cleanup']={'script':'../clean_key_edges.py','rgb_key':[255,0,255],
            'rgb_euclidean_distance_max':155,'applies_to':'jade/ivory/gold/brown hero with no purple costume',
            'frames':direction_rows,'feet_y_preserved':1179}
        record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    manifest['final_key_edge_cleanup']={'script':'clean_key_edges.py','all_feet_y':1179,'frames_checked':32,
        'removed_key_pixels':sum(r['removed_key_pixels'] for r in records)}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(manifest['final_key_edge_cleanup'],ensure_ascii=False))

if __name__=='__main__': main()
