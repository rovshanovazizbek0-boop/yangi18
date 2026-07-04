import "./globals.css";
import Header from "../components/Header";

export const metadata = {
  title: "AI News Uzbekistan — Sun'iy intellekt yangiliklari o'zbek tilida",
  description:
    "Dunyodagi eng muhim AI yangiliklari — qisqa, tushunarli va o'zbek tilida. OpenAI, Gemini, Claude, xAI, Meta va boshqalar.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="uz">
      <body>
        <Header />
        <main className="mx-auto max-w-6xl px-4 pb-16">{children}</main>
        <footer className="border-t border-slate-800 py-8 text-center text-sm text-slate-500">
          © {new Date().getFullYear()} AI News Uzbekistan — sun&apos;iy intellekt yangiliklari o&apos;zbek tilida
        </footer>
      </body>
    </html>
  );
}
