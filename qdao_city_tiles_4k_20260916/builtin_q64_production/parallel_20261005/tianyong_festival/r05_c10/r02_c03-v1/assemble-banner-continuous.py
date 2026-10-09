from pathlib import Path
D=Path(__file__).parent
s=(D.parent/'grid-assemble.py').read_text().replace("D=Path(sys.argv[1]);F=D/'final-v1'","D=Path(__file__).parent;F=D/'final-v1'").replace("D/'context.png'","D/'context-before-banner-mask.png'").replace('smooth((x-1040)/160)','smooth((x-1140)/60)').replace('cw=np.where(C[:,:,3]==255,cw,0);','cw=np.where((x>=1034)&(x<=1122),smooth((y-1130)/50),cw);cw=np.where(C[:,:,3]==255,cw,0);').replace("'bounds':[54,214] if side=='left' else [1040,1200]","'bounds':[54,214] if side=='left' else [1140,1200]").replace("'contextExactBeyond1200'","'bannerLeftEdgeReturnSourceY':[1130,1180],'intentionalBannerEdgeAIRepair':True,'contextExactBeyond1200'")
exec(compile(s,str(__file__),'exec'))
from PIL import Image
Image.open(D/'final-v1/joined.png').crop((1020,430,1170,1254)).save(D/'final-v1/qa/banner-left-edge.png')
