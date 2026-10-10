from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'integrate_r10_c16_internal.py').read_text()
s=s.replace("B=T/'repairs/internal-color-match'","B=T/'repairs/internal-color-match-v2'").replace("D=T/'repairs/internal-final'","D=T/'repairs/internal-final-v2'").replace("a.sha(B/'candidate.png')=='83bda970e93c68ad09a5eb6fe76b432b3fc343b16e0515bda0659261608ca0f4'","a.sha(B/'candidate.png')=='f678022f2c6bc03506c49d8f8d2a0adce37809af4fb6129c65b12884fbf8fc89'")
s=s.replace("assert j.raw(j.cut(base,box))==meta['rawSourceRGBSha256']","assert a.sha(meta['source']['file'])==meta['source']['sha256'];assert j.raw(j.cut(j.rgb(meta['source']['file']),box))==meta['rawSourceRGBSha256']")
s=s.replace('rawSourceROIValidated=True,eligible=',"rawSourceROIValidated=True,generationSourceBeforeLocalFieldRefinement=meta['source'],applicationBaseRebase='Same geometry and original source seam masks; smaller17px difference filter refined tonal residual only.',eligible=")
(p/'integrate_r10_c16_internal_v2.py').write_text(s,encoding='utf-8')
