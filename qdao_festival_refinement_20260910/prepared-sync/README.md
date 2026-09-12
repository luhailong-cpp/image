# 准备导出同步

已发布198份仓库内准备导出：76个旧UI副本换用当前v10源图，122个物件副本与当前600像素正式源按既有规则同步。所有目标尺寸、RGBA通道、命名和九宫格转换规则保留；122个物件Alpha逐像素未变，76个旧UI的外形透明度采用已验收当前源图，未沿用旧皮肤轮廓。

全部198项均与既有转换配方的预期RGBA哈希一致，源图未修改，发布前备份齐全。[发布记录](publication.json) · [视觉核对](visual-approval.json) · [复现脚本](sync_prepared.py)。

仅更新图片仓库prepared目录，未读取或同步真实客户端；旧客户端报告保留，当前指针另存为client_ui_refresh_20260908/prepared-festival-current.json。
