using System;
using System.IO;
using System.Linq;
using MmorpgClient.UI.EditorTools;
using MmorpgClient.UI.Ugui;
using TMPro;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

internal class CommandScript : IRunCommand
{
    public void Execute(ExecutionResult result)
    {
        if (EditorApplication.isPlayingOrWillChangePlaymode) throw new InvalidOperationException("Expected Edit Mode");
        QdaoUguiBuilder.BuildAll();
        var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Resources/UI/Ugui/Prefabs/QdaoServerSelect.prefab");
        result.Log("BUILD_OK|Images=" + prefab.GetComponentsInChildren<UnityEngine.UI.Image>(true).Length + "|Buttons=" + prefab.GetComponentsInChildren<Button>(true).Length + "|TMP=" + prefab.GetComponentsInChildren<TMP_Text>(true).Length);
        GameObject cameraGo = null;
        GameObject canvasGo = null;
        RenderTexture target = null;
        Texture2D texture = null;
        var previous = RenderTexture.active;
        try
        {
            cameraGo = new GameObject("[RefreshQaCamera]", typeof(Camera));
            var camera = cameraGo.GetComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.black;
            camera.orthographic = true;
            camera.nearClipPlane = .1f;
            camera.farClipPlane = 100f;
            camera.cullingMask = 1 << 5;
            camera.transform.position = new UnityEngine.Vector3(0, 0, -10);
            target = new RenderTexture(2560,1080,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.sRGB);
            camera.targetTexture = target;
            canvasGo = new GameObject("[RefreshQaCanvas]",typeof(RectTransform),typeof(Canvas),typeof(CanvasScaler),typeof(GraphicRaycaster));
            var canvas = canvasGo.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceCamera;
            canvas.worldCamera = camera;
            canvas.planeDistance = 1;
            canvas.pixelPerfect = true;
            var scaler = canvasGo.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new UnityEngine.Vector2(2560,1080);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.Expand;
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab,canvasGo.transform);
            var view = instance.GetComponent<QdaoServerSelectView>();
            view.PrepareForPreview();
            foreach (var t in canvasGo.GetComponentsInChildren<UnityEngine.Transform>(true)) t.gameObject.layer = 5;
            texture = new Texture2D(2560,1080,TextureFormat.RGB24,false,false);
            void Shoot(string name)
            {
                Canvas.ForceUpdateCanvases();
                foreach (var text in instance.GetComponentsInChildren<TMP_Text>(true)) text.ForceMeshUpdate(true,true);
                Canvas.ForceUpdateCanvases();
                camera.Render();
                RenderTexture.active = target;
                texture.ReadPixels(new Rect(0,0,2560,1080),0,0,false);
                texture.Apply(false,false);
                string path = "E:/work/image/client_ui_refresh_20260908/qa/" + name + ".png";
                File.WriteAllBytes(path,texture.EncodeToPNG());
                result.Log("CAPTURE_OK|" + path);
            }
            view.ShowLanding(true); Shoot("01-login-native");
            view.ShowLanding(false); Shoot("02-server-native");
            view.ShowCredentialForPreview(); Shoot("03-account-native");
        }
        finally
        {
            RenderTexture.active = previous;
            if (cameraGo != null) cameraGo.GetComponent<Camera>().targetTexture = null;
            if (texture != null) UnityEngine.Object.DestroyImmediate(texture);
            if (target != null) { target.Release(); UnityEngine.Object.DestroyImmediate(target); }
            if (canvasGo != null) UnityEngine.Object.DestroyImmediate(canvasGo);
            if (cameraGo != null) UnityEngine.Object.DestroyImmediate(cameraGo);
        }
    }
}
