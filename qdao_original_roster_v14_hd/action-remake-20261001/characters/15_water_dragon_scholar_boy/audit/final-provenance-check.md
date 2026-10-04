# 15 水龙书生：冻结选表逐图来源核验

核验时间（UTC）：2026-10-03T23:11:42.767499+00:00

当前 196/196 槽，195 张本批生成、1 张旧图复用；196 个独立源 SHA。
来源技术核验：196 槽无错误；错误 0 项，警告 0 项。
本轮修正 6 个已唯一证实的路径/补证，记录在 provenance-path-repairs.json；未修改历史型号、质量、生成时间、源图 SHA。
选表核验期间不变：True。

本报告不代替本聊天/主审的离线视觉和动态复核，不表示用户验收。用户尚未验收，客户端未接入、未运行验收。

## 核验项目

- selectedShaMatch：196
- nativeHighResolutionRgbaPng：196
- transparentAlpha：196
- generationRecordPresent：196
- generationShaMatch：196
- actualModelQualityExplicitlyUnconfirmed：196
- promptFileMatchesSubmission：196
- newRequestMatchesSubmission：195
- receiptMatchesHostOutput：196
- hostOriginalMatchesSelected：195
- referenceSequenceMatchesSubmission：196
- referenceFileShaMatches：600
- historicalSubmissionPreserved：1

配置目标 GPT Image 2.5 Sunburst / max；全部选图实际型号/质量仍按工具未披露明确为 null。没有将配置目标、提示词或本次补核冒充实际工具返回。

## 最后施法接地选择

- cast/E/06：sources/new/cast-E-06-ground-v3.png；SHA e9136168e600c510b25ec8d29504f99ea6711ee16ca226a82419bf68d6de1bfe。
- cast/E/07：sources/new/cast-E-07-ground-v4.png；SHA 24ada7fc19d133c348e3adf1a812a7c83e56ace173c31ee661d6bcf20954110c。
- cast/E/09：sources/new/cast-E-09-ground-v1.png；SHA 0e0ab8e02caea1d21ff039f8de592228cd63f6ed07b5d4ccfccdedab62be877f。

## 问题

- 当前冻结快照未检出来源链错误。

旧 run/E/09 保留历史绝对路径；本轮只在本机已知恢复目录定位提示词、回执与参考图并核对原 SHA。无旧机器宿主原图并不改写原历史记录。
