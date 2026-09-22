"""Prepare an exact real-call request for one independent N/NE sprite; does not generate."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
RECOVERY = ROOT / "qdao_original_roster_v14_hd/recovery-20260921"
PHASES = {
    1: "LEFT heel contacts in front, RIGHT foot remains behind pushing off through the toe. Both feet have ground contact. Left stride is forward along the heading; right stride is backward. This is the first contact extreme.",
    2: "LEFT leg begins accepting weight, left knee softens and body lowers slightly. RIGHT heel rises while its toe still pushes off behind. A distinct small advance from frame01, not the identical stride.",
    3: "LEFT leg fully supports weight with foot flat; RIGHT trailing toes have just left the ground and right knee folds. Left foot is planted, right foot just lifted behind.",
    4: "LEFT foot remains planted and supports the body; RIGHT knee swings forward from behind but has not yet reached the left leg. Right boot is lifted with toe down; the two legs are approaching passing.",
    5: "Passing pose: LEFT leg is straight beneath pelvis and carries weight. RIGHT knee and lifted boot pass immediately beside the supporting left leg. Right boot is visibly raised; left sole remains grounded.",
    6: "LEFT leg remains the grounded support slightly behind the pelvis. RIGHT thigh advances ahead, right knee bent and right boot moving forward, lower than passing. Right foot is still in the air.",
    7: "LEFT foot supports the body behind; RIGHT leg is stretching forward, knee opening, toe gently raised and heel approaching the invisible ground. Right foot has not touched ground.",
    8: "RIGHT boot is just about to land ahead, heel extremely close to the ground with toe slightly up. LEFT support heel starts rising behind. Late right pre-contact; both feet are far apart along the heading.",
    9: "RIGHT heel contacts in front, LEFT foot remains behind pushing off through the toe. Both feet have ground contact. Right stride is forward along the heading; left stride is backward. Opposite contact extreme to frame01.",
    10: "RIGHT leg begins accepting weight, right knee softens and body lowers slightly. LEFT heel rises while its toe still pushes off behind. A distinct small advance from frame09.",
    11: "RIGHT leg fully supports weight with foot flat; LEFT trailing toes have just left the ground and left knee folds. Right foot is planted, left foot just lifted behind.",
    12: "RIGHT foot remains planted and supports the body; LEFT knee swings forward from behind but has not yet reached the right leg. Left boot is lifted with toe down; the legs are approaching passing.",
    13: "Passing pose: RIGHT leg is straight beneath pelvis and carries weight. LEFT knee and lifted boot pass immediately beside the supporting right leg. Left boot is visibly raised; right sole remains grounded.",
    14: "RIGHT leg remains the grounded support slightly behind the pelvis. LEFT thigh advances ahead, left knee bent and left boot moving forward, lower than passing. Left foot is still in the air.",
    15: "RIGHT foot supports the body behind; LEFT leg is stretching forward, knee opening, toe gently raised and heel approaching the invisible ground. Left foot has not touched ground. This leads smoothly toward frame16 and then frame01.",
    16: "LEFT boot is just about to land ahead, heel extremely close to the ground with toe slightly up. RIGHT support heel starts rising behind. Late left pre-contact; this must transition naturally to LEFT heel contact in frame01, not repeat it.",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("direction", choices=("N", "NE"))
    parser.add_argument("frame", help="01..16 or idle")
    parser.add_argument("--version", type=int, default=1)
    parser.add_argument("--extra", default="")
    parser.add_argument("--pose-reference", type=Path)
    args = parser.parse_args()
    idle = args.frame == "idle"
    frame = 0 if idle else int(args.frame)
    assert idle or 1 <= frame <= 16
    direction = args.direction
    attempt_name = f"idle-{direction}-v{args.version}" if idle else f"{direction}-{frame:02d}-v{args.version}"
    target = RECOVERY / "20-generation" / attempt_name
    target.mkdir(parents=True, exist_ok=False)
    refs = [RECOVERY / "20-reference/identity-inspection-1024.png",
            ROOT / "designs/jubaozhai-ui/02-characters.png",
            RECOVERY / "20-generation/idle-S-v1/raw.png"]
    if args.pose_reference:
        refs.append(args.pose_reference.resolve())
    assert all(path.is_file() for path in refs)
    facing = ("NORTH / N: exact REAR VIEW, facing directly away from camera toward the TOP of the image. Show the BACK of her head and robe, no face and no eyes. Her anatomical RIGHT hand is on viewer RIGHT and holds the astrolabe; her anatomical LEFT hand on viewer LEFT holds the three star cards."
              if direction == "N" else
              "NORTHEAST / NE: back-right THREE-QUARTER view, heading diagonally toward the TOP RIGHT of the image. We predominantly see her BACK and right side, only a tiny right cheek contour if naturally visible, no front-facing eyes. Her anatomical RIGHT hand on the near right side holds the astrolabe; her anatomical LEFT hand on the far left side holds the three cards. Do not flip or swap them.")
    pose = ("INDEPENDENT IDLE: relaxed balanced standing, both boots grounded, slightly apart, knees neutral and no walking stride. This is a freshly drawn dedicated standing pose, not a walking-frame crop." if idle else
            f"WALK PHASE {frame:02d}/16, continuous calm walking in place along the stated heading: {PHASES[frame]} At least one foot firmly supports her at all times. Show coherent actual skeletal articulation, natural separate leg trajectories and slight counter-swing of the two arms. Do not rotate the body away from its fixed heading. Leg names are anatomical, never viewer-relative.")
    prompt = f"""Use case: stylized-concept.
Create ONE independent production game sprite for 20_star_formation_master_girl from 五行奇谈: a complete single full-body {direction} {'idle' if idle else 'walking'} pose, native square 1024x1024 or larger, genuine transparent alpha background. One character and one pose only.
Reference image1 is her authoritative original-portrait identity (only whole-image downsampled for input). Preserve the same 2.3-head-tall rounded chibi girl with oversized head and compact torso/legs; dark brown-black long straight hair, high half-up bun, ornate gold star crown, red star side ornament and short red tassels. Preserve black/ivory Daoist robes, red panels, warm gold star/cloud trim, red-gold star belt, ivory trousers and black/gold boots. RIGHT hand holds the short-handled circular charcoal/gold star astrolabe, concentric orbital rings and central red-star jewel with short tassels. LEFT hand holds exactly three physical black/gold talisman cards with red-star centers. Both equipment items remain held, complete and at the same scale; render their physically appropriate reverse side when viewed from behind. No floating star effects, new weapons or equipment swaps.
Reference image2 is the approved PRIMARY RENDERING STYLE only: bright clean rounded refined hand-painted Daoist chibi fantasy, soft painted volume, crisp readable silhouette and restrained gold material. Do not copy its UI, green clothing, male face or text. Reference image3 is the same character's new front idle; use its scale and material consistency, but independently draw the requested rear gait rather than preserving its front stance.
{'Reference image4 is a same-direction pose/design continuity reference. Keep its back-view costume, camera, proportions and rendering, but draw the NEW leg articulation specified below. Do not inherit edge fringe, incorrect gait, airborne feet or wrong leg assignment from that reference.' if args.pose_reference else ''}
DIRECTION: {facing}
POSE: {pose}
Fixed slightly elevated game-sprite camera and constant proportions. Keep legs and complete boots readable below the robe and hair. Center upper-body axis x=512, lowest grounded boot sole at y=942 on a 1024 square, crown top around y=65. Use the same coordinates proportionally for larger native output. All crown, hair, sleeves, cards, astrolabe and tassels fully inside generous margins. Roughly 870px full character height on 1024; no zoom, camera changes or per-pose body resizing. No exaggerated bobbing, crossing legs, running or airborne jump. Gentle even lighting.
Preserve opaque ivory clothing and clean antialiased edges. True transparent background, NO floor, NO ground shadow, NO halo, NO checkerboard baked into RGB, NO red/purple/magenta edge fringe, NO text, labels, borders or sprite sheets. Newly drawn articulated pose only, never mirrored, copied, interpolated, warped or translated from an existing pose. Highest visual finish supported by the host.
{args.extra}
"""
    (target / "prompt.txt").write_bytes(prompt.encode("utf-8"))
    config = json.loads((RECOVERY / "20-generation/idle-S-v1/request.json").read_text(encoding="utf-8"))["configSnapshot"]
    request = {"character_id": "20_star_formation_master_girl", "slot": f"idle/{direction}.png" if idle else f"walk/{direction}/{frame:02d}.png",
               "attempt": attempt_name, "route": "builtin", "source_is_single_frame": True,
               "actual_request": {"prompt": prompt, "referenced_image_paths": [str(p).replace('\\','/') for p in refs],
                                  "started_at": datetime.now(timezone.utc).isoformat(), "model": None, "quality": None},
               "configSnapshot": config, "reference_roles": {str(refs[0]).replace('\\','/'): "authoritative original identity; downsampled with source chain",
                                                                 str(refs[1]).replace('\\','/'): "approved primary painting/material style",
                                                                 str(refs[2]).replace('\\','/'): "same character front idle scale and material only"},
               "reference_bindings_at_start": [{"path": str(p), "sha256": sha(p)} for p in refs],
               "note": "Prepared immediately before the actual built-in call; tool has no model/quality selectors. No result exists until returned."}
    (target / "request.json").write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"attempt":str(target),"prompt":prompt,"referenced_image_paths":request['actual_request']['referenced_image_paths']},ensure_ascii=False))


if __name__ == "__main__":
    main()
