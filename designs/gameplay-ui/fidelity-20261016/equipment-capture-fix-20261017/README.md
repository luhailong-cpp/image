装备 Capture 入口最小修正

本包仅修改 EquipmentForgeUiVerification.cs，连同原 GUID .meta 共两个文件；独立 sourceguard 六项，Editor 三个验收入口离线复编退出 0。没有运行 Unity 或写入 client。

06-loading 分支先点击真实 BagCategory_3“已穿戴”入口，再选择 EquipSlot_3；读取阶段的强化区有意隐藏，因此仅该断言从正式锻造根下包含隐藏控件的集合中 Single 查找，确认唯一控件同时隐藏、不可用。其他可交互控件仍严格 activeInHierarchy + Single。原截图状态、目标物品、发包次数、确认、回包及关闭断言全部保留。

visual-fixes-20261017 的全部代码与 PNG 在安装后逐一 SHA 相同。Unity 导入器重写了 Sprite .meta 的序列化字段和已有 DefaultTexturePlatform maxTextureSize（16384），导致 .meta 不再字节相同；原图尺寸均小于 4096，实际图像没有缩放。安装一致性记录在 ../qa/postinstall-consistency.json。

新截图尚未审核，本包不构成运行验收或视觉通过结论。
