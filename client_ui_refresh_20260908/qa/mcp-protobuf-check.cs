using UnityEngine;
using Google.Protobuf;
using Google.Protobuf.Collections;
internal class CommandScript : IRunCommand
{
    public void Execute(ExecutionResult result)
    {
        var data=new AttributePanelInfo();
        data.Schemes.Add(new AttributeSchemeInfo{SchemeId=1,Name="Preview"});
        result.Log("PROTOBUF_OK|" + data.Schemes.Count);
    }
}
