import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, normalize, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const ignoredDirectories = new Set([".git", "deploy", "scripts"]);
const errors = [];

function collectHtml(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    if (entry.name.startsWith(".") || ignoredDirectories.has(entry.name)) return [];
    const path = join(directory, entry.name);
    if (entry.isDirectory()) return collectHtml(path);
    return entry.name.endsWith(".html") ? [path] : [];
  });
}

function localTarget(from, raw) {
  const value = raw.split("#", 1)[0].split("?", 1)[0];
  if (!value || /^(?:https?:|mailto:|tel:|data:)/i.test(value)) return null;
  const decoded = decodeURIComponent(value);
  const candidate = decoded.startsWith("/")
    ? join(root, decoded.slice(1))
    : resolve(dirname(from), decoded);
  return normalize(candidate);
}

for (const file of collectHtml(root)) {
  const html = readFileSync(file, "utf8");
  const label = relative(root, file);
  for (const [pattern, message] of [
    [/<html\s+lang="[^"]+"/i, "missing document language"],
    [/<meta\s+name="viewport"/i, "missing viewport"],
    [/<meta\s+name="description"/i, "missing description"],
    [/<title>[^<]+<\/title>/i, "missing title"],
  ]) {
    if (!pattern.test(html)) errors.push(`${label}: ${message}`);
  }

  if (/Design preview|href="#"|albertkytytzov-cyber\.github\.io\/open-music-player-support/i.test(html)) {
    errors.push(`${label}: contains preview, empty, or legacy production text`);
  }

  for (const match of html.matchAll(/\b(?:href|src)="([^"]+)"/gi)) {
    const target = localTarget(file, match[1]);
    if (!target) continue;
    let resolved = target;
    if (existsSync(resolved) && statSync(resolved).isDirectory()) resolved = join(resolved, "index.html");
    if (!existsSync(resolved) && !resolved.endsWith(".html") && !resolved.includes(".")) resolved += ".html";
    if (!existsSync(resolved)) errors.push(`${label}: missing local target ${match[1]}`);
  }

  for (const match of html.matchAll(/<script\s+type="application\/ld\+json">([\s\S]*?)<\/script>/gi)) {
    try { JSON.parse(match[1]); } catch (error) { errors.push(`${label}: invalid JSON-LD (${error.message})`); }
  }
}

for (const required of [
  "index.html", "support.html", "support-ru.html", "privacy.html",
  "privacy-ru.html", "press.html", "news/index.html", "news/launch.html",
  "news/version-1-2.html", "news/now-free.html", "404.html", "robots.txt", "sitemap.xml",
]) {
  if (!existsSync(join(root, required))) errors.push(`missing required file ${required}`);
}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}

console.log(`PASS: ${collectHtml(root).length} HTML pages and all local links validated.`);
