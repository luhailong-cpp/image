using System;
using System.Collections.Generic;
using UnityEngine;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace QDaoCharacter
{
    public enum QDaoDirection
    {
        East,
        NorthEast,
        North,
        NorthWest,
        West,
        SouthWest,
        South,
        SouthEast
    }

    [DisallowMultipleComponent]
    [RequireComponent(typeof(SpriteRenderer))]
    public sealed class QDaoEightDirectionPlayer : MonoBehaviour
    {
        public const string SpriteResourcePath = "QDaoCharacter/Walk";

        private static readonly IReadOnlyDictionary<QDaoDirection, string> DirectionPrefixes =
            new Dictionary<QDaoDirection, string>
            {
                { QDaoDirection.East, "east" },
                { QDaoDirection.NorthEast, "northeast" },
                { QDaoDirection.North, "north" },
                { QDaoDirection.NorthWest, "northwest" },
                { QDaoDirection.West, "west" },
                { QDaoDirection.SouthWest, "southwest" },
                { QDaoDirection.South, "south" },
                { QDaoDirection.SouthEast, "southeast" }
            };

        [Header("Movement")]
        [SerializeField, Min(0.1f)] private float moveSpeed = 3.25f;
        [SerializeField] private Vector2 minimumWorldPosition = new Vector2(-6.7f, -3.15f);
        [SerializeField] private Vector2 maximumWorldPosition = new Vector2(6.7f, 1.45f);

        [Header("Animation")]
        [SerializeField, Min(1f)] private float framesPerSecond = 7.5f;
        [SerializeField] private QDaoDirection initialFacing = QDaoDirection.South;

        private readonly Dictionary<QDaoDirection, Sprite[]> framesByDirection =
            new Dictionary<QDaoDirection, Sprite[]>();

        private SpriteRenderer spriteRenderer;
        private QDaoDirection facing;
        private int frameIndex;
        private float frameTimer;
        private bool spritesLoaded;

        public QDaoDirection Facing => facing;
        public bool IsMoving { get; private set; }
        public Vector2 MoveInput { get; private set; }
        public int LoadedFrameCount { get; private set; }

        private void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            facing = initialFacing;
            spritesLoaded = LoadFrames();

            if (spritesLoaded)
            {
                ShowCurrentFrame();
            }
        }

        private void Update()
        {
            if (!spritesLoaded)
            {
                return;
            }

            MoveInput = ReadMoveInput();
            IsMoving = MoveInput.sqrMagnitude > 0.001f;

            if (!IsMoving)
            {
                frameIndex = 0;
                frameTimer = 0f;
                ShowCurrentFrame();
                return;
            }

            Vector2 normalizedMovement = Vector2.ClampMagnitude(MoveInput, 1f);
            Move(normalizedMovement);

            QDaoDirection newFacing = GetDirection(normalizedMovement);
            if (newFacing != facing)
            {
                facing = newFacing;
                frameIndex = 0;
                frameTimer = 0f;
            }

            AdvanceAnimation(Time.deltaTime);
        }

        public void ConfigureBounds(Vector2 minimum, Vector2 maximum)
        {
            minimumWorldPosition = Vector2.Min(minimum, maximum);
            maximumWorldPosition = Vector2.Max(minimum, maximum);
        }

        public static QDaoDirection GetDirection(Vector2 movement)
        {
            if (movement.sqrMagnitude <= Mathf.Epsilon)
            {
                return QDaoDirection.South;
            }

            float angle = Mathf.Atan2(movement.y, movement.x) * Mathf.Rad2Deg;
            if (angle < 0f)
            {
                angle += 360f;
            }

            int octant = Mathf.RoundToInt(angle / 45f) & 7;
            return (QDaoDirection)octant;
        }

        private bool LoadFrames()
        {
            Sprite[] allSprites = Resources.LoadAll<Sprite>(SpriteResourcePath);
            LoadedFrameCount = allSprites.Length;

            if (allSprites.Length == 0)
            {
                Debug.LogError(
                    $"[QDaoCharacter] No sprites found in Resources/{SpriteResourcePath}. " +
                    "Run Tools > QDao Character > Build Walk Demo Scene to import the character frames.",
                    this);
                return false;
            }

            foreach (KeyValuePair<QDaoDirection, string> pair in DirectionPrefixes)
            {
                string expectedPrefix = pair.Value + "_frame_";
                List<Sprite> directionFrames = new List<Sprite>();

                foreach (Sprite sprite in allSprites)
                {
                    if (sprite.name.StartsWith(expectedPrefix, StringComparison.OrdinalIgnoreCase))
                    {
                        directionFrames.Add(sprite);
                    }
                }

                directionFrames.Sort((left, right) => string.CompareOrdinal(left.name, right.name));
                if (directionFrames.Count == 0)
                {
                    Debug.LogError($"[QDaoCharacter] Missing animation frames for {pair.Key}.", this);
                    return false;
                }

                framesByDirection[pair.Key] = directionFrames.ToArray();
            }

            return true;
        }

        private void Move(Vector2 movement)
        {
            Vector3 position = transform.position;
            position += (Vector3)(movement * (moveSpeed * Time.deltaTime));
            position.x = Mathf.Clamp(position.x, minimumWorldPosition.x, maximumWorldPosition.x);
            position.y = Mathf.Clamp(position.y, minimumWorldPosition.y, maximumWorldPosition.y);
            transform.position = position;
        }

        private void AdvanceAnimation(float deltaTime)
        {
            Sprite[] frames = framesByDirection[facing];
            frameTimer += deltaTime;
            float frameDuration = 1f / Mathf.Max(1f, framesPerSecond);

            while (frameTimer >= frameDuration)
            {
                frameTimer -= frameDuration;
                frameIndex = (frameIndex + 1) % frames.Length;
            }

            ShowCurrentFrame();
        }

        private void ShowCurrentFrame()
        {
            Sprite[] frames;
            if (!framesByDirection.TryGetValue(facing, out frames) || frames.Length == 0)
            {
                return;
            }

            int safeFrameIndex = Mathf.Clamp(frameIndex, 0, frames.Length - 1);
            Sprite nextSprite = frames[safeFrameIndex];
            if (spriteRenderer.sprite != nextSprite)
            {
                spriteRenderer.sprite = nextSprite;
            }
        }

        private static Vector2 ReadMoveInput()
        {
            Vector2 keyboardInput = Vector2.zero;
            Vector2 gamepadInput = Vector2.zero;

#if ENABLE_INPUT_SYSTEM
            Keyboard keyboard = Keyboard.current;
            if (keyboard != null)
            {
                float horizontal = 0f;
                float vertical = 0f;

                if (keyboard.aKey.isPressed || keyboard.leftArrowKey.isPressed)
                {
                    horizontal -= 1f;
                }

                if (keyboard.dKey.isPressed || keyboard.rightArrowKey.isPressed)
                {
                    horizontal += 1f;
                }

                if (keyboard.sKey.isPressed || keyboard.downArrowKey.isPressed)
                {
                    vertical -= 1f;
                }

                if (keyboard.wKey.isPressed || keyboard.upArrowKey.isPressed)
                {
                    vertical += 1f;
                }

                keyboardInput = new Vector2(horizontal, vertical);
            }

            Gamepad gamepad = Gamepad.current;
            if (gamepad != null)
            {
                gamepadInput = gamepad.leftStick.ReadValue();
                if (gamepadInput.sqrMagnitude < 0.0225f)
                {
                    gamepadInput = Vector2.zero;
                }
            }
#else
            keyboardInput = new Vector2(Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical"));
#endif

            Vector2 input = gamepadInput.sqrMagnitude > keyboardInput.sqrMagnitude
                ? gamepadInput
                : keyboardInput;
            return Vector2.ClampMagnitude(input, 1f);
        }

        private void OnValidate()
        {
            moveSpeed = Mathf.Max(0.1f, moveSpeed);
            framesPerSecond = Mathf.Max(1f, framesPerSecond);
            Vector2 actualMinimum = Vector2.Min(minimumWorldPosition, maximumWorldPosition);
            Vector2 actualMaximum = Vector2.Max(minimumWorldPosition, maximumWorldPosition);
            minimumWorldPosition = actualMinimum;
            maximumWorldPosition = actualMaximum;
        }
    }
}
