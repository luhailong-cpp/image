"""Pure c16 repair replay. No writes, generation, resampling, or DAY mutation."""
from pathlib import Path
import importlib.util
import sys
import numpy as np
from PIL import Image

T = Path(__file__).resolve().parent
_path = T.parent / 'r08_c15/replay_c15_consolidated.py'
_spec = importlib.util.spec_from_file_location('c16_shared_rgb_math', _path)
math = importlib.util.module_from_spec(_spec)
_old = sys.dont_write_bytecode
try:
    sys.dont_write_bytecode = True
    _spec.loader.exec_module(math)
finally:
    sys.dont_write_bytecode = _old
sha, ref, read, need, rgb, cut, blend, match = (getattr(math, k) for k in ('sha','ref','read','need','rgb','cut','blend','match'))

SOURCE_OPS = {
    'west-joint': [f'west-only-joint-s{i}' for i in range(1,5)],
    'mast-1024': ['mast-1024'], 'mast-2048': ['mast-2048'], 'mast-3072': ['mast-3072'],
    'hull-combined': ['hull-upper','hull-lower'],
    'water-combined': ['water-upper','water-lower'],
    'west-rail-insertion-finish': ['west-insertion-finish'],
    'west-rail-second': ['west-rail-second'],
    'upper-diagonal-small-notch': ['west-insertion-finish'],
}

def native_id(e):
    p=Path(e['file'])
    return 'west-only-joint-'+p.stem if p.parent.name=='west-only-joint' else p.parent.name

def verify(e):
    need(Path(e['file']).is_file() and sha(e['file'])==e['sha256'],'Dependency mismatch: '+e['file'])

def mask(e):
    verify(e)
    with Image.open(e['file']) as im:
        need(im.mode=='L','Non-L mask: '+e['file'])
        return np.array(im)

def seam_alpha(e):
    """Check exact 2-pixel transition ownership and source-coordinate metadata."""
    m=mask(e['maskPng']); verify(e['maskNpz'])
    with np.load(e['maskNpz']['file'],allow_pickle=False) as z:
        need(np.array_equal(m,z['alpha_u8']),'PNG/NPZ alpha mismatch '+e['id'])
        need(z['pair_rect_xyxy'].tolist()==e['pairOverlapRectXYXY'],'Pair coordinate mismatch '+e['id'])
        need(int(z['transition_pixels'])==2,'Wrong transition width '+e['id'])
        offsets=z['seam_offsets'].copy()
    ov=e['overlapPixels']; d=np.arange(ov)[None,:]-offsets[:,None]
    reconstructed=np.where(d<=-2,0,np.where(d==-1,64,np.where(d==0,191,255))).astype(np.uint8)
    if e['orientation']=='horizontal': reconstructed=reconstructed.T
    need(np.array_equal(m,reconstructed),'Seam offsets differ from alpha '+e['id'])
    b=e['pairOverlapRectXYXY']
    need(m.shape==(b[3]-b[1],b[2]-b[0]),'Seam shape mismatch '+e['id'])
    return m

def reconstruct_insertion_alpha(e,seams):
    b=e['rectXYXY']; out=np.zeros((b[3]-b[1],b[2]-b[0]),np.uint8)
    need(not e['eligibilityMaskApplied'],'Unhandled eligibility')
    for i,roi in enumerate(e['intendedRepairRectsXYXY'],1):
        x0,y0,x1,y1=roi; h,w=y1-y0,x1-x0
        edge=min(e['edgeSearchPixels'],(w-1)//2,(h-1)//2)
        a=np.full((h,w),255,np.uint8)
        for side,val in [('left',x0),('right',x1),('top',y0),('bottom',y1)]:
            if val==(0 if side in ('left','top') else 4096): continue
            se=seams[f'{e["id"]}-roi{i}-{side}']; m=seam_alpha(se)
            expected={'left':[x0,y0,x0+edge,y1],'right':[x1-edge,y0,x1,y1],'top':[x0,y0,x1,y0+edge],'bottom':[x0,y1-edge,x1,y1]}[side]
            need(se['pairOverlapRectXYXY']==expected,'Insertion side coordinates differ')
            target={'left':a[:,:edge],'right':a[:,-edge:],'top':a[:edge],'bottom':a[-edge:]}[side]
            np.minimum(target,255-m if side in ('right','bottom') else m,out=target)
        local=[x0-b[0],y0-b[1],x1-b[0],y1-b[1]]
        np.maximum(cut(out,local),a,out=cut(out,local))
    need(np.array_equal(out,mask(e['alpha'])),'Insertion alpha reconstruction differs '+e['id'])
    return out

def source_groups(m,arrays,mode='day',field_sink=None):
    seams={e['id']:e for e in m['seams']}
    def join(ids,starts,origin,label,right_only=False):
        current=(arrays[ids[0]][:,627:] if right_only else arrays[ids[0]]).copy()
        for i,ident in enumerate(ids[1:],1):
            nxt=arrays[ident][:,627:] if right_only else arrays[ident]
            start=starts[i]; ov=current.shape[0]-start; se=seams[f'{label}-{i}-{i+1}']
            a=mask(se['maskPng']); before=current[-ov:]; later=nxt[:ov]
            need(se['orientation']=='horizontal','Unknown join orientation')
            need(se['pairOverlapRectXYXY']==[origin[0],origin[1]+start,origin[0]+current.shape[1],origin[1]+start+ov],'Join rect differs')
            need(before.shape==later.shape and a.shape==before.shape[:2],'Join shape differs')
            if mode!='raw':
                later,field,weight=match(before,later,a,max_delta=32 if mode=='day' else 24)
                if field_sink: field_sink(se['id'],field,weight,a,se['localColorMatch'])
            current=np.concatenate((current[:-ov],blend(before,later,a),nxt[ov:]),axis=0)
        return current
    out={'west-joint':join(SOURCE_OPS['west-joint'],[0,1024,2048,2842],[0,0],'west-joint',True),
         'hull-combined':join(SOURCE_OPS['hull-combined'],[0,562],[1421,2280],'hull-pair'),
         'water-combined':join(SOURCE_OPS['water-combined'],[0,1024],[2525,0],'water-pair')}
    for label,ids in SOURCE_OPS.items():
        if label not in out: out[label]=arrays[ids[0]]
    need(set(out)=={e['id'] for e in m['insertions']},'Insertion catalog mismatch')
    return out

def replay(m,base,arrays,mode='day',field_sink=None,stage_sink=None):
    pieces=source_groups(m,arrays,mode,field_sink); result=base.copy(); union=np.zeros((4096,4096),np.uint8)
    for i,e in enumerate(m['insertions']):
        b=e['rectXYXY']; before=cut(result,b).copy(); piece=pieces[e['id']]; a=mask(e['alpha'])
        need(before.shape==piece.shape and a.shape==piece.shape[:2],'Insertion size mismatch '+e['id'])
        if mode!='raw':
            piece,field,weight=match(before,piece,a,max_delta=32 if mode=='day' else 24)
            if field_sink: field_sink(e['id'],field,weight,a,e['localBoundaryColorMatch'])
        result[b[1]:b[3],b[0]:b[2]]=blend(before,piece,a)
        np.maximum(cut(union,b),a,out=cut(union,b))
        if stage_sink: stage_sink(i,e,result)
    need(np.array_equal(base[union==0],result[union==0]),'Changed outside insertion union')
    return result,union
