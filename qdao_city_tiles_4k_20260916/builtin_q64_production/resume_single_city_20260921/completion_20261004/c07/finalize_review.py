"""Record this agent's completed native-pixel visual review (not an auto-pass)."""
from pathlib import Path
import datetime, hashlib, json
from PIL import Image

R = Path(__file__).resolve().parent
O = R / 'tone-candidate-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assembly = json.loads((O/'assembly.json').read_text(encoding='utf-8'))
returns = json.loads((O/'qa-returns/index.json').read_text(encoding='utf-8'))
assert sha(assembly['candidate']['file']) == assembly['candidate']['sha256'] == '1d2349396db310f1cae103c0c5f290b8217e8cb3a2b5bf63a16cab2f2c4f7d0c'
assert sha(assembly['source']['file']) == assembly['source']['sha256']
stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
notes = {
    ('x',1024): '象牙铺石、金色圆弧及下部框线跨缝连续；未见直立亮度割线、截断或双边。',
    ('x',2048): '斜向金边、象牙长框与灰蓝面板跨缝连续；此前中心错阶未重现，框线仍为单边。',
    ('x',3072): '上部雕刻及下部长框衔接连续；雕刻轮廓无十字色差，未见返回带造成的重影。',
    ('y',1024): '左侧铺石、中部金边和右侧雕刻/大石板连续；未见横向亮度台阶。',
    ('y',2048): '左侧长金线、中部框角及右侧石板边连续；暗面纹理均匀，无四象限色阶。',
    ('y',3072): '横向金色框底及右侧灰蓝、象牙长板连续；此前框线回接处无新增折边或双线。',
}
seams=[]
for axis in ('x','y'):
    for at in (1024,2048,3072):
        segments=[]
        for seg in range(4):
            stem=f'{axis}{at}-seg{seg+1}.png'
            core=O/'qa'/stem
            ret=O/'qa-returns'/stem
            assert Image.open(core).size == (1024,320)
            assert Image.open(ret).size == (1024,512)
            segments.append({'span':[seg*1024,(seg+1)*1024],'core':{'file':str(core),'sha256':sha(core)},'fullCorrectionAndReturn':{'file':str(ret),'sha256':sha(ret)},'actualViewedAtOriginalPixels':True,'resized':False,'losslessRotate90':axis=='x','visualResult':'pass'})
        seams.append({'axis':axis,'at':at,'span':[0,4096],'result':'pass','observation':notes[(axis,at)],'segments':segments})
junctions=[]
for y in (1024,2048,3072):
    for x in (1024,2048,3072):
        p=O/'qa'/f'junction-{x}-{y}.png'
        assert Image.open(p).size==(512,512)
        junctions.append({'center':[x,y],'cropLTRB':[x-256,y-256,x+256,y+256],'file':str(p),'sha256':sha(p),'actualViewedAtOriginalPixels':True,'resized':False,'visualResult':'pass','observation':'中心无可辨十字亮度阶差；经过的真实石缝、框线和雕刻保持连续，未见重复边缘。'})
review={'schemaVersion':1,'reviewedAtUtc':stamp,'reviewer':'Codex /root/audit_city','candidate':assembly['candidate'],'source':assembly['source'],'status':'internal_six_full_seams_nine_junctions_and_color_returns_pass','method':'Actual view_image(detail=original) inspection of 24 core seam crops (1024x320), 9 junction crops (512x512), and 24 full correction/return crops (1024x512). Vertical strips were losslessly rotated by 90 degrees; no QA crop was scaled. This records completed visual inspection, not an automatic inference from image dimensions or hashes.','reviewedNativeImages':57,'fullSeams':seams,'junctions':junctions,'correctionReturnReview':{'result':'pass','index':str(O/'qa-returns/index.json'),'coverage':'All six full-length +/-192-pixel correction bands plus 64 native pixels on each side. All four native edge tapers are included in the first/last segments.','observation':'所有渐变回接未见新色带、矩形边界或重影；无几何重采样。'},'mechanicalValidation':{'outsideAllCorrectionBandsUnchanged':returns['outsideAllCorrectionBandsUnchanged'],'outerBoundaryPixelsUnchanged':returns['outerBoundaryPixelsUnchanged'],'maxStoredChannelDifference':returns['maxStoredChannelDifference'],'maxAppliedFloatCorrection':assembly['actualMaxCorrection'],'changedPixels':returns['changedPixels'],'geometricResampling':False,'upsampledNative':False,'sourceFileUnchanged':True},'limits':['仅 r08_c07 内部接缝和本次修色回接验收通过。','四侧与相邻图块的最终组合尚需主任务核验；原四侧边界像素完整保留。','未据此宣称天墉整图、全部 7 套主城或客户端导航/加载验收完成。'],'formalAccepted':False,'globalSelectionChanged':False,'cleanupPerformed':False}
(O/'visual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
returns['visualReviewStatus']='passed_actual_view'
returns['visualReview']=str(O/'visual-review.json')
(O/'qa-returns/index.json').write_text(json.dumps(returns,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
latest={'schemaVersion':1,'updatedAtUtc':stamp,'city':'天墉节庆','coordinate':'r08_c07','candidate':assembly['candidate'],'localReview':str(O/'visual-review.json'),'assembly':str(O/'assembly.json'),'internalSeamsPassed':6,'internalJunctionsPassed':9,'correctionReturnsPassed':True,'externalNeighborReview':'pending_parent_integration','formalAccepted':False,'fullNativeAttempt':{'status':'rejected_dimensions_not_native4096','record':str(R/'full-native-attempt/rejection.json')},'preparedNotSubmitted':['v1024-top'],'cleanUpAllowedNow':False}
(R/'latest-candidate.json').write_text(json.dumps(latest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(R/'README.md').write_text('''# 天墉 r08_c07 本轮内部接缝完成记录

当前可接续候选为 `tone-candidate-v1/r08_c07.png`，原生 4096×4096，SHA-256 `1d2349396db310f1cae103c0c5f290b8217e8cb3a2b5bf63a16cab2f2c4f7d0c`。

从 continuation_20261004 的 candidate-v4 原像素出发，对旧 1024 拼接网格实施有限局部颜色匹配。只改 RGB 值，实际通道最大差值 8/255；不移动、缩放、模糊或重画纹理，四侧外边像素及全部修色带以外像素完全不变。

实际看完 57 张未缩放 QA：24 个整缝分段、9 个交点、24 个完整修色及回接分段。6 条 4096 全长内部缝和 9 个交点通过；回接未见新增矩形色差或双边。逐项证据见 `tone-candidate-v1/visual-review.json`，操作及来源见 `tone-candidate-v1/assembly.json`。

4096 整图内置生成探针实际只返回 1254×1254，已记录拒用且未放大。`v1024-top` 仅准备参考，未提交生成。最终候选本次机械修色未增加模型调用，AI 来源沿 candidate-v4 的逐图记录追溯。

四侧邻图组合仍由主任务核验，正式资源选择、全城状态和清理未改动。本目录未宣称全部主城完成。
''',encoding='utf-8')
print(json.dumps({'candidate':assembly['candidate'],'internalSeamsPassed':6,'junctionsPassed':9,'nativeViews':57,'review':str(O/'visual-review.json')},ensure_ascii=False))
