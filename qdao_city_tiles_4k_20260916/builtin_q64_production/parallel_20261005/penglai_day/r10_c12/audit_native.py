from helper import *
items=[]
for row in range(1,5):
 for col in range(1,5):
  name=f'p{row}{col}';f=ROOT/'native'/f'{name}.png';rec=p.read(str(f)+'.generation.json');call=p.read(ROOT/'prompts'/f'{name}.call.json')
  with Image.open(f) as im: im.load();dims=list(im.size)
  checks={'nativeHash':p.sha(f)==rec['sha256'],'native1254':dims==[1254,1254],'toolOutputHash':p.sha(Path(rec['toolResultPath']))==rec['sha256'],'promptSavedExact':Path(rec['prompt']).read_text(encoding='utf8').strip()==call['prompt'].strip(),'submittedPromptExact':rec['submittedParameters']['prompt']==call['prompt'],'referenceHashes':all(p.sha(Path(x['file']))==x['sha256'] for x in rec['references']),'approvedStyleActuallyAttached':STYLE in call['referenced_image_paths'],'builtinRoute':rec['route']=='builtin','noFalseModelAssertion':rec['submittedParameters']['model'] is None and rec['submittedParameters']['quality'] is None and rec['actualModel'] is None and rec['actualQuality'] is None,'toolHintSaved':Path(rec['evidence']['toolOutputHintFile']).exists()}
  assert all(checks.values()),(name,checks)
  items.append({'patch':name,'file':str(f),'sha256':p.sha(f),'generationRecord':str(f)+'.generation.json','checks':checks})
tile=ROOT/'tiles/r10_c12-candidate.png'
with Image.open(tile) as im:
 im.load();assert im.size==(4096,4096)
 for row in range(1,5):
  for col in range(1,5):
   src=Image.open(ROOT/'native'/f'p{row}{col}.png').convert('RGB').crop((115,115,1139,1139))
   box=((col-1)*1024,(row-1)*1024,col*1024,row*1024)
   assert im.crop(box).tobytes()==src.tobytes()
report={'auditedAt':p.stamp(),'passed':True,'nativePatchCount':16,'width':4096,'height':4096,'file':str(tile),'sha256':p.sha(tile),'all16CoresPixelExact':True,'method':'16 integer core crops [115,115,1139,1139]; zero scale/resample; full coverage','formalAccepted':False,'visualSeamQA':'delegated; repair candidates recorded separately','patches':items}
p.write(ROOT/'evidence/native-provenance-audit.json',report)
lines=['# r10_c12 原生细节候选','',f'已补齐16张原生1254×1254细节图，按每张1024×1024核心区域拼成4096×4096候选。没有放大最终像素。','',f'- [当前完整像素候选](tiles/r10_c12-candidate.png)：SHA256 `{p.sha(tile)}`。','- [覆盖预览](current-preview.png)为缩小的检查图，不用于正式切块。','- [原生来源和逐像素验证](evidence/native-provenance-audit.json)全部通过。','- 内部、相邻图块拼缝修补与视觉验收见 `repairs/`，该原始候选不代表正式验收。整城与客户端仍未验收。','- p14采用新版北邻c12jointv3的原生锚点，记录见 [参考派生记录](guides/p14-north-v3.png.generation.json)及 [锚点制作脚本](prepare_north_v3.py)。','', '本批均使用内置image_gen；配置目标为 ChatGPT Images 2.5 / gpt-image-2.5-sunburst / max。工具未提供型号和质量选择器，也未披露实际型号与质量，因此各图记录中的实际值均为null，不能把配置目标当作已确认返回值。','', '| 原生图 | 来源记录 | 实际提示词 |','|---|---|---|']
for x in items:
 n=x['patch'];lines.append(f'| [{n}](native/{n}.png) | [生成记录](native/{n}.png.generation.json) | [提示词](prompts/{n}.prompt.txt) |')
(ROOT/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print(json.dumps({'passed':True,'patchCount':16,'candidateSha256':p.sha(tile),'allCoresPixelExact':True}))

