from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import hashlib, json

batch = Path(__file__).resolve().parent
prod = batch.parent
root = prod.parent
target = prod / 'donghai_batch_r08_c11_20260920'
assert not target.exists(), 'Preserve previous plans'
target.mkdir()
guides = target / 'guides'
guides.mkdir()
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
sources = []
for appearance, version in [('donghai_day', 'output_v3'), ('donghai_lantern', 'output_v2')]:
    src = root / 'builtin_q64_all_city_references' / appearance / 'map-native-layout-reference.png'
    im = Image.open(src).convert('RGB')
    # Only a structure/style guide. No pixels here are promoted to final artwork.
    rect = [40960 - 115, 28672 - 115, 45056 + 115, 32768 + 115]
    box = [rect[0]*im.width/65536, rect[1]*im.height/65536, rect[2]*im.width/65536, rect[3]*im.height/65536]
    dst = guides / f'{appearance}-c11-layout-only.png'
    im.transform((1254,1254), Image.Transform.EXTENT, box, Image.Resampling.BICUBIC).save(dst)
    neighbor = prod / appearance / 'r08_c08_c09_c10_joint' / version / 'r08_c10-extended-context.png'
    nim = Image.open(neighbor).convert('RGB')
    overlap = guides / f'{appearance}-c10-native-right-overlap.png'
    nim.crop((4096,0,4326,4326)).save(overlap)
    sources.append(dict(appearance=appearance, layoutSource=str(src),layoutSourceSha256=sha(src),
        layoutSourcePixels=list(im.size),layoutSourceBoxXYXY=box,layoutGuide=str(dst),layoutGuideSha256=sha(dst),
        referenceResampledOnly=True,referencePixels=[1254,1254],
        leftNeighbor=str(neighbor),leftNeighborSha256=sha(neighbor),leftOverlap=str(overlap),
        leftOverlapSha256=sha(overlap),leftOverlapPixels=[230,4326],leftOverlapResized=False))
plan = dict(schemaVersion=1,createdAtUtc=datetime.now(timezone.utc).isoformat(),
    status='plan_ready_waiting_for_root_lantern_v2_merge',
    tile='r08_c11',row=8,column=11,finalPixelRectXYWH=[40960,28672,4096,4096],
    worldRect=dict(x=237.5,z=150,width=18.75,height=18.75),
    appearances=['donghai_day','donghai_lantern'],
    rationale='Continue the selected c08-c10 strip eastward across the street, foliage and house edge. Day geometry is authoritative for the matching festival appearance.',
    sources=sources,route='builtin_image_gen',configuredModelTarget='gpt-image-2.5-sunburst',configuredQualityTarget='max',
    actualBackendModel=None,actualQualityPreset=None,backendModelVerified=False,qualityVerified=False,
    nativePatchPlan=dict(rows=4,columns=4,core=1024,halo=115,adjacentOverlap=230,nativeExpectedPixels=[1254,1254],
        extendedContextPixels=[4326,4326],finalCropBoxXYXY=[115,115,4211,4211]),
    stages=[
        'After root merges the lantern-v2 ledger, inspect local day layout-only guide and selected c10 context. Generate and retain a native local layout study with builtin GPT Image; this study is a structure guide, never a 4K completed tile.',
        'Prepare one unified day geometry canvas and 16 overlapping guide crops. Carry the exact 230px selected c10 overlap into the first-column guides. Handcraft prompts, inspect actual references, preserve every source and ordered submitted input hash.',
        'Generate 16 native day detail patches sequentially with actual adjacent native context. Assemble without enlarging native artwork; repair all internal/cross-tile seams before selecting c11.',
        'Prepare lantern guides from the accepted local day structure and selected c10 lantern overlap; the whole lantern reference supplies appearance only. Generate 16 new native lantern patches and repair without moving roads, footprint, entrances or house placement.',
        'Inspect all complete seams, intersections and actual repair ROI edges at native scale, audit hashes/rejoin, and emit an incremental candidate ledger for root merge.'
    ],
    generationStarted=False,newNativeSources=0,finalArtUpscaled=False,accepted=False,runtimePublished=False,
    existingC10NativeComplete16of16=True,oldQueueMustNotBeReplayed=True,
    dependencies=[str(batch/'lantern-v2-ledger-update-20260920.json')],
    limitations=['References are only low-resolution layout/style guides. They are never counted as HD final artwork.','This plan does not mark any tile complete.','Complete-city, navigation, foreground and Unity runtime acceptance remain pending.'])
(target/'next-adjacent-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(plan=str(target/'next-adjacent-plan.json'),sources=len(sources),newNativeSources=0)))
