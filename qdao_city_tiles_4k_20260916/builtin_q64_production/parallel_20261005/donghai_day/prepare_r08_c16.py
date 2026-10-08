"""Right-edge tile preparation; the out-of-city halo is guidance only."""
from pathlib import Path
from PIL import Image
import numpy as np
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;P=R.parents[3];T=R/'r08_c16'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 for name in ['guides','prompts','native','output','qa']:(T/name).mkdir(parents=True,exist_ok=True)
 source=P/'qdao_city_tiles_4k_20260916/builtin_q64_all_city_references/donghai_day/map-native-layout-reference.png'
 target=T/'guides/local-layout.png'
 assert not target.exists() and not (T/'plan.json').exists(),'Existing c16 plan retained'
 with Image.open(source) as image:
  image.load();assert image.size==(1254,1254)
  rgb=np.array(image.convert('RGB'));extended=Image.fromarray(np.pad(rgb,((0,0),(0,4),(0,0)),mode='edge'))
  global_box=[61325,28557,65651,32883];box=[v*1254/65536 for v in global_box]
  extended.transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC).save(target)
  edge=rgb[546:630,-3:];edge_check={'sourceEdgeRegionXYXY':[1251,546,1254,630],'minRGB':edge.min(axis=(0,1)).tolist(),'maxRGB':edge.max(axis=(0,1)).tolist(),'allBlackPixels':int(np.all(edge==0,axis=2).sum()),'pixelCount':int(edge.shape[0]*edge.shape[1]),'visualReview':'pending'}
 now=datetime.now(timezone.utc).isoformat()
 border={'mapBounds':[0,0,65536,65536],'requestedGlobalBox':global_box,'beyondRightMapPixels':115,'rightmostCoreCoordinateExclusive':65536,'rightHaloPurpose':'context only; exclude from all formal core pixels','layoutGuidancePadding':'four source-reference columns extended from rightmost source pixels using edge clamp, reference only','finalCorePixelsNotPadded':True,'finalArtUpscaled':False,'sourceRightEdgeInspection':edge_check}
 plan={'tile':'r08_c16','globalRect':[61440,28672,4096,4096],'worldRect':{'x':331.25,'z':150,'width':18.75,'height':18.75},'layoutSource':str(source),'layoutSourceSha256':sha(source),'layoutSourceBox':box,'globalBox':global_box,'sourceGuide':str(target),'guideSha256':sha(target),'westNeighbor':str(R/'r08_c15/output/r08_c15.png'),'westNeighborSha256':None,'westBindingStatus':'pending','westNeighborRole':'Pending final c15 output SHA; no c01 generation or assembly until explicitly bound','preparedAtUtc':now,'status':'layout_reference_prepared_structure_pending','referenceEnlargementOnly':True,'formalAccepted':False,'nativeGrid':[4,4],'core':1024,'halo':115,'boundaryPolicy':border,'geometryStatus':'confirmed layout crop only; local structure review pending','dayFestivalGeometryAligned':False,'navigationAccepted':False}
 save(T/'plan.json',plan)
 save(Path(str(target)+'.generation.json'),{'file':str(target),'sha256':sha(target),'createdAtUtc':now,'derivedFrom':[{'file':str(source),'sha256':sha(source)}],'operation':'reference-only enlarged global layout crop with clamped right-edge guidance beyond map bounds','sourceBox':box,'globalBox':global_box,'pixels':[1254,1254],'allowedInFinal':False,'countsAsHDArt':False,'boundaryPolicy':border})
 print(json.dumps(plan))
if __name__=='__main__':main()
