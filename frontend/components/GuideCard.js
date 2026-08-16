import Link from "next/link";
import { difficultyName, providerName } from "../lib/guides";

export default function GuideCard({ guide, compact = false }) {
  return (
    <article className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 transition hover:border-emerald-600">
      <div className="mb-3 flex flex-wrap items-center gap-2 text-xs">
        <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 font-semibold text-emerald-400">
          {providerName(guide.provider)}
        </span>
        <span className="text-slate-500">{difficultyName(guide.difficulty)}</span>
        <span className="text-slate-600">•</span>
        <span className="text-slate-500">{guide.duration_minutes} daqiqa</span>
        {guide.generation_type === "ai" && (
          <span className="rounded-full border border-violet-800 px-2 py-0.5 text-violet-300">AI agent · kunlik</span>
        )}
      </div>
      <Link href={`/organish/${guide.slug}`}>
        <h2 className={`${compact ? "text-base" : "text-xl"} mb-2 font-bold leading-snug hover:text-emerald-400`}>
          {guide.title}
        </h2>
      </Link>
      {!compact && <p className="mb-4 text-sm leading-relaxed text-slate-300">{guide.excerpt}</p>}
      <Link href={`/organish/${guide.slug}`} className="text-sm font-semibold text-emerald-400 hover:underline">
        Qadam-baqadam o'rganish →
      </Link>
    </article>
  );
}
