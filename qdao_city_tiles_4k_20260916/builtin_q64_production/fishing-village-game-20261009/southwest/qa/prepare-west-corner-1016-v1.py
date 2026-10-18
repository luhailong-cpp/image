import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
Q=Path(__file__).resolve().parent;Z=Q.parent
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
box=[15757,32141,17011,33395]
srcs=[
 ('r08_c04',Z/'native/r08_c04_p04_04_v1.png',[15245,31629,16499,32883],[15757,32141,16384,32768]),
 ('r08_c05',Q/'block2x2-r08r09c05c06-v7-r08_c05-context-native.png',[16269,28557,20595,32883],[16384,32141,17011,32768]),
 ('r09_c04',Q/'block2x2-r09r10c03c04-v1-r09_c04-context-native.png',[12173,32653,16499,36979],[15757,32768,16384,33395]),
 ('r09_c05',Q/'block2x2-r08r09c05c06-v7-r09_c05-context-native.png',[16269,32653,20595,36979],[16384,32768,17011,33395])
]
im=Image.new('RGB',(1254,1254));records=[]
for tile,p,s,g in srcs:
 crop=[g[0]-s[0],g[1]-s[1],g[2]-s[0],g[3]-s[1]]
 im.paste(Image.open(p).convert('RGB').crop(crop),(g[0]-box[0],g[1]-box[1]))
 records.append({'tile':tile,'source':ref(p),'sourceGlobalBox':s,'sourceCropBox':crop,'globalBox':g})
p=Q/'west-corner-r08r09c04c05-v1-source-1254.png';assert not p.exists();im.save(p)
t={'image':ref(p),'globalContextBox':box,'sources':records,'nativePixelsResampled':False,'purpose':'native-coordinate composite edit target across four export core boundaries; not approved art'}
out=Q/'west-corner-r08r09c04c05-v1-source-trace.json';assert not out.exists();out.write_text(json.dumps(t,indent=2)+'\n',encoding='utf-8')
print(json.dumps(t))

