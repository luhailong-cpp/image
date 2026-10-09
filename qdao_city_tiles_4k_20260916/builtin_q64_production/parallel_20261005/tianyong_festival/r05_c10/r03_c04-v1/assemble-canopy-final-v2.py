from pathlib import Path
D=Path(__file__).parent
s=(D/'assemble-canopy.py').read_text().replace("F=D/'final-v1'","F=D/'final-v2'").replace('cw=np.where(C[:,:,3]==255,cw,0);','cw=np.maximum(cw,s((x-780)/40)*s((y-1070)/30));cw=np.where(C[:,:,3]==255,cw,0);').replace("'bottomSourceSmoothstepY':[1140,1200]","'bottomSourceSmoothstepY':[1140,1200],'canopySourceSmoothstepY':[1070,1100]")
exec(compile(s,str(__file__),'exec'))
