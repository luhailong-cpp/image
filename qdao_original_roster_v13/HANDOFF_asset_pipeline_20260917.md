# asset_pipeline 交接 — 20260917

用户已要求移交另一窗口。本代理已停止启动新绘图、新 Unity 轮次和新发布；下文是可继续执行的准确状态，不是剩余工作已完成声明。

最后只读核对时间：**2026-09-18 03:48:31 UTC**（工作记录文件名依用户指定保留20260917）。没有活动中的 Unity、publisher、input-capture 或本工作预览 Python 进程；8874 没有监听。两个工程的 `Temp/UnityLockfile` 均不存在。不要把旧 PID/session 当成仍运行。

## 路径与范围

- 工作根：`E:/work/image/qdao_original_roster_v13`
- 正式工程：`E:/work/mmorpg-client`
- 唯一隔离验证工程：`E:/work/tmp/qdao-original-live-candidate-20260917`
- 新运行资源族：`Assets/Resources/World/Characters/QdaoOriginalRosterV13/<原ID>`
- 原身份来源：指定提交 `9adcf9291e4a867601868889a5965f3cd48630ba` 的23角色，精确ID、源路径、SHA看 `inventory.json`。额外旧道童是00别名，不是第24人。
- 现有V12/V11、吕洞宾目录保留；Original V13用alignment v2/root `[256,471]`，不要混用吕洞宾V13的v3合同。
- 正式工程当前实际目录仅 **00_reference_topright_boy、01_ice_sword_girl、02_fire_talisman_boy**。隔离工程另有 **03_lotus_healer_girl**，共4名Original。

## 已正式完成（不可再改封存候选）

| 角色 | manifest SHA | QC SHA | validation SHA |
|---|---|---|---|
| 00_reference_topright_boy | 2c326ade53a0a05899e397525cc55404242727917a9961d12e29cdfd19e46394 | cc63a0e2721b2e2ea3a153120ecb7c0c7ee24d19df3ef6fcd7732534b29cd82e | a64b32af64f1f3d16530356f6c6c2a36961becd9718b0a604855d25a43017f50 |
| 01_ice_sword_girl | 1250c568a803c55e95cc6374ff983cdcf0ccc78cb5d0395807f0357c33f2d729 | 64636dbb5e8baf746274b4adc34180897c3c93859a6a8256051303122733780a | fac5b3630b713d703d4267805fba8cb0f77f2a23cc3a7ea9a1a7e82d50cd1e9d |
| 02_fire_talisman_boy | 5ec4bdd5fa0a760393174a7522c9960d80f5bd9682137f2e962745b291c3f3be | 6a76fe0f5332a64a6ef2567aade13e698f7a181779344b4f395ef7ff49baef51 | 9b5684b0da63736ad3a3ba3e29dccddb6671b5501b5fe0cebd8d9daca31cdbcf |

每人145PNG：128实绘walk、8独立idle、1原4096完整降采样肖像1024、8条带。正式每人148文件：上述145PNG + 原字节manifest.json + 原字节validation.json + appearance.json。137张图是客户端运行必需图片，8条带另保留。

**Run1（00+02）**：`runtime-validation/accepted-originals-run1/`

- 独立项目实际 EditMode329/329、PlayMode21/21，0失败/跳过。
- schema2 `testedOriginalCount=2`、`selectedAppearanceCount=10`；两人真实16帧/30ms/480.00003ms/speed9，实际motor各4.800003单位、16姿势、2静止帧内独立idle。
- Play输入25,347文件，SHA `302a87555ea02e4f7e29d1328adfa0541450984e42bff54c53848c681ee3f276`。post全量比较0增删改。
- 正式发布记录 `publish-execute.json` SHA `a218c4f81af2fb72658ee00d22ced657aecce0b5604a4fd84336b1bdef36cd05`。
- `formal-publication-audit.json`：296新文件精确匹配实测输入；原2,222角色文件0增删改。

**Run2（只新增01）**：`runtime-validation/accepted-originals-run2/`

- 实际 EditMode329/329（15:14:03–15:15:53 UTC）、PlayMode21/21（15:23:43–15:24:03 UTC），0失败/跳过。
- schema2实际Original3（00/01/02）、selected11；三人都真实motor、16采样姿势、独立idle和speed9/480ms通过。
- Edit输入25,495文件，相比Run1 post仅新增01的148文件，旧输入无变化。随后159个新01 `.meta` 由Unity生成。
- Play输入25,654文件，SHA `22085d15234754ae4d1197243163ddf589b761fbaea24d206b1e738f9018229a`；`post-playmode.json` SHA `f5209a1098d7bfb79166c868b061b30aba7ff470aaa211fd4bf7249bf0b2879f`，全量0增删改。
- 正式发布记录SHA `aff27600327c130c530f64c14478de56d8f988fcce66df42d507a74254f9b6f0`；148新文件与实测输入一致；已有2,518文件（含00/02及V12）0增删改。
- 01 appearance SHA `d38bc3b8e43461dbd277447b69d32d011283d3e823338a810979769639e43d97`。

每个Run的README、`runtime-result-review.json`、原XML/log/launch/completion、`city-captures/runtime-observed-appearances.json`和`formal-publication-audit.json`齐全。实际看过00/01/02各自的主城截图。截图在各自motor路线之前，所以朝向不必与最后idle观测相同。`approved-roster-runtime.png`是旧8人的合并图，不能说它包含全部Original。

运行范围是**真实离线天墉沙盒和真实CharacterController**，不是在线登录。每个Original真实motor只跑一条N路线；另一个Animator测试覆盖八方向，不能混称八条真实导航路线。旧 `contract-run1` 的Original0报告只用于已绑定的V12速度基线，不能用于任何新Original接受。

## 03 当前准确状态：已stage，未跑Run3 Unity，未正式发布

候选：`candidate/03_lotus_healer_girl/`，已完成真实修图、实际视觉审查和封存。

- manifest：`a22f6256ecb15cc4d39dd9dc5272895aca4e875b354f7ac5aa88390a18ceb5e4`
- QC：`2b0486e01b42c2412653167f19dcd137b8f9902f55f6a5151dc3fd7f24aac7cc`
- validation：`738934da3334a240d86667a99b0223ad105a05cace58eef86b1138234b0ef8a2`
- visual-review：`3035ce79c36c40d2afdc3c3c1fef2db5322f88f582b484bf16a48c5fa6440f43`
- appearance：`3ca7f44bbf467cc10c64c750e270f705f8dbf04834ee56287ee1fd14077e5af8`
- 有效视觉输入是 `review/fresh-review-input-v2.json`。第一次 `fresh-review-input.json` 保留withdrawn，不能拿它审批。
- 有效封存历史：`review/approval-history/20260917T151643-505b9f1d/`；`approve-execution-v2.log`退出0。SW07–11反向鞋尖已真实重绘并重新审核。

`runtime-validation/accepted-originals-run3/stage03-dry-run.json` 由client_v13只读执行：ready、blocked[]、writesPerformed=false。随后本代理**已经**执行stage，`stage03-execute.json`为completed、writesPerformed=true、148文件进入隔离工程；不要重复stage。

最后stage调用session **48459已经退出0**。其创建记录时间15:48:23 UTC是调用开始时间，不是结果完成时间。没有后续活动中的stage/Unity/快照/发布进程。

Run3目前仅有：

- `stage03-dry-run.json`、空的stderr、`stage03-execute.json`
- `formal-protected-characters-before.json`：正式现有**2,666文件**，包含00/01/02及V12，无已发布Original被排除。
- `reviewed-code-comparison.json`：当时12个相关C#源码在正式/隔离逐SHA相同。
- `bind_inputs.py`：支持从Run1、Run2、Run3实际stage记录绑定所有候选和新快照。
- `audit_formal_publication.py`：只接受本轮正式发布03，保护其余已有角色。
- `progress.json`已修正为交接后stage完成、未开新Unity状态。

**尚无** Run3 `input-editmode.json`、`input-playmode.json`、Edit/Play XML/log/launch、runtime observations或publish结果。03不能被说成游戏验收通过或正式接入。

## 接手后按顺序执行（这些命令在交接时未执行）

先阅读 `tools/PUBLISHING.md` 和publisher实现。检查工程没有被另一个窗口使用；不要重建/覆盖整个隔离工程，不要混入04–07。若文件已经被接手者创建，先检查实际状态，不覆盖证据或盲目重跑。

工作目录统一：

```powershell
Set-Location E:/work/image/qdao_original_roster_v13
```

1. 03已stage。建立全新的Run3 Edit输入，并封存当前capture工具字节。capture覆盖Assets/Packages/ProjectSettings/Library/PackageCache，检查symlink/junction/hardlink及文件稳定性。预计只比Run2 post多03的148文件，但必须看实际比较。

```powershell
python -X utf8 -B tools/capture_unity_inputs.py --project E:/work/tmp/qdao-original-live-candidate-20260917 --output E:/work/image/qdao_original_roster_v13/runtime-validation/accepted-originals-run3/input-editmode.json --compare E:/work/image/qdao_original_roster_v13/runtime-validation/accepted-originals-run2/post-playmode.json
python -X utf8 -B runtime-validation/accepted-originals-run3/bind_inputs.py --phase editmode --character 00_reference_topright_boy --character 01_ice_sword_girl --character 02_fire_talisman_boy --character 03_lotus_healer_girl
```

绑定应为592资源、12当前核心源码、恰好4个Original目录。不要把绑定成功当作Unity已通过。若正式相关源码已改变，不能回退别人的代码来匹配旧测试；审核当前变更后重新准备同版相关输入及新Run证据。其它地图/UI工作不要覆盖。

2. 实际EditMode，检查XML Passed/0失败后才继续。

```powershell
& ./tools/run_unity_tests.ps1 -Platform EditMode -Project E:/work/tmp/qdao-original-live-candidate-20260917 -Run accepted-originals-run3 -InputSnapshot E:/work/image/qdao_original_roster_v13/runtime-validation/accepted-originals-run3/input-editmode.json -Scope 'Fresh run3 for sealed03 alongside accepted00/01/02; no later Original candidates included.'
```

3. Unity退出后捕获Play输入（不要省略Unity新生成的meta），绑定后实际PlayMode。

```powershell
python -X utf8 -B tools/capture_unity_inputs.py --project E:/work/tmp/qdao-original-live-candidate-20260917 --output E:/work/image/qdao_original_roster_v13/runtime-validation/accepted-originals-run3/input-playmode.json --compare E:/work/image/qdao_original_roster_v13/runtime-validation/accepted-originals-run3/input-editmode.json
python -X utf8 -B runtime-validation/accepted-originals-run3/bind_inputs.py --phase playmode --character 00_reference_topright_boy --character 01_ice_sword_girl --character 02_fire_talisman_boy --character 03_lotus_healer_girl
& ./tools/run_unity_tests.ps1 -Platform PlayMode -Project E:/work/tmp/qdao-original-live-candidate-20260917 -Run accepted-originals-run3 -InputSnapshot E:/work/image/qdao_original_roster_v13/runtime-validation/accepted-originals-run3/input-playmode.json -Scope 'Actual run3 real motor and animation for Original00/01/02/03: 8x16 inventory,30ms480ms,unchanged speed9,dedicated idle and fallbacks.'
```

4. 读取本轮实际XML和 `city-captures/runtime-observed-appearances.json`。预期schema2 Original4、selected12，但只认实际报告。03需真实manifest/activation三SHA、全部8方向库存16/unique textures16、实际motor16采样姿势/距离>3/speed9/480ms/专用idle。注意浮点480.00003等用容差。看03实际地图PNG；原始报告不手工改写。

5. Unity退出后完整post输入比较；若动态字体出现真实变化，保留并说明，不能回滚制造零差异。核心代码或候选变化需处理后重跑匹配证据。

```powershell
python -X utf8 -B tools/capture_unity_inputs.py --project E:/work/tmp/qdao-original-live-candidate-20260917 --output E:/work/image/qdao_original_roster_v13/runtime-validation/accepted-originals-run3/post-playmode.json --compare E:/work/image/qdao_original_roster_v13/runtime-validation/accepted-originals-run3/input-playmode.json
```

6. 真实通过后，正式publisher先dry-run。它会再次独立重建136源帧，通常数分钟。可以与只读post快照并行，但实际execute必须在结果和变化都核对完之后。

```powershell
python -X utf8 -B tools/publish_original_roster_v13.py --character 03_lotus_healer_girl --publish-project E:/work/mmorpg-client --runtime-report E:/work/image/qdao_original_roster_v13/runtime-validation/accepted-originals-run3/city-captures/runtime-observed-appearances.json --input-snapshot E:/work/image/qdao_original_roster_v13/runtime-validation/accepted-originals-run3/input-playmode.json --editmode-results E:/work/image/qdao_original_roster_v13/runtime-validation/accepted-originals-run3/editmode.xml --playmode-results E:/work/image/qdao_original_roster_v13/runtime-validation/accepted-originals-run3/playmode.xml | Tee-Object -FilePath runtime-validation/accepted-originals-run3/publish-dry-run.json
```

确认ready、blocked[]后，在完全相同命令中追加 `--execute`（放在管道之前），输出改为 `publish-execute.json`。用户此前已授权正式接入；本轮交接停止并不等于要求另一次发布许可，但不得绕过实际门禁。代码会拒绝Unity锁文件、不同版本目标覆盖、缺图/陈旧视觉/不匹配运行证据。

7. 完成后再执行独立保护审计：

```powershell
python -X utf8 -B runtime-validation/accepted-originals-run3/audit_formal_publication.py
```

应核对03的148文件与本轮实测输入一致，旧2,666文件无变化。记录实际结论，更新本轮README/progress/PUBLISHING后再推进后续角色。

## 07 原角色：只核对身份，完全没有开始绘制

精确ID：`07_moon_shadow_assassin_girl`，名字月影少女。

原图：`E:/work/image/qdao_original_roster_v13/baseline/q_daoist_character_pack_4096/07_moon_shadow_assassin_girl_transparent_4096.png`

4096×4096 RGBA，SHA `8ccc7e9118ed1ca608a407687e5a76cf392b1f694ef7737ccc28536caae84bfc`，与指定提交一致。

**本代理没有07图片生成调用，没有未保存的07生成结果，没有07 prompt/receipt/raw，也没有07 generation或candidate目录。原图尚未实际显示目检。** 只读取了inventory和技能文档，随后用户要求交接。下一窗口不要假定07 idle或S锚点已画。

原安排是在03运行等待间隙绘制07原肖像、8独立idle、S四关键姿势。只写07专属generation/candidate，绝不加入正在验证的Unity输入。先看原图锁定大头圆脸短身，不重设计原肖像；肖像从4096完整降采样1024。使用真实内置image_gen绘图，后续型号与最高画质遵守[统一设置](../config/image-generation.json)和[执行策略](../docs/IMAGE_MODEL_POLICY.md)，沿用已获内置授权，不擅自切换计费API。工具后端隐藏时仍诚实保留model_requested与actual未断言的区别。

参考入口：`imagegen`和`generate2dsprite`技能。本机view_image/本地referenced_image_paths曾有ACL错误；已验证可通过elevated exec读取原图/显示PNG或JPEG，再用最少 `num_last_images_to_include`。生成原图从工具实际output_hint路径复制，不伪造来源、不用代码绘画充当新动作。留存prompt、原raw、实际tool receipt。

旧角色可靠做法：先8向中立idle（2行4列，必须实看方向，E/W有可能生成交换，用显式idle-order诚实映射），定一次common_scale（既有常用0.88，但先按07原图实际判断）。S关键姿势2×2对应1/5/9/13，1和9相反承重腿，5和13分别经过。后续25/50/75%是动作目标，必须真实生成并视觉判断，不是程序插值。不合格阶段可单帧/单一区间真重绘。支持原生1×1、1×2、2×1、2×2、2×4、4×4及显式output-frames/source-cell-indices；不得伪造原生网格。

## 工具与不能踩的坑

- `tools/publish_original_roster_v13.py` 默认dry-run，fresh verify在内存中运行，**不改**已封存validation。独立stage项目限E:/work/tmp；正式发布需真实本轮报告/快照/两份Passed XML及launch绑定。
- **不要**对已封存00–03运行 `pipeline review/import`，会把状态回到pending；不要单独运行缺少 `--require-visual` 的verify，可能覆盖最终validation。使用现有publisher足以重新只读重建。
- 每人完整145PNG，128walk全部真实生成＋8独立idle；旧Lu固定64奇数帧SHA规则不能套到Original23。
- 固定整格共同尺度、整数平移、脚线471；不逐帧bbox缩放、不变形、不重复帧补数。源格真实触边必须重绘，不能用平移掩盖。透明源仅记录化alpha<=8噪声清理；不能擅自放宽为32。
- root新增 `--chroma-profile purple-preserve`，记录阈值50/75，适合原图紫衣被标准100/150误抠的明确场景；默认仍100/150。先目检再选。vendor未改，verify只接受记录的这两组阈值并重放。
- `import_sheet`已用getattr默认standard兼容旧SimpleNamespace入口。01正式execute用新verify重建全部136旧100/150记录，fresh结果与封存逐项一致；03stage也完成。旧候选没有重加工。
- Run2 `processing-tools-at-runtime/`保留修改前pipeline/verify/publisher/vendor；`processing-tools-at-publication/`与`publication-tool-start.json`保留发布启动时版本。随后仅getattr的小修已记录当前SHA如下。

最后检查工具SHA：

| 文件 | SHA256 |
|---|---|
| pipeline.py | b77cf4907b8be338912fbe352311702de2ea919a3b721b273ff90bb587f84ad3 |
| verify.py | ad079a51003ac1045bffa40609910f23f2e987c9bf017781e92711e2976595a5 |
| publish_original_roster_v13.py | 6a96c21d073a41442226c29a4ab80ad0fbcee83687711711eec2f093f2388f47 |
| capture_unity_inputs.py | 197e624c9bff79435c840d5db1ad3c46732896f9e98de67c2408ca8040cbc662 |
| run_unity_tests.ps1 | 6fde9cbf147db1de0cf01f493db25fbf68a688c431f9276bcbdb617c3c86beb0 |

本机普通exec/view_image历史有ACL helper问题，已授权范围内使用 `exec_command` require_escalated完成读写/Unity。曾因额度导致自动审查不可用，后已恢复；不要把那次失败当作动作已经执行。后台Unity必须Hidden。不要跨shell拼递归删除；这里不需要删除或重建工程。

旧过程标识，仅追溯：Run1 Play PID33604/session18940已结束；Run2 Edit PID55152/session7864、Play PID52032/session48335、正式publish session20261均已结束；Run3 stage session48459已结束。之前预览PID41664现在不存在，8874无监听。如需恢复画面预览，可在确认端口空闲后新开 `python -B tools/serve_preview.py --port 8874`，不要认为旧服务仍在。

交接文件写完后本代理停止业务写入，不会自动推进下一步。
