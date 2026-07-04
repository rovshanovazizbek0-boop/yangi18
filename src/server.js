import "dotenv/config";
import express from "express";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const DATA_FILE = path.join(here, "..", "data", "tahlillar.json");
const PUBLIC_DIR = path.join(here, "..", "public");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(PUBLIC_DIR));

// Tahlil natijalarini JSON ko'rinishida qaytaradi.
app.get("/api/tahlillar", (req, res) => {
  if (!fs.existsSync(DATA_FILE)) {
    return res.json({ yangilangan_vaqt: null, tahlillar: [] });
  }
  const data = JSON.parse(fs.readFileSync(DATA_FILE, "utf8"));

  const { kategoriya } = req.query;
  if (kategoriya) {
    data.tahlillar = data.tahlillar.filter(
      (item) => item.kategoriya.toLowerCase() === String(kategoriya).toLowerCase(),
    );
  }
  res.json(data);
});

app.listen(PORT, () => {
  console.log(`🌐 Server ishga tushdi: http://localhost:${PORT}`);
});
