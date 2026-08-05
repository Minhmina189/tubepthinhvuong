import { NextRequest, NextResponse } from "next/server";
import { createServiceRoleClient } from "@/lib/supabase-server";

// SePay gửi POST đến endpoint này sau khi phát hiện chuyển khoản
export async function POST(req: NextRequest) {
  // Xác thực secret từ SePay (cấu hình trong SePay dashboard)
  const secret = req.headers.get("x-sepay-token") ?? req.headers.get("authorization");
  if (
    process.env.SEPAY_WEBHOOK_SECRET &&
    secret !== process.env.SEPAY_WEBHOOK_SECRET &&
    secret !== `Bearer ${process.env.SEPAY_WEBHOOK_SECRET}`
  ) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await req.json();
  const content: string = (body.content ?? body.description ?? "").toUpperCase();
  const value: number = body.value ?? 0;

  // Tìm mã đơn hàng trong nội dung chuyển khoản (dạng MINAXXXXXX)
  const match = content.match(/MINA[A-Z0-9]{6}/);
  if (!match) return NextResponse.json({ success: true, note: "No order code found" });

  const orderCode = match[0];
  const service = createServiceRoleClient();

  // Tìm đơn hàng
  const { data: order } = await service
    .from("orders")
    .select("*, order_items(skill_id, price)")
    .eq("order_code", orderCode)
    .eq("status", "pending")
    .single();

  if (!order) return NextResponse.json({ success: true, note: "Order not found or already paid" });

  // Kiểm tra số tiền (cho phép sai lệch nhỏ 1000đ)
  if (Math.abs(value - order.total_amount) > 1000) {
    return NextResponse.json({ success: true, note: "Amount mismatch" });
  }

  // Cập nhật trạng thái đơn hàng
  await service
    .from("orders")
    .update({
      status: "paid",
      sepay_transaction_id: String(body.id ?? ""),
      paid_at: new Date().toISOString(),
    })
    .eq("id", order.id);

  // Tạo purchase records cho từng skill
  const purchases = order.order_items.map((item: { skill_id: string }) => ({
    user_id: order.user_id,
    skill_id: item.skill_id,
    order_id: order.id,
  }));

  await service.from("purchases").upsert(purchases, { onConflict: "user_id,skill_id" });

  return NextResponse.json({ success: true });
}
