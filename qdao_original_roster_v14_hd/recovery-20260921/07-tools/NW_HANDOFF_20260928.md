# 07 NW 离线修正冻结记录：2026-09-28

当前 NW 为 16 行走 + 1 独立站立候选。静态复核完成并冻结给根任务汇总；未实时播放、未正式批准、未接入客户端。

- NW11/12/13 从各自真实 1254 RGBA 原生图整画布等比重导出，高度由 902/838/905 改为 860/853/867；NW10 保持 849。未局部拉伸、未拼接或合成伪帧。
- NW16 内置透明单帧编辑共 3 次，选用 continuity-r20260928c；a 被 c 替代，b 因近臂前伸过量拒选。选用 c 原生 1254×1254，导出1024×1024，主体854高，保留原腿相位。
- 已逐张实际查看17组深浅底，每个背景的角色显示保持1024×1024；重查当前PNG、sidecar、原生SHA。15份原生当前在位并匹配，idle/NW及NW01仅有历史删除后的文字链。
- 当前17槽无像素完全重复或精确镜像重复；两份GIF均16帧且每帧30ms。GIF时长检查不等于实时视觉播放。
- 所有本轮实际型号/质量均未披露，字段null；配置目标仍只是目标。收费API调用0。

仍待live：NW11/12/13头宽396/422/398（最大相邻差约6.6%），NW15→16→01手腕与刀刃的闭环变化，以及其余高度起伏。当前静态没有裁边或实色背景；不以静态结论替代运行时步态验收。浏览器URL识别故障后本轮未操作UI、未绕过。

绑定报告：[report.json](nw-final-repair-20260928/report.json)。本轮前记录为 pre-repair-text-records.json；只保留文字快照，没有图片回退副本。

| 槽位 | 当前 SHA256 | 主体高 |
|---|---|---|
| idle/NW.png | `15babfb591ecc976aa4b23a0117586730ad80c2f63df54fee4e9550565b19a7c` | 897 |
| walk/NW/01.png | `5bd1ce5abf53fc72c584f441a872867b5ddb21658b92058aa81212cda4b9aabb` | 850 |
| walk/NW/02.png | `295004e286c49a1eda9c8a85056230f800abdc798a9a957d12f7d31e5bf2f6f7` | 842 |
| walk/NW/03.png | `e517d65097a5cf3687a1b399166f4bd3b93ba27b113fa6c425a5fed283ad9c3c` | 844 |
| walk/NW/04.png | `deb8aa2f8d869839e3bfea4bdf648770e44806da693ce523abeee1c1c5cb8085` | 846 |
| walk/NW/05.png | `b5133c4da7a076caf1cd0580eb0abe362faec12e54298e1da2b30a4980969de7` | 876 |
| walk/NW/06.png | `49cc7af2bfc8cea930b8b5bfbe2882008ac846a6c7430db14a4cac9e906c48c7` | 856 |
| walk/NW/07.png | `b63bb75966bd36e017ec3eceba20a32c819a7e3a8d8c22678c46f1f33b28f85a` | 860 |
| walk/NW/08.png | `b1e516e4329ef79db2f91af942a304b37d5159295991a631cdd3cf094f8beff1` | 887 |
| walk/NW/09.png | `d6efaba47e59f4f245cbecd84d5df49c450d26b6ecca13e862f26b72936135ae` | 859 |
| walk/NW/10.png | `6f0bd47e6d1d53163a5866aa6deae146353ad36e29c34df5e8191af589d63c1d` | 849 |
| walk/NW/11.png | `70d473a65a2191dc9aa61546ea7a868a39c94de43a17328f75d1ea81faf4c2c9` | 860 |
| walk/NW/12.png | `f8cd3b4e0f704c844ac714e0e493bbc976eab76cadd293b30fbd7772e45613dd` | 853 |
| walk/NW/13.png | `f2ac5e8eef630c6099c2b8827b3aec5c12c4322d5ea0063405795fc0bf945b5c` | 867 |
| walk/NW/14.png | `a89f1e959d004c6ed69afdb10f00efe1355a502f72401a6c2859c05ef08c3119` | 877 |
| walk/NW/15.png | `6b95cf4fa9a8643473caf36b10f50f4bb20308378b0bca7d0ef2002aa65b772d` | 881 |
| walk/NW/16.png | `9c8acad38af93f5273f63c6610a2fef6dcfd5f6142375ebc4c9ef26ab178c696` | 854 |

恢复第一步：读取此报告并重新核对17槽当前SHA，再在允许且可可靠识别URL的浏览器环境播放当前版30ms深浅底循环，特别检查10→11→12→13及15→16→01。不要把旧全量预览SHA用于当前四张修改图。
