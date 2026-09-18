from pathlib import Path
import json,hashlib
from PIL import Image
P=Path(r'E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production');R=P.parent
for v,ver in [('lanxian_day','v4'),('lanxian_spring','v5')]:
 d=P/v/'r08_c08'
 for sub in ('guides','prompts','native','output','qa','regional-reference'): (d/sub).mkdir(parents=True,exist_ok=True)
 prod=json.loads((R/f'q64_production_plans/{v}.json').read_text(encoding='utf-8-sig'));entry=next(t for t in prod['tiles'] if t['id']=='r08_c08')
 p=json.loads((P/v/'r08_c07/plan.json').read_text());p.update({'sampleTile':{'id':'r08_c08','row':8,'column':8,'worldRect':entry['worldRect']},'samplePixelRectInWholeCity':[28672,28672,32768,32768],'sampleSourceCrop':[548.625,548.625,627,627],'status':'regional_reference_pending','patches':[]})
 p['leftNeighborBoundary']={'tile':'r08_c07','file':str(P/v/f'pair_r08_c06_c07/output/r08_c07-extended-context-{ver}.png'),'acceptedCoreWidth':115,'unacceptedOuterContextWidth':115}
 p['directAttemptRole']='No new native 4K-size claim. Regional reference only followed by 16 real native details.'
 p['guidePreparation']={'status':'pending','motherCoversExpanded4326':True,'guideOnly':True};p['geometryAuthority']='lanxian_day r08_c08; spring uses final day detail geometry as guides'
 for key in ('directAttemptGuide','directAttemptActualPixels','sharedGeometrySource'):p.pop(key,None)
 (d/'plan.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
 assembly=(P/v/'r08_c07/assemble_builtin.py').read_text().replace('r08_c07','r08_c08');(d/'assemble_builtin.py').write_text(assembly)
 if v=='lanxian_day':
  im=Image.open(R/'builtin_q64_all_city_references/lanxian_day/map-native-layout-reference.png').convert('RGB');s=im.width/65536
  box=[(28672-115)*s,(28672-115)*s,(32768+115)*s,(32768+115)*s]
  canvas=im.transform((4326,4326),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC)
  left=Image.open(p['leftNeighborBoundary']['file']).convert('RGB');canvas.paste(left.crop((4096,0,4211,4326)),(0,0))
  canvas.save(d/'guides/preliminary-layout-canvas-only.png')
  canvas.resize((1254,1254),Image.Resampling.BICUBIC).save(d/'guides/regional.layout-only.png')
 print(v,entry['finalPixelRect'],entry['worldRect'])
