# E/W 双帧接地修正交接

校验时间：2026-10-04T19:25:38.461051+00:00

已完成 32 正式帧：每方向替换 01、04、05、06、07、08、09、12、13、14、15、16，保留 02、03、10、11。

E：01–08 右腿支撑，09–16 左腿支撑。W：01–08 左腿支撑，09–16 右腿支撑。每半轮按 2 帧初承重、2 帧身体经过、2 帧后支撑、2 帧后蹬接触分段。靴轴随行进方向；同段两帧为独立姿势。

正常 APNG：16 × 75ms = 1200ms；慢速：16 × 300ms = 4800ms。静态原图与连图已查看，客户端未接入，世界空间锁脚未验收。正常 1×动态最终由根窗口复核。

模型目标 GPT Image 2.5 Sunburst / max；内置入口无选择器，实际型号和质量未确认。候选与回执均保留，E05 attempt03 网络失败记录保留，实际采用 attempt04。

文件校验问题：无

|方向|帧|本轮|支撑脚|位置段|正式SHA256|
|---|---|---|---|---|---|
|E|01|替换|right|initial_load|b99270b6d15c59343e97ffb97c5e78915783e1033d4458b61713209d698e115c|
|E|02|保留|right|initial_load|a0d7bb9102637b377f5949f43e0992226d021f7d5132d29d399084b647635ac9|
|E|03|保留|right|body_passes_support|2b99f86c21e716a2232f159729605fabe62acc73ebe9c771907d40d0454f29fe|
|E|04|替换|right|body_passes_support|938682b7405c998421380eea870b0877bcfe8f5ff3f35a0f68b8be2b2c8d80e8|
|E|05|替换|right|rear_support|15af3ffc80dbc0a1e34f47295697549689475fd353613970365d5f2c07daf300|
|E|06|替换|right|rear_support|057cb541e4dd944f22847484e6a5587cf6fe6b8ac3478a289075bd8147bbd83c|
|E|07|替换|right|rear_push_contact|44d42f15408d0eae47915d4b1efff8c062b42ea7219f89345419fa2811b59fd9|
|E|08|替换|right|rear_push_contact|2aa2a2007e5605111985d137a7b00279b109763da4c06b81dcbceed7946858d9|
|E|09|替换|left|initial_load|00d058842f2f0a704717958648f233163134a981911b48222b87e71287371f4b|
|E|10|保留|left|initial_load|57e0279d93946e0660d6db00d7dbf0e253718e98b16ac5eace089c9746069de5|
|E|11|保留|left|body_passes_support|bd20c0d15e8850432421e22fe07756e18be58de972ea05f8375633a11fafd2bb|
|E|12|替换|left|body_passes_support|aa02fa40d3ff55695fa989b8560815174953956a1c070650f567b5f1e1a36607|
|E|13|替换|left|rear_support|0afc00d91e71d1426ba1d3e77f4c88fee9d7b01b268d420694555c36a08c766c|
|E|14|替换|left|rear_support|349a4e245f52e9cf78145434e03cbf2f9e70926cbc4c0eb07852f203f50de55d|
|E|15|替换|left|rear_push_contact|a74275a99d048e2627e8890caa088f37fc231d5a4d646026b23da9588483c9c7|
|E|16|替换|left|rear_push_contact|953d4dbc0285b8b34a455e6eb0a4f2893d454fdaa36238a41ae457e351c3b1af|
|W|01|替换|left|initial_load|a16d0d7b6bfa0c875bd596d28931c617029d0c4354c3f0170cd22917b5af51c9|
|W|02|保留|left|initial_load|ca04d33bcc8e856903e14d9763312174b3fe3071758b6c9cc75d4ddf77c6e910|
|W|03|保留|left|body_passes_support|9bcc956c225500ba17610512db9585e94532aa735ee1f0b1f5f9967d0afb33da|
|W|04|替换|left|body_passes_support|593af3c5cd77550123cb9778cb1aa4b0748b668d1f131075c6e7e53d583fb47d|
|W|05|替换|left|rear_support|684206b7efc11775af91b24f835d75cce627c677fc3b6db0f9ff847955d6fb5a|
|W|06|替换|left|rear_support|b904f544102a9c3182857547e9cb1b74e812854a6f527bcf45d2dd4f55652b3a|
|W|07|替换|left|rear_push_contact|a2468831f8280228ebccbaa0ed776f3b2e5fd60665cc6f1f818e7e76b5c70812|
|W|08|替换|left|rear_push_contact|5cda74036c56ee30453013660e144df9bf3531a92144fbb3f8d167c42459b6d5|
|W|09|替换|right|initial_load|212d548887131b7e13809a0ee7917c9f33afa7e2907d440e7de64ff59052a6f5|
|W|10|保留|right|initial_load|42805fce7d71bd3725466c8ed90cf9d3eb6d794887b9b0f78a29befc17472191|
|W|11|保留|right|body_passes_support|420e26bec8b26b0eaa7a07df5b760a78dcac870c96d508201ec1bf3153953fe6|
|W|12|替换|right|body_passes_support|339beec8a79e7dab76e66dae49c77bde74ffea5c95f1565a1047b1a11946d4a0|
|W|13|替换|right|rear_support|32799b8d375218f763351d5db0460a32793aa59bcad9db39308bebdc46a803ce|
|W|14|替换|right|rear_support|fc5db6838766f023f2f055d6b4f9527503e2c5c52243312c52e3f1abbfe573fc|
|W|15|替换|right|rear_push_contact|7d0d1ff21b9eacbeeb7b1e74970016717a6234011eea5da1e92bd5b12741b47a|
|W|16|替换|right|rear_push_contact|3cac0d04281db888995d0e6a2d02efc6656081a3e25c9425b3d1439729dcbf77|
