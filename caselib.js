// What the browser cases share. Not a case itself. The browser counterpart of caselib.py:
// starts the product ("the shop") on a scratch database, opens a page in Chromium, and runs the
// checks on the product and then on each wrong variant, which the checks must refuse.
// A wrong variant (L0002, L0019) is the same shop with one fault in the page: a function that
// runs in every page once the product has served it, changes it the way a wrong product would
// have written it, and returns true when it did. Nothing here reads the product's source.
// A missing browser fails the case; it never skips (L0001, L0012).
// The browser cases are all under general labels, so they name no page of any product: what
// they need to know about the one in front of them is in surface/NAME.json (L0024).
const { spawn } = require('child_process');
const fs = require('fs');
const net = require('net');
const os = require('os');
const path = require('path');

const label = (text) => text.split('#')[0].split(/\s+/).filter(Boolean).join(' ').toLowerCase();

// The surface of the product in front of the cases: the one SURFACE names, or the one label in
// product/LABELS that has a file in surface/. No product to find is a failure, not a skip.
function product() {
  const found = {};
  for (const file of fs.existsSync('surface') ? fs.readdirSync('surface').sort() : []) {
    if (file.endsWith('.json')) { const one = JSON.parse(fs.readFileSync(path.join('surface', file), 'utf8')); found[label(one.label)] = one; }
  }
  let name = process.env.SURFACE;
  if (name === undefined) {
    const declared = fs.existsSync(path.join('product', 'LABELS')) ? fs.readFileSync(path.join('product', 'LABELS'), 'utf8').split('\n').map(label) : [];
    const named = declared.filter((word) => word in found);
    if (named.length !== 1) {
      console.log('product/LABELS declares ' + named.length + ' labels that have a surface in surface/ (' + (Object.keys(found).join(', ') || 'none there')
        + '): there is no one product to put this case to');
      process.exit(1);
    }
    [name] = named;
  }
  if (!(label(name) in found)) { console.log("no surface/*.json is labelled '" + name + "'"); process.exit(1); }
  return found[label(name)];
}
const surface = product();
exports.surface = surface;

// The command line, as in caselib.py: no site-packages, and SHOP names another build.
// ./check runs the cases where the product is bytecode with no source (L0019, L0038).
const main = !fs.existsSync(surface.main) && fs.existsSync(surface.main + 'c') ? surface.main + 'c' : surface.main;
const COMMAND = ['-S', '-E', '-s', process.env.SHOP || main];

// A value in a surface file may say {today} for today's date, {today+20} for a day after it, and {80*W} for a letter repeated.
const value = (text) => String(text).replace(/\{today\}/g, new Date().toLocaleDateString('en-CA'))
  .replace(/\{today\+(\d+)\}/g, (_, days) => new Date(Date.now() + Number(days) * 864e5).toLocaleDateString('en-CA'))
  .replace(/\{(\d+)\*(.)\}/g, (_, times, letter) => letter.repeat(Number(times)));

function freePort() {
  return new Promise((resolve) => {
    const probe = net.createServer();
    probe.listen(0, '127.0.0.1', () => { const { port } = probe.address(); probe.close(() => resolve(port)); });
  });
}

exports.value = value;

// A fault that adds one style rule to every page.
exports.style = (css) => new Function('const sheet = document.createElement("style"); sheet.textContent = '
  + JSON.stringify(css) + '; document.head.appendChild(sheet); return true;');

async function attempt(browser, checks, fault) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'shop-'));
  const port = await freePort();
  const base = 'http://127.0.0.1:' + port;
  let shop = null;
  const start = async (args) => {
    if (shop) { const gone = new Promise((resolve) => shop.once('exit', resolve)); shop.kill(); await gone; }
    shop = spawn('python3', COMMAND.concat(['--db', path.join(dir, 'shop.db'), '--port', String(port)], args), { stdio: 'ignore' });
    for (let tries = 0; ; tries += 1) {
      try { await fetch(base + '/'); break; } catch (error) {
        if (tries > 50) throw new Error('the shop did not start');
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
    }
  };
  // What a surface file calls "posts": forms sent one after another, each of which the product
  // must accept, and between them the product started again with other arguments.
  const fill = async (posts) => {
    for (const post of posts) {
      if (!Array.isArray(post)) { await start(post.restart.map(value)); continue; }
      const [where, fields] = post;
      const pairs = (Array.isArray(fields) ? fields : Object.entries(fields)).map(([name, text]) => [name, value(text)]);
      const answer = await fetch(base + where, { method: 'POST', body: new URLSearchParams(pairs), redirect: 'manual' });
      if (answer.status !== 303) throw new Error('wrong: POST ' + where + ' answered ' + answer.status);
    }
  };
  const page = await browser.newPage({ bypassCSP: Boolean(fault) });
  page.setDefaultTimeout(5000);
  const seen = { checks: 0, acted: 0 };
  const expect = (condition, what) => { if (!condition) throw new Error('wrong: ' + what); seen.checks += 1; };
  try {
    if (fault) {
      await page.exposeFunction('faultActed', () => { seen.acted += 1; });
      await page.addInitScript('document.addEventListener("DOMContentLoaded", () => { if ((' + fault.toString() + ')()) window.faultActed(); });');
    }
    await start([]);
    await page.goto(base + '/');
    await checks(page, base, expect, fill);
    return seen;
  } catch (error) {
    await new Promise((resolve) => setTimeout(resolve, 50));  // let the last page's fault report in
    error.acted = seen.acted;
    throw error;
  } finally {
    await page.close();
    if (shop) shop.kill();
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
