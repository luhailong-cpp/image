using UnityEngine;
internal class CommandScript : IRunCommand
{
    public void Execute(ExecutionResult result)
    {
        ClientUiQaCapture.CaptureCityAttribute();
        result.Log("CITY_ATTRIBUTE_CAPTURE_COMPLETE");
    }
}
