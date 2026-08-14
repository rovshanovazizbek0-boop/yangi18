// Sanalar doim Toshkent vaqtida ko'rsatiladi. Zona ko'rsatilmasa, sahifani
// render qilayotgan server o'z zonasida formatlaydi — Vercel UTC'da ishlagani
// uchun o'quvchi 5 soat orqadagi vaqtni ko'rardi.
export const SITE_TIMEZONE = "Asia/Tashkent";

export function formatDateTime(value) {
  if (!value) return "";
  return new Date(value).toLocaleString("uz-UZ", { timeZone: SITE_TIMEZONE });
}

export function formatDate(value) {
  if (!value) return "";
  return new Date(value).toLocaleDateString("uz-UZ", { timeZone: SITE_TIMEZONE });
}
