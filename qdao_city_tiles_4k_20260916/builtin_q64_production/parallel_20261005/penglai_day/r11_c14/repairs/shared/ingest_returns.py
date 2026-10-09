from pathlib import Path
import sys
from PIL import Image
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));import ai_helper as h
G=Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
for n,g in [('north-return','54f4c917-ecee-4e73-8586-bbfc9d30e50e'),('ne-return','a0f11275-2741-4c1a-951a-03f988ecf4f2'),('rail-return','0c7f4f4b-dabb-416d-bc34-9515eab6086b')]:h.ingest(n,G/('exec-'+g+'.png'))
for label in ['source','generated']:
 p=O/('ne-return-'+label+'.png');d=O/('ne-gap-'+label+'-qa.png');Image.open(p).crop((280,400,650,740)).save(d);h.derived(d,[p],{'method':'native QA crop','bbox':[280,400,650,740]})

