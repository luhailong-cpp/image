"""Extract the accepted title plaque; all slicing stays in the image project."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json

root = Path(__file__).resolve().parent
source = root.parent / 'qdao_ui_redesign_v5/01_login_2560x1080.png'
box = (140, 75, 1100, 570)
# Hand-traced outer contour of the actual gold plaque in the approved image.
# This is a cutout mask, not replacement artwork or a generated title.
points = [
    (496,8),(516,15),(530,30),(533,47),(527,61),(548,62),
    (551,45),(565,48),(574,61),(588,68),(595,83),(593,96),(586,105),
    (596,92),(610,86),(627,87),(641,95),(647,108),(648,123),(642,136),
    (637,139),(654,145),(681,149),(708,158),(735,168),(748,169),
    (774,156),(803,150),(830,151),(850,156),(877,173),(882,165),
    (894,156),(911,155),(925,160),(936,171),(941,187),(939,204),
    (932,218),(919,225),(929,245),(939,273),(944,300),(942,328),
    (934,354),(921,377),(904,392),(889,409),(884,425),(869,437),
    (849,443),(824,446),(800,444),(774,437),(746,425),(724,436),
    (695,445),(661,452),(626,455),(589,454),(552,449),(522,443),
    (512,453),(509,472),(500,489),(490,478),(486,455),(477,445),
    (440,452),(402,456),(363,456),(324,453),(291,447),(269,441),
    (250,432),(244,427),(224,436),(200,442),(174,445),(148,441),
    (127,432),(114,420),(111,404),(96,398),(76,382),(61,361),
    (51,336),(47,308),(49,278),(55,253),(65,232),(72,222),
    (62,210),(58,195),(59,179),(65,166),(76,156),(90,152),
    (104,153),(116,160),(125,170),(129,180),(149,169),(177,156),
    (201,151),(223,152),(246,157),(267,166),(278,172),(290,173),
    (313,162),(340,153),(369,147),(387,137),(390,127),(384,118),
    (375,117),(369,122),(359,120),(351,111),(351,101),(357,92),
    (369,87),(385,87),(398,91),(407,101),(411,113),(412,117),
    (421,108),(408,103),(402,95),(399,82),(402,69),(411,59),
    (431,48),(445,45),(444,54),(435,62),(433,70),(441,71),
    (450,65),(464,60),(461,46),(464,30),(476,17)
]
im = Image.open(source).convert('RGBA').crop(box)
scale = 4
mask = Image.new('L', (im.width*scale, im.height*scale))
ImageDraw.Draw(mask).polygon([(x*scale,y*scale) for x,y in points], fill=255)
im.putalpha(mask.resize(im.size, Image.Resampling.LANCZOS))
dest = root / 'additional/title_logo.png'
dest.parent.mkdir(parents=True, exist_ok=True)
im.save(dest)
meta = {'source': str(source), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'crop_xyxy': box, 'contour': points, 'method': 'manual alpha contour, 4x antialias mask; original title pixels retained',
        'output': 'title_logo.png', 'size': im.size, 'resampled_artwork': False}
dest.with_suffix('.extraction.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
bg = Image.new('RGBA', im.size, '#174C42'); bg.alpha_composite(im)
bg.convert('RGB').save(root / 'qa/title_cutout_check.jpg', quality=94)
print(dest)
