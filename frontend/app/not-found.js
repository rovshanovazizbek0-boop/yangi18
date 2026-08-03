import Link from "next/link";

export const metadata = {
  title: "Sahifa topilmadi",
  robots: { index: false, follow: true },
};

export default function NotFound() {
  return (
    <div className="mx-auto max-w-xl py-24 text-center">
      <div className="mb-3 text-5xl">404</div>
      <h1 className="mb-3 text-2xl font-bold">Sahifa topilmadi</h1>
      <p className="mb-6 text-slate-400">
        Havola eskirgan yoki sahifa o&apos;chirilgan bo&apos;lishi mumkin.
      </p>
      <Link href="/" className="rounded-lg bg-blue-600 px-4 py-2 font-semibold hover:bg-blue-500">
        Bosh sahifaga qaytish
      </Link>
    </div>
  );
}
