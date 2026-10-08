"""Meaningful synthetic geometry/numerical checks; never visual acceptance."""
from pathlib import Path
import hashlib
import json
import re
import datetime
import numpy as np
from PIL import Image
import engine


def coords(x,y,w,h):
    yy,xx=np.mgrid[y:y+h,x:x+w]
    return np.stack([xx%251,yy%241,(xx//251+yy//241)%251],axis=2).astype(np.uint8)


def flip(a,name):
    if name[0]=='S':a=np.flip(a,0)
    if name[1]=='E':a=np.flip(a,1)
    return np.ascontiguousarray(a)


def geometry():
    layout=engine.Layout(stride=16,halo=3,count=4);n,h,p,e=layout.tile,layout.halo,layout.patch,layout.extended;results=[]
    truth=coords(100-h,100-h,e,e)
    for name in ['NW','NE','SW','SE']:
        v,hrole,corner=engine.orientation(name)
        neighbors={role:coords(100+dc*n,100+dr*n,n,n) for role,(dr,dc) in engine.ROLES.items() if role in [v,hrole,corner]}
        for present in [False,True]:
            data=dict(neighbors)
            if not present:data.pop(corner)
            canvas,known,seeds=engine.seed_neighbors(layout,data)
            assert np.array_equal(canvas[known],truth[known])
            cy=0 if v=='north' else e-h;cx=0 if hrole=='west' else e-h
            assert bool(known[cy:cy+h,cx:cx+h].all())==present
            images=dict(data);coverage=np.zeros((n,n),np.uint8)
            for r,c in engine.order(layout,name):
                x,y=layout.origin(r,c);patch=truth[y:y+p,x:x+p]
                ops=engine.context_operations(layout,r,c,name,data)
                context,mask=engine.materialize_context(layout,ops,images)
                assert np.array_equal(context[mask],patch[mask])
                # Every referenced native predecessor exists in this wavefront.
                assert all(op['source'] in images for op in ops)
                edges=engine.active_edges(layout,r,c,name,data);local=known[y:y+p,x:x+p].copy();owner=engine.owner_mask(local,edges,layout)
                before=canvas[y:y+p,x:x+p].copy();merged=np.where(owner[:,:,None],patch,before)
                assert np.array_equal(merged[~owner],before[~owner])
                canvas[y:y+p,x:x+p]=merged;known[y:y+p,x:x+p]=True
                images[f'p{r+1}{c+1}']=patch;coverage[r*16:(r+1)*16,c*16:(c+1)*16]+=1
            assert np.all(coverage==1) and known[h:h+n,h:h+n].all()
            assert np.array_equal(canvas[h:h+n,h:h+n],coords(100,100,n,n))
            results.append(dict(wavefront=name,trueCornerPresent=present,all16CoresExactlyOnce=True,allContextCropsMatchGlobalCoordinates=True,protectedSupportUnchanged=True))
    # Actual production clipping widths and external corner locations.
    actual=engine.Layout()
    for name in ['NW','NE','SW','SE']:
        v,hrole,corner=engine.orientation(name);sr=0 if v=='north' else 3;sc=0 if hrole=='west' else 3
        for r in range(4):
            ops=engine.context_operations(actual,r,sc,name,{hrole:True})
            op=next(o for o in ops if o['source']==hrole)
            assert op['cropLTRB'][3]-op['cropLTRB'][1]==[1139,1254,1254,1139][r]
        for c in range(4):
            ops=engine.context_operations(actual,sr,c,name,{v:True})
            op=next(o for o in ops if o['source']==v)
            assert op['cropLTRB'][2]-op['cropLTRB'][0]==[1139,1254,1254,1139][c]
    return results


def numerical():
    layout=engine.Layout(stride=128,halo=16,count=4);p=layout.patch;yy,xx=np.mgrid[:p,:p]
    context=np.stack([128+45*np.sin(xx/7)+35*np.cos(yy/9),130+50*np.cos(xx/8)+25*np.sin(yy/11),110+40*np.sin((xx+yy)/9)],axis=2).clip(0,255).astype(np.uint8)
    patch=(np.roll(context,(1,2),axis=(0,1)).astype(np.int16)+5).clip(0,255).astype(np.uint8)
    known=(xx<32)|(yy<32);canonical=None;results=[]
    for name in ['NW','NE','SW','SE']:
        v,h,_=engine.orientation(name);edges=[engine.SIDES[h],engine.SIDES[v]]
        a,b,k=flip(context,name),flip(patch,name),flip(known,name);owner=engine.owner_mask(k,edges,layout)
        result,flow,tone,report=engine.register_native(a,b,k,owner,edges,layout,max_shift=6.,tone_cap=18.,return_depth=64)
        weight=engine.inward_weight(layout,edges,64)
        assert np.array_equal(result[~owner],a[~owner])
        assert np.array_equal(result[(weight==0)&owner],b[(weight==0)&owner])
        assert np.all(flow[weight==0]==0) and np.all(tone[weight==0]==0)
        assert np.linalg.norm(flow,axis=2).max()<=6.00001 and np.abs(tone).max()<=18.00001
        assert report['foldedAppliedPixels']==0 and report['jacobianMinimumInAppliedPixels']>=.25
        canonical_flow=flip(flow,name)
        if name[1]=='E':canonical_flow[:,:,0]*=-1
        if name[0]=='S':canonical_flow[:,:,1]*=-1
        values=(flip(result,name),canonical_flow,flip(tone,name))
        if canonical is None:canonical=values
        else:
            for actual,expected in zip(values,canonical):assert np.allclose(actual,expected,rtol=0,atol=1e-6)
        results.append(dict(wavefront=name,maxFlow=float(np.linalg.norm(flow,axis=2).max()),maxTone=float(np.abs(tone).max()),jacobianMinimum=report['jacobianMinimumInAppliedPixels'],reflectionEquivalent=True,zeroInfluenceExactlyNative=True,protectedContextUnchanged=True))
    # Every single edge and adjacent pair uses the exact reflected finite weight.
    for edges in [['left'],['right'],['top'],['bottom'],['left','top'],['right','top'],['left','bottom'],['right','bottom']]:
        w=engine.inward_weight(layout,edges,64);x=16 if 'left' in edges else (143 if 'right' in edges else 100);y=16 if 'top' in edges else (143 if 'bottom' in edges else 100)
        assert w[y,x]==1
        xr=x+64 if 'left' in edges else (x-64 if 'right' in edges else x)
        yr=y+64 if 'top' in edges else (y-64 if 'bottom' in edges else y)
        assert w[yr,xr]==0
    return results


def qa_geometry():
    gx=8192;gy=8192;n=4096;final=Image.fromarray(coords(gx,gy,n,n));results=[]
    for name in ['NW','NE','SW','SE']:
        v,h,corner=engine.orientation(name)
        neighbors={role:Image.fromarray(coords(gx+dc*n,gy+dr*n,n,n)) for role,(dr,dc) in engine.ROLES.items() if role in [v,h,corner]}
        count=0;shared=[];returns=[]
        for label,image,operation,roles in engine.qa_images(final,neighbors,name):
            count+=1
            if label.startswith('junction-'):
                _,x,y=label.split('-');expected=coords(gx+int(x)-160,gy+int(y)-160,320,320)
                assert np.array_equal(np.asarray(image),expected);continue
            if label.startswith('four-tile-'):
                x=gx+(0 if h=='west' else n);y=gy+(0 if v=='north' else n)
                assert np.array_equal(np.asarray(image),coords(x-512,y-512,1024,1024));continue
            if label.startswith('internal-'):
                match=re.match(r'internal-([xy])(\d+)-(.*)',label);axis,pos,suffix=match.groups();pos=int(pos)
                if suffix!='full':pos+=(-256 if (axis=='x' and h=='east') or (axis=='y' and v=='south') else 256)
                assert operation['position']==pos
                vertical=axis=='x';startx=gx+pos-160 if vertical else gx;starty=gy if vertical else gy+pos-160
            else:
                side=label.split('-')[0];vertical=side in ['west','east']
                if '-return-' in label:
                    pos=256 if side in ['west','north'] else 3840;assert operation['position']==pos
                    startx=gx+pos-160 if vertical else gx;starty=gy if vertical else gy+pos-160;returns.append((side,pos))
                elif '-shared-' in label:
                    shared.append(side);pos=0 if side in ['west','north'] else 4096
                    startx=gx+pos-160 if vertical else gx;starty=gy if vertical else gy+pos-160
                else:
                    pos=0 if side in ['west','north'] else 3776
                    startx=gx+pos if vertical else gx;starty=gy if vertical else gy+pos
            actual=np.asarray(image)
            assert actual.shape==(1280,1024,3)
            for section in range(4):
                expected=coords(startx,starty+section*1024,320,1024) if vertical else coords(startx+section*1024,starty,1024,320)
                if vertical:expected=np.rot90(expected)
                assert np.array_equal(actual[section*320:(section+1)*320],expected),(name,label,section)
        assert count==28 and set(shared)=={v,h} and {s for s,_ in returns}=={v,h}
        results.append(dict(wavefront=name,qaImagesVerified=count,all4096PixelsPerEdgeCovered=True,reverseReturnsCorrect=True,actualSharedSides=shared,fourTileCornerCoordinateCorrect=True))
    return results


if __name__=='__main__':
    folder=Path(__file__).resolve().parent
    report=dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),productionImagesRead=False,productionGenerationCalled=False,productionOutputsWritten=False,automaticVisualAcceptance=False,
                geometry=geometry(),numericalRegistration=numerical(),native4096QA=qa_geometry(),result='pass')
    report['tools']=[dict(file=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [folder/'engine.py',folder/'cli.py',folder/'verify.py',engine.ROOT/'native_assemble.py']]
    out=folder/'test-evidence.json';out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(result=report['result'],evidence=str(out),geometryCases=len(report['geometry']),registrationCases=len(report['numericalRegistration']),qaCases=len(report['native4096QA']),productionImagesRead=False)))
