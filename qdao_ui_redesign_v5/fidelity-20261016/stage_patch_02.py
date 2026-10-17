from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
CLIENT=Path('E:/work/mmorpg-client')
PATCH=ROOT/'patch-02'
rel='Assets/Scripts/UI/Ugui/QdaoCoreFidelityArt.cs'
src=CLIENT/rel
old=src.read_text(encoding='utf-8-sig')
needle='                text.outlineColor = QdaoUguiTheme.Html("#28412B"); text.outlineWidth = .10f;'
assert old.count(needle)==1
new=old.replace(needle,'                ApplyGoldOutline(text);',1)
needle='        public static Sprite LoadCharacterPortrait(string id)'
method='''        private static void ApplyGoldOutline(TMP_Text text)
        {
            // Inactive freshly baked labels may not have TMP's m_sharedMaterial yet.
            // Begin from the font asset's valid material instead of outline setters,
            // which clone m_sharedMaterial without checking that it exists.
            var source = text.font != null ? text.font.material : null;
            if (source == null) return;
            const string resource = "UI/Ugui/CoreFidelity20261016/CoreGoldText";
            Material outline = Resources.Load<Material>(resource);
#if UNITY_EDITOR
            if (!Application.isPlaying)
            {
                const string path = "Assets/Resources/" + resource + ".mat";
                outline = UnityEditor.AssetDatabase.LoadAssetAtPath<Material>(path);
                if (outline == null)
                {
                    outline = new Material(source) { name = "CoreGoldText" };
                    outline.EnableKeyword("OUTLINE_ON");
                    outline.SetFloat("_OutlineWidth", .10f);
                    outline.SetColor("_OutlineColor", QdaoUguiTheme.Html("#28412B"));
                    UnityEditor.AssetDatabase.CreateAsset(outline, path);
                }
                // A persistent dedicated preset survives SaveAsPrefabAsset + reload.
                // Never serialize a temporary material or edit the font's own material.
                text.fontSharedMaterial = outline;
                return;
            }
#endif
            if (outline != null)
            {
                text.fontSharedMaterial = outline;
                return;
            }
            text.fontSharedMaterial = source;
            var instance = text.fontMaterial; // TMP owns and disposes this runtime clone.
            if (instance == null) return;
            instance.EnableKeyword("OUTLINE_ON");
            instance.SetFloat("_OutlineWidth", .10f);
            instance.SetColor("_OutlineColor", QdaoUguiTheme.Html("#28412B"));
            text.UpdateMeshPadding();
        }

'''
assert new.count(needle)==1;new=new.replace(needle,method+needle,1)
dest=PATCH/'client'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(new,encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'destinationRoot':str(CLIENT),'files':[{'source':'client/'+rel,'target':rel,'sha256':sha(dest)}],'guards':[{'target':rel,'sha256Before':sha(src)}],'scope':'One helper fix: valid source material, OUTLINE_ON, dedicated persistent preset for prefab authoring and TMP-owned runtime instance fallback; shared font material remains untouched.','afterInstall':'BuildAll creates persistent Assets/Resources/UI/Ugui/CoreFidelity20261016/CoreGoldText.mat once. Rebuild and reload production prefab before capture.','generatedOnBuild':['Assets/Resources/UI/Ugui/CoreFidelity20261016/CoreGoldText.mat','Assets/Resources/UI/Ugui/CoreFidelity20261016/CoreGoldText.mat.meta'],'newImages':False,'businessTransactionsModified':False}
(PATCH/'install-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
compile=(ROOT/'compile-staged-core.ps1').read_text(encoding='utf-8-sig').replace('[string]$Phase="login-server"','[string]$Phase="patch-02"')
(PATCH/'compile-staged.ps1').write_text(compile,encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False))
