"""Water-preserving prompt for the eastern boundary native column."""
import sys,json
import production_r08_c16 as w
p=w.p
r=int(sys.argv[1]);name=f'r{r:02d}_c04'
w.guide(r,4)
prompt='''Use case: precise-object-edit. Edit IMAGE 1 only for an opaque native-pixel crop of a bright clean rounded Q-style fishing village. Preserve the calm smooth blue/cyan WATER MATERIAL exactly as shown: a few extremely broad, soft, low-contrast color fields. Do not draw new water details. Do NOT turn the water into a crisp pattern or textured swatch. No new ripple contours, cells, foam, bright streaks, wave blocks, caustic lines, pale patches or grain. The quiet blue plane is intentional final art, not missing detail.
Polish ONLY the existing pictured wooden boat fragment and small capped post if present. Retain all pictured shapes, precise positions, outlines, proportions, colors and light. At the top, the already-sharp 230-pixel overlap is actual native previous-row context: preserve its golden cap geometry and water colors; continue those forms without a line at the overlap boundary. If a part of the field contains only water, leave it as quiet water. Do not add any object or structure. Keep smooth rounded warm timber volume, clean outlines and restrained highlights.
IMAGE 2 is the primary user-confirmed style for controlled rounded hand-painted forms and material quality only, no UI. Keep the camera, crop and composition fixed. The rightmost 115 pixels are only open-water context beyond the 65536-pixel map edge and will be excluded from the final core: fill them naturally without black, blank or transparent border. No text, characters, crop, zoom, blur filter, oversharpening or photoreal texture. Return one opaque 1254x1254 native image, highest available finish, exact field of view.'''
refs=[{'file':str(p.T/'guides'/f'{name}.png'),'role':'edit target; quiet water is intentional, sharp upper strip is actual native neighbor context; soft boat interior reference requires polish'}, {'file':str(p.STYLE),'role':'primary confirmed style and materials, no UI'}]
for x in refs:x['sha256']=p.sha(x['file'])
(p.T/'prompts'/f'{name}.txt').write_text(prompt,encoding='utf-8');p.savej(p.T/'prompts'/f'{name}.references.json',refs)
print(json.dumps({'name':name,'prompt':prompt,'references':[x['file'] for x in refs]}))
