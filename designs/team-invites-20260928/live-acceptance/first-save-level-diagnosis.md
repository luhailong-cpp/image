# 首次存盘前等级未知造成在线名单漏人的修复

2026-09-29 真实验收命令：`run-robot.ps1`。

`result-20260929-055518.log` 记录两个本次随机测试账号 2202、2203 经 Gateway/Gate 正常进入场景，好友申请与接受均成功。RPC 12 返回目标 2203：在线、名称“道友heuewr”、职业 1、性别 1、归属区 1，但等级未赋值（protobuf 为 0）。旧在线目录要求 `level > 0`，会把这类玩家隐藏。

已核实并排除错误字段：Friend 与 Team 均读 `PlayerAllData.player_database_data.level_component.level`。`proto/common/database/player_cache.proto` 定义这是跨区/退出保存的完整快照。`cpp/libs/services/scene/player/system/player_lifecycle.cpp:2366` 先反序列化快照，2369–2372 在首次注册时只把 Scene ECS 等级置为 1；没有立即回写 Redis 展示快照。

仅对本次测试角色做 GET 的 `probe-test-profiles.go`，在它们正常退出后返回：

```text
test_player_id=2202 cached_level=1 registration_timestamp=1790675719 name=道友10kwp3 class_id=1
test_player_id=2203 cached_level=1 registration_timestamp=1790675721 name=道友heuewr class_id=1
```

因此等级 0 是存盘展示快照尚未知，不能作为邀请资格或在线身份门槛。修复仅删除该门槛，原样返回 0，客户端显示“—”；不会伪造 1，也不会对存档做补写。姓名、职业、会话 ONLINE、profile/session ID 与归属区验证全部保留。

回归 `TestOnlineDirectoryKeepsOnlineNewPlayerBeforeFirstSnapshot` 使用真实 Redis 协议接缝（miniredis）复现“有姓名职业且在线的新角色没有 level_component”。旧实现只返回已存盘角色，`level-regression-red.log` 为失败证据；修复后应返回新角色且等级仍为 0，同时空姓名、空 ID、错误 ID、自身仍被排除。好友资料和在线目录字段也要求一致。

真实验收通过各测试角色自己的只读属性面板 RPC 167 取得实时等级，要求 RPC 12/119 的已知等级与之严格相同；未知 0 可以保留。周期存盘可能在两次读取之间将 0 补成 1，因此不要求两份跨时间缓存快照逐字节相等。保留在线能力位、按姓名/编号搜索、同区、排除自身、邀请推送/接受与退出变离线等原始断言，避免把漏列问题改成测试静默放行。
