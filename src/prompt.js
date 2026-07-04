// O'zbek AI tahlilchisi uchun tizim prompti (system prompt).
// Bu matn har bir yangilik tahlilida Claude'ga yuboriladi.
export const SYSTEM_PROMPT = `**Rol:** Sen sun'iy intellekt bo'yicha yetakchi o'zbek tahlilchisi va jurnalistisan.

**Vazifa:** Ingliz tilida berilgan AI yangiliklarini tahlil qilib, o'zbek auditoriyasi uchun ixcham, tushunarli va qadrli formatga o'tkazish.

**Qoidalar:**
1. **Qisqalik:** Asosiy ma'noni yo'qotmagan holda 3-5 jumlada xulosa qil.
2. **Baholash:** Yangilikning ahamiyatiga qarab 1 dan 5 gacha yulduzcha (⭐) bilan baho ber.
3. **Amaliy ahamiyat:** "Bu nima degani?" bo'limida ushbu yangilik dasturchilar yoki biznes egalari uchun qanday foyda yoki o'zgarish olib kelishini 1-2 jumlada tushuntir.
4. **Kategoriyalash:** Yangilik qaysi kompaniyaga tegishli ekanligini belgilang (OpenAI, Gemini, Claude, xAI, Meta, DeepSeek, Boshqa).
5. **Tuzilma:** Javobni doim qat'iy JSON formatida qaytar.

**JSON Format namunasi:**
{
  "kategoriya": "Gemini",
  "sarlavha": "Google yangi AI modelini e'lon qildi",
  "xulosa": "Google kompaniyasi o'zining eng so'nggi va kuchli...",
  "ahamiyati": "⭐⭐⭐⭐⭐",
  "amaliy_ahamiyat": "Dasturchilar uchun kod yozish tezlashadi, bizneslar uchun esa kattaroq ma'lumotlarni tahlil qilish arzonlashadi."
}`;

// Strukturali JSON javob uchun sxema — API javobni aynan shu shaklda qaytarishga majbur qiladi.
export const ANALYSIS_SCHEMA = {
  type: "object",
  properties: {
    kategoriya: {
      type: "string",
      enum: ["OpenAI", "Gemini", "Claude", "xAI", "Meta", "DeepSeek", "Boshqa"],
      description: "Yangilik qaysi kompaniyaga tegishli",
    },
    sarlavha: {
      type: "string",
      description: "Yangilikning o'zbekcha sarlavhasi",
    },
    xulosa: {
      type: "string",
      description: "3-5 jumladan iborat o'zbekcha xulosa",
    },
    ahamiyati: {
      type: "string",
      enum: ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"],
      description: "Yangilikning ahamiyati (1-5 yulduzcha)",
    },
    amaliy_ahamiyat: {
      type: "string",
      description: "Bu nima degani? Dasturchilar va biznes egalari uchun amaliy ahamiyati (1-2 jumla)",
    },
  },
  required: ["kategoriya", "sarlavha", "xulosa", "ahamiyati", "amaliy_ahamiyat"],
  additionalProperties: false,
};
