using MmorpgClient.Game.Skills;
using MmorpgClient.UI.Ugui.Battle;
using UnityEngine;
using UnityEngine.UI;

namespace MmorpgClient.UI.Ugui.Skills
{
    public sealed class SkillUiRoot : MonoBehaviour
    {
        public static SkillUiRoot Instance { get; private set; }
        public SkillClient Client { get; private set; }
        private SkillPanel _panel;
        private AppBootstrap _app;
        public bool IsVisible => _panel?.IsVisible == true;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void AutoSpawn() => EnsureSpawned();

        public static void EnsureSpawned()
        {
            if (Instance != null) return;
            var go = new GameObject("[SkillUi]");
            DontDestroyOnLoad(go);
            go.AddComponent<SkillUiRoot>();
        }

        public static void Open()
        {
            EnsureSpawned();
            Instance.EnsureBound();
            Instance._panel?.Show();
        }

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Update()
        {
            EnsureBound();
            if (IsVisible && (_app?.GameClient?.InGame != true ||
                BattleUiRoot.Instance?.IsBattleLayerVisible == true)) HidePanel();
#if ENABLE_INPUT_SYSTEM
            if (IsVisible && UnityEngine.InputSystem.Keyboard.current?.escapeKey.wasPressedThisFrame == true) HidePanel();
#else
            if (IsVisible && Input.GetKeyDown(KeyCode.Escape)) HidePanel();
#endif
        }

        public void HidePanel() => _panel?.Hide();

        private void EnsureBound()
        {
            if (_app == null) _app = FindAnyObjectByType<AppBootstrap>();
            if (_app == null) return;
            if (_panel == null) BuildCanvas();
            if (Client == SkillClient.Instance) return;
            Unbind();
            Client = SkillClient.Instance;
            if (Client == null) return;
            Client.Changed += OnChanged;
            Client.Error += OnError;
            Client.Message += OnMessage;
            OnChanged();
            if (IsVisible) Client.RequestPanel();
        }

        private void BuildCanvas()
        {
            var go = new GameObject("[SkillUgui]", typeof(RectTransform), typeof(Canvas),
                typeof(CanvasScaler), typeof(GraphicRaycaster));
            go.transform.SetParent(transform, false);
            var canvas = go.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 162;
            canvas.pixelPerfect = true;
            var scaler = go.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(QdaoUguiTheme.DesignWidth, QdaoUguiTheme.DesignHeight);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.Expand;
            var page = new GameObject("WindowRoot", typeof(RectTransform));
            var rect = (RectTransform)page.transform;
            rect.SetParent(go.transform, false);
            rect.anchorMin = rect.anchorMax = rect.pivot = new Vector2(0.5f, 0.5f);
            rect.sizeDelta = new Vector2(QdaoUguiTheme.DesignWidth, QdaoUguiTheme.DesignHeight);
            rect.anchoredPosition = Vector2.zero;
            _panel = new SkillPanel(this, rect);
        }

        private void OnChanged() => _panel?.Apply(Client?.Snapshot);
        private void OnError(string error) => _panel?.SetStatus(error, true);
        private void OnMessage(string text) => _panel?.SetStatus(text);

        private void Unbind()
        {
            if (Client == null) return;
            Client.Changed -= OnChanged;
            Client.Error -= OnError;
            Client.Message -= OnMessage;
            Client = null;
        }

        private void OnDestroy()
        {
            Unbind();
            if (Instance == this) Instance = null;
        }
    }
}
