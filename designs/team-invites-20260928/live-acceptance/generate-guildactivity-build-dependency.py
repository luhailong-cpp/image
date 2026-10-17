"""调用仓库正式导表器生成 Scene 工程已登记却缺失的 GuildActivity C++ 依赖。

只在本验收目录生成暂存产物；部署时只复制五个目标文件，不更新全表聚合器。
不编辑 schema、xlsx 或模板。
"""

from pathlib import Path
import hashlib
import json
import sys

SERVER = Path("E:/work/xuanming-server-mmo")
EXPORTER = SERVER / "tools/data_table_exporter"
sys.path.insert(0, str(EXPORTER))

from core.config_loader import load_config
from core.table_source import read_all_tables
from core.foreign_key import validate_foreign_keys
from core.primary_key import validate_primary_keys
from core.generators.config_gen import generate_config_classes
from core.generators.comp_gen import generate_comp_headers

cfg = load_config(EXPORTER / "exporter_config.yaml")
tables = read_all_tables(cfg)
fk = validate_foreign_keys(tables, cfg)
pk = validate_primary_keys(tables, cfg)
if not fk.ok or not pk.ok:
    raise RuntimeError("正式导表预检失败: " + repr(fk.errors + pk.errors))
selected = [table for table in tables if table.name == "GuildActivity"]
if len(selected) != 1:
    raise RuntimeError("GuildActivity 源表必须恰好一张")

stage = Path(__file__).resolve().parent / "guildactivity-generated"
cfg.cpp.code_dir = stage
for lang in (cfg.go, cfg.java, cfg.csharp, cfg.python, cfg.ue):
    lang.enabled = False
generate_config_classes(cfg, selected)
generate_comp_headers(cfg, selected)

files = ["guildactivity_table.cpp", "guildactivity_table.h", "guildactivity_table_fk.cpp",
         "guildactivity_table_fk.h", "guildactivity_table_comp.h"]
evidence = {
    "generator": str(EXPORTER),
    "source": ["data/GuildActivity.xlsx", "data/schema/guildactivity_table.proto"],
    "validation": "正式导表器读取全部源表，FK 与 PK 校验通过；只生成 GuildActivity C++ 管理器与组件",
    "files": [{"name": name, "sha256": hashlib.sha256((stage / name).read_bytes()).hexdigest()}
              for name in files],
}
(stage / "generation-evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(evidence, ensure_ascii=True, indent=2))
