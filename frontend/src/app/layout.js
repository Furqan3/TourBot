// app/layout.js
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Chatbot App",
  description: "A Next.js chatbot application",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${inter.className} flex flex-col h-screen bg-gray-100`}>
        <main className="flex-grow overflow-hidden flex items-center justify-center p-4">
          <div className="w-full max-w-4xl bg-white rounded-lg shadow-md p-6 space-y-4">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}