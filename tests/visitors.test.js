/* The registration screen's rules (visitor.js) and its place in the website.
   Run: node --test tests/visitors.test.js  (also part of npm test) */
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.join(__dirname, '..');
const plain = (value) => JSON.parse(JSON.stringify(value));   // objects made inside the vm

/* Loads visitor.js as on founder.html (data-no-gate): only window.G12Visitors. */
function load(config) {
  const window = { G12_VISITORS: config || { url: '', key: '' }, console: { error() {} } };
  const context = {
    window, console: window.console, atob: (s) => Buffer.from(s, 'base64').toString('binary'),
    document: { currentScript: { hasAttribute: (name) => name === 'data-no-gate' } }
  };
  vm.runInNewContext(fs.readFileSync(path.join(root, 'visitor.js'), 'utf8'), context);
  return window.G12Visitors;
}

test('visitor.js: a full three-part Arabic name is required (the same rules as the database)', () => {
  const V = load();
  const ok = (raw) => V.nameProblem(V.cleanName(raw)) === '';
  ['أحمد محمد علي', 'سارة أحمد محمود السيد', 'محمد عبد الله حسن', '  مُحَمَّـد   عبد الله    حسن ', 'آية إبراهيم مصطفى', 'هدى علي حسن']
    .forEach((name) => assert.ok(ok(name), name));
  ['', '   ', 'أحمد', 'أحمد محمد', 'Ahmed Mohamed Ali', 'أحمد م علي', 'أحمد محمد 12', 'أحمد محمد علي٣', 'أحمد <b>محمد</b> علي', 'أحمد محمد @علي', 'أحمد '.repeat(20)]
    .forEach((name) => assert.ok(!ok(name), JSON.stringify(name)));
  assert.equal(V.cleanName('  مُحَمَّـد   عبد الله    حسن '), 'محمد عبد الله حسن');
  assert.match(V.nameProblem('أحمد محمد'), /ثلاثة أسماء/);
});

test('visitor.js: never uses a secret key; the public key goes in the apikey header', () => {
  assert.equal(load({ url: 'https://x.supabase.co', key: 'sb_secret_abc' }).config(), null);
  const jwt = (role) => 'eyJhbGciOiJIUzI1NiJ9.' + Buffer.from(JSON.stringify({ role })).toString('base64').replace(/=+$/, '') + '.sig';
  assert.equal(load({ url: 'https://x.supabase.co', key: jwt('service_role') }).config(), null);
  const V = load({ url: 'https://x.supabase.co/', key: 'sb_publishable_abc' });
  assert.deepEqual(plain(V.config()), { url: 'https://x.supabase.co', key: 'sb_publishable_abc' });
  assert.deepEqual(plain(V.headers(V.config())), { apikey: 'sb_publishable_abc', 'Content-Type': 'application/json' });
  assert.equal(V.headers(V.config(), 'user-token').Authorization, 'Bearer user-token');
  const legacy = load({ url: 'https://x.supabase.co', key: jwt('anon') });
  assert.ok(legacy.config(), 'the legacy anon key is allowed');
  assert.equal(load().config(), null, 'not set up: off');
});

test('visitor register: every page shows the screen (except the founder page), and no secret is in the website files', () => {
  const pages = fs.readdirSync(root).filter((f) => f.endsWith('.html'));
  pages.forEach((page) => {
    const html = fs.readFileSync(path.join(root, page), 'utf8');
    if (page === 'founder.html') {
      assert.ok(html.includes('<script src="visitor.js" data-no-gate></script>'), 'founder.html: no screen');
      assert.ok(html.includes('noindex'), 'founder.html is not indexed');
      return;
    }
    assert.ok(/<body[^>]*>\n  <script src="visitor-config.js"><\/script>\n  <script src="visitor.js"><\/script>/.test(html), page + ' loads the screen first');
  });
  const files = fs.readdirSync(root).filter((f) => /\.(js|html|json)$/.test(f));
  files.forEach((file) => {
    const text = fs.readFileSync(path.join(root, file), 'utf8');
    assert.ok(!/sb_secret_[A-Za-z0-9]/.test(text.replace(/"sb_secret_…"|\("sb_secret_…"\)|\/\^sb_secret_\/i/g, '')), file + ' has no secret key');
    assert.ok(!/service_role"?\s*[:=]\s*["']ey/.test(text), file + ' has no service_role key');
  });
});
