using System;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

internal class CommandScript : IRunCommand
{
    public void Execute(ExecutionResult result)
    {
        result.Log("MCP_BASELINE|UNITY=" + Application.unityVersion + "|PLAYING=" + EditorApplication.isPlaying + "|COMPILING=" + EditorApplication.isCompiling + "|UPDATING=" + EditorApplication.isUpdating);
        for (int i = 0; i < SceneManager.sceneCount; i++)
        {
            var s = SceneManager.GetSceneAt(i);
            result.Log("SCENE|" + s.path + "|ROOTS=" + s.rootCount + "|DIRTY=" + s.isDirty);
        }
        result.Log("CAMERAS|" + string.Join(";", UnityEngine.Object.FindObjectsByType<Camera>(FindObjectsInactive.Include, FindObjectsSortMode.None).Select(c => c.name + ":" + c.enabled)));
        result.Log("CANVASES|" + string.Join(";", UnityEngine.Object.FindObjectsByType<Canvas>(FindObjectsInactive.Include, FindObjectsSortMode.None).Select(c => c.name + ":" + c.renderMode)));
        var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Resources/UI/Ugui/Prefabs/QdaoServerSelect.prefab");
        if (prefab != null)
            result.Log("SERVER_PREFAB|IMAGES=" + prefab.GetComponentsInChildren<UnityEngine.UI.Image>(true).Length + "|BUTTONS=" + prefab.GetComponentsInChildren<Button>(true).Length + "|ROOT=" + prefab.name);
    }
}
