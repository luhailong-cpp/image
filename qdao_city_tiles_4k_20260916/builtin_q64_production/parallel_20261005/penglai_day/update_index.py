import production as p
from PIL import Image,ImageDraw
b=p.ROOT
def main():
    recs=[]
    for f in sorted((b/'native').glob('*.png.generation.json')):
        d=p.read(f);recs.append({'file':d['file'],'sha256':d['sha256'],'record':str(f),'actualPixels':[d['width'],d['height']],'actualModel':d['actualModel'],'actualQuality':d['actualQuality']})
    p.write(b/'asset-index.json',{'appearance':'penglai_day','title':'06 仙岛日景地图','updatedAt':p.stamp(),'wholeCityPixels':[65536,65536],'tilePixels':[4096,4096],'grid':[16,16],'baselineCandidates':p.H['baselineCandidates'],'newNativeDetails':recs,'newFullPixelCandidate':{'file':str(b/'tiles/r09_c13-raw-candidate.png'),'globalPixelRectXYWH':[49152,32768,4096,4096],'pixels':[4096,4096],'status':'pending_seam_repairs','formalAccepted':False},'wholeCityComplete':False,'clientAccepted':False})
    layout=Image.open(p.H['layout']['file']).convert('RGB');canvas=Image.blend(layout,Image.new('RGB',layout.size,(30,36,42)),.56);draw=ImageDraw.Draw(canvas)
    for i in range(17):
        q=round(i*1254/16);draw.line((q,0,q,1253),fill=(95,105,108));draw.line((0,q,1253,q),fill=(95,105,108))
    for c in [10,11,12,13]:
        box=(round((c-1)*1254/16),round(8*1254/16),round(c*1254/16),round(9*1254/16));draw.rectangle(box,outline=(255,204,82) if c<13 else (80,227,228),width=4);draw.text((box[0]+4,box[1]+6),f'09-{c}',fill='white',font_size=16)
    box=(round(11*1254/16),round(9*1254/16),round(12*1254/16),round(10*1254/16));draw.rectangle(box,outline=(160,226,113),width=4);draw.text((box[0]+4,box[1]+6),'10-12',fill='white',font_size=16)
    draw.rectangle((8,8,650,90),fill=(25,33,35));draw.text((20,17),'LAYOUT REFERENCE / NOT FULL HD ART',fill='white',font_size=23);draw.text((20,53),'Gold: 3 inherited | Cyan: QA pending | Green: drawing',fill='white',font_size=18)
    out=b/'coverage-preview.png';canvas.save(out);p.derived(out,[p.H['layout']['file']],{'method':'layout-only coverage overlay','notProductionArt':True})
    lines=['# 06 仙岛日景地图制作中','', '内部资产 ID：`penglai_day`。新成果仅写入本目录，旧来源只读。','', '目标：65536×65536；16×16，共256张4096×4096。整城、正式验收及客户端验收均未完成。','', '## 当前像素与检查范围','', '- 已核对并复用旧 r09_c10、r09_c11、r09_c12 三张候选，SHA与handoff一致。','- 新 r09_c13 已有16张1254×1254原生细节片，按1024核心、115外围上下文拼成完整4K候选；无成品放大。','- 原始候选尚有内部色差和 c12 共边几何问题；独立修补与校正工作位于 `repairs/`，未经检查不升级正式计数。','- r10_c12 正在独立子目录连续向南扩展。','- 原生来源型号/质量由宿主管理，工具未披露；配置目标 gpt-image-2.5-sunburst/max 与实际提交/返回分别记录。','', '## 入口','', '- [逐图索引](asset-index.json)','- [进度](progress.json) / [当前工作](current-work.json)','- [当前r09_c13预览](current-preview.png) / [全城覆盖位置示意](coverage-preview.png)','- [完整像素候选](tiles/r09_c13-raw-candidate.png)（未验收，不是正式成品）','- [内部校正](repairs/internal/candidate-record.json) / [共边修补](repairs/left-edge/repair-status.json)','- [导航与日景/节庆约束](evidence/structure-navigation-review.json)','', '## 原生图与逐图记录','', '| 图 | 记录 |','|---|---|']
    for r in recs:
        name=p.Path(r['file']).name;lines.append(f'| [{name}](native/{name}) | [生成记录](native/{name}.generation.json) |')
    lines+=['', '所有提示词位于 `prompts/`；内置结果路径、哈希、参考图角色及提交参数见逐图记录。结构稿和guides仅为布局参考，不能计作高清成品。','', '当前在制图、修补依赖和唯一像素来源暂留；确认最终导出和当前引用完整后按用户规则清理原图、拒稿和中间图片，文字来源证据保留。']
    (b/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('index updated',len(recs))
if __name__=='__main__':main()
