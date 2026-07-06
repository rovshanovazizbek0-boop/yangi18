import { ImageResponse } from "next/og";

// PWA manifest uchun PNG ikon generatori (192/512)
export function pwaIcon(px) {
  const s = px / 192; // 192 ga nisbatan masshtab
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
          background: "#0f172a",
        }}
      >
        <div
          style={{
            fontSize: 88 * s,
            fontWeight: 700,
            background: "linear-gradient(135deg, #3b82f6, #06b6d4)",
            backgroundClip: "text",
            color: "transparent",
          }}
        >
          AI
        </div>
        <div
          style={{
            fontSize: 26 * s,
            color: "#94a3b8",
            letterSpacing: 6 * s,
          }}
        >
          NEWS
        </div>
      </div>
    ),
    { width: px, height: px }
  );
}
