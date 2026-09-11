from pathlib import Path
import json, hashlib
from datetime import datetime, timezone

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
items=json.loads((OUT/'inventory.json').read_text(encoding='utf-8'))
reference=ROOT/'docs/references/ui-style-20260910.png'
direction_notes={
 'east':'右向侧身，金发带、玉绿背心、米白衣裤、手持太极葫芦和短红穗延续参考角色。',
 'west':'左向侧身，金发带、玉绿背心、米白衣裤与手持太极葫芦延续参考角色。',
 'north':'背向，金发带与玉绿金边后襟保持同一角色材质；短腿和步态形变仍为Q版。',
 'south':'正面，圆脸大眼、金发带、玉绿米白衣装和手持葫芦与参考一致。',
 'northeast':'右后斜向，背部绿金纹样、米白短腿与金发带保持统一；红穗为正常配饰。',
 'northwest':'左后斜向，绿金后襟、米白衣裤与金发带保持统一，画法未跳出参考体系。',
 'southeast':'右前斜向，圆脸大眼、绿金衣装、米白裤与葫芦同属参考道童。',
 'southwest':'左前斜向，短身短肢、暖金发带、绿金衣装和葫芦均与参考一致。'
}
review=[]
for i,r in enumerate(items):
    current=hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()
    base={k:r[k] for k in ['path','sha256','size']}
    base['sha256_at_completion']=current
    base['source_unchanged_during_review']=current==r['sha256']
    base['style_status']='符合当前参考体系，可保留原画'
    base['visual_review']='本次实际查看完整轮廓联系表，并查看该文件独立原像素3倍浅色/深色背景边缘截图。'
    if i<32:
        direction=Path(r['path']).stem.split('_frame_')[0]
        base['style_observation']=direction_notes[direction]
        base['quality_status']='局部抠图边缘待修'
        base['quality_severity']='medium'
        base['quality_observation']='该帧发梢轮廓在浅底和深玉绿底均有可见品红细边与零星突出像素。只确认本帧已查看的发梢区域；不把红色流苏、暖金反光判为污染。'
        base['evidence']=[{'path':f'walk-{i//8+1:02d}.jpg','cell':i%8+1,'kind':'整张轮廓与风格实看'}, {'path':f'edges-{i//8+1:02d}.png','cell':i%8+1,'crop_xyxy':r['edge_crop'],'scale':3,'resampling':'nearest','backgrounds':['#f1eedf','#172a25'],'kind':'该帧独立发梢边缘实看'}]
    else:
        j=i-32
        styles=['狐团团为圆脸幼狐，米白毛、金发带、绿色披肩与太极葫芦吻合道家Q版，狐尾青绿渐染为设计色。','符小虎为短身幼虎，暖橙黑纹毛色、玉绿披肩、暖金符纸与太极坠饰符合参考材质，虎纹是物种差异。','云啾啾为大头幼鹤，米白羽毛、青绿翅羽、太极坠饰与软云座统一；应保留幼鸟形态。','灵月九尾狐保持狐吻、尖耳、修长四肢及九尾；大面积淡紫冷白毛色与参考狐一致，不能因颜色阈值去掉淡紫毛。']
        base['style_observation']=styles[j]
        base['quality_status']='局部极细残色，可在精修时处理' if j<3 else '毛边局部修整'
        base['quality_severity']='low'
        quality=['腹部下缘可见零星很细粉色像素，缩略整体未见明显色圈；红流苏为正常装饰，不列为风格问题。','脚底下缘和颈部毛披肩交界有零星极细紫色像素，整体无明显脏边；橙色毛、粉鼻和金饰均为正常配色。','腹部与腿间、羽尖内隙有极细粉紫边，缩略图不突出；红冠、暖黄鸟喙与淡绿云座为正常配色。','所查看的两处尾毛内隙，外缘可见比内部冷紫毛更粉的细线和阶梯状细毛。属于局部边缘质量；大面积淡紫毛色、白毛亮部本身不据此判错。']
        base['quality_observation']=quality[j]
        crops=r['edge_crops'][:1] if j==0 else r['edge_crops']
        base['evidence']=[{'path':'pets.jpg','cell':j+1,'kind':'整张轮廓与风格实看'}]+[{'path':'edges-05.png','cell':j*2+k+1,'crop_xyxy':box,'scale':3,'resampling':'nearest','backgrounds':['#f1eedf','#172a25'],'kind':'原像素局部浅深底实看；已补以无损PNG显示核验'} for k,box in enumerate(crops)]
    review.append(base)
out={'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),'reference':{'path':reference.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(reference.read_bytes()).hexdigest()},'scope':'character_move_8dir 全部32帧 + 当前正式4只宠物透明PNG，合计36张。静态视觉与局部透明边缘复核，不包含动画播放或客户端接入验收。','source_art_modified':False,'method':'先分别显示全部36张完整轮廓，再分别显示32张独立发梢原像素3倍浅/深底截图及4只宠物局部截图。颜色阈值只定位候选区域，所有判断来自实际查看。','count':len(review),'unique_paths':len({r['path'] for r in review}),'unchanged_at_completion':sum(r['source_unchanged_during_review'] for r in review),'records':review}
(OUT/'review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:out[k] for k in ['count','unique_paths','unchanged_at_completion','source_art_modified']},ensure_ascii=False))
