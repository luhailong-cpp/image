from prepare_repair import *
v=HERE/"geometry-east-v2";req=read(v/"repair.request.json");raw=v/"host-result-shifted.png";source=Path("C:/Users/luyua/.codex/generated_images/01a11b0f-f960-71e1-a23f-11564ac63532/exec-0142a84a-9401-451e-9856-44b7843b16c8.png")
im=Image.open(raw);assert im.size==(1254,1254)
write(str(raw)+".generation.json",dict(**ref(raw),generatedAt=datetime.now(timezone.utc).isoformat(),width=1254,height=1254,format="PNG",tool="image_gen.imagegen",route="builtin",configSnapshot=req["configSnapshot"],submittedParameters=req["submittedParameters"],actualSubmitted=req["actualSubmitted"],actualModel=None,actualQuality=None,unverifiedReason="Host-managed builtin does not expose actual model/quality",evidence={"sourceOutputPath":str(source),"sourceOutputSha256":sha(source),"resultId":source.stem},prompt=req["prompt"],promptSha256=req["promptSha256"],references=req["references"],mapping=ref(v/"mapping.json"),approvedForPromotion=False))
text=(HERE/"diagnose_geometry_east.py").read_text().replace('v=HERE/"geometry-east-v1";d=v/"bounded-v2"','v=HERE/"geometry-east-v2";d=v/"bounded"').replace('alpha=smooth((xx-932)/70)*smooth((yy-545)/50)*smooth((885-yy)/70)','alpha=smooth((xx-902)/70)*smooth((yy-515)/50)*smooth((905-yy)/50)').replace('[932,545,1139,885]','[902,515,1139,905]').replace('[1002,595,1139,815]','[972,565,1139,855]').replace('for n in ["qa-east-endpoint.png","qa-local-return.png"]','for n in []')
text=text[:text.index('write(v/"hard-composite-review.json"')]+ '\nprint(json.dumps(stats))\n'
path=HERE/"diagnose_geometry_east_v2.py";path.write_text(text,encoding="utf-8")
print(str(raw))

