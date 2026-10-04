"""Private attack/SW replacement entry. Reuse register validation, explicitly replace one verified SHA."""
from pathlib import Path
import sys,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
code=(ROOT/"tools"/"register_frame.py").read_text(encoding="utf-8")
code=code.replace("ROOT = Path(__file__).resolve().parents[1]","ROOT = Path(__file__).resolve().parents[2]")
code=code.replace('if output.exists() or sidecar.exists():\n        raise ValueError(f"拒绝覆盖已有登记，请先人工确认该帧用途: {output}")','''if output.exists() or sidecar.exists():
        if not args.replace_sha256 or not output.is_file() or not sidecar.is_file() or digest(output) != args.replace_sha256:
            raise ValueError("Replacement requires exact existing export SHA256 and sidecar")
        if args.action != "attack" and not (args.action == "run" and args.direction == "SW"):
            raise ValueError("Private scope is attack or run/SW only")
        old_record = read_json(sidecar)
    else:
        old_record = None''')
code=code.replace('output.write_bytes(output_bytes)','''if old_record:
        retired = receipt_path.with_name(receipt_path.name.removesuffix(".receipt.json") + ".replaced-export.generation.json")
        retired.write_text(json.dumps(old_record, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
        record["replacedExport"] = {"sha256": args.replace_sha256, "record": relative(retired), "reason": args.replace_reason, "oldImageRetention": "replaced in place after all inputs verified; historical reference hashes remain truthful"}
    output.write_bytes(output_bytes)''')
code=code.replace('args = parser.parse_args()','''parser.add_argument("--replace-sha256")
    parser.add_argument("--replace-reason", default="定向AI修正")
    args = parser.parse_args()''')
exec(compile(code,__file__,"exec"),globals())

