import assert from "node:assert/strict";
import test from "node:test";

import { serializeJsonLd } from "../lib/json-ld.mjs";

test("JSON-LD script yopuvchi tegini HTML sifatida chiqarmaydi", () => {
  const payload = { title: "Sinov </script><script>alert(1)</script>" };
  const serialized = serializeJsonLd(payload);

  assert.equal(serialized.includes("</script>"), false);
  assert.deepEqual(JSON.parse(serialized), payload);
});
