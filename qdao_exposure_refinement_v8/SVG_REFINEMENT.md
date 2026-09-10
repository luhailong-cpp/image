# SVG 曝光修复接入说明

2026-09-09，对仓库正式 SVG 只读审计；本模块与验证脚本本身不覆盖素材。逐文件结果见 `svg_audit.json`。

## 审计结果

- 共 120 个 SVG，其中 118 个包含内嵌 PNG，2 个只有原生文字。
- 总计 370 个内嵌 PNG 引用，对应 79 个唯一原始 PNG 字节 SHA-256。
- 79 个内嵌 PNG 均能与仓库独立 PNG 精确匹配（扫描 958 个独立 PNG），可直接复用其修复结果。
- 两个纯文字 SVG 为 `q_daoist_login_ui_uncropped_highres_final_layers/native_q5/labels.svg`（28 个 text）与 `qdao_ui_redesign_v5/hud/hud_labels.svg`（3 个 text）。没有背景、白雾或过曝位图需要处理；浅米白文字用于深色按钮可读性，保留颜色。
- 当前组件保留了一些旧渐变 defs，但可见图像已由 PNG 表达。这些 defs 应保持原状，不应因为出现浅色 stop 就当作可见泛白区域修改。

## 模块 API

```python
from svg_grade import grade_svg_bytes, inspect_svg_bytes, svg_structure_bytes

# 键必须是修复前 PNG 原始字节的 SHA-256，值为其修复结果 PNG bytes。
svg_output, stats = grade_svg_bytes(
    original_svg_bytes,
    grade_raster_bytes,
    png_sha256_index=original_sha_to_graded_png_bytes,
)

# 可在正式替换前/后检查全部非图片内容逐字节一致。
assert svg_structure_bytes(original_svg_bytes) == svg_structure_bytes(svg_output)
```

`grade_raster_bytes` 接收 PNG bytes 并返回 PNG bytes，不接受路径或元组。只有没有精确字节哈希匹配时才调用。若像素相同但压缩编码不同，回调可使用自己的像素缓存；模块不会把这种情况误判为字节相同。

一个文档内相同 PNG 最多处理一次，含 href 与 xlink:href 的重复引用。外部引用原路径保持不变，不再次加载或处理图片。除确实发生变化的内嵌 PNG 属性值外，整个 SVG 保持逐字节不变，包括文字、坐标、属性顺序、命名空间、空白、引号、注释、原生颜色和未使用的 defs。回调输出的 PNG 像素尺寸必须与输入一致。透明度由调用方的位图处理器保护。

函数不向 SVG 注入处理标记；跨运行避免重复调色应由总控使用原始备份和修复清单负责。UTF-16/32 或自定义 XML 实体声明会报错而不是静默重写。本仓库 SVG 均已通过解析。

## 验证

执行 `python qdao_exposure_refinement_v8/tools/check_svg_grade.py`：已通过 3 个真实 SVG 的内存调色检查，包含通用行背景、带重复图片的 HUD 与纯文字层。验证了非位图内容逐字节一致、标签数量、文字、坐标、原生颜色、defs、嵌图数量、PNG 尺寸和 alpha 不变。

额外使用真实 PNG payload 检查 href/xlink:href、重复引用、外部路径、注释中的伪 image、属性引号内的 `>`、base64 空白、精确 SHA 索引复用及原样回调保持整个文件 bytes 不变。全部通过。检查产生的调色图仅存在于内存，不作为正式修复素材。
