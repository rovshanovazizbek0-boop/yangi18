export function seoDescription(value, maxLength = 165) {
  const text = String(value || "").replace(/\s+/g, " ").trim();
  if (text.length <= maxLength) return text;

  const candidate = text.slice(0, maxLength + 1);
  const wordBoundary = candidate.lastIndexOf(" ");
  const cutAt = wordBoundary >= Math.floor(maxLength * 0.65) ? wordBoundary : maxLength;
  return `${candidate.slice(0, cutAt).trimEnd()}…`;
}
