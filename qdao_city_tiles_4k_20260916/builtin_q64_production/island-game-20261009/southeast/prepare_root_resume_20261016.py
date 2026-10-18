from workflow import *
from pathlib import Path

tid='r08_c13'
pf=ROOT/f'progress-{tid}.json'
p=read(pf)
p.update(status='active_native_continuation',workingVersions={'11':'v02','14':'v01','31':'v01','41':'v01','44':'v01'},generatedNativeCount=8,selectedCoordinateCount=5,inFlight=False,updatedAt=now(),pendingRepair={'34':'v01 invented tan paving subdivision; v02 remove it','42':'v01 invented floral medallion and paving borders; v02 remove them'},nextStep='Repair layout-changing paving ornaments before propagating; continue independent 12/21')
write(pf,p)
common=' Use case: precise-object-edit. Edit the FIRST attached native 1254x1254 image; the SECOND image is the layout/context constraint only. Keep the same fixed crop and scale, bright hand-painted Q Daoist daylight, same crisp brush texture, existing plants, boulders and shadows. Return one opaque 1254x1254 image. No texts, characters, buildings, new objects or change of camera.'
descs={
'34':'Remove the newly invented cream/tan decorative paving bands that make a large V-shaped or cross-shaped division across the middle of this image. Replace ONLY these internal bands with ordinary broad pale blue-grey stone slabs of the same scale, grain, weak mortar joints and shade as the immediately surrounding paving. This is a continuous plain stone courtyard, no medallions, no geometric color borders. Keep the actual top/right planted rocky verge exactly at its current silhouette, and do not remove its natural narrow edge. Keep the bottommost 230 pixels exactly unchanged as the verified neighboring overlap. Do not redesign, multiply or move the rocks, plants or shadows.',
'42':'Remove the incorrectly invented carved floral stone medallion at the top-right and all cream/tan decorative paving bands that cross the paved area. Replace those ornament and band areas with the continuous plain pale blue-grey broad courtyard slabs shown by the layout. Keep the slab scale, subtle cracks and weak mortar lines. Keep ALL existing foliage/flowers/branches and their silhouette unchanged. Keep the leftmost 230 pixels and bottommost 230 pixels exactly unchanged, because they are verified adjacent native overlaps. The only change is to turn the decorated paved surface into plain continuous grey paving. No new edging, medallion, fence or objects.'}
for rc,d in descs.items():
 pid=f'{tid}_p{rc}';v='v02';af=ROOT/'prompts'/f'{pid}_{v}.args.json'
 if af.exists():continue
 refs=[ROOT/'native'/f'{pid}_v01.png',ROOT/'guides'/f'{pid}.native-context-v01.png']
 prompt=d+common
 pf2=ROOT/'prompts'/f'{pid}_{v}.prompt.txt';pf2.write_text(prompt,encoding='utf-8')
 args={'prompt':prompt,'referenced_image_paths':[str(x) for x in refs],'transparent_background':False}
 write(af,args)
 write(ROOT/'prompts'/f'{pid}_{v}.request.json',{'promptPath':str(pf2),'references':[{'file':str(x),'sha256':sha(x),'role':'native edit target' if i==0 else 'fixed coordinate layout/context only'} for i,x in enumerate(refs)],'transparent_background':False})
print('Saved root selection and two precise layout repair requests.')
