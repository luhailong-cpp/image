# 四种组队邀请入口

2026-09-28。参考用户提供的两张游戏截图中的玩家列表和角色操作入口；画法、材质及控件复用项目已确认的 [结伴同游 TeamV2](../team-ui-v2/README.md)，没有复制参考游戏的美术。

## 游戏入口

- 组队：按 **T → 邀请道友**，打开「邀友同游」。未建队时可从聊天邀请进入并创建队伍。
- 好友邀请：真实好友名单，显示姓名、等级、职业、头像及在线状态。
- 周围玩家：当前场景 AOI 内的真实玩家，排除自己。远端资料尚未同步时显示真实编号，头像和等级只展示已取得的信息。
- 在线玩家：同一归属区服的在线角色，支持服务端姓名／编号搜索和分页加载，包含已经是好友的玩家。
- 聊天邀请：最近实际聊天的玩家；聊天头像 → 仙友小传 → **邀请组队**。没有在线证据时显示“状态待确认”，邀请提交仍由服务端检查。
- 保留玩家编号直接邀请、创建队伍、刷新、上一页／下一页／加载更多。

所有入口共用现有 `TeamClient.Invite → InviteToTeam`。只在权威快照确认后显示“已邀请”；对方接受后才入队。自己、已在队伍、已邀请、已知离线、满员、非队长与在途请求均有明确提示；关闭覆盖窗口恢复组队窗口的输入和焦点。

## 实际 Unity 界面

两种分辨率共 16 张截图曾用于验证文字字形、操作状态与布局，由生产 Unity 控件渲染，名单为离线测试样例。2026-10-15 已按用户要求删除这些图片及 11 张联机验收截图，保留文字验收与来源记录；逐文件清单见 [截图清理记录](../../docs/screenshot-cleanup-20261015.json)。

## 实现与验证

实际客户端：`E:/work/mmorpg-client`；服务端：`E:/work/xuanming-server-mmo`。

- 完整客户端运行时代码 Roslyn 编译：零错误。
- Windows 客户端构建成功：`E:/work/tmp/wuxing-team-invites-player-20260928/mmorpg.exe`，0 编译错误。全项目构建记录含 499 条警告（包括既有推理包 shader 及其他开发工具脚本警告），本轮未修改这些模块。
- Unity EditMode：**157/157**；PlayMode：**8/8**。原始 XML 与运行记录在 [qa](qa/)。
- 邀请目录独立 NUnit 回归：**17/17**，覆盖协议序列化、异步旧回包、查询合并、游标、空页、断线换角与已知／未知在线状态，见 [记录](integration/verification-data/result.json)。
- Friend 服务完整测试、`go vet`、构建：见 [服务端证据](integration/verification-server.json)。
- 在线目录复用 `RecommendFriends` 的显式 `online_only` 分支，要求回包 `online_directory=true`，旧服不支持时明确报未开放；不会把随机好友推荐误显示成在线名单。
- 在线目录每页限量、有请求限流和截止时间；Redis SCAN 在玩家上下线期间不是跨页快照，客户端按玩家 ID 去重，刷新重新读取。
- 2026-09-29 双账号真实协议验收已通过：Gateway/Gate 登录、RPC 12 双向好友资料、RPC 119 按编号与昵称搜索并翻页、邀请推送和邀请列表、接受后双方两人同队、离线后好友状态更新及在线目录排除。见 [真实联网证据](live-acceptance/verification-live.json)。
- 本次续验修复两处边界：聊天候选不再继承旧好友缓存的离线判断；新角色首次存盘前等级未知时仍可出现在在线名单。两项均保留先红后绿的回归证据。等级未知时省略数值，不伪造等级。

## 本地运行状态

34 个客户端／服务端交付文件已同步并逐个核对 SHA256，见 [同步核验](qa/source-verification.json)。新版 `friend.exe` 已安装到 `E:/work/xuanming-server-mmo/bin/go_services/friend.exe`，原程序保存在该服务器的 `run/backups/team-invites-*`。

2026-09-28 的首次联机验收受 Docker/MySQL 未就绪阻塞。2026-09-29 续验时基础设施已恢复，已启动并验证修复后的本地好友服务（端口 50400），完整真实协议验收通过。没有清理数据库、重置 Docker 或删除持久卷。验收仅创建随机测试账号，测试队伍和好友边已清理，历史用户未被修改。

当前运行版本及哈希见 [好友服务部署证据](live-acceptance/friend-level-fix-deployment.json)；可重复协议验收见 [run-robot.ps1](live-acceptance/run-robot.ps1)。`integration/friend-invites.exe` 与部署脚本所读验证记录已更新为本次修复后的最终版本；服务已运行时无需重复部署。联网功能依赖数据库、Redis、etcd、Kafka、data_service 与组队服务运行。

环境附注：运行中的 Match 二进制尚未包含另一次提交的可选队员昵称字段，旧回包的队员名由客户端显示为玩家编号；本次邀请候选名单的真实姓名已单独验证。未为该独立部署重启其他任务的服务。

同步脚本在 [integration/apply.ps1](integration/apply.ps1)，先校验原文件 SHA256，防止覆盖其他任务的改动。验证脚本在 [verify-client.ps1](integration/verify-client.ps1) 和 [verify-server.ps1](integration/verify-server.ps1)。协议由正式 `protoc` 生成，没有手改生成产物。

## 美术来源

本轮没有新生图或 AI 改图。界面直接使用客户端 `UI/Ugui/TeamV2` 正式皮肤、现有 `QdaoCharacterCatalog` 头像与项目字体；原素材模型／质量记录沿用 [TeamV2 来源](../team-ui-v2/source/generation.json)。截图属于软件渲染验证，不虚报为 GPT Image 生成。
