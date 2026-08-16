export class ApiError extends Error {
  constructor(message, status = 500, options = {}) {
    super(message, options);
    this.name = "ApiError";
    this.status = status;
  }
}

async function errorDetail(response) {
  try {
    const payload = await response.json();
    return typeof payload?.detail === "string" ? payload.detail : null;
  } catch {
    return null;
  }
}

/** 404 uchun null qaytaradi; vaqtinchalik API/tarmoq xatolarini yashirmaydi. */
export async function fetchJson(url, fetchImpl = fetch) {
  let response;
  try {
    response = await fetchImpl(url, { cache: "no-store" });
  } catch (cause) {
    throw new ApiError("Backend bilan bog'lanib bo'lmadi", 503, { cause });
  }

  if (response.status === 404) return null;
  if (!response.ok) {
    const detail = await errorDetail(response);
    throw new ApiError(detail || `Backend xatosi (${response.status})`, response.status);
  }

  try {
    return await response.json();
  } catch (cause) {
    throw new ApiError("Backend yaroqsiz JSON javob qaytardi", 502, { cause });
  }
}
