import test from "node:test";
import assert from "node:assert/strict";
import { seoDescription } from "../lib/seo.mjs";

test("short descriptions are normalized without changing their meaning", () => {
  assert.equal(seoDescription("  Qisqa\n\nSEO   tavsif.  "), "Qisqa SEO tavsif.");
});

test("long descriptions are shortened on a word boundary", () => {
  const value = "OpenAI yangi imkoniyat taqdim etdi. ".repeat(12);
  const result = seoDescription(value, 120);

  assert.ok(result.length <= 121);
  assert.ok(result.endsWith("…"));
  assert.ok(!result.endsWith(" …"));
  assert.ok(value.includes(result.slice(0, -1)));
});
