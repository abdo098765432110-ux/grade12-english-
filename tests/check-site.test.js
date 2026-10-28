/* Tests for tools/check-site.js — run with: node --test tests/*.test.js
   Builds small throw-away copies of the site in a temporary folder. */
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const PROJECT = path.join(__dirname, '..');
const CHECKER = path.join(PROJECT, 'tools', 'check-site.js');
/* Website files: the pages, .nojekyll, and every .css, .js, .json and .svg
   file at the top level (there are no css, js, data or image folders). */
const SITE_ITEMS = fs.readdirSync(PROJECT).filter((name) =>
  /\.(html|css|js|json|svg)$/.test(name) || name === '.nojekyll');

function copySite(skip) {
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'g12-site-'));
  SITE_ITEMS.filter((item) => !(skip || []).includes(item)).forEach((item) => {
    fs.cpSync(path.join(PROJECT, item), path.join(folder, item), { recursive: true });
  });
  return folder;
}

function check(folder) {
  const run = spawnSync(process.execPath, [CHECKER, folder], { encoding: 'utf8' });
  return { code: run.status, out: run.stdout + run.stderr };
}

test('the project itself passes', () => {
  const result = check(PROJECT);
  assert.equal(result.code, 0, result.out);
  assert.match(result.out, /Result: OK/);
});

test('missing website files are reported (files not uploaded next to index.html)', () => {
  const result = check(copySite(['style.css', 'i18n-ar.js', 'common.js', 'units.json']));
  assert.equal(result.code, 1);
  assert.match(result.out, /index\.html: "style\.css" was not found/);
  assert.match(result.out, /index\.html: "i18n-ar\.js" was not found/);
  assert.match(result.out, /index\.html: "common\.js" was not found/);
  assert.match(result.out, /"units\.json" was not found/);
});

test('old css, js and data folders are reported as unused', () => {
  const folder = copySite();
  ['css', 'js', 'data'].forEach((name) => {
    fs.mkdirSync(path.join(folder, name));
    fs.writeFileSync(path.join(folder, name, 'old-copy.txt'), 'old');
  });
  const result = check(folder);
  assert.equal(result.code, 0, result.out);
  assert.match(result.out, /The "js" folder is not used by this version of the website/);
  assert.match(result.out, /The "data" folder is not used/);
});

test('a file name with different upper/lower case is reported', () => {
  const folder = copySite();
  fs.renameSync(path.join(folder, 'style.css'), path.join(folder, 'Style.css'));
  const result = check(folder);
  assert.equal(result.code, 1);
  assert.match(result.out, /"style\.css" has different upper\/lower case from the file on disk \("Style\.css"\)/);
  assert.match(result.out, /Style\.css has capital letters/);
});

test('absolute paths and full site addresses are reported', () => {
  const folder = copySite();
  const page = path.join(folder, 'index.html');
  let html = fs.readFileSync(page, 'utf8');
  html = html.replace('href="style.css"', 'href="/style.css"');
  html = html.replace('href="grammar.html"', 'href="https://someone.github.io/grade12-english/grammar.html"');
  fs.writeFileSync(page, html);
  const result = check(folder);
  assert.equal(result.code, 1);
  assert.match(result.out, /"\/style\.css" starts with "\/"/);
  assert.match(result.out, /uses the full site address/);
});

test('a missing data file is reported', () => {
  const folder = copySite();
  fs.rmSync(path.join(folder, 'reading-passages.json'));
  const result = check(folder);
  assert.equal(result.code, 1);
  assert.match(result.out, /"reading-passages\.json" was not found/);
});
