using UnityEditor;
internal class CommandScript : IRunCommand
{
    public void Execute(ExecutionResult result)
    {
        result.Log("PREVIEW_TRANSITION|WAS_PLAYING="+EditorApplication.isPlaying);
        EditorApplication.isPlaying=false;
    }
}
