import { ImageResponse } from "next/og";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export const alt = "AI News Uzbekistan — Sun'iy intellekt yangiliklari";

export default function OgImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "#020617",
          fontFamily: "sans-serif",
          gap: 30,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 130,
            height: 130,
            borderRadius: 32,
            background: "#0f172a",
            border: "6px solid #3b82f6",
            color: "#38bdf8",
            fontSize: 60,
            fontWeight: 700,
          }}
        >
          AI
        </div>
        <div
          style={{
            display: "flex",
            gap: 18,
            color: "white",
            fontSize: 68,
            fontWeight: 700,
          }}
        >
          <span>AI News</span>
          <span style={{ color: "#60a5fa" }}>Uzbekistan</span>
        </div>
        <div style={{ color: "#94a3b8", fontSize: 32 }}>
          Sun&apos;iy intellekt yangiliklari — o&apos;zbek tilida
        </div>
        <div style={{ color: "#475569", fontSize: 28 }}>aixabar.uz</div>
      </div>
    ),
    size
  );
}
