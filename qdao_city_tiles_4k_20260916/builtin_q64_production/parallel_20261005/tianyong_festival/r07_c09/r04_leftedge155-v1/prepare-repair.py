from pathlib import Path
from PIL import Image
D=Path(__file__).parent;R=D/'repair-v1';R.mkdir(exist_ok=True)
A=Image.open(D/'native.png').convert('RGBA');C=Image.open(D/'context.png').convert('RGBA');A.alpha_composite(C);A.convert('RGB').save(R/'native-with-exact-anchors.png')
