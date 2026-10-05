from pathlib import Path
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
for direction in ["E","W"]:
    sheet=Image.new("RGB",(960,350),(216,222,214));draw=ImageDraw.Draw(sheet)
    for col,n in enumerate([8,9,10]):
        im=Image.open(B/"runtime/attack"/direction/f"{n:02d}.png").resize((320,320),Image.Resampling.LANCZOS)
        bg=Image.new("RGBA",im.size,(216,222,214,255));bg.alpha_composite(im)
        sheet.paste(bg.convert("RGB"),(col*320,0));draw.text((col*320+8,325),f"attack {direction} {n:02d} / 30ms",fill="black")
    sheet.save(D/f"{direction}-08-09-10-full320.jpg",quality=97)
print("E/W recovery comparisons written")

