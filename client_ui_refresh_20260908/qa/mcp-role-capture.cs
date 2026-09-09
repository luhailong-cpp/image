using System;
using System.IO;
using MmorpgClient.UI.Ugui.Role;
using TMPro;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;
internal class CommandScript : IRunCommand
{
    public void Execute(ExecutionResult result)
    {
        if (EditorApplication.isPlayingOrWillChangePlaymode) throw new InvalidOperationException("Expected Edit Mode");
        GameObject cameraGo = null;
        RenderTexture target = null;
        Texture2D texture = null;
        var previous = RenderTexture.active;
        try
        {
            cameraGo = new GameObject("[RoleQaCamera]",typeof(Camera));
            var camera = cameraGo.GetComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.black;
            camera.orthographic = true;
            camera.nearClipPlane = .1f;
            camera.farClipPlane = 100f;
            camera.cullingMask = 1 << 5;
            camera.transform.position = new UnityEngine.Vector3(0,0,-10);
            target = new RenderTexture(2560,1080,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.sRGB);
            camera.targetTexture = target;
            texture = new Texture2D(2560,1080,TextureFormat.RGB24,false,false);
            for (int mode = 0; mode < 2; mode++)
            {
                RoleFlowUi.ShowEditorPreview(mode == 1);
                var previewRoot = GameObject.Find("[RoleUiEditorPreview]");
                if (previewRoot == null) throw new Exception("Role preview root missing");
                var canvas = previewRoot.GetComponentInChildren<Canvas>(true);
                canvas.renderMode = RenderMode.ScreenSpaceCamera;
                canvas.worldCamera = camera;
                canvas.planeDistance = 1;
                foreach (var t in previewRoot.GetComponentsInChildren<UnityEngine.Transform>(true)) t.gameObject.layer = 5;
                Canvas.ForceUpdateCanvases();
                foreach (var text in previewRoot.GetComponentsInChildren<TMP_Text>(true)) text.ForceMeshUpdate(true,true);
                Canvas.ForceUpdateCanvases();
                camera.Render();
                RenderTexture.active = target;
                texture.ReadPixels(new Rect(0,0,2560,1080),0,0,false); texture.Apply(false,false);
                var path = "E:/work/image/client_ui_refresh_20260908/qa/" + (mode == 0 ? "04-role-select-native.png" : "05-role-create-native.png");
                File.WriteAllBytes(path,texture.EncodeToPNG());
                result.Log("CAPTURE_OK|" + path + "|IMAGES=" + previewRoot.GetComponentsInChildren<UnityEngine.UI.Image>(true).Length + "|BUTTONS=" + previewRoot.GetComponentsInChildren<Button>(true).Length);
                RoleFlowUi.HideEditorPreview();
            }
        }
        finally
        {
            RoleFlowUi.HideEditorPreview();
            RenderTexture.active = previous;
            if (cameraGo != null) cameraGo.GetComponent<Camera>().targetTexture = null;
            if (texture != null) UnityEngine.Object.DestroyImmediate(texture);
            if (target != null) { target.Release(); UnityEngine.Object.DestroyImmediate(target); }
            if (cameraGo != null) UnityEngine.Object.DestroyImmediate(cameraGo);
        }
    }
}
