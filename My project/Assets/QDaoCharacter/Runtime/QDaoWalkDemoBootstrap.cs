using UnityEngine;

namespace QDaoCharacter
{
    [DisallowMultipleComponent]
    public sealed class QDaoWalkDemoBootstrap : MonoBehaviour
    {
        private const int BackgroundSortingOrder = -100;
        private const int DecorationSortingOrder = -80;
        private const int GroundSortingOrder = -50;

        private static readonly Color BackdropTop = new Color(0.025f, 0.09f, 0.18f, 1f);
        private static readonly Color BackdropBottom = new Color(0.035f, 0.30f, 0.32f, 1f);
        private static readonly Color Jade = new Color(0.12f, 0.78f, 0.66f, 1f);
        private static readonly Color Gold = new Color(1f, 0.71f, 0.25f, 1f);

        private bool built;

        private void Awake()
        {
            BuildDemo();
        }

        private void BuildDemo()
        {
            if (built)
            {
                return;
            }

            built = true;
            Application.targetFrameRate = 60;

            Camera demoCamera = CreateCamera();
            CreateEnvironment(demoCamera);
            QDaoEightDirectionPlayer player = CreatePlayer();
            QDaoWalkDemoHud hud = gameObject.AddComponent<QDaoWalkDemoHud>();
            hud.Bind(player);
        }

        private Camera CreateCamera()
        {
            GameObject cameraObject = new GameObject("QDao Demo Camera");
            cameraObject.transform.SetParent(transform, false);
            cameraObject.transform.position = new Vector3(0f, -0.35f, -10f);
            cameraObject.tag = "MainCamera";

            Camera demoCamera = cameraObject.AddComponent<Camera>();
            demoCamera.orthographic = true;
            demoCamera.orthographicSize = 5f;
            demoCamera.clearFlags = CameraClearFlags.SolidColor;
            demoCamera.backgroundColor = BackdropTop;
            demoCamera.nearClipPlane = 0.1f;
            demoCamera.farClipPlane = 50f;
            demoCamera.allowHDR = true;
            demoCamera.allowMSAA = true;

            cameraObject.AddComponent<AudioListener>();
            return demoCamera;
        }

        private void CreateEnvironment(Camera demoCamera)
        {
            float height = demoCamera.orthographicSize * 2f + 1f;
            float width = Mathf.Max(18f, height * Mathf.Max(1.6f, demoCamera.aspect));

            Sprite gradient = CreateGradientSprite(96, 96, BackdropBottom, BackdropTop);
            CreateSpriteObject(
                "Code Generated Gradient Backdrop",
                gradient,
                Vector3.zero,
                new Vector2(width, height),
                Color.white,
                BackgroundSortingOrder,
                transform);

            Sprite haze = CreateSoftEllipseSprite(192, 96);
            CreateSpriteObject(
                "Jade Ground Haze",
                haze,
                new Vector3(0f, -3.15f, 0f),
                new Vector2(13.8f, 2.5f),
                new Color(Jade.r, Jade.g, Jade.b, 0.28f),
                GroundSortingOrder,
                transform);

            CreateSpriteObject(
                "Golden Ground Glow",
                haze,
                new Vector3(0f, -3.05f, 0f),
                new Vector2(8.5f, 1.05f),
                new Color(Gold.r, Gold.g, Gold.b, 0.17f),
                GroundSortingOrder + 1,
                transform);

            CreateCloud(haze, new Vector2(-6.6f, 2.55f), new Vector2(4.9f, 1.2f), 0.16f, 0.12f);
            CreateCloud(haze, new Vector2(5.8f, 2.15f), new Vector2(5.6f, 1.35f), 0.13f, 0.17f);
            CreateCloud(haze, new Vector2(-5.3f, -0.15f), new Vector2(3.6f, 0.75f), 0.09f, 0.22f);
            CreateCloud(haze, new Vector2(6.4f, -0.55f), new Vector2(4.2f, 0.9f), 0.08f, 0.27f);

            Sprite orb = CreateSoftCircleSprite(72);
            Vector2[] orbPositions =
            {
                new Vector2(-7.3f, 3.45f),
                new Vector2(-5.8f, 1.45f),
                new Vector2(-3.9f, 3.05f),
                new Vector2(3.8f, 3.25f),
                new Vector2(5.7f, 1.05f),
                new Vector2(7.2f, 3.6f)
            };

            for (int index = 0; index < orbPositions.Length; index++)
            {
                float size = index % 2 == 0 ? 0.32f : 0.22f;
                Color tint = index % 2 == 0
                    ? new Color(Gold.r, Gold.g, Gold.b, 0.55f)
                    : new Color(Jade.r, Jade.g, Jade.b, 0.48f);
                GameObject orbObject = CreateSpriteObject(
                    "Ambient Spirit Light " + (index + 1),
                    orb,
                    orbPositions[index],
                    new Vector2(size, size),
                    tint,
                    DecorationSortingOrder + 1,
                    transform);

                QDaoAmbientMotion motion = orbObject.AddComponent<QDaoAmbientMotion>();
                motion.Initialize(orbPositions[index], 0.08f + index * 0.01f, 0.55f + index * 0.07f, index * 0.9f);
            }
        }

        private QDaoEightDirectionPlayer CreatePlayer()
        {
            GameObject playerObject = new GameObject("QDao Eight Direction Player");
            playerObject.SetActive(false);
            playerObject.transform.SetParent(transform, false);
            playerObject.transform.position = new Vector3(0f, -2.45f, 0f);

            SpriteRenderer renderer = playerObject.AddComponent<SpriteRenderer>();
            renderer.sortingOrder = 10;
            renderer.color = Color.white;

            Sprite shadowSprite = CreateSoftEllipseSprite(128, 64);
            CreateSpriteObject(
                "Character Shadow",
                shadowSprite,
                new Vector3(0f, -0.08f, 0f),
                new Vector2(1.75f, 0.42f),
                new Color(0f, 0.02f, 0.03f, 0.58f),
                4,
                playerObject.transform);

            Sprite glowSprite = CreateSoftCircleSprite(96);
            CreateSpriteObject(
                "Character Soft Glow",
                glowSprite,
                new Vector3(0f, 1.15f, 0f),
                new Vector2(3.5f, 3.5f),
                new Color(Gold.r, Gold.g, Gold.b, 0.07f),
                3,
                playerObject.transform);

            QDaoEightDirectionPlayer player = playerObject.AddComponent<QDaoEightDirectionPlayer>();
            player.ConfigureBounds(new Vector2(-6.7f, -3.15f), new Vector2(6.7f, 1.45f));
            playerObject.SetActive(true);
            return player;
        }

        private void CreateCloud(
            Sprite haze,
            Vector2 position,
            Vector2 size,
            float opacity,
            float phase)
        {
            GameObject cloud = CreateSpriteObject(
                "Ambient Cloud",
                haze,
                position,
                size,
                new Color(0.52f, 0.92f, 0.88f, opacity),
                DecorationSortingOrder,
                transform);

            QDaoAmbientMotion motion = cloud.AddComponent<QDaoAmbientMotion>();
            motion.Initialize(position, 0.05f, 0.18f, phase * Mathf.PI * 2f);
        }

        private static GameObject CreateSpriteObject(
            string objectName,
            Sprite sprite,
            Vector3 position,
            Vector2 worldSize,
            Color tint,
            int sortingOrder,
            Transform parent)
        {
            GameObject spriteObject = new GameObject(objectName);
            spriteObject.transform.SetParent(parent, false);
            spriteObject.transform.localPosition = position;

            SpriteRenderer renderer = spriteObject.AddComponent<SpriteRenderer>();
            renderer.sprite = sprite;
            renderer.color = tint;
            renderer.sortingOrder = sortingOrder;

            Vector2 spriteSize = sprite.bounds.size;
            spriteObject.transform.localScale = new Vector3(
                worldSize.x / Mathf.Max(0.001f, spriteSize.x),
                worldSize.y / Mathf.Max(0.001f, spriteSize.y),
                1f);
            return spriteObject;
        }

        private static Sprite CreateGradientSprite(int width, int height, Color bottom, Color top)
        {
            Texture2D texture = CreateTexture("QDao Code Gradient", width, height);
            Color[] pixels = new Color[width * height];

            for (int y = 0; y < height; y++)
            {
                float vertical = y / (float)(height - 1);
                Color rowColor = Color.Lerp(bottom, top, Mathf.SmoothStep(0f, 1f, vertical));

                for (int x = 0; x < width; x++)
                {
                    float horizontal = x / (float)(width - 1);
                    float centerGlow = Mathf.Clamp01(1f - Vector2.Distance(
                        new Vector2(horizontal, vertical),
                        new Vector2(0.5f, 0.34f)) * 1.5f);
                    Color glow = Color.Lerp(rowColor, new Color(0.06f, 0.42f, 0.39f, 1f), centerGlow * 0.22f);
                    pixels[y * width + x] = glow;
                }
            }

            texture.SetPixels(pixels);
            texture.Apply(false, true);
            return Sprite.Create(texture, new Rect(0, 0, width, height), new Vector2(0.5f, 0.5f), 100f);
        }

        private static Sprite CreateSoftEllipseSprite(int width, int height)
        {
            Texture2D texture = CreateTexture("QDao Code Soft Ellipse", width, height);
            Color[] pixels = new Color[width * height];

            for (int y = 0; y < height; y++)
            {
                float normalizedY = (y / (float)(height - 1) - 0.5f) * 2f;
                for (int x = 0; x < width; x++)
                {
                    float normalizedX = (x / (float)(width - 1) - 0.5f) * 2f;
                    float distance = normalizedX * normalizedX + normalizedY * normalizedY;
                    float alpha = 1f - Mathf.SmoothStep(0.15f, 1f, distance);
                    pixels[y * width + x] = new Color(1f, 1f, 1f, alpha);
                }
            }

            texture.SetPixels(pixels);
            texture.Apply(false, true);
            return Sprite.Create(texture, new Rect(0, 0, width, height), new Vector2(0.5f, 0.5f), 100f);
        }

        private static Sprite CreateSoftCircleSprite(int size)
        {
            Texture2D texture = CreateTexture("QDao Code Soft Circle", size, size);
            Color[] pixels = new Color[size * size];

            for (int y = 0; y < size; y++)
            {
                float normalizedY = (y / (float)(size - 1) - 0.5f) * 2f;
                for (int x = 0; x < size; x++)
                {
                    float normalizedX = (x / (float)(size - 1) - 0.5f) * 2f;
                    float distance = Mathf.Sqrt(normalizedX * normalizedX + normalizedY * normalizedY);
                    float alpha = 1f - Mathf.SmoothStep(0.08f, 1f, distance);
                    pixels[y * size + x] = new Color(1f, 1f, 1f, alpha);
                }
            }

            texture.SetPixels(pixels);
            texture.Apply(false, true);
            return Sprite.Create(texture, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), 100f);
        }

        private static Texture2D CreateTexture(string textureName, int width, int height)
        {
            Texture2D texture = new Texture2D(width, height, TextureFormat.RGBA32, false);
            texture.name = textureName;
            texture.wrapMode = TextureWrapMode.Clamp;
            texture.filterMode = FilterMode.Bilinear;
            return texture;
        }
    }

    [DisallowMultipleComponent]
    internal sealed class QDaoAmbientMotion : MonoBehaviour
    {
        private Vector3 origin;
        private float amplitude;
        private float speed;
        private float phase;

        public void Initialize(Vector2 startPosition, float movementAmplitude, float movementSpeed, float startPhase)
        {
            origin = new Vector3(startPosition.x, startPosition.y, transform.localPosition.z);
            amplitude = movementAmplitude;
            speed = movementSpeed;
            phase = startPhase;
        }

        private void Update()
        {
            float time = Time.time * speed + phase;
            transform.localPosition = origin + new Vector3(
                Mathf.Sin(time * 0.73f) * amplitude,
                Mathf.Sin(time) * amplitude,
                0f);
        }
    }

    [DisallowMultipleComponent]
    internal sealed class QDaoWalkDemoHud : MonoBehaviour
    {
        private QDaoEightDirectionPlayer player;
        private GUIStyle titleStyle;
        private GUIStyle bodyStyle;
        private GUIStyle statusStyle;
        private Texture2D panelTexture;

        public void Bind(QDaoEightDirectionPlayer targetPlayer)
        {
            player = targetPlayer;
        }

        private void OnGUI()
        {
            EnsureStyles();

            float scale = Mathf.Clamp(Screen.height / 900f, 0.78f, 1.35f);
            float margin = 24f * scale;
            float panelWidth = Mathf.Min(430f * scale, Screen.width - margin * 2f);
            Rect panel = new Rect(margin, margin, panelWidth, 142f * scale);

            GUI.DrawTexture(panel, panelTexture, ScaleMode.StretchToFill);
            GUI.Label(new Rect(panel.x + 20f * scale, panel.y + 14f * scale, panel.width - 40f * scale, 30f * scale),
                "QDAO · 8-DIRECTION WALK", titleStyle);
            GUI.Label(new Rect(panel.x + 20f * scale, panel.y + 51f * scale, panel.width - 40f * scale, 26f * scale),
                "WASD / Arrow Keys / Left Stick", bodyStyle);

            string state = player != null && player.IsMoving ? "WALKING" : "IDLE";
            string facing = player != null ? FormatDirection(player.Facing) : "LOADING";
            GUI.Label(new Rect(panel.x + 20f * scale, panel.y + 83f * scale, panel.width - 40f * scale, 25f * scale),
                state + "  ·  " + facing, statusStyle);
            GUI.Label(new Rect(panel.x + 20f * scale, panel.y + 112f * scale, panel.width - 40f * scale, 20f * scale),
                "1254×1254 lossless PNG · 8 directions × 4 frames", bodyStyle);
        }

        private void EnsureStyles()
        {
            if (titleStyle != null)
            {
                return;
            }

            panelTexture = new Texture2D(1, 1, TextureFormat.RGBA32, false);
            panelTexture.SetPixel(0, 0, new Color(0.015f, 0.055f, 0.09f, 0.86f));
            panelTexture.Apply(false, true);

            titleStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 21,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleLeft
            };
            titleStyle.normal.textColor = new Color(1f, 0.78f, 0.34f, 1f);

            bodyStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 14,
                alignment = TextAnchor.MiddleLeft
            };
            bodyStyle.normal.textColor = new Color(0.78f, 0.92f, 0.91f, 1f);

            statusStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 15,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleLeft
            };
            statusStyle.normal.textColor = new Color(0.25f, 1f, 0.78f, 1f);
        }

        private static string FormatDirection(QDaoDirection direction)
        {
            switch (direction)
            {
                case QDaoDirection.NorthEast:
                    return "NORTH-EAST";
                case QDaoDirection.NorthWest:
                    return "NORTH-WEST";
                case QDaoDirection.SouthEast:
                    return "SOUTH-EAST";
                case QDaoDirection.SouthWest:
                    return "SOUTH-WEST";
                default:
                    return direction.ToString().ToUpperInvariant();
            }
        }
    }
}
