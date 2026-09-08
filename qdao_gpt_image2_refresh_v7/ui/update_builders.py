"""One-time migration of legacy SVG builders to the new AI-painted inputs."""
from pathlib import Path

repo=Path(__file__).resolve().parents[2]

def edit(rel, old, new):
    p=repo/rel; s=p.read_text('utf8')
    if new in s:return
    if old not in s: raise ValueError(f'Missing migration anchor in {rel}: {old[:100]}')
    p.write_text(s.replace(old,new,1),'utf8')

edit('qdao_gpt_image2_refresh_v7/ui/prepare_assets.py','from scipy import ndimage','from PIL import ImageFilter\nfrom collections import deque')
edit('qdao_gpt_image2_refresh_v7/ui/prepare_assets.py',"        labels,count=ndimage.label(a[:,:,3]>20)\n        sizes=np.bincount(labels.ravel()); sizes[0]=0\n        if count==0: raise ValueError(f'Empty generated cell {name}')\n        keep=labels==int(sizes.argmax())\n        near=ndimage.binary_dilation(keep,iterations=2)","""        pending=a[:,:,3]>20; best=[]; hh,ww=pending.shape
        for yy,xx in zip(*np.nonzero(pending)):
            if not pending[yy,xx]:continue
            queue=[(int(yy),int(xx))]; pending[yy,xx]=False; points=[]
            while queue:
                py,px=queue.pop();points.append((py,px))
                for ny,nx in ((py-1,px),(py+1,px),(py,px-1),(py,px+1)):
                    if 0<=ny<hh and 0<=nx<ww and pending[ny,nx]:
                        pending[ny,nx]=False;queue.append((ny,nx))
            if len(points)>len(best):best=points
        if not best:raise ValueError(f'Empty generated cell {name}')
        keep=np.zeros((hh,ww),dtype=np.uint8)
        by,bx=zip(*best);keep[by,bx]=255
        near=np.array(Image.fromarray(keep).filter(ImageFilter.MaxFilter(5)))>0""")

edit('qdao_ui_redesign_v5/components/build.mjs', 'for (const a of assets) {\n  const source = svg', '''// v7 artwork: newly generated built-in image_gen inputs, prepared at fixed dimensions.
const aiRoot = path.resolve(root, '../../qdao_gpt_image2_refresh_v7/ui');
const aiSourceMap = JSON.parse(await fs.readFile(path.join(aiRoot, 'source-map.json'), 'utf8'));
for (const a of assets) {
  const painted = await fs.readFile(path.join(aiRoot, 'derived/components', `${a.id}.png`));
  a.body = `<image x="0" y="0" width="${a.width}" height="${a.height}" href="data:image/png;base64,${painted.toString('base64')}"/>`;
  a.authoring = 'New built-in image_gen artwork; deterministic alpha cleanup, nine-slice layout and status placement; portable embedded PNG in SVG.';
  a.v7_sources = aiSourceMap.derivatives[a.id];
  const source = svg''')
edit('qdao_ui_redesign_v5/components/build.mjs', "product: '五行奇谈', version: '5.2', created: '2026-09-06'", "product: '五行奇谈', version: '7.0', created: '2026-09-07'")
edit('qdao_ui_redesign_v5/components/build.mjs', "authoring: 'Original native SVG geometry; no source game images or dynamic text embedded.',", "authoring: 'New built-in image_gen artwork, fixed-contract derivatives embedded portably in SVG. Dynamic text remains separate.',\n  ai_provenance: { source_map: '../../qdao_gpt_image2_refresh_v7/ui/source-map.json', prepare: '../../qdao_gpt_image2_refresh_v7/ui/prepare_assets.py', native_sources: aiSourceMap.native_sources, model_parameter_exposed: false, quality_parameter_exposed: false },")
edit('exact_qdao_slices/build_native_q5.mjs', "  const source=xml(w,h,body,file,vw,vh),", '''  // New v7 AI painting; logical SVG viewBox and physical canvas remain intact.
  const painted=await fs.readFile(path.join(repo,'qdao_gpt_image2_refresh_v7/ui/derived/legacy',file));
  body=`<image x="0" y="0" width="${vw}" height="${vh}" href="data:image/png;base64,${painted.toString('base64')}"/>`;
  const source=xml(w,h,body,file,vw,vh),''')
edit('exact_qdao_slices/build_native_q5.mjs', "authoring:'Native SVG, palette and symbols from 五行奇谈 v5 components.'", "authoring:'New built-in image_gen v7 artwork; alpha cleanup and fixed-border resampling; embedded portable PNG in SVG.',v7_source_map:'qdao_gpt_image2_refresh_v7/ui/source-map.json'")
edit('exact_qdao_slices/build_native_q5.mjs', "authoring:'Native SVG rebuilt from v5 symbols; this legacy filename now stores true RGBA.'", "authoring:'New built-in image_gen v7 emblems; true-alpha atlas at legacy coordinates.'")
print('UI builders migrated to v7 AI inputs.')
