const fs=require('fs'),path=require('path'),crypto=require('crypto');
const sharp=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const scene=__dirname,world='E:/work/image/designs/world-map-original-20260925/fidelity-20261016';
const client='E:/work/mmorpg-client',generated='C:/Users/luyua/.codex/generated_images/01a147f7-db0b-7272-b66f-08f0473eee35';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const config=JSON.parse(fs.readFileSync('E:/work/image/config/image-generation.json','utf8'));
const metaTemplate=fs.readFileSync('E:/work/image/designs/team-ui-v2/fidelity-20261016/runtime-assets/team_skin.png.meta','utf8');
for(const root of [scene,world])for(const dir of ['integration','runtime-assets','source','qa'])fs.mkdirSync(path.join(root,dir),{recursive:true});
const sOriginal=path.resolve(scene,'../scene-select.png'),wOriginal=path.resolve(world,'../world-map-original_2560x1080.png');
const sEdit=path.join(generated,'exec-1b9017eb-1041-4ba5-8e27-b5626c69dc11.png'),wEdit=path.join(generated,'exec-18e01e68-7065-494f-a51a-40911a9c2715.png');
const records={scene:[],world:[]};
async function save(kind,key,pipeline,sources,operation){
 const root=kind==='scene'?scene:world,file=path.join(root,'runtime-assets',key+'.png');await pipeline.png().toFile(file);
 const m=await sharp(file).metadata(),existing=fs.existsSync(file+'.meta')?fs.readFileSync(file+'.meta','utf8').match(/guid: (\w+)/)?.[1]:null;
 const guid=existing||crypto.randomBytes(16).toString('hex');
 fs.writeFileSync(file+'.meta',metaTemplate.replace(/guid: \w+/,`guid: ${guid}`));
 const record={file:path.basename(file),sha256:hash(file),width:m.width,height:m.height,format:m.format,guid,
  resourceKey:'UI/Ugui/'+(kind==='scene'?'SceneSelectV1/':'WorldMapOriginal/')+'Fidelity20261016/'+key,
  operation,derivedFrom:sources.map(p=>({file:p,sha256:hash(p)})),generationEvidence:'../source/host-edit.json',actualModel:null,actualQuality:null};
 fs.writeFileSync(file+'.generation.json',JSON.stringify(record,null,2)+'\n');records[kind].push(record);
}
function stage(root,name,transform){
 const source=client+'/Assets/Scripts/UI/Ugui/Gameplay/'+name,guardFile=path.join(root,'source-checkout.json');
 if(!fs.existsSync(guardFile))fs.writeFileSync(guardFile,JSON.stringify({copiedAtUtc:new Date().toISOString(),source,sha256:hash(source)},null,2)+'\n');
 fs.writeFileSync(path.join(root,'integration',name),transform(fs.readFileSync(source,'utf8').replaceAll('\r\n','\n')));
}
function replaceRegion(code,start,end,body){const a=code.indexOf(start),b=code.indexOf(end,a+start.length);if(a<0||b<0)throw Error(start);return code.slice(0,a)+body+'\n\n'+code.slice(b);}
(async()=>{
 const s=await sharp(sEdit).resize(1931,814).png().toBuffer();
 const header=await sharp(s).extract({left:785,top:112,width:340,height:40}).png().toBuffer();
 const paper=await sharp(s).extract({left:420,top:115,width:340,height:37}).resize(1215,510).png().toBuffer();
 // Keep the original frame/background pixels; only native dynamic areas receive cleaned surfaces.
 await save('scene','scene_skin',sharp(sOriginal).composite([
  {input:header,left:785,top:112},{input:paper,left:360,top:155},
  {input:await sharp(s).extract({left:673,top:686,width:263,height:69}).png().toBuffer(),left:673,top:686},
  {input:await sharp(s).extract({left:989,top:686,width:270,height:69}).png().toBuffer(),left:989,top:686}
 ]),[sOriginal,sEdit],{type:'original-static-pixels-with-host-cleaned-dynamic-areas',originalSize:[1931,814],regions:[[785,112,340,40],[360,155,1215,510],[673,686,263,69],[989,686,270,69]]});
 await save('scene','row_normal',sharp(s).extract({left:362,top:159,width:393,height:60}),[sOriginal,sEdit],{type:'host-cleaned-row-crop',rectangle:[362,159,393,60]});
 await save('scene','row_selected',sharp(s).extract({left:1176,top:596,width:394,height:63}),[sOriginal,sEdit],{type:'host-cleaned-selected-row-crop',rectangle:[1176,596,394,63]});
 await save('scene','button_secondary',sharp(s).extract({left:673,top:686,width:263,height:69}),[sOriginal,sEdit],{type:'host-cleaned-button-crop',rectangle:[673,686,263,69]});
 await save('scene','button_primary',sharp(s).extract({left:989,top:686,width:270,height:69}),[sOriginal,sEdit],{type:'host-cleaned-button-crop',rectangle:[989,686,270,69]});
 const w=await sharp(wEdit).resize(2560,1080).png().toBuffer();
 const regions=[[128,984,307,40],[2023,977,149,55],[2342,978,167,53],[1234,507,63,49]];
 await save('world','world_skin',sharp(wOriginal).composite(await Promise.all(regions.map(async([left,top,width,height])=>({left,top,input:await sharp(w).extract({left,top,width,height}).png().toBuffer()})))),
  [wOriginal,wEdit],{type:'original-static-pixels-with-host-cleaned-player-location-and-controls',originalSize:[2560,1080],regions});
 await save('world','destination_plate',sharp(w).extract({left:60,top:976,width:418,height:64}),[wOriginal,wEdit],{type:'host-cleaned-footer-plate-crop',rectangle:[60,976,418,64]});
 for(const [kind,root,input,original] of [['scene',scene,sEdit,sOriginal],['world',world,wEdit,wOriginal]]){
  const m=await sharp(input).metadata();fs.writeFileSync(path.join(root,'source/host-edit.json'),JSON.stringify({createdAtUtc:new Date().toISOString(),tool:'image_gen.imagegen',route:'builtin',
   configSnapshot:config,officialRecheckedOn:'2026-10-17',submittedParameters:{model:null,quality:null,transparent_background:false,referenced_image_paths:[original]},actualModel:null,actualQuality:null,
   unverifiedReason:'Host managed; tool exposes no model/quality selectors and returns no verifiable model/quality fields.',
   prompt:'edit.prompt.txt',nativeOutput:{path:input,sha256:hash(input),width:m.width,height:m.height,format:m.format},references:[{file:original,role:'approved original edit target and style reference',sha256:hash(original)}]},null,2)+'\n');
  fs.writeFileSync(path.join(root,'runtime-assets.json'),JSON.stringify({createdAtUtc:new Date().toISOString(),images:records[kind]},null,2)+'\n');
 }
 stage(scene,'SceneChannelWindow.cs',code=>{
  code=code.replace('public const int Columns = 2;','public const int Columns = 3;')
   .replace('private const float FrameWidth = 1760, FrameHeight = 924;','private const float FrameWidth = 1931, FrameHeight = 814;')
   .replace('private const float ListX = 100, ListY = 183;','private const float ListX = 363, ListY = 159;')
   .replace('private const float RowWidth = 760, RowHeight = 66, RowPitch = 71, ColumnGap = 40;','private const float RowWidth = 393, RowHeight = 60, RowPitch = 62.5f, ColumnGap = 14;')
   .replace('private const float FooterY = 798;','private const float FooterY = 695;');
  code=replaceRegion(code,'        public SceneChannelWindow(UnityEngine.Transform parent)','        /// <summary>\n        /// 换一份视图;',`        public SceneChannelWindow(UnityEngine.Transform parent)
        {
            _root=QdaoUguiFactory.CreateStretch("SceneChannelWindow",parent,Vector4.zero);
            _root.gameObject.SetActive(false);
            var shade=_root.gameObject.AddComponent<Image>();shade.color=new Color(.025f,.10f,.08f,.68f);shade.raycastTarget=true;
            _root.gameObject.AddComponent<GameplayInputBlocker>();
            var frame=QdaoUguiFactory.CreateCenteredRect("SceneChannelFrame",_root,FrameWidth,FrameHeight);
            frame.localScale=UnityEngine.Vector3.one*(2560f/1931f);
            FidelityArt(frame,"scene_skin",0,0,FrameWidth,FrameHeight);
            var topClose=QdaoUguiFactory.CreateHitButton("SceneChannelTopClose",frame,1547,30,86,86);topClose.onClick.AddListener(Hide);
            _current=Text(frame,"",600,112,730,40,26,Ink,alignment:TextAlignmentOptions.Center);_current.name="SceneChannelCurrent";
            _list=QdaoUguiFactory.CreateRect("SceneChannelLines",frame,ListX,ListY,ListWidth,ListHeight);
            _status=Text(frame,"",375,660,1180,29,20,Muted,alignment:TextAlignmentOptions.Center);_status.name="SceneChannelStatus";
            _previous=FidelityButton(frame,"上一页",375,FooterY,90,45,()=>MovePage(-1),false,23);_previous.name=PreviousPageButtonName;
            _pageLabel=Text(frame,"",468,FooterY,100,45,23,Muted,alignment:TextAlignmentOptions.Center);_pageLabel.name="SceneChannelPage";
            _next=FidelityButton(frame,"下一页",570,FooterY,90,45,()=>MovePage(1),false,23);_next.name=NextPageButtonName;
            var close=QdaoUguiFactory.CreateHitButton(CloseButtonName,frame,673,686,263,69);close.onClick.AddListener(Hide);
            Text(close.transform,"取消",20,0,223,69,36,Ink,alignment:TextAlignmentOptions.Center);
            _refresh=QdaoUguiFactory.CreateHitButton(RefreshButtonName,frame,989,686,270,69);
            _refresh.onClick.AddListener(()=>{if(CanRefresh)RefreshRequested?.Invoke();});
            _refreshLabel=Text(_refresh.transform,RefreshText,20,0,230,69,36,Cream,alignment:TextAlignmentOptions.Center);
            Pagination(_previous,_next,_pageLabel,0,1);
        }`);
  code=code.replace('float x = slot % Columns * (RowWidth + ColumnGap);','float x = slot % Columns == 0 ? 0 : slot % Columns == 1 ? 412 : 813;');
  const a=code.indexOf('            var button = Button(_list,'),b=code.indexOf('            button.name = LineButtonPrefix',a);
  code=code.slice(0,a)+`            var button=FidelityButton(_list,SceneChannelModels.LineName(line.ChannelNo),x,y,RowWidth,RowHeight,
                ()=>RequestSwitch(sceneId),line.IsCurrent,27,selectable,true);
`+code.slice(b);
  code=code.replace('new Vector2(64, 0)','new Vector2(82, 0)').replace('new Vector2(170, RowHeight)','new Vector2(170, RowHeight)')
   .replace('CurrentTagText, 250, 0, 110, RowHeight, 26, Cream','CurrentTagText, 308, -7, 72, 24, 18, Cream')
   .replace('button.transform, 520, (RowHeight - 18) / 2, 18, 18','button.transform, 31, (RowHeight - 18) / 2, 18, 18')
   .replace('546, 0, 160, RowHeight, 28','252, 0, 126, RowHeight, 21');
  const helper=`        private const string FidelityResourceRoot="UI/Ugui/SceneSelectV1/Fidelity20261016/";
        private static Image FidelityArt(UnityEngine.Transform parent,string key,float x,float y,float w,float h)
            => QdaoUguiFactory.CreateImage(key,parent,x,y,w,h,QdaoUguiTheme.RequireSprite(FidelityResourceRoot+key));
        private static Button FidelityButton(UnityEngine.Transform parent,string value,float x,float y,float w,float h,
            Action click,bool selected=false,float fontSize=26,bool enabled=true,bool row=false)
        {
            var button=QdaoUguiFactory.CreateArtButton(value,parent,x,y,w,h,QdaoUguiTheme.RequireSprite(FidelityResourceRoot+
                (row?(selected?"row_selected":"row_normal"):(selected?"button_primary":"button_secondary"))),out var image);
            image.type=Image.Type.Simple;button.interactable=enabled;button.navigation=new Navigation{mode=Navigation.Mode.Automatic};
            button.onClick.AddListener(()=>click?.Invoke());
            Text(button.transform,value,16,0,w-32,h,fontSize,selected?Cream:Ink,alignment:TextAlignmentOptions.Center);
            return button;
        }

`;
  return code.replace('        private void RequestSwitch(ulong sceneId)',helper+'        private void RequestSwitch(ulong sceneId)');
 });
 stage(world,'CityTravelWindow.cs',code=>{
  code=replaceRegion(code,'        public CityTravelWindow(UnityEngine.Transform parent)','        public void SetDestinations',`        public CityTravelWindow(UnityEngine.Transform parent)
        {
            _root=QdaoUguiFactory.CreateStretch("CityTravelWindow",parent,Vector4.zero);_root.gameObject.SetActive(false);
            var shade=_root.gameObject.AddComponent<Image>();shade.color=new Color(.025f,.10f,.08f,.68f);shade.raycastTarget=true;
            _root.gameObject.AddComponent<GameplayInputBlocker>();
            var frame=QdaoUguiFactory.CreateCenteredRect("CityTravelFrame",_root,2560,1080);
            QdaoUguiFactory.CreateImage("ApprovedWorldMap",frame,0,0,2560,1080,QdaoUguiTheme.RequireSprite(FidelityResourceRoot+"world_skin"));
            var close=QdaoUguiFactory.CreateHitButton("CloseCityTravel",frame,2435,12,93,93);close.onClick.AddListener(Hide);
            _current=Text(frame,"",128,984,307,40,26,Ink);_current.name="CityTravelCurrent";
            _destinationList=QdaoUguiFactory.CreateRect("Destinations",frame,515,976,800,64);
            // The approved world map is the main artwork. Existing destination-preview data remains available to the view,
            // but its old square thumbnail is not a second painted map over the original composition.
            var previewRect=QdaoUguiFactory.CreateRect("SelectedMapPreview",frame,0,0,0,0);
            _preview=previewRect.gameObject.AddComponent<RawImage>();_preview.raycastTarget=false;_preview.color=Color.clear;
            _name=Text(frame,"",1336,984,292,43,25,Ink);_name.name="SelectedDestinationName";
            _description=Text(frame,"",515,925,1050,32,23,Cream);_description.name="SelectedDestinationDescription";
            _appearanceHint=Text(frame,"",515,893,1050,30,21,Cream);_appearanceHint.name="DestinationAppearanceHint";
            _status=Text(frame,"",515,859,1400,32,23,Cream);_status.name="CityTravelStatus";
            _day=QdaoUguiFactory.CreateHitButton("DayAppearance",frame,2007,970,80,67);_day.onClick.AddListener(()=>SelectFestival(false));
            Text(_day.transform,"日景",0,0,80,67,25,Cream,alignment:TextAlignmentOptions.Center);
            _festivalButton=QdaoUguiFactory.CreateHitButton("FestivalAppearance",frame,2087,970,116,67);_festivalButton.onClick.AddListener(()=>SelectFestival(true));
            _festivalLabel=Text(_festivalButton.transform,"节庆",0,0,116,67,25,Cream,alignment:TextAlignmentOptions.Center);
            _zoneButton=FidelityButton(frame,"本区",1648,976,236,64,CycleZone,25);_zoneButton.name="TravelZoneCycle";
            _zoneLabel=_zoneButton.GetComponentInChildren<TMP_Text>();_zoneLabel.overflowMode=TextOverflowModes.Ellipsis;_zoneButton.gameObject.SetActive(false);
            _travel=QdaoUguiFactory.CreateHitButton("TravelToSelectedCity",frame,2218,960,304,80);
            _travel.onClick.AddListener(()=>
            {
                if(_selected==null)return;var zone=SelectedZone;
                if(zone!=null)ZoneTravelRequested?.Invoke(zone.ZoneId,_selected.SceneConfigId,_festival);
                else TravelRequested?.Invoke(_selected.SceneConfigId,_festival);
            });
            _travelLabel=Text(_travel.transform,"前往",91,0,203,80,27,Cream,alignment:TextAlignmentOptions.Center);
        }`);
  code=code.replace('var button = Button(_destinationList, value.Name, 0, row * 144, 296, 116,\n                    () => Select(value), key: "tab_normal", fontSize: 34);',
   'var button=FidelityButton(_destinationList,value.Name,row*195,0,190,64,()=>Select(value),26);');
  const a=code.indexOf('        private static void SetTab(Button button, bool selected)');
  code=code.slice(0,a)+`        private const string FidelityResourceRoot="UI/Ugui/WorldMapOriginal/Fidelity20261016/";
        private static Button FidelityButton(UnityEngine.Transform parent,string value,float x,float y,float w,float h,Action click,float size)
        {
            var button=QdaoUguiFactory.CreateArtButton(value,parent,x,y,w,h,QdaoUguiTheme.RequireSprite(FidelityResourceRoot+"destination_plate"),out var image);
            image.type=Image.Type.Simple;button.navigation=new Navigation{mode=Navigation.Mode.Automatic};button.onClick.AddListener(()=>click?.Invoke());
            Text(button.transform,value,12,0,w-24,h,size,Ink,alignment:TextAlignmentOptions.Center);return button;
        }

        private static void SetTab(Button button,bool selected)
        {
            var image=button.targetGraphic as Image;
            if(image!=null&&image.sprite!=null)image.color=selected?new Color(1f,.94f,.75f):Color.white;
            var label=button.GetComponentInChildren<TMP_Text>();if(label!=null)label.color=button.name=="DayAppearance"||button.name=="FestivalAppearance"?(selected?Cream:Gold):Ink;
        }
    }
}
`;
  return code;
 });
 console.log(JSON.stringify({sceneAssets:records.scene.length,worldAssets:records.world.length,staged:['SceneChannelWindow.cs','CityTravelWindow.cs']}));
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
