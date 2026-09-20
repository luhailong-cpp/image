# V14 runtime publication gates

Use explicit --character for the requested remaining character. Existing complete Original00–03 and their512 fallbacks remain intact. No HD character is currently complete or published.

The authored runtime set is exactly137 PNG (128 walk +8 dedicated idle +portrait) and3 JSON (manifest,validation,appearance). The input/target may additionally contain only root runtime-index.asset, its.meta, authored-file metas and the known idle/walk directory metas. Extra strips, orphan metas and nested files named runtime-index.asset are rejected. A first Edit input can precede Unity meta/index generation; Play input must bind the actual generated index and all authored asset metas. The formal Editor derives its own index from formal PNG GUIDs.

Publish requires complete passed real Unity Edit/Play results, all20 HD contract and14 HD lifetime/loader cases including parameter cases, no skipped/inconclusive/failed cases, normal exit0 with retained launch/completion/log records, matching full filters, project and input snapshots. Forty source/meta paths plus6 existing camera script/config/meta paths are compared against tested inputs. The additional camera files are not modified by the publisher.

The actual schema2 camera observations now include imageSha256, configuredZoomMin and configuredZoomDefault. The publisher verifies the exact saved PNG bytes, decoded1920x1080 dimensions, recorded camera configuration, projection size, visible feet and clipping flag. The current minimum camera follows feet and can crop the top; that fact is retained and explicitly reviewed. A default nonempty JSON object with an empty imagePath is not evidence.

After inspecting each actual normal and nearest capture, save a review and pass --runtime-visual-review PATH for formal publication. Staging does not need this post-runtime review. The publisher never creates visual approval. This is the shape; placeholders and pending status must not be changed into a pass until actual images were inspected:

```json
{
  "schema": "qdao-original-v14-hd/runtime-visual-review-v1",
  "status": "pending",
  "reviewer": "actual reviewer",
  "reviewed_utc": "UTC timestamp after the actual runtime report",
  "runtime_report_sha256": "exact report SHA256",
  "input_snapshot_sha256": "exact Play input SHA256",
  "views": [
    {
      "character_id": "exact requested original ID",
      "view": "normalView",
      "status": "pending",
      "image_sha256": "normal PNG SHA from actual runtime observation",
      "notes": "Actual identity/detail/edge/contact observations",
      "clipping_reviewed": false,
      "full_frame_inside_capture": true
    },
    {
      "character_id": "same original ID",
      "view": "nearestView",
      "status": "pending",
      "image_sha256": "nearest PNG SHA from actual runtime observation",
      "notes": "Actual close detail and any clipping observations",
      "clipping_reviewed": false,
      "full_frame_inside_capture": false
    }
  ]
}
```

`full_frame_inside_capture` must equal the recorded actual flag, including false when cropped. A passed review needs nonempty notes for both views, clipping_reviewed true, and exact report/input/image hashes. Missing/stale/duplicate/predated reviews are rejected. The completed publication audit records runtime visual review, PNG, XML, launch, completion and log hashes.

`test_publish_original_roster_v14_gates.py` uses only temporary procedural PNG/XML gate fixtures. They are deleted from a verified E:/work/tmp test directory and never enter Unity Resources, candidate manifests, approval records or publication. Their results do not count as visual artwork acceptance.
