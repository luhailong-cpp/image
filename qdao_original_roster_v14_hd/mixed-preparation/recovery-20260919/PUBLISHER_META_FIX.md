# 首次04发布：独立工程元数据保护修复

修复对象为 `tools/publish_mixed_roster.py` 的 `formal_character_baseline` 与 `stage_binding`。问题是实际正式/隔离工程的旧作者资源一致，但637个旧 `.meta` 因各自GUID和Unity导入内容不同。原逻辑要求跨工程旧全集相同，导致合法首次04发布也失败。

现在分别核对两套完整资源保护：

- 正式：固定历史 `mixed-resolution-client-run1/formal-safety-baseline.json` 的已知SHA、正式工程路径、schema、范围、前序review SHA、46历史源码路径和3451角色文件。所有角色文件含meta的路径、SHA、字节数必须与当前正式库存完全相同。
- 隔离：全部旧作者文件与meta对本轮stage审计的 `protected_before` 逐路径/SHA相同。只允许新增04目录、其新meta和原先不存在的V14家族meta；原先已存在的家族meta不能被排除。
- 跨工程：作者资源集合和SHA完全相同；仅meta不要求跨工程字节一致。它们仍分别受到上述完整保护。
- 新发布audit增加 `legacyProtection`，保存固定正式基线绑定、双方库存摘要、作者/meta数量和跨工程meta差异数。

无需新增“接受现状”的baseline参数或写文件：每次prepare原本就读取新鲜正式Assets/Packages/ProjectSettings完整库存，execute前后再次核对；历史固定角色基线负责防止先前旧图/meta漂移。历史baseline中的源码是同步前记录，仅检查其身份和范围，当前源码仍由50项独立绑定检查。

`test_publish_mixed_baselines.py` 的16项小型门禁测试全部通过（10.026秒），涵盖允许独立GUID/importer、两工程作者/meta变化、大小变化、删文件/增文件、跨工程作者不一致、固定基线SHA/身份/范围错误、时间/重复行/路径逃逸及既存家族meta保护。既有大fixture测试补充了合成正式基线以保持兼容，本次未再运行该耗时全套。三个相关Python文件语法检查通过；真实历史baseline的SHA/身份/范围/3451记录自洽检查通过。

验证没有启动Unity、创建stage、执行publication、改写正式/隔离角色文件或历史baseline。测试是发布门禁逻辑验证，不能冒充真实资产Unity验收。

边界与风险：

- 仍仅允许04首次发布。05/06还需要前序V14发布和导入证据链、双方派生index核对及多个混合角色的runtime验收，不能仅追加ID。
- 如果正式Unity后来重新导入旧角色而改变旧meta，固定历史基线会按设计拒绝。必须明确审查该变更并迁移保护合同，不能临时生成新baseline跳过。
- 测试/审计为本地断言和SHA绑定，不是签名认证；原有真实素材、审批、运行截图、Unity输入与测试门禁全部保留。
