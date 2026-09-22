# 10 赤枪少女：来源归档与静态核对

`archive_and_audit.py` 只处理本角色证据，不调用生成模型、不修改像素、不批准美术、不写公共索引。初始库存证据及原肖像/输入缩小图来源记录位于 `../10-work/audit/`。

```powershell
$qdaoPython = 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$qdaoTool = 'qdao_original_roster_v14_hd/recovery-20260921/10-tools/archive_and_audit.py'
& $qdaoPython -X utf8 -B $qdaoTool archive --archive 'qdao_original_roster_v14_hd/recovery-20260921/10-generation/S01-v2' --original '<工具实际返回的PNG绝对路径>' --result '<保存实际output_hint的JSON路径>'
& $qdaoPython -X utf8 -B $qdaoTool check --archive 'qdao_original_roster_v14_hd/recovery-20260921/10-generation/S01-v2'
```

归档要求已有 `request.json` 与 `prompt.txt`。只允许删除补丁保存时额外附带的末尾 CR/LF，原文本另存；任何其他提示词差异都会拒绝。真实默认原图保留，复制到 `raw.png` 后核验 SHA。真实工具结果原字节复制为 `tool-result.json`，原始 `output_hint` 内必须确实含指定输出路径。

每个原图产生 `raw.png.generation.json`、`generation-receipt.json`、`static-check.json`；型号与质量仍为 null/unverified，完整配置只是目标快照。请求若未包含开始时配置或参考 SHA，脚本明确记录审计/归档时观测，不声称开始时绑定。工具未返回完成时间时保持 null，`resultObservedAt` 单独表示归档观测时间。

原生尺寸小于 1024 或缺少透明 alpha 仍保留真实返回图与证据，并将相应素材门禁标为失败。证据字节核对通过不表示动作、身份、枪杆握持、比例、残边或 30ms 循环审阅通过。

`preflight` 已执行一次并保留 0 walk / 0 idle 快照；该命令拒绝覆盖已有快照。全部命令拒绝替换已存在的生成证据，重试需要新 attempt 目录。
