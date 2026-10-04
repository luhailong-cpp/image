# Git 同步说明

`17-spirit-scribe-actions.zip` 作为本地生成的交付包保留，Git 同步完整交付原文件。克隆仓库后可直接使用这些原文件，交付入口见 [DELIVERY.md](DELIVERY.md)。

如需重新生成 ZIP，在本角色目录使用 Python 3 运行 `python tools/package_delivery.py`；该现有脚本会生成本地 ZIP 并更新 `package.json` 中的打包记录。
