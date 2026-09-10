"""Extract reviewed source cells with transparent magenta matting.

Preserves every disconnected painted component; there is no largest-component
filter. Explicit source boxes and border pixels are reviewed against each source.
"""
from pathlib import Path
import argparse
import json
import hashlib
import numpy as np
from PIL import Image, ImageDraw
from art_support import PACK, ARTWORK, save

# Manually reviewed source rectangles in 01-plates.png (1254 x 1254).
PLATES = {
 'jade': {'box':[16,153,613,368], 'borders':[144,69,144,68], 'body_height':176,
          'hanging':[[20,173,60,214],[539,173,578,214]]},
 'ivory': {'box':[641,153,1238,333], 'borders':[142,68,142,66]},
 'card_normal': {'box':[13,514,614,714], 'borders':[89,51,89,54]},
 'card_selected': {'box':[640,514,1240,714], 'borders':[87,51,87,54]},
 'title': {'box':[16,905,614,1104], 'borders':[146,65,145,65], 'body_height':165,
           'hanging':[[23,153,62,199],[541,153,581,199]],
           'edge_samples':{'top':[195,0,220,65],'bottom':[195,100,220,165]},
           'stamps':[['center-top',[277,13,322,45]],['center-bottom',[277,137,322,161]]]},
 'muted': {'box':[641,905,1239,1077], 'borders':[145,65,145,63]}
}


def matte(image):
    """Estimate alpha from magenta dominance, then remove backdrop contamination.

    Opaque jade, gold, ivory and vermilion have min(R,B)-G <= 0, so their
    cores retain alpha 255. All non-key components survive independently.
    The generated backdrop is near (250,2,250), with small paint variation;
    the 225 key span removes it while retaining partially covered edge pixels.
    """
    array = np.asarray(image.convert('RGBA')).astype(np.float32)
    rgb = array[:,:,:3]
    dominance = np.maximum(0,np.minimum(rgb[:,:,0],rgb[:,:,2])-rgb[:,:,1])
    coverage = np.clip(1-dominance/225.0,0,1)
    coverage[coverage<.025]=0
    coverage[coverage>.985]=1
    alpha = coverage*(array[:,:,3]/255)
    key = np.array([250,2,250],dtype=np.float32)
    safe = np.maximum(coverage,.00001)
    unmatted = (rgb-(1-coverage[:,:,None])*key)/safe[:,:,None]
    unmatted = np.clip(unmatted,0,255)
    out = np.dstack([unmatted,np.round(alpha*255)]).astype(np.uint8)
    out[out[:,:,3]==0,:3]=0
    return Image.fromarray(out,'RGBA')


def load_index():
    path=ARTWORK/'index.json'
    if path.exists():return json.loads(path.read_text('utf-8-sig'))
    return {'version':1,'schema':'Explicit per-asset source crops and source pixel borders; full RGBA file plus optional separately anchored ornaments.',
            'assets':{}}


def extract_plates(index):
    source_path=PACK/'source/01-plates.png'
    if not source_path.exists():return []
    with Image.open(source_path) as source:
        if source.size!=(1254,1254):raise ValueError('01-plates source layout requires review at its actual native size')
        for name,spec in PLATES.items():
            crop=matte(source.crop(spec['box']))
            save(crop,ARTWORK/f'{name}.png')
            entry={'resize_mode':'horizontal_caps','file':f'{name}.png','size':list(crop.size),'source':'source/01-plates.png',
                   'source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),
                   'source_box_xyxy':spec['box'],
                   'nine_slice':dict(zip(('left','top','right','bottom'),spec['borders'])),
                   'alpha_cleanup':'min(R,B)-G chroma-key coverage and magenta edge unmatting; every disconnected foreground component retained'}
            if spec.get('body_height'):
                body=crop.crop((0,0,crop.width,spec['body_height']))
                entry['hanging_overlays']=[]
                for i,box in enumerate(spec['hanging']):
                    file=f'{name}.tassel-{i}.png';save(crop.crop(box),ARTWORK/file)
                    entry['hanging_overlays'].append({'file':file,'source_box_xyxy':box,
                                                     'anchor':'bottom-left' if i==0 else 'bottom-right'})
                    ImageDraw.Draw(body).rectangle(box,fill=(0,0,0,0))
                entry['body_file']=f'{name}.body.png'
                entry['body_size']=list(body.size)
                save(body,ARTWORK/entry['body_file'])
            if spec.get('edge_samples'):
                entry['edge_samples']=spec['edge_samples']
                entry['horizontal_center_sample']=[195,0,220,crop.height]
            if spec.get('stamps'):
                entry['fixed_stamps']=[]
                for i,(anchor,box) in enumerate(spec['stamps']):
                    file=f'{name}.stamp-{i}.png';save(crop.crop(box),ARTWORK/file)
                    entry['fixed_stamps'].append({'file':file,'source_box_xyxy':box,'anchor':anchor})
            index['assets'][name]=entry
    return list(PLATES)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sheet',choices=['plates','all'],default='all')
    args=parser.parse_args()
    ARTWORK.mkdir(parents=True,exist_ok=True)
    index=load_index()
    names=extract_plates(index)
    (ARTWORK/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps({'extracted':names,'index':str(ARTWORK/'index.json')}))


if __name__=='__main__':main()
