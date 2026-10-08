from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parent
Image.open(R/'native.png').crop((440,170,850,430)).save(R/'notch-qa.png')
