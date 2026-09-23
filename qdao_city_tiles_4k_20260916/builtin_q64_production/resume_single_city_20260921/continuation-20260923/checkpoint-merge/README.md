# 共享台账针对性合并

`merge_checkpoint.py` 默认只有 `prepare`，不会直接更新共享文件。`apply` 必须另行传入已经审阅的 `plan.json` SHA。本目录只处理 JSON；不生成、移动、删除或修改图片，不调用 Git。

## 当前结构与更新范围

2026-09-23 首次只读核对时，当前城市 ledger 为 8 个完整候选、248 个缺少完整候选、正式验收 0；256 个坐标、480 条相邻边、225 个四块交点全部存在。根部的 24 候选、392 原生细节、110 返修是历史字段，不能代表清理后的当前实存文件。当前单城进度由 `activeProductionRun` 指向的 session / ledger 决定。

脚本从五个**实时对象**合并，保留未认识字段、旧历史、`sourceRetention`、冻结交接记录和历史数组。更新：

- ledger 中显式选用坐标、当前实际存在的完整 PNG、邻接覆盖计数；正式与整城 gate 始终为 0 / false。
- session 的选用候选、完整坐标数、剩余坐标数、当前原生源实存清单，以及 ledger 的真实 SHA。
- status / catalog / current-batch 的 `activeProductionRun` 当前指针、SHA 和实存数；status / catalog 的 `currentBatchSha256`。
- catalog 的本外观增加 `currentSelectedCandidates`。旧 `currentCandidates` 和根 `candidates` 是已注明历史含义的文本，不冒充当前图。

`nativeRecords`、`repairRecords`、`newNativeDetailCount`、`newNativeRepairCount` 保留历史语义。新 `retainedNativeInventory` 按当前实际 PNG 字节、尺寸和生成记录统计。现存拒稿/回退小片在被清理前会算入“实存源”，明确不代表选用、成品、工具调用次数或验收通过。扫描覆盖旧源记录、`native` 目录和 session 中 `*.png.generation.json`；其他格式的真实原生返修必须通过 `additionalNativeSources` 显式传入。

## 输入

所有当前输入路径必须在 ART 制作根内，可以是绝对路径或相对 ART 的路径；输出当前指针统一是相对 ART 路径，旧历史路径不改写。

```json
{
  "schemaVersion": 1,
  "selectedCandidates": [
    {
      "tile": "r08_c07",
      "file": "builtin_q64_production/resume_single_city_20260921/.../r08_c07.png",
      "sha256": "明确选用的 PNG SHA256",
      "pixels": [4096, 4096],
      "status": "selected_local_candidate_external_reviews_pending",
      "record": {"file": ".../repair.json", "sha256": "真实 SHA256"},
      "qa": {"file": ".../c07-review.json", "sha256": "真实 SHA256"},
      "scopedLocalContinuityPassed": false
    }
  ],
  "modelCapabilityEvidence": {"file": ".../model-capability.json", "sha256": "真实 SHA256"},
  "additionalNativeSources": [
    {
      "file": ".../repair-native-1254.png",
      "sha256": "真实 PNG SHA256",
      "kind": "repair",
      "record": {"file": ".../repair.json", "sha256": "真实 SHA256"}
    }
  ],
  "localReviews": []
}
```

选图 QA 文件必须实际包含该选图 SHA。脚本不替代美术审阅，也不依据记录文件名推导“通过”。新选图涉及的外边与交点全部变为 pending。旧 scoped 记录只在原 ledger 的整个候选 SHA 元组完全不变时继承，继承依据保存为旧 ledger SHA，不宣称刚刚目检。

如确实已有新鲜同版本外边/交点审阅，`localReviews` 每项采用：

```json
{
  "id": "r08_c07|r09_c07",
  "candidateSha256ByTile": {"r08_c07": "选图 SHA", "r09_c07": "邻图 SHA"},
  "result": "passed",
  "evidence": {"file": ".../real-review-binding.json", "sha256": "真实 SHA256"}
}
```

`result` 仅限 passed / failed / pending；evidence 文件必须实际包含所有关联 PNG SHA。四块交点必须传完整四个 SHA。即使 scoped 通过，整城 gate 仍为 false。

## 两阶段执行

```powershell
& $python .\merge_checkpoint.py prepare --selection '明确选图.json'
```

prepare 会建立全新 transaction 目录，保存五文件原字节、selection 原字节、拟写文件、源实存清单、plan；最后重新比较所有共享文件与依赖。检查 `after`、plan summary、选图 QA 和所有字段差异后，才执行：

```powershell
& $python .\merge_checkpoint.py apply --transaction 'transaction 绝对路径' --reviewed-plan-sha256 '实际已审阅 plan SHA'
```

apply 使用 Windows `CreateFileW` 零共享模式同时持有五个目标的独占句柄，并持有当前依赖的只读零共享句柄。所有目标和依赖全部 SHA 通过后才开始按 ledger → session → batch → catalog → status 写入；每文件刷盘并从同一句柄重新验 SHA。无关闭重开造成的 CAS 间隙。多文件写入不是伪称原子的事务：每次写入前后持久化 journal；失败记录 attempted / committed / 实际 SHA，不自动回滚，更不覆盖新并发内容。任何已尝试事务禁止盲目重试；先检查 receipt 和原字节备份。

同一时段仍有生成/清理任务时应协调后重新 prepare：清单的 observedAtUtc 是真实观察时间，不是未来时刻的实存承诺。依赖被删除、内容改变、共享 JSON 并发变化都会使 apply 在首写前中止。

## 已验证范围

`check_safety.py` 只创建本目录下隔离的 JSON fixture，不打开真实五个共享文件。已验证 Windows 第二句柄被拒绝、五文件成功写入、单个目标 CAS 冲突全组零写入、注入第三文件失败后的部分提交日志。`prepare-smoke-selection.json` 是空选图的演练输入，**不是 root 审定的选图清单**；演练 transaction 不应应用。真实选图需重新 prepare。
