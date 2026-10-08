from pathlib import Path
from PIL import Image
import sys,json,hashlib,shutil
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;T=R/'r08_c16';NAME=sys.argv[-1] if sys.argv[-1].startswith('r0') else 'r01_c04';D=T/'repairs'/f'{NAME}-quiet-water';N=T/'native'/f'{NAME}.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prep():
 D.mkdir(parents=True,exist_ok=True)
 prompt='''Use case: precise-object-edit. Edit IMAGE 1 only. Remove ALL the invented bright interlocking water ripples and dense light patches. Restore the calm smooth blue/cyan WATER MATERIAL of IMAGE 3 (the exact original guide for this crop). This entire square is unoccupied quiet open water. Keep its overall blue/cyan hue and gentle existing lighting. Use only a FEW very broad soft low-contrast hand-painted color transitions, each hundreds of pixels wide. No narrow bright edges, no sharp ripple contours, no foamy streaks, no pale highlights, no caustic network, no small cells and no mottled repeated texture. The surface should read as one calm clean softly shaded plane, never a patterned material swatch. Do not add any objects or horizon, do not change framing. IMAGE 2 is the primary confirmed rounded Q-style rendering quality only; do not copy UI. Exact same full opaque 1254x1254 square composition; no border, transparent strip, black strip, text, noise, blur filter or photorealism. Highest available finish. Return only the corrected image 1.'''
 prompt=prompt.replace('This entire square is unoccupied quiet open water.', 'Preserve exactly every existing non-water object, including any cropped golden post cap or boat parts; do not move, remove, or repaint them. Change ONLY the water material.')
 refs=[{'file':str(N),'sha256':sha(N),'role':'edit target, incorrect dense bright water pattern to remove'}, {'file':str(R.parents[3]/'designs/gameplay-ui/04-guild.png'),'sha256':sha(R.parents[3]/'designs/gameplay-ui/04-guild.png'),'role':'primary confirmed style only'}, {'file':str(T/'guides'/f'{NAME}.png'),'sha256':sha(T/'guides'/f'{NAME}.png'),'role':'exact crop guide for required quiet soft low-contrast water material, not final pixels'}]
 if NAME=='r01_c03':
  prompt='''Use case: precise-object-edit. Edit IMAGE 1 only. Remove the artificial straight vertical water color seam at x approximately 1024, where the rightmost 230-pixel neighbor-context strip begins. It is an image stitch artifact, not a physical water boundary. Connect the existing soft low-contrast blue/cyan fields naturally through that thin vertical junction, with no straight edge and no added water ripples. Keep the slanted golden rope at the left completely unchanged; keep all broad water colors, quiet smooth material, framing and daylight unchanged. Do not invent waves, foam, pale lines, grain or sharp water patterns. IMAGE 2 is primary confirmed rounded hand-painted style only. IMAGE 3 identifies the same framing and original colors but its straight context-strip boundary must also be removed, not copied. Correct only the visible tonal seam, with subtle continuous blue fields around it. Keep exact 1254x1254 opaque square composition. Return only image 1 corrected.'''
  refs[0]['role']='edit target, remove artificial vertical water-context boundary near x1024'
  refs[2]['role']='same layout/colors reference only, artificial boundary is not scene geometry'
 if NAME=='r02_c03':
  prompt='''Use case: precise-object-edit. Edit IMAGE 1 only. Restore ONE missing existing object fragment: the cropped golden rounded post cap at the BOTTOM-RIGHT edge, exactly as it appears in IMAGE 3. Its top begins near y1037, its left edge near x1080, and the right and bottom sides are cropped by the square edges. Copy its existing curved silhouette, golden color and gentle rounded shading from IMAGE 3, at exactly the same size and location. Do not invent a whole post or change the crop. IMAGE 3 contains real neighboring native pixels for this golden cap. Keep the diagonal rope, wooden rail fragment, all quiet blue water, camera and lighting in IMAGE 1 unchanged. IMAGE 2 is primary confirmed rounded clean hand-painted style only. No other addition, no ripples, no bright water patterns, no text or border. Return one corrected opaque 1254x1254 image 1 with only the missing cap fragment restored.'''
  refs[0]['role']='edit target, restore missing bottom-right existing golden cap fragment'
  refs[2]['role']='exact crop and actual right native overlap showing the missing golden post cap'
 if NAME=='r04_c04':
  prompt='''Use case: precise-object-edit. Edit IMAGE 1 only. Remove ONLY the invented shiny GOLD METAL RIM/BAND clipped across the wooden boat fragment at the very top-left (roughly x100-285, y0-48). Restore simple continuous warm brown wooden planks in that tiny area, using the corresponding part of IMAGE 3 as exact shape and material guide. There is no metal collar or decoration there. Keep the rest of the wooden fragment, its exact outer contour, all quiet blue water and all daylight colors UNCHANGED. No new plank details or objects. IMAGE 2 is primary confirmed clean rounded Q-style hand-painted quality, no UI. Keep exact full-square framing and dimensions. This is one tiny unwanted added-detail removal, not a repaint of the scene. No text, border, ripple patterns, noise, additional highlights or contrast change. Return only one opaque 1254x1254 corrected image 1.'''
  refs[0]['role']='edit target, remove only invented gold rim in top-left overlap'
  refs[2]['role']='exact native neighbor context guide, plain wood with no invented gold rim'
 (D/'prompt.txt').write_text(prompt,encoding='utf-8');js(D/'references.json',refs)
 print(json.dumps({'prompt':prompt,'references':[x['file'] for x in refs]}))
def adopt(src):
 src=Path(src);im=Image.open(src);assert im.size==(1254,1254)
 oldrecord=Path(str(N)+'.generation.json');old=json.loads(oldrecord.read_text(encoding='utf-8'))
 assert old['sha256']==sha(N)
 historical=D/'superseded-generation.json';shutil.copyfile(oldrecord,historical)
 refs=json.loads((D/'references.json').read_text(encoding='utf-8'));assert refs[0]['sha256']==sha(N)
 refs[0].update(availability='superseded',historicalRecord=str(historical),historicalRecordSha256=sha(historical),pixelValidation='historical-record-only-not-current-pixels')
 shutil.copyfile(src,N)
 new=dict(old,file=str(N),sha256=sha(N),generatedAt=datetime.now(timezone.utc).isoformat(),evidence={'toolResultSourcePath':str(src),'toolResultSha256':sha(src),'responseMetadata':'Local result path; model and quality not disclosed.'},prompt=str(D/'prompt.txt'),promptSha256=sha(D/'prompt.txt'),references=refs)
 new['submittedParameters']['referenced_image_paths']=[x['file'] for x in refs]
 js(oldrecord,new)
 results={'r01_c03':'water-context tonal seam connected','r02_c03':'missing bottom-right existing golden cap restored','r04_c04':'invented gold rim removed, boat and quiet water retained'}
 js(D/'review.json',{'sourceSha256':old['sha256'],'correctedSha256':sha(N),'actualVisualInspection':'performed on tool result','result':results.get(NAME,'dense water texture removed; quiet low-contrast material restored'),'formalAccepted':False})
 print(json.dumps({'file':str(N),'sha256':sha(N)}))
if sys.argv[1]=='prepare':prep()
elif sys.argv[1]=='record':adopt(sys.argv[2])
