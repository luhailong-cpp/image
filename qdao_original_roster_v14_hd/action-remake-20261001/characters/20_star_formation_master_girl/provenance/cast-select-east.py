from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1]
mapping=['01-v2','02-v1','03-v1','04-v3','05-v2','06-v1','09-v1','05-v1','10-v1','08-v1','11-v1','12-v1','13-v1','14-v1','15-v1','16-v1']
frames=[]
for i,stem in enumerate(mapping,1):
 path='generation/cast/E/'+stem+'.png'
 rp=B/(path+'.generation.json');r=json.loads(rp.read_text(encoding='utf-8-sig'))
 r['review']={'status':'static_candidate','note':'已实看：三卡、单盘、双手双靴可辨；以选表帧号使用。相机/根锚点与完整动态衔接仍待验收。','dynamicAcceptance':False}
 if stem=='04-v3':r['review']['note']+=' 聚势重心与步幅较明显，需动态重点复核。'
 if stem=='15-v1':r['review']['note']+=' 流苏部分遮挡中间卡，三卡仍可数，动态复核。'
 rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 frames.append({'action':'cast','direction':'E','frame':f'{i:02d}','source':path,'generationRecord':path+'.generation.json','sha256':r['sha256'],'review':r['review']})
sel={'action':'cast','schemaVersion':2,'dynamicAcceptance':False,'frames':frames,'notes':['E/W分别独立绘制；未动态验收','E重排举盘高度相位，07-v1残色、01-v1卡遮挡、04-v1/v2多卡角拒用','每帧45ms，总720ms；E释放建议第10槽(原08-v1)'],'releaseFrames':{'E':'10'}}
(B/'cast-selection.json').write_text(json.dumps(sel,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
