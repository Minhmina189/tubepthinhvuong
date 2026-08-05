import type { Metadata } from "next";
import "./globals.css";
import { CartProvider } from "@/components/CartProvider";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "Mina Skill Hub · Thế giới Skill bán hàng chuyên nghiệp",
  description:
    "Mua Skill AI bán hàng, tạo ảnh, tạo video. Thanh toán tự động — tải ngay sau khi mua.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body>
        <CartProvider>
          <Header />
          <main className="min-h-screen">{children}</main>
          <footer className="text-center py-8 text-sm text-gray-400 border-t border-gray-100 mt-16">
            © 2024 Mina Skill Hub · Mọi giao dịch được bảo vệ an toàn
          </footer>
        </CartProvider>
      </body>
    </html>
  );
}
