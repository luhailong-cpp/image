"""Recompute the approved RGB repair from immutable before files, without writes.
Use --trial for the six portrait/front-frame representatives; default verifies
all198 independent portrait/frame images. Derived rows are checked separately.
"""
import argparse
import importlib.util
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
        expected=row['output_sha256']
        supp=e.PACK/'supplement_28'
        if row['slug']=='28_moon_rabbit_artificer' and row['relative']=='portrait.png' and (supp/'publication.json').exists():
            approved=e.load(supp/'approval.json');assert e.sha(supp/'repair.py')==approved['processor_sha256']
            spec=importlib.util.spec_from_file_location('supplement28_rebuild',supp/'repair.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
            old28=supp/'before/qdao_chibi_roster_v11/28_moon_rabbit_artificer/portrait.png'
            assert np.array_equal(np.asarray(im),np.asarray(Image.open(old28).convert('RGBA')))
            im,_,_=mod.clean(im);expected=approved['sha256']
        target=e.ROOT/row['path'];assert e.sha(target)==expected
        assert np.array_equal(np.asarray(im),np.asarray(Image.open(target).convert('RGBA'))),row['path']
        n+=1
    print(f'PASS {n} recomputed independent exports; pixel-identical to approved current media; no writes.')
if __name__=='__main__':main()
