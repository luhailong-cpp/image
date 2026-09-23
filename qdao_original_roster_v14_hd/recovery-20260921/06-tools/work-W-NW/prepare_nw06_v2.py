from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent));import archive_generation as archive
GEN=HERE.parent.parent/'06-generation'
r=json.loads((GEN/'NW08-single-v2/request.json').read_text())
r['referenced_image_paths'][2]=str(GEN/'NW05-single-v1/raw.png');r['referenced_image_paths'][3]=str(GEN/'NW07-single-v1/raw.png')
p=r['prompt'];p=p[:p.index('POSE NW08')]+'POSE NW06 RIGHT leg late swing, one frame after reference3 NW05: LEFT leg is fully supporting, left foot at SCREEN LEFT x43% y93% flat planted, left knee nearly straight. RIGHT leg at SCREEN RIGHT has its knee bent about 70 degrees and swings forward AWAY toward upper-left, right boot center x60% y85%, clearly raised, some sole still visible but less than reference3. Right boot never is the lowest foot. Do not exchange leg identity or heel elevations. Compared with NW05, open the right knee a little, move right boot a little further forward away and down. Compared with NW07, the right leg must be more flexed and airborne, left heel must be more flat.\n'+p[p.index('Ensure the two legs'):p.index('\nCRITICAL:')]
p += '\nCRITICAL: LEFT foot screen-left LOW planted, RIGHT foot screen-right HIGH raised. The current requested right-swing foot order is exactly like NW05, reference3. No left lifted foot. Keep both boots separate and connected naturally to correct hips.\n'
archive.prepare('NW06-single-v2',p,r['referenced_image_paths'])
