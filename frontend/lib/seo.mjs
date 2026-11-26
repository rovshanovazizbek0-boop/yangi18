function truncateOnWord(value, maxLength) {
  const text = String(value || "").replace(/\s+/g, " ").trim();
  if (text.length <= maxLength) return text;

  const limit = Math.max(1, maxLength - 1);
  const candidate = text.slice(0, limit + 1);
  const wordBoundary = candidate.lastIndexOf(" ");
  const cutAt =
    wordBoundary >= Math.floor(limit * 0.65) ? wordBoundary : limit;
  return `${candidate.slice(0, cutAt).trimEnd()}…`;
}

// Layout template `"%s — AI Xabar"` (+11 belgi) bilan jami <= 65 belgi chiqadi.
export function seoTitle(value, maxLength = 54) {
  return truncateOnWord(value, maxLength);
}

export function seoDescription(value, maxLength = 155) {
  return truncateOnWord(value, maxLength);
}
