"use client";

import { useCallback, useEffect, useState } from "react";
import { API_URL } from "../../lib/api";

const STATUSES = [
  { value: "pending", label: "⏳ Kutilmoqda" },
  { value: "published", label: "✅ Chop etilgan" },
  { value: "rejected", label: "❌ Rad etilgan" },
];

export default function AdminPage() {
  const [token, setToken] = useState("");
  const [loggedIn, setLoggedIn] = useState(false);
  const [status, setStatus] = useState("pending");
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState(null);
  const [message, setMessage] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [draft, setDraft] = useState(null);

  useEffect(() => {
    const saved = sessionStorage.getItem("admin_token");
    if (saved) {
      setToken(saved);
      setLoggedIn(true);
    }
  }, []);

  const api = useCallback(
    async (path, options = {}) => {
      const res = await fetch(`${API_URL}${path}`, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          "X-Admin-Token": token,
          ...(options.headers || {}),
        },
      });
      if (res.status === 401) {
        setLoggedIn(false);
        sessionStorage.removeItem("admin_token");
        throw new Error("Token noto'g'ri");
      }
      if (!res.ok) throw new Error((await res.json()).detail || "Xatolik");
      return res.json();
    },
    [token],
  );

  const load = useCallback(async () => {
    try {
      const [list, statistics, categoryList] = await Promise.all([
        api(`/api/admin/articles?status=${status}`),
        api("/api/admin/stats"),
        api("/api/categories"),
      ]);
      setArticles(list);
      setStats(statistics);
      setCategories(categoryList);
    } catch (error) {
      setMessage(error.message);
    }
  }, [api, status]);

  useEffect(() => {
    if (loggedIn) load();
  }, [loggedIn, load]);

  async function action(path, method = "POST") {
    try {
      await api(path, { method });
      setMessage("✅ Bajarildi");
      load();
    } catch (error) {
      setMessage(`❌ ${error.message}`);
    }
  }

  function startEditing(article) {
    setEditingId(article.id);
    setDraft({
      title: article.title,
      seo_title: article.seo_title,
      summary: article.summary,
      content: article.content,
      practical_note: article.practical_note,
      tags: (article.tags || []).join(", "),
      importance: article.importance,
      category_id: article.category?.id || "",
      image_url: article.image_url || "",
    });
    setMessage("");
  }

  async function saveEditing(event, articleId) {
    event.preventDefault();
    try {
      const payload = {
        ...draft,
        tags: draft.tags.split(",").map((tag) => tag.trim()).filter(Boolean),
        importance: Number(draft.importance),
        category_id: Number(draft.category_id),
        image_url: draft.image_url || null,
      };
      await api(`/api/admin/articles/${articleId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      setEditingId(null);
      setDraft(null);
      setMessage("✅ Maqola saqlandi");
      await load();
    } catch (error) {
      setMessage(`❌ ${error.message}`);
    }
  }

  if (!loggedIn) {
    return (
      <div className="mx-auto max-w-sm py-24">
        <h1 className="mb-4 text-xl font-bold">🔐 Admin panel</h1>
        <input
          type="password"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          placeholder="Admin token"
          className="mb-3 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 outline-none focus:border-blue-500"
        />
        <button
          onClick={() => {
            sessionStorage.setItem("admin_token", token);
            setLoggedIn(true);
          }}
          className="w-full rounded-lg bg-blue-600 py-2 font-semibold hover:bg-blue-500"
        >
          Kirish
        </button>
      </div>
    );
  }

  return (
    <div className="py-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">🛠 Admin panel</h1>
        <button
          onClick={() => {
            sessionStorage.removeItem("admin_token");
            setLoggedIn(false);
          }}
          className="text-sm text-slate-400 hover:text-white"
        >
          Chiqish
        </button>
      </div>

      {stats && (
        <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-5">
          {[
            ["Jami", stats.jami],
            ["Kutilmoqda", stats.kutilmoqda],
            ["Chop etilgan", stats.chop_etilgan],
            ["Rad etilgan", stats.rad_etilgan],
            ["Telegramda", stats.telegramga_yuborilgan],
          ].map(([label, value]) => (
            <div key={label} className="rounded-xl border border-slate-800 p-4 text-center">
              <div className="text-2xl font-bold text-blue-400">{value}</div>
              <div className="text-xs text-slate-400">{label}</div>
            </div>
          ))}
        </div>
      )}

      <div className="mb-4 flex gap-2">
        {STATUSES.map((s) => (
          <button
            key={s.value}
            onClick={() => setStatus(s.value)}
            className={`rounded-full px-4 py-1.5 text-sm ${
              status === s.value
                ? "bg-blue-600 text-white"
                : "border border-slate-700 text-slate-300"
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {message && <div className="mb-4 text-sm text-slate-300">{message}</div>}

      <div className="space-y-4">
        {articles.length === 0 && (
          <p className="py-10 text-center text-slate-500">Bu holatda maqolalar yo&apos;q.</p>
        )}
        {articles.map((article) => (
          <div key={article.id} className="rounded-xl border border-slate-800 p-5">
            <div className="mb-1 flex flex-wrap items-center gap-2 text-xs text-slate-400">
              <span className="rounded-full bg-blue-500/10 px-2 py-0.5 text-blue-400">
                {article.category?.name || "—"}
              </span>
              <span>{"⭐".repeat(article.importance)}</span>
              <span>{article.source_name}</span>
              {article.sent_to_telegram && <span>📨 Telegramda</span>}
            </div>
            {editingId === article.id ? (
              <form onSubmit={(event) => saveEditing(event, article.id)} className="my-4 space-y-3">
                <label className="block text-sm">
                  <span className="mb-1 block text-slate-400">Sarlavha</span>
                  <input
                    value={draft.title}
                    onChange={(event) => setDraft({ ...draft, title: event.target.value })}
                    minLength={12}
                    required
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
                  />
                </label>
                <label className="block text-sm">
                  <span className="mb-1 block text-slate-400">SEO sarlavha</span>
                  <input
                    value={draft.seo_title}
                    onChange={(event) => setDraft({ ...draft, seo_title: event.target.value })}
                    minLength={12}
                    required
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
                  />
                </label>
                <label className="block text-sm">
                  <span className="mb-1 block text-slate-400">Qisqa xulosa</span>
                  <textarea
                    value={draft.summary}
                    onChange={(event) => setDraft({ ...draft, summary: event.target.value })}
                    rows={3}
                    minLength={40}
                    required
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
                  />
                </label>
                <label className="block text-sm">
                  <span className="mb-1 block text-slate-400">Maqola</span>
                  <textarea
                    value={draft.content}
                    onChange={(event) => setDraft({ ...draft, content: event.target.value })}
                    rows={10}
                    minLength={100}
                    required
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
                  />
                </label>
                <label className="block text-sm">
                  <span className="mb-1 block text-slate-400">Amaliy ahamiyati</span>
                  <textarea
                    value={draft.practical_note}
                    onChange={(event) => setDraft({ ...draft, practical_note: event.target.value })}
                    rows={2}
                    minLength={20}
                    required
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
                  />
                </label>
                <div className="grid gap-3 sm:grid-cols-3">
                  <label className="block text-sm sm:col-span-2">
                    <span className="mb-1 block text-slate-400">Teglar, vergul bilan</span>
                    <input
                      value={draft.tags}
                      onChange={(event) => setDraft({ ...draft, tags: event.target.value })}
                      className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
                    />
                  </label>
                  <label className="block text-sm">
                    <span className="mb-1 block text-slate-400">Ahamiyati</span>
                    <select
                      value={draft.importance}
                      onChange={(event) => setDraft({ ...draft, importance: event.target.value })}
                      className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
                    >
                      {[1, 2, 3, 4, 5].map((value) => <option key={value} value={value}>{value}</option>)}
                    </select>
                  </label>
                </div>
                <label className="block text-sm">
                  <span className="mb-1 block text-slate-400">Kategoriya</span>
                  <select
                    value={draft.category_id}
                    onChange={(event) => setDraft({ ...draft, category_id: event.target.value })}
                    required
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
                  >
                    <option value="" disabled>Kategoriyani tanlang</option>
                    {categories.map((category) => (
                      <option key={category.id} value={category.id}>{category.name}</option>
                    ))}
                  </select>
                </label>
                <label className="block text-sm">
                  <span className="mb-1 block text-slate-400">Rasm URL’i</span>
                  <input
                    type="url"
                    value={draft.image_url}
                    onChange={(event) => setDraft({ ...draft, image_url: event.target.value })}
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
                  />
                </label>
                <div className="flex gap-2">
                  <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 font-semibold hover:bg-blue-500">
                    💾 Saqlash
                  </button>
                  <button
                    type="button"
                    onClick={() => { setEditingId(null); setDraft(null); }}
                    className="rounded-lg border border-slate-700 px-4 py-2 text-slate-300"
                  >
                    Bekor qilish
                  </button>
                </div>
              </form>
            ) : (
              <>
                <h2 className="mb-1 font-semibold">{article.title}</h2>
                <p className="mb-3 text-sm text-slate-400">{article.summary}</p>
              </>
            )}
            <div className="flex flex-wrap gap-2 text-sm">
              {editingId !== article.id && (
                <button
                  onClick={() => startEditing(article)}
                  className="rounded-lg bg-blue-800 px-3 py-1.5 hover:bg-blue-700"
                >
                  ✏️ Tahrirlash
                </button>
              )}
              {article.status !== "published" && (
                <button
                  onClick={() => action(`/api/admin/articles/${article.id}/approve`)}
                  className="rounded-lg bg-green-700 px-3 py-1.5 hover:bg-green-600"
                >
                  ✅ Tasdiqlash
                </button>
              )}
              {article.status === "published" && !article.sent_to_telegram && (
                <button
                  onClick={() => action(`/api/admin/articles/${article.id}/telegram`)}
                  className="rounded-lg bg-sky-700 px-3 py-1.5 hover:bg-sky-600"
                >
                  📤 Telegramga
                </button>
              )}
              {article.status === "pending" && (
                <button
                  onClick={() => action(`/api/admin/articles/${article.id}/reject`)}
                  className="rounded-lg bg-yellow-800 px-3 py-1.5 hover:bg-yellow-700"
                >
                  🚫 Rad etish
                </button>
              )}
              <button
                onClick={() => action(`/api/admin/articles/${article.id}`, "DELETE")}
                className="rounded-lg bg-red-900 px-3 py-1.5 hover:bg-red-800"
              >
                🗑 O&apos;chirish
              </button>
              <a
                href={article.original_url}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-lg border border-slate-700 px-3 py-1.5 text-slate-300"
              >
                🔗 Manba
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
