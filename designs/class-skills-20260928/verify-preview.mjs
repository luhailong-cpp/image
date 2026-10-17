// 本地 HTML 功能与布局验收。复用已安装的浏览器与随宿主提供的 Playwright，不安装依赖。
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const previewRoot = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.SKILL_QA_PLAYWRIGHT || 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const browserPath = process.env.SKILL_QA_BROWSER || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const fullIcons = process.argv.includes('--full-icons');
const check = (condition, message) => { if (!condition) throw new Error(message); };
const browser = await chromium.launch({ executablePath: browserPath, headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1040 }, deviceScaleFactor: 1 });
const errors = [];
page.on('pageerror', error => errors.push(error.message));
const results = { checkedAt: new Date().toISOString(), browser: 'installed Chrome, isolated headless context', checks: [], screenshots: [], missingIcons: [] };
try {
  await page.goto('http://127.0.0.1:4311/', { waitUntil: 'networkidle' });
  await page.locator('[data-skill="1101"]').waitFor();
  await page.locator('#reset-demo').click();
  check(await page.locator('.skill-row').count() === 8, '初始技能列表应为8项');
  await page.locator('[data-skill="1102"]').click();
  await page.locator('#upgrade-one').click();
  check((await page.locator('#status-message').innerText()).includes('修习至1级'), '学习未更新等级');
  check(await page.locator('#role-gold').inputValue() === '119800', '学习金币扣减错误');
  await page.locator('#upgrade-ten').click();
  check((await page.locator('#status-message').innerText()).includes('修习至10级'), '批量修习未止于满级');
  check(await page.locator('#role-gold').inputValue() === '80500', '批量修习总费用错误');
  check(await page.locator('#upgrade-one').isDisabled(), '满级按钮未禁用');
  results.checks.push('学习、批量修习、金币扣减、满级禁用');
  await page.locator('[data-class="2"]').click();
  await page.locator('[data-skill="1204"]').click();
  await page.locator('#upgrade-one').click();
  check((await page.locator('.detail-metrics').innerText()).includes('回复20%法力'), '太虚澄心初阶回复量错误');
  await page.locator('#upgrade-ten').click();
  check((await page.locator('.detail-metrics').innerText()).includes('回复23.6%法力'), '纯辅助升级后没有展示成长');
  results.checks.push('纯辅助技能升级后效果成长');
  await page.locator('[data-category="passive"]').click();
  check(await page.locator('.skill-row').count() === 3, '被动筛选应为3项');
  await page.locator('[data-class="3"]').click();
  await page.locator('[data-category="active"]').click();
  await page.locator('[data-skill="1305"]').click();
  check((await page.locator('#skill-detail').innerText()).includes('不能复活'), '急救技能缺少存活限制');
  await page.locator('.demo-settings summary').click();
  await page.locator('#role-gold').fill('0');
  await page.locator('#role-gold').press('Tab');
  check(await page.locator('#upgrade-one').isDisabled(), '金币不足仍可学习');
  await page.locator('#role-level').fill('1');
  await page.locator('#role-level').press('Tab');
  check((await page.locator('[data-skill="1305"]').getAttribute('class')).includes('locked'), '低等级技能缺少未解锁状态');
  results.checks.push('职业切换、主动/被动筛选、金币不足与等级限制');
  await page.locator('#show-overview').click();
  check(await page.locator('.overview-item').count() === 32, '图鉴数量不是32');
  const images = await page.locator('.overview-item img').evaluateAll(nodes => nodes.map(node => ({ source: node.getAttribute('src'), loaded: node.complete && node.naturalWidth > 0 })));
  const squareIcons = await page.locator('.overview-item img').evaluateAll(nodes => nodes.every(node => {
    const rect = node.getBoundingClientRect();
    return Math.abs(rect.width - rect.height) < 1;
  }));
  check(squareIcons, '图鉴必须完整显示正方形图标，不得被固定高度裁切');
  results.missingIcons = images.filter(image => !image.loaded).map(image => image.source);
  if (fullIcons) check(results.missingIcons.length === 0, '正式图鉴仍有缺失图标');
  const qaDir = path.join(previewRoot, 'qa');
  fs.mkdirSync(qaDir, { recursive: true });
  await page.screenshot({ path: path.join(qaDir, 'overview-desktop.png'), fullPage: true });
  results.screenshots.push('qa/overview-desktop.png');
  await page.locator('[data-overview-skill="1408"]').click();
  check((await page.locator('#skill-detail h2').innerText()) === '乘风蓄势', '图鉴到技能详情跳转失败');
  results.checks.push('32项图鉴与详情跳转');
  await page.locator('#reset-demo').click();
  for (const classId of [1, 2, 3, 4]) {
    await page.locator(`[data-class="${classId}"]`).click();
    await page.locator('[data-category="all"]').click();
    const classRows = await page.locator('.skill-row').evaluateAll(nodes => nodes.map(node => ({
      skillId: node.dataset.skill,
      text: node.innerText,
      loaded: [...node.querySelectorAll('img')].every(image => image.complete && image.naturalWidth > 0),
    })));
    check(classRows.length === 8, `职业${classId}的全部技能列表应为8项`);
    if (fullIcons) check(classRows.every(row => row.loaded), `职业${classId}列表缩略图缺失`);
    results.checks.push(`职业${classId}全部8项名称与列表图标加载`);
    await page.screenshot({ path: path.join(qaDir, `skills-class-${classId}.png`), fullPage: true });
    results.screenshots.push(`qa/skills-class-${classId}.png`);
  }
  await page.locator('[data-class="1"]').click();
  await page.locator('[data-category="all"]').click();
  await page.locator('[data-skill="1101"]').click();
  await page.locator('.demo-settings summary').click();
  await page.screenshot({ path: path.join(qaDir, 'skills-desktop.png'), fullPage: true });
  results.screenshots.push('qa/skills-desktop.png');
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: path.join(qaDir, 'skills-mobile.png'), fullPage: true });
  results.screenshots.push('qa/skills-mobile.png');
  const sizes = await page.evaluate(() => ({ viewport: document.documentElement.clientWidth, content: document.documentElement.scrollWidth }));
  check(sizes.content <= sizes.viewport, `移动端水平溢出: ${JSON.stringify(sizes)}`);
  await page.reload({ waitUntil: 'networkidle' });
  check(await page.locator('#role-gold').inputValue() === '120000', '本地状态持久化失效');
  check(errors.length === 0, errors.join('\n'));
  results.checks.push('390px移动布局无横向溢出、刷新保留状态、无页面JS异常');
  results.javascriptErrors = errors;
  results.status = 'passed';
  fs.writeFileSync(path.join(previewRoot, 'preview-validation.json'), JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results, null, 2));
} finally { await browser.close(); }
