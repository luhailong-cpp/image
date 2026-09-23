# 05 天音少女清理计划（只规划，未删除）

核对：2026-09-23T07:20:24.661394+00:00；清单修订：2026-09-23T07:22:02.245628+00:00。当前 `05-delivery-preview/revisions/complete-review-v1` 的128walk+8idle已逐张SHA验证；最终命名与离线美术验收由主代理完成。

05独占图片共2125个。逐文件绝对路径、SHA、当前引用和外部原图见 [JSON](CLEANUP-PLAN-20260923.json)。来源文字记录保留。

| 处置 | 图片数 | MiB |
|---|---:|---:|
| PROTECT | 61 | 19.93 |
| HOLD_REFERENCE_CONTRACT_REVIEW | 5 | 18.40 |
| DELETE_AFTER_FINAL_ACCEPTANCE | 1572 | 1361.91 |
| DELETE_AFTER_FINAL_REBIND | 303 | 163.85 |
| PROTECT_UNTIL_FINAL_NAME_BOUND | 184 | 142.72 |

当前预览仅实际读取自身runtime的136张PNG；selected-overrides及方向selection仍指向staging，删除当前选用导出前先重新绑定最终包，或明确标为历史。原图路径和SHA应追加已删除标记；删除后不再承诺来源像素重建。

宿主generated_images具体图路径132个：现存91、历史缺失41、现存SHA绑定异常0。现存文件均逐个列出，工作区外操作需对应权限；不得删除整个宿主目录，不猜测旧用户名路径。

保护：当前4096肖像、全部designs风格图、V13现正式52walk+8idle及其他角色。另有基线肖像、V13候选portrait和N/E/S三个strip列为HOLD；共享代码/HTML仍用到的图另列HOLD，不当作无引用图片。

执行前先完成最终验收、定名、136张SHA与当前引用复核；仅按具体图片路径删除，绝不递归删除目录或删除JSON/MD/txt等记录；每项重新核对SHA和工作区包含关系。正式客户端或Unity未由本计划验收。
