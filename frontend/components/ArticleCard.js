import Link from "next/link";
import ArticleImage from "./ArticleImage";
import { formatDate } from "../lib/date";

export default function ArticleCard({ article, compact = false, priority = false }) {
  const stars = "⭐".repeat(Math.max(1, Math.min(5, article.importance)));
  const date = formatDate(article.published_at);

  if (compact) {
    return (
      <Link
        href={`/maqola/${article.slug}`}
        className="block rounded-lg border border-slate-800 p-3 hover:border-blue-600"
      >
        <div className="mb-1 text-xs text-slate-400">
          {article.category?.name} · {stars}
        </div>
        <div className="text-sm font-medium leading-snug">{article.title}</div>
      </Link>
    );
  }

  return (
    <article className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60 transition hover:border-blue-600">
      <ArticleImage
        src={article.image_url}
        alt={`${article.title} maqolasi rasmi`}
        priority={priority}
      />

      <div className="p-5">
        <div className="mb-2 flex items-center justify-between text-xs text-slate-400">
          <span className="rounded-full bg-blue-500/10 px-2.5 py-0.5 font-semibold text-blue-400">
            {article.category?.name || "AI"}
          </span>
          <span>{stars}</span>
        </div>
        <Link href={`/maqola/${article.slug}`}>
          <h2 className="mb-2 text-lg font-semibold leading-snug hover:text-blue-400">
            {article.title}
          </h2>
        </Link>
        <p className="mb-3 line-clamp-3 text-sm leading-relaxed text-slate-300">
          {article.summary}
        </p>
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>{date}</span>
          <Link href={`/maqola/${article.slug}`} className="text-blue-400 hover:underline">
            To&apos;liq o&apos;qish →
          </Link>
        </div>
      </div>
    </article>
  );
}
