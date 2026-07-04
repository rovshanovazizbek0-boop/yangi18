import "dotenv/config";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { fetchLatestNews } from "./feeds.js";
import { analyzeAll } from "./analyzer.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(here, "..", "data");
const OUTPUT_FILE = path.join(DATA_DIR, "tahlillar.json");

async function main() {
  console.log("📡 AI yangiliklari yig'ilmoqda...");
  const news = await fetchLatestNews(3);
  console.log(`   ${news.length} ta yangilik topildi.\n`);

  if (news.length === 0) {
    console.error("Hech qanday yangilik topilmadi. Internet aloqasini tekshiring.");
    process.exit(1);
  }

  console.log("🤖 Claude yordamida tahlil qilinmoqda...");
  const analyses = await analyzeAll(news, {
    onProgress: (current, total, title) =>
      console.log(`  [${current}/${total}] ${title.slice(0, 70)}`),
  });

  fs.mkdirSync(DATA_DIR, { recursive: true });
  const output = {
    yangilangan_vaqt: new Date().toISOString(),
    tahlillar: analyses,
  };
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2), "utf8");

  console.log(`\n✅ ${analyses.length} ta tahlil saqlandi: ${OUTPUT_FILE}`);
  console.log("   Natijalarni ko'rish uchun: npm run serve");
}

main().catch((error) => {
  console.error("Xatolik:", error.message);
  process.exit(1);
});
