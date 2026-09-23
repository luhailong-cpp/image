# 2026-09-21 首图与工具核验

对象：`15-generation/S-idle-v1/raw.png`，实际1254×1254 RGBA，SHA256 `6ed31a2f2a3da218c7621134d3ccbb2f2dc6e8db9bab38d440cd16d1ee04236b`。本次只使用用户授权的确定性后处理，没有生图服务调用。

输出：`15-delivery-preview/runtime/idle/S.png`，1024×1024 RGBA，SHA256 `7d24a3d5432324cacddfcefc1ed4cd54ebbeb3444c1258820009aec618c4a102`，有效脚点 `(512,942)`，非零alpha包围盒 `[172,118,818,945]`。这是临时选用的独立站立图；不构成完整角色美术批准或客户端验收。

工具实际验证：

- `--help` 与 `--scan` 正常。
- 对同一slot再次 `--process --select` 被拒绝，既有归档与交付文件逐文件SHA均未改变。
- 独立载入原有 `tools/pipeline.py`，仅在内存执行其keyer/despill/axis和同样固定 `.88` 整格缩小对齐，结果与本工具交付图逐像素完全一致。
- `submitted-prompt.txt` 与真实request.prompt的UTF-8字节完全一致；已有额外末尾换行的 `prompt.txt` 原件保留。
- 首图完成时只读扫描为0 walk、1 idle、135缺槽；来源与交付SHA绑定通过，无原图复用或交付SHA重复。后续库存须重新扫描。

深浅底各1024检查图位于 `15-generation/S-idle-v1/processing-fixed088-v1/check-light.png` 和 `check-dark.png`。已目视完整画面：发梢、扇、垂饰、衣摆和两只鞋均完整，未见明显背景残留。尚未执行放大逐像素、全角色比例、八方向步态或首尾接缝验收。

原始低alpha清除25614像素，品红抠色额外清除0像素；边缘去溢出改2383像素，alpha与几何不变，边带外改动0。最终画布边缘可见像素0，强品红阈值候选35，边带品红相近色31；这些可能包含合法发丝/衣物色彩，数值不得直接当作残边不合格或美术通过结论。完整统计见该次 `processing-fixed088-v1/processing.json`。

未调用、修改共享pipeline的preview/index写入路径，未做Git操作、发布或Unity运行。
