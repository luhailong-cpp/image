# 装备界面接入与后端缺口

只读审计日期：2026-10-08。本文记录审计时的源码与生成物状态，不代表服务已部署或联机验收通过。本轮仅接入客户端美术，不修改服务端源码、配表或协议，不手工分配消息号。

## 本轮美术可以接什么

装备详情卡、按钮、关闭图标、期望属性窗口与复选框可以使用新的图片资源；名称、数值与交互仍由客户端控件绘制。

- 已有装备源契约可承载名称、图标、等级、职业要求、基础属性、蓝／粉／黄词条及“当前值／上限”；依据：[player_bag.proto:13](E:/work/xuanming-server-mmo-equip/proto/scene/player_bag.proto:13)、[player_bag.proto:31](E:/work/xuanming-server-mmo-equip/proto/scene/player_bag.proto:31)。绿色档仅预留，不等于已实现套装。
- 真实显示由服务端投影生成，包含名称、单位、上限和排序；职业名目前留空，因为 Class 表没有名称列。依据：[player_equip.cpp:680](E:/work/xuanming-server-mmo-equip/cpp/libs/services/scene/player/system/player_equip.cpp:680)、[player_equip.cpp:694](E:/work/xuanming-server-mmo-equip/cpp/libs/services/scene/player/system/player_equip.cpp:694)。
- “期望属性”的勾选、保存和将来对真实炼化回包的命中提醒，可以是客户端本地偏好。勾选不能改变随机概率，也不能被界面当成炼化已成功的证据。
- 有合法服务器快照时，详情卡可展示真实字段。离线演示与资源检查只能证明界面效果，不能证明炼化、穿脱或服务部署已完成。

## 现有装备代码还缺正式生成与验证

主仓 `E:/work/xuanming-server-mmo` 目前仍是旧背包契约：物品只有基础展示字段，RPC 只有 GetBag、SortBag。依据：[主仓 player_bag.proto:12](E:/work/xuanming-server-mmo/proto/scene/player_bag.proto:12)、[主仓 player_bag.proto:59](E:/work/xuanming-server-mmo/proto/scene/player_bag.proto:59)。装备扩展位于 `E:/work/xuanming-server-mmo-equip` 的既有未提交工作中，不能将其视为已合入主仓或已上线。

| 已有源码 | 尚未完成的接入 |
|---|---|
| 穿上、卸下请求均传 item_id，响应带错误及背包／装备栏两份快照；[player_bag.proto:83](E:/work/xuanming-server-mmo-equip/proto/scene/player_bag.proto:83) | 服务端消息号注册只有 GetBag=191、SortBag=192，没有穿脱号；[message_id.txt:192](E:/work/xuanming-server-mmo-equip/proto/message_id.txt:192) |
| 客户端已有穿脱调用；[PlayerFeaturesClient.cs:251](E:/work/mmorpg-client-equip/Assets/Scripts/Game/PlayerFeatures/PlayerFeaturesClient.cs:251) | 客户端 MessageIds 仍缺 EquipItem、UnequipItem；[MessageIds.cs:31](E:/work/mmorpg-client-equip/Assets/Scripts/Net/MessageIds.cs:31)、[EquipmentUI-20261007.md:115](E:/work/mmorpg-client-equip/Docs/EquipmentUI-20261007.md:115) |
| 装备属性、属性池、等级上限、条数规则四张源表和 schema 已存在 | 审计时 generated/tables 尚无对应四张表，生成版 player_bag.proto 仍是旧契约；[生成版 player_bag.proto:55](E:/work/xuanming-server-mmo-equip/generated/proto/_unified/proto/scene/player_bag.proto:55) |

这条已有装备功能的后续顺序是：正式导表 → proto-gen → 同步客户端消息号与限流表 → 编译受影响目标 → 装备回归与机器人冒烟 → 客户端真实联机验证。不得用占位消息号绕过生成流程。源码交接记录也明确标为待验证：[equipment-attributes.md:534](E:/work/xuanming-server-mmo-equip/docs/design/equipment-attributes.md:534)、[equipment-attributes.md:632](E:/work/xuanming-server-mmo-equip/docs/design/equipment-attributes.md:632)。

## 炼化业务当前缺什么

装备旁支明确将炼化、改造、进化、套装、限制交易／绑定列为未实现：[equipment-attributes.md:37](E:/work/xuanming-server-mmo-equip/docs/design/equipment-attributes.md:37)、[equipment-attributes.md:517](E:/work/xuanming-server-mmo-equip/docs/design/equipment-attributes.md:517)。已存在的 [RollAffixes:342](E:/work/xuanming-server-mmo-equip/cpp/libs/services/scene/player/system/equip_attribute_rules.h:342) 是创建装备时可复用的掷值函数，并非炼化入口。

缺少：可选属性池查询、炼化请求／结果协议、耗材与费用规则、原子扣费及重掷流程、重复请求保护、持久化与失败回滚验收。当前 BagItemInfo 只携带已经生成的词条，没有可选属性全集或属性池标识；不能把现有词条当成完整可选列表。

以下仅是后续实现需要讨论的最小信息，**不是已有或已批准的协议，不指定消息号、字段号或 RPC 名称**：

| 用途 | 最小信息 |
|---|---|
| 查询可炼化信息 | 请求目标装备实例 ID；响应业务错误、该装备可选属性的稳定 ID／名称／单位、实际适用的炼化档，以及耗材与货币种类／数量 |
| 执行炼化 | 请求目标装备实例 ID、实际选择的炼化档和用于防重复执行的操作标识；服务端校验归属、条件和消耗后原子更新 |
| 返回结果 | 业务错误、对应操作标识、真实新词条，以及受影响的背包／装备栏／货币快照；优先复用已有快照结构 |

期望属性 ID 集合可留在客户端，用真实返回词条判断是否命中；若今后需要跨设备同步偏好，再单独定义偏好存取。改造百分比、进化星级、交易天数等字段未存在，界面不得伪造。服务端若扩展功能，还需按主仓规则同步 Java 版本；本次未审计或修改 Java 版本。

## 参考截图与本作属性的差异

当前源配置见 [equip_xlsx_patch.py:82](E:/work/xuanming-server-mmo-equip/tools/scripts/equip_xlsx_patch.py:82)；武器／防具池见 [equip_xlsx_patch.py:140](E:/work/xuanming-server-mmo-equip/tools/scripts/equip_xlsx_patch.py:140)。

- 武器共 12 项：伤害、力量、体质、灵力、敏捷、准确、物理连击率、反击率、物理必杀率、所有技能上升、忽视所有抗异常、法术必杀率。
- 防具共 17 项：防御、气血、法力、力量、体质、灵力、敏捷、所有属性、反震率、抗中毒、抗冰冻、抗昏睡、抗遗忘、抗混乱、所有抗异常、抗法术、抗物理。
- 截图中的金／木／水／火／土相性、所有相性、五行抗性、所有抗性、忽视所有抗性不属于当前装备属性池；本作使用“物理必杀率”，并加入“法术必杀率”“抗法术”“抗物理”。
- 速度目前只作鞋的基础属性，不在随机词条池；截图里的速度随机词条、改造百分比、进化星级、绿色套装效果和限制交易天数不能直接搬入真实详情。

审计没有编译、导表、生成协议、运行联机测试或部署服务。远端 PR／Issue 未核对：本机未找到 gh 命令。
