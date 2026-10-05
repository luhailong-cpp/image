from extract_review import ROOT, VIDEO, frames, sheet
from PIL import Image
import json, hashlib

segments=[]
observations={
    'E':['344–367 连续段维持朝画面右的侧向，370 起才明显转向 NE；前后腿主要在画面左右的运动平面交替。','350–354 可观察前摆、脚向身体下方回落与承重附近的过渡；356–360 有下一次前后伸展及回收。短暂前伸不应等同于连续多帧把膝完全锁直。','前脚鞋尖的短暂轻微上翘与腿部前摆一起变化；后摆腿保留膝弯，整只鞋没有突然扭成另一方向。不能据低分辨率鞋尖轮廓定量要求零上翘。'],
    'W':['312–328 连续段维持朝画面左的侧向；306–310 为 SW，故不放入同方向连续段。','314–318 的前脚朝左伸出后接近身体下方，随后319–324出现回收/另一腿向前的交替；腿不是一直用伸直膝盖前踢。','鞋掌前端保持朝左的整体关系；后腿回收时鞋底可能变得更竖，但伴随屈膝，不能只按鞋掌屏幕倾角判为外翻。'],
}
for direction,lo,hi in [('E',344,368),('W',312,329)]:
    sheet(list(range(lo,hi)),f'{direction}-continuous.jpg')
    ims=[frames[i][2].crop((560,185,715,335)).resize((310,300),Image.Resampling.NEAREST) for i in range(lo,hi)]
    durations=[round((i+1)*1000/24)-round(i*1000/24) for i in range(hi-lo)]
    ims[0].save(ROOT/f'{direction}-continuous-1x.webp',save_all=True,append_images=ims[1:],duration=durations,loop=0,lossless=True)
    encoded=Image.open(ROOT/f'{direction}-continuous-1x.webp')
    encoded_durations=[]
    for j in range(encoded.n_frames):
        encoded.seek(j); encoded.load(); encoded_durations.append(encoded.info['duration'])
    assert sum(encoded_durations)==sum(durations)
    segments.append({'screenDirection':direction,'zeroBasedFrameStart':lo,'zeroBasedFrameEndInclusive':hi-1,'frameCount':hi-lo,'firstPtsSeconds':frames[lo][1],'lastPtsSeconds':frames[hi-1][1],'intervalIncludingLastFrameSeconds':(hi-lo)/24,'sampling':'every decoded frame; no temporal skipping','contactSheet':f'{direction}-continuous.jpg','playback':f'{direction}-continuous-1x.webp','sourceFrameDurationsMs':durations,'encodedWebpFrames':encoded.n_frames,'encodedWebpDurationsMs':encoded_durations,'playbackEncodingNote':'Lossless encoder coalesces identical adjacent cropped images and sums their durations. Contact sheet retains every decoded source frame; total 1x timing is unchanged.','observations':observations[direction]})
report={'reviewDate':'2026-10-04','sourceVideo':str(VIDEO),'sourceSha256':hashlib.sha256(VIDEO.read_bytes()).hexdigest(),'decoder':'PyAV 19.0.1','nominalFps':24,'nativeFrameSize':[1280,592],'cropXYXY':[560,185,715,335],'reviewEnlargement':'2x nearest-neighbor; no synthesis, sharpening, pose modification or interpolation','segments':segments,'requestedTimestampCorrections':[{'requestedSeconds':14.167,'nearestZeroBasedFrame':340,'observedScreenDirection':'E / right-facing','comment':'不是 W；该帧头/胸与脚整体朝右。339–369 是侧向 E 段，本次选中344–367以避开边界并保持小型联系图。'},{'requestedSeconds':10.92,'nearestZeroBasedFrame':262,'observedScreenDirection':'NE / upper-right-facing','comment':'258–263 仍是 NE，264–268 转 N，269 再转 NW；不能当作纯 E 段。'}],'limitations':['Direction labels are visual screen-space interpretations, not engine metadata.','Each shoe is only roughly 8–15 native pixels long; compression, dark shadow, nameplate and effects prevent exact ankle angle, sole contour or precise contact timing measurements.','A slightly curled boot tip or foreshortened sole is not sufficient evidence of foot-axis twisting.','W sample is shorter than one second. Neither clip proves this project’s 8 support frames or 16 x 75 ms timing.','Do not copy costume, proportions or rendering style. These clips support motion-plane and neighboring-pose comparison only.'],'applicationToProject':['Compare forward reach, knee flexion, ankle return and foot pitch as one sequence; avoid holding a long straight-knee kick with the whole toe section strongly raised.','Do not remove natural heel rise, normal knee bending, perspective or slight toe clearance during swing.','For each proposed correction, preserve already-correct frames and compare the changed pose with both adjacent frames and 1x playback.']}
(ROOT/'side-reference-motion-analysis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
