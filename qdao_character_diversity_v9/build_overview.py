"""Build the final review index from delivered PNGs; no generated source art."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PACK = HERE.parent / 'q_daoist_character_pack_4096'


def main():
    manifest = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
    rows = [row for row in manifest['assets'] if 'age_direction' in row]
    width, header, cw, ch = 2640, 150, 440, 520
    canvas = Image.new('RGB', (width, header + 4 * ch + 75), '#f1eee5')
    draw = ImageDraw.Draw(canvas)
    font_path = str(Path('C:/Windows/Fonts/msyh.ttc'))
    title = ImageFont.truetype(font_path, 48)
    label = ImageFont.truetype(font_path, 27)
    small = ImageFont.truetype(font_path, 23)
    draw.text((45, 25), '五行奇谈 · 原创道家 Q 版群像', font=title, fill='#264943')
    draw.text((48, 95), '01—22 人物差异化 / 直发、束发与辫发 / 4096 × 4096 透明成品', font=small, fill='#52645a')
    for i, row in enumerate(rows):
        x, y = (i % 6) * cw, header + (i // 6) * ch
        with Image.open(PACK / row['path']) as original:
            im = original.crop(original.getchannel('A').getbbox())
            im.thumbnail((cw-48, ch-85), Image.Resampling.LANCZOS)
            canvas.paste(im, (x + (cw-im.width)//2, y + ch-70-im.height), im)
        draw.text((x+28, y+ch-55), f"{row['id'][:2]}  {row['name']}", font=label, fill='#264943')
    draw.text((4*cw+25, header+3*ch+170), '22 个独立人物造型', font=label, fill='#264943')
    draw.text((4*cw+25, header+3*ch+222), '脸型 · 年龄 · 职业 · 体态', font=small, fill='#52645a')
    draw.text((4*cw+25, header+3*ch+267), '00 与额外主角参考保持原样', font=small, fill='#52645a')
    draw.text((48, header+4*ch+18), '正式成品索引；实际素材均为独立 RGBA PNG。此总览为排版合成，人物来自逐张内置生图。', font=small, fill='#52645a')
    canvas.save(HERE / 'roster_overview.png', optimize=True)
    print('Final roster index: 22 portraits')


if __name__ == '__main__':
    main()
