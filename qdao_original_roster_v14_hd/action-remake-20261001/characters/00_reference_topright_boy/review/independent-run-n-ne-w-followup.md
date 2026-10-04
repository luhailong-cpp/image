# N 后续原生修复交接

本文件补充并覆盖前一报告的候选推荐；原48帧审核SHA保留在 independent-run-n-ne-w.json。

当前推荐 N04-v2、N06-v7、N14-v2、N15-v3；NE04-v6、W16-v4延续原推荐。N12-v5仅作条件候选：部位尺度已正确，左鞋底1131比N04-v2蹬地鞋1151高20，更像刚离地，不能标接地完成。

| 新源 | 静态结论 | alpha128主体底 |
|---|---|---|
| generation/run/N/14-v2.png | preferred_static_candidate | 1025 |
| generation/run/N/15-v2.png | rejected_foot_too_low | 1164 |
| generation/run/N/06-v6.png | rejected_scale_drift | 1160 |
| generation/run/N/12-v4.png | superseded_scale_fixed_toe_too_low | 1182 |
| generation/run/N/06-v7.png | preferred_static_candidate | 1024 |
| generation/run/N/04-v2.png | preferred_static_candidate | 1151 |
| generation/run/N/15-v3.png | preferred_static_candidate | 1081 |
| generation/run/N/12-v5.png | conditional_candidate_toeoff_timing_pending | 1131 |

## 来源与实际观察

- **generation/run/N/14-v2.png**
  - SHA256: `81a109a42c800b5a1467d68a1e29cc829920c1f0e6a95f7cc02ec45b8703e2e0`
  - 以06v5正确部位尺寸换成第二半圈：左后折鞋底朝镜头、右鞋跟前摆；右空臂后摆，头背和葫芦与母版相合。
- **generation/run/N/15-v2.png**
  - SHA256: `7af7732cd78915a249f60cdb376dfa16cd1362716728087972f2c57dcd72f78c`
  - 头背尺度已修好，但右鞋底1164到达虚拟地面附近，未体现下降腾空。
- **generation/run/N/06-v6.png**
  - SHA256: `e511f9f6c4ec3507cbe6ca4b065a1baa644eace203a2dc1d5fe3c556d66eaaab`
  - 右空臂收至身侧、遮挡关系正确，但全身和头背再次放大，不能替换。
- **generation/run/N/12-v4.png**
  - SHA256: `12b0f41141d7879f62e2ef52eb7be417f3a890b3920eed41b115fb6bc0eb9edb`
  - 头背回到06v5正确档，左后蹬/右前膝/右空臂后摆正确；左鞋尖1182，低于04v2的1151约31，转做局部膝踝修。
- **generation/run/N/06-v7.png**
  - SHA256: `d7c3750044bd1c86e9515ad8e0c6efcb5a63eab459aa2f48d541b4491a002de1`
  - 以06v5为唯一动作底、附风格图，只修右空臂。头背葫芦和两条腾空腿尺寸位置稳定，右前臂向远处前摆，拳被躯干和袖部分遮挡，与后折右腿反向。
- **generation/run/N/04-v2.png**
  - SHA256: `be795835bc0baebdd08a9ffde3d1484b2fee7ee43cfcd217424e26e190025f7d`
  - 纠正旧04左右腿相位：右鞋在画面右后伸蹬地、鞋底朝镜头，左膝前摆露鞋跟；右空臂向前被遮挡。头背与05/06正确档相合，右鞋底1151。
- **generation/run/N/15-v3.png**
  - SHA256: `187352ee0f43ec100e15b99fbbde8e8998f17f01750eafda7d10d72f8c42af1d`
  - 只上收右膝踝后，头背双手保持v2，右鞋底1081；比14v2的1025下降，仍明显悬空。请求1110实际多收29，未逐帧后处理。
- **generation/run/N/12-v5.png**
  - SHA256: `1d0b8581a7e74f8d6132a7a368bcb1dd38109a7fb673041f120e5a69dd90d495`
  - 保持v4正确部位尺寸；左踝上收实测51而不是请求31，最低1131，比04v2的1151高20。更像刚离地而非前掌最后接触；可供尺度修复候选，不能标接地完成。

新增8张均1254×1254 RGBA，宿主PNG逐字节一致，配套prompt/request/receipt/generation记录及SHA完整。实际模型和质量仍未确认。没有修改selected-new、manifest、导出资源或05/07/08的新版本。

本轮确认原N04腿相位与05不连贯，并发现06右空臂与后折右腿同向的外观，分别用04-v2和06-v7改正。N05/07/08交总控独占处理。N13由总控在14/15合入后再看。未作浏览器播放，未批准整组动态。

