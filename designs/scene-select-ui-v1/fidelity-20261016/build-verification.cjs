const fs=require('fs'),path=require('path'),crypto=require('crypto');
const scene=__dirname,world='E:/work/image/designs/world-map-original-20260925/fidelity-20261016',client='E:/work/mmorpg-client';
const geometry=`
    [Serializable] private sealed class GeometryReport
    {
        public string fixture="explicit offline editor fixture", coordinateSystem="2560x1080 DesignRoot, top-left origin", unityVersion;
        public bool captureOnly=true,liveServerVerified=false;
        public int width,height;public GeometryItem[] items;
    }
    [Serializable] private sealed class GeometryItem
    {
        public string name,kind,text,resourcePath,font;public Vector2 topLeft,size;public bool interactable,isTextTruncated;
    }
    private static void WriteGeometry(string file,int width,int height,RectTransform design)
    {
        var items=new List<GeometryItem>();
        foreach(var rect in design.GetComponentsInChildren<RectTransform>(false))
        {
            var label=rect.GetComponent<TMP_Text>();var image=rect.GetComponent<Image>();var button=rect.GetComponent<Button>();
            if(label==null&&image==null&&button==null)continue;
            var corners=new UnityEngine.Vector3[4];rect.GetWorldCorners(corners);
            var lo=design.InverseTransformPoint(corners[1]);var hi=design.InverseTransformPoint(corners[3]);
            items.Add(new GeometryItem{name=rect.name,kind=button!=null?"Button":label!=null?"TMP":"Image",
                text=label==null?"":label.text,font=label?.font==null?"":label.font.name,isTextTruncated=label!=null&&label.isTextTruncated,
                resourcePath=image?.sprite==null?"":AssetDatabase.GetAssetPath(image.sprite),interactable=button!=null&&button.IsInteractable(),
                topLeft=new Vector2(lo.x-design.rect.xMin,design.rect.yMax-lo.y),size=new Vector2(hi.x-lo.x,lo.y-hi.y)});
        }
        File.WriteAllText(file,JsonUtility.ToJson(new GeometryReport{width=width,height=height,unityVersion=Application.unityVersion,items=items.ToArray()},true));
    }
`;
for(const [root,oldName,newName,designName] of [
 [scene,'SceneChannelUiVerification','SceneChannelFidelityVerification','design'],
 [world,'CityTravelUiVerification','WorldMapFidelityVerification','root']
]){
 let code=fs.readFileSync(client+'/Assets/Editor/'+oldName+'.cs','utf8').replaceAll('\r\n','\n').replaceAll(oldName,newName);
 if(!code.includes('using System.Collections.Generic;'))code=code.replace('using System;','using System;\nusing System.Collections.Generic;');
 code=code.replace(/    public static string OutputDirectory \{ get; set; \} = Path.GetFullPath\(Path.Combine\(\n        Application.dataPath, "[^"\n]+"\)\);/,
  `    public static string OutputDirectory { get; set; } = "${root.replaceAll('\\','/')}/qa";`);
 code=code.replace('CaptureAll()','Capture()').replace('[MenuItem("MMORPG/UI/Capture scene channel screens (offline)")]','[MenuItem("MMORPG/UI/Scene Select/Capture fidelity")]')
  .replace('[MenuItem("MMORPG/UI/Capture city travel screens")]','[MenuItem("MMORPG/UI/World Map/Capture fidelity")]');
 code=code.replace('Capture(2560, 1080);','CaptureResolution(2560, 1080);').replace('Capture(1920, 1080);','CaptureResolution(1920, 1080);')
  .replace('public static void Capture(int width, int height)','private static void CaptureResolution(int width, int height)');
 code=code.replace('        if (EditorApplication.isPlayingOrWillChangePlaymode)','        if (EditorApplication.isPlayingOrWillChangePlaymode || EditorApplication.isCompiling || EditorApplication.isUpdating)');
 const a=code.indexOf('        // 批处理模式下新开的编辑器'),b=code.indexOf('        var scene =',a);
 if(a>=0)code=code.slice(0,a)+code.slice(b);
 code=code.replace('EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive)','EditorSceneManager.NewPreviewScene()')
  .replace('            SceneManager.SetActiveScene(scene);\n','')
  .replace(/(var camera = new GameObject\("[^"]+"\).AddComponent<Camera>\(\);)/,'$1\n            SceneManager.MoveGameObjectToScene(camera.gameObject,scene);camera.scene=scene;')
  .replace('            var canvas = canvasObject.GetComponent<Canvas>();','            SceneManager.MoveGameObjectToScene(canvasObject,scene);\n            var canvas = canvasObject.GetComponent<Canvas>();')
  .replace('            if (previousScene.IsValid() && previousScene.isLoaded) SceneManager.SetActiveScene(previousScene);\n','')
  .replace('            if (scene.IsValid() && scene.isLoaded) EditorSceneManager.CloseScene(scene, true);','            if (scene.IsValid()) EditorSceneManager.ClosePreviewScene(scene);\n            if(SceneManager.GetActiveScene()!=previousScene)throw new InvalidOperationException("Active scene changed during fidelity capture.");');
 code=code.replace('                File.WriteAllBytes(Path.Combine(OutputDirectory, name + "_" + width + "x" + height + ".png"), pixels.EncodeToPNG());',
  `                File.WriteAllBytes(Path.Combine(OutputDirectory, name + "_" + width + "x" + height + ".png"), pixels.EncodeToPNG());\n                WriteGeometry(Path.Combine(OutputDirectory,name+"_"+width+"x"+height+".geometry.json"),width,height,${designName});`);
 if(root===scene){code=code.replaceAll('Lines(16,','Lines(24,').replaceAll('Lines(20,','Lines(28,').replace('LineButtonPrefix + 20','LineButtonPrefix + 28');}
 code=code.replace(/\n}\n#endif\s*$/,'\n'+geometry+'}\n#endif\n');
 fs.writeFileSync(path.join(root,'integration',newName+'.cs'),code);
 const meta=path.join(root,'integration',newName+'.cs.meta');if(!fs.existsSync(meta))fs.writeFileSync(meta,'fileFormatVersion: 2\nguid: '+crypto.randomBytes(16).toString('hex')+'\n');
}
let compile=fs.readFileSync('E:/work/image/designs/team-ui-v2/fidelity-20261016/compile-staged.ps1','utf8');
compile=compile.replace("if($_.FullName.Replace('\\','/') -match '/UI/Ugui/Team/(TeamWindow|TeamUiArt)\\.cs$'){'\"'+(Join-Path $package ('integration/'+$_.Name))+'\"'}else{'\"'+$_.FullName+'\"'}",
`if($_.Name -eq 'SceneChannelWindow.cs'){'"'+(Join-Path $package 'integration/SceneChannelWindow.cs')+'"'}elseif($_.Name -eq 'CityTravelWindow.cs'){'"E:/work/image/designs/world-map-original-20260925/fidelity-20261016/integration/CityTravelWindow.cs"'}else{'"'+$_.FullName+'"'}`)
 .replaceAll('TeamFidelity.Runtime','SceneTravelFidelity.Runtime').replaceAll('TeamFidelity.Editor','SceneTravelFidelity.Editor')
 .replace("('"+'"'+"'+(Join-Path $package 'integration/TeamFidelityVerification.cs')+'"+'"'+"')",
  "('"+'"'+"'+(Join-Path $package 'integration/SceneChannelFidelityVerification.cs')+'"+'"'+"')+('\"E:/work/image/designs/world-map-original-20260925/fidelity-20261016/integration/WorldMapFidelityVerification.cs\"')");
fs.writeFileSync(path.join(scene,'compile-staged.ps1'),compile);
console.log('Capture utilities and combined compile script staged.');
