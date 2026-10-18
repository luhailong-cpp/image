import sys,json,hashlib
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parent.parent
s=sys.argv[1]
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=R/'native'/(s+'.png');rq=rd(R/'native'/(s+'.request.json'));rc=rd(R/'native'/(s+'.receipt.json'))
with Image.open(p) as im:
 size=list(im.size); keys=list(im.info.keys())
assert size==[1254,1254],size
for x in rq['references']:assert sh(x['path'])==x['sha256']
out={'file':p.as_posix(),'sha256':sh(p),'generatedAt':rc['finishedAtUtc'],'width':1254,'height':1254,'format':'PNG','tool':'image_gen__imagegen','route':'builtin','submittedParameters':rq['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin returned no actual model or quality metadata.','evidence':{'receipt':(R/'native'/(s+'.receipt.json')).as_posix(),'receiptFields':['result.output_hint'],'pngMetadataKeys':keys},'prompt':(R/'native'/(s+'.prompt.txt')).as_posix(),'references':rq['references'],'coordinates':rq['coordinates'],'status':'candidate_pending_seam_qa','nativePixelsResampled':False}
with Path(str(p)+'.generation.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps({'stem':s,'sha256':out['sha256'],'size':size}))

