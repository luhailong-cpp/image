from pathlib import Path
import json,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
    p=ROOT/p
    assert p.resolve().is_relative_to(ROOT)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
frames=[]
notes={
'E':{
1:('近侧右手握单盘、远左手三卡边缘可辨，无明显多手或断指；双靴完整。','预备双膝轻屈；01到02脚底上跳、头身侧向后移，不能用最低像素贴地掩盖。'),
2:('近右盘远左三卡，抓握和腕部连接可读；两靴分离。','后仰/低重心有表达，但与03的身体和腿姿态过于接近，初受力与峰值递进不清。'),
3:('近右盘远左三卡，双靴和膝踝有明确体积；未见额外肢体。','名义峰值相较02后仰并未清楚增强，几乎是近似姿态；需重做峰值骨架。'),
4:('持物归属正确，右握柄左持三卡；双靴完整。','从03到04头部与躯干明显长高/右移，支撑脚注册变化，缓冲回弹不够连贯。'),
5:('近右手已收回胸前握盘、远左手三卡，手部可读；双靴完整。','盘位从04到05向左下收，再于06升回面前，收势有额外折返；两处耳旁星穗比邻帧增加，需核实饰物。'),
6:('近右盘远左三卡，双靴完整且无粘脚；恢复表情平静。','06到01脚间距与头部/盘位仍变化，和原idle的接续尚未验收。')
},
'W':{
1:('近侧左手恰三张卡、远右手握盘，朝左单眼，双靴分开。','预备候选；脚底较本段93%虚拟地面偏低，01到02位置变化明显。'),
2:('v2已修回朝左单眼，近左三卡、远右星盘；双靴鞋跟鞋尖可读。','早期受力幅度比v1减小，但手盘与骨盆相对01向右移、双脚向左移，固定支撑关系仍需修改。'),
3:('朝左单眼、近左三卡远右盘，恰两靴且轮廓完整。','峰值帧两脚相对02整体左移，尤其前靴位移明显；身体更像向前跨步而不是被来自左侧的力推向右侧。需要以02已锁定脚位重修峰值骨架。'),
4:('朝左单眼，近左三卡远右盘，双靴完整；盘位降低。','03到04前靴向右跳超过一个鞋长，后靴也右移；未给出腾空/迈步因果，不通过固定根点受击连续性。'),
5:('恢复闭口，近左三卡远右盘、双靴完整；头身与04较一致。','基于04编辑，恢复趋势可读；后方靴向内收约50原生像素，仍有轻度脚滑，不能算固定双脚通过。'),
6:('朝左单眼、左手恰三卡右手握盘、两靴完整；05到06脚位基本保持。','恢复微姿态相较05变化很小，肩颈略放松；06到01脚距、手盘高度和头部注册仍有跳变，未通过完整循环或idle转接。')
}}
for d in ('E','W'):
    for i in range(1,7):
        version=2 if (d=='E' and i==5) or (d=='W' and i==2) else 1
        path=ROOT/f'generation/hit/{d}/{i:02d}-v{version}.png'
        if not path.exists(): continue
        recpath=Path(str(path)+'.generation.json')
        meta=json.loads(recpath.read_text(encoding='utf-8-sig'))
        im=Image.open(path); im.load()
        alpha=im.getchannel('A')
        hist=alpha.histogram()
        f={'direction':d,'frame':i,'source':path.relative_to(ROOT).as_posix(),'generationRecord':recpath.relative_to(ROOT).as_posix(),'sha256':sha(path),'staticAnatomy':notes[d][i][0],'sequenceFinding':notes[d][i][1],'staticReview':'anatomy_readable_candidate','sequenceReview':'needs_revision','technical':{'nativeSize':list(im.size),'mode':im.mode,'alphaExtrema':list(alpha.getextrema()),'transparentPixelFraction':hist[0]/(im.width*im.height),'alpha128BoundsForDiagnosisOnly':list(alpha.point(lambda x:255 if x>=128 else 0).getbbox()),'sourceRecordHashMatches':meta['sha256']==sha(path),'modelAndQualityNotConfirmed':meta['actualModel'] is None and meta['actualQuality'] is None}}
        frames.append(f)
save('provenance/hit-final-review.json',{
'schema':1,'character':ROOT.name,'reviewedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),
'scope':'hit E6+W6 strict anatomy/proportions/phase review; original PNGs read only',
'method':'实际查看角色画像、E/W原idle、designs风格、12张原生图及E顺序接触表。手脚可读性与序列相位分开判断；未以数量或SHA差异作为通过依据。未执行客户端动态验收。',
'status':'needs_revision','expectedFrames':12,'reviewedFrameCount':len(frames),
'staticAnatomyCandidates':len(frames),'completeActionAccepted':False,'dynamicAcceptance':False,'clientIntegrated':False,
'timing':{'frameMs':40,'segmentMs':240},'frames':frames,
'priorityFixes':[
{'priority':1,'slots':['hit/W/02','hit/W/03','hit/W/04'],'reason':'支撑脚横向滑动及03峰值受力方向不明确；严格锁相机及同一双脚位置，重绘骨架变化，不能最低像素贴地或包围盒缩放伪修。'},
{'priority':1,'slots':['hit/E/02','hit/E/03'],'reason':'初受力与峰值过于相似，明确躯干后仰及膝髋压缩幅度递进。'},
{'priority':2,'slots':['hit/E/04','hit/E/05','hit/E/06','hit/W/05','hit/W/06'],'reason':'检查回弹/收势的头身、盘位、双脚注册和相位接续。'},
{'priority':2,'slots':['hit/E/*','hit/W/*'],'reason':'固定全局相机、比例与虚拟地面检查，制作正常40ms、慢速与逐帧预览后再动态验收；未在本次强行通过。'}],
'modelEvidence':'目标GPT Image2.5 Sunburst/max；内置实际model/quality未开放或返回，null保留，未将目标当实测。',
'cleanup':'本角色正式导出及当前引用尚未确认，因此保留当前在制源及文字证据，旧拒稿不进入选帧。'})

