from pathlib import Path
N=Path(__file__).parent
s=(N/'prepare-next-row.py').read_text(encoding='utf-8')
s=s.replace('import numpy as np,json,hashlib,shutil','import numpy as np,json,hashlib,shutil,sys')
s=s.replace("D=N/'r03_c04-v1';D.mkdir(exist_ok=True)","D=N/sys.argv[1];D.mkdir(exist_ok=True);y0=int(sys.argv[2]);y1=y0+1254")
s=s.replace('local=[2957,1933,4211,3187]','local=[2957,y0,4211,y1]')
s=s.replace('C=A.crop(local);C.paste(R.crop((0,1933,115,3187)),(1139,0));C.save(D/\'context.png\');arr=np.array(C)',"C=A.crop(local);ca=np.array(C);ky=int(np.where(ca[:,0,3]==255)[0][0]);C.paste(R.crop((0,y0,115,y1)),(1139,0));C.save(D/'context.png');arr=np.array(C)\nif cp.get('prospectiveRight'):\n P=Image.open(cp['prospectiveRight']['file']).convert('RGBA');assert np.array_equal(np.array(P.crop((0,y0+ky,61,y1))),np.array(R.crop((0,y0+ky,61,y1)))), 'Latest root right has not integrated prior same-edge returns; resolve explicit ROI before generation'")
s=s.replace('arr[1024:','arr[ky:').replace('arr[:1024,','arr[:ky,')
s=s.replace("'knownStartY':1024","'knownStartY':ky")
s=s.replace("'exact native bottom230 and right115'","f'exact native bottom{1254-ky} and right115'")
s=s.replace('[2957,2957,4096,3187]','[2957,y0+ky,4096,y1]').replace('[0,1024]','[0,ky]').replace('[0,1933,115,3187]','[0,y0,115,y1]')
s=s.replace("'patch':'r03_c04'","'patch':D.name")
(N/'prepare-grid-right.py').write_text(s,encoding='utf-8')
