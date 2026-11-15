// Kiểm tra khóa dịch (T-27e): khóa dùng trong code phải có ở vi.json và en.json; hai file phải cùng bộ khóa.
// Chạy: node scripts/check-i18n.mjs   (thêm --list để in các khóa tĩnh tìm được)
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../src/", import.meta.url));
const flatten = (obj, prefix = "") => Object.entries(obj).flatMap(([k, v]) =>
  typeof v === "object" && v !== null ? flatten(v, `${prefix}${k}.`) : [`${prefix}${k}`]);
const vi = new Set(flatten(JSON.parse(readFileSync(join(root, "lib/i18n/messages/vi.json"), "utf8"))));
const en = new Set(flatten(JSON.parse(readFileSync(join(root, "lib/i18n/messages/en.json"), "utf8"))));

const files = [];
const walk = (dir) => readdirSync(dir).forEach((name) => {
  const path = join(dir, name);
  if (statSync(path).isDirectory()) walk(path);
  else if (/\.(tsx?|ts)$/.test(name)) files.push(path);
});
walk(root);

const used = new Set();
const dynamic = new Set();
const keyRe = /\bt\(\s*["']([a-zA-Z0-9_.]+)["']/g;
const tplRe = /\bt\(\s*`([a-zA-Z0-9_.]+)\.\$\{/g;
const labelRe = /(?:labelKey|titleKey|key):\s*["']([a-z][a-zA-Z0-9]*\.[a-zA-Z0-9_.]+)["']/g;
for (const file of files) {
  const src = readFileSync(file, "utf8");
  for (const m of src.matchAll(keyRe)) used.add(m[1]);
  for (const m of src.matchAll(labelRe)) used.add(m[1]);
  for (const m of src.matchAll(tplRe)) dynamic.add(m[1]);
}
if (process.argv.includes("--list")) {
  console.log([...used].sort().join("\n"));
  console.log("-- dynamic prefixes --\n" + [...dynamic].sort().join("\n"));
  process.exit(0);
}
let errors = 0;
const report = (msg) => { errors += 1; console.error(msg); };
for (const key of used) {
  if (!vi.has(key)) report(`missing in vi.json: ${key}`);
  if (!en.has(key)) report(`missing in en.json: ${key}`);
}
for (const prefix of dynamic) {
  if (![...vi].some((k) => k.startsWith(`${prefix}.`))) report(`no keys for dynamic prefix in vi.json: ${prefix}.*`);
}
for (const key of vi) if (!en.has(key)) report(`in vi.json but not en.json: ${key}`);
for (const key of en) if (!vi.has(key)) report(`in en.json but not vi.json: ${key}`);
console.log(errors ? `\n${errors} problem(s)` : `OK: ${used.size} static keys, ${dynamic.size} dynamic prefixes, ${vi.size} entries`);
process.exit(errors ? 1 : 0);
