from pathlib import Path
B=Path(__file__).parent;S=B.parent/'r06_c10'
s=(S/'full-chain-proof.py').read_text().replace('r06_c10','r05_c10').replace('r07_c10','r06_c10').replace('[36864,20480,40960,24576]','[36864,16384,40960,20480]').replace('finalCoupled07','finalCoupled06')
(B/'full-chain-proof.py').write_text(s)
s=(S/'prepare-whole-qa.py').read_text().replace('24256','20160').replace('24896','20800')
(B/'prepare-whole-qa.py').write_text(s)
