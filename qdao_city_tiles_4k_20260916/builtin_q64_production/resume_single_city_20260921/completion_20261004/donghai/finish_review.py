from pathlib import Path
from PIL import Image
import numpy as np
import json,hashlib,datetime
R=Path(__file__).resolve().parent;M=R/'baseline/source-and-qa-manifest.json';data=json.loads(M.read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src={(s['appearance'],s['tile']):s for s in data['sources']}
validation=[]
for q in data['qa']:
 path=Path(q['file']);actual=Image.open(path).convert('RGB');expect=Image.new('RGB',tuple(q['pixels']))
 assert sha(path)==q['sha256']
 if 'source' in q:
  assert sha(q['source'])==q['sourceSha256'];im=Image.open(q['source']).convert('RGB')
  for c in q['crops']:
   piece=im.crop(c['sourceLTRB'])
   if c.get('rotation')==90:piece=piece.transpose(Image.Transpose.ROTATE_90)
   expect.paste(piece,tuple(c['sheetLTRB'][:2]))
 else:
  app=path.parent.name;le=src[(app,q['leftTile'])];ri=src[(app,q['rightTile'])]
  q['sources']=[le,ri];pair=Image.new('RGB',(512,4096));pair.paste(Image.open(le['file']).crop((3840,0,4096,4096)),(0,0));pair.paste(Image.open(ri['file']).crop((0,0,256,4096)),(256,0))
  for c in q['crops']:expect.paste(pair.crop(c['pairLTRB']).transpose(Image.Transpose.ROTATE_90),tuple(c['sheetLTRB'][:2]))
 assert np.array_equal(np.array(actual),np.array(expect)),str(path)
 validation.append({'file':str(path),'sha256':sha(path),'nativePixelReconstructionMatches':True,'actualViewedOriginalPixels':True,'assessment':'No visible broken contour, hard rectangular color boundary, doubled edge or blurred seam in this sheet.','localSeamScopeAccepted':True})
data['visualReviewPending']=False
M.write_text(json.dumps(data,indent=2),encoding='utf-8')
notes={
 'donghai_day/r08_c08':'Fish basin rim, canopy and wooden uprights continue across reviewed seams. Ground grout and cast-shadow contours remain continuous.',
 'donghai_day/r08_c09':'Lantern string, mast, blue canopy, fish and barrel outlines are continuous in the reviewed strips. Painted cloudy ground shading has no hard grid boundary.',
 'donghai_day/r08_c10':'Yellow canopy, stall rails, fish tray, foliage and stone base continue across reviewed strips and junctions.',
 'donghai_lantern/r08_c08':'Glowing lanterns, gold canopy trim, fish basin and floor grout continue. Faceted warm/purple lighting is painterly, without a visible rectangular grid join.',
 'donghai_lantern/r08_c09':'Blue canopy stripes and perimeter, lantern chain, mast and seafood rims remain continuous. Existing soft irregular light patches are not counted as hard seam defects.',
 'donghai_lantern/r08_c10':'Reviewed all internal strips including repaired fish-tray region; no split fish outlines or tray-rim break seen. Strong gold/purple reflected-light patches remain part of the existing painted appearance.'}
reviews=[]
for s in data['sources']:
 key=s['appearance']+'/'+s['tile'];qpath=R/'baseline'/s['appearance']/s['tile']/'qa'
 ent={'source':s,'actuallyViewedOverview':'1024 square orientation reference only; not a full4096 pixel review','actuallyViewedNativeQA':[str(qpath/n) for n in ['x1024-full.png','x2048-full.png','x3072-full.png','y1024-full.png','y2048-full.png','y3072-full.png','nine-junctions.png']],'internalSeamScope':'all six1024-grid internal lines over full4096 length,320-pixel-wide band each','internalJunctionScope':'all nine internal intersections,512-square each','assessment':notes[key],'internalScopesAccepted':True,'allArtworkPixelsReviewedAtNativeResolution':False,'formalAccepted':False}
 (qpath/'visual-review.json').write_text(json.dumps(ent,indent=2),encoding='utf-8');reviews.append(ent)
record={'reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'verify_model','sources':data['sources'],'visualSheetsActuallyViewed':46,'overviewReferencesActuallyViewed':6,'internalFullLengthSeamBands':36,'internalJunctions':54,'fullLengthSharedBoundaryBands':4,'sharedBoundaryBandWidth':512,'nativeQaPixelsResized':False,'allQaReconstructedFromPinnedSources':True,'validation':validation,'tiles':reviews,'needsImageRepairInReviewedScopes':False,'newImageGenerationCalls':0,'newToneCorrectionCalls':0,'sourcePixelsModified':False,'formalAcceptedTiles':0,'unreviewed':['All non-seam areas at native pixel resolution','External neighbor edges north and south of r08, outer west of c08 and outer east of c10','Four-formal-tile junctions, since no adjacent row exists in these candidates','Gameplay loading, collision, navigation, and runtime appearance switching'],'scopeConclusion':'Six existing4096 candidates pass the requested internal seam/9-point and existing two shared-boundary scopes per appearance. This is scoped visual review, not wholecity completion or final tile delivery.'}
(R/'review.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
(R/'README.md').write_text('''# 东海日景与元宵六块复核\n\n从旧 current-batch 钉住日景 output_v3 和元宵 output_v2 的 r08_c08、r08_c09、r08_c10，六张均实测4096×4096且SHA与索引一致。\n\n本次实际以原像素查看46张QA：36条内部全长接缝（每条宽320，分四段无缩放排板）、54个内部交点（每点512²，六张九宫格）、4条正式图块共边（各宽512，全4096长度）。另看6张1024²缩略总览，只用来定位构图，不冒充完整4K逐像素检查。全部46张QA另从当前源像素重建验证一致。\n\n上述范围未见需要修补的断线、错位、硬矩形色带、双边或模糊接缝。日景与元宵各三块的鱼摊、木柱、篷布、灯笼、石缝和共边轮廓在所看范围连续。因此本次没有为增加修改数量而调色或再生图；源文件像素未改。逐块与逐QA结论见 review.json，各qa/visual-review.json记录确切范围。\n\n仍未检查全部非缝区域的原像素、上下邻行共边、c08西侧/c10东侧未制邻块、正式四块交点及客户端实机。正式验收新增0，整城完成新增0。六块是旧坐标复核，不是新生成六块。\n''',encoding='utf-8')
print(json.dumps({'review':str(R/'review.json'),'actualViewedNativeSheets':46,'internalLines':36,'internalJunctions':54,'commonEdges':4,'sourcesModified':False}))
