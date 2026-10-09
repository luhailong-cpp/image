from pathlib import Path
import sys,json,hashlib
B=Path(__file__).resolve().parent/'r08_c16/repairs/consolidated-sync'
name=sys.argv[1]
assert name in ('water-upper','water-lower') and not (B/'native'/(name+'.png')).exists()
pp=B/'prompts'/(name+'.prepared.json'); rp=B/'prompts'/(name+'.request.json')
prepared=json.loads(pp.read_text(encoding='utf8')); request=json.loads(rp.read_text(encoding='utf8'))
extra='\nWater-only clarification: This window contains only open water. Keep exactly Image1\'s existing broad, low-detail painted water planes. Recolor those same planes to the surrounding clean royal-blue/violet festival water with restrained peach-pink lighting already visible in Image2. Repair Image2\'s abrupt vertical pasted-color cutoff into one continuous painted surface. Do not create clouds, new cloud contours, bright small ripples, thin streaks, reflected buildings, sparks, ropes, wood, decorative waves or added texture. Preserve the existing water pattern locations from Image1 and the outer-edge color continuity from Image2. No straight image-splice line.'
if name=='water-lower':
    extra=extra.replace('This window contains only open water.', 'This window has open water behind a real diagonal rope at left and a real round wooden post head near the bottom. Preserve those exact foreground objects and edges from Image1. The following water instructions apply exclusively to the water background.')
    extra=extra.replace('sparks, ropes, wood, decorative waves', 'sparks, additional ropes or wood, decorative waves')
request['prompt']=request['prompt'].split('\nWater-only clarification:')[0]
request['prompt']+=extra
prompt=Path(prepared['prompt']);prompt.write_text(request['prompt'],encoding='utf8')
prepared['promptSha256']=hashlib.sha256(prompt.read_bytes()).hexdigest()
prepared['localWaterClarification']='Broad DAY planes preserved; match surrounding festival hue, no new water geometry or texture'
for path,value in [(rp,request),(pp,prepared)]:path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(name+' request clarified before first generation')
