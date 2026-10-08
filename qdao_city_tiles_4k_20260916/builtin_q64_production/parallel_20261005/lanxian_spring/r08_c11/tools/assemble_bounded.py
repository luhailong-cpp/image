"""Selective bounded native-pixel quilting, never an automatic acceptance step.

Requires a SHA-pinned completed hard-cut assembly and explicit per-seam plan.
Unlisted seams retain nominal hard-cut ownership, zero tone and zero blending.
No source image is changed. No resampling, warp, blur or geometric shift exists
in this implementation: integer translation is deliberately fixed at zero.

Plan example: {"baselineManifestSha256":"...", "approvedForTrial":true,
  "seams":{"r01_c02:left":{"mode":"dp_tone", "reason":"...",
    "visualEvidence":"..."}}}. Modes: keep, dp, tone, dp_tone.
External west and south accept keep/tone only. Exterior115 halos are restored
from both selected neighbors using the hard-cut baseline explicit corner owner.
Optional localNativeFields require exact native SHA, material labels, axis and
local support. They correct inherited guide-paste tone steps only when reviewed;
these are not automatic seam operations. All default modes remain keep.
Run only after full baseline visual review and root instruction.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
import numpy as np
from PIL import Image
from common import (TILE, NATIVE, CORE, HALO, OVERLAP, EXTENDED,
                    now, sha, read, write, info, load_native, load_neighbors, unchanged)
from assemble import save_qa, external_halo_fragments, place_external_halos

MAX_TONE, SUPPORT, TRANSITION = 16, 160, 6
CLASS_NAMES = ['unclassified protected', 'green and yellow-green foliage', 'turquoise water',
               'warm paving', 'neutral gray stone', 'pink blossom', 'brown wood', 'cool gray paving shadow']
MATERIAL_THRESHOLDS = {
    'neutralGray': 'RGB chroma <= 35',
    'warmPaving': 'r>=120, 5<=r-g<=45, 9<=g-b<=65; yellow-green foliage overrides',
    'water': 'g-r>=18, b-r>=25, g>=70, b>=90',
    'foliage': '(g-r>=7 and g-b>=9) OR (g>=r-18 and g-b>=60)',
    'pink': 'r>=150, b>=100, r-g>=10, b-g>=3, r-b>=3',
    'brownWood': 'r<185, g<130, b<100, r-g>=20, g-b>=10; other colored materials override',
    'coolShadow': '65<=r, b<=225, 0<=b-r<=50, b>=g, 8<=chroma<=50',
}

def material(image):
    """Conservative separated hues; unknown material never receives RGB fields."""
    f=image.astype(np.int16); r,g,b=f[...,0],f[...,1],f[...,2]
    chroma=np.max(f,axis=2)-np.min(f,axis=2)
    labels=np.zeros(r.shape,np.uint8)
    labels[chroma<=35]=4
    labels[(r>=65)&(b<=225)&(b>=r)&(b-r<=50)&(b>=g)&(chroma>=8)&(chroma<=50)]=7
    labels[(r>=120)&(r-g>=5)&(r-g<=45)&(g-b>=9)&(g-b<=65)]=3
    labels[(r<185)&(g<130)&(b<100)&(r-g>=20)&(g-b>=10)]=6
    labels[(g-r>=18)&(b-r>=25)&(g>=70)&(b>=90)]=2
    labels[((g-r>=7)&(g-b>=9))|((g>=r-18)&(g-b>=60))]=1
    labels[(r>=150)&(b>=100)&(r-g>=10)&(b-g>=3)&(r-b>=3)]=5
    return labels


def gradient(a):
    f=a.astype(np.float32)
    return np.maximum(np.max(np.abs(np.diff(f,axis=0,prepend=f[:1])),axis=2),
                      np.max(np.abs(np.diff(f,axis=1,prepend=f[:,:1])),axis=2))

def smoothstep(t):
    t=np.clip(t,0,1); return t*t*(3-2*t)

def minimum_path(cost):
    h,w=cost.shape; prev=cost[0].astype(np.float64).copy()
    parent=np.zeros((h,w),np.int8)
    for y in range(1,h):
        v=np.stack((np.r_[np.inf,prev[:-1]],prev,np.r_[prev[1:],np.inf]))
        choice=np.argmin(v,axis=0);parent[y]=choice-1
        prev=cost[y]+np.min(v,axis=0)
    path=np.empty(h,np.int16);path[-1]=np.argmin(prev)
    for y in range(h-1,0,-1):path[y-1]=path[y]+parent[y,path[y]]
    return path

def cost(a,b,valid):
    result=np.mean(np.abs(a.astype(np.float32)-b.astype(np.float32)),axis=2)
    result+=.25*np.abs(gradient(a)-gradient(b))
    result+=8*(material(a)!=material(b))
    result[~valid]=1e5
    result[:,:16]+=1e5;result[:,-16:]+=1e5
    result+=.01*np.abs(np.arange(result.shape[1])[None,:]-HALO)
    return result

def estimate_bias(a,b,valid):
    """Per-material medians; interpolation changes the field, never image pixels."""
    delta=a.astype(np.float32)-b.astype(np.float32)
    ca,cb=material(a),material(b)
    usable=valid&(ca==cb)&(cb!=0)&(gradient(a)<18)&(gradient(b)<18)
    usable&=(np.max(np.abs(delta),axis=2)<48)
    h=len(a);centres=np.arange(0,h+63,64).clip(0,h-1)
    nodes=np.zeros((len(centres),len(CLASS_NAMES),3),np.float32);evidence=[]
    for i,y in enumerate(centres):
        lo,hi=max(0,int(y)-48),min(h,int(y)+49)
        for cls in range(1,len(CLASS_NAMES)):
            values=delta[lo:hi][usable[lo:hi]&(cb[lo:hi]==cls)]
            if len(values)<24:continue
            proposed=np.clip(np.median(values,axis=0),-MAX_TONE,MAX_TONE)
            before=float(np.abs(values).mean());after=float(np.abs(values-proposed).mean())
            gain=(before-after)/max(before,1e-6)
            accepted=bool(np.max(np.abs(proposed))>=1 and gain>=.10)
            if accepted:nodes[i,cls]=proposed
            evidence.append({'axisNode':int(y),'class':CLASS_NAMES[cls],
                'samples':len(values),'proposedRGB':proposed.tolist(),
                'beforeMeanAbsolute':before,'afterMeanAbsolute':after,
                'relativeGain':gain,'applied':accepted})
    axis=np.arange(h)
    bias=np.stack([np.stack([np.interp(axis,centres,nodes[:,cls,k])
                            for k in range(3)],axis=1)
                   for cls in range(len(CLASS_NAMES))],axis=1).astype(np.float32)
    return bias,evidence

def field_for(raw,path,bias,vertical):
    classes=material(raw);h,w=classes.shape
    if vertical:
        distance=np.abs(np.arange(w)[None,:]-path[:,None])
        weight=1-smoothstep(distance/SUPPORT)
        field=bias[np.arange(h)[:,None],classes]*weight[...,None]
    else:
        distance=np.abs(np.arange(h)[:,None]-path[None,:])
        weight=1-smoothstep(distance/SUPPORT)
        field=bias[np.arange(w)[None,:],classes]*weight[...,None]
    return field,weight

def select_path(a,b,valid,enabled,axis_mask=None):
    nominal=np.full(len(a),HALO,np.int16)
    if not enabled:return nominal,{'decision':'nominal_hardcut'}
    energy=cost(a,b,valid)
    if axis_mask is not None:
        energy[~axis_mask,:]=1e5
        energy[~axis_mask,HALO]=0
    proposed=minimum_path(energy)
    ii=np.arange(len(a));before=float(energy[ii,nominal].mean())
    after=float(energy[ii,proposed].mean());gain=(before-after)/max(before,1e-6)
    accepted=bool(gain>=.08 and np.any(proposed!=HALO))
    return (proposed if accepted else nominal),{'decision':'minimum_error_path' if accepted else 'retain_nominal_no_clear_metric_gain',
        'centerEnergy':before,'proposedEnergy':after,'relativeGain':gain,
        'requiredRelativeGain':.08,'pathStepLimitPixels':1,
        'pathSearchRange':[16,OVERLAP-17],'proposedMinMax':[int(proposed.min()),int(proposed.max())]}

def seam_spec(plan,cell,side):
    spec=plan.get('seams',{}).get(f'{cell}:{side}',{'mode':'keep'})
    mode=spec.get('mode','keep')
    if mode not in ('keep','dp','tone','dp_tone'):raise ValueError(f'Unknown mode: {mode}')
    if side in ('west','south') and mode not in ('keep','tone'):raise ValueError('External boundary geometry and cut are fixed')
    if mode!='keep' and (not spec.get('reason') or not spec.get('visualEvidence')):
        raise ValueError(f'Non-keep seam needs reason and visualEvidence: {cell}:{side}')
    return spec

def axial_scope(spec,origin):
    ranges=spec.get('coreAxisRanges')
    if not ranges:return np.ones(NATIVE,np.float32),np.ones(NATIVE,bool)
    axis=np.arange(NATIVE)+origin-HALO
    weights=np.zeros(NATIVE,np.float32);active=np.zeros(NATIVE,bool)
    fade=int(spec.get('axisFadePixels',64))
    if fade<8 or fade>160:raise ValueError('Axial field fade must be8..160 pixels')
    for lo,hi in ranges:
        if hi<=lo:raise ValueError('Invalid axial range')
        inside=(axis>=lo)&(axis<hi);active|=inside
        # A range touching the outer full-tile halo does not need an artificial
        # fade at the canvas boundary. Internal range returns always fade.
        left=np.ones(NATIVE) if lo<=-HALO else smoothstep((axis-lo)/fade)
        right=np.ones(NATIVE) if hi>=4096+HALO else smoothstep((hi-1-axis)/fade)
        weights=np.maximum(weights,left*right*inside)
    return weights,active

def local_native_field(raw,cell,source_sha,specs):
    """Explicit color-only local fields for non-seam guide-paste artifacts.

    Each entry: patchId, sourceSha256, reason, visualEvidence, axis x|y,
    linePositionNative, axisRangeNative [lo,hi], side both|positive|negative,
    supportPixels (1..160), axisFadePixels (8..160), materialRGB {label:[r,g,b]}.
    No sample invention or geometry operation. Fields sum only under final
    cumulative clipping at16; exterior selected halos are restored afterward.
    """
    result=np.zeros(raw.shape,np.float32); records=[]; classes=material(raw)
    for spec in specs:
        if spec.get('patchId')!=cell:continue
        if spec.get('sourceSha256')!=source_sha:raise ValueError('Local field must pin exact raw native SHA')
        if not spec.get('reason') or not spec.get('visualEvidence'):raise ValueError('Local field needs explicit visual evidence and reason')
        axis=spec.get('axis');position=spec.get('linePositionNative')
        if axis not in ('x','y') or not isinstance(position,(int,float)) or not 0<=position<NATIVE:raise ValueError('Invalid local field axis/line')
        support=int(spec.get('supportPixels',160));fade=int(spec.get('axisFadePixels',64))
        if not 1<=support<=SUPPORT or not 8<=fade<=160:raise ValueError('Local support/fade out of bound')
        lo,hi=spec.get('axisRangeNative',[0,NATIVE])
        if not 0<=lo<hi<=NATIVE:raise ValueError('Local axis range must be inside native')
        coord=np.arange(NATIVE);distance=coord-position
        perpendicular=1-smoothstep(np.abs(distance)/support)
        side=spec.get('side','both')
        if side=='positive':perpendicular*=distance>=0
        elif side=='negative':perpendicular*=distance<=0
        elif side!='both':raise ValueError('Invalid local field side')
        axial=(coord>=lo)&(coord<hi)
        left=np.ones(NATIVE) if lo==0 else smoothstep((coord-lo)/fade)
        right=np.ones(NATIVE) if hi==NATIVE else smoothstep((hi-1-coord)/fade)
        axial=axial*left*right
        weight=axial[:,None]*perpendicular[None,:] if axis=='x' else perpendicular[:,None]*axial[None,:]
        palette=np.zeros((len(CLASS_NAMES),3),np.float32)
        rgb=spec.get('materialRGB',{})
        if not rgb:raise ValueError('Local field needs at least one explicit material RGB')
        for key,value in rgb.items():
            label=int(key)
            if label not in range(1,len(CLASS_NAMES)) or len(value)!=3 or not np.isfinite(value).all() or np.max(np.abs(value))>MAX_TONE:raise ValueError('Local material RGB out of bound')
            palette[label]=value
        added=palette[classes]*weight[...,None]
        result+=added
        records.append({**spec,'actualNonzeroPixels':int(np.any(added!=0,axis=2).sum()),'maskDefinition':'raw-native material label times bounded smoothstep field; no image blur'})
    return result,records


def assemble(plan_path,baseline_path,output_name):
    plan_path=Path(plan_path).resolve(strict=True);baseline_path=Path(baseline_path).resolve(strict=True)
    if not plan_path.is_relative_to(TILE) or not baseline_path.is_relative_to(TILE):
        raise ValueError('Plan and hard-cut manifest must be inside this tile')
    plan=read(plan_path);baseline=read(baseline_path)
    if plan.get('approvedForTrial') is not True:raise ValueError('Explicit reviewed trial plan required')
    if plan.get('baselineManifestSha256')!=sha(baseline_path):raise ValueError('Plan does not pin the current hard-cut baseline')
    if baseline.get('tile')!='r08_c11' or baseline['parameters']['method']!='core ownership hard-cut plus selected west and south exterior halos':
        raise ValueError('A completed unchanged hard-cut baseline is required')
    if plan.get('integerTranslations'):raise ValueError('This selective trial keeps all geometry at integer shift[0,0]; no automatic shift')
    known={f'r{r:02d}_c{c:02d}:{side}' for r in range(1,5) for c in range(1,5) for side in ((['left'] if c>1 else ['west'])+(['top'] if r>1 else [])+(['south'] if r==4 else []))}
    if set(plan.get('seams',{}))-known:raise ValueError('Unknown seam key; refusing silently ignored plan')
    if any(f.get('patchId') not in {f'r{r:02d}_c{c:02d}' for r in range(1,5) for c in range(1,5)} for f in plan.get('localNativeFields',[])):raise ValueError('Unknown local field patchId')
    if not re.fullmatch(r'[a-z][a-z0-9_-]*',output_name):raise ValueError('Simple output directory name required')
    output=TILE/output_name
    if output.exists():raise ValueError('Refuse to overwrite any existing candidate')
    arrays={};sources=[]
    for row in range(4):
        for col in range(4):
            im,source=load_native(row+1,col+1)
            arrays[(row,col)]=np.asarray(im);sources.append(source)
    expected={(s['patchId'],s['sha256']) for s in baseline['sources']}
    if expected!={(s['patchId'],s['sha256']) for s in sources}:raise ValueError('Native source set differs from hard-cut')
    for result in baseline['outputs'].values():
        if sha(result['file'])!=result['sha256']:raise ValueError('Baseline output changed')
    neighbors,boundary_sources=load_neighbors()
    if baseline['boundarySources']!=boundary_sources:raise ValueError('Boundary source identities differ from hard-cut')
    corner=baseline['southwestExteriorHaloDecision']
    if not corner.get('explicitDecisionProvided') or corner.get('selection') not in ('west','south'):raise ValueError('Hardcut must pin explicit exterior corner owner')
    corner_owner=corner['selection']
    west_image=neighbors['west'];west=np.asarray(west_image);south=np.asarray(neighbors['south'])
    west_halo,south_halo=external_halo_fragments(neighbors)
    canvas=np.zeros((EXTENDED,EXTENDED,3),np.uint8);valid=np.zeros((EXTENDED,EXTENDED),bool)
    canvas[:,:HALO]=west[:,4096:4096+HALO];valid[:,:HALO]=True
    owners=np.zeros((EXTENDED,EXTENDED),np.uint8);owners[:,:HALO]=255
    output.mkdir();(output/'masks').mkdir();(output/'fields').mkdir()
    steps=[]
    for row in range(4):
        for col in range(4):
            cell=f'r{row+1:02d}_c{col+1:02d}';raw=arrays[(row,col)]
            x,y=col*CORE,row*CORE
            old=canvas[y:y+NATIVE,x:x+NATIVE].copy();seen=valid[y:y+NATIVE,x:x+NATIVE].copy()
            source_sha=next(s['sha256'] for s in sources if s['patchId']==cell)
            local_field,local_records=local_native_field(raw,cell,source_sha,plan.get('localNativeFields',[]))
            joins={}
            for side in ((['left'] if col else ['west'])+(['top'] if row else [])+(['south'] if row==3 else [])):
                spec=seam_spec(plan,cell,side);mode=spec.get('mode','keep')
                vertical=side in ('west','left')
                axial_weight,axis_mask=axial_scope(spec,y if vertical else x)
                if side=='west':
                    a=west[y:y+NATIVE,4096:4326];b=raw[:,:OVERLAP];v=np.ones(a.shape[:2],bool)
                elif side=='south':a,b,v=south[:OVERLAP,x:x+NATIVE].transpose(1,0,2),raw[CORE:].transpose(1,0,2),np.ones((NATIVE,OVERLAP),bool)
                elif vertical:a,b,v=old[:,:OVERLAP],raw[:,:OVERLAP],seen[:,:OVERLAP]
                else:a,b,v=old[:OVERLAP].transpose(1,0,2),raw[:OVERLAP].transpose(1,0,2),seen[:OVERLAP].T
                bias=np.zeros((NATIVE,len(CLASS_NAMES),3),np.float32);bias_evidence=[]
                if 'tone' in mode:bias,bias_evidence=estimate_bias(a,b,v)
                allowed_classes=spec.get('toneMaterials',list(range(1,len(CLASS_NAMES))))
                if any(cls not in range(1,len(CLASS_NAMES)) for cls in allowed_classes):raise ValueError('Unknown tone material label')
                for cls in range(len(CLASS_NAMES)):
                    if cls not in allowed_classes:bias[:,cls]=0
                path,decision=select_path(a,b,v,'dp' in mode,axis_mask)
                if side=='south':path=path+CORE
                joins[side]={'path':path,'bias':bias,'vertical':vertical,'spec':spec,
                    'decision':decision,'biasEvidence':bias_evidence,'mode':mode,
                    'axialWeight':axial_weight,'axisMask':axis_mask}
            # Tone field follows the selected actual path; no historical path field survives.
            def render_fields():
                fs=[];ws=[]
                for j in joins.values():
                    if 'tone' in j['mode']:
                        f,w=field_for(raw,j['path'],j['bias'],j['vertical'])
                        axial=j['axialWeight'][:,None] if j['vertical'] else j['axialWeight'][None,:]
                        fs.append(f*axial[...,None]);ws.append(w*axial)
                f=np.zeros(raw.shape,np.float32)
                if fs:f=np.clip(np.sum(fs,axis=0)/np.maximum(1,np.sum(ws,axis=0))[...,None],-MAX_TONE,MAX_TONE)
                f=np.clip(f+local_field,-MAX_TONE,MAX_TONE)
                return np.clip(np.rint(raw.astype(np.float32)+f),0,255).astype(np.uint8)
            corrected=render_fields()
            # One path refinement against tone-corrected original pixels, then rebuild field.
            for side,j in joins.items():
                if 'dp' not in j['mode']:continue
                if side=='left':a,b,v=old[:,:OVERLAP],corrected[:,:OVERLAP],seen[:,:OVERLAP]
                else:a,b,v=old[:OVERLAP].transpose(1,0,2),corrected[:OVERLAP].transpose(1,0,2),seen[:OVERLAP].T
                j['path'],j['refinedDecision']=select_path(a,b,v,True,j['axisMask'])
            corrected=render_fields();delta=corrected.astype(np.int16)-raw.astype(np.int16)
            assert np.max(np.abs(delta))<=MAX_TONE
            alpha=np.ones((NATIVE,NATIVE),np.float32)
            for side,j in joins.items():
                if side in ('west','south'):continue
                path=j['path'];dp=bool('dp' in j['mode'] and np.any(path!=HALO))
                signed=(np.arange(NATIVE)[None,:]-path[:,None] if j['vertical']
                        else np.arange(NATIVE)[:,None]-path[None,:])
                incoming=(signed>=0).astype(np.float32)
                if dp:
                    blended=np.clip((signed+TRANSITION/2)/TRANSITION,0,1)
                    axial=j['axialWeight'][:,None] if j['vertical'] else j['axialWeight'][None,:]
                    # No feather survives outside the same reviewed axis scope
                    # that bounds its tone field. Fade its width contribution
                    # at range endpoints to retain the baseline elsewhere.
                    incoming=incoming+axial*(blended-incoming)
                alpha=np.minimum(alpha,incoming)
            alpha[~seen]=1
            if col==0:alpha[:,:HALO]=0
            alpha8=np.rint(alpha*255).astype(np.uint8);weight=alpha8.astype(np.uint32)[...,None]
            joined=((old.astype(np.uint32)*(255-weight)+corrected.astype(np.uint32)*weight+127)//255).astype(np.uint8)
            canvas[y:y+NATIVE,x:x+NATIVE]=joined;valid[y:y+NATIVE,x:x+NATIVE]=True
            own=owners[y:y+NATIVE,x:x+NATIVE];own[alpha8>=128]=row*4+col+1
            mask=output/'masks'/f'{cell}.alpha.png';Image.fromarray(alpha8).save(mask)
            field=output/'fields'/f'{cell}.rgb-delta.npz';np.savez_compressed(field,rgbDelta=delta.astype(np.int8))
            paths=output/'masks'/f'{cell}.paths.npz';np.savez_compressed(paths,**{side:j['path'] for side,j in joins.items()})
            bias_path=output/'fields'/f'{cell}.bias.npz';np.savez_compressed(bias_path,**{side:j['bias'] for side,j in joins.items()})
            steps.append({'patchId':cell,'nativeOriginXY':[x,y],'integerTranslationXY':[0,0],
                'alpha':info(mask),'rgbDelta':info(field),'paths':info(paths),'bias':info(bias_path),
                'maxPerChannelDelta':np.abs(delta).max(axis=(0,1)).tolist(),
                'changedNativePixels':int(np.any(delta!=0,axis=2).sum()),
                'localNativeFields':local_records,
                'blendPixels':int(((alpha8>0)&(alpha8<255)).sum()),
                'seams':{side:{k:v for k,v in j.items() if k not in ('path','bias','axialWeight','axisMask')}
                         for side,j in joins.items()}})
            print(json.dumps({'cell':cell,'tonePixels':steps[-1]['changedNativePixels'],'blendPixels':steps[-1]['blendPixels']}),flush=True)
    assert valid.all()
    restored=Image.fromarray(canvas)
    place_external_halos(restored,owners,west_halo,south_halo,corner_owner)
    canvas=np.asarray(restored).copy()
    west_mask=owners[:,:HALO]==255;south_mask=owners[4211:]==254
    assert np.array_equal(canvas[:,:HALO][west_mask],np.asarray(west_halo)[west_mask])
    assert np.array_equal(canvas[4211:][south_mask],np.asarray(south_halo)[south_mask])
    if not plan.get('localNativeFields') and all(v.get('mode','keep')=='keep' for v in plan.get('seams',{}).values()):
        assert np.array_equal(canvas,np.asarray(Image.open(baseline['outputs']['extended']['file']).convert('RGB'))), 'All-keep must exactly equal baseline'
    for source in sources:
        if sha(source['file'])!=source['sha256'] or sha(source['generationRecord']['file'])!=source['generationRecord']['sha256']:
            raise ValueError('Source or source record changed during trial')
    unchanged(boundary_sources)
    core=Image.fromarray(canvas[HALO:4211,HALO:4211]);ext=Image.fromarray(canvas)
    cp,ep,op=output/'core4096.png',output/'extended4326.png',output/'native-owner-mask4326.png'
    core.save(cp);ext.save(ep);Image.fromarray(owners).save(op)
    qa=save_qa(output,core,neighbors)
    manifest={'schemaVersion':1,'tile':'r08_c11','createdAtUtc':now(),
        'status':'selective_bounded_trial_pending_all_visual_QA','script':info(__file__),
        'plan':info(plan_path),'baseline':info(baseline_path),'sources':sources,
        'boundarySources':boundary_sources,'southwestExteriorHaloDecision':corner,'steps':steps,
        'parameters':{'integerTranslationMax':0,'actualAllTranslations':[0,0],
            'resampling':False,'warp':False,'blur':False,'newAIGeneration':False,
            'perSourcePerChannelRgbBound':MAX_TONE,'supportPixels':SUPPORT,
            'dpTransitionPixels':TRANSITION,'minimumPathStepPixels':1,
            'materialGroups':CLASS_NAMES,'materialThresholds':MATERIAL_THRESHOLDS,'unknownMaterialCorrection':0,
            'localNativeFields':'explicit raw-native SHA-pinned material fields; cumulative clamp16 with seam field',
            'toneNodeSpacing':64,'toneWindowRadius':48,'sameClassSampleMin':24,
            'toneGainThreshold':.10,'pathGainThreshold':.08,
            'defaultUnlistedSeam':'unchanged nominal hardcut',
            'fieldIntersection':'weighted average; per-source clipped16, never additive beyond bound',
            'blendDefinition':'6px transition of genuine source pixels, no resampling or invented geometry'},
        'outputs':{'core':info(cp),'extended':info(ep),'owner':info(op)},
        'sourceHashesUnchanged':True,'exteriorHaloOwnedPixelsByteIdentical':True,
        'westExteriorHaloFullByteEqual':bool(np.array_equal(canvas[:,:HALO],np.asarray(west_halo))),
        'southExteriorHaloFullByteEqual':bool(np.array_equal(canvas[4211:],np.asarray(south_halo))),
        'qa':qa,'formalAccepted':False,'qualifiedComplete4KCandidate':False,
        'qaAccepted':False,'clientAccepted':False,
        'remaining':['Inspect all24 internal seam segments,9 junctions,4 west segments,4 south segments and4 outer corners.',
            'Inspect each field support return and material-class contour for an artificial tone edge.',
            'DP and tone metrics do not certify visual quality or repair incompatible geometry/texture frequency.',
            'North/east external adjacency, diagonal corner and navigation remain pending.']}
    write(output/'assembly.json',manifest)
    for p in (cp,ep):write(str(p)+'.generation.json',{'file':str(p),'sha256':sha(p),
        'newGeneration':False,'actualModel':None,'actualQuality':None,
        'derivedFrom':sources+list(boundary_sources.values()),'assembly':info(output/'assembly.json'),
        'operation':'selective bounded original-pixel overlap quilting; no upscale/warp/blur',
        'formalAccepted':False})
    print(json.dumps({'candidate':str(cp),'qaCount':len(qa),'formalAccepted':False}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',required=True)
    parser.add_argument('--baseline',default=str(TILE/'assembly_hardcut/assembly.json'))
    parser.add_argument('--output-name',required=True)
    args=parser.parse_args()
    try:assemble(args.plan,args.baseline,args.output_name)
    except (OSError,ValueError,KeyError) as error:parser.exit(2,f'error: {error}\n')
