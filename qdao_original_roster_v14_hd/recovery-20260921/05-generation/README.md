# 05 NE03 / NE16 返工准备

当前状态：**已准备，尚未生图；等待04验收及主代理启动。** 不自动调用、不排定时、不请求收费API，不修改旧关键帧或 canonical。精确提示词与参考图片已按本机路径核对，不能把模板当实际生成请求或receipt。

| 槽位 | 提示词目标 | 参考顺序 |
|---|---|---|
| [NE03-pose-v2](NE03-pose-v2/prompt.txt) | 屏幕左靴维持支撑，屏幕右靴只抬到NE04之前的早期摆动，避免旧NE03的摆动腿交换和头部下跳 | 旧01源格 → 旧05源格 → 新NE04原生raw |
| [NE16-pose-v2](NE16-pose-v2/prompt.txt) | 屏幕右靴支撑，左靴走完旧13以来的摆动；头、冠、上身与旧01同等比例，接触前只保留小幅鞋角/膝弯变化 | 旧01源格 → 旧13源格 → 新NE15原生raw（仅相位参考，不继承较小体型） |

每帧最多3张参考。源格512图只作旧形象、相机、姿势参考，不作为原生高清来源；新工具返回单帧两边必须均≥1024，再按统一`.84`导出1024方图。请求真实透明背景、实体人物，明确保留紫发、紫衣、紫靴、淡紫半透明飘带；不能全局去紫。独立导入强制 `purple-preserve`，阈值50/75。

NE03目标源图主体约93%高；NE16约94%高，以保留旧01的最终810px主体高度为目标。不能为了数字把单帧scale改小或改大。NE16通过后仍须检查NE14/15，旧审计已发现15高777、16高766、01高810；只修16不自动证明15→16也平滑。

## 启动时的实际调用顺序

先重新view每张本地参考，然后运行下面的`--start`准备实际请求时间。`prepare_request.py`只写request，不调用任何生图。

```powershell
$py05 = 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py05 qdao_original_roster_v14_hd/recovery-20260921/05-tools/prepare_request.py --slot NE03 --start
```

随后由代理将对应`request.json`里的`actual_request.prompt`、`referenced_image_paths`原样传入内置`image_gen`。工具没有型号/质量选择器时记录`host-managed-unverified`，不将prompt或`gpt-image`元数据当显式锁定型号的证明。把真实返回的`output_hint`保存为本次目录的`tool-result.json`，保留原默认生成路径；不要记录空壳receipt或伪造成功。

```powershell
& $py05 qdao_original_roster_v14_hd/recovery-20260921/05-tools/archive_builtin_result.py --archive qdao_original_roster_v14_hd/recovery-20260921/05-generation/NE03-pose-v2 --original '<真实工具返回的默认PNG绝对路径>' --tool-result qdao_original_roster_v14_hd/recovery-20260921/05-generation/NE03-pose-v2/tool-result.json
& $py05 qdao_original_roster_v14_hd/recovery-20260921/05-tools/import_local_frame.py --archive qdao_original_roster_v14_hd/recovery-20260921/05-generation/NE03-pose-v2 --batch-id NE03-pose-v2 --frame 3 --staging-root qdao_original_roster_v14_hd/recovery-20260921/05-generation/NE03-pose-v2/staging
```

NE16同理，槽位改`NE16`、目录/批次改`NE16-pose-v2`、帧号改16。每次只写自己的独立staging目录；脚本没有canonical选项，已有manifest会拒绝覆盖。失败或返工使用新的版本目录，不覆盖已归档request/raw/receipt。

归档器复制原生raw，保留原默认文件，保存实际请求、精确prompt、output_hint、1次成功内置/0次收费API、SHA、PNG尺寸/CRC及C2PA元数据；C2PA签名不作已验证声明。导入器核对原图存在且SHA一致、原生尺寸、开始/完成时间、参考绑定、精确prompt，然后用现有未修改公共管线和独立verifier复算；仅在自己的staging写manifest、sources、五阶段图、单帧validation与深浅预览。

## 验收与当前缺口

1. NE03检查旧01→新02→新03→新04→旧05，支撑与摆动腿不能突换；冠、琴、上身不能随单帧缩小或下跳。
2. NE16检查旧13→新14→新15→新16→旧01→新02，双腿与首尾身高连续。
3. 紫色服装和半透明飘带须保持；残边检查同时用深/浅背景和原生局部，不能仅按magenta数值删色。
4. 合并旧NE01/05/09/13与12张新图，按同世界大小制16帧30ms/480ms循环；生成新文件绑定，不复用旧审计SHA宣称通过。
5. 此阶段只准备。尚无真实新raw、工具成功receipt或本轮导入结果，后续工具验收不能标为已通过。

旧关键帧、候选基线与参考SHA记录见[PREPARED.json](PREPARED.json)。旧整体来源JSON换行失配事实仍保留在[05审计](../05-audit/NE-VISUAL-REVIEW.md)，本准备不修写旧元数据。全角色仍需SE/SW/W/NW各16张新walk；不恢复已移出角色。
