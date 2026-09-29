"use strict";

// Only local design-preview data; there is no account, inventory or server connection.
const STORAGE_KEY = "wuxing-qitan-mail-ui-v1";
const STORAGE_VERSION = 3;
const festivalEvents = {
  midautumn: {
    image: "event-midautumn.png", alt: "金发带 Q 版小道童与玉兔在青绿道观赏月放花灯",
    tone: "dark", kicker: "中 秋 雅 集", lines: ["月满仙山", "玉兔送福"], tagline: "桂香伴月 · 花灯寄情",
    title: "月满仙山 · 玉兔送福", intro: "与道友共赏一轮明月，提一盏花灯，在桂香与云海间赴团圆之约。",
    activities: ["月下祈福", "花灯游园", "玉兔寻宝"]
  },
  "spring-festival": {
    image: "event-spring-festival.png", alt: "道家 Q 版仙山迎春插画，点缀红灯笼与新春福饰",
    kicker: "新 春 迎 福", lines: ["岁启仙山", "福满云门"], tagline: "迎春纳福 · 共赴新岁",
    title: "岁启仙山 · 福满云门", intro: "新春福灯照亮山门，与道友互道吉言，在青绿仙境里迎接新的旅程。",
    activities: ["迎春祈福", "新岁游园", "福签寻踪"], gift: "迎春福礼",
    letter: "新春将至，仙山福灯次第点亮。邀你与道友同游山门、互赠祝福，迎接万物更新。"
  },
  "lantern-festival": {
    image: "event-lantern-festival.png", alt: "道家 Q 版元宵灯会插画，圆润花灯映照仙山",
    tone: "dark", kicker: "元 宵 灯 会", lines: ["灯映云阶", "元夕同游"], tagline: "花灯如昼 · 团圆相伴",
    title: "灯映云阶 · 元夕同游", intro: "提灯走过云阶，与道友猜灯谜、赏灯影，在暖光里共度团圆之夜。",
    activities: ["花灯游园", "灯谜小会", "团圆祈愿"], gift: "元宵灯礼",
    letter: "元夕灯火照亮云阶，山门已备好花灯与灯谜。愿你在热闹灯影中寻得一份团圆与欢喜。"
  },
  "spring-equinox": {
    image: "event-spring-equinox.png", alt: "道家 Q 版春分插画，小道童在青绿仙山湖畔照料新芽，燕子掠过春空",
    kicker: "春 分 新 绿", lines: ["昼夜均分", "万物迎新"], tagline: "燕归云岭 · 新芽初生",
    title: "昼夜均分 · 万物迎新", intro: "春光正好，山间新芽破土。与道友循着燕影游园，一同迎接草木舒展的时节。",
    activities: ["春日育苗", "燕归寻踪", "仙山游园"], gift: "春分新芽礼",
    letter: "春分已至，昼夜相半，仙山草木悄然抽新。邀你与道友照料一株嫩芽，共赏明净春光。"
  },
  qingming: {
    image: "event-qingming.png", alt: "道家 Q 版清明踏青插画，青绿仙山沐在清润春光中",
    kicker: "清 明 踏 青", lines: ["清风寄思", "踏青寻春"], tagline: "春草新绿 · 清心远行",
    title: "清风寄思 · 踏青寻春", intro: "循着山间新绿缓步远行，折柳寄思，在清润春光中珍惜眼前相伴。",
    activities: ["仙山踏青", "折柳寄思", "春景寻访"], gift: "清明春礼",
    letter: "清风拂过山间，草木正绿。邀你放慢脚步踏青寻春，也在这一日遥寄思念、珍惜相伴。"
  },
  "dragon-boat": {
    image: "event-dragon-boat.png", alt: "道家 Q 版端午插画，龙舟、艾草与粽叶点缀青绿水岸",
    kicker: "端 午 雅 集", lines: ["艾香满袖", "龙舟逐浪"], tagline: "粽叶清香 · 平安相伴",
    title: "艾香满袖 · 龙舟逐浪", intro: "沿着青绿水岸观龙舟、闻艾香，与道友共享粽香和端午安康。",
    activities: ["龙舟观赛", "香囊祈安", "粽香小宴"], gift: "端午安康礼",
    letter: "粽叶飘香，艾草迎风。仙山水岸已传来龙舟鼓声，邀你与道友共度平安热闹的端午。"
  },
  "summer-solstice": {
    image: "event-summer-solstice.png", alt: "道家 Q 版夏至插画，仙山湖畔荷叶舒展，小道童在清风中纳凉",
    kicker: "夏 至 清 风", lines: ["日长云暖", "荷风送凉"], tagline: "绿荫映水 · 共赏盛夏",
    title: "日长云暖 · 荷风送凉", intro: "长日照亮仙山水岸，荷叶随风轻摇。与道友漫步绿荫，寻一处清凉共度盛夏。",
    activities: ["荷塘纳凉", "绿荫游园", "夏日祈愿"], gift: "夏至清凉礼",
    letter: "夏至已至，白昼正长，荷风吹过青绿水岸。邀你与道友在山间寻一处清凉，共赏盛夏生机。"
  },
  qixi: {
    image: "event-qixi.png", alt: "道家 Q 版七夕插画，星桥与柔和灯影映照仙山夜色",
    tone: "dark", kicker: "七 夕 星 愿", lines: ["星桥映夜", "巧愿成真"], tagline: "星河为证 · 心愿相随",
    title: "星桥映夜 · 巧愿成真", intro: "仰望仙山星河，写下心愿，和珍惜的人一同走过柔光点亮的星桥。",
    activities: ["星桥祈愿", "巧艺游园", "星灯寻踪"], gift: "七夕星愿礼",
    letter: "今夜星河明亮，云间星桥悄然点亮。邀你与珍惜的人同赏星灯，把心中所愿轻轻写下。"
  },
  "autumn-equinox": {
    image: "event-autumn-equinox.png", alt: "道家 Q 版秋分插画，仙山秋色与成熟稻穗映照澄澈天空",
    kicker: "秋 分 丰 景", lines: ["昼夜再平", "金穗迎秋"], tagline: "云清谷熟 · 秋色正浓",
    title: "昼夜再平 · 金穗迎秋", intro: "秋分天高云淡，山间谷穗渐熟。与道友登高望远，分享丰收时节的安宁与喜悦。",
    activities: ["秋野寻穗", "山间赏景", "丰年祈愿"], gift: "秋分丰收礼",
    letter: "秋分已至，昼夜相半，仙山染上温润秋色。邀你与道友走过成熟田畦，同享丰收的喜悦。"
  },
  "double-ninth": {
    image: "event-double-ninth.png", alt: "道家 Q 版重阳登高插画，菊花与茱萸点缀秋日仙山",
    kicker: "重 阳 登 高", lines: ["登高望远", "敬长安康"], tagline: "菊香满山 · 福寿绵长",
    title: "登高望远 · 敬长安康", intro: "循秋色登上云峰，赏菊祈福，也向长者送上一份敬意与平安祝愿。",
    activities: ["仙山登高", "赏菊祈福", "敬老献礼"], gift: "重阳安康礼",
    letter: "秋色染遍云峰，菊香飘过山门。邀你登高望远，也向身边长者道一声安康。"
  },
  "winter-solstice": {
    image: "event-winter-solstice.png", alt: "道家 Q 版冬至插画，仙山雪景与暖炉小宴相映",
    kicker: "冬 至 围 炉", lines: ["长夜渐短", "暖意长存"], tagline: "围炉相聚 · 共盼春归",
    title: "长夜渐短 · 暖意长存", intro: "山外清雪初落，山内暖炉正红。与道友相聚片刻，分享一碗热食和冬日祝福。",
    activities: ["围炉小宴", "冬日祈暖", "雪景游园"], gift: "冬至暖心礼",
    letter: "冬至已到，仙山炉火正暖。邀你暂歇脚步，与道友围炉小聚，静待春归。"
  },
  laba: {
    image: "event-laba.png", alt: "道家 Q 版腊八插画，暖粥与节庆小饰点缀冬日道观",
    kicker: "腊 八 送 暖", lines: ["腊香盈盏", "福粥暖心"], tagline: "一碗暖粥 · 岁末安宁",
    title: "腊香盈盏 · 福粥暖心", intro: "岁末山中飘起粥香，与道友分享一碗暖粥，把平安与祝福送入寒冬。",
    activities: ["暖粥分享", "岁末祈福", "山门送暖"], gift: "腊八暖粥礼",
    letter: "腊八粥香漫过山门，岁末的暖意也随之而来。邀你与道友同坐片刻，分享平安和祝福。"
  }
};
const newFestivalIds = Object.keys(festivalEvents).filter(id => id !== "midautumn");
const solarTermsAddedInV3 = ["spring-equinox", "summer-solstice", "autumn-equinox"];
function makeFestivalMail(id) {
  const event = festivalEvents[id];
  return { id, category: "event", title: event.title, sender: "仙盟司礼", date: "节日演示", expires: "7 天后到期",
    read: false, claimed: false, expired: false, festival: id,
    paragraphs: ["亲爱的道友：", event.letter,
      `随信奉上<strong>${event.gift}</strong>，愿道友修行顺遂。前往节日雅集，还可体验${event.activities.join("、")}。`,
      "请在邮件到期前领取附件，莫让这份心意久候。"], signature: "仙盟司礼 敬上",
    rewards: [{name:event.gift,count:1,icon:"icon-chest.png"},{name:"祈福符",count:3,icon:"icon-talisman.png"}] };
}
const seedMails = [
  { id: "midautumn", category: "event", title: "月满仙山 · 玉兔送福", sender: "仙盟司礼", date: "09-14 10:00", expires: "6 天后到期", read: false, claimed: false, expired: false, festival: "midautumn",
    paragraphs: ["亲爱的道友：", "桂香入云，月满仙山。中秋雅集已备好花灯与团圆好礼，邀你与道友共赏明月。", "随信奉上<strong>玉兔团圆礼</strong>，愿道友修行顺遂，所行皆有良伴。前往雅集，还可体验月下祈福、花灯游园与玉兔寻宝。", "请在邮件到期前领取附件，莫让这份心意久候。"], signature: "仙盟司礼 敬上",
    rewards: [{name:"灵玉",count:200,icon:"round_badge_lotus.png"},{name:"修行丹",count:10,icon:"icon-pill.png"},{name:"祈福符",count:5,icon:"icon-talisman.png"},{name:"团圆礼匣",count:1,icon:"icon-chest.png"}] },
  ...newFestivalIds.map(makeFestivalMail),
  { id: "maintenance", category: "system", title: "维护补偿，请道友查收", sender: "仙盟总管", date: "09-14 08:30", expires: "6 天后到期", read: false, claimed: false, expired: false,
    paragraphs: ["亲爱的道友：", "仙境例行维护已经结束。感谢道友的耐心等候，随信奉上维护补偿，请在有效期内领取。", "本次维护优化了部分界面的显示与操作体验。愿道友重返仙境，一路顺遂。", "<div class=\"body-bullet\">维护补偿：灵玉 × 100、修行丹 × 5。</div>", "如有未尽之处，也欢迎道友继续提出宝贵意见。"], signature: "仙盟总管 敬上",
    rewards: [{name:"灵玉",count:100,icon:"round_badge_lotus.png"},{name:"修行丹",count:5,icon:"icon-pill.png"}] },
  { id: "notice", category: "system", title: "仙境来信 · 游历小记", sender: "云游道人", date: "09-13 18:00", expires: "5 天后到期", read: false, claimed: false, expired: false,
    paragraphs: ["道友，见信如晤：", "秋风已过山门，桂花渐次开放。行经荷池、石桥与青玉道观时，不妨驻足片刻，看看仙山新景。", "这封信仅为游历提醒，不附带奖励。愿道友行有所获，心有所安。", "修行有时，闲游亦有所得。待下次云海相逢，再与你共饮一壶清茶。"], signature:"云游道人 手书",rewards:[] },
  { id: "adventure", category: "reward", title: "云游试炼 · 通关奖励", sender: "试炼执事", date: "09-13 12:20", expires: "5 天后到期", read: false, claimed: false, expired: false,
    paragraphs: ["道友，恭喜通关！", "你已完成本轮云游试炼。随信奉上历练奖励，感谢你守护仙山的安宁。", "请查收附件，休整片刻，再赴下一程山海。"], signature:"试炼执事 敬上",
    rewards:[{name:"修行丹",count:20,icon:"icon-pill.png"},{name:"云游卷",count:3,icon:"icon-scroll.png"}] },
  { id: "claimed", category: "reward", title: "初入仙山 · 修行见礼", sender: "接引道童", date: "09-12 09:00", expires: "4 天后到期", read: true, claimed: true, expired: false,
    paragraphs: ["道友，欢迎来到五行仙境：", "这份入门小礼愿能伴你踏上修行之路。修行丹助你增长见闻，祈福符愿你逢凶化吉。", "随信奖励已领取，愿道友心怀善念，自在云游。"], signature:"接引道童 敬上",
    rewards:[{name:"修行丹",count:10,icon:"icon-pill.png"},{name:"祈福符",count:2,icon:"icon-talisman.png"}] },
  { id: "expired", category: "event", title: "花灯夜游 · 上期赠礼", sender: "仙盟司礼", date: "09-06 19:00", expires: "已于 09-13 到期", read: true, claimed: false, expired: true,
    paragraphs: ["亲爱的道友：", "上期花灯夜游已经落幕。愿暖灯长明，映照道友的修行归途。", "本邮件已超过领取期限，随信附件已失效，无法继续领取。期待下一次雅集与你再会。"], signature:"仙盟司礼 敬上",
    rewards:[{name:"花灯礼匣",count:1,icon:"icon-chest.png"},{name:"祈福符",count:3,icon:"icon-talisman.png"}] }
];
const categoryNames = { all: "全部", system: "系统", event: "活动", reward: "奖励" };
const categoryIcons = { system: "icon-scroll.png", event: "round_badge_taiji.png", reward: "icon-chest.png" };
const cloneSeed = () => JSON.parse(JSON.stringify(seedMails));
let state = { mails: cloneSeed(), selectedId: "midautumn", category: "all" };
let toastTimer;
let eventReturnFocus;

function readSavedState() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (!saved || ![1, 2, STORAGE_VERSION].includes(saved.version) || !Array.isArray(saved.items)) return;
    const savedItems = new Map(saved.items.map(item => [item.id, item]));
    // Keep previously deleted mail deleted. Only add festivals absent from an older version.
    const addedFestivalIds = saved.version === 1 ? newFestivalIds :
      saved.version === 2 ? solarTermsAddedInV3 : [];
    state.mails = cloneSeed().filter(mail => savedItems.has(mail.id) ||
      addedFestivalIds.includes(mail.id)).map(mail => {
      const item = savedItems.get(mail.id);
      return item ? { ...mail, read: item.read === true, claimed: item.claimed === true && mail.rewards.length > 0 } : mail;
    });
    state.category = Object.hasOwn(categoryNames, saved.category) ? saved.category : "all";
    state.selectedId = saved.selectedId;
  } catch { /* A blocked or stale local store simply starts a fresh preview. */ }
}

function saveState() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ version: STORAGE_VERSION, category: state.category, selectedId: state.selectedId,
      items: state.mails.map(({id, read, claimed}) => ({id, read, claimed})) }));
  } catch { /* The preview remains usable when local storage is unavailable. */ }
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[char]));
}
function canClaim(mail) { return Boolean(mail && mail.rewards.length && !mail.claimed && !mail.expired); }
function visibleMails() { return state.mails.filter(mail => state.category === "all" || mail.category === state.category); }
function selectedMail() { return state.mails.find(mail => mail.id === state.selectedId); }
function ensureSelection(markRead = true) {
  const visible = visibleMails();
  if (!visible.some(mail => mail.id === state.selectedId)) state.selectedId = visible[0]?.id || null;
  if (markRead && selectedMail()) selectedMail().read = true;
}
function showToast(message) {
  const toast = document.getElementById("toast");
  clearTimeout(toastTimer);
  toast.textContent = message;
  toast.hidden = false;
  toastTimer = setTimeout(() => { toast.hidden = true; }, 4000);
}
function claimState(mail) {
  if (mail.expired) return { label: "已过期", className: "expired" };
  if (mail.claimed) return { label: "✓ 已领取", className: "claimed" };
  if (mail.rewards.length) return { label: "待领取", className: "pending" };
  return { label: "无附件", className: "notice" };
}

function renderList() {
  const list = document.getElementById("mail-list");
  const rows = visibleMails();
  const oldScroll = list.scrollTop;
  list.innerHTML = rows.length ? rows.map(mail => {
    const status = claimState(mail);
    const isSelected = mail.id === state.selectedId;
    return `<button type="button" class="mail-row${isSelected ? " is-selected" : ""}${mail.read ? " is-read" : ""}${mail.expired ? " is-expired" : ""}" data-mail-id="${mail.id}" aria-pressed="${isSelected}" aria-label="${escapeHtml(mail.title)}，${mail.read ? "已读" : "未读"}，${status.label.replace("✓ ", "")}">
      <span class="mail-row-icon"><img src="assets/${categoryIcons[mail.category]}" alt="">${!mail.read ? "<span class=\"unread-dot\" aria-hidden=\"true\"></span>" : ""}</span>
      <span class="mail-row-title"><span class="text">${escapeHtml(mail.title)}</span></span>
      <span class="mail-row-subline"><span>${mail.date.slice(0,5)}</span><span class="mail-row-tag">${categoryNames[mail.category]}</span><span class="mail-row-state ${status.className}">${status.label}</span></span>
    </button>`;
  }).join("") : `<div class="empty-list"><img src="assets/round_badge_taiji.png" alt=""><p>暂无${state.category === "all" ? "" : categoryNames[state.category]}邮件</p></div>`;
  list.scrollTop = oldScroll;
  document.getElementById("all-count").textContent = state.mails.length;
  document.getElementById("inbox-count").textContent = `${rows.length} 封${state.category === "all" ? "邮件" : categoryNames[state.category] + "邮件"}`;
  const unread = state.mails.filter(mail => !mail.read).length;
  const pending = state.mails.filter(canClaim).length;
  document.getElementById("mail-summary").innerHTML = `未读 <strong>${unread}</strong> 封<span aria-hidden="true">　·　</span>待领 <strong>${pending}</strong> 封`;
  document.getElementById("claim-all").disabled = pending === 0;
  document.getElementById("clean-read").disabled = !state.mails.some(mail => mail.read && !canClaim(mail));
  document.querySelectorAll("[data-category]").forEach(button => {
    const active = button.dataset.category === state.category;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", active);
  });
}

function renderDetail() {
  const detail = document.getElementById("mail-detail");
  const mail = selectedMail();
  if (!mail) {
    detail.innerHTML = `<div class="empty-detail"><img src="assets/round_badge_taiji.png" alt=""><h2>云中无新笺</h2><p>道友，暂时没有需要查收的邮件。</p></div>`;
    return;
  }
  const status = claimState(mail);
  const festival = festivalEvents[mail.festival];
  const banner = festival ? `<figure class="event-banner ${festival.tone === "dark" ? "is-dark" : "is-light"}"><img src="assets/${festival.image}" alt="${escapeHtml(festival.alt)}"><figcaption class="banner-label"><p class="kicker">${escapeHtml(festival.kicker)}</p><h3>${festival.lines.map(escapeHtml).join("<br>")}</h3><p>${escapeHtml(festival.tagline)}</p></figcaption></figure>` : "";
  const rewards = mail.rewards.length ? `<div class="attachments" aria-label="邮件附件">${mail.rewards.map(reward => `<div class="reward ${status.className}" tabindex="0" role="img" aria-label="${reward.name} ${reward.count} 个${mail.claimed ? "，已领取" : mail.expired ? "，已失效" : ""}" title="${reward.name} × ${reward.count}${mail.claimed ? " · 已领取" : mail.expired ? " · 已失效" : ""}"><img src="assets/${reward.icon}" alt=""><span class="reward-count">${reward.count}</span><span class="reward-name">${reward.name}</span></div>`).join("")}</div>` : `<div class="no-attachments"><img src="assets/notice_icon.png" alt=""><span>这是一封通知邮件，没有附件。</span></div>`;
  const claimButton = mail.rewards.length ? `<button id="claim-mail" type="button" class="button primary" ${canClaim(mail) ? "" : "disabled"}>${mail.expired ? "已过期" : mail.claimed ? "✓ 已领取" : "领取附件"}</button>` : "";
  detail.innerHTML = `<header class="detail-header"><button class="mail-back" id="back-to-list" type="button">‹ 返回收件箱</button><div class="detail-heading"><h2 id="detail-title">${escapeHtml(mail.title)}</h2><p class="detail-meta"><span>寄件人：${escapeHtml(mail.sender)}</span><span>${mail.date}</span></p></div><span class="mail-status ${status.className}">${status.label}</span></header>
    <div class="mail-reader" tabindex="0" aria-label="邮件正文，可滚动">${banner}<div class="mail-copy">${!festival ? '<img class="text-seal" src="assets/round_badge_taiji.png" alt="">' : ""}${mail.paragraphs.map((p,index) => p.startsWith("<div") ? p : `<p${index === 0 ? ' class="salutation"' : ""}>${p}</p>`).join("")}<p class="signature">${mail.signature}</p></div></div>
    <footer class="detail-footer"><div class="attachment-heading"><h3>${mail.rewards.length ? "随信好礼" : "仙笺寄语"}</h3><p>${mail.expired ? "附件已失效 · " : ""}${mail.expires}</p></div><div class="attachment-and-actions">${rewards}<div class="detail-actions"><button id="delete-mail" class="delete-mail" type="button" aria-label="删除当前邮件" title="${canClaim(mail) ? "请先领取有效附件，再删除邮件" : "删除当前邮件"}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M9 6V3h6v3M6 6l1 15h10l1-15M10 10v7M14 10v7"></path></svg></button>${festival && !mail.expired ? '<button id="open-event" class="button secondary" type="button">前往活动</button>' : ""}${claimButton}</div></div></footer>`;
  detail.dataset.currentMail = mail.id;
  document.getElementById("footer-note").textContent = mail.expired ? "邮件已过期，附件无法领取。道友可删除此封邮件。" : canClaim(mail) ? "查看邮件不会自动领取，记得在到期前领取附件。" : "附件领取后将保留邮件，可通过「清理已读」整理收件箱。";
}

function render() { renderList(); renderDetail(); saveState(); }
function selectMail(id, mobile = false) {
  const mail = state.mails.find(item => item.id === id);
  if (!mail) return;
  state.selectedId = id;
  mail.read = true;
  if (mobile) document.querySelector(".mail-window").classList.add("mobile-detail");
  render();
  if (mobile) document.getElementById("back-to-list").focus({preventScroll:true});
  else document.querySelector(`[data-mail-id="${id}"]`)?.focus({preventScroll:true});
}
function claimOne() {
  const mail = selectedMail();
  if (!canClaim(mail)) return;
  mail.claimed = true;
  render();
  showToast(`已领取「${mail.title}」的 ${mail.rewards.length} 项附件`);
}
function claimAll() {
  const eligible = state.mails.filter(canClaim);
  if (!eligible.length) return showToast("暂时没有可领取的附件");
  eligible.forEach(mail => { mail.claimed = true; });
  render();
  showToast(`已领取 ${eligible.length} 封邮件，共 ${eligible.reduce((sum, mail) => sum + mail.rewards.length, 0)} 项附件`);
}
function deleteCurrent() {
  const mail = selectedMail();
  if (!mail) return;
  if (canClaim(mail)) return showToast("这封邮件还有可领取的附件，请先领取再删除");
  state.mails = state.mails.filter(item => item.id !== mail.id);
  ensureSelection();
  render();
  showToast("已删除这封邮件");
}
function cleanRead() {
  const removable = state.mails.filter(mail => mail.read && !canClaim(mail));
  if (!removable.length) return showToast("没有可清理的已读邮件，待领附件会保留");
  state.mails = state.mails.filter(mail => !removable.includes(mail));
  ensureSelection();
  render();
  showToast(`已清理 ${removable.length} 封已读邮件，含有效待领附件的邮件已保留`);
}

function openFestivalDialog(mail, returnFocus) {
  const festival = festivalEvents[mail?.festival];
  if (!festival) return;
  const dialog = document.getElementById("event-dialog");
  const art = dialog.querySelector(".event-dialog-art");
  art.src = `assets/${festival.image}`;
  art.alt = festival.alt;
  dialog.querySelector(".event-kicker").textContent = festival.kicker.replaceAll(" ", "");
  dialog.querySelector("#event-title").textContent = festival.title;
  dialog.querySelector("#event-intro").textContent = festival.intro;
  dialog.querySelector(".event-activities").replaceChildren(...festival.activities.map(activity => {
    const label = document.createElement("span");
    label.textContent = activity;
    return label;
  }));
  eventReturnFocus = returnFocus;
  dialog.showModal();
}

document.getElementById("mail-list").addEventListener("click", event => {
  const row = event.target.closest("[data-mail-id]");
  if (row) selectMail(row.dataset.mailId, window.innerWidth <= 900);
});
document.querySelector(".categories").addEventListener("click", event => {
  const button = event.target.closest("[data-category]");
  if (!button) return;
  state.category = button.dataset.category;
  ensureSelection(window.innerWidth > 900);
  document.querySelector(".mail-window").classList.remove("mobile-detail");
  render();
});
document.getElementById("mail-detail").addEventListener("click", event => {
  const button = event.target.closest("button");
  if (!button || button.disabled) return;
  if (button.id === "claim-mail") claimOne();
  if (button.id === "delete-mail") deleteCurrent();
  if (button.id === "back-to-list") document.querySelector(".mail-window").classList.remove("mobile-detail");
  if (button.id === "open-event") openFestivalDialog(selectedMail(), button);
});
document.getElementById("claim-all").addEventListener("click", claimAll);
document.getElementById("clean-read").addEventListener("click", cleanRead);
document.getElementById("reset-demo").addEventListener("click", () => {
  state = { mails: cloneSeed(), selectedId: "midautumn", category: "all" };
  ensureSelection(window.innerWidth > 900);
  document.querySelector(".mail-window").classList.remove("mobile-detail");
  document.getElementById("event-dialog").close();
  document.getElementById("reopen-panel").hidden = true;
  document.querySelector(".mail-window").hidden = false;
  render();
  showToast("已恢复初始演示邮件");
});
document.getElementById("close-mail").addEventListener("click", () => {
  document.querySelector(".mail-window").hidden = true;
  document.getElementById("reopen-panel").hidden = false;
  document.getElementById("reopen-mail").focus();
});
document.getElementById("reopen-mail").addEventListener("click", () => {
  document.querySelector(".mail-window").hidden = false;
  document.getElementById("reopen-panel").hidden = true;
  document.getElementById("close-mail").focus();
});
document.querySelectorAll("[data-close-dialog]").forEach(button => button.addEventListener("click", () => document.getElementById("event-dialog").close()));
document.getElementById("event-dialog").addEventListener("close", () => eventReturnFocus?.isConnected && eventReturnFocus.focus());
document.getElementById("event-dialog").addEventListener("click", event => {
  if (event.target !== event.currentTarget) return;
  const box = event.currentTarget.getBoundingClientRect();
  if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) event.currentTarget.close();
});
function fitStage() {
  if (window.innerWidth <= 900) return;
  const scale = Math.min(window.innerWidth / 2560, window.innerHeight / 1080);
  document.getElementById("stage").style.transform = `translate(-50%,-50%) scale(${scale})`;
}
window.addEventListener("resize", fitStage);
readSavedState();
ensureSelection(window.innerWidth > 900);
render();
fitStage();
