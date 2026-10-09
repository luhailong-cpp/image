from pathlib import Path
import json,hashlib,datetime
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r06_c10")
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
ref=lambda p:{"file":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
v=read(B/"root-source-pixel-verification.json");q=read(B/"full-tile-local-qa.json")
out={
"tile":"r06_c10","reviewedAtUTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
"source":v["source"],"sourceCheckpoint":v["rootCheckpoint"],
"fullyPaintedNativeTileReviewed":True,"formalAccepted":False,"geometryAndNavigationAcceptance":False,
"coverageOpaquePixels":16777216,"expectedPixels":16777216,"nativeScale":1,
"rootSourcePixelIdenticalToReviewedLocalSource":True,"differentPixels":0,
"pixelVerification":ref(B/"root-source-pixel-verification.json"),"localVisualReview":ref(B/"full-tile-local-qa.json"),
"inspectionPanels":q["wholeTilePanels"],"allTilePixelsVisuallyCovered":True,"internalSeams":q["internalSeams"],"nineIntersections":q["nineIntersections"],
"southBorder":{"source":v["rootSouth"],"globalY":24576,"globalXRange":[36864,40960],"all4096ColumnsReviewed":True,"rootTop320PixelsIdenticalToViewedLocalSouth":True,"reviewPanels":q["southPanels"],"status":"visually continuous"},
"openInternalFindings":[],
"closedOrNonactionableObservations":[{"tileLocalLTRB":[490,1715,600,1790],"observation":"Very faint pale diagonal visible behind left balustrade opening.","assessment":"Low-contrast paving/light facet within one native design area, not dangling seam or triangular fracture; not an actionable internal defect."}],
"pendingExternalChecks":["Full north border and corner QA after r05_c10 is generated and coupled.","Full west border and corners after r06_c09 exists.","Full east border and corners after r06_c11 exists.","Whole 256-tile city review, geometry/navigation and nearest-camera runtime validation remain outside this visual review."],
"exportReadyAsPaintedCandidate":True,"cursorMayAdvanceAfterRootRecordsThisReview":True,
"rootStateModifiedByThisReview":False
}
p=B/"root-source-full-tile-review.json";p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(ref(p)))

