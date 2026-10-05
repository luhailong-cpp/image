from repair import *
import numpy as np
seg=int(sys.argv[1]);version=sys.argv[2] if len(sys.argv)>2 else 'v1'
target=R/f's{seg}-target-native.png';generated=R/f's{seg}-repair-{version}.png'
a=Image.open(target).convert('RGB');b=Image.open(generated).convert('RGB')
mask=Image.new('L',(1254,1254),0);mask.paste(255,(627,115,915,1139));mp=R/f's{seg}-mask-{version}.png';mask.save(mp)
derived(mp,[target,generated],{'method':'hard right-only binary repair mask','rectLTRB':[627,115,915,1139],'feather':0})
a.paste(b.crop((627,115,915,1139)),(627,115))
joined=R/f's{seg}-joined-{version}.png';a.save(joined)
derived(joined,[target,generated,mp],{'method':'exact right-only native crop replacement','rectLTRB':[627,115,915,1139],'resampling':None})
qa=R/f's{seg}-qa-{version}.png';a.crop((507,115,1035,1139)).save(qa)
derived(qa,[joined],{'method':'native crop','boxLTRB':[507,115,1035,1139],'jointImageX':120,'rightBoundaryImageX':408})
strip=R/f's{seg}-strip-{version}.png';b.crop((627,115,915,1139)).save(strip)
derived(strip,[generated],{'method':'native integer crop','sourceBoxLTRB':[627,115,915,1139],'globalRectXYWH':[49152,32768+(seg-1)*1024,288,1024],'resampling':None,'status':'pending_visual_review'})
