#if UNITY_EDITOR
using System;
using System.IO;
using MmorpgClient.Game.Skills;
using MmorpgClient.UI.Ugui;
using MmorpgClient.UI.Ugui.Skills;
using TMPro;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

/// <summary>Explicit offline capture of production controls. No flag means no scene or rendering work.</summary>
[InitializeOnLoad]
public static class ClassSkillUiVerification
{
    private const string Output = "E:/work/image/designs/class-skills-20260928/qa";
    private const string Flag = Output + "/run-native-capture.flag";
    private static double _nextCheck;
    static ClassSkillUiVerification() { EditorApplication.update += CheckRequest; }

    private static void CheckRequest()
    {
        if (EditorApplication.timeSinceStartup < _nextCheck) return;
        _nextCheck = EditorApplication.timeSinceStartup + 1;
        if (!File.Exists(Flag) || EditorApplication.isCompiling || EditorApplication.isUpdating ||
            EditorApplication.isPlayingOrWillChangePlaymode) return;
        File.Delete(Flag);
        try { CaptureAll(); }
        catch (Exception error) { File.WriteAllText(Output + "/native-capture-error.txt", error.ToString()); Debug.LogException(error); }
    }

    [MenuItem("MMORPG/UI/Capture class skill windows")]
    public static void CaptureAll()
    {
        if (EditorApplication.isPlayingOrWillChangePlaymode) throw new InvalidOperationException("Skill capture requires Edit Mode; Play Mode was not changed.");
        Directory.CreateDirectory(Output);
        Capture(2560, 1080);
        Capture(1920, 1080);
        File.WriteAllText(Output + "/native-capture-complete.txt", DateTime.UtcNow.ToString("O") +
            "\nTwelve offline native UI captures, including the longest description and eight-row view. Fixture values are isolated from live network state.\n");
    }

    private static void Capture(int width, int height)
    {
        var previousScene = SceneManager.GetActiveScene();
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
        SceneManager.SetActiveScene(scene);
        var previousTarget = RenderTexture.active;
        RenderTexture target = null;
        Texture2D pixels = null;
        try
        {
            var camera = new GameObject("SkillCaptureCamera").AddComponent<Camera>();
            camera.enabled = false;
            camera.transform.position = new UnityEngine.Vector3(0, 0, -10);
            camera.orthographic = true;
            camera.nearClipPlane = .1f;
            camera.farClipPlane = 100f;
            camera.cullingMask = 1 << 31;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = QdaoUguiTheme.Letterbox;
            target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            target.Create(); camera.targetTexture = target;
            pixels = new Texture2D(width, height, TextureFormat.RGB24, false, false);
            var canvasObject = new GameObject("SkillCaptureCanvas", typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler));
            var canvas = canvasObject.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceCamera;
            canvas.worldCamera = camera; canvas.planeDistance = 2f;
            var scaler = canvasObject.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(2560, 1080);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.Expand;
            var root = QdaoUguiFactory.CreateCenteredRect("DesignRoot", canvasObject.transform, 2560, 1080);
            QdaoUguiFactory.CreateImage("Backdrop", root, 0, 0, 2560, 1080, QdaoRefreshArt.Load("sanctuary_background"));
            var owner = SkillUiRoot.Instance;
            if (owner == null)
            {
                owner = new GameObject("SkillQaOwner").AddComponent<SkillUiRoot>();
                owner.enabled = false;
            }
            var panel = new SkillPanel(owner, root);
            root.Find("CharacterSkillWindow").gameObject.SetActive(true);
            for (uint classId = 1; classId <= 4; classId++)
            {
                var snapshot = new SkillBookSnapshot { ClassId = classId, PlayerLevel = 68, CurrencyBalance = 265800 };
                foreach (var definition in SkillCatalog.ForClass(classId))
                    snapshot.Entries.Add(new SkillEntryState
                    {
                        Id = definition.skillId, Definition = definition, Rank = 3, RankLimit = 10,
                        NextRankCost = 1600 + definition.unlockLevel * 10,
                    });
                panel.Apply(snapshot);
                panel.SetStatus("离线布局验收 · 示例数值");
                foreach (var go in scene.GetRootGameObjects())
                    foreach (var transform in go.GetComponentsInChildren<UnityEngine.Transform>(true)) transform.gameObject.layer = 31;
                WriteCapture($"class-{classId}");
                if (classId == 3)
                {
                    root.Find("CharacterSkillWindow/SkillRow4Plate").GetComponent<Button>().onClick.Invoke();
                    WriteCapture("long-description-1305");
                    root.Find("CharacterSkillWindow/Filter0Plate").GetComponent<Button>().onClick.Invoke();
                    WriteCapture("eight-skills");
                    root.Find("CharacterSkillWindow/Filter1Plate").GetComponent<Button>().onClick.Invoke();
                }
            }

            void WriteCapture(string name)
            {
                Canvas.ForceUpdateCanvases();
                foreach (var label in root.GetComponentsInChildren<TMP_Text>(true)) label.ForceMeshUpdate(true, true);
                Canvas.ForceUpdateCanvases();
                camera.Render();
                RenderTexture.active = target;
                pixels.ReadPixels(new Rect(0, 0, width, height), 0, 0, false);
                pixels.Apply(false, false);
                File.WriteAllBytes($"{Output}/{name}-{width}x{height}.png", pixels.EncodeToPNG());
            }
        }
        finally
        {
            RenderTexture.active = previousTarget;
            if (pixels != null) UnityEngine.Object.DestroyImmediate(pixels);
            if (target != null) { target.Release(); UnityEngine.Object.DestroyImmediate(target); }
            if (previousScene.IsValid() && previousScene.isLoaded) SceneManager.SetActiveScene(previousScene);
            if (scene.IsValid() && scene.isLoaded) EditorSceneManager.CloseScene(scene, true);
        }
    }
}
#endif
