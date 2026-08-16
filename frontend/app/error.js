"use client";

import { useEffect } from "react";

export default function GlobalError({ error, reset }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="mx-auto max-w-xl py-24 text-center">
      <h1 className="mb-3 text-2xl font-bold">Sahifani yuklab bo&apos;lmadi</h1>
      <p className="mb-6 text-slate-400">
        Server vaqtincha javob bermayapti. Birozdan keyin qayta urinib ko&apos;ring.
      </p>
      <div className="flex justify-center gap-3">
        <button
          type="button"
          onClick={reset}
          className="rounded-lg bg-blue-600 px-4 py-2 font-semibold hover:bg-blue-500"
        >
          Qayta urinish
        </button>
        <a
          href="/"
          className="rounded-lg border border-slate-700 px-4 py-2 text-slate-300 hover:text-white"
        >
          Bosh sahifa
        </a>
      </div>
    </div>
  );
}
