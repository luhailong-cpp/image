# Original 00–22 发布入口

`publish_original_roster_v13.py` 默认只读 dry-run，默认检查全部 23 个正式 ID。未批准、缺图或证据过期的候选返回 `blocked`、`writesPerformed: false`；已有单个完整候选时应使用明确的 `--character`，默认全部23人仍要求每人都完整通过。不创建占位 PNG，不改候选审核状态，也不更改吕洞宾/V12/V11资源。

```powershell
python E:/work/image/qdao_original_roster_v13/tools/publish_original_roster_v13.py
```

每个候选必须先由现有 `approve.py` 完成真实视觉审核封存，再由 `verify.py --require-visual` 得到最终验证。发布入口重新执行内存中的独立重建验证，并复核：

- 原身份与指定提交 `9adcf9291e4a867601868889a5965f3cd48630ba` 的肖像 SHA；不接受 Lu ID 或道童别名。
- 145 张最终 PNG：128 行走、8 独立站立、8 条带、1 肖像。
- 16 帧、30ms、480ms、实际 alignment v2、脚线 471。
- manifest/QC/visual-review/validation 与所有最终图片的精确 SHA，以及真实生成来源、分方向审核和视觉证据。

完整批准后，先对一个独立 Unity 项目 dry-run。项目必须位于 `E:/work/tmp`，且已经复制当前客户端代码，包括 schema 2 的 Sandbox 观测测试。以下目录是下一轮要准备的项目名称，不是当前已验收的存在证明：

```powershell
python E:/work/image/qdao_original_roster_v13/tools/publish_original_roster_v13.py --character 01_ice_sword_girl --stage-project E:/work/tmp/qdao-original-candidate-next
```

只有 dry-run 显示 `ready_dry_run` 后，显式追加 `--execute` 才会复制资源。目标固定为 `Assets/Resources/World/Characters/QdaoOriginalRosterV13/<原ID>`，输出 145 PNG 与 `appearance.json`、原字节 `manifest.json`、原字节 `validation.json`。同 ID 已存在且字节相同则跳过；不同版本不会被覆盖。写入先在项目 Temp 完整校验，再改名进入最终目录；有目标 Unity 锁文件则拒绝。

候选资源进入独立项目后，保存完整输入快照，分别真实运行 EditMode、PlayMode。运行器支持 `-Project`，并要求快照里的项目路径一致。使用新 Run 名，保留每次启动 JSON、日志与 XML。

```powershell
& E:/work/image/qdao_original_roster_v13/tools/run_unity_tests.ps1 -Platform EditMode -Project E:/work/tmp/qdao-original-candidate-next -Run original-candidate-next -InputSnapshot E:/work/image/qdao_original_roster_v13/runtime-validation/input-snapshot-next.json
& E:/work/image/qdao_original_roster_v13/tools/run_unity_tests.ps1 -Platform PlayMode -Project E:/work/tmp/qdao-original-candidate-next -Run original-candidate-next -InputSnapshot E:/work/image/qdao_original_roster_v13/runtime-validation/input-snapshot-next.json
```

正式发布仍先 dry-run，必须提供这次实际 Original 观测、输入快照和两套 Passed XML：

```powershell
python E:/work/image/qdao_original_roster_v13/tools/publish_original_roster_v13.py --character 01_ice_sword_girl --publish-project E:/work/mmorpg-client --runtime-report E:/work/image/qdao_original_roster_v13/runtime-validation/original-candidate-next/city-captures/runtime-observed-appearances.json --input-snapshot E:/work/image/qdao_original_roster_v13/runtime-validation/input-snapshot-next.json --editmode-results E:/work/image/qdao_original_roster_v13/runtime-validation/original-candidate-next/editmode.xml --playmode-results E:/work/image/qdao_original_roster_v13/runtime-validation/original-candidate-next/playmode.xml
```

正式 gate 要求源代码与实际测试快照一致、启动记录绑定同一候选、真实 Original 8向×16帧库存、实际运动16姿势、独立idle及真实motor证据。实际速度、480ms周期、周期行进距离及控制器源码与已经保存的 V12运行基线比较；不接受手填 `speedUnchanged=true`。schema 2 的 `testedOriginalCount` 必须包含此次角色，0不能发布。全部符合后才能显式追加 `--execute`。

首次无Original素材的历史基线：`runtime-validation/contract-run1` 为 EditMode329/329、PlayMode21/21；原角色实际启用0，旧8人V12。此前泛化观测代码的独立编译记录在 `observer-preparation`，只读门禁检查在 `publication-tool-validation`。后续每个角色仍需对应真实完整候选的新运行。

当前已实际完成 `runtime-validation/accepted-originals-run1`：00 道童与 02 火符少年 stage 后 EditMode329/329、PlayMode21/21 通过，schema2 真实 `testedOriginalCount=2`。25,347 个 Play 输入在运行前后逐 SHA 零变化；真实 16 姿势、30ms/480ms、speed9、motor 与停止 idle 均通过。正式 publisher 已将两人 296 个完整文件接入 `E:/work/mmorpg-client`，独立审计确认与实际测试输入一致，原有 2,222 个角色文件不变。详见该 Run 的 README、publish-execute.json 与 formal-publication-audit.json。


`runtime-validation/accepted-originals-run2` 随后实际验收并正式接入01冰剑少女：新输入仅加入01，EditMode329/329、PlayMode21/21通过，schema2真实Original3（00/01/02），25654个Play输入运行前后逐SHA零变化。正式01的148文件与实测输入一致，已有2518文件（含00/02与V12）不变。03另在Run3处理，没有混入Run2。


Run3（2026-09-18）已真实验收并正式接入03莲花医者的512px V13：Edit329/329、Play21/21，实际Original4、selected12；25961个Play输入运行前后0增删改。148新文件与实测输入一致，旧2666角色文件0增删改。详见accepted-originals-run3。用户随后要求提高原生细节与帧分辨率，V14 HD独立推进；本次03仅作为已验证512回退，不计HD完成。
