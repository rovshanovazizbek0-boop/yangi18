import { API_URL } from "../../../../lib/api";

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/api/news/rss`, {
      next: { revalidate: 300 },
    });
    if (!response.ok) {
      return new Response("RSS hozircha mavjud emas", { status: 502 });
    }

    return new Response(await response.text(), {
      headers: {
        "Content-Type": "application/rss+xml; charset=utf-8",
        "Cache-Control": "public, s-maxage=300, stale-while-revalidate=600",
      },
    });
  } catch (error) {
    console.error("RSS proxy error:", error);
    return new Response("RSS hozircha mavjud emas", { status: 502 });
  }
}
