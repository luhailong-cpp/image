import sys,io,base64
from PIL import Image
im=Image.open(sys.argv[1]).convert('RGBA');im.thumbnail((900,900));b=Image.new('RGB',im.size,'#f3ebdb');b.paste(im,mask=im.getchannel('A'));f=io.BytesIO();b.save(f,format='JPEG',quality=80);print(base64.b64encode(f.getvalue()).decode())
