from pathlib import Path
root=Path(__file__).resolve().parents[2]
hook="""// Windows viewers can briefly hold a generated asset while it is refreshed.
const rawWriteFile = fs.writeFile.bind(fs);
fs.writeFile = async (...params) => {
  for (let attempt=0;;attempt++) {
    try { return await rawWriteFile(...params); }
    catch (error) {
      if (attempt>=12 || !['UNKNOWN','EBUSY','EPERM'].includes(error.code)) throw error;
      await new Promise(resolve=>setTimeout(resolve,250));
    }
  }
};
"""
for rel in ['qdao_ui_redesign_v5/components/build.mjs','exact_qdao_slices/build_native_q5.mjs','qdao_ui_redesign_v5/hud/build.mjs']:
    p=root/rel;s=p.read_text('utf8')
    if 'const rawWriteFile' not in s:s=s.replace("import fs from 'node:fs/promises';","import fs from 'node:fs/promises';\n"+hook,1)
    for expr,target in [
        ("sharp(Buffer.from(source)).png({ compressionLevel: 9 })", "path.join(root, a.png)"),
        ("sharp(Buffer.from(overview)).png({ compressionLevel: 9 })", "path.join(root, 'overview.png')"),
        ("sharp(Buffer.from(badgeOverview)).png({ compressionLevel: 9 })", "path.join(root, 'badges_overview.png')"),
        ("sharp(Buffer.from(source)).png({compressionLevel:9})", "dest"),
        ("sharp(Buffer.from(source)).png({ compressionLevel: 9 })", "path.join(root, `${name}.png`)"),
        ("sharp(background).composite([{ input: overlay, left: 0, top: 0 }]).removeAlpha().png({ compressionLevel: 9 })", "fullPath")
    ]:s=s.replace(f'await {expr}.toFile({target})',f'await fs.writeFile({target}, await {expr}.toBuffer())')
    p.write_text(s,'utf8')
print('Finite retry added for transient Windows generated-file handles.')
