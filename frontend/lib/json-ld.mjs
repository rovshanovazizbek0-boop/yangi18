/**
 * JSON-LD ni HTML <script> ichiga xavfsiz joylash uchun serializatsiya qiladi.
 * JSON ichidagi `</script>` HTML parser tomonidan haqiqiy yopuvchi teg sifatida
 * talqin qilinmasligi uchun `<` belgisi Unicode escape ko'rinishiga o'tkaziladi.
 */
export function serializeJsonLd(value) {
  return JSON.stringify(value)
    .replaceAll("<", "\\u003c")
    .replaceAll("\u2028", "\\u2028")
    .replaceAll("\u2029", "\\u2029");
}
