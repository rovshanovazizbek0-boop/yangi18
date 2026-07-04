# 🤖 AI Yangiliklar Tahlilchisi

Jahon sun'iy intellekt yangiliklarini **o'zbek tilida**, qisqa va tushunarli formatda taqdim etuvchi dastur.

Dastur ingliz tilidagi AI yangiliklarini (OpenAI, Google, Anthropic, TechCrunch va boshqa manbalardan) avtomatik yig'adi va Claude API yordamida har birini o'zbek auditoriyasi uchun tahlil qiladi.

## Har bir tahlil quyidagilarni o'z ichiga oladi

| Maydon | Tavsif |
|---|---|
| `kategoriya` | Yangilik qaysi kompaniyaga tegishli (OpenAI, Gemini, Claude, xAI, Meta, DeepSeek, Boshqa) |
| `sarlavha` | O'zbekcha sarlavha |
| `xulosa` | 3-5 jumladan iborat qisqa xulosa |
| `ahamiyati` | 1 dan 5 gacha yulduzcha (⭐) baho |
| `amaliy_ahamiyat` | "Bu nima degani?" — dasturchilar va biznes egalari uchun amaliy ahamiyati |

Misol:

```json
{
  "kategoriya": "Gemini",
  "sarlavha": "Google yangi AI modelini e'lon qildi",
  "xulosa": "Google kompaniyasi o'zining eng so'nggi va kuchli...",
  "ahamiyati": "⭐⭐⭐⭐⭐",
  "amaliy_ahamiyat": "Dasturchilar uchun kod yozish tezlashadi, bizneslar uchun esa kattaroq ma'lumotlarni tahlil qilish arzonlashadi."
}
```

## O'rnatish

1. Loyihani yuklab oling va bog'liqliklarni o'rnating:

   ```bash
   npm install
   ```

2. `.env` faylini yarating va API kalitini kiriting:

   ```bash
   cp .env.example .env
   # .env faylida ANTHROPIC_API_KEY qiymatini to'ldiring
   ```

   API kalitini [platform.claude.com](https://platform.claude.com) saytidan olish mumkin.

## Ishlatish

**1. Yangiliklarni yig'ish va tahlil qilish:**

```bash
npm run analyze
```

Bu buyruq RSS manbalardan eng so'nggi yangiliklarni oladi, har birini Claude yordamida tahlil qiladi va natijani `data/tahlillar.json` fayliga saqlaydi.

**2. Natijalarni brauzerda ko'rish:**

```bash
npm run serve
```

So'ng brauzerda [http://localhost:3000](http://localhost:3000) sahifasini oching. Sahifada tahlillarni kompaniya bo'yicha filtrlash mumkin.

## Loyiha tuzilishi

```
src/
  prompt.js     — o'zbek tahlilchisi tizim prompti va JSON sxemasi
  feeds.js      — RSS manbalardan yangiliklar yig'ish
  analyzer.js   — Claude API orqali tahlil qilish
  index.js      — asosiy skript (yig'ish + tahlil + saqlash)
  server.js     — natijalarni ko'rsatuvchi veb-server
public/
  index.html    — o'zbekcha veb-interfeys
data/
  tahlillar.json — tahlil natijalari (avtomatik yaratiladi)
```

## Texnologiyalar

- **Node.js 18+** (ES modules)
- **Claude API** (`@anthropic-ai/sdk`) — strukturali JSON javob (`output_config.format`) bilan
- **rss-parser** — yangiliklar yig'ish uchun
- **Express** — veb-server uchun
