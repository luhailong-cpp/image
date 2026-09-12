# 素材存储与清理

核对日期：2026-09-12。建议继续用GitHub管理代码、提示词、清单和少量预览，大批生成原图和素材包单独存储；必须随代码版本恢复的正式大素材可用Git LFS。

## 本次结果

| 已清理内容 | 数量 | 释放空间 |
|---|---:|---:|
| Git报告的陈旧tmp_obj垃圾 | 26个 | 16.45 GiB |
| 旧.work制图缓存和QA图片 | 258张 | 315.77 MiB |
| v8中完全重复的中间PNG | 35张 | 142.08 MiB |
| 合计 | 319个文件 | 16.90 GiB |

[清理记录](STORAGE_CLEANUP_20260912.json)保存路径、尺寸和缓存图片哈希；[去重映射](STORAGE_DUPLICATES_20260912.json)保存35张重复图的SHA-256及现存副本路径，可恢复历史报告中的中间图。已增加忽略规则，避免重新提交这些可重复产出的图片。

正式素材、兼容旧路径、确认参考、生成来源、备份、暂存验收输入及JSON记录保留。约3.59 GiB的Unity安装下载属于其他工具任务，本次未删除。

清理时本地Git pack约42.93 GiB，这不等于GitHub服务端准确占用。本次没有改写提交历史；删除已提交图片也不会自动清掉其历史版本。其他任务仍在推送，因此本次未执行GC、历史重写、强推或迁移。

## 适合本仓库的存储

| 方案 | 用途与限制 |
|---|---|
| GitHub普通Git | 代码、文档、提示词、索引和少量预览。官方建议.git控制在10 GB内；单对象硬限制100 MB，并建议生成文件放对象存储。[官方限制](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits) |
| GitHub LFS | 必须随版本还原的正式大素材。Free/Pro包含10 GiB存储、每月10 GiB下载；每次修改完整累计文件版本，需要控制版本数量。[官方计量](https://docs.github.com/en/billing/concepts/product-billing/git-lfs) |
| Cloudflare R2标准存储 | 大批原图与素材包的推荐备选。每月含10 GB-month存储、100万次A类和1000万次B类操作，直接出口流量免费；超额存储每GB-month为0.015美元。是否免费取决于账户全部用量。[官方价格](https://developers.cloudflare.com/r2/pricing/) |
| Gitee | 可以托管代码，但不建议为了图库扩容迁入。官方LFS指南写明仅对付费企业开放，免费版0 GB、付费档附带1 GB，可再购买扩容。[官方说明](https://help.gitee.com/enterprise/code-manage/code-hosting/large-file-manage/git-lfs) |

主要在中国大陆工作时，可以试传比较阿里云OSS或腾讯云COS；核算存储、请求和下载流量费用。[OSS计费](https://help.aliyun.com/zh/oss/billing-overview)、[COS计费](https://cloud.tencent.com/document/product/436/36522)。只需个人备份时，本地素材目录配合已有网盘或外置盘也可以。

## 后续迁移顺序

先确定独立存储位置，上传并核对文件数量与SHA-256，在仓库保留路径、版本、尺寸、哈希和下载位置清单，验证能在干净目录还原正式素材。之后再选择归档旧仓库并建立精简仓库，或在完整备份、协作同步后重写现有历史。换Git平台、添加.gitignore或启用LFS，都不会自动清理已有大文件历史。
