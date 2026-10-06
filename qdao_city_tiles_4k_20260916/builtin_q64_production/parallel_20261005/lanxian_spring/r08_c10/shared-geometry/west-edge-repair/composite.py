from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
req=json.loads((P/'request.json').read_text(encoding='utf-8'))
basefile=P/'source-core4096.png';gfile=P/'generated-original-1254.png'
assert sha(basefile)==req['sourceC10']['sha256']
base=np.asarray(Image.open(basefile).convert('RGB'))
generated=np.asarray(Image.open(gfile).convert('RGB'))
assert base.shape==(4096,4096,3) and generated.shape==(1254,1254,3)
alpha=np.zeros((4096,4096),dtype=np.uint8)
xx,yy=np.meshgrid(np.arange(72,dtype=np.float32),np.arange(1120,1380,dtype=np.float32))
distance=np.minimum(np.abs(yy-(1182.0+0.52*xx)),np.abs(yy-(1301.0+0.52*xx)))
cross=np.clip((20-distance)/8,0,1)
along=np.clip((72-xx)/40,0,1)
alpha[1120:1380,:72]=np.rint(255*cross*along).astype(np.uint8)
ay,ax=np.where(alpha>0)
assert int(ax.max())<200 and int(ay.min())>=1120 and int(ay.max())<1380
result=base.copy()
a=alpha[ay,ax,None].astype(np.float32)/255
source=generated[ay-700,ax+627,:]
result[ay,ax,:]=np.rint(source.astype(np.float32)*a+base[ay,ax,:].astype(np.float32)*(1-a)).clip(0,255).astype(np.uint8)
outfile=P/'edited-core4096.png';maskfile=P/'alpha4096.png'
Image.fromarray(result).save(outfile);Image.fromarray(alpha).save(maskfile)
outside=bool(np.array_equal(base[alpha==0],result[alpha==0]))
assert outside
changed=np.any(result!=base,axis=2);cy,cx=np.where(changed)
assert int(cx.min())>=0 and int(cx.max())<200 and int(cy.min())>=1120 and int(cy.max())<1380
c09=Image.open(req['sourceC09']['file']).convert('RGB')
assert sha(Path(req['sourceC09']['file']))==req['sourceC09']['sha256']
def join(img,x0,y0,x1,y1):
 out=Image.new('RGB',(x1-x0,y1-y0))
 if x0<0:out.paste(c09.crop((4096+x0,y0,4096,y1)),(0,0))
 if x1>0:out.paste(img.crop((max(0,x0),y0,x1,y1)),(max(0,-x0),0))
 return out
qa=[]
baseim=Image.fromarray(base);resim=Image.fromarray(result)
def board(name,box):
 before=join(baseim,*box);after=join(resim,*box)
 out=Image.new('RGB',(before.width,before.height*2));out.paste(before,(0,0));out.paste(after,(0,before.height))
 p=P/(name+'.png');out.save(p)
 qa.append({'file':str(p),'sha256':sha(p),'c10RelativeBoxLTRB':box,'scale':1,'orderTopBottom':['before','after'],'operation':'exact crop and vertical paste only'})
board('qa-before-after',[-128,1120,240,1400])
board('qa-mask-left-edge',[-48,1120,48,1400])
board('qa-mask-right-edge',[48,1140,96,1390])
board('qa-mask-top-edge',[-24,1144,100,1192])
board('qa-mask-bottom-edge',[-24,1335,100,1380])
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'base':{'file':str(basefile),'sha256':sha(basefile),'originalPath':req['sourceC10']['file']},'readonlyNeighbor':req['sourceC09'],'generated':{'file':str(gfile),'sha256':sha(gfile),'generationRecord':str(gfile)+'.generation.json'},'operation':'Integer coordinate crop of native AI edit result into c10-only narrow two-line mask. Alpha compositing at same coordinates; no image resizing, coordinate shift, geometry warp or blur. c09 not pasted into production output.','mapping':{'generatedContextC10LTRB':[-627,700,627,1954],'generatedLookupXY':['c10x+627','c10y-700']},'maskDefinition':{'envelopeRequested':[0,1120,200,1380],'supportLTRB':[int(ax.min()),int(ay.min()),int(ax.max()+1),int(ay.max()+1)],'lineCenters':['y=1182+0.52*x','y=1301+0.52*x'],'xRange':[0,72],'crossLineFullAlphaHalfWidth':12,'crossLineFeatherPx':8,'alongLineFullAlphaX':[0,32],'alongLineFadeX':[32,72]},'alpha':{'file':str(maskfile),'sha256':sha(maskfile),'mode':'L','size':[4096,4096],'nonzeroPixels':int((alpha>0).sum())},'outputs':[{'file':str(outfile),'sha256':sha(outfile),'pixels':[4096,4096],'role':'unreviewed c10 local edge repair candidate'}],'changedPixels':int(changed.sum()),'actualChangedBoxLTRB':[int(cx.min()),int(cy.min()),int(cx.max()+1),int(cy.max()+1)],'outsideMaskByteEqual':outside,'maxAbsRGBChange':np.max(np.abs(result.astype(np.int16)-base.astype(np.int16)),axis=(0,1)).tolist(),'c09SourceHashUnchanged':True,'resampling':None,'warp':None,'wholeRasterResized':False,'qaBoards':qa,'formalAccepted':False,'qa':'pending actual view'}
write(P/'processing.json',record)
write(P/'edited-core4096.png.derivation.json',{'file':str(outfile),'sha256':sha(outfile),'operation':record['operation'],'derivedFrom':[record['base'],record['generated']],'alpha':record['alpha'],'processing':str(P/'processing.json'),'actualModel':None,'actualQuality':None,'formalAccepted':False})
print(json.dumps({'file':str(outfile),'sha256':sha(outfile),'mask':str(maskfile),'changedPixels':record['changedPixels'],'actualChangedBoxLTRB':record['actualChangedBoxLTRB'],'outsideMaskByteEqual':outside},ensure_ascii=False))
