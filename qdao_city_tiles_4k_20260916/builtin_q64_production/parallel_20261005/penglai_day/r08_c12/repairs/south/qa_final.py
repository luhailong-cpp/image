from helper import *
import numpy as np
from PIL import ImageDraw
north=R/'output/r08_c12-south-candidate-v3.png';south=R/'output/r09_c12-north-candidate-v3.png'
full=Image.new('RGB',(4096,8192));full.paste(Image.open(north),(0,0));full.paste(Image.open(south),(0,4096))
qa=R/'qa/final-v3';qa.mkdir(exist_ok=True)
records=[]
for name,y,h in [('north-return',3469,320),('shared',3936,320),('south-old-return',4480,320),('south-final-return',4800,400)]:
 sheet=Image.new('RGB',(1024,4*(h+24)),(24,24,24));d=ImageDraw.Draw(sheet)
 for i in range(4):
  box=(i*1024,y,(i+1)*1024,y+h);d.text((7,i*(h+24)+4),f'{name} segment{i+1} native pixels',fill='white');sheet.paste(full.crop(box),(0,i*(h+24)+24))
 dest=qa/(name+'.png');sheet.save(dest);p.derived(dest,[north,south],{'method':'native strips stacked no resize','combinedY':y,'height':h});records.append(str(dest))
# final-return board split to keep each image within native1600
big=Image.open(qa/'south-final-return.png')
for k in range(2):
 dest=qa/f'south-final-return-half{k+1}.png';big.crop((0,k*848,1024,(k+1)*848)).save(dest);p.derived(dest,[qa/'south-final-return.png'],{'method':'native split no resize'})
review={'reviewedAt':p.stamp(),'actualVisualInspection':True,'internal':{'candidate':str(N),'sha256':p.sha(N),'sixFullInternalLinesViewed':True,'nineJunctionsViewed':True,'registrationMaxAbsPixels':1.2656754897687903,'nativeScale':1,'findings':'Rectangular material seams removed; consistent broad foliage, wood contours and roof geometry. Subpixel registration improves small groove transitions; no large incompatible geometry remained internally.'},'south':{'sixAiNativeOutputs':[{'file':str(R/'native'/f'{n}.png'),'sha256':p.sha(R/'native'/f'{n}.png')} for n in ['s1','s2','s3','s4','return-curb','return-wood']],'firstPassFindings':'The shared boundary became continuous, but s2/s3 lower returns created clear curb/leaf/wood notches; rejected for final acceptance.','finalLocalFix':'Native AI return-curb and return-wood, binary cuts and limited RGB fields. Return-curb cut expanded into clean ground to preserve whole stone outline.','sourceBoundaryModel':'Single teal planter, uninterrupted trunk, one coherent curb, continuous window and doorway','returnInspectionPendingLastBoards':True},'formalAccepted':False,'wholeMapComplete':False}
p.write(qa/'review.json',review)
print(qa)
