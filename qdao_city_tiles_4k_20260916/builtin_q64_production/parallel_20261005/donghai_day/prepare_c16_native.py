"""c16-only native preparation with quiet water preserved."""
import sys,json
import production_r08_c16 as w
p=w.p
r=int(sys.argv[1]);c=int(sys.argv[2]);name=f'r{r:02d}_c{c:02d}'
assert not (p.T/'native'/f'{name}.png').exists(), 'Native patch already exists; do not regenerate it.'
w.guide(r,c)
prompt='''Use case: precise-object-edit. Edit IMAGE 1 only for an opaque native-pixel crop of a bright clean rounded Q-style fishing village. Preserve the calm smooth blue/cyan WATER MATERIAL exactly as shown: a few extremely broad, soft, low-contrast color fields. Do not draw new water details. Do NOT turn the water into a crisp pattern or textured swatch. No new ripple contours, cells, foam, bright streaks, wave blocks, caustic lines, pale patches or grain. The quiet blue plane is intentional final art, not missing detail.
Polish ONLY the existing pictured cropped boat, wood, rope, net or small post if actually present. Retain every pictured shape, precise position, outline, proportion, color and light. Already-sharp strips at any edge are actual native neighboring context: preserve their geometry and water colors exactly; continue those forms naturally across the sharp/soft transition without a physical line. If the entire field contains only water, output only the quiet low-contrast water surface with no objects. Do not add an object, structure, ornament or extra plank joint. Keep smooth rounded warm timber volume, clean outlines and restrained highlights. Do not invent gold metal bands or extra rope.
IMAGE 2 is the primary user-confirmed style for controlled rounded hand-painted forms and material quality only, no UI. Keep the camera, crop and composition fixed. Fill the whole field opaquely without black, blank or transparent borders. No text, characters, crop, zoom, blur filter, oversharpening or photoreal texture. Return one opaque 1254x1254 native image, highest available finish, exact field of view.'''
if c==4:prompt+=' The outermost right 115 pixels are blue-water context beyond the map bounds, cropped out of the final core.'
refs=[{'file':str(p.T/'guides'/f'{name}.png'),'role':'edit target; quiet water intentional; sharp edge strips actual native neighbors; soft existing objects reference-only'}, {'file':str(p.STYLE),'role':'primary confirmed style and materials, no UI'}]
for x in refs:x['sha256']=p.sha(x['file'])
(p.T/'prompts'/f'{name}.txt').write_text(prompt,encoding='utf-8');p.savej(p.T/'prompts'/f'{name}.references.json',refs)
print(json.dumps({'name':name,'prompt':prompt,'references':[x['file'] for x in refs]}))
