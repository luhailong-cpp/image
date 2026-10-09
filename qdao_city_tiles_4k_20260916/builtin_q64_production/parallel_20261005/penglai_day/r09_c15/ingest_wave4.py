import helper as h
from pathlib import Path
src=Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
for n,p in {'p14':'exec-a4061195-f5ac-4713-b825-65ef15301cc8.png','p23':'exec-851ecdb0-e804-47e9-85cc-c2234d49e73e.png','p32':'exec-958e9ebd-aca2-443c-b1bf-539502bea4a4.png','p41':'exec-f445adb4-bf6c-40d7-b8b4-e8e555d05331.png'}.items():h.ingest(str(src/p),n)
