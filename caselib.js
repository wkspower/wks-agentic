// What the browser cases share. Not a case itself. The browser counterpart of caselib.py:
// starts the shop on a scratch database, opens a page in Chromium, and runs the checks on
// the product and then on each wrong variant (L0002), which the checks must refuse.
// A missing browser fails the case; it never skips (L0001, L0012).
const { spawn } = require('child_process');
const fs = require('fs');
const net = require('net');
const os = require('os');
const path = require('path');

function freePort() {
  return new Promise((resolve) => {
    const probe = net.createServer();
    probe.listen(0, '127.0.0.1', () => { const { port } = probe.address(); probe.close(() => resolve(port)); });
  });
}

async function attempt(browser, product, checks) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'shop-'));
  const port = await freePort();
  const shop = spawn('python3', [path.join(product, 'petshop.py'), '--db', path.join(dir, 'shop.db'), '--port', String(port)],
    { stdio: 'ignore' });
  const base = 'http://127.0.0.1:' + port;
  const page = await browser.newPage();
  page.setDefaultTimeout(5000);
  let count = 0;
  const expect = (condition, what) => { if (!condition) throw new Error('wrong: ' + what); count += 1; };
  try {
    for (let tries = 0; ; tries += 1) {
      try { await page.goto(base + '/'); break; } catch (error) {
        if (tries > 50) throw new Error('the shop did not start');
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
    }
    await checks(page, base, expect);
    return count;
  } finally {
    await page.close();
    shop.kill();
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

exports.run = async function run(checks, wrong) {
  let browser;
  try {
    browser = await require('playwright').chromium.launch();
  } catch (error) {
    console.log('no browser to run the pages in: ' + error.message.split('\n')[0]);
    process.exit(1);
  }
  let code = 1;
  try {
    const passed = await attempt(browser, 'product', checks);
    if (!passed || !wrong.length) throw new Error(passed + ' checks and ' + wrong.length + ' wrong variants: nothing was measured');
    for (const [name, from, to] of wrong) {
      const work = fs.mkdtempSync(path.join(os.tmpdir(), 'wrong-'));
      try {
        const source = fs.readFileSync('product/petshop.py', 'utf8');
        const times = source.split(from).length - 1;
        if (times !== 1) throw new Error('wrong variant "' + name + '" cannot be applied: its text occurs ' + times + ' times in product/petshop.py');
        fs.writeFileSync(path.join(work, 'petshop.py'), source.replace(from, to));
        let caught = false;
        try { await attempt(browser, work, checks); } catch (error) { caught = true; }
        if (!caught) throw new Error('the case passes on a wrong variant: ' + name);
      } finally {
        fs.rmSync(work, { recursive: true, force: true });
      }
    }
    console.log(passed + ' checks passed in ' + browser.browserType().name() + ' ' + browser.version() + '; '
      + wrong.length + ' of ' + wrong.length + ' wrong variants refused');
    code = 0;
  } catch (error) {
    console.log(error.message.split('\n')[0]);
  } finally {
    await browser.close();
  }
  process.exit(code);
};
