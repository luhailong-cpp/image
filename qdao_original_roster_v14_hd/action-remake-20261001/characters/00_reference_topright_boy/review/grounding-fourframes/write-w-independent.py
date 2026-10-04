"""Record independent static observations for the exact visually inspected W selection."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
path = ROOT / "generation/run/W/selection-middle4-side2-20261004.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
expected = "be5b876321ec0c1d029312d0c38cf5c106f3ee8908f3004f3c4a8119bf109cac"
assert sha(path) == expected, "Selection changed; new visual review required"
rows = json.loads(path.read_text(encoding="utf-8-sig"))
observations = [
    "右支撑腿向W前伸，鞋跟侧初接触，另一腿后折；左手抱葫芦，右空臂后摆。",
    "同一右前脚转更平的加载姿态，左恢复腿后折；与01并非同一鞋掌姿态。",
    "右脚回到髋下，膝屈缓冲，左恢复鞋靠近身体下方；右空手仍在后摆回程。",
    "右中段继续承重，左膝开始经过、左鞋仍抬起；右空拳出现在前侧，葫芦抱持侧未变。",
    "右支撑脚平掌承重，左膝向前上提；头身与相邻修订保持同一量级，没有先前的突然放大。",
    "原生复核06-v5：右支撑膝踝相连、鞋掌仍朝地，左摆腿更前伸；头发、脸与身体比例已恢复到05附近。",
    "原生复核07-v4：右腿向髋后伸出、后跟开始抬而前掌朝地；左腿前抬，头身放大问题已收回。",
    "原生复核：右腿后伸幅度进一步增加，前掌端朝地；左腿前方预备落脚，空右拳维持前摆段。",
    "原生复核：换左脚前伸初触，右腿后折；膝踝未错接，空右手与左持葫芦保持身份。",
    "同一左前脚由初触转较平承重，右腿仍后折恢复；前侧两张姿态确有差异。",
    "原生复核11-v3：近侧左支撑脚已在髋下，远侧右鞋抬起经过；双腿身份正确，头身与12和13接近。",
    "左髋下持续承重，右恢复膝更向前上方；右空手在后侧，左手握持葫芦稳定。",
    "左中段后半支撑，右摆腿向前抬起；鞋尖均朝W，未见脚掌向外扭转。",
    "原生复核14-v4：左中段末支撑、右腿进一步向前伸，头身与13/15相近；先前14突然放大已消除。",
    "左腿后伸推蹬、跟部提起而前掌朝地，右腿抬于前方；空右臂保持后摆。",
    "原生复核：左后伸腿与踝角继续变化，右腿预备前落；转01时支撑换到右脚，持物侧和脚朝向未交换。",
]
assert [r["frame"] for r in rows] == list(range(1, 17))
seen, pixel_seen, checked = set(), set(), []
for row in rows:
    source = ROOT / row["source"]
    digest = sha(source)
    assert digest == row["sourceSha256"] and digest not in seen
    seen.add(digest)
    record_path = Path(str(source) + ".generation.json")
    record = json.loads(record_path.read_text(encoding="utf-8-sig"))
    assert record["sha256"] == digest and record["route"] == "builtin"
    with Image.open(source) as im:
        im.load()
        assert im.size == (1254, 1254) and im.mode == "RGBA" and im.format == "PNG"
        pixel_digest = hashlib.sha256(im.tobytes()).hexdigest()
    assert pixel_digest not in pixel_seen
    pixel_seen.add(pixel_digest)
    checked.append({"frame": row["frame"], "source": row["source"], "sourceSha256": digest,
                    "generationRecordSha256": sha(record_path), "nativePixelSha256": pixel_digest,
                    "supportFoot": row["supportFoot"], "positionPair": ((row["frame"] - 1) % 8) // 2 + 1,
                    "staticObservation": observations[row["frame"] - 1]})
report = {
    "atUtc": datetime.now(timezone.utc).isoformat(), "reviewer": "delivery_check independent static review",
    "direction": "W", "status": "static_reviewed_no_confirmed_hard_defect",
    "selection": {"path": path.relative_to(ROOT).as_posix(), "sha256": expected},
    "methods": ["依据最终选表重新生成并实际查看全部16帧完整画布和固定区域腿部联系表。", "已实际查看最终槽01、05、06、07、08、09、11、14、16完整原生图；07/14在上次修订落盘后也已单独审看。", "完整画布联系表使用固定W导出变换、240px显示，不逐帧拟合或贴地。", "支撑膝踝、腿的前后遮挡、鞋掌与鞋尖、持物手、头身和相邻相位综合判断；未以alpha最低点证明地面。"],
    "contactSheets": [{"path": "review/grounding-fourframes/" + name, "sha256": sha(OUT / name)} for name in ("W-independent-contact.jpg", "W-independent-lower.jpg")],
    "contactSourceRecord": {"path": "review/grounding-fourframes/W-independent-contact.sources.json", "sha256": sha(OUT / "W-independent-contact.sources.json")},
    "nativeSlotsViewed": [1, 5, 6, 7, 8, 9, 11, 14, 16],
    "nativeSourceCount": 16, "uniqueFileAndPixelHashes": True,
    "contactPattern": [{"foot": "right", "front": [1, 2], "middleEarly": [3, 4], "middleLate": [5, 6], "rear": [7, 8]}, {"foot": "left", "front": [9, 10], "middleEarly": [11, 12], "middleLate": [13, 14], "rear": [15, 16]}],
    "visibleSupportFrames": {"right": list(range(1, 9)), "left": list(range(9, 17))},
    "contactConfidence": "medium: static support geometry only; world-ground and dynamic foot locking are unverified",
    "resolvedConfirmedFindings": [{"issue": "06-v3、07-v3、14-v3在完整画布序列中头身明显放大", "currentSources": ["06-v5", "07-v4", "14-v4"], "conclusion": "本次完整联系表及原生复核未再见相同程度的大小跳变。"}],
    "hardStaticDefectsRemaining": [],
    "limitations": ["03→04、10→11可见空右拳由身体后侧转向前侧或反向，葫芦遮挡中间路径；正常速度下是否显得突跳仍需实播判断。未判为新的高置信静态肢体错误。", "接地、鞋掌承重由2D形状和相位判断，尚无世界地面标定、根点位移与滑步测量。", "首尾换脚身份已静态检查，但没有动态循环或客户端运行验收。"],
    "timing": {"frameMs": 75, "cycleMs": 1200, "scope": "selection contract only; no playback performed"},
    "dynamicVisualVerified": False, "clientIntegrated": False, "frames": checked,
}
(OUT / "W-independent.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": report["status"], "nativeSources": 16, "hardStaticDefects": 0, "selectionSha256": expected}))
