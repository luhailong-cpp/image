from pathlib import Path
import sys
sys.dont_write_bytecode=True
import ai_helper as h
base=Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
for i,f in enumerate(['exec-30ba13c9-521f-47aa-9dae-9129ef546a44.png','exec-63f5ac2e-5beb-4439-9ffb-966d0e55f62c.png','exec-5d898b4d-3ead-472f-a239-23335a153303.png','exec-5abc1d13-90b5-404e-9f16-8b98b133c1bc.png'],1):h.ingest(f'west{i}-ai-v1',base/f)
