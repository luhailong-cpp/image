using UnityEngine;
internal class CommandScript : IRunCommand
{
    public void Execute(ExecutionResult result)
    {
        result.Log("BATTLE_CAPTURE_STATUS|RUNNING="+ClientBattleUiQaCapture.IsRunning+"|"+ClientBattleUiQaCapture.Status);
    }
}
