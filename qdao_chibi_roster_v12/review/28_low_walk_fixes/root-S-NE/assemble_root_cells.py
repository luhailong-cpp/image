from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
r=Path(r'E:\work\image\qdao_chibi_roster_v12');p=r/'review/28_low_walk_fixes/root-S-NE';c=r/'candidate-stable-body/28_moon_rabbit_artificer'
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
records=[]
for d in ['S','NE']:
 src=p/(d+'04-'+d+'08-low-raw.png');native=Image.open(src).convert('RGBA');norm=native.resize((886,443),Image.Resampling.LANCZOS);oldsrc=c/'source'/('walk-'+d+'-final.png');old=Image.open(oldsrc).convert('RGBA');out=old.copy()
 for j,phase in enumerate([4,8]):
  box=[j*443,0,(j+1)*443,443];cell=norm.crop(box);cp=p/(d+f'{phase:02d}-cell.png');cell.save(cp);idx=phase-1;out.paste(cell,(idx%4*443,idx//4*443))
  records.append({'direction':d,'canonical_phase':phase,'cell_path':str(cp),'cell_sha256':sha(cp),'source_path':str(src),'source_sha256':sha(src),'native_size':list(native.size),'source_grid':[2,1],'source_grid_index':j+1,'whole_sheet_resolution_normalization':[886,443],'cell_box':box,'cell_size':[443,443],'original_selected_source':str(oldsrc),'original_selected_source_sha256':sha(oldsrc),'original_phase':phase,'canonical_cycle_rotation':0,'prompt_path':str(p/(d+'04-'+d+'08-low-prompt.txt')),'mirror':False,'body_bbox_fit':False,'synthetic_frame':False})
 for i in [0,1,2,4,5,6]:
  b=(i%4*443,i//4*443,i%4*443+443,i//4*443+443);assert old.crop(b).tobytes()==out.crop(b).tobytes()
 target=p/(d+'-selected-full-sheet.png');out.save(target)
 board=Image.new('RGB',(1200,660),'#ff00ff');draw=ImageDraw.Draw(board)
 for i in range(8):
  b=(i%4*443,i//4*443,i%4*443+443,i//4*443+443);board.paste(out.crop(b).resize((300,300)),(i%4*300,i//4*330+25));draw.text((i%4*300+8,i//4*330+4),d+f'{i+1:02d}',fill='black')
 board.save(p/(d+'-full-cycle-review.jpg'),quality=92)
(p/'selected-source-map.json').write_text(json.dumps({'status':'root_generated_and_source_inspected_pending_full_cycle_review','records':records,'untouched_full_source_cells_verified':12},indent=2)+'\n')
print('Prepared4 authored cells and2 full-sheet previews;12 unchanged original cells preserved')

