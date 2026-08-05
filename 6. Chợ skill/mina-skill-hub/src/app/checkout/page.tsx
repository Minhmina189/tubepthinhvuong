"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useCart } from "@/components/CartProvider";
import { createClient } from "@/lib/supabase-client";
import { formatVND } from "@/lib/types";

type CheckoutState = "cart" | "qr" | "paid";

export default function CheckoutPage() {
  const { items, total, clearCart } = useCart();
  const [state, setState] = useState<CheckoutState>("cart");
  const [orderId, setOrderId] = useState("");
  const [orderCode, setOrderCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  const supabase = createClient();

  const bankCode = process.env.NEXT_PUBLIC_BANK_CODE ?? "VCB";
  const bankAccount = process.env.NEXT_PUBLIC_BANK_ACCOUNT ?? "";
  const bankName = process.env.NEXT_PUBLIC_BANK_ACCOUNT_NAME ?? "MINA SKILL HUB";

  const qrUrl = `https://img.vietqr.io/image/${bankCode}-${bankAccount}-compact2.png?amount=${total}&addInfo=${orderCode}&accountName=${encodeURIComponent(bankName)}`;

  const createOrder = async () => {
    setLoading(true);
    setError("");
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      router.push("/auth/login");
      return;
    }
    const res = await fetch("/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: items.map((i) => ({ skillId: i.skill.id, price: i.skill.price })) }),
    });
    const json = await res.json();
    if (!res.ok) {
      setError(json.error ?? "Có lỗi xảy ra, thử lại nhé");
      setLoading(false);
      return;
    }
    setOrderId(json.orderId);
    setOrderCode(json.orderCode);
    setState("qr");
    setLoading(false);
  };

  // Poll for payment confirmation
  useEffect(() => {
    if (state !== "qr" || !orderId) return;
    pollRef.current = setInterval(async () => {
      const res = await fetch(`/api/orders/${orderId}`);
      const json = await res.json();
      if (json.status === "paid") {
        clearTimeout(pollRef.current!);
        setState("paid");
        clearCart();
        setTimeout(() => router.push("/dashboard"), 2000);
      }
    }, 3000);
    return () => clearInterval(pollRef.current!);
  }, [state, orderId]);

  if (items.length === 0 && state === "cart") {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <p className="text-5xl mb-4">🛒</p>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Giỏ Skill đang trống</h2>
        <p className="text-sm text-gray-500 mb-6">Hãy chọn Skill bạn muốn kích hoạt nhé!</p>
        <a href="/" className="inline-block bg-gray-900 text-white px-6 py-2.5 rounded-xl text-sm font-semibold hover:bg-gray-700">
          Khám phá Skill
        </a>
      </div>
    );
  }

  if (state === "paid") {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <p className="text-5xl mb-4">🎉</p>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Thanh toán thành công!</h2>
        <p className="text-sm text-gray-500">Đang chuyển đến trang Skill của bạn...</p>
      </div>
    );
  }

  if (state === "qr") {
    return (
      <div className="max-w-md mx-auto px-4 py-12">
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 text-center">
          <h2 className="font-bold text-gray-900 text-lg mb-1">Quét QR để thanh toán</h2>
          <p className="text-sm text-gray-500 mb-4">
            Chuyển khoản đúng nội dung:{" "}
            <span className="font-mono font-bold text-gray-900">{orderCode}</span>
          </p>

          <div className="relative inline-block">
            <Image src={qrUrl} alt="QR thanh toán" width={260} height={260} className="rounded-xl mx-auto" />
          </div>

          <div className="mt-4 bg-amber-50 border border-amber-200 rounded-xl p-3 text-sm text-amber-800">
            <strong>Số tiền:</strong> {formatVND(total)}<br />
            <strong>Nội dung CK:</strong> {orderCode}<br />
            <strong>Ngân hàng:</strong> {bankCode} · {bankAccount}
          </div>

          <p className="mt-4 text-xs text-gray-400 animate-pulse">
            ⏳ Đang chờ xác nhận thanh toán...
          </p>

          <button
            onClick={() => { setState("cart"); clearInterval(pollRef.current!); }}
            className="mt-4 text-xs text-gray-400 hover:text-gray-600 underline"
          >
            Huỷ và quay lại giỏ
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-12">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Xác nhận đơn hàng</h1>

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm divide-y divide-gray-50">
        {items.map(({ skill }) => (
          <div key={skill.id} className="flex items-center justify-between px-5 py-4">
            <div className="flex items-center gap-3">
              <span className="text-2xl">{skill.icon}</span>
              <div>
                <p className="text-sm font-medium text-gray-900">{skill.name}</p>
                <p className="text-xs text-gray-400 capitalize">{skill.tier}</p>
              </div>
            </div>
            <span className="text-sm font-semibold text-gray-900">{formatVND(skill.price)}</span>
          </div>
        ))}
        <div className="flex items-center justify-between px-5 py-4 bg-gray-50">
          <span className="font-bold text-gray-900">Tổng cộng</span>
          <span className="font-bold text-lg text-coral-500">{formatVND(total)}</span>
        </div>
      </div>

      {error && <p className="mt-3 text-sm text-red-500 text-center">{error}</p>}

      <button
        onClick={createOrder}
        disabled={loading}
        className="mt-6 w-full bg-gray-900 text-white py-3.5 rounded-xl font-semibold hover:bg-gray-700 transition disabled:opacity-50"
      >
        {loading ? "Đang tạo đơn..." : "Thanh toán qua QR Banking"}
      </button>
      <p className="mt-3 text-center text-xs text-gray-400">
        Thanh toán qua VietQR · Tự động mở khóa sau khi chuyển khoản
      </p>
    </div>
  );
}
