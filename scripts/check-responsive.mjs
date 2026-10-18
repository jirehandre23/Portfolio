import { createRequire } from 'node:module';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const require = createRequire(import.meta.url);
const {chromium, webkit} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base=process.env.PORTFOLIO_TEST_URL || 'http://127.0.0.1:9000';
fs.mkdirSync('/tmp/portfolio-screenshots',{recursive:true});
for(const [name,type,widths] of [['chromium',chromium,[320,375,390,430,768,1024,1440]],['webkit',webkit,[390,844]]]) {
 const browser=await type.launch({headless:true});
 for(const width of widths) {
  const context=await browser.newContext({viewport:{width,height:width===844?390:844},isMobile:width<=844,hasTouch:width<=844,reducedMotion:'reduce'});
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const path of ['/','/projects/creditlens/','/projects/fraudwatch/']) {
   await page.goto(base+path,{waitUntil:'networkidle'});
   if(path.includes('creditlens'))await page.locator('#exposure').filter({hasText:'$19.3M'}).waitFor();
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${name} ${width} ${path}: page overflow`);
   if(path==='/') {
    if(width<=600)for(const value of await page.locator('.hero-num-val').all()) assert.ok(await value.evaluate(e=>e.scrollWidth<=e.clientWidth+1),`Stat text overlaps at ${width}`);
    const toggle=page.locator('#hamburger');
    if(width<=1100) {
     await toggle.click();await page.locator('#mobileMenu.open').waitFor();
     assert.equal(await toggle.getAttribute('aria-expanded'),'true');
     assert.equal(await page.evaluate(()=>document.activeElement.textContent.trim()),'About');
     await page.keyboard.press('Escape');assert.equal(await toggle.getAttribute('aria-expanded'),'false');
     await toggle.click();await page.locator('#mobileMenu a[href="#projects"]').click();
     assert.equal(await toggle.getAttribute('aria-expanded'),'false');assert.ok(page.url().endsWith('#projects'));
     const rect=await page.locator('.astat-val').first().boundingBox();assert.ok(rect.x>=0 && rect.x+rect.width<=width+1);
     if(width<=768)assert.equal(await page.locator('.astat-val').first().evaluate(e=>getComputedStyle(e).textAlign),'left');
    }
    // Verify important links aren't merely hidden by body overflow clipping.
    for(const selector of ['.hero-actions a','.clink','.pcard']) {
     for(const link of await page.locator(selector).all()) {
      const box=await link.boundingBox();assert.ok(box.x>=-1&&box.x+box.width<=width+1,`${selector} clipped at ${width}`);
     }
    }
   }
   if(path.includes('creditlens')) {
    await page.getByRole('button',{name:'Moderate',exact:true}).click();assert.equal(await page.locator('#dscr').textContent(),'0.64×');
    assert.ok(await page.locator('.scroll').first().evaluate(e=>e.clientWidth<=innerWidth));
   }
   if(path.includes('fraudwatch')) {
    await page.locator('#demo-status').filter({hasText:'Ready'}).waitFor();
    await page.getByRole('button',{name:'Score transaction',exact:true}).click();
    assert.equal(await page.locator('#count').textContent(),'1');
    const routine=parseFloat(await page.locator('#latest-score').textContent());
    await page.getByRole('button',{name:'Unusual example',exact:true}).click();
    await page.getByRole('button',{name:'Score transaction',exact:true}).click();
    const unusual=parseFloat(await page.locator('#latest-score').textContent());
    assert.ok(unusual>routine,'Examples should yield different actual model scores');
    await page.getByRole('button',{name:'Confirmed fraud',exact:true}).click();
    assert.equal(await page.locator('#labeled').textContent(),'1');
    await page.getByRole('button',{name:'Load normal sample',exact:true}).click();
    assert.equal(await page.locator('#count').textContent(),'500');
    assert.equal(await page.locator('#labeled').textContent(),'0');
    await page.getByRole('button',{name:'Reveal sample labels',exact:true}).click();
    assert.equal(await page.locator('#labeled').textContent(),'500');
    await page.getByRole('button',{name:'Load shifted sample',exact:true}).click();
    assert.equal(await page.locator('#labeled').textContent(),'0');
    await page.getByRole('button',{name:'Reveal sample labels',exact:true}).click();
    assert.equal(await page.locator('#labeled').textContent(),'500');
    await page.getByRole('button',{name:'Clear session',exact:true}).click();
    assert.equal(await page.locator('#count').textContent(),'0');
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Fraud demo overflow');
   }
   if(width===390) {
    await page.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=600){scrollTo(0,y);await new Promise(r=>setTimeout(r,20));}scrollTo(0,0);});
    await page.screenshot({path:`/tmp/portfolio-screenshots/${name}-${path==='/'?'home':path.split('/')[2]}-${width}.png`,fullPage:true});
   }
  }
  assert.deepEqual(errors,[],`${name} ${width}: JavaScript errors`);
  console.log(`PASS ${name}: ${width}px, home + both projects, navigation and controls`);
  await context.close();
 }
 await browser.close();
}
