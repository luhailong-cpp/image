"""Refresh current pointers without restoring superseded timing presets."""

# RETIRED_20261005: direct human timing correction supersedes historical writers.
raise SystemExit("Retired: use tools/build_preview.py, build_delivery.py, build_run_board.py and build_timing_grounding.py; run60ms/960ms.")
from pathlib import Path
import json
import run_timing_1200
ROOT=Path(__file__).resolve().parents[1]
run_timing_1200.update()
(ROOT/'review/run_partial_preview.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=run_E_preview.html"><p>旧五帧片段已被当前十六帧预览取代：<a href="run_E_preview.html">打开E当前预览</a></p></html>',encoding='utf-8')
(ROOT/'review/run_inventory.json').write_text(json.dumps({'deprecated':True,'reason':'旧五帧观察已过时，不作为当前进度','currentInventory':'review/run_EW_inventory.json','additionalInventory':'review/run_NE_inventory.json','scope':'E/W与NE的当前记录；全八向库存由根代理汇总','currentTiming':{'frameMs':75,'loopMs':1200},'updated':'2026-10-04'},ensure_ascii=False,indent=2),encoding='utf-8')
