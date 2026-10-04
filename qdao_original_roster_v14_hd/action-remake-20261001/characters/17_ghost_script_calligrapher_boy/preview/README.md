# 灵篆书生离线动作预览

直接用浏览器打开 `index.html`，无需服务器或客户端。页面内嵌盘点清单，图片通过相对路径读取，移动仓库时需保留目录结构。

功能：动作与方向切换、正常速度、0.25 倍慢速、上一帧/下一帧/拖动帧序、深底/浅底/棋盘底、候选版本选择、逐图 SHA 与来源记录。完整槽位模式保留缺帧为空；“已生成关键帧研究连播”会跳过缺口，不能用来证明完整动作或动态验收。

新增 PNG 后，从任意工作目录执行本角色的 `tools/build_preview.py`，再刷新页面。脚本只读取 staging PNG、对应 generation 记录、review 文件与六张已指定本地旧关键帧；只写 preview/index.html 和 preview/manifest-preview.json，不修改图片、主清单或状态文件。

```powershell
& 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy/tools/build_preview.py'
```

`manifest-preview.json` 记录每个真实槽位、当前选帧、候选版本、实际文件 SHA、原生尺寸及六张旧关键帧的原始相对路径。较高版本号只用于选择当前在制候选，不表示视觉通过。施法 E10 默认显示 v3，并保留 pending 与具体问题。

地面虚线仅用于检查，按 1254 画布中的 y=1155 显示；所有 PNG 使用完整画布等比显示，不逐帧按最低像素贴地或独立缩放人物包围盒。

布局检查：桌面 1440 像素与手机 390 像素；验证本地 file 协议加载、缺帧留空、E10 v3 待验收状态、旧 E06 相对路径、空方向播放禁用、无水平溢出和无 JavaScript 错误。结果见 `qa-results.json`。检查不代表美术或客户端验收。
