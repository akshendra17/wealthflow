import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  
  await page.goto('http://localhost:5173/upload', { waitUntil: 'networkidle0' });
  
  // Wait for the select button
  const trigger = await page.$('.select-trigger');
  if (trigger) {
    const text1 = await page.evaluate(el => el.textContent, trigger);
    console.log('Select trigger text BEFORE click:', text1);
    
    await trigger.click();
    
    // Wait for the dropdown options
    await page.waitForSelector('.select-option');
    const options = await page.$$('.select-option');
    console.log(`Found ${options.length} options`);
    
    if (options.length > 1) {
      // Click the second option (HDFC Bank)
      await options[1].click();
      
      // Give it a moment to re-render
      await new Promise(r => setTimeout(r, 500));
      
      const text2 = await page.evaluate(el => el.textContent, trigger);
      console.log('Select trigger text AFTER click:', text2);
    }
  } else {
    console.log('Could not find .select-trigger');
  }

  await browser.close();
})();
