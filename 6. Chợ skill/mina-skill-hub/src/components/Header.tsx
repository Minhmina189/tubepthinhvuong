"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useCart } from "./CartProvider";
import { createClient } from "@/lib/supabase-client";
import type { User } from "@supabase/supabase-js";

export function Header() {
  const { count } = useCart();
  const [user, setUser] = useState<User | null>(null);
  const supabase = createClient();

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => setUser(data.user));
    const { data: listener } = supabase.auth.onAuthStateChange((_, session) =>
      setUser(session?.user ?? null)
    );
    return () => listener.subscription.unsubscribe();
  }, []);

  const signOut = async () => {
    await supabase.auth.signOut();
    setUser(null);
  };

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-gray-100">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" className="font-bold text-lg tracking-tight">
          Mina Skill Hub
        </Link>

        <nav className="hidden md:flex items-center gap-6 text-sm text-gray-600">
          <Link href="/#sanh-1" className="hover:text-gray-900">Tạo Ảnh</Link>
          <Link href="/#sanh-2" className="hover:text-gray-900">Tạo Video</Link>
          <Link href="/#sanh-3" className="hover:text-gray-900">Đặc Biệt</Link>
        </nav>

        <div className="flex items-center gap-3">
          {user ? (
            <>
              <Link
                href="/dashboard"
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Skill của tôi
              </Link>
              <button
                onClick={signOut}
                className="text-sm text-gray-400 hover:text-gray-600"
              >
                Đăng xuất
              </button>
            </>
          ) : (
            <Link
              href="/auth/login"
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Đăng nhập
            </Link>
          )}

          <Link
            href="/checkout"
            className="relative flex items-center gap-1.5 bg-gray-900 text-white text-sm px-3 py-1.5 rounded-full hover:bg-gray-700 transition"
          >
            <span>🛒</span>
            <span>Giỏ Skill</span>
            {count > 0 && (
              <span className="absolute -top-1.5 -right-1.5 bg-coral-500 text-white text-xs w-4 h-4 rounded-full flex items-center justify-center font-bold">
                {count}
              </span>
            )}
          </Link>
        </div>
      </div>
    </header>
  );
}
