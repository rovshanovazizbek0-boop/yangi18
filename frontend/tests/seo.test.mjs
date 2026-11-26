import test from "node:test";
import assert from "node:assert/strict";
import { seoDescription, seoTitle } from "../lib/seo.mjs";

test("short descriptions are normalized without changing their meaning", () => {
  assert.equal(seoDescription("  Qisqa\n\nSEO   tavsif.  "), "Qisqa SEO tavsif.");
});

test("long descriptions are shortened on a word boundary within limit", () => {
  const value = "OpenAI yangi imkoniyat taqdim etdi. ".repeat(12);
  const result = seoDescription(value, 120);

  assert.ok(result.length <= 120);
  assert.ok(result.endsWith("…"));
  assert.ok(!result.endsWith(" …"));
  assert.ok(value.includes(result.slice(0, -1)));
  assert.ok(seoDescription(value).length <= 155);
});

test("long titles fit within 65 chars with site suffix", () => {
  const value = "42 ta shtat bosh prokurorlari Character.AI platformasiga foydalanuvchilar chatlarini sotishni taqiqlashga harakat qilmoqda";
  const result = seoTitle(value);

  assert.ok(result.length <= 54);
  assert.ok(`${result} — AI Xabar`.length <= 65);
  assert.ok(result.endsWith("…"));
});
