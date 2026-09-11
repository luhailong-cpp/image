from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
d=json.loads((OUT/'supplement.json').read_text(encoding='utf-8'))
records=[]
for r in d['records']:
    if r['representative']!=r['id']:continue
    n=int(r['id'][1:]);verdict='match';tags=[]
    if n>=48:continue  # Later additions are reviewed separately.
    reason='新增属性切片保持深玉绿、米白、细金框；相较旧v7亮玉横条更接近用户选角参考。'
    action='保留造型和配色，接入时按实际尺寸检查。'
    if n==1 or n>=34:
        verdict='technical';tags=['review-sheet']
        reason='已查看的素材/曝光审查联系表，属于既有图像的审查排布，不是新增美术风格。';action='保留审查用途。'
    elif n in {2,3,4,23,25,30}:
        verdict='minor';tags=['cutout-reconstruction','banding']
        reason='配色及边饰接近原稿，但去字区域出现横向平涂色带/拉伸纹理，手绘云纹连续性有所丢失；主按钮和空白步进按钮尤明显。'
        action='从无字母件恢复连续手绘底纹；避免用窄条反复拉伸填补文字区域。'
    elif n in {10,11}:
        verdict='minor';tags=['cutout-reconstruction','border-remnant']
        reason='卡片左侧原头像区域留下上下两条截断描金线，内区纸色/绿色接补可见；属于去字去头像后的重建痕迹。'
        action='重建完整卡片底板和独立头像框，修齐内外边线，随后再切。'
    elif n==5:
        verdict='minor';tags=['cutout-contamination']
        reason='关闭按钮下方同时带出了矩形绿底和相邻面板金边；如果作为独立按钮贴到其他面板，会出现背景块。'
        action='明确是面板角饰还是独立按钮；独立用法需只保留圆钮、云饰、吊穗。'
    elif n==12:
        verdict='minor';tags=['cutout-reconstruction','border-remnant']
        reason='头像框四边厚度与角接不均，右/下边出现深绿直线块，和原稿细金框不够连续。'
        action='整理完整细金头像框，保持四边和角饰一致。'
    elif n==15:
        verdict='minor';tags=['avatar-framing']
        reason='灵玥头像大半面积是尾巴，脸位于左下且远小于另外三只宝宝；身份正确但头像构图与同组不一致。'
        action='按眼睛/面部中心重新取头像，统一四只宠物头部视觉尺寸，不更改灵玥形象。'
    elif n in {28,29}:
        verdict='technical';tags=['baked-text-background']
        reason='标题字图带完整不透明深绿矩形底；与标题板重叠时可能出现色块，不能当透明文字层使用。'
        action='提取透明文字或用客户端字体重排；将字与绿色标题皮肤分开。'
    elif n==16:
        reason='已从正式幼鹤素材取像，大圆头、黄喙和短颈正确；已修复旧宝宝整屏图里成年鹤头像的身份偏差。'
        action='保留此头像；旧整屏稿仍需同步这一身份修订。'
    records.append({'id':r['id'],'verdict':verdict,'reason':reason,'action':action,'issue_tags':tags})
byid={r['id']:r for r in d['records']}
def paths(*ns):return [byid[f'X{n:04d}']['path'] for n in ns]
out={'owner':'supplement','reviewed_pages':[p['path'] for p in d['pages'][:3]],'records':records,'findings':[
 {'title':'新属性切片画风更接近，但去字修补痕迹可见','severity':'medium','paths':paths(2,3,4,10,11,23,25,30),'evidence':'全看30个单件切片：主按钮出现横向绿色色带，宠物卡左侧留有中断的描金内框，部分无字底板缺少连续手绘纹理。','action':'保留深玉细金方向，局部修复无字母件的纹理和完整边线。'},
 {'title':'新属性切片的独立层与头像取景需调整','severity':'medium','paths':paths(5,12,15,28,29),'evidence':'关闭按钮带出邻接面板底；头像框边线不齐；灵玥头像脸过小；两个标题字图带不透明绿底。','action':'清理独立层边界、统一头像取景，字图改为透明或客户端文字。'}
],'notes':['本补充覆盖扫描期间新增的33个属性资源文件及14张曝光审查联系表。两个sources源图与已审阅人物/宝宝原稿像素相同，按像素关联。','新增云啾啾头像已正确采用幼鹤形象；旧整屏头像问题不再继承到此切片。']}
(OUT/'supplement-findings.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(records))
