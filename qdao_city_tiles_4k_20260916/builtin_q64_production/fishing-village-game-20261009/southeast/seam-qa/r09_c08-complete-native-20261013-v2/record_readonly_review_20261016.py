from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Q=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast")/"seam-qa"/"r09_c08-complete-native-20261013-v2"/"readonly-review-20261016-v1"
a=json.loads((Q/"source-and-pixel-audit.json").read_text())
notes={
"north-segment-1":"石块边缘和草缝大体接续；横缝上方为粗碎斑驳，下方细裂纹/小颗粒更密，材料横向变化清楚。",
"north-segment-2":"斜向石缝端点基本对位；下半石面细格与米白层显著增多，上半较粗蓝灰斑驳，材质未通过。",
"north-segment-3":"铺石排布和中心草缝延续；下半重复细格纹理与上半粗面存在明显密度差，仍待修。",
"north-segment-4":"右缘灯笼与流苏无明显位置断裂，石缝大体接续；横缝处石面明暗与斑纹颗粒发生变化。",
"east-segment-1":"灯笼流苏及铺石方向延续；右侧石面和投影明显比左侧软、模糊，中心竖缝清晰度断层突出。",
"east-segment-2":"蓝瓦、金色卷饰形状和轮廓接续，无明显结构位移；局部蓝色高光及笔触宽度变化，材料仍保留pending，不能因轮廓对齐而通过。",
"east-segment-3":"瓦垄及瓦端圆弧连续；中心附近蓝色深浅、亮带和笔触层次略变，需与整面屋瓦集中材料校准。",
"east-segment-4":"已查看窗格采用后的当前原生strip；蓝瓦/檐梁/立柱轮廓基本连续，左下窗格片段已替换。橙色檐梁仍有显著竖向色阶，瓦面亮带及墙柱笔触也未统一，未通过材料。",
"intersection-x29696-y32768":"交点石缝/草簇对位基本成立；下半石面比上半细密，四象限质感变化可见。",
"intersection-x30720-y32768":"交点石缝连续；下方石块呈重复细格，上方颗粒较粗，横向材料接合未通过。",
"intersection-x31744-y32768":"石块轮廓总体贯通；左下细格与右下粗斑、上半粗纹同时出现，四象限材料不统一。",
"intersection-x32768-y32768":"灯笼、金帽与流苏轴线连续；左铺石清晰、右铺石模糊的竖向过渡明显，横向石面质感亦变化。",
"intersection-x32768-y33792":"金色卷饰和蓝色脊瓦几何接续；背景石面纹理粗细及投影表现不同，材料保留pending。",
"intersection-x32768-y34816":"瓦垄没有明显错位；高光笔触宽度、蓝色饱和度在四象限有细微接合变化，材料未最终接受。",
"intersection-x32768-y35840":"瓦垄/檐口形状延续；横缝及竖缝附近亮带与暗蓝层变化，材料pending。虽引用p44新源，裁切像素与旧证据完全相同。",
"south-segment-1":"root实际查看：铺石横缝从密集碎纹突变为大而稀的纹理，少数缝端有轻微台阶；pending。",
"south-segment-2":"root实际查看：左石地纹理变化；木柱/横板整体对位，但亮度及纹理层级改变；pending。",
"south-segment-3":"root实际查看：木柱纹理密度及背景清晰度在横缝变化明显，结构大体延续；pending。",
"intersection-x29696-y36864":"root实际查看：同铺石粗细和局部接合问题；pending。",
"intersection-x30720-y36864":"root实际查看：工作台/箱子/袋结构连续，木纹横缝变化；pending。",
"intersection-x31744-y36864":"root实际查看：灯笼轮廓延续，柱子与背景木墙色调/清晰度横向断层；pending。新p44/p14源hash变化，但该裁切像素经独立重放为零差异。"}
obs=[]
for r in a["records"]:
 if r["scope"]=="impact_audit_only_no_visual_acceptance":continue
 for s in r["currentSources"]:assert hashlib.sha256(Path(s["file"]).read_bytes()).hexdigest()==s["sha256"]
 obs.append(dict(id=r["id"],image=r["currentImage"] or r["oldImage"],imageSha256=r["currentImageSha256"] or r["oldImageSha256"],reviewer="/root/east_water_finish_20261016" if r["scope"]=="own_native_view" else "/root",visuallyInspectedByThisAgent=r["scope"]=="own_native_view",rootReviewReceived=r["scope"]=="root_view_received",nativeScale=True,currentPixelReplayVerified=True,observations=notes[r["id"]],layout="large_forms_continue; see local issue observations",materialAccepted=False,formalAccepted=False))
out=dict(createdAt=datetime.now(timezone.utc).isoformat(),scope="r09_c08 north/east 8 native strips plus7 non-south crosses; root 6 south observations reused only after exact current replay",sourceAudit=str(Q/"source-and-pixel-audit.json"),sourceAuditSha256=hashlib.sha256((Q/"source-and-pixel-audit.json").read_bytes()).hexdigest(),observations=obs,windowAdoptionImpact=dict(northEastEvidencePixelsChanged=[dict(id="east-segment-4",changedPixels=29355)],northEastEvidencePixelIdentical=14,p44HashChangedButCropIdentical=["intersection-x32768-y35840"],rootSixSouthAllPixelIdentical=True,otherImpactedEvidenceNotViewed=[dict(id="south-segment-4",changedPixels=142779),dict(id="intersection-x32768-y36864",changedPixels=126657)],refreshRecommendation="Only east-segment-4, south-segment-4 and southeast cross x32768/y36864 need new pixels. p44/p14 hash changes alone do not invalidate other pixel-identical crops."),originalImagesAndSelectionsReadOnly=True,newImageOnly="Exact native current east segment4 evidence, no resampling",formalAccepted=False,internalReady=False)
p=Q/"visual-review.json";assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf8");print(p)

