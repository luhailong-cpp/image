from prepare_repair import *
v=HERE/"geometry-east-v3";req=read(v/"repair.request.json");raw=v/"host-result-shifted.png";source=Path("C:/Users/luyua/.codex/generated_images/01a11b0f-f960-71e1-a23f-11564ac63532/exec-7f3a8e0b-43e7-466b-aadf-677dbd123a1a.png")
im=Image.open(raw);assert im.size==(1254,1254)
write(str(raw)+".generation.json",dict(**ref(raw),generatedAt=datetime.now(timezone.utc).isoformat(),width=1254,height=1254,format="PNG",tool="image_gen.imagegen",route="builtin",configSnapshot=req["configSnapshot"],submittedParameters=req["submittedParameters"],actualSubmitted=req["actualSubmitted"],actualModel=None,actualQuality=None,unverifiedReason="Host-managed builtin does not expose actual model/quality",evidence={"sourceOutputPath":str(source),"sourceOutputSha256":sha(source),"resultId":source.stem},prompt=req["prompt"],promptSha256=req["promptSha256"],references=req["references"],mapping=ref(v/"mapping.json"),approvedForPromotion=False))
text=(HERE/"diagnose_geometry_east_v2.py").read_text().replace('v=HERE/"geometry-east-v2"','v=HERE/"geometry-east-v3"').replace('alpha=smooth((xx-902)/70)*smooth((yy-515)/50)*smooth((905-yy)/50)','alpha=smooth((xx-844)/50)*smooth((yy-525)/50)*smooth((885-yy)/50)').replace('[902,515,1139,905]','[844,525,1139,885]').replace('[972,565,1139,855]','[894,575,1139,835]').replace('(902,515,1254,915)','(814,495,1254,915)')
path=HERE/"diagnose_geometry_east_v3.py";path.write_text(text,encoding="utf-8")
print(str(raw))

