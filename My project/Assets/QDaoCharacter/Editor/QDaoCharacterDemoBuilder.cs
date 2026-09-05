using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace QDaoCharacter.Editor
{
    internal sealed class QDaoCharacterSpriteImporter : AssetPostprocessor
    {
        internal const string SpriteAssetFolder = "Assets/Resources/QDaoCharacter/Walk";
        private const string SpriteAssetPrefix = SpriteAssetFolder + "/";

        private void OnPreprocessTexture()
        {
            string normalizedPath = assetPath.Replace('\\', '/');
            if (!normalizedPath.StartsWith(SpriteAssetPrefix, StringComparison.OrdinalIgnoreCase))
            {
                return;
            }

            Configure((TextureImporter)assetImporter);
        }

        internal static void Configure(TextureImporter importer)
        {
            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Single;
            importer.spritePixelsPerUnit = 400f;

            TextureImporterSettings spriteSettings = new TextureImporterSettings();
            importer.ReadTextureSettings(spriteSettings);
            spriteSettings.spriteAlignment = (int)SpriteAlignment.Custom;
            spriteSettings.spritePivot = new Vector2(0.5f, 0.04f);
            importer.SetTextureSettings(spriteSettings);

            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            importer.alphaIsTransparency = true;
            importer.sRGBTexture = true;
            importer.mipmapEnabled = false;
            importer.isReadable = false;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.filterMode = FilterMode.Bilinear;
            importer.maxTextureSize = 2048;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.crunchedCompression = false;
            importer.compressionQuality = 100;
        }
    }

    public static class QDaoCharacterDemoBuilder
    {
        public const string DemoScenePath = "Assets/Scenes/QDaoCharacterWalkDemo.unity";

        private static readonly string[] Directions =
        {
            "east",
            "northeast",
            "north",
            "northwest",
            "west",
            "southwest",
            "south",
            "southeast"
        };

        [MenuItem("Tools/QDao Character/Build Walk Demo Scene", priority = 1)]
        public static void BuildDemoScene()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            ConfigureAndImportSprites();

            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject root = new GameObject("QDao Character Walk Demo (Code Generated)");
            root.AddComponent<QDaoWalkDemoBootstrap>();

            if (!EditorSceneManager.SaveScene(scene, DemoScenePath))
            {
                throw new InvalidOperationException("Could not save demo scene at " + DemoScenePath);
            }

            SetDemoAsFirstBuildScene();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);

            SceneAsset sceneAsset = AssetDatabase.LoadAssetAtPath<SceneAsset>(DemoScenePath);
            EditorSceneManager.playModeStartScene = sceneAsset;
            Selection.activeObject = root;
            Debug.Log("[QDaoCharacter] Built code-driven walk demo scene: " + DemoScenePath);
        }

        [MenuItem("Tools/QDao Character/Validate Walk Demo", priority = 2)]
        public static void ValidateDemo()
        {
            List<string> errors = new List<string>();
            ValidateSpriteAssets(errors);
            ValidateScene(errors);
            ValidateBuildSettings(errors);

            if (errors.Count > 0)
            {
                throw new InvalidOperationException(
                    "[QDaoCharacter] Validation failed:\n - " + string.Join("\n - ", errors));
            }

            Debug.Log(
                "[QDaoCharacter] VALIDATION PASSED: 32 lossless 1254×1254 sprites, " +
                "8 directions × 4 frames, demo scene and build settings are ready.");
        }

        public static void BuildAndValidateFromCommandLine()
        {
            BuildDemoScene();
            ValidateDemo();
        }

        private static void ConfigureAndImportSprites()
        {
            string[] textureGuids = AssetDatabase.FindAssets(
                "t:Texture2D",
                new[] { QDaoCharacterSpriteImporter.SpriteAssetFolder });

            foreach (string guid in textureGuids)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
                if (importer == null)
                {
                    continue;
                }

                QDaoCharacterSpriteImporter.Configure(importer);
                importer.SaveAndReimport();
            }
        }

        private static void ValidateSpriteAssets(ICollection<string> errors)
        {
            string[] textureGuids = AssetDatabase.FindAssets(
                "t:Texture2D",
                new[] { QDaoCharacterSpriteImporter.SpriteAssetFolder });

            string[] paths = textureGuids
                .Select(AssetDatabase.GUIDToAssetPath)
                .Where(path => path.EndsWith(".png", StringComparison.OrdinalIgnoreCase))
                .OrderBy(path => path, StringComparer.Ordinal)
                .ToArray();

            if (paths.Length != 32)
            {
                errors.Add("Expected 32 PNG frames, found " + paths.Length + ".");
            }

            foreach (string direction in Directions)
            {
                int count = paths.Count(path =>
                    System.IO.Path.GetFileNameWithoutExtension(path)
                        .StartsWith(direction + "_frame_", StringComparison.OrdinalIgnoreCase));
                if (count != 4)
                {
                    errors.Add("Expected 4 " + direction + " frames, found " + count + ".");
                }
            }

            foreach (string path in paths)
            {
                Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
                Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(path);
                TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;

                if (texture == null || texture.width != 1254 || texture.height != 1254)
                {
                    errors.Add(path + " is not imported at the original 1254×1254 resolution.");
                }

                if (sprite == null)
                {
                    errors.Add(path + " is not imported as a Sprite.");
                }

                if (importer == null || importer.textureCompression != TextureImporterCompression.Uncompressed)
                {
                    errors.Add(path + " is not using lossless/uncompressed import settings.");
                }

                if (importer != null && importer.mipmapEnabled)
                {
                    errors.Add(path + " has mipmaps enabled.");
                }
            }
        }

        private static void ValidateScene(ICollection<string> errors)
        {
            SceneAsset sceneAsset = AssetDatabase.LoadAssetAtPath<SceneAsset>(DemoScenePath);
            if (sceneAsset == null)
            {
                errors.Add("Demo scene is missing: " + DemoScenePath);
                return;
            }

            Scene scene = EditorSceneManager.OpenScene(DemoScenePath, OpenSceneMode.Single);
            bool hasBootstrap = scene.GetRootGameObjects()
                .Any(root => root.GetComponent<QDaoWalkDemoBootstrap>() != null);
            if (!hasBootstrap)
            {
                errors.Add("Demo scene does not contain QDaoWalkDemoBootstrap.");
            }
        }

        private static void ValidateBuildSettings(ICollection<string> errors)
        {
            EditorBuildSettingsScene[] scenes = EditorBuildSettings.scenes;
            if (scenes.Length == 0 || !scenes[0].enabled || scenes[0].path != DemoScenePath)
            {
                errors.Add("Demo scene is not the first enabled scene in Build Settings.");
            }
        }

        private static void SetDemoAsFirstBuildScene()
        {
            List<EditorBuildSettingsScene> scenes = EditorBuildSettings.scenes
                .Where(scene => scene.path != DemoScenePath)
                .ToList();
            scenes.Insert(0, new EditorBuildSettingsScene(DemoScenePath, true));
            EditorBuildSettings.scenes = scenes.ToArray();
        }
    }
}
