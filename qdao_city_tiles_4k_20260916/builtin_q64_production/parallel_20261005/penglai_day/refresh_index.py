"""Refresh only this map's production inventory; never claims runtime acceptance."""
import production as p
from PIL import Image, ImageDraw
import os,time,uuid
b=p.ROOT

def save_preview(image,target):
    temp=target.with_name(target.stem+'.write-'+uuid.uuid4().hex+'.png')
    image.save(temp)
    for attempt in range(4):
        try:
            os.replace(temp,target)
            return
        except OSError:
            if attempt==3: raise
            time.sleep(.5)

def rel(path):
    path=p.Path(path)
    return path.relative_to(b).as_posix() if path.is_relative_to(b) else path.as_posix()

def main():
    plan=p.read(p.H['plan']['file'])
    current={x['tile']:{'file':x['file'],'sha256':x['sha256'],'status':'inherited_candidate'} for x in p.H['baselineCandidates']}
    if (b/'tiles/current/integration.json').exists():
        integration=p.read(b/'tiles/current/integration.json')
        for key,tile in [('c12','r09_c12'),('c13','r09_c13')]:
            current[tile]={**integration[key],'status':integration['status']}
    active={}
    for folder in sorted(b.glob('r??_c??')):
        if not folder.is_dir(): continue
        progress=p.read(folder/'progress.json') if (folder/'progress.json').exists() else {}
        active[folder.name]={'nativePatches':len(list((folder/'native').glob('p??.png'))),'targetPatches':16,'stage':progress.get('stage','preparing')}
        candidate=folder/'tiles'/f'{folder.name}-candidate.png'
        if candidate.exists(): current[folder.name]={'file':str(candidate),'sha256':p.sha(candidate),'status':'full_pixels_seam_qa_pending'}
    # Explicit reviewed integrations take precedence over initial assembly files.
    overrides_path=b/'tiles/current/current-overrides.json'
    if overrides_path.exists():
        overrides=p.read(overrides_path)
        for tile,item in overrides['tiles'].items():
            assert p.sha(item['file'])==item['sha256'],f'Current candidate changed without index update: {tile}'
            assert Image.open(item['file']).size==(4096,4096),tile
            current[tile]=item
    generated=[]
    for record in sorted(b.rglob('*.generation.json')):
        item=p.read(record)
        if item.get('route')=='builtin': generated.append({'file':item.get('file'),'sha256':item.get('sha256'),'record':str(record),'nativePixels':[item.get('width'),item.get('height')],'role':item.get('role'),'actualModel':item.get('actualModel'),'actualQuality':item.get('actualQuality')})
    tiles=[]
    for tile in plan['tiles']:
        entry={k:tile[k] for k in ['id','row','column','finalPixelRect','worldRect']}
        entry.update(current.get(tile['id'],{'file':None,'sha256':None,'status':'drawing' if tile['id'] in active else 'missing'}));entry['formalAccepted']=False;tiles.append(entry)
    common={'appearance':'penglai_day','updatedAt':p.stamp(),'formalAccepted':0,'wholeCityComplete':False,'clientAccepted':False}
    p.write(b/'tile-manifest.json',{**common,'kind':'production_inventory_not_runtime_manifest','wholeCityPixels':[65536,65536],'grid':[16,16],'tilePixels':[4096,4096],'availableFullPixelCandidates':len(current),'missingFullPixelTiles':256-len(current),'tiles':tiles})
    p.write(b/'asset-index.json',{**common,'title':'06 仙岛日景地图','currentCandidates':current,'activeTiles':active,'generatedImages':generated,'tileManifest':'tile-manifest.json'})
    count=len(list((b/'native').glob('p??.png')))+sum(x['nativePatches'] for x in active.values())
    p.write(b/'progress.json',{**common,'targetTiles':256,'inheritedCompleteCandidateTiles':3,'newCompleteCandidateTiles':len(current)-3,'availableFullPixelCandidateTiles':len(current),'missingFullPixelTiles':256-len(current),'newNativeDetailPatches':count,'activeTiles':active,'status':'native_expansion_and_seam_qa'})
    p.write(b/'current-work.json',{'updatedAt':p.stamp(),'stage':'native_expansion_and_seam_qa','stableR09Candidate':current.get('r09_c13'),'activeTiles':active,'next':'Finish native detail patches and seam QA in active tiles, then expand into adjacent missing tiles. Whole-city and runtime acceptance pending.','outputDirectory':str(b),'refreshScript':'refresh_index.py','noDuplicateGeneration':'Check records and prior tool outputs before repeating interrupted calls.'})
    layout=Image.open(p.H['layout']['file']).convert('RGB');canvas=Image.blend(layout,Image.new('RGB',layout.size,(30,36,42)),.56);draw=ImageDraw.Draw(canvas)
    for i in range(17):
        q=round(i*1254/16);draw.line((q,0,q,1253),fill=(95,105,108));draw.line((0,q,1253,q),fill=(95,105,108))
    for tile in tiles:
        if tile['id'] not in current and tile['id'] not in active: continue
        r,c=tile['row'],tile['column'];box=(round((c-1)*1254/16),round((r-1)*1254/16),round(c*1254/16),round(r*1254/16))
        draw.rectangle(box,outline=(80,227,228) if tile['id'] in current else (160,226,113),width=4);draw.text((box[0]+4,box[1]+6),f'{r:02}-{c:02}',fill='white',font_size=16)
    draw.rectangle((8,8,700,90),fill=(25,33,35));draw.text((20,17),'LAYOUT REFERENCE / NOT FULL HD ART',fill='white',font_size=23);draw.text((20,53),f'{len(current)}/256 full-pixel candidates | Formal acceptance: 0',fill='white',font_size=18)
    out=b/'coverage-preview.png';canvas.save(out);p.derived(out,[p.H['layout']['file']],{'method':'layout-only coverage overlay','notProductionArt':True})
    lines=['# 06 仙岛日景地图制作中','','内部资产 ID：`penglai_day`。仅在本目录继续制作，旧来源只读。','',f'目标为65536×65536、16×16共256张4096×4096。目前有 **{len(current)}张完整像素候选**，尚缺{256-len(current)}张完整像素图块。正式验收0张；整城和客户端验收尚未完成。','','## 当前图块','','| 图块 | 当前图片 | 检查状态 |','|---|---|---|']
    for tile,item in sorted(current.items()):
        status='局部图像及接缝已复查；其余相邻块待完成' if item['status']=='local_candidate_visual_review_passed' else ('继承候选，已核对来源' if item['status']=='inherited_candidate' else '完整像素，接缝验收处理中')
        lines.append(f'| {tile} | [4096×4096 PNG]({rel(item["file"])}) | {status} |')
    lines+=['','r09_c13 已合并内部修缝、两处AI木纹修补及c12共享边，轮廓微阶已修复。实际像素来源、早期配准和色彩场保留完整记录，不将拼合图标成单次原生4K。','','## 正在补齐','']
    for tile,item in active.items(): lines.append(f'- {tile}：{item["nativePatches"]}/16张原生细节片；{item["stage"]}。')
    lines+=['','## 文件与检查入口','','- [当前区域预览](current-region-preview.png) / [全城覆盖位置](coverage-preview.png)','- [256块清单](tile-manifest.json) / [逐图来源索引](asset-index.json)','- [进度](progress.json) / [继续制作位置](current-work.json)','- [r09整合复查](qa/integrated-r09/root-review.json)','- [导航与日景/节庆约束](evidence/structure-navigation-review.json)','','## 生图与保留规则','','使用宿主内置image_gen。所有生图和AI编辑均有独立记录；配置目标与实际参数分开，工具未披露的型号和质量为未确认。实际提示词、参考图角色、工具来源、原生尺寸和SHA可从逐图索引查询。结构稿及低清布局仅用于参考，未作为高清成品放大。','','当前用于邻块衔接、尚未导出最终成品的唯一在制稿及修补依赖暂留。成品与引用核验完成后，按用户规则清除拒稿、回退图和中间图，保留来源文字证据。','','刷新本索引使用 `refresh_index.py`。']
    (b/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    rows=[int(t[1:3]) for t in current];cols=[int(t[5:7]) for t in current]
    r0,r1=min(rows),max(rows);c0,c1=min(cols),max(cols);cell=min(400,2000//(c1-c0+1))
    region=Image.new('RGB',(cell*(c1-c0+1),54+cell*(r1-r0+1)),(32,41,44));dr=ImageDraw.Draw(region)
    dr.text((12,10),'PENGLAI DAY - CURRENT CANDIDATES / PREVIEW ONLY',fill='white',font_size=24)
    for tile,item in current.items():
        row=int(tile[1:3]);col=int(tile[5:7])
        if r0<=row<=r1 and c0<=col<=c1:
            x=(col-c0)*cell;y=54+(row-r0)*cell
            region.paste(Image.open(item['file']).convert('RGB').resize((cell,cell),Image.Resampling.LANCZOS),(x,y))
    save_preview(region,b/'current-region-preview.png')
    p.derived(b/'current-region-preview.png',[v['file'] for v in current.values()],{'method':'downscale-only spatial overview; blank cells have no complete candidate','rows':[r0,r1],'columns':[c0,c1],'productionArt':False,'notNativeQAEvidence':True})
    print({'fullPixelCandidates':len(current),'nativeDetailPatches':count,'activeTiles':active,'formalAccepted':0})

if __name__=='__main__': main()
