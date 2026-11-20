// What the browser cases share. Not a case itself. The browser counterpart of caselib.py:
// starts the shop on a scratch database, opens a page in Chromium, and runs the checks on
// the product and then on each wrong variant, which the checks must refuse.
// A wrong variant (L0002, L0019) is the same shop with one fault in the page: a function that
// runs in every page once the product has served it, changes it the way a wrong product would
// have written it, and returns true when it did. Nothing here reads the product's source.
// A missing browser fails the case; it never skips (L0001, L0012).
const { spawn } = require('child_process');
const fs = require('fs');
const net = require('net');
const os = require('os');
const path = require('path');

// The command line, as in caselib.py: no site-packages, and SHOP names another build.
const COMMAND = ['-S', '-E', '-s', process.env.SHOP || path.join('product', 'petshop.py')];

function freePort() {
  return new Promise((resolve) => {
    const probe = net.createServer();
    probe.listen(0, '127.0.0.1', () => { const { port } = probe.address(); probe.close(() => resolve(port)); });
  });
}

// A fault that adds one style rule to every page.
exports.style = (css) => new Function('const sheet = document.createElement("style"); sheet.textContent = '
  + JSON.stringify(css) + '; document.head.appendChild(sheet); return true;');

async function attempt(browser, checks, fault) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'shop-'));
  const port = await freePort();
  const shop = spawn('python3', COMMAND.concat(['--db', path.join(dir, 'shop.db'), '--port', String(port)]), { stdio: 'ignore' });
  const base = 'http://127.0.0.1:' + port;
  const page = await browser.newPage({ bypassCSP: Boolean(fault) });
  page.setDefaultTimeout(5000);
  const seen = { checks: 0, acted: 0 };
  const expect = (condition, what) => { if (!condition) throw new Error('wrong: ' + what); seen.checks += 1; };
  try {
    if (fault) {
      await page.exposeFunction('faultActed', () => { seen.acted += 1; });
      await page.addInitScript('document.addEventListener("DOMContentLoaded", () => { if ((' + fault.toString() + ')()) window.faultActed(); });');
    }
    for (let tries = 0; ; tries += 1) {
      try { await page.goto(base + '/'); break; } catch (error) {
        if (tries > 50) throw new Error('the shop did not start');
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
    }
    await checks(page, base, expect);
    return seen;
  } catch (error) {
    await new Promise((resolve) => setTimeout(resolve, 50));  // let the last page's fault report in
    error.acted = seen.acted;
    throw error;
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
    const passed = (await attempt(browser, checks)).checks;
    if (!passed || !wrong.length) throw new Error(passed + ' checks and ' + wrong.length + ' wrong variants: nothing was measured');
    let acted = 0;
    for (const [name, fault] of wrong) {
      let refused = null;
      try { await attempt(browser, checks, fault); } catch (error) { refused = error; }
      if (!refused) throw new Error('the case passes on a wrong variant: ' + name);
      if (!refused.acted) throw new Error('wrong variant "' + name + '" never acted, and the case failed on it anyway: ' + refused.message.split('\n')[0]);
      acted += refused.acted;
      console.log('refused "' + name + '": ' + refused.message.split('\n')[0]);
    }
    console.log(passed + ' checks passed in ' + browser.browserType().name() + ' ' + browser.version() + '; '
      + wrong.length + ' of ' + wrong.length + ' wrong variants refused, each after its fault acted (' + acted + ' acts)');
    code = 0;
  } catch (error) {
    console.log(error.message.split('\n')[0]);
  } finally {
    await browser.close();
  }
  process.exit(code);
};
