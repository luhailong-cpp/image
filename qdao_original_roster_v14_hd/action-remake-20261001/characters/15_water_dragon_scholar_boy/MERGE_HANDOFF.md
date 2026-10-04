> 当前状态：用户指出其他方向仍不正确，上一轮离线通过结论已撤回，正按09竹弓少女当前版定向重修。跑步最新正式预览参数为1200ms/圈、16帧各75ms；旧快速档已移除。下文上一轮交接细节尚待本轮完成后更新，不能据此宣称本轮已完成。

# 15 水龙书生 · 合并交接

仅合并本角色目录 `qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy/`。196 帧已齐并完成逐帧静态复核；完整播放的最终离线结论以 `audit/final-review.json` 为权威，并须与当前 196 槽的来源 SHA 和 14 组动作一致。

`offline_reviewed` 是本聊天／主审的离线复核状态，不表示用户已验收。用户尚未验收，客户端未接入、未运行验收；本次没有覆盖客户端资源。

## 文件与来源权威

- `manifest.json`：196 张 runtime 的精确路径、SHA、时序、事件标记与审核状态。
- `provenance/derived/*.json`：成品 SHA、固定画布变换、原生来源 SHA，以及完整内嵌 `originalGenerationRecord`。
- `audit/final-review.json`：本聊天／主审实际离线播放复核结论，绑定每槽 `sourceSha256` 与 14 组 `offlineApproved`；不由文件数量或自动检查推定通过。
- `audit/final-provenance-check.json/md`、`audit/final-delivery-check.json/md`：来源链和最终交付技术核验；技术通过不替代视觉或用户验收。
- `sources-index.json`、`provenance/generation/`、`provenance/reused/`、请求／回执／提示词：保留选帧与逐图历史证据。路径修正前后见 `audit/provenance-path-repairs.json`。

当前选择是 195 张本批生成图和 1 张旧图复用。旧跑步原 E07 的 SHA `4c270e0c04de54a112120677088626beb0e7b0e15c358dc387d499ed305dc627` 重选为当前 `run/E/09`；原文件名是历史相位标签，不能据此改回旧槽位。其他尾批选择及其 SHA 直接读取当前 manifest/derived，不在本文维护第二份易过期选表。

每张图片均保留独立来源，没有镜像、复制或插值凑数。另一台电脑未提交的素材未读取；旧批次、角色画像、idle 和 designs 仅作只读参考。

## 帧组与本地时序

| 动作 | 方向 | 每方向帧数 | 本地播放时序 |
| --- | --- | ---: | --- |
| run | N/NE/E/SE/S/SW/W/NW | 16 | weighted720，逐帧承重节奏，720ms/圈 |
| hit | E/W | 6 | 40ms/帧，240ms/段 |
| attack | E/W | 12 | 30ms/帧，360ms/段 |
| cast | E/W | 16 | 45ms/帧，720ms/段 |

跑步原始时序：`[50,70,60,40,30,25,35,50]ms × 2`。最终复核应用后，具体数值写入每个 run 帧的 `durationMs`，以及组级 `frameDurationsMs`、`cycleMs=720`；时序状态为 `offline_selected_not_client`。默认配置与来源见 `audit/run-timing.json`。

GIF 采用 10ms 精度，实际时序为 `[50,70,60,40,30,30,30,50]ms × 2`，仍共 720ms；各组预览 JSON 同时记录原始、请求与 GIF 实际时长。0.25× 慢速按原始时序放大四倍。HTML 保留 640/720/800ms 均匀节奏比较，480ms 仅为旧基线，不作为当前正常速度验收结论。战斗原时序及其 GIF 取整方式保留。

攻击命中／施法释放等事件以当前 manifest 中的逐帧 `event` 为准。它们用于素材接入对位，不代表已在客户端测定的战斗判定时刻。

## 画布与锚点

正式成品为 1024×1024 RGBA。统一变换为完整原生 1254×1254 → 940×940，置入 1024×1024 的 `(42,49)`；全局虚拟根 `(512,942)`，Unity 自下而上 pivot 约定 `(0.5,0.08)`。

不对单帧脚底贴地，不按包围盒独立缩放，不移动整人抹去腾空。接地、膝踝和脚掌方向的修正发生在实际图像姿态中；固定导出变换保持全组一致。

## 模型证据

配置目标为 GPT Image 2.5 Sunburst / max，实际使用内置宿主管理入口。该入口未提供型号／质量选择器，未披露实际返回版本或质量；相关 `model/quality` 和 `actualModel/actualQuality` 保持 null／未确认。配置目标、提示词和官方产品说明不作为逐图实测证明。历史记录的时间、模型证据和图片 SHA 均保留原义。

## 预览与复核工具

`preview/index.html` 提供单动作、240/384px、正常／慢速和逐帧查看；`preview/all-directions.html` 提供八方向跑步 4×2 同播及六组战斗正常／慢速并列。`preview/run-all-directions.gif` 是八方向跑步总览；`preview/key-poses-current.png` 从当前 runtime 的 run/E01、hit/E03、attack/E06、cast/E10 生成。

审核状态应用工具 `tools/finalize_review.py` 只接受已存在且完全匹配当前来源的主审记录，不生成复核通过结论。最终交付可执行：

```text
python tools/final_delivery_check.py --write-report --write-retention-plan
```

该命令检查现有成品、派生链、时序和当前预览，没有删除功能。原生图片清理后仍可运行；不能将历史源图已清理误判为 runtime 不完整。依赖原图的 `build_delivery.py` 不作为清理后的核验入口。

## 图片清理与合并边界

最终复核与交付检查通过后已执行清理：删除 514 张原图、退稿与中间图片，保留 196 张正式 PNG 与 44 张当前预览，共 240 张图片。删除前 SHA、逐图路径及时间见 `audit/retention-executed.json`；清理后的技术检查仍为 0 错误、0 警告。6 份过期诊断 HTML 及 1 份 Python 缓存的清理见 `audit/auxiliary-cleanup.json`。逐图模型／质量／时间、提示词、请求、回执与来源文字未删除。

最后施法 E06/E07/E09 已修复明显脚位横滑；E06/E07 仍保留原生约15–25px底线变化及 E07 约20px脚缘横差，属于主审本地预览接受的绘制差异，未声称逐像素锁地。真实移动速度与地面接触需在客户端接入时匹配。

保留 196 张最终 runtime PNG、两个交付 HTML、各组最新 contact、跑步主选 720ms／慢速 GIF、战斗正常／慢速 GIF、八方向总览和当前关键姿态，以及必要接入与来源文字。按用户规则清理原图、回退／拒稿、历史诊断图、PNG/GIF/APNG 等中间图片；不因旧记录引用原图路径而永久保留全部像素。生成记录、模型／质量、提示词、参考 SHA、回执及路径修正文字继续完整保留。`manifest.source`、`inventory` 和派生记录中的源路径是生成历史，不承诺源图片仍在目录。

只处理本角色目录，不清理其他角色、旧批次、共享风格／身份参考或宿主图片缓存。合并另一台电脑时比较相对路径与 SHA，保留其未提交工作差异，由用户决定合并。

当前收尾环境只读核查到 Git 分支为 `main`，与批次启动时记录的 `codex/character-actions-20261001` 不同。本聊天未切分支，未操作共享 Git 暂存、提交或推送，也不擅自调整这一环境差异。

