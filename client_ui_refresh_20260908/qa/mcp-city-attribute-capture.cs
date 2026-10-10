using System;
using System.IO;
using System.Linq;
using System.Reflection;
using MmorpgClient.UI.Ugui;
using MmorpgClient.UI.Ugui.Attribute;
using MmorpgClient.UI.Ugui.Battle;
using MmorpgClient.World;
using MmorpgClient.World.Tianyong;
using TMPro;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
internal class CommandScript : IRunCommand
{
    const BindingFlags Private = BindingFlags.Instance | BindingFlags.NonPublic;
    static void Invoke(object target,string method) { target.GetType().GetMethod(method,Private)?.Invoke(target,null); }
    static T Field<T>(object target,string name) { return (T)target.GetType().GetField(name,Private).GetValue(target); }
    static void Add(object model,string name,object value) { var list=model.GetType().GetProperty(name).GetValue(model); list.GetType().GetMethod("Add",new[]{value.GetType()}).Invoke(list,new[]{value}); }
    public void Execute(ExecutionResult result)
    {
        if (EditorApplication.isPlayingOrWillChangePlaymode) throw new Exception("Expected Edit Mode");
        var previousScene = SceneManager.GetActiveScene();
        var scene = EditorSceneManager.OpenScene("Assets/Scenes/World/TianyongSandbox.unity",OpenSceneMode.Additive);
        SceneManager.SetActiveScene(scene);
        RenderTexture target = null;
        Texture2D texture = null;
        Camera camera = null;
        var previousRender = RenderTexture.active;
        RenderTexture previousTarget = null;
        try
        {
            var sandbox = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<TianyongSandboxBootstrap>(true)).Single();
            sandbox.BuildSandbox(); sandbox.SetHelpVisible(false);
            camera = sandbox.WorldCamera;
            previousTarget = camera.targetTexture;
            target = new RenderTexture(2560,1080,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.sRGB);
            camera.targetTexture = target;
            Invoke(sandbox,"LateUpdate");
            var animator = sandbox.Player.GetComponent<QdaoBoySpriteAnimator>();
            if (animator != null)
            {
                if (sandbox.Player.transform.Find("sprite") == null) Invoke(animator,"Awake");
                Invoke(animator,"LateUpdate");
            }
            foreach (var label in sandbox.Player.GetComponentsInChildren<WorldLabelBillboard>(true)) { Invoke(label,"Awake"); Invoke(label,"LateUpdate"); }
            var battleGo = new GameObject("[CityQaBattleUi]");
            var battle = battleGo.AddComponent<BattleUiRoot>();
            Invoke(battle,"BuildCanvas");
            Field<UiTextButton>(battle,"_entryButton").SetVisible(true);
            Field<UiTextButton>(battle,"_spectateEntryButton").SetVisible(true);
            var attributeGo = new GameObject("[CityQaAttributeUi]");
            var attribute = attributeGo.AddComponent<AttributeUiRoot>();
            Invoke(attribute,"BuildCanvas");
            Field<UiTextButton>(attribute,"_entryButton").SetVisible(true);
            foreach (var root in new[]{battleGo,attributeGo})
                foreach (var canvas in root.GetComponentsInChildren<Canvas>(true))
                { canvas.renderMode = RenderMode.ScreenSpaceCamera; canvas.worldCamera = camera; canvas.planeDistance = 1f; }
            texture = new Texture2D(2560,1080,TextureFormat.RGB24,false,false);
            void Shoot(string name)
            {
                Canvas.ForceUpdateCanvases();
                foreach (var root in scene.GetRootGameObjects()) foreach (var text in root.GetComponentsInChildren<TMP_Text>(true)) text.ForceMeshUpdate(true,true);
                Canvas.ForceUpdateCanvases(); camera.Render();
                RenderTexture.active = target; texture.ReadPixels(new Rect(0,0,2560,1080),0,0,false); texture.Apply(false,false);
                var path = "E:/work/image/client_ui_refresh_20260908/qa/" + name + ".png";
                File.WriteAllBytes(path,texture.EncodeToPNG()); result.Log("CAPTURE_OK|"+path);
            }
            Shoot("06-main-city-native");
            result.Log("CITY_OK|PLAYER=" + sandbox.Player.name + "|TILES=" + sandbox.Map.Root.GetComponentsInChildren<MeshRenderer>(true).Count(r=>r.name.StartsWith("Tile_")) + "|SPRITES=" + sandbox.Player.GetComponentsInChildren<SpriteRenderer>(true).Length + "|WALKABLE=" + TianyongPaintedCity.IsPaintingWalkable(sandbox.Player.transform.position));
            var panel = Field<AttributePanel>(attribute,"_panel");
            var data = new AttributePanelInfo { ActiveSchemeId=1,MaxSchemes=3,Level=75,CreateSchemeCostGold=100000 };
            Add(data,"Schemes",new AttributeSchemeInfo{SchemeId=1,Name="\u65b9\u6848\u4e00"});
            Add(data,"Schemes",new AttributeSchemeInfo{SchemeId=2,Name="\u5168\u7075\u65b9\u6848"});
            Add(data,"Pools",new AttributePoolInfo{PoolId=1,Name="\u5c5e\u6027\u70b9",Total=300,Remaining=10,Unlocked=true,DimensionCap=300});
            Add(data,"Pools",new AttributePoolInfo{PoolId=2,Name="\u76f8\u6027\u70b9",Total=40,Remaining=5,Unlocked=true,DimensionCap=30});
            Add(data,"Pools",new AttributePoolInfo{PoolId=3,Name="\u4ed9\u9b54\u70b9",Total=20,Remaining=4,Unlocked=true,DimensionCap=20});
            string[] names={"\u4f53\u8d28","\u7075\u529b","\u529b\u91cf","\u654f\u6377"};
            for(uint i=0;i<4;i++) Add(data,"Dimensions",new AttributeDimensionInfo{DimensionId=101+i,PoolId=1,Name=names[i],Desc="\u4fee\u884c\u5c5e\u6027\uff0c\u63d0\u9ad8\u89d2\u8272\u6218\u6597\u80fd\u529b\u3002",Allocated=60,Value=135,Cap=300,Sort=i});
            data.Derived = new DerivedAttributeInfo{Health=5800,MaxHealth=5800,Mana=2300,MaxMana=2300,PhysicalAttack=1380,MagicAttack=2180,Speed=860,Defense=960};
            panel.ApplyPanel(data); panel.Show();
            Shoot("07-attribute-native");
            for(uint i=4;i<8;i++) Add(data,"Dimensions",new AttributeDimensionInfo{DimensionId=101+i,PoolId=1,Name=new[]{"\u6839\u9aa8","\u609f\u6027","\u8eab\u6cd5","\u5b9a\u529b"}[i-4],Desc="\u6700\u5927\u516b\u884c\u5e03\u5c40\u9a8c\u6536\u3002",Allocated=10,Value=25,Cap=300,Sort=i});
            panel.ApplyPanel(data); Shoot("07b-attribute-eight-rows-native");
            result.Log("ATTRIBUTE_OK|ROWS=8|NETWORK=disconnected");
        }
        finally
        {
            RenderTexture.active=previousRender;
            if(camera!=null) camera.targetTexture=previousTarget;
            if(texture!=null) UnityEngine.Object.DestroyImmediate(texture);
            if(target!=null){target.Release();UnityEngine.Object.DestroyImmediate(target);}
            if(previousScene.IsValid()&&previousScene.isLoaded) SceneManager.SetActiveScene(previousScene);
            if(scene.IsValid()&&scene.isLoaded) EditorSceneManager.CloseScene(scene,true);
        }
    }
}
