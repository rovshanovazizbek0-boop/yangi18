import { fetchJson } from "./api-core.mjs";
import { unstable_rethrow } from "next/navigation";

// Server (SSR) konteyner ichida backend'ga ichki tarmoq orqali murojaat qiladi
// (API_URL_INTERNAL), brauzer esa tashqi manzildan (NEXT_PUBLIC_API_URL).
const isServer = typeof window === "undefined";
const API_URL =
  (isServer && process.env.API_URL_INTERNAL) ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

export async function apiGet(path, params = {}) {
  const url = new URL(`${API_URL}${path}`);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) url.searchParams.set(key, value);
  });
  try {
    return await fetchJson(url);
  } catch (error) {
    // Next.js prerender/dynamic-render signallarini oddiy tarmoq xatosi deb
    // o'rab yubormaslik kerak; framework ularni o'zi boshqaradi.
    unstable_rethrow(error);
    throw error;
  }
}

export { API_URL };
