// Katalogda ishlatiladigan umumiy nomlar va "hali tekshirilmagan" holati.
// Vosita ma'lumoti qo'lda to'ldirilgani uchun ko'p maydon null bo'lib turadi —
// bu vaqtinchalik holat, uni bo'sh joy sifatida emas, ochiq aytish kerak.

export const TOOL_CATEGORIES = {
  matn: "Matn va suhbat",
  rasm: "Rasm yaratish",
  video: "Video",
  ovoz: "Ovoz va musiqa",
  kod: "Dasturlash",
  agent: "AI agentlari",
  qidiruv: "Qidiruv",
  tarjima: "Tarjima",
  unumdorlik: "Ish unumdorligi",
};

export function categoryName(slug) {
  return TOOL_CATEGORIES[slug] || slug;
}

export const NOT_CHECKED = "Hali tekshirilmagan";

export function yesNo(value, { yes = "Ha", no = "Yo'q" } = {}) {
  if (value === true) return yes;
  if (value === false) return no;
  return NOT_CHECKED;
}

/** O'zbekiston ma'lumoti umuman to'ldirilganmi. */
export function hasUzData(uz = {}) {
  return (
    uz?.vpn_kerakmi !== null && uz?.vpn_kerakmi !== undefined ||
    Boolean(uz?.tolov) ||
    Boolean(uz?.ozbek_tili) ||
    Boolean(uz?.narx_somda) ||
    (uz?.tolov_yollari || []).length > 0
  );
}
