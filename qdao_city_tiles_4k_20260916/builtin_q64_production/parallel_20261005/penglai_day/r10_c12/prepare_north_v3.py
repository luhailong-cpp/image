from helper import *
north=BASE/'repairs/left-edge/both-side/c12-right-revised-candidate-v3.png'
assert p.sha(north)=='5360e699ffd62956298a39a9acfdf585baad778f71d63fad0d82afb343c6bc66'
src=ROOT/'guides/p14.png'
im=Image.open(src).convert('RGB')
# p14 guide x=3072 in halo canvas; tile coordinate is x-115.
im.paste(Image.open(north).convert('RGB').crop((2957,3981,4096,4096)),(0,0))
dest=ROOT/'guides/p14-north-v3.png';im.save(dest)
p.derived(dest,[src,north],{'method':'replace exact native north115px; preserved geometry reference below','northSourceBoxLTRB':[2957,3981,4096,4096],'targetXY':[0,0],'guideOnly':True,'formalAccepted':False})
anchor=ROOT/'references/north-p14-v3-native.png'
Image.open(north).convert('RGB').crop((2957,2842,4096,4096)).save(anchor)
p.derived(anchor,[north],{'method':'exact native crop north context for p14','sourceBoxLTRB':[2957,2842,4096,4096],'referenceOnly':True})
print(dest)
