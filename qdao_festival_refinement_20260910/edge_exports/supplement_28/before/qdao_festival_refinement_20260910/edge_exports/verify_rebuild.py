"""Recompute the approved RGB repair from immutable before files, without writes.
Use --trial for the six portrait/front-frame representatives; default verifies
all198 independent portrait/frame images. Derived rows are checked separately.
"""
import argparse
import numpy as np
from PIL import Image
import repair_v11_edges as e

def main():
    p=argparse.ArgumentParser();p.add_argument('--trial',action='store_true');a=p.parse_args()
    stage=e.load(e.PACK/'stage.json');assert stage['processor_sha256']==e.sha(e.PACK/'repair_v11_edges.py')
    n=0
    for row in stage['files']:
        if a.trial and row['relative'] not in ('portrait.png','walk/S/01.png'):continue
        old=e.ROOT/row['before'];assert e.sha(old)==row['source_sha256']
        im=Image.open(old).convert('RGBA')
        if row['changed_rgb_pixels']:im,_,_=e.clean(im,row['slug'])
        target=e.ROOT/row['path'];assert e.sha(target)==row['output_sha256']
        assert np.array_equal(np.asarray(im),np.asarray(Image.open(target).convert('RGBA'))),row['path']
        n+=1
    print(f'PASS {n} recomputed independent exports; pixel-identical to approved current media; no writes.')
if __name__=='__main__':main()
