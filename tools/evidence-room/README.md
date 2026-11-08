# The Evidence Room

A tiny, offline-first conversation evidence viewer built with HTML and JavaScript. No dependencies, build step, login, server or network requests.

## Use

Download **both** `index.html` and `app.js` into the same folder. Open `index.html` in Firefox. Select a TXT/JSON file or paste text, search the visible entries, and export an offline-readable HTML snapshot.

**Formats:** JSON arrays of messages, `{ "messages": [...] }`, `{ "conversation": { "messages": [...] } }`; each message can have `role`/`sender` and `content`/`text`. TXT files recognize explicit line-start `USER:`, `ASSISTANT:`, `SYSTEM:`, `TOOL:` markers; other text is **UNATTRIBUTED**.

**Privacy:** The app runs locally in the browser. It never sends data to a network endpoint. Files are not persisted between page loads.

**Evidence limits:** This is a viewer, not an Atomic Chat database extractor. It cannot retrieve messages absent from an imported file, validate authenticity, or recover truncated context. HTML exports are readable snapshots, not restorable JSON backups. Source files should be preserved unchanged for auditing.

## Safety

All imported text is rendered using `textContent`; generated HTML escapes content. No imported markup or scripts are executed. The viewer imposes a 10 MB file-size limit.

Part of the [LFM 2 audit](../../audits/lfm2-700m/2026-11-08-behavior-and-context-audit.md).
