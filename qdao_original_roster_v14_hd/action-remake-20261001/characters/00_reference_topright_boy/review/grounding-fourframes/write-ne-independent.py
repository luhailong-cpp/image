"""Record the independent static review of the inspected NE selection and exact sources."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
path = ROOT / "generation/run/NE/selection-middle4-side2-20261004.json"
selection = json.loads(path.read_text(encoding="utf-8-sig"))
rows = selection["frames"]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(path) == "561eabd25610adf834b0aaf48659905299302fc011f06afeff4bddc79fe5d054", "Selection changed; new visual review is required before recording approval"
observations = [
    "右支撑腿在画面右侧向跑向前落，左恢复腿后折露底；空右臂在身后。",
    "右支撑鞋由初落转较平承重，膝踝相连；左腿仍后折，右空手仍在后摆段。",
    "右膝明显缓冲，右鞋掌朝地、腿位进入髋下；左鞋底仍露在后方。",
    "同一右支撑腿稍伸，左恢复鞋向身体收拢，右手开始回程；双腿没有交换。",
    "右脚髋下承重，左抬腿进一步经过，左鞋可见底面积减小；右空手前摆。",
    "右脚维持中段末支撑，左腿前抬受到衣摆遮挡，鞋跟形状和腿线可读；没有新增脚或断腕。",
    "右腿朝画面左下后伸，鞋跟抬起而前掌端朝地；左腿已前抬，右空手在前。",
    "右后伸腿和踝角继续变化，鞋掌朝向仍沿NE轴；左脚准备前落，静态未见外翻硬伤。",
    "原生复核：支撑腿来自远侧左髋，从右抬腿后方斜向前下连接左鞋；近侧右抬鞋整底仍朝观察者，身份未交换。",
    "原生复核：同一左膝加深缓冲、左踝回收到更靠髋下，支撑鞋更平；右恢复腿和右空拳位置连续。",
    "原生复核：左髋下深缓冲承重，右腿后折；上身压低可见，头部仍保持NE转向，未见与邻帧不相容的大幅放大。",
    "左支撑鞋与膝相连，右恢复腿更靠近躯干；右空手由前摆退回身侧。",
    "左中段后半支撑，右恢复膝开始向前；左葫芦抱持持续，右拳后摆。",
    "左中段末支撑，右鞋由露底转为侧后跟，右膝前移；鞋朝向与NE一致。",
    "原生复核：左后伸腿在画面左下，前掌端朝地、后跟抬起；近侧右腿前抬，空右臂后摆，葫芦仍在左手。",
    "原生复核：左后伸腿与踝角有独立变化，右腿前抬准备转入01；头身与15相近，静态首尾身份衔接成立。",
]
assert sorted(r["frame"] for r in rows) == list(range(1, 17))
seen_files, seen_pixels, checked = set(), set(), []
for row in rows:
    p = ROOT / row["source"]
    actual = sha(p)
    assert actual == row["sha256"]
    record_path = ROOT / row["generationRecord"]
    record = json.loads(record_path.read_text(encoding="utf-8-sig"))
    assert record["sha256"] == actual and record["route"] == "builtin"
    with Image.open(p) as im:
        im.load()
        assert im.size == (1254, 1254) and im.mode == "RGBA" and im.format == "PNG"
        pixels = hashlib.sha256(im.tobytes()).hexdigest()
    assert actual not in seen_files and pixels not in seen_pixels
    seen_files.add(actual); seen_pixels.add(pixels)
    checked.append({"frame": row["frame"], "source": row["source"], "sourceSha256": actual,
                    "generationRecordSha256": sha(record_path), "nativePixelSha256": pixels,
                    "supportFoot": "right" if row["frame"] <= 8 else "left",
                    "positionPair": ((row["frame"] - 1) % 8) // 2 + 1,
                    "staticObservation": observations[row["frame"] - 1]})
native_slots = [3, 9, 10, 11, 15, 16]
report = {
    "atUtc": datetime.now(timezone.utc).isoformat(), "reviewer": "delivery_check independent static review",
    "direction": "NE", "status": "static_reviewed_no_confirmed_hard_defect",
    "selection": {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)},
    "methods": ["实际查看全部16帧完整画布联系表及统一区域腿部图。", "实际查看槽03、09、10、11、15、16的完整1254原生图。", "膝-踝-鞋连接、前后遮挡、鞋底与鞋面、持物与空手相位、头身大小综合判断；不以最低alpha像素代替地面。", "所有16原生RGBA文件和generation记录SHA实测核验；完整RGBA像素唯一。"],
    "contactSheets": [{"path": "review/grounding-fourframes/" + name, "sha256": sha(OUT / name)} for name in ("NE-candidate-full.jpg", "NE-candidate-legs.jpg")],
    "nativeSlotsViewed": native_slots, "nativeSourceCount": 16, "uniqueFileAndPixelHashes": True,
    "contactPattern": [{"foot": "right", "front": [1, 2], "middleEarly": [3, 4], "middleLate": [5, 6], "rear": [7, 8]}, {"foot": "left", "front": [9, 10], "middleEarly": [11, 12], "middleLate": [13, 14], "rear": [15, 16]}],
    "visibleSupportFrames": {"right": list(range(1, 9)), "left": list(range(9, 17))},
    "contactConfidence": "medium: static sprite shape supports the stated sequence; world-ground and dynamic contact are unverified",
    "keyFinding": "09-v10与10-v7保留远侧左腿支撑身份，前伸到加载具有独立膝踝变化；头身和左抱葫芦/右空拳连续。",
    "hardStaticDefectsRemaining": [],
    "limitations": ["03和11存在更深的承重压缩及上身位移，应在正常尺寸实播检查节奏和视觉起伏；静态未认定为新的比例硬伤。", "前侧/中段/后侧由二维透视与关节关系判断，没有世界地面标定或滑步测量。", "未实播动态循环；首尾时间连续性、实际移动速度与客户端滑步未验收。"],
    "timing": {"frameMs": 75, "cycleMs": 1200, "scope": "selection contract only; no playback performed"},
    "dynamicVisualVerified": False, "clientIntegrated": False, "frames": checked,
}
(OUT / "NE-independent.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": report["status"], "nativeSources": 16, "hardStaticDefects": 0, "selectionSha256": sha(path)}))
