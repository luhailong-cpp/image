# 06 战斗 68 帧独立静态复核

本报告逐图核对受击 12、普攻 24、施法 32 张当前正式图。只证明静态核对；未代填动态循环或客户端验收。

## 观察

- hit/E：近侧右手持杖、远侧左手持符牌；后仰/缓冲中双靴仍朝东，02 抬起前靴而没有外拧。
- hit/W：近侧左手持符牌、远侧右手持杖；反冲中双靴朝西。00 与 02 已额外查看完整单帧，握持清楚。
- attack/E：近侧右臂持杖、远侧左手持符牌；脚尖朝东。00/09/10/11 换手错误经独立 AI 重绘后再次实际查看。06 前伸出手，随后收招。
- attack/W：近侧左手持符牌、远侧右手持杖；脚尖朝西。06 完整单帧可见出手手臂与杖柄连贯，08–11 收招。
- cast/E：近侧右手持杖、远侧左手持符牌；脚尖朝东。09 释放与 12–15 收势完整单帧已额外查看，未见换手。
- cast/W：近侧左手持符牌、远侧右手持杖；脚尖朝西。09 释放及 11/12 完整单帧已额外查看，11/12 鞋尖向左、鞋跟在右。

## 已修正问题

普攻 E00/09/10/11 的近侧右手错持符牌已各自通过 AI 重绘修复；四张新图已重新实际查看。

## 当前限制

- 本报告是静态逐图检查，不代表完整正常/慢放循环验收。
- E11 新稿头部位置与旧稿存在约 30px 高度变化，现整体更接近 E00/01；循环衔接由主窗口单独复核。
- 宿主未披露实际型号及质量；配置目标 GPT Image 2.5 Sunburst/max 不当作实测。
- 当前无客户端，未接入或运行客户端。

当前未解决阻断问题：0 项。来源图片不可用提示：0 项。

## 当前正式图 SHA

| file | SHA256 |
| --- | --- |
| runtime/hit/E/00.png | 5a0be96de26fc6b1108c1740760dc6f64123554c01bf856b5beeb545a64d583f |
| runtime/hit/E/01.png | f10d02c667fa1cc3e33555edf3bf19d2d3fafbd13b44efb5847e0dd9ca617b00 |
| runtime/hit/E/02.png | d4095affb9a08f52877d442a3b8e7d8491defff0843a526c9b3fc15748515416 |
| runtime/hit/E/03.png | 8d227bc11bd4a56d76787d77bb6eef37165d04370575454b631fba5874d1b99c |
| runtime/hit/E/04.png | 12077f4d429a8c234c860f438034ee712eec699c59a080c39c4b45cabeb675c9 |
| runtime/hit/E/05.png | 04b7946db07d837c8858ead2280f572147151bba5020ea988382ec2716e50f7d |
| runtime/hit/W/00.png | 0a68c5c2b487120fb5fa55a46b900c1ee0371cb55bc7f1550689d4f46b1a42a2 |
| runtime/hit/W/01.png | f67e889abdf762b9af144756d90e6d9a642057399d3e8a76e2da19e6b3c580e0 |
| runtime/hit/W/02.png | 5cec59d2ccfe4cca3f794b0dbde204f3eeee81d308f1b195699d62037d9a817d |
| runtime/hit/W/03.png | 6e301b16bbda7a0851440ba98fbca2155ac1ceee7f2ac7fc31271121e33003cf |
| runtime/hit/W/04.png | 0925a69a58b6fe4c504bd7342af26174d290683acf67aaf9954ff53188786a14 |
| runtime/hit/W/05.png | a78c764b2a6afd21a42c6a9100999f4b14d662f2536d5ea1904db094ab3b9128 |
| runtime/attack/E/00.png | 3ecd11c7dbd35c49525dc2e9c7b652c8277bb7bb77ce3016dac195dfb22d389e |
| runtime/attack/E/01.png | 5af36dd905e655ba6512dcc0663f0ba8b648c9acf209c9bbae00d08ffeedd221 |
| runtime/attack/E/02.png | 362574b5dda33672e7999018a94ae0c35426c5375635932db25d2ae4ee370257 |
| runtime/attack/E/03.png | 516f3cdc32a13407c2f8a3d212708ca3e3f23dc2df4aaf7959d040311940ca3f |
| runtime/attack/E/04.png | 5ea2191773e8172e96ed2ae087a61772eee0e370484e8314891cc4688b1a860a |
| runtime/attack/E/05.png | c3ecbd526bf0c883de1b91f255a050ca744da44492d8f2ec52e8199babd4eafe |
| runtime/attack/E/06.png | 60f3564d743c10c7d3d661cca08d8fed6d5232249fc3d2b1feacdd4b026777d9 |
| runtime/attack/E/07.png | 486837e67265001b441c7f172e3b55beb7e4895d6e664d33c0267a4bf9c8e307 |
| runtime/attack/E/08.png | 5b4ff75baf0a0c94f0166bcb7691e4ad610f277fc879576aebf0810e424d2520 |
| runtime/attack/E/09.png | 1c63f5d5b23e348f1a08bc7f0b4f38120c0a3481d2df3bba5ad99311faedd53a |
| runtime/attack/E/10.png | 16511330d601c4af270787e1a08ae31e41148768317cccd64c2aa0c74b5621ae |
| runtime/attack/E/11.png | 88214a08136415253441a2b657df4ebf6d06177cd1a64ea41cef19efa5ea0e45 |
| runtime/attack/W/00.png | 768397a77738f59e6e2e7163979db2be7e4da28af12e64ad36d789dd41e09b8d |
| runtime/attack/W/01.png | fb5b45df5a314a639b672d875ab015ad4e628c351316c20a0c8c6499171474c0 |
| runtime/attack/W/02.png | 29a5bc6755d1e4ae5c0455bf21089ef732082bfee074bc19d2f6e91941715534 |
| runtime/attack/W/03.png | 8812662750f7c4c6fe4b9a18202bd43e4c24cf5be19c011b78c112a1a1781a67 |
| runtime/attack/W/04.png | ecd3a69b98fb80413f761262e37305ced3b17d728a6a21b6c18967ef4ce3f455 |
| runtime/attack/W/05.png | 2e82a410e304330400958be82b4a412489b569bcfecb3ff164c471e910326a40 |
| runtime/attack/W/06.png | f86d688d9fec46c95ec9217d4c6c95ee710e719216e5614720cb40cf15398921 |
| runtime/attack/W/07.png | 427b315d08bf74b7018d799fe5f2edd1a5b86e122627e29764efde3bc3cea88f |
| runtime/attack/W/08.png | b5797805807ccae308a2b2ed42357f8efe3f513461898e3366f8ccc7b01693db |
| runtime/attack/W/09.png | bc1f605358192d0d3ff1494851f49596f1cb91e51f071b050cdc4a4113061d22 |
| runtime/attack/W/10.png | 54b57e1d48b50fb27d59f3b1e2459eee6b80241715ada3ecc5d9fd00e075b26b |
| runtime/attack/W/11.png | f7532b2edcab64dec3a75db355ba2c1fddb0691b67caaea5a774605048f4379c |
| runtime/cast/E/00.png | 020ea69b454aec3333e3dd64c0b5171f76aa218541e6e69eb09f18ff6e558d7e |
| runtime/cast/E/01.png | 816b2a2b5ae4ae0d34f23436a1bb38fc9884a086010d8785089adc9f91a43126 |
| runtime/cast/E/02.png | d6866b6276146e1d2d90fdd821e3ffd3a17896cc5bb667066081f40741aa2f31 |
| runtime/cast/E/03.png | 3862ea0ed39a26da81a27dc18852e4000356644b40aecdea9f373d18dbf64eca |
| runtime/cast/E/04.png | 6ab51c568763c70c2cfd34c72e743ac345f44381acf0958047675c31833937ad |
| runtime/cast/E/05.png | 5d526c5148eb80bc6c5baaf1ec346e15b059e035df8af872aa34c194fa0e2c03 |
| runtime/cast/E/06.png | 9e2592350104b92cdc66ab14e9367d335b4fc04205e553b2c60f645d38ce575b |
| runtime/cast/E/07.png | 14faa0315f8256abf8c1458f35097da84b0cee9390bba11a9f7b0608655a6d70 |
| runtime/cast/E/08.png | f016874ecb35838f7ed098f578607495a9d8beef21d7da603b827a2e8299c814 |
| runtime/cast/E/09.png | 209f7f18b5679520c406bf45e56987a3cdc1c775b39d79198f053501861f0bf5 |
| runtime/cast/E/10.png | 13a9023eaa35c2129c4d19f4aeb16c5f7f1207fe21a34f86bd22f345d8db0c33 |
| runtime/cast/E/11.png | 428d17940b6ad1dd111f3dae4da777d7f31d5d040227d4d2351b21c74c26ce88 |
| runtime/cast/E/12.png | 7e4d009a29613133a5399b9ea6ce599c8b9d7643cac77cf675d8a03f5af3d38b |
| runtime/cast/E/13.png | 474e0d54c5e0f99e4f011a6df6d024205e83bb09724e456564039192b3ede5ca |
| runtime/cast/E/14.png | bf417ed7ac60930b9b5a16ff089b3131c17d55a233faa9a964d2449bb8f18ffb |
| runtime/cast/E/15.png | 05386a09224f811dbf647d882509ab502444f0489e8d846750612ae0883b4848 |
| runtime/cast/W/00.png | 96a7ede3d3ada6fe7dd77d31d120d143eb71583afa6b11a0788d72bd1dcb6ebc |
| runtime/cast/W/01.png | 46c6bf37c9d369076e2ad418b335941b959ee36e798e22106abdb5ce35977732 |
| runtime/cast/W/02.png | 6af4bf57847834c51b3fa7370c9ac4503d0e86ca897f67ae042f04a865906375 |
| runtime/cast/W/03.png | 5623587375c7efcaea95cc5ee7fb830a716be6a6754620e554626c0d696e77c1 |
| runtime/cast/W/04.png | f893d73520cc1ada337fb20590ebf7a8c7f93dd1d732e185a20c29c8de1067bb |
| runtime/cast/W/05.png | 6c10461fcf5dd76873e70963e8b8d554f8ae339811ef2baf747c1c445f88817f |
| runtime/cast/W/06.png | 191dcd7ac70c02e79430cab5c192041eb7d35e77313b3760dc3ee2453e9abff1 |
| runtime/cast/W/07.png | dfb901f3648bf9aa0c74a4af9e747c042ec1dbe3358ad32430d6fffb538b9f54 |
| runtime/cast/W/08.png | 2f84735bb53b61142ad0bca8f98bac602da4c86b57ea67878ac1b5699fd9f95a |
| runtime/cast/W/09.png | 2e2c99abc6076ecf4e26b9891d1b404093241b5c35e81ff9edefd1d160ccb151 |
| runtime/cast/W/10.png | 014d41110a19c206a776465526da6ea20d50f6fdb116ffb2a088ea37b7970fd7 |
| runtime/cast/W/11.png | 725136b1ad1d4bbae037c2889fab9065d5a49c67236a6407048ec69c3cc47dc7 |
| runtime/cast/W/12.png | 1942e3eac4367b08df74b16e40c69a509e6f27cae7cedcbc3d1f5adc182e9554 |
| runtime/cast/W/13.png | f49717f8ced4aef3912d29575bd4582afaa539893e79d79bc7a7ca2335885abb |
| runtime/cast/W/14.png | 93b2d162f4e4f13bba4258f414963929b93328fb2ea6049bb3debecfe6217bf8 |
| runtime/cast/W/15.png | 9bbeccba500f9f2e2fb96f6fc2f8b053bc2303031ce2509f407b3a6b22d11a7a |

## 新视频反馈后的局部修正

本轮视频反馈定位并AI局部修正：近侧解剖左靴鞋尖向W/左延展，右侧鞋跟块与鞋侧壁恢复，12→13的近正面鞋轴突变已处理。膝弯、白绑腿/踝位置、远靴、收勢、身份和右杖左牌保持。已实际查看1254原生与1024正式图；动态另验。

逐图来源：work/cast_W_13_videoaxis_v1.png.generation.json。其他 67 行图像检查记录保持，当前 68 行 SHA 已同步。


2026-10-05 补充复核：战斗 68 帧肩—袖口—腕—手指及握持已逐张实看，未发现新增明确上肢错误。cast W14/15 近侧左靴向镜头偏转已使用内置 image_gen 分别局部修正；朝 W 长鞋侧恢复，踝点、膝弯、另一靴、头脸相机、右杖左牌保留，两帧各 45ms。已实看原生和 1024 导出，只更新本报告对应两行，其他 66 行保留。完整逐帧与来源见 upper_limb_combat_20261005.json。仍属静态审查，不代表连续播放或客户端验收。
