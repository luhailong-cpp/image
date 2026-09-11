"""Extract reviewed source cells with transparent magenta matting.

Preserves every disconnected painted component; there is no largest-component
filter. Explicit source boxes and border pixels are reviewed against each source.
"""
from pathlib import Path
import argparse
import json
import hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
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
    """Remove generated magenta only at the key field and its edge fringe.

    Nearby painted pink, gold and other interior hues remain fully opaque. Every
    disconnected ornament is retained; no connected-component pruning is used.
    """
    array = np.asarray(image.convert('RGBA')).astype(np.float32)
    rgb = array[:,:,:3]
    dominance = np.maximum(0,np.minimum(rgb[:,:,0],rgb[:,:,2])-rgb[:,:,1])
    strong_key = (dominance>170) & (rgb[:,:,1]<85)
    fringe = np.asarray(Image.fromarray((strong_key*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7)))>0
    coverage = np.ones(dominance.shape,dtype=np.float32)
    coverage[fringe] = np.clip(1-dominance[fringe]/225.0,0,1)
    coverage[coverage<.025]=0
    coverage[coverage>.985]=1
    alpha = coverage*(array[:,:,3]/255)
    key = np.array([250,2,250],dtype=np.float32)
    safe = np.maximum(coverage,.00001)
    unmatted = (rgb-(1-coverage[:,:,None])*key)/safe[:,:,None]
    out = np.dstack([np.clip(unmatted,0,255),np.round(alpha*255)]).astype(np.uint8)
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
            entry={'resize_mode':'nine_slice','file':f'{name}.png','size':list(crop.size),'source':'source/01-plates.png',
                   'source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),
                   'source_box_xyxy':spec['box'],
                   'nine_slice':dict(zip(('left','top','right','bottom'),spec['borders'])),
                   'alpha_cleanup':'Strong magenta field plus a 3px fringe only; chroma-key coverage and magenta edge unmatting, opaque painted interiors, every disconnected foreground component retained'}
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
                entry['hanging_inside_canvas']=True
                save(body,ARTWORK/entry['body_file'])
            if spec.get('edge_samples'):
                entry['edge_samples']=spec['edge_samples']
                entry['horizontal_center_sample']=[195,0,220,crop.height]
            if spec.get('stamps'):
                entry['fixed_stamps']=[]
                for i,(anchor,box) in enumerate(spec['stamps']):
                    file=f'{name}.stamp-{i}.png';save(crop.crop(box),ARTWORK/file)
                    entry['fixed_stamps'].append({'file':file,'source_box_xyxy':box,'anchor':anchor})
            # Fill the contractual body height. The source's center side ornaments
            # are fixed overlays; rotated straight top rail supplies stretchable sides.
            body_height=entry.get('body_size',entry['size'])[1]
            top=entry['nine_slice']['top']
            entry.setdefault('edge_samples',{}).update({
                'left':{'box':[195,0,220,top],'rotate':90},
                'right':{'box':[195,0,220,top],'rotate':270}})
            side_boxes={
                'jade':[[0,62,95,127],[502,62,597,127]],
                'ivory':[[0,62,95,128],[502,62,597,128]],
                'card_normal':[[0,65,70,143],[531,65,601,143]],
                'card_selected':[[0,65,70,143],[530,65,600,143]],
                'title':[[0,65,95,127],[503,65,598,127]],
                'muted':[[0,62,95,115],[503,62,598,115]]}
            for i,box in enumerate(side_boxes[name]):
                file=f'{name}.side-{i}.png';save(crop.crop(box),ARTWORK/file)
                entry.setdefault('fixed_stamps',[]).append({'file':file,'source_box_xyxy':box,
                    'anchor':'left-center' if i==0 else 'right-center'})
            index['assets'][name]=entry
    return list(PLATES)


# Native rectangles reviewed from each actual source; do not infer grid crops.
SHEETS = {
 'windows': [
  ('frame','02-main-window.png',[47,68,1625,861],[290,200,285,205]),
  ('panel','03-content-window.png',[43,68,1629,870],[180,130,180,130])],
 'emblems': [
  ('taiji','04-emblems.png',[41,35,301,292],None),
  ('pagoda','04-emblems.png',[345,35,604,291],None),
  ('furnace','04-emblems.png',[648,35,909,292],None),
  ('mountain','04-emblems.png',[952,35,1211,292],None),
  ('lotus','04-emblems.png',[40,333,301,590],None),
  ('sword','04-emblems.png',[346,332,603,590],None),
  ('water','04-emblems.png',[648,333,908,590],None),
  ('compass','04-emblems.png',[952,333,1211,590],None),
  ('peach_spirit','04-emblems.png',[42,630,299,884],None),
  ('flame','04-emblems.png',[346,630,603,885],None),
  ('check','04-emblems.png',[649,630,905,884],None),
  ('lock','04-emblems.png',[953,630,1209,885],None),
  ('status_red','04-emblems.png',[40,924,298,1178],None),
  ('status_green','04-emblems.png',[344,923,602,1179],None),
  ('status_orange','04-emblems.png',[648,924,906,1179],None),
  ('status_gray','04-emblems.png',[953,924,1210,1178],None)],
 'ornaments': [
  ('flower','05-ornaments.png',[53,69,375,383],None),
  ('corner','05-ornaments.png',[459,68,787,380],None),
  ('divider','05-ornaments.png',[828,180,1226,262],None),
  ('tassel','05-ornaments.png',[124,440,314,824],None),
  ('lantern','05-ornaments.png',[512,431,732,824],None),
  ('moon_rabbit','05-ornaments.png',[864,463,1216,808],None),
  ('recommend','05-ornaments.png',[35,971,410,1084],None),
  ('knob','05-ornaments.png',[485,900,758,1142],None),
  ('medallion','05-ornaments.png',[835,906,1220,1139],None)],
 'fields': [
  ('stat_field','06-attribute-fields.png',[25,100,393,193],[65,32,80,32]),
  ('slider_track','06-attribute-fields.png',[445,113,809,177],[48,21,48,21]),
  ('slider_fill','06-attribute-fields.png',[864,113,1227,177],[46,21,46,21]),
  ('slider_thumb','06-attribute-fields.png',[115,362,302,519],None),
  ('step_normal','06-attribute-fields.png',[528,348,726,536],[72,66,76,76]),
  ('step_selected','06-attribute-fields.png',[947,348,1144,536],[72,66,76,76]),
  ('tab_vertical_normal','06-attribute-fields.png',[156,598,256,882],[35,68,35,85]),
  ('tab_vertical_selected','06-attribute-fields.png',[577,598,677,882],[35,68,35,85]),
  ('section_header','06-attribute-fields.png',[849,699,1239,796],[70,32,100,35]),
  ('portrait_frame','06-attribute-fields.png',[57,912,360,1208],[78,75,88,84]),
  ('close_button','06-attribute-fields.png',[535,974,718,1150],None),
  ('dropdown_arrow','06-attribute-fields.png',[967,1011,1123,1119],None)]
}


def extract_sheet(index, category):
    names=[]
    for name, filename, box, borders in SHEETS[category]:
        source_path=PACK/'source'/filename
        if not source_path.exists():
            continue
        with Image.open(source_path) as source:
            expected=(1672,941) if category=='windows' else (1254,1254)
            if source.size!=expected:
                raise ValueError(f'{filename} native size changed; explicit crops need review')
            crop=matte(source.crop(box))
        save(crop,ARTWORK/f'{name}.png')
        entry={'file':f'{name}.png','size':list(crop.size),'source':'source/'+filename,
               'source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),
               'source_box_xyxy':box,
               'alpha_cleanup':'Strong magenta field plus a 3px fringe only; chroma-key coverage and magenta edge unmatting, opaque painted interiors, every disconnected foreground component retained'}
        if borders:
            entry['nine_slice']=dict(zip(('left','top','right','bottom'),borders))
        if name in ('slider_track','slider_fill'):
            entry['resize_mode']='horizontal_caps'
        if name=='divider':
            entry['fixed_horizontal_segments']={'left_end':[0,0,126,82],
                'left_rail':[127,0,155,82],'center':[155,0,243,82],
                'right_rail':[244,0,272,82],'right_end':[272,0,398,82]}
        index['assets'][name]=entry
        names.append(name)
    return names


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sheet',choices=['plates','windows','emblems','ornaments','fields','all'],default='all')
    args=parser.parse_args()
    ARTWORK.mkdir(parents=True,exist_ok=True)
    index=load_index()
    names=extract_plates(index) if args.sheet in ('plates','all') else []
    for category in SHEETS:
        if args.sheet in (category,'all'):
            names.extend(extract_sheet(index,category))
    (ARTWORK/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps({'extracted':names,'asset_count':len(index['assets']),'index':str(ARTWORK/'index.json')}))


if __name__=='__main__':main()
