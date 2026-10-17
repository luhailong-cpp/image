# 组队邀请真实协议验收

2026-09-29 最终通过：`result-20260929-061513.log`，退出码 0，末行 `TEAM_INVITES_ACCEPTANCE_OK`。完整结构化结果见 `verification-live.json`；测试账号角色为 2210/2211，测试队伍 74004670217781248 已解散、好友关系已解除、会话已退出。前几次失败分别保留了真实缺陷复现和验收边界的诊断证据。

该程序通过现有 Gateway → Gate → 路由服调用正式 RPC，不直连修改 MySQL 或 Redis，也不启停服务。`build-robot.ps1` 用 Go overlay 扩展仓库现有 robot 登录/收包工具，实际仓库文件不变。

运行前需 Gateway、Gate、Scene、Login、DataService、ClientRpcRouter、Match（Team）、Friend 及其基础设施健康。区服为 1；Friend 端口 50400。由外层负责启动与版本核对。

```powershell
& './build-robot.ps1'
& './run-robot.ps1'
```

登录凭证仅由环境 `LOGIN_DEV_PASSWORD_SHARED_SECRET` 继承。未设置时沿用仓库 `start_game.ps1` 的做法，只读现有 `robot/etc/robot.yaml`，不回显、不写入新配置或日志。

每次使用密码学随机账号 `robot_tinv_<16hex>_a/b`。若登录时已有角色，程序立即拒绝，避免碰历史用户。验收包括：

- 真实登录进场，空好友/无队伍检查；A 添加 B、B 接受。
- RPC 167 只读取得各测试角色的实时等级；RPC 12 校验双向好友在线状态、姓名、职业和同区资料。缓存等级允许未知 0，已知时必须等于角色实时等级。
- RPC 119 `online_only=true` 必须返回 `online_directory=true`；按编号与姓名搜索，`limit=1` 与非空游标继续，包含好友、排除自己；与好友资料的姓名、职业、外观一致，已知等级必须等于实时面板。周期存盘在两次读取间把 0 补成 1 是合法变化。
- A 建队邀请 B，B 收到真实推送并能从邀请列表查询，接受后双方视图成员都是 A/B 各一人。
- 解散本次队伍，B 退出后 RPC 12 报离线，RPC 119 遍历不再包含 B。
- 无论成功或失败都尽力清理本次队伍、好友边或待处理申请，正常退出会话。不删除账号或角色记录。

退出码 0 且末行 `TEAM_INVITES_ACCEPTANCE_OK` 才算全部通过；失败日志带具体 RPC/断言。`result-*.log` 为真实运行证据，账号与角色编号保留以便复核。

两账号不能单独验证“非队长邀请一个未入队的第三人”：现有服务先判断目标队伍归属，B 邀 A 会先返回目标已在队伍。该场景仍由 Team 现有服务单元测试覆盖，本脚本不声称验证该分支。

当前运行 Match 构建于 2026-09-28 08:29，早于同日 11:26 的 `3c7fb8f2e` 队员昵称提交，TeamMemberView.Name 仍可能为空。本次以权威队伍 ID、成员唯一编号、在线态及区服验收接受成功；RPC 12/119 候选姓名仍必须完整。为避免覆盖其他任务的 Match 修改，不重启该服务；空的可选 Team 姓名以 `TEAM_INVITES_OPTIONAL_TEAM_NAME_UNDEPLOYED` 单独记录。

请求间隔为 2.1 秒：Gate 的 `MessageLimiter` 使用整秒时钟且以严格大于窗口才驱逐旧记录，119 配表的每秒 1 次实际需跨两个整秒。验收不修改运行限流配置。

`build-evidence.json` 记录本次直接从当前 Friend 源码执行的 test/vet/build 结果与两个二进制哈希，没有用昨天的源码 overlay 覆盖其他人的推荐逻辑修改。

首次 Unity 双实例验收遗留关系已于 2026-09-29 单独清理。当时的清理入口只允许 `robot_tui_a07a9cf9d38949ef_leader/member`，必须已有且只有一个角色，并精确匹配 2213/2212；不允许建角，只通过正式 RemoveFriend 解除这对关系。成功证据为 `unity-first-pair-cleanup.json` 与 `cleanup-20260929-064828.log`。当前清理入口已限定为下述两次后续 run，不再用于这对已清理账号。

2026-10-01 后续清理已完成：用户明确回复“允许清理本轮测试数据”后，更新后的清理入口只允许 `fcf7df80745d4021`（2216/2217）与 `d342a978cc8f456b`（2218/2219）两次验收 run。通过 `run-robot.ps1 -Mode unity-cleanup -CleanupRun <run>` 分别执行，两个进程退出码均为 0，并产生 `TEAM_INVITES_UNITY_CLEANUP_OK`。进场前验证精确账号及唯一既有角色；两对角色初始队伍均已为 0，无需解散。最终双方正式 RPC 均确认无队、互非好友，且已正常退出。账号和角色保留。完整授权、范围、哈希与结果见 `cleanup-authorized-20261001.json`，执行日志为 `cleanup-fcf7df80745d4021-20261001-100424.log`、`cleanup-d342a978cc8f456b-20261001-100457.log`。历史 `unity-fcf7df80745d4021-cleanup-provenance.json` 保留当时未获授权的拒绝记录，本次结果以新证据为准。
