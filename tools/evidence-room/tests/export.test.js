"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const app = fs.readFileSync(path.join(__dirname, "../app.js"), "utf8");

async function exportMessages(input, sourceName = "fixture.json") {
  const listeners = new Map();
  let archive;
  const context = vm.createContext({
    Blob,
    document: {
      getElementById: id => ({
        addEventListener: (event, callback) => listeners.set(`${id}:${event}`, callback)
      }),
      createElement: tag => {
        assert.equal(tag, "a");
        return {click() {}};
      }
    },
    URL: {
      createObjectURL: blob => { archive = blob; return "blob:fixture"; },
      revokeObjectURL() {}
    },
    setTimeout() {}
  });
  vm.runInContext(app, context);
  // Exercise the actual JSON normalizer and export click handler.
  vm.runInContext(`records = jsonMessages(${JSON.stringify(input)}); sourceName = ${JSON.stringify(sourceName)};`, context);
  listeners.get("export:click")();
  return archive ? archive.text() : null;
}

test("export preserves timestamp and created_at values without date conversion", async () => {
  const html = await exportMessages({messages: [
    {role: "user", content: "First", timestamp: "2026-11-08T16:45:12.345+05:30"},
    {role: "assistant", content: "Second", created_at: "Original local time: 16:46"},
    {role: "system", content: "Third", timestamp: 0}
  ]});
  assert.ok(html.includes("<h2>USER #1 · 2026-11-08T16:45:12.345+05:30</h2>"));
  assert.ok(html.includes("<h2>ASSISTANT #2 · Original local time: 16:46</h2>"));
  assert.ok(html.includes("<h2>SYSTEM #3 · 0</h2>"));
});

test("timestamp keeps existing precedence over created_at", async () => {
  const html = await exportMessages({conversation: {messages: [
    {role: "user", text: "First", timestamp: "primary", created_at: "fallback"},
    {role: "tool", text: "Second", timestamp: null, created_at: "fallback"}
  ]}});
  assert.ok(html.includes("<h2>USER #1 · primary</h2>"));
  assert.ok(html.includes("<h2>TOOL #2 · fallback</h2>"));
});

test("missing and empty timestamps leave the export heading unchanged", async () => {
  const html = await exportMessages([
    {role: "user", content: "No timestamp"},
    {role: "assistant", content: "Empty timestamp", timestamp: "", created_at: "ignored"},
    "Plain text entry"
  ]);
  assert.ok(html.includes("<h2>USER #1</h2>"));
  assert.ok(html.includes("<h2>ASSISTANT #2</h2>"));
  assert.ok(html.includes("<h2>UNATTRIBUTED #3</h2>"));
  assert.ok(!html.includes(" · "));
});

test("untrusted timestamps, message text, and source names are HTML-escaped", async () => {
  const payload = '<script>"quoted" & \'single\'</script>';
  const escaped = "&lt;script&gt;&quot;quoted&quot; &amp; &#39;single&#39;&lt;/script&gt;";
  const html = await exportMessages([{role: "user", content: payload, timestamp: payload}], payload);
  assert.ok(html.includes(`<h2>USER #1 · ${escaped}</h2>`));
  assert.ok(html.includes(`<pre>${escaped}</pre>`));
  assert.ok(html.includes(`Source: ${escaped}.`));
  assert.ok(!html.includes("<script>"));
});

test("empty records do not produce an archive", async () => {
  assert.equal(await exportMessages([]), null);
});
