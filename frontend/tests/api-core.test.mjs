import assert from "node:assert/strict";
import test from "node:test";

import { ApiError, fetchJson } from "../lib/api-core.mjs";

test("404 topilmagan resurs uchun null qaytaradi", async () => {
  const result = await fetchJson("https://api.test/missing", async () => ({
    ok: false,
    status: 404,
  }));
  assert.equal(result, null);
});

test("backend 5xx xatosi yashirilmaydi", async () => {
  await assert.rejects(
    fetchJson("https://api.test/news", async () => ({
      ok: false,
      status: 503,
      json: async () => ({ detail: "Vaqtinchalik xato" }),
    })),
    (error) => error instanceof ApiError && error.status === 503,
  );
});

test("tarmoq xatosi vaqtinchalik API xatosiga aylantiriladi", async () => {
  await assert.rejects(
    fetchJson("https://api.test/news", async () => {
      throw new Error("offline");
    }),
    (error) => error instanceof ApiError && error.status === 503,
  );
});
