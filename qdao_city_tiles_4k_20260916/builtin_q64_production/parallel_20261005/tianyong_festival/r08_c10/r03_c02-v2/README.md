# r08_c10 / r03_c02 v2

实际完成 1 次内置 image_gen 重绘，返回原生 1254×1254；原字节保存于 `native.png`，SHA256 `ff9d92a5b93afbb1c4d7b134795b552d82379d801e7956c67ece46072835a308`。没有 API、放大、配准或写入 current。

本次以 v001 的原下方230行作为唯一原生上下文，v1只用于看问题，没有提交其漂移结果作为权威参考。实际提示词见 [prompt.txt](prompt.txt)，真实 payload 见 [request.json](request.json)，工具结果输出提示与时间见 [tool-response.json](tool-response.json)，宿主路径与逐图记录见 [native.png.generation.json](native.png.generation.json)。配置目标 gpt-image-2.5-sunburst/max；实际提交 model/quality 与实际返回值均为 null，generatedAt 未知、观察完成时间单独保存。

v2 已恢复宽横向象牙石带，约位于 y680..770。但下方已知轮廓仍有约 -21..+29px 漂移，直接回接可见台阶和色差。详见 [visual-review.json](visual-review.json) 和 [原像素量测](overlap-edge-diagnostic.json)。未计完整4K、未通过正式验收。

[下一移位输入方案](next-shifted-context-proposal.json)将1254方片范围移至本块 `[909,2330,2163,3584]`，下627行原生已知、上627行缺失，把真实横带放在新片y303..393。本方案尚未执行；更大已知范围不保证成功，仍须实际生成和逐边实看。
