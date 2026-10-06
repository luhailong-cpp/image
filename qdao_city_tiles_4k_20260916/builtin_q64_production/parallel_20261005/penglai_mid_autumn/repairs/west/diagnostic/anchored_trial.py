from pathlib import Path
source=(Path(__file__).parent/'recommended_trial.py').read_text(encoding='utf-8')
# Reuse the same reconstruction; only replace the measured endpoint flow anchor.
source=source.replace("anchor=cv2.GaussianBlur(np.median(lf[:,590:615],axis=1),(1,11),0)","""anchor=cv2.GaussianBlur(np.median(lf[:,590:615],axis=1),(1,11),0)
ay=np.arange(1254,dtype=np.float32)
exactDy=np.interp(ay,[1070,1121,1169,1210,1235,1253],[float(anchor[1070,1]),8,10,-3,2,2]).astype(np.float32)
aw=smooth((ay-1070)/30)
anchor[:,0]*=(1-aw)
anchor[:,1]=anchor[:,1]*(1-aw)+exactDy*aw""")
source=source.replace('recommended-','anchored-')
source=source.replace("oldOnlySupportX=[590,615],", "oldOnlySupportX=[590,615],endpointAnchorsOldToRawY=[[1121,1129],[1169,1179],[1210,1207],[1235,1237]],endpointAnchorDx=0,")
source=source.replace("resampling='bicubic, native dimensions retained, no enlargement or new pixels'", "resampling='bicubic existing source pixels; native dimensions retained, no enlargement or generative art'")
exec(compile(source,__file__,'exec'))
