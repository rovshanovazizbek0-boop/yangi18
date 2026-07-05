import "./globals.css";
import Header from "../components/Header";

export const metadata = {
  title: "AI News Uzbekistan — Sun'iy intellekt yangiliklari o'zbek tilida",
  description:
    "Dunyodagi eng muhim AI yangiliklari — qisqa, tushunarli va o'zbek tilida. OpenAI, Gemini, Claude, xAI, Meta va boshqalar.",
  verification: {
    google: "jXooaK9j5y0IH4ngJRPi--LR795mmAU5b_Qebo4QBjs",
  },
};


export default function RootLayout({ children }) {
  return (
    <html lang="uz">
      <body>
        <Header />
        <main className="mx-auto max-w-6xl px-4 pb-16">{children}</main>
        <footer className="border-t border-slate-800 py-8 text-center text-sm text-slate-500">
          <div className="mb-3 flex justify-center gap-4 flex-wrap">
            <a
              href="https://t.me/aixabarlari"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-sky-400 transition-colors"
            >
              📢 Telegram Kanal (@aixabarlari)
            </a>
            <span>•</span>
            <a
              href="https://t.me/Ainewsuzbek_bot"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-blue-400 transition-colors"
            >
              🤖 Telegram Bot (@Ainewsuzbek_bot)
            </a>
          </div>
          © {new Date().getFullYear()} AI News Uzbekistan — sun&apos;iy intellekt yangiliklari o&apos;zbek tilida
        </footer>

      </body>
    </html>
  );
}
