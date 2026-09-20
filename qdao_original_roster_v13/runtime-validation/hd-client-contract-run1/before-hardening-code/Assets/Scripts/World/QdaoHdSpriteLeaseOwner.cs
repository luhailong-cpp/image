using UnityEngine;

namespace MmorpgClient.World
{
    /// <summary>Retains an HD direction while a UI Image/afterimage still displays one of its sprites.</summary>
    [DisallowMultipleComponent]
    public sealed class QdaoHdSpriteLeaseOwner : MonoBehaviour
    {
        private QdaoHdResources.Lease _lease;
        public void BindSprite(Sprite sprite)
        {
            var next = QdaoHdResources.RetainSprite(sprite);
            var previous = _lease;
            _lease = next;
            previous?.Dispose();
        }
        // Call only after clearing/replacing all images this owner protects.
        public void Clear() { var previous = _lease; _lease = null; previous?.Dispose(); }
        private void OnDestroy() => Clear();
    }
}
