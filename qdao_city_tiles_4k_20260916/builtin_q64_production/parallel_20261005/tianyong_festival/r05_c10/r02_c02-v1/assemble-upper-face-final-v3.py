from pathlib import Path
D=Path(__file__).parent
s=(D/'assemble-upper-clean.py').read_text().replace("F=D/'final-v2'","F=D/'final-v3'").replace('W=np.maximum(np.array(M)/255,np.array(M.filter(ImageFilter.GaussianBlur(9)))/255);','y,x=np.indices((1254,1254));sm=lambda t:np.clip(t,0,1)**2*(3-2*np.clip(t,0,1));W=sm((x-100)/25)*(1-sm((x-1040)/160))*(1-sm((y-175)/40));').replace("r['selectedFinalDirectory']='final-v2'","r['selectedFinalDirectory']='final-v3'")
exec(compile(s,str(__file__),'exec'))
