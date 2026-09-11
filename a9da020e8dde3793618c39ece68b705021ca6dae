"""Record the root reviewer's manually observed findings from all 16 contact pages."""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
d=json.loads((OUT/'inventory.json').read_text(encoding='utf-8'))
rows=[]
heavy={189,190,192,193,194,195,196,198,203,204,205,206,208,209,212,213,221,222,224,225,226,227,241,247,248,249,262,264,265,268,275,276}
small_bright={187,191,197,223,232,233,244,250,*range(251,261),271,272,273}
screens={280,281,282,283,284,286,287,289,290}
for r in d['records']:
    if r['owner']!='client_designs' or r['representative']!=r['id']:continue
    n=int(r['id'][1:]); verdict='match'; tags=[]
    reason='已在联系表逐项查看：造型、手绘层次与所属家族一致，未见明显异风格。'
    action='保留；不因题材配色不同而重绘。'
    if 41<=n<=62:
        reason='职业人物保持大头短身、圆眼和手绘服饰；冰蓝、火红、紫色属于职业主题，不能据此判为风格错误。'
    elif 63<=n<=186:
        reason='物件图标采用一致深玉底、暖金边、米白材质、云纹与红穗；道具雕刻和金属高光符合物件用途。'
    if n in heavy:
        verdict='deviates';tags=['ui-material','ui-family-shape']
        reason='相较已确认选角参考，绿/米白表面的大理石云纹更强、两端金色云饰更厚；页签/列表/搜索/卡片采用重复按钮端帽，失去原稿的细框和用途差异。'
        action='从同一选角参考按按钮、页签、列表、输入框、卡片分别重做无字母件；保留尺寸与九宫格约定。'
    elif n in small_bright:
        verdict='minor';tags=['ui-highlight']
        reason='符号和圆润道家造型连贯；局部绿玉及金属高光比参考更鲜亮。小型功能图标可保留，优先级低于面板与横条。'
        action='在统一UI母件时轻微收敛高光，保留符号辨识度。'
    elif n in {207,228,238,246}:
        verdict='minor';tags=['ui-frame']
        reason='米白底板和描金角饰大体匹配；绿框与内纸面的明亮黄绿倾向略强，且线框较硬。'
        action='随整套UI统一纸色、绿框亮度和金线宽度。'
    elif n in screens:
        verdict='deviates';tags=['ui-material','screenshot-evidence']
        reason='截图中可见v7亮绿纹理和重复云纹横条占据页签、列表、卡片等位置；说明差异已进入这份界面验收画面。'
        action='修正组件源图后重新导出并拍摄对应页面；截图只作问题证据，本次未验证当前客户端正在使用的版本。'
    elif n==291:
        verdict='deviates';tags=['legacy-result-panel','screenshot-evidence']
        reason='胜利界面为大面积深棕木纹板、均匀金线和通用薄荷渐变按钮，缺少已确认界面的米白纸面、深玉标题、局部云饰。'
        action='将结算窗口及返回按钮纳入同套玉绿米白UI重制；核对实际客户端资源来源。'
    elif n in {1,2,3,4,294,295,310}:
        verdict='historical';tags=['old-design','ui-material']
        reason='旧属性预览沿用亮绿厚边v7组件，内部原生表单偏平；已存在v2-painted更贴近选角参考的稿件。'
        action='作为旧版本保留；后续实现以v2-painted为皮肤目标，不继续传播旧皮肤。'
    elif n==312:
        verdict='historical';tags=['superseded-reference']
        reason='UI皮肤接近参考，但此图为去除相性页签前的修订版本；当前人物效果稿是01-character-ui-no-affinity.png。'
        action='保留追溯，不作为当前交付入口。'
    elif n in {314,315}:
        verdict='historical';tags=['layout-only-reference']
        reason='外部旧游戏截图用于信息布局参考；皮肤并非本项目目标，不列为待重绘项目资产。'
        action='保持布局参考身份。'
    elif n==313:
        verdict='minor';tags=['pet-portrait-identity']
        reason='面板深玉绿、米白、细金边与局部云饰接近参考；云啾啾头像为黑颈红顶长尖喙成年鹤，与已交付圆头短颈黄喙幼鹤形象不一致。'
        action='保留UI结构和皮肤，用已确认宠物透明图制作头像；头像局部修正。'
    elif n in {201}:
        verdict='technical';tags=['overlay']
        reason='透明云气叠加层；无底板属功能设计，不按缺背景或低饱和误判。';action='保留透明图层用途。'
    elif n in {292,293}:
        verdict='technical';tags=['review-sheet']
        reason='素材总览或抠图检查图，仅用于审查；其中正式素材已经单独检查。';action='保留审查记录。'
    rows.append({'id':r['id'],'verdict':verdict,'reason':reason,'action':action,'issue_tags':tags})
def path(n):return next(r['path'] for r in d['records'] if r['id']==f'A{n:04d}')
findings=[
 {'title':'客户端横条皮肤偏离已确认选角稿','severity':'high','paths':[path(n) for n in [189,192,193,198,204,222,248,281]],'evidence':'已实看所有client_designs联系表，并放大02-server-native.png：绿色玉纹偏亮、金色端帽过厚，页签/列表/卡片共用按钮形态。','action':'以深玉绿薄框的已确认选角稿重新分别建立各用途无字母件，随后统一派生。'},
 {'title':'结算截图仍呈现另一套深棕木纹UI','severity':'high','paths':[path(291)],'evidence':'放大截图可见深棕木板、统一金边及浅绿通用按钮，与米白纸面和深玉标题参考差异明显。','action':'结算窗口和按钮纳入同一皮肤家族；实际运行引用需另核验。'},
 {'title':'旧属性预览仍传播v7亮绿厚边皮肤','severity':'medium','paths':[path(n) for n in [294,295,1]],'evidence':'旧预览与v2-painted同时存在；前者亮绿框、云纹胶囊按钮和平面表单，后者深玉细金框更接近用户参考。','action':'标清版本，以v2-painted为属性UI皮肤目标。'},
 {'title':'宝宝新稿中的云啾啾头像身份不一致','severity':'medium','paths':[path(313),path(237)],'evidence':'新稿头像是成年黑颈尖喙红顶鹤；正式透明宝宝是短颈圆眼黄喙幼鹤。界面皮肤本身接近参考。','action':'仅重取已确认宠物头像，避免整张面板重绘。'}
]
result={'owner':'client_designs','reviewed_pages':[f'contacts/client_designs/{i:02d}.jpg' for i in range(1,17)],'records':rows,'findings':findings,'notes':['全部246个独立像素内容均在联系表实际查看；关键界面另放大核对。像素相同别名由汇总脚本关联。','同步清单提及的9个category_idle/panel旧客户端路径在本库prepared目录未找到，不能从清单直接认定已看到这些旧图或当前页面仍在使用。','UI/UX Pro Max检索未返回可验证的游戏风格一致性条目；本次采用技能通用一致性原则，具体判断依据项目参考图，不使用通用网页配色模板。']}
(OUT/'client_designs-findings.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(rows))
