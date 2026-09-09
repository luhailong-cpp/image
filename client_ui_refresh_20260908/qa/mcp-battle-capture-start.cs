using UnityEngine;
internal class CommandScript : IRunCommand
{
    public void Execute(ExecutionResult result)
    {
        ClientBattleUiQaCapture.StartCaptureAll();
        result.Log("BATTLE_CAPTURE_STARTED|"+ClientBattleUiQaCapture.Status);
    }
}
