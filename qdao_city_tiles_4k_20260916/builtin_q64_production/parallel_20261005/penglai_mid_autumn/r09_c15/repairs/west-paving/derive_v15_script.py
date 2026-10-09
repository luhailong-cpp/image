from pathlib import Path
p=Path(__file__).parent
s=(p/'build_v14_local_proposal.py').read_text()
s=s.replace("proposed-joint-v14","proposed-joint-v15").replace("proposal-v14","proposal-v15").replace("perimeter-v14","perimeter-v15").replace("join-v14","join-v15").replace("detail-v14","detail-v15").replace("crossings-v14","crossings-v15")
start=s.index("tone=np.zeros_like(src")
end=s.index("# Measure only low-gradient",start)
s=s[:start]+"""originalsrc=src.copy()
left=fixed[:,626].astype(np.float32); right=src[:,627].astype(np.float32)
ranges=[(90,135),(320,370),(400,480),(810,875)]
values=[];measurements=[]
for lo,hi in ranges:
 scores=[]
 for shift in np.arange(-6,6.001,.125):
  sampled=np.stack([np.interp(np.arange(lo,hi)+shift,np.arange(1254),right[:,c]) for c in range(3)],axis=1)
  residual=left[lo:hi]-sampled
  bias=np.clip(np.median(residual,axis=0),-18,18)
  score=float(np.mean((residual-bias)**2))
  scores.append((float(shift),score))
 best=min(scores,key=lambda v:v[1]);values.append(best[0])
 measurements.append({'targetRows':[lo,hi],'actualWestColumn':626,'nativeSourceColumn':627,'bestShiftY':best[0],'candidateShiftScorePairs':scores})
profile=np.interp(np.arange(1254),[(lo+hi)/2 for lo,hi in ranges],values).astype(np.float32)
profile=cv.GaussianBlur(profile[:,None],(1,0),12)[:,0]
flow=np.zeros((1254,1254,2),np.float32)
flow[:,:,1]=profile[:,None]*smooth((807-xx)/128)
flow[alpha==0]=0
dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1])
jac=(1+dxu)*(1+dyv)-dyu*dxv
assert np.linalg.norm(flow,axis=2).max()<=6.00001
assert jac[alpha>0].min()>=.25
src=cv.remap(originalsrc,xx+flow[:,:,0],yy+flow[:,:,1],cv.INTER_CUBIC,borderMode=cv.BORDER_REPLICATE)
""" + s[end:]
s=s.replace("[('alpha',alpha),('colorCorrection',tone),('sameMaterialEndpointMask',safe)]","[('alpha',alpha),('flow',flow),('jacobian',jac),('colorCorrection',tone),('sameMaterialEndpointMask',safe)]")
s=s.replace("'actualMaxSourceDisplacement':0","'actualMaxSourceDisplacement':float(np.linalg.norm(flow,axis=2).max()),'measuredNativeEndpointCorrespondence':measurements")
s=s.replace("'jacobian':1","'jacobianMinimumInAppliedPixels':float(jac[alpha>0].min())")
s=s.replace("no registration","bounded native source registration")
(p/'build_v15_local_proposal.py').write_text(s)

