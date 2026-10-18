from workflow import *
from PIL import Image
import numpy as np
s=(ROOT/'record_and_prepare_root_20261016.py').read_text(encoding='utf-8')
exec(s[s.index('def request('):s.index("f=ROOT/'tiles/r08_c13.candidate")])
exec(s[s.index("tid='r08_c12';target="):])
