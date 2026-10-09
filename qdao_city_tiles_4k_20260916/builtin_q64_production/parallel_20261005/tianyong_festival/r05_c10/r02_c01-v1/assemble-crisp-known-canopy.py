from pathlib import Path
D=Path(__file__).parent
s=(D.parent/'grid-assemble.py').read_text().replace("D=Path(sys.argv[1]);F=D/'final-v1'","D=Path(__file__).parent;F=D/'final-v2'").replace('smooth((x-1040)/160)','smooth((x-1024)/16)').replace('cw=np.where(C[:,:,3]==255,cw,0);','tassel=smooth((x-235)/20)*(1-smooth((x-500)/25));cw=np.maximum(cw,smooth((x-510)/25)*smooth((y-1024)/16));cw=cw*(1-tassel)+np.maximum(smooth((y-1140)/40),smooth((x-1024)/16))*tassel;cw=np.where(C[:,:,3]==255,cw,0);').replace("'bottomSourceSmoothstepY':[1040,1200]","'bottomSourceSmoothstepY':[1040,1200],'wholeTasselSourceY':[1140,1180],'leafSourceY':[1024,1040],'rightSourceX':[1024,1040]")
exec(compile(s,str(__file__),'exec'))
