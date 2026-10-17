/* Local-only design preview. catalog.json is the shared source for names, rules and numbers. */
(() => {
  "use strict";
  const storageKey = "wuxing.class-skills.preview.v2";
  const state = { classId: 1, skillId: 1101, category: "all", level: 68, gold: 120000, ranks: {} };
  let catalog;
  const $ = (selector) => document.querySelector(selector);
  const percent = (value) => `${Number((value * 100).toFixed(2))}%`;
  const poems = { 1: "一戈惊千嶂\n赤心守山河", 2: "玄符牵星汉\n九霄入掌中", 3: "一丹滋万象\n心定众生安", 4: "青羽先云起\n长风过九州" };
  const statNames = { defense: "防御", physicalAttack: "物伤", maxHp: "气血上限", magicAttack: "法伤", maxMp: "法力上限", outgoingHeal: "治疗量", speed: "速度", crit: "暴击率" };

  function persist() {
    try { localStorage.setItem(storageKey, JSON.stringify(state)); } catch { /* Preview also works without storage permission. */ }
  }
  function restore() {
    let saved;
    try { saved = JSON.parse(localStorage.getItem(storageKey)); } catch { saved = null; }
    for (const school of catalog.classes) {
      state.ranks[1000 + school.id * 100 + 1] = 1;
      state.ranks[1000 + school.id * 100 + 6] = 1;
    }
    if (!saved || typeof saved !== "object") return;
    if (catalog.classes.some((school) => school.id === saved.classId)) state.classId = saved.classId;
    state.level = Number.isFinite(saved.level) ? Math.max(1, Math.min(85, Math.floor(saved.level))) : 68;
    state.gold = Number.isFinite(saved.gold) ? Math.max(0, Math.min(99999999, Math.floor(saved.gold))) : 120000;
    for (const skill of catalog.skills) {
      const rank = Number(saved.ranks?.[skill.id]);
      if (Number.isInteger(rank) && rank >= 0 && rank <= skill.maxRank) state.ranks[skill.id] = rank;
    }
    state.skillId = catalog.skills.some((skill) => skill.id === saved.skillId && skill.classId === state.classId) ? saved.skillId : 1000 + state.classId * 100 + 1;
  }
  function rankOf(skill) { return state.ranks[skill.id] || 0; }
  function requirement(skill, nextRank) { return skill.unlockLevel + 2 * (nextRank - 1); }
  function costOf(skill, nextRank) { return 100 * nextRank * nextRank + skill.unlockLevel * 10; }
  function canUpgrade(skill) {
    const rank = rankOf(skill);
    return rank < skill.maxRank && state.level >= requirement(skill, rank + 1) && state.gold >= costOf(skill, rank + 1);
  }
  function targetLabel(skill) {
    if (skill.type === "passive" || skill.targetTeam === "self") return "自身";
    return `${skill.targetTeam === "enemy" ? "敌方" : "己方"}${skill.maxTargets}人`;
  }
  function scaledDescription(skill) {
    if (skill.type !== "passive") return skill.description;
    const value = skill.passivePercent * (1 + catalog.rules.rankPassiveGrowth * (Math.max(1, rankOf(skill)) - 1));
    return `常驻提升${Number((value * 100).toFixed(2))}${skill.passiveStat === "crit" ? "个百分点" : "%"}${statNames[skill.passiveStat]}。`;
  }
  function icon(skill, className = "") {
    return `<img class="${className}" src="${skill.iconPath}" alt="${skill.name}技能图标" width="256" height="256">`;
  }
  function renderClasses() {
    $("#class-list").innerHTML = catalog.classes.map((school) => `<button type="button" class="class-button${school.id === state.classId ? " selected" : ""}" data-class="${school.id}" aria-pressed="${school.id === state.classId}"><span>${school.name}</span><small>${school.role}</small></button>`).join("");
    const school = catalog.classes.find((item) => item.id === state.classId);
    $("#class-title").textContent = school.name;
    $("#class-subtitle").textContent = `${school.role} · ${school.theme}`;
    $("#school-poem").innerHTML = poems[school.id].split("\n").join("<br>");
    $("#learned-count").textContent = catalog.skills.filter((skill) => skill.classId === state.classId && rankOf(skill) > 0).length;
  }
  function renderList() {
    const visible = catalog.skills.filter((skill) => skill.classId === state.classId && (state.category === "all" || skill.type === state.category));
    if (!visible.some((skill) => skill.id === state.skillId)) state.skillId = visible[0].id;
    $("#skill-list").innerHTML = visible.map((skill) => {
      const rank = rankOf(skill);
      const locked = state.level < skill.unlockLevel;
      return `<button type="button" class="skill-row${state.skillId === skill.id ? " selected" : ""}${locked ? " locked" : ""}" data-skill="${skill.id}" aria-pressed="${state.skillId === skill.id}" aria-label="${skill.name}，${skill.category}，${rank}级${locked ? "，未解锁" : ""}">${icon(skill)}<span><span class="row-name">${skill.name}</span><span class="row-kind">${locked ? `${skill.unlockLevel}级解锁` : skill.type === "active" ? "主动术法" : "被动心法"}</span></span><span class="row-rank">${rank}<small> / ${skill.maxRank}</small></span><span class="row-meta">${skill.manaPercent ? `${percent(skill.manaPercent)}法力` : "无消耗"}<small>${targetLabel(skill)}</small></span></button>`;
    }).join("");
  }
  function renderDetail() {
    const skill = catalog.skills.find((item) => item.id === state.skillId);
    const rank = rankOf(skill);
    const factor = 1 + catalog.rules.rankDamageGrowth * (Math.max(1, rank) - 1);
    const nextRank = rank + 1;
    const maxed = rank >= skill.maxRank;
    let effect = "持续增益";
    if (skill.attackMultiplier) effect = `${Number((skill.attackMultiplier * factor * 100).toFixed(1))}%${skill.damageType === "magic" ? "法伤" : "物伤"}`;
    else if (skill.healMultiplier) effect = `${Number((skill.healMultiplier * factor * 100).toFixed(1))}%法伤 + ${Number((skill.healPerLevel * factor).toFixed(1))}×角色等级`;
    else if (skill.restoreManaPercent) effect = `回复${percent(skill.restoreManaPercent * factor)}法力`;
    else if (skill.type === "passive") effect = `提升${percent(skill.passivePercent * (1 + catalog.rules.rankPassiveGrowth * (Math.max(1, rank) - 1)))}${statNames[skill.passiveStat]}`;
    else if (skill.buffKind !== "none") effect = `${statNames[skill.buffKind]}${skill.buffPercent > 0 ? "+" : ""}${percent(skill.buffPercent * factor)}`;
    const needLevel = requirement(skill, nextRank);
    const price = costOf(skill, nextRank);
    $("#skill-detail").innerHTML = `<p class="detail-kicker">${skill.className} · ${skill.type === "active" ? "术法真传" : "内修心法"}</p>${icon(skill, "detail-art")}<h2>${skill.name}</h2><div class="detail-tags"><span class="detail-tag">${skill.category}</span><span class="detail-tag">${targetLabel(skill)}</span><span class="detail-tag">${rank ? `已修习 ${rank} 级` : "尚未修习"}</span></div><p class="detail-description">${scaledDescription(skill)}</p><dl class="detail-metrics"><div><dt>法力消耗</dt><dd>${skill.manaPercent ? `最大法力的 ${percent(skill.manaPercent)}` : "无"}</dd></div><div><dt>冷却回合</dt><dd>${skill.cooldownRounds ? `${skill.cooldownRounds} 回合` : "无"}</dd></div><div><dt>${skill.type === "passive" ? "常驻收益" : skill.healMultiplier ? "治疗基础" : "技能效果"}</dt><dd>${effect}</dd></div><div><dt>${skill.durationRounds ? "效果持续" : "初始解锁"}</dt><dd>${skill.durationRounds ? `${skill.durationRounds} 回合` : `角色 ${skill.unlockLevel} 级`}</dd></div></dl><div class="learning"><div class="learning-row"><span>修习条件</span><strong class="${!maxed && state.level < needLevel ? "insufficient" : ""}">${maxed ? "已臻圆满" : `角色 ${needLevel} 级 · 当前 ${state.level} 级`}</strong></div><div class="learning-row"><span>拥有金币</span><strong>${state.gold.toLocaleString("zh-CN")}</strong></div><div class="learning-row"><span>本次消耗</span><strong class="${!maxed && state.gold < price ? "insufficient" : ""}">${maxed ? "—" : `${price.toLocaleString("zh-CN")} 金币`}</strong></div><div class="detail-actions"><button class="button" id="upgrade-one" ${canUpgrade(skill) ? "" : "disabled"}>${maxed ? "已满级" : rank ? "修习一级" : "学习"}</button><button class="button secondary" id="upgrade-ten" ${canUpgrade(skill) ? "" : "disabled"}>连续修习</button></div></div>`;
  }
  function render() {
    renderClasses(); renderList(); renderDetail();
    document.querySelectorAll("[data-category]").forEach((button) => { const active = button.dataset.category === state.category; button.classList.toggle("selected", active); button.setAttribute("aria-pressed", String(active)); });
    $("#role-level").value = state.level;
    $("#role-gold").value = state.gold;
    persist();
  }
  function upgrade(count) {
    const skill = catalog.skills.find((item) => item.id === state.skillId);
    let upgraded = 0, spent = 0;
    while (upgraded < count && canUpgrade(skill)) {
      const nextRank = rankOf(skill) + 1;
      const cost = costOf(skill, nextRank);
      state.gold -= cost;
      spent += cost;
      state.ranks[skill.id] = nextRank;
      upgraded++;
    }
    render();
    $("#status-message").textContent = upgraded ? `${skill.name}已修习至${rankOf(skill)}级，消耗${spent.toLocaleString("zh-CN")}金币。` : "当前等级或金币未满足修习条件。";
  }
  function setScreen(overview) {
    $("#skills-screen").hidden = overview; $("#overview-screen").hidden = !overview;
    $("#show-skills").classList.toggle("selected", !overview); $("#show-skills").setAttribute("aria-pressed", String(!overview));
    $("#show-overview").classList.toggle("selected", overview); $("#show-overview").setAttribute("aria-pressed", String(overview));
  }
  function renderOverview() {
    $("#overview-grid").innerHTML = catalog.classes.map((school) => `<section class="overview-class"><header><h2>${school.name}</h2><p>${school.role} · ${school.theme}</p></header><div class="overview-icons">${catalog.skills.filter((skill) => skill.classId === school.id).map((skill) => `<button class="overview-item" data-overview-skill="${skill.id}" aria-label="查看${skill.name}详情">${icon(skill)}<h3>${skill.name}</h3><p>${skill.category} · ${skill.unlockLevel}级解锁</p></button>`).join("")}</div></section>`).join("");
  }
  async function init() {
    try {
      const response = await fetch("catalog.json");
      if (!response.ok) throw new Error(`Catalog HTTP ${response.status}`);
      catalog = await response.json();
      restore(); render(); renderOverview();
      if (location.hash === "overview") setScreen(true);
      $("#class-list").addEventListener("click", (event) => { const button = event.target.closest("[data-class]"); if (!button) return; state.classId = Number(button.dataset.class); state.skillId = 1000 + state.classId * 100 + 1; render(); });
      $("#skill-list").addEventListener("click", (event) => { const button = event.target.closest("[data-skill]"); if (!button) return; state.skillId = Number(button.dataset.skill); render(); $("[data-skill='" + state.skillId + "']").focus({ preventScroll: true }); });
      document.querySelectorAll("[data-category]").forEach((button) => button.addEventListener("click", () => { state.category = button.dataset.category; render(); }));
      $("#skill-detail").addEventListener("click", (event) => { if (event.target.closest("#upgrade-one")) upgrade(1); if (event.target.closest("#upgrade-ten")) upgrade(10); });
      $("#show-skills").addEventListener("click", () => { setScreen(false); history.replaceState(null, "", "#skills"); });
      $("#show-overview").addEventListener("click", () => { setScreen(true); history.replaceState(null, "", "#overview"); });
      $("#overview-grid").addEventListener("click", (event) => { const button = event.target.closest("[data-overview-skill]"); if (!button) return; const skill = catalog.skills.find((item) => item.id === Number(button.dataset.overviewSkill)); state.classId = skill.classId; state.skillId = skill.id; state.category = "all"; setScreen(false); render(); window.scrollTo({ top: 0, behavior: "auto" }); });
      $("#reset-demo").addEventListener("click", () => { try { localStorage.removeItem(storageKey); } catch {} state.ranks = {}; state.level = 68; state.gold = 120000; restore(); render(); $("#status-message").textContent = "本地演示已重置，各门派首式术法与首卷心法已学会。"; });
      $("#role-level").addEventListener("change", (event) => { state.level = Math.max(1, Math.min(85, Math.floor(Number(event.target.value) || 1))); render(); });
      $("#role-gold").addEventListener("change", (event) => { state.gold = Math.max(0, Math.min(99999999, Math.floor(Number(event.target.value) || 0))); render(); });
    } catch (error) {
      $("#status-message").textContent = "技能目录未能载入，请从本地 HTTP 预览地址打开页面。";
      console.error(error);
    }
  }
  init();
})();
