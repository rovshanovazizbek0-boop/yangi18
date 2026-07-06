import { ImageResponse } from "next/og";

export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
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
          borderRadius: 36,
        }}
      >
        <div
          style={{
            fontSize: 84,
            fontWeight: 700,
            background: "linear-gradient(135deg, #3b82f6, #06b6d4)",
            backgroundClip: "text",
            color: "transparent",
          }}
        >
          AI
        </div>
        <div style={{ fontSize: 24, color: "#94a3b8", letterSpacing: 4 }}>
          XABAR
        </div>
      </div>
    ),
    size
  );
}
