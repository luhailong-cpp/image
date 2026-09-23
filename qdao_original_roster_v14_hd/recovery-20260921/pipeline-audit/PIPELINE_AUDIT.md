# 2026-09-21 角色管线只读接续核查

本报告只读核查现有工具和素材；未生图、未导入、未改公共工具、未运行 Unity、未批准素材。当前角色范围仍为 00–10、14、15、17、20；移出角色不恢复。

## 04 可立即利用的原图

`generation-current-builtin/04_mountain_guardian_boy/NW08-single-v1`、`NW10-single-v1`、`NW11-single-v1` 都有 raw/prompt/receipt，raw 为真实 1254×1254，prompt 文件与 receipt.actual_request.prompt 逐字节对应。NW04/06/07 的这三项检查也通过。

| 批次 | raw SHA256 |
|---|---|
| NW04-single-v1 | a488f681a7664a0f3b325bd7ecd6707e968eb13706598fb4145d572eeced12e8 |
| NW06-single-v1 | 21d483a3729828d21dd7414d257713bfc46d246070831449858a1c3dbc88ed04 |
| NW07-single-v1 | b948b1172d77aa39842dc8ccc0d0faf482839091c014dc906f4df5aa3c26cd3c |
| NW08-single-v1 | 8138b358f3d2ddd9be0b419726fd7c646eb0e25731ca9bfb6d5fe82b297ad16d |
| NW10-single-v1 | 0e23ffb1b02bdc996c702c5de64380be8e7b875aea108d045c44b1cbbf69124e |
| NW11-single-v1 | 4109f80305ed58c1ac09939d6069d4e83adf3ad82d765fc28c3a9f852549e5b5 |

上述 SHA 是本机归档 raw 的现场实测，未声称本机存在原默认输出文件。

## 本机路径与直接可执行命令

可用 Python（已实际用其 Pillow 打开素材）：

```powershell
$qdaoPython = 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$qdaoRoot = 'D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd'
```

本机 `py -3` 报告 No Installed Pythons Found，不能使用旧文档的 luyua 用户路径。`E:/work/image` 和 `C:/Users/luyua/.codex/generated_images` 本机均不存在。

历史 `continue_import.py` 的 ROOT 已用脚本位置计算，但还会强读 receipt.original_generated_file 并校验，归档 raw 已存在也仍强读。因此本机不能直接执行旧示例。无需改旧回执即可调用底层管线；下述新进程禁用共享 preview 回调。检查原图可用后才执行，每批改 batch/frame：

```powershell
$qdaoImport = @'
import importlib.util,json,sys
from pathlib import Path
from types import SimpleNamespace
root=Path(sys.argv[1]); batch=sys.argv[2]; frame=int(sys.argv[3])
b=root/'generation-current-builtin/04_mountain_guardian_boy'/batch
receipt=json.loads((b/'generation-receipt.json').read_text(encoding='utf-8-sig'))
assert (b/'prompt.txt').read_bytes().decode('utf-8-sig') == receipt['actual_request']['prompt']
s=importlib.util.spec_from_file_location('qdao_pipeline',root/'tools/pipeline.py')
p=importlib.util.module_from_spec(s);s.loader.exec_module(p);p.preview=lambda:None
p.import_sheet(SimpleNamespace(command='import-walk',character='04_mountain_guardian_boy',direction='NW',source=b/'raw.png',prompt=b/'prompt.txt',receipt=b/'generation-receipt.json',batch_id=batch,common_scale=.84,chroma_profile='standard',rows=1,cols=1,source_cell_indices=None,idle_order=None,output_frames=str(frame),start_frame=1))
'@
& $qdaoPython -X utf8 -B -c $qdaoImport $qdaoRoot 'NW08-single-v1' 8
& $qdaoPython -X utf8 -B "$qdaoRoot/tools/verify.py" --character 04_mountain_guardian_boy --direction NW --frame 8
```

同样可用于 NW10/11。`verify.py` 会写对应 review/validation-NW-XX.json；单帧结果只是像素重建，不能替代完整方向连播、视觉通过或严格 receipt 原路径校验。`pipeline.py` 默认会写共享 preview-index.json/index.html，必须保留上述 callback 禁用或由主代理独占统一刷新。

## NW04/06/07 残边修订边界

当前 `.84` 全角色尺度、standard 100/150 色键、despill radius4/reference12 都已记录且由独立重建复现。04 已使用 standard；改成 purple-preserve 50/75 会保留更多紫色，并不是更强去边。现有 importer/独立重建只接受 [100,150] 或 [50,75]；私自提高阈值或换算法不能获得有效重建通过。

修订前保存这三张旧最终 PNG、processing/frame-sources.json、manifest.json、qc.json、旧单帧 validation，以及文件 SHA 清单。原 source/<旧batch>、processing/batches/<旧batch> 不动。以新 batch ID 保存新处理/新生图证据；同旧 batch 重跑会覆盖旧处理阶段文件，不足以保留历史。同一源单格最多对应一个最终动作槽，不能因重处理当作新增帧。

若现管线不能消除残边，需内置图像编辑/重绘，或由主代理单独扩展并版本化合法处理合同和独立重建器；不能在输出 PNG 上修后只更新 SHA 冒充重建。保留旧处理证据，修后重新深浅底放大及独立重建。

## receipt 的严格规则与迁机阻塞

`tools/assemble_mixed_roster.py:104` 的 validate_native_receipt 要求：

- actual_request.prompt 与 prompt.txt UTF-8 文本严格相同，不做换行归一。
- referenced_image_paths 为非空实际绝对路径列表，每个原路径必须现场存在；当前 SHA 被写入绑定报告。
- output_hint 必须保留工具的 `Generated images are saved to ... as ...png by default.` 路径格式。
- original_generated_file 原路径必须存在，必须与 output_hint PNG 路径一致，且内容 SHA 与归档 raw 相同。
- generation_calls 整数 1、paid_api_calls 整数 0，started_at 带时区。

04 已归档 receipt 的 refs 仍为 E:/work/image，原输出仍为 C:/Users/luyua。历史回执不能改成 D:/ 路径伪装当时实际请求。本机相应参考文件在 D:/luyuan/wuxingqitan/image 的同相对路径存在，但原默认输出路径没有随项目出现。现有 mixed_workspace.py 只适配工作区/正式发布位置，不适配上述来源验证。

因此可先正常补图、处理、做局部单帧重建；当前严格 mixed assembly 会在旧 absolute refs/original checks 处失败。后续需要明确独立的迁移绑定，保留历史 receipt 字节，区分“原历史路径/原默认文件缺失”与“迁移归档 raw 当前 SHA”；不能仅把验证函数改成路径存在即放行，也不建议伪造 E: 或旧用户目录。若使用可追溯迁移记录，应限定精确历史来源和 SHA，并让 check 路径独立复核；本次没有实施该工具改动。

## SW 孤立原图

三份 exec-df5633ce、exec-907b94e6、exec-e93ff345 当前只在 04 交接中找到文字引用。repo 文件名搜索及本机 Administrator 的 generated_images/archived_sessions/sessions 对指定文件名/原会话 ID 搜索未找到这些原件或原会话。原 luyua 路径不存在。没有找回真实 prompt、receipt 或可靠 SW14/15/16 槽位映射，因此不能恢复为这三槽；优先按真实缺槽重新生成，继续保存历史未映射说明。

## 几何与混合预览

新图原生完整 cell 两边 >=1024；1254 单图按 `1024 / 1254 * .84` 缩到 860×860 工作图，再整数位移进入 1024×1024 透明 PNG，脚底 alpha>8 最低点 y942，上身前42%像素 x 中位数锚至512。禁止按逐帧人物 bbox 单独缩放。04/05统一 .84、06统一 .88；pivot[.5,.08]。旧512/52PPU与新1024/104PPU具有相同世界尺寸。

修复历史来源路径绑定后，在 V14目录下创建全新的混合装配目录；不可覆盖既有 run。以下 `RECOVERY_NEW_RUN` 必须替换为本轮新目录名：

```powershell
& $qdaoPython -X utf8 -B "$qdaoRoot/tools/assemble_mixed_roster.py" assemble --character 04_mountain_guardian_boy --preparation "$qdaoRoot/mixed-preparation/preserve-20260918-run1" --hd-candidate "$qdaoRoot/candidate/04_mountain_guardian_boy" --output "$qdaoRoot/mixed-candidates/RECOVERY_NEW_RUN/04_mountain_guardian_boy" --reconcile-legacy-text
# dry run可用后，同命令加 --execute；完整验收时加 --require-complete
& $qdaoPython -X utf8 -B "$qdaoRoot/tools/assemble_mixed_roster.py" check --directory "$qdaoRoot/mixed-candidates/RECOVERY_NEW_RUN/04_mountain_guardian_boy" --require-complete
& $qdaoPython -X utf8 -B "$qdaoRoot/tools/serve_mixed_preview.py" --assembly "$qdaoRoot/mixed-candidates/RECOVERY_NEW_RUN/04_mountain_guardian_boy" --port 8876
```

打开 http://127.0.0.1:8876/ 。真实 PNG，8方向、16×30ms=480ms，独立 idle，正常/放大、01/05/09/13以及15→16→01接缝；旧全HD预览不适合混合尺寸。预览默认暂停，审核输入导出始终pending，不自动批准。当前无本轮新的预览/美术验收结论。

## 其余8名肖像现场确认

下列文件都在 `D:/luyuan/wuxingqitan/image/q_daoist_character_pack_4096/`，实际 Pillow 打开为4096×4096 RGBA，均有同名 records JSON 和 prompts 文本。没有恢复移出名单的文件。

| ID / PNG文件名 | SHA256 |
|---|---|
| 07_moon_shadow_assassin_girl_transparent_4096.png | 8ccc7e9118ed1ca608a407687e5a76cf392b1f694ef7737ccc28536caae84bfc |
| 08_alchemy_prodigy_boy_transparent_4096.png | fcbf04089dbc229887d9c18b2b21e9dfb7997c5ec28c086e45db2d78e9bef82e |
| 09_bamboo_archer_girl_transparent_4096.png | c7ba2937630b589f16c0581f76421f20eccb19599aba6b47cca748de450447dd |
| 10_crimson_spear_girl_transparent_4096.png | ea068eb40dbd372b108d2e7d041c8e270e898f8ae979ce039873a08e49a0260f |
| 14_short_hair_snow_summoner_girl_transparent_4096.png | 834fbe56bc3de4aa8a241d7e12a9725095cfcf486b98066876a8e70fa343c2a8 |
| 15_water_dragon_scholar_boy_transparent_4096.png | c3b96a88c2fdebb36951c8b47d3b1860b0e5895ae775bb360beb036bb393de70 |
| 17_ghost_script_calligrapher_boy_transparent_4096.png | 34d13fe2558dee7ab8403180a7cd4c26e95b0b9795181053057b5759c69a5614 |
| 20_star_formation_master_girl_transparent_4096.png | 4a5de67ffb880a852554d460c709f7179bffd3706fa7bf825767e5369e9bd3e5 |
