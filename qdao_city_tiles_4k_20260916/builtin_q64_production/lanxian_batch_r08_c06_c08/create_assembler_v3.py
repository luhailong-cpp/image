from pathlib import Path
P=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/lanxian_spring/r08_c08')
s=(P/'assemble_builtin_single_v2.py').read_text(encoding='utf-8-sig')
s=s.replace('prompt = ROOT / "prompts" / selection.get("prompt",f"{tile_id}.single-reference.prompt.txt")','pre_record = read_json(record_path)\n            prompt = Path(pre_record.get("promptFile", pre_record.get("promptPath", "")))\n            if not prompt.is_absolute(): prompt = ROOT / prompt')
s=s.replace('record = read_json(record_path)\n            if record.get', '''record = read_json(record_path)
            refs = record.get("submittedImages", record.get("actualInputReferences", []))
            if not refs: raise ValueError(f"Missing submitted references: {record_path}")
            for ref in refs:
                rp = Path(ref.get("path", ref.get("file", "")))
                if not rp.is_absolute(): rp = ROOT / rp
                if not rp.is_file() or sha256(rp) != ref["sha256"]:
                    raise ValueError(f"Submitted reference hash mismatch: {rp}")
            if record.get''')
s=s.replace('"userSelectedModel": "GPT Image 2.0 (host builtin)"','"userSelectedModel": "ChatGPT Images 2.5 target; host managed; actual variant unverified"')
target=P/'assemble_builtin_single_v3.py'
assert not target.exists()
target.write_text(s,encoding='utf-8')
print(target)
