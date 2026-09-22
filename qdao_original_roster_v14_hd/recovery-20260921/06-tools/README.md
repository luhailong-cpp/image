# 06 雷法少年隔离工具

这些入口只服务06，未修改公共V14管线、canonical、旧S16、8idle或其他角色。Python使用本机 bundled runtime：`C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`。

`06-work`已从`06-audit`完整复制8张E及其90个来源/处理文件，原字节一致；换行恢复证据保存在`06-work/audit-seed-evidence`。其中E03已选用AI编辑`E03-edge-v3`的原生1254透明稿并导出1024，旧E03和处理metadata在本目录`history/`保留。E03-v2因放大和底边可见裁切拒收，`smoke-work`是被拒导入的隔离残留，不能选用。

## 单帧导入与复核

```powershell
$py06='C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py06 -B qdao_original_roster_v14_hd/recovery-20260921/06-tools/import_frame.py --archive qdao_original_roster_v14_hd/recovery-20260921/06-generation/E07-single-v1 --batch-id E07-single-v1 --direction E --frame 7
& $py06 -B qdao_original_roster_v14_hd/recovery-20260921/06-tools/verify_work.py
```

默认输出到`06-work/candidate/06_thunder_caster_boy`，默认`--chroma-profile native-alpha`，固定common_scale=.88。`--staging-root`可指向本`06-tools`下独立工作树以避免并发manifest竞争；禁止canonical。批次ID必须新建，若替换已占槽，先精确保留旧PNG和metadata，再写隔离候选。

`native-alpha`不色键、不去紫、不清低alpha，不改变RGB；只对原画布按`.88*1024/max(native_size)`统一缩小、LANCZOS重采样和整数脚底锚定。原图alpha>8不能触边；孤立alpha1边界像素可保留。最终对所有alpha>0检查是否落入画布，不能借阈值隐藏裁切。源图、keyed、normalized、cleaned、final五阶段和完整参数均保存，`alpha_verify.py`独立重建；本地variant不冒充公共V14标准色键路径。旧图继续用其原standard参数验证。

`import_frame.py`接收04旧格式或本窗口`request.json`的request envelope及receipt；逐项核对prompt、实际reference路径、原生尺寸、raw SHA与仍存在的工具原文件。原始request/prompt/receipt保持不变。原生和输出各自有生成/派生记录。模型和质量为host-managed/unverified，不把配置目标写成已返回值。

## 原图归档

`archive_generation.py prepare --batch NAME --prompt-file FILE --reference PATH ...`在调用前冻结配置与精确输入，输出的request就是应传给imagegen的参数。调用后使用`finalize --batch NAME --original TOOL_OUTPUT --tool-result-json RESULT`归档原图及逐图记录；RESULT保存真实output_hint与可用调用证据，勿包含base64。本窗口root已有等价归档流程时可直接使用，不需重写已有文件。

## 固定SHA的混合素材预览

```powershell
& $py06 -B qdao_original_roster_v14_hd/recovery-20260921/06-tools/select_work.py --output qdao_original_roster_v14_hd/recovery-20260921/06-tools/selections-review-set-v1.json
& $py06 -B qdao_original_roster_v14_hd/recovery-20260921/06-tools/build_package.py --revision review-set-v1 --selections qdao_original_roster_v14_hd/recovery-20260921/06-tools/selections-review-set-v1.json
& $py06 -B qdao_original_roster_v14_hd/recovery-20260921/06-tools/audit_snapshot.py --revision review-set-v1
```

`select_work`显式选用06-work所有已导入槽；调用前root应完成取舍，不将拒稿导入其中。旧V13 S16与8idle原字节优先保留（512不放大冒充HD），其余取固定SHA的work/canonical。每次新revision，禁止原地覆盖审过的快照。首个`audit-start-v1`真实库存24walk+8idle，缺104；只有完整S向产生深浅两个16帧30ms GIF，缺帧方向显示空槽。

预览包含8方向、独立idle、深浅底、正常/放大、逐帧及15→16→01→02接缝。齐套后应有16个GIF，每个16帧×30ms=480ms。GIF、SHA与透明边界审计只证明文件合同，动态步态与美术验收需root另绑定manifest SHA记录，不能自动传播正式批准或Unity/客户端运行通过。
