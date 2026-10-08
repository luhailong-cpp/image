"""Probe bounded registration of existing AI south repairs to immutable lower art."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;T=R/'r07_c15';D=T/'repairs/unified'
sys.path.insert(0,str(D/'python-deps'))
import cv2
def rgb(p):return np.asarray(Image.open(p).convert('RGB')).copy()
def main():
 south=rgb(R/'r08_c15/output/r08_c15.png');result=[]
 for i,x0 in enumerate([0,1024,2048,2842],1):
  folder=D/'south-finishing'/f's{i}';src=rgb(folder/'edited-native.png');target=rgb(folder/'input.png')
  g0=cv2.cvtColor(target,cv2.COLOR_RGB2GRAY);g1=cv2.cvtColor(src,cv2.COLOR_RGB2GRAY)
  dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
  dis.setFinestScale(0);dis.setGradientDescentIterations(40);dis.setVariationalRefinementIterations(10)
  flow=dis.calc(g0,g1,None)
  line=np.median(flow[635:650],axis=0)
  line=cv2.GaussianBlur(line[None,:,:],(31,1),0)[0]
  line=np.clip(line,-96,96)
  yy,xx=np.mgrid[:627,:1254].astype(np.float32)
  w=np.clip((yy-240)/(627-240),0,1);w=w*w*(3-2*w)
  dx=line[None,:,0]*w;dy=line[None,:,1]*w
  mapped=cv2.remap(src,xx+dx,yy+dy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
  im=Image.new('RGB',(1254,400));im.paste(Image.fromarray(mapped[-200:]),(0,0));im.paste(Image.fromarray(south[:200,x0:x0+1254]),(0,200))
  im.save(D/'qa-probes'/f's{i}-flow-common-edge.png')
  Image.fromarray(mapped).save(folder/'registered-upper.png')
  np.savez_compressed(folder/'registration-flow.npz',dx=dx.astype(np.float16),dy=dy.astype(np.float16),boundary_flow=line.astype(np.float16))
  result.append({'name':f's{i}','dxRange':[float(dx.min()),float(dx.max())],'dyRange':[float(dy.min()),float(dy.max())]})
 print(json.dumps(result,indent=2))
 (D/'registration-flow-probe.json').write_text(json.dumps({'opencvVersion':cv2.__version__,'result':result},indent=2))
if __name__=='__main__':main()

