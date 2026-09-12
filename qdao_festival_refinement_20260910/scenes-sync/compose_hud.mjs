// Existing v10 HUD compositing recipe, isolated from frozen contracts and server screens.
import { createRequire } from 'node:module';
const require=createRequire(import.meta.url);
const [sharpPath,background,overlay,output]=process.argv.slice(2);
const sharp=require(sharpPath);
const [b,o]=await Promise.all([sharp(background).metadata(),sharp(overlay).metadata()]);
if(b.width!==2560||b.height!==1080||o.width!==2560||o.height!==1080||!o.hasAlpha) throw Error('HUD input contract');
await sharp(background).composite([{input:overlay,left:0,top:0}]).removeAlpha().png({compressionLevel:9}).toFile(output);
