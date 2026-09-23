# 08 炼丹童子：可复现后处理与离线预览

2026-09-23 当前交付入口：`../08-delivery-preview/revisions/final-v1/`。下文是制作期间的工具说明，历史审阅快照不再是交付版本。最终验收与清理状态以 `../08-delivery-preview/08-HANDOFF.md` 为准。原图与加工图片按用户要求清理后，`process.py`/`build.py`只能作为历史处理逻辑证据，不能再假设源图仍在；最终包通过 `verify_final.py --runtime-only` 复核。

只读 `../08-generation`，只写 `../08-delivery-preview`。不写 shared candidate、不改原始 raw/request/receipt，不生成、镜像、插值或复制动作凑帧。

在 image 工作目录使用 bundled Python：

```powershell
$py08 = 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py08 qdao_original_roster_v14_hd/recovery-20260921/08-tools/process.py --attempt idle-S-v1
& $py08 qdao_original_roster_v14_hd/recovery-20260921/08-tools/process.py --attempt all
& $py08 qdao_original_roster_v14_hd/recovery-20260921/08-tools/build.py --revision review-v1
```

process 读取 request 的 `slot`，不靠目录名推测动作。每个独立 raw 只能对应一个动作槽。需要原生至少 1024×1024、RGBA 和真实透明背景；只清除 alpha 1–8 的残留，其余 alpha 与 RGB 在整格缩放前保持。缩放统一为 `1024/max(width,height)*0.88`，不放大，不按单个人物包围盒变更比例。脚点按上身 alpha 中轴及最下方 alpha>8 定位 `[512,942]`。实际主体触边或对齐后截断时拒绝处理。输出含源、清边、缩放、对齐的 SHA 与操作链；模型和质量只采用实际 receipt 披露值，未知为 null。

每个处理目录的 `qa-light.png` / `qa-dark.png` 为 1024 合成检查图；`frame.png` 为正式尺寸透明派生图。raw 生成补充记录保存在此处理目录的 `raw.png.generation.json`，不回写原生图目录。早期 request 未保存 configSnapshot 时明确标为处理时补记，不能宣称请求时已有该快照。

build 总是建立新 revision，拒绝覆盖。自动排除源目录 `review.json` 中 `status: rejected`；若同槽存在多份未拒稿，必须使用 `--selection path/to/selection.json`，JSON 内容为精确映射，例如：

```json
{"walk/E/09":"walk-E-09-v2"}
```

清单逐槽记录 PNG、源 raw、请求、回执、来源记录 SHA，缺槽明确列出。每个完整16帧方向才生成浅/深底 GIF，并重读核对16×30ms=480ms；缺帧不代填。HTML支持八方向同时查看、正常512显示、1:1放大、浅深底、暂停逐帧、独立站立，以及15→16→01→02接缝模式。GIF及接触表只做预览缩小，runtime保留1024。

`smoke-idle-s-v1` 是工具实测快照，仅0walk+1idle，不是交付齐套。S idle 经1024浅深底目视未见彩色残边或截断；完整动作美术、接缝与浏览器播放仍需实际检查。脚本始终保留 `visual_approval: false`、Unity/正式客户端未验收；不会把库存完整当成美术通过。
