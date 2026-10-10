from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'repair_r10_c16_north_color_v2.py').read_text().replace("D=T/'repairs/north-integrated-color-v2'","D=T/'repairs/north-integrated-color-v3'")
s=s.replace('raw_all=base.copy();image=base.copy();operations=[]','''raw_all=base.copy();image=base.copy();operations=[]
# Root-authorized completion of the original top-row internal difference fields.
authorization=a.load_json(T/'repairs/north-color-scope-authorization.json')
assert authorization['coreRowsAllowed']==[0,800] and authorization['approvedBy']=='root'
prefix=np.zeros((800,4096,3),np.int16);weight=np.ones(800,np.float32)
fade=np.linspace(0,1,101,dtype=np.float32);fade=fade*fade*(3-2*fade);weight[700:800]=1-fade[:100]
prefix_sources=[]
for left in (1,2,3):
 fp=T/'repairs/internal-color-match-v2/fields'/f'vertical_r01_c{left:02d}_c{left+1:02d}.npz'
 with np.load(fp) as saved:
  rect=saved['rect_extended_xywh'];x=int(rect[0])-115;corr=saved['correction_rgb_i16'][115:915]
 prefix[:,x:x+230]=np.rint(corr.astype(np.float32)*weight[:,None,None]).astype(np.int16)
 prefix_sources.append(j.ref(fp))
image[:800]=np.clip(image[:800].astype(np.int16)+prefix,0,255).astype(np.uint8)
np.savez_compressed(F/'prefix-internal-field.npz',correction_rgb_i16=prefix,weight_f16=weight.astype(np.float16))''')
s=s.replace('assert np.array_equal(image[627:],original[627:])','assert np.array_equal(image[800:],original[800:])')
s=s.replace('belowY627ExactlyPreserved=True','belowY627ExactlyPreserved=False,belowY800ExactlyPreserved=True,scopeAuthorization=j.ref(T/\'repairs/north-color-scope-authorization.json\'),prefixSources=prefix_sources,prefixInternalField=j.ref(F/\'prefix-internal-field.npz\')')
s=s.replace("assert a.sha(ep)==ns and a.sha(V/'candidate.png')==EXPECTED", "for k,x in enumerate([909,1933,2957],1):extra.append(a.save_image(Q/f'prefix-transition-{k}.png',Image.fromarray(image[580:930,x-110:x+340])))\nassert a.sha(ep)==ns and a.sha(V/'candidate.png')==EXPECTED")
(p/'repair_r10_c16_north_color_v3.py').write_text(s,encoding='utf-8')
