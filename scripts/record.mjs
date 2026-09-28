import { chromium } from 'playwright';
import { mkdir, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';

const configs = {
  hvac: { url: 'https://3dglobe.granpai.com/demo/hvac/', title: '9 locations. One interactive map.', caption: 'Find a branch. Explore the details.', cta: 'Explore the live demo' },
  timeline: { url: 'https://3dglobe.granpai.com/demo/timeline/', title: 'Watch your company grow.', caption: 'One pin for every milestone.', cta: 'See the Growth Timeline' },
  'global-impact': { url: 'https://3dglobe.granpai.com/demo/global-impact/', title: 'Every project, one scroll away.', caption: 'Explore locations in the sidebar.', cta: 'Explore the live demo' },
};
const wanted = process.env.DEMO || 'hvac';
if (wanted !== 'all' && !configs[wanted]) throw new Error(`Unknown demo: ${wanted}`);
await mkdir('output', { recursive: true });
const browser = await chromium.launch({ headless: true, args: ['--enable-webgl', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-dev-shm-usage'] });
try {
  for (const name of wanted === 'all' ? Object.keys(configs) : [wanted]) {
    const cfg = configs[name];
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1, recordVideo: { dir: 'output', size: { width: 1440, height: 900 } }, reducedMotion: 'no-preference' });
    const page = await context.newPage();
    const videoStarted = Date.now();
    page.on('console', msg => { if (msg.type() === 'error') console.log(`[browser] ${msg.text()}`); });
    try {
      await page.goto(cfg.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.locator('#live-demo').scrollIntoViewIfNeeded();
      await page.locator('.granpai-globe-wrapper').first().waitFor({ state: 'visible', timeout: 30000 });
      // Fail visibly if the interactive renderer never starts; a blank video is not a success.
      await page.locator('.granpai-globe-wrapper canvas').first().waitFor({ state: 'visible', timeout: 45000 });
      await page.waitForTimeout(2500);
      const globe = page.locator('.granpai-globe-wrapper').first();
      const box = await globe.boundingBox();
      if (!box) throw new Error('Globe has no visible bounds');
      await page.screenshot({ path: `output/${name}-check.png` });
      const trimSeconds = Math.max(0, (Date.now() - videoStarted) / 1000 - 0.5);
      await page.mouse.move(box.x + box.width * .58, box.y + box.height * .48);
      await page.waitForTimeout(2500);
      if (name === 'hvac') {
        const next = page.getByRole('button', { name: /next/i }).first();
        // Known visible pin positions for the North America camera, in viewport pixels.
        // Try multiple branches because auto-rotation may move markers a little.
        for (const [x, y] of [[1162, 406], [1112, 420], [1035, 448], [947, 393]]) {
          await page.mouse.click(x, y);
          await page.waitForTimeout(350);
          if (await next.isVisible().catch(() => false)) break;
        }
        if (!await next.isVisible().catch(() => false)) throw new Error('No HVAC pin modal opened');
        await page.waitForTimeout(1800);
        await next.click();
      } else if (name === 'timeline') {
        const play = page.getByRole('button', { name: /play/i }).first();
        if (await play.isVisible().catch(() => false)) await play.click();
      } else {
        const item = page.locator('[class*="sidebar"] [class*="item"]').filter({ visible: true }).first();
        if (await item.count()) await item.click({ timeout: 3000 }).catch(() => {});
      }
      await page.waitForTimeout(7000);
      await writeFile(`output/${name}.json`, JSON.stringify({ ...cfg, demo: name, trimSeconds }, null, 2));
      console.log(`Recorded ${name}; canvas ${box.width}x${box.height}`);
    } finally {
      const video = page.video();
      await context.close();
      if (video) await rename(await video.path(), path.resolve(`output/${name}.webm`));
    }
  }
} finally { await browser.close(); }
