from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;D=R/'r07_c15/repairs/unified';sys.path.insert(0,str(D/'python-deps'));import cv2
south=np.asarray(Image.open(R/'r08_c15/output/r08_c15.png').convert('RGB'))
reports=[]
for i,x0 in enumerate([0,1024,2048,2842],1):
 f=D/'south-finishing'/f's{i}';p=np.asarray(Image.open(f/'edited-native.png').convert('RGB'))
 t=np.asarray(Image.open(f/'input.png').convert('RGB'))
 g0=cv2.cvtColor(t,cv2.COLOR_RGB2GRAY);g1=cv2.cvtColor(p,cv2.COLOR_RGB2GRAY)
 dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM);dis.setFinestScale(0);flow=dis.calc(g0,g1,None)
 blur=cv2.GaussianBlur(g0,(11,11),0);gx=cv2.Sobel(blur,cv2.CV_32F,1,0);gy=cv2.Sobel(blur,cv2.CV_32F,0,1)
 yy,xx=np.mgrid[650:1140:8,80:1175:8];valid=(np.hypot(gx[yy,xx],gy[yy,xx])>35)&(np.hypot(flow[yy,xx,0],flow[yy,xx,1])<140)
 targetxy=np.stack([xx[valid],yy[valid]],axis=1).astype(np.float32);srcxy=targetxy+flow[yy[valid],xx[valid]]
 matrix,inliers=cv2.estimateAffine2D(targetxy,srcxy,method=cv2.RANSAC,ransacReprojThreshold=5,maxIters=5000,confidence=0.995)
 yy,xx=np.mgrid[:627,:1254].astype(np.float32);w=np.clip((yy-150)/(627-150),0,1)
 dx=(matrix[0,0]*xx+matrix[0,1]*yy+matrix[0,2]-xx)*w
 dy=(matrix[1,0]*xx+matrix[1,1]*yy+matrix[1,2]-yy)*w
 mapped=cv2.remap(p,(xx+dx).astype(np.float32),(yy+dy).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
 sheet=Image.new('RGB',(1254,400));sheet.paste(Image.fromarray(mapped[-200:]),(0,0));sheet.paste(Image.fromarray(south[:200,x0:x0+1254]),(0,200));sheet.save(D/'qa-probes'/f's{i}-affine-common-edge.png')
 reports.append({'name':f's{i}','matrixTargetToSource':matrix.tolist(),'inliers':int(inliers.sum()),'points':len(inliers),'maxDx':float(np.abs(dx).max()),'maxDy':float(np.abs(dy).max())})
print(json.dumps(reports,indent=2));(D/'registration-affine-probe.json').write_text(json.dumps(reports,indent=2))

