from pathlib import Path
import hashlib,json
from PIL import Image
R=Path(__file__).resolve().parent
S=R.parents[1];ROOT=next(p for p in R.parents if (p/'config/image-generation.json').is_file())
O=R.parent/'c10-seed';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=S/'next_tile_r09_c10/repairs/versions/external-v8/r09_c10.png'
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
assert sha(source)=='f5a45f15f69104c6f3dfe9f7a855e71f5d142d896cc78ffadbf12b3a57f813e4'
assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
box=[37773,32141,39027,33395]
im=Image.new('RGBA',(1254,1254),(0,0,0,0))
im.paste(Image.open(source).convert('RGBA').crop((909,0,2163,627)),(0,627))
im.save(O/'native-lower-half-outpaint-context.png')
guide=Image.open(master).convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in box))
guide.save(O/'master-layout-reference-only.png')
info=lambda p:{'file':str(p),'sha256':sha(p)}
record={'scope':'native coupled boundary seed; target upper627px new r08_c10 artwork, lower627px exact r09_c10 geometry reference','globalCropLTRB':box,'newUpperTileLocalCropLTRB':[909,3469,2163,4096],'existingLowerTileLocalCropLTRB':[909,0,2163,627],'existingNativeSource':info(source),'masterLayoutSource':info(master),'referenceImages':[info(O/'native-lower-half-outpaint-context.png'),info(O/'master-layout-reference-only.png')],'guideIsUpscaledReferenceOnly':True,'guidePixelsMayEnterFinalArtwork':False,'newArtworkGenerated':False,'formalAccepted':False}
(O/'preparation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(str(O))
