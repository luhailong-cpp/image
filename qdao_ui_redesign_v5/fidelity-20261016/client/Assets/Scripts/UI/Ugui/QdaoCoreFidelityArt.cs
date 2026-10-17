using TMPro;
using UnityEngine;
using UnityEngine.UI;
namespace MmorpgClient.UI.Ugui
{
    internal static class QdaoCoreFidelityArt
    {
        public const string Root = "UI/Ugui/CoreFidelity20261016/";
        public static readonly Color Ink = QdaoUguiTheme.Html("#244C3E"), Ivory = QdaoUguiTheme.Html("#FFF3D3");
        public static Sprite Load(string key)
        {
            string alias = key switch {
                "server_card_wide_normal" => "server_card_normal", "server_card_wide_selected" => "server_card_selected",
                "server_card_wide_disabled" => "server_card_disabled", "list_row_normal" => "server_category_normal",
                "list_row_selected" => "server_category_selected", "list_row_disabled" => "server_category_normal",
                "search_normal" => "server_search", "tab_normal" => "server_back", "tab_selected" => "server_category_selected",
                "primary_button_normal" => "server_enter", "primary_button_selected" => "server_enter", _ => key };
            return Resources.Load<Sprite>(Root + alias) ?? QdaoRefreshArt.Load(key);
        }
        public static void Skin(Image image, string key)
        {
            if (image == null) return;
            image.sprite = Load(key); image.color = Color.white;
            image.type = image.sprite.border.sqrMagnitude > 0 ? Image.Type.Sliced : Image.Type.Simple;
            image.preserveAspect = false;
            image.pixelsPerUnitMultiplier = Mathf.Max(.01f, image.sprite.rect.height / Mathf.Max(1, image.rectTransform.rect.height));
        }
        public static Image Panel(string name, UnityEngine.Transform parent, float x, float y, float w, float h, string key = "content_panel")
        { var image = QdaoUguiFactory.CreateImage(name,parent,x,y,w,h,Load(key)); Skin(image,key); return image; }
        public static Button Button(string name, UnityEngine.Transform parent,float x,float y,float w,float h,string key,out Image image)
        {
            var button=QdaoUguiFactory.CreateArtButton(name,parent,x,y,w,h,Load(key),out image);Skin(image,key);
            button.navigation=new Navigation { mode=Navigation.Mode.Automatic };
            var colors=button.colors;colors.highlightedColor=new Color(1,.97f,.84f);colors.selectedColor=colors.highlightedColor;button.colors=colors;
            return button;
        }
        public static void ApplyText(TMP_Text text) { if(text!=null){text.font=QdaoUguiTheme.ResolveFont();text.richText=false;} }
        public static Sprite LoadCharacterPortrait(string id)
        {
            // Same-identity standalone portrait only. Unknown ids still remain unknown;
            // this UI path does not approve or activate any animation package.
            return id == "04_mountain_guardian_boy" ? Resources.Load<Sprite>(Root + "portraits/04_mountain_guardian_boy") : null;
        }
    }
    internal static class RoleFidelityArt
    {
        private static string Key(string key) => key switch {
            "server_card_medium_normal" => "role_card_normal", "server_card_medium_selected" => "role_card_selected",
            "list_row_normal" => "role_card_normal", "list_row_selected" => "role_card_selected",
            "primary_button_normal" => "role_enter", "primary_button_selected" => "role_enter",
            "tab_normal" => "role_back", _ => key };
        public static Sprite Load(string key) => QdaoCoreFidelityArt.Load(Key(key));
        public static void Skin(Image image,string key) => QdaoCoreFidelityArt.Skin(image,Key(key));
        public static Image Panel(string name,UnityEngine.Transform parent,float x,float y,float w,float h,string key="content_panel")
            => QdaoCoreFidelityArt.Panel(name,parent,x,y,w,h,Key(key));
        public static Button Button(string name,UnityEngine.Transform parent,float x,float y,float w,float h,string key,out Image image)
            => QdaoCoreFidelityArt.Button(name,parent,x,y,w,h,Key(key),out image);
    }
}
