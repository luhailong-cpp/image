from prepare_repair import *
src=(HERE/"save_geometry_north.py").read_text()
start=src.index('base=Image.open(')
body=src[start:].replace('cv.GaussianBlur(safe.astype(np.float32),(0,0),3)','cv.GaussianBlur(safe.astype(np.float32),(0,0),1)').replace('cv.GaussianBlur(residual*safe[:,:,None],(0,0),3)','cv.GaussianBlur(residual*safe[:,:,None],(0,0),1)').replace('cv.GaussianBlur(tab[lab],(0,0),3)','cv.GaussianBlur(tab[lab],(0,0),1)').replace('alpha=np.maximum(a1,a2)','alpha=a1').replace('north-only local sigma3','north-only local sigma1').replace('[[0,115,312,288],[390,115,650,223]]','[[0,115,312,288]]').replace('[[0,115,272,248],[425,115,615,188]]','[[0,115,272,248]]')
prefix='from prepare_repair import *\nv=HERE/"geometry-north-v1";d=v/"rock-sigma1";d.mkdir(exist_ok=False);req=read(v/"repair.request.json");raw=v/"host-result-shifted.png";host=Image.open(raw).convert("RGB")\n'
path=HERE/"build_north_rock_sigma1.py";path.write_text(prefix+body,encoding="utf-8")
print(str(path))

