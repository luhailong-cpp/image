from pathlib import Path
p=Path(__file__).parent
s=(p/'build_v16_endpoint_proposal.py').read_text().replace('v16','v17')
s=s.replace('flow=np.zeros((1254,1254,2),np.float32);flow[:,:,1]=profile[:,None]*weight','slope=np.interp(np.arange(1254),[0,250,360,410,580,650,1253],[.34,.34,.40,-.50,-.50,.53,.53]).astype(np.float32);transportY=yy-slope[:,None]*(xx-627);transportedProfile=np.interp(transportY.ravel(),np.arange(1254),profile).reshape(1254,1254);flow=np.zeros((1254,1254,2),np.float32);flow[:,:,1]=transportedProfile*weight')
s=s.replace('tone=np.clip(cv.GaussianBlur(res[:,None,:],(1,0),.7)[:,0],-18,18)[:,None,:]*weight[:,:,None]*owner[:,:,None]','boundedProfile=np.clip(cv.GaussianBlur(res[:,None,:],(1,0),.7)[:,0],-18,18);transportedTone=np.stack([np.interp(transportY.ravel(),np.arange(1254),boundedProfile[:,c]).reshape(1254,1254) for c in range(3)],axis=2);tone=transportedTone*weight[:,:,None]*owner[:,:,None]')
s=s.replace("('flow',flow)","('transportY',transportY),('measuredSlopeProfile',slope),('flow',flow)")
s=s.replace('Quarter-pixel states in [-6,6], adjacent-row shift variation <=0.5, 2px field smoothing.','Quarter-pixel states in [-6,6], adjacent-row shift variation <=0.5, 1.2px field smoothing. Endpoint flow and color transported parallel to actual observed native diagonal line slopes (0.34,0.4,-0.5,0.53); no horizontal row strip copying.')
(p/'build_v17_endpoint_proposal.py').write_text(s)

