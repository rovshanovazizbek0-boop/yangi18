"use client";

import { useState } from "react";
import Image from "next/image";

const BRAND_THEMES = {
  openai: {
    bg: "from-emerald-950 via-slate-950 to-teal-950",
    glow: "rgba(16, 185, 129, 0.2)",
    badge: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
    icon: (
      <svg className="w-12 h-12 text-emerald-400" viewBox="0 0 24 24" fill="currentColor">
        <path d="M22.28 9.53a5.95 5.95 0 0 0-.52-4.91 6.05 6.05 0 0 0-6.51-2.9 6.07 6.07 0 0 0-4.63-2.12c-3.1 0-5.69 2.33-6.04 5.39A6.03 6.03 0 0 0 .97 8.07a6 6 0 0 0 1.25 7.02 5.95 5.95 0 0 0 .52 4.91 6.05 6.05 0 0 0 6.51 2.9 6.07 6.07 0 0 0 4.63 2.12c3.1 0 5.69-2.33 6.04-5.39a6.03 6.03 0 0 0 3.61-3.08 6 6 0 0 0-1.25-7.02zm-8.8 12.37a4.47 4.47 0 0 1-2.94-1.1l.15-.09 4.88-2.82a.8.8 0 0 0 .4-.69v-6.9l2.07 1.2v5.74a4.5 4.5 0 0 1-4.56 4.66zm-8.3-3.66a4.48 4.48 0 0 1-.58-3.09l.15.09 4.88 2.82a.8.8 0 0 0 .8 0l5.97-3.45v2.39l-4.97 2.87a4.5 4.5 0 0 1-6.25-1.63zM3.4 9.17a4.46 4.46 0 0 1 2.36-1.99v5.82a.8.8 0 0 0 .4.69l5.97 3.45-2.07 1.2-4.97-2.87a4.5 4.5 0 0 1-1.69-6.3zm14.34 2.84l-5.97-3.45 2.07-1.2 4.97 2.87a4.5 4.5 0 0 1 1.69 6.3 4.47 4.47 0 0 1-2.36 1.99v-5.82a.8.8 0 0 0-.4-.69zm2.4-3.09l-.15-.09-4.88-2.82a.8.8 0 0 0-.8 0l-5.97 3.45V6.47l4.97-2.87a4.5 4.5 0 0 1 6.83 4.72v.03zm-7.7-1.42l-2.9 1.68-2.9-1.68 2.9-1.68 2.9 1.68z" />
      </svg>
    ),
  },
  gemini: {
    bg: "from-indigo-950 via-slate-950 to-blue-950",
    glow: "rgba(99, 102, 241, 0.2)",
    badge: "bg-indigo-500/10 text-indigo-300 border-indigo-500/30",
    icon: (
      <svg className="w-12 h-12 text-indigo-400" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0C12 6.627 6.627 12 0 12c6.627 0 12 5.627 12 12 0-6.627 5.627-12 12-12-6.627 0-12-5.627-12-12z" />
      </svg>
    ),
  },
  claude: {
    bg: "from-amber-950/90 via-slate-950 to-orange-950/80",
    glow: "rgba(245, 158, 11, 0.2)",
    badge: "bg-amber-500/10 text-amber-300 border-amber-500/30",
    icon: (
      <svg className="w-12 h-12 text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="4" fill="currentColor" />
        <path d="M12 2v3m0 14v3M2 12h3m14 0h3m-3.5-6.5l-2.1 2.1m-8.8 8.8l-2.1 2.1m0-13l2.1 2.1m8.8 8.8l2.1 2.1" strokeLinecap="round" />
      </svg>
    ),
  },
  meta: {
    bg: "from-blue-950 via-slate-950 to-cyan-950",
    glow: "rgba(6, 182, 212, 0.2)",
    badge: "bg-cyan-500/10 text-cyan-300 border-cyan-500/30",
    icon: (
      <svg className="w-12 h-12 text-cyan-400" viewBox="0 0 24 24" fill="currentColor">
        <path d="M16.5 4C13.46 4 12 6.13 12 8c0-1.87-1.46-4-4.5-4C3.8 4 1 6.8 1 12c0 5.2 2.8 8 6.5 8 3.04 0 4.5-2.13 4.5-4 0 1.87 1.46 4 4.5 4 3.7 0 6.5-2.8 6.5-8 0-5.2-2.8-8-6.5-8zm-9 13.5c-2.4 0-4-1.9-4-5.5s1.6-5.5 4-5.5c2.3 0 3.3 1.9 3.5 3.5-.2 1.6-1.2 7.5-3.5 7.5zm9 0c-2.3 0-3.3-5.9-3.5-7.5.2-1.6 1.2-3.5 3.5-3.5 2.4 0 4 1.9 4 5.5s-1.6 5.5-4 5.5z" />
      </svg>
    ),
  },
};

const DEFAULT_THEME = {
  bg: "from-blue-950 via-slate-950 to-slate-900",
  glow: "rgba(59, 130, 246, 0.2)",
  badge: "bg-blue-500/10 text-blue-300 border-blue-500/30",
  icon: (
    <svg className="w-12 h-12 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 2a10 10 0 1 0 10 10H12V2z" />
      <path d="M12 2a10 10 0 0 1 10 10" />
      <path d="M12 12L2.5 7.5" />
    </svg>
  ),
};

export default function SingleArticleImage({ src, alt, category, title }) {
  const [error, setError] = useState(false);

  const slug = category?.slug?.toLowerCase();
  const theme = BRAND_THEMES[slug] || DEFAULT_THEME;
  const categoryName = category?.name || "AI Xabar";

  if (error || !src) {
    return (
      <div className={`relative mb-8 flex aspect-video w-full flex-col justify-between overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-br ${theme.bg} p-8 shadow-2xl`}>
        {/* Glow Effects */}
        <div
          className="absolute -right-16 -top-16 h-64 w-64 rounded-full blur-3xl pointer-events-none"
          style={{ backgroundColor: theme.glow }}
        />
        <div
          className="absolute -bottom-16 -left-16 h-64 w-64 rounded-full blur-3xl pointer-events-none"
          style={{ backgroundColor: theme.glow }}
        />

        {/* Top bar */}
        <div className="relative z-10 flex items-center justify-between">
          <span className={`inline-flex items-center gap-2 rounded-full border px-4 py-1.5 text-xs font-semibold backdrop-blur-md ${theme.badge}`}>
            {categoryName}
          </span>
          <span className="font-mono text-xs tracking-widest text-slate-500 uppercase">
            AIXABAR.UZ
          </span>
        </div>

        {/* Center brand logo */}
        <div className="relative z-10 flex flex-col items-center justify-center my-auto">
          <div className="rounded-3xl border border-slate-700/60 bg-slate-900/70 p-5 backdrop-blur-md shadow-2xl">
            {theme.icon}
          </div>
        </div>

        {/* Bottom bar */}
        <div className="relative z-10 border-t border-slate-800/80 pt-3 text-xs text-slate-400">
          <span className="font-medium text-slate-300">{title || "Eksklyuziv tahliliy maqola"}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="relative mb-6 aspect-video overflow-hidden rounded-xl bg-slate-900">
      <Image
        src={src}
        alt={alt}
        fill
        unoptimized
        sizes="(max-width: 768px) 100vw, 768px"
        className="object-cover"
        priority
        onError={() => setError(true)}
      />
    </div>
  );
}
