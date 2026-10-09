from pathlib import Path
import json, hashlib, datetime
b=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r06_c10")
index=json.loads((b/'full-tile-qa/inspection-index.json').read_text())
report={
"tile":"r06_c10","checkedAtUTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
"status":"local-visual-QA-passed-awaiting-root-integration","localAccepted":True,"formalAccepted":False,"rootPublished":False,
"source":index["source"],"coverageOpaquePixels":16777216,
"visualMethod":"All nine 1536x1536 overlapping native-scale panels and all three 1536x640 south-seam panels actually opened with view_image original detail; no upsampling.",
"wholeTilePanels":index["wholeTilePanels"],"southSource":index["southSource"],"southPanels":index["southPanels"],
"allTilePixelsVisuallyCovered":True,"resamplingApplied":False,
"internalSeams":[{"axis":a,"tileLocalCoordinate":v,"completeLengthChecked":4096,"result":"continuous"} for a in ["x","y"] for v in [1024,2048,3072]],
"nineIntersections":[{"tileLocalXY":[x,y],"result":"no visible join artifact"} for y in [1024,2048,3072] for x in [1024,2048,3072]],
"southSeam":{"worldY":24576,"worldXRange":[36864,40960],"all4096ColumnsChecked":True,"result":"paving, curved stone base, green body and shadows continuous"},
"findings":["Ivory balustrade and flowerbed footprint, plants, curved curb, central paving, red festival structure, jade pagoda-shaped base and shadow checked throughout.","No new dangling tile joints, triangular cracks, repeated contours, shifted connected objects or opaque gaps observed at joins.","A faint pale diagonal is visible through the left balustrade opening around tile-local x 490..600/y 1715..1790. It reads as a low-contrast paving/light facet behind the opening, not a broken join; retained and explicitly noted for root review.","Gold decoration remains ornamental cloud/floral forms; no readable word claim."],
"pixelProof":{"file":str(b/'full-chain-integration-proof.json'),"sha256":hashlib.sha256((b/'full-chain-integration-proof.json').read_bytes()).hexdigest(),"all16ManifestsSequentiallyReconstructFinal":True},
"scopeLimit":"Visual local acceptance only. Root separately confirms current source ROIs, integrates queued manifests and validates final pixel identity. No unknown external neighbor pixels are claimed."
}
out=b/'full-tile-local-qa.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({"report":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest()}))

