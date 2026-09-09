using System;
using System.Linq;
using MmorpgClient.UI.Ugui;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
internal class CommandScript : IRunCommand
{
    void Check(bool passed,string label,ExecutionResult result) { if(!passed) throw new Exception("ASSERT_FAILED|"+label); result.Log("ASSERT_PASS|"+label); }
    public void Execute(ExecutionResult result)
    {
        var prefab=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Resources/UI/Ugui/Prefabs/QdaoServerSelect.prefab");
        var instance=UnityEngine.Object.Instantiate(prefab);
        try
        {
            var view=instance.GetComponent<QdaoServerSelectView>();
            view.Initialize(null); view.PrepareForPreview();
            var buttons=instance.GetComponentsInChildren<Button>(true);
            Button Button(string name) => buttons.Single(b=>b.name==name);
            var modal=instance.GetComponentsInChildren<UnityEngine.Transform>(true).Single(t=>t.name=="CredentialPanel").gameObject;
            Check(Button("EnterButton").interactable,"open_server_enterable",result);
            Button("ServerCardArt_5").onClick.Invoke();
            Check(!Button("EnterButton").interactable&&!Button("EnterGame").interactable,"maintenance_both_entries_disabled",result);
            Button("EnterButton").onClick.Invoke();
            Check(!modal.activeSelf,"maintenance_event_does_not_open_account",result);
            view.PrepareForPreview();
            var search=instance.GetComponentsInChildren<TMP_InputField>(true).Single(i=>i.name=="SearchInput");
            search.text="qa_nonexistent_3849";
            Check(!Button("EnterButton").interactable,"no_search_results_cannot_enter_stale_server",result);
            Button("EnterButton").onClick.Invoke();
            Check(!modal.activeSelf,"empty_selection_event_does_not_open_account",result);
            view.PrepareForPreview();
            var serialized=new SerializedObject(view);
            var landingServers=serialized.FindProperty("_landingServers");
            Check(landingServers!=null,"landing_reference_is_serialized",result);
            landingServers.objectReferenceValue=null; serialized.ApplyModifiedPropertiesWithoutUndo();
            bool rejected=false;
            try{view.PrepareForPreview();}catch(MissingReferenceException){rejected=true;}
            Check(rejected,"missing_landing_reference_rejected",result);
        }
        finally{UnityEngine.Object.DestroyImmediate(instance);}
    }
}
