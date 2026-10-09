from pathlib import Path
D=Path(__file__).parent
s=(D.parent/'grid-assemble.py').read_text().replace("D=Path(sys.argv[1]);F=D/'final-v1'","D=Path(__file__).parent;F=D/'final-v2'").replace('cw=np.where(C[:,:,3]==255,cw,0);','cw=np.maximum(cw,smooth((x-495)/20)*smooth((y-1024)/16));cw=np.where(C[:,:,3]==255,cw,0);').replace("'bottomSourceSmoothstepY':[1040,1200]","'bottomSourceSmoothstepY':[1040,1200],'bottomPlantStoneSourceY':[1024,1040]")
exec(compile(s,str(__file__),'exec'))
