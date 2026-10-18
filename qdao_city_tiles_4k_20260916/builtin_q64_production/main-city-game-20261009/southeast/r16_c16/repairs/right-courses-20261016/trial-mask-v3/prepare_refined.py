from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'compose_mask.py').read_text(encoding='utf-8')
s=s.replace("D=Path(__file__).resolve().parent;R=D.parent","BASE=Path(__file__).resolve().parent;R=BASE.parent;D=BASE/'refined-v1';D.mkdir(exist_ok=False)")
s=s.replace("np.rint(1328-.435*xs),np.rint(1489-.677*xs)","np.rint(1332-.45*xs),np.rint(1494-.667*xs)")
s=s.replace("xs<=470","xs<=473")
s=s.replace("np.arange(-8,1)","np.arange(-2,3)")
s=s.replace("(bottom[None,:]-ys)/3","(bottom[None,:]-ys)/2")
s=s.replace("bottom alpha3","bottom alpha2")
out=D/'compose_refined.py';assert not out.exists();out.write_text(s,encoding='utf-8')

