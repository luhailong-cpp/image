from pathlib import Path
p=Path(r'E:\work\image\qdao_chibi_roster_v12\review\approve_lion_guard_20260914.py')
t=p.read_text(encoding='utf-8-sig')
t=t.replace('25_lion_drum_guard','23_lantern_courier').replace('25-lion-guard','23-lantern-courier').replace('25_lion_guard_natural_fixes','23_lantern_natural_fixes').replace('5d90d5b04eea74bf5f780e221fc5cfb8e1de313faac344e9258a4e9b45a7b840','385c3158106d5e5a9b439d2015a714a0e13c6c24c90dd9d801699f08c7bd72b6')
t=t.replace('Distinct short-haired sturdy lion drum guard identity, red and ivory cloth costume, dark trousers, wraps and boots; no magical light or fantasy armor.','Distinct twin-braid young lantern courier identity; warm red and ochre cloth, ivory trousers, cloth-wrapped boots and a single paper lantern in anatomicalLEFT hand. No magical aura or fantasy armor.')
t=t.replace('10 authored lower pre-contact poses remove the prior high-knee march; strong guard strides and modest rear heel lift retained as character motion.','10 authored lower pre-contact poses in E/SE/S/SW/W remove front kicks; existing light courier strides, modest heel lift and rear-view foot depth retained.')
t=t.replace('3 idle head shapes rebuilt to match same-direction walks; source changes limited to13 whole cells and cycle rotation.','9 walk heads rebuilt to match the same-direction idle; 19 total redrawn cells, 53 original pose cells and portrait preserved. All directions independently confirmed RIGHT-first in original order.')
t=t.replace('25 visually approved','23 visually approved')
out=p.with_name('approve_lantern_20260914.py');out.write_text(t,encoding='utf-8')

