from pathlib import Path
import sys,numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from heal import now,ref,read,write,derived
F=P.parents[1];R=F/'references';plan=read(F/'plan.json');S=4736;K=1254/S
# Same planning scale, with 1600 actual world pixels of W context rather than only320.
orig=Image.open(R/'structure.png').convert('RGB').resize((S,S),Image.Resampling.LANCZOS)
canvas=Image.new('RGB',(S,S),(15,63,121));canvas.paste(orig,(1280,0))
n,w,nw=[Image.open(plan[k]).convert('RGB') for k in ['northCandidate','westCandidate','northWestCandidate']]
canvas.paste(w.crop((2496,0,4096,4096)),(0,320));canvas.paste(n.crop((0,3776,3136,4096)),(1600,0));canvas.paste(nw.crop((2496,3776,4096,4096)),(0,0))
base=P/'wide-west-base-v5.png';derived(canvas.resize((1254,1254),Image.Resampling.LANCZOS),base,[R/'structure.png',Path(plan['northCandidate']),Path(plan['westCandidate']),Path(plan['northWestCandidate'])],dict(kind='same-scale planning frame with wider actual W context',globalFrameXYWH=[51648,40640,4736,4736],trueJoinX=1600*K,trueJoinY=320*K,planningOnly=True,unsupportedSouthwestBelowY=1170))
a=np.array(Image.open(base).convert('RGB'));y,x=np.mgrid[:1254,:1254];join=int(np.ceil(1600*K));shift=1280*K
hole=((x>=join)&(x<join+180)&(y>=85)&(y<610))|((y>=85)&(y<205)&(x>=join)&(x<int(465+shift)))
rgba=np.concatenate([a,np.full((1254,1254,1),255,dtype=np.uint8)],axis=2);rgba[hole]=[255,255,255,0]
target=P/'wide-west-edit-target-v5.png';derived(Image.fromarray(rgba),target,[base],dict(kind='AI input current-side water-only L, preserving all objects',trueJoinX=1600*K,trueJoinY=320*K))
prompt='''Repair ONLY the transparent white WATER holes of Image1. Return one opaque1254-square. Image2 is the same unmasked frame showing immutable context; Image3 is approved STYLE ONLY, never UI. This is a cropped existing game map, not a standalone scene. Preserve the exact crop, every object, scale, positions, hue and existing pixels. Do not shift, zoom or recenter anything.
Most of the left half (x0..423) is existing real WEST neighbor. Its SMALL softly faceted cobalt water ripples and dispersed warm reflection cells are the authoritative WATER PAINTING SCALE. Top y0..84 is the existing real NORTH neighbor. The white missing current-side water begins at x424 and y85. Extend the exact existing water cells and gold reflection endpoints across these coordinates, retaining their scale and subdued brightness near the join. Gradually transition to the broader original water cells visible on the right of the hole. The tile coordinates x424/y85 must not become bright outlines, vertical or horizontal bands, color steps or regular borders. No new straight line or new column of gold water. The water near the left hole edge must look exactly like the real water immediately to its LEFT, not a uniform big-cell cyan mesh. Continue the upper gold reflection at its real width and slant; do not copy the entire column to the wrong x position.
Do not repaint or redesign ANY physical object. Keep the existing cropped left quay wall exactly as-is; it already naturally ends inside the old neighbor. Keep original boat rim, small square bow post, all bench planks and braces, clipped sail and mast, and the north wooden dock. The white holes contain only water and their fixed limits are not object edges. Do not extend stone or add a new quay, boat, post, mast, rope, person, lantern, sky, moon, horizon, decoration, border, text, or UI. Clean saturated evening cobalt water and warm gold, rounded hand-painted chibi materials, no blur/noise/photo texture. Only fill gaps, preserving composition exactly.'''
pp=P/'heal-v5.prompt.txt';pp.write_text(prompt,encoding='utf-8');refs=[target,base,Path('D:/work/image/designs/gameplay-ui/04-guild.png')]
call=dict(prompt=prompt,referenced_image_paths=[str(q) for q in refs],transparent_background=False);write(P/'heal-v5.call.json',call)
write(P/'heal-v5.request.json',dict(preparedAt=now(),notSubmittedYet=True,submittedParameters=dict(model=None,quality=None,**call),configSnapshot=read(P/'heal-v2.request.json')['configSnapshot'],references=[ref(q) for q in refs],prompt=ref(pp),base=ref(base),planningOnly=True,productionPixels=False,nativeDetailCount=0,globalFrameXYWH=[51648,40640,4736,4736],originalPlanningShiftX=shift))
print(P/'heal-v5.call.json')
