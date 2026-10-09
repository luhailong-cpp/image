from pathlib import Path
import ai_helper as h
D=Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
for n,f in {'deck-rail':'exec-230d5d86-c00f-47d9-ad95-2032a73e6a16.png','left-pile':'exec-743a2895-8397-49a5-8481-667369f2c5d7.png','right-pile':'exec-e9f2e1cf-219a-4a8f-a013-9191100165d5.png','sail-spar':'exec-e0841ecf-dc90-428a-9b62-9ebecd1830b1.png'}.items():print(h.ingest(n,D/f))
