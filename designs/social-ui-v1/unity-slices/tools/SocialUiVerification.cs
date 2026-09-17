#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using MmorpgClient.Game.Social;
using MmorpgClient.UI.Ugui;
using MmorpgClient.UI.Ugui.Social;
using TMPro;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

/// <summary>Captures and exercises the native social window in a temporary offline scene.</summary>
public static class SocialUiVerification
{
    public static string OutputDirectory = Path.GetFullPath(Path.Combine(Application.dataPath, "../../image/designs/social-ui-v1/unity-slices/qa"));
    [Serializable] private sealed class Report
    {
        public string status = "passed", unityVersion, completedAtUtc;
        public bool liveServerVerified = false;
        public string[] screenshots, checks;
    }
    private static readonly List<string> Shots = new();
    private static readonly List<string> Checks = new();

    [MenuItem("MMORPG/UI/Social/Capture and verify native windows")]
    public static void CaptureAll()
    {
        if (EditorApplication.isPlayingOrWillChangePlaymode || EditorApplication.isCompiling)
            throw new InvalidOperationException("Stable Edit mode is required.");
        Directory.CreateDirectory(OutputDirectory);
        Shots.Clear(); Checks.Clear();
        Capture(2560, 1080);
        Capture(1920, 1080);
        File.WriteAllText(Path.Combine(OutputDirectory, "native-capture.json"), JsonUtility.ToJson(
            new Report { unityVersion = Application.unityVersion, completedAtUtc = DateTime.UtcNow.ToString("O"),
                screenshots = Shots.ToArray(), checks = Checks.ToArray() }, true));
        Debug.Log("SOCIAL_NATIVE_CAPTURE_OK|screenshots=" + Shots.Count + "|checks=" + Checks.Count);
    }

    private static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException("Social native QA: " + message);
        Checks.Add(message);
    }

    private static void Capture(int width, int height)
    {
        var previous = SceneManager.GetActiveScene();
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
        var previousTarget = RenderTexture.active;
        RenderTexture target = null;
        Texture2D pixels = null;
        SocialWindow window = null;
        try
        {
            SceneManager.SetActiveScene(scene);
            var camera = new GameObject("SocialCaptureCamera").AddComponent<Camera>();
            camera.enabled = false;
            camera.transform.position = new UnityEngine.Vector3(0, 0, -10);
            camera.orthographic = true;
            camera.nearClipPlane = .1f; camera.farClipPlane = 100;
            camera.cullingMask = 1 << 31;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = QdaoUguiTheme.Letterbox;
            target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            target.Create(); camera.targetTexture = target;
            pixels = new Texture2D(width, height, TextureFormat.RGB24, false, false);
            var canvasObject = new GameObject("SocialCaptureCanvas", typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            var canvas = canvasObject.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceCamera; canvas.worldCamera = camera; canvas.planeDistance = 2;
            var scaler = canvasObject.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(2560, 1080);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.Expand;
            var design = QdaoUguiFactory.CreateCenteredRect("SocialCaptureDesign", canvasObject.transform, 2560, 1080);
            QdaoUguiFactory.CreateImage("Backdrop", design, 0, 0, 2560, 1080, QdaoUguiTheme.RequireSprite("UI/Ugui/SocialV1/main-city"));
            var state = new SocialState(preview: true);
            window = new SocialWindow(design, state);
            QdaoUguiFactory.CreateText("OfflineFixtureBadge", design, 300, 1035, 1960, 42,
                "离线界面验收 · 示例角色与消息", 24, QdaoUguiTheme.Cream, TextAlignmentOptions.Center);

            void Shoot(string name)
            {
                foreach (var root in scene.GetRootGameObjects())
                    foreach (var child in root.GetComponentsInChildren<UnityEngine.Transform>(true)) child.gameObject.layer = 31;
                Canvas.ForceUpdateCanvases();
                foreach (var text in canvasObject.GetComponentsInChildren<TMP_Text>(true)) text.ForceMeshUpdate(true, true);
                Canvas.ForceUpdateCanvases();
                camera.Render(); RenderTexture.active = target;
                pixels.ReadPixels(new Rect(0, 0, width, height), 0, 0, false); pixels.Apply(false, false);
                string filename = name + "_" + width + "x" + height + ".png";
                File.WriteAllBytes(Path.Combine(OutputDirectory, filename), pixels.EncodeToPNG());
                Shots.Add(filename);
                Require(window.IsVisible, width + ": window visible for " + name);
            }

            window.Show(SocialPage.Groups); Shoot("01-groups");
            window.Show(SocialPage.World); Shoot("02-world");
            window.Show(SocialPage.Rumor); Shoot("03-rumor");
            Require(!canvasObject.GetComponentsInChildren<TMP_InputField>().Any(input => input.name.IndexOf("Composer", StringComparison.OrdinalIgnoreCase) >= 0),
                width + ": rumor has no active message composer");
            window.Hide();
            Require(!window.IsVisible, width + ": window closes");
        }
        finally
        {
            window?.Dispose();
            RenderTexture.active = previousTarget;
            if (pixels != null) UnityEngine.Object.DestroyImmediate(pixels);
            if (target != null) { target.Release(); UnityEngine.Object.DestroyImmediate(target); }
            if (previous.IsValid() && previous.isLoaded) SceneManager.SetActiveScene(previous);
            EditorSceneManager.CloseScene(scene, true);
        }
    }

    [MenuItem("MMORPG/UI/Social/Build offline preview scene and prefab")]
    public static void BuildPreviewAssets()
    {
        if (EditorApplication.isPlayingOrWillChangePlaymode || EditorApplication.isCompiling)
            throw new InvalidOperationException("Stable Edit mode is required.");
        const string scenePath = "Assets/Scenes/SocialPreview.unity";
        const string prefabPath = "Assets/Prefabs/UI/SocialOfflinePreview.prefab";
        Directory.CreateDirectory(Path.GetDirectoryName(scenePath));
        Directory.CreateDirectory(Path.GetDirectoryName(prefabPath));
        var previous = SceneManager.GetActiveScene();
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
        try
        {
            SceneManager.SetActiveScene(scene);
            var host = new GameObject("Social Offline Preview", typeof(SocialPreviewHost));
            PrefabUtility.SaveAsPrefabAsset(host, prefabPath);
            if (!EditorSceneManager.SaveScene(scene, scenePath)) throw new IOException("Could not save social preview scene.");
        }
        finally
        {
            if (previous.IsValid() && previous.isLoaded) SceneManager.SetActiveScene(previous);
            EditorSceneManager.CloseScene(scene, true);
        }
        AssetDatabase.ImportAsset(scenePath, ImportAssetOptions.ForceSynchronousImport);
        AssetDatabase.ImportAsset(prefabPath, ImportAssetOptions.ForceSynchronousImport);
        Debug.Log("SOCIAL_PREVIEW_ASSETS_OK|" + scenePath);
    }
}
#endif
