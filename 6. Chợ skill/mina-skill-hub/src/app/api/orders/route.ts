import { NextRequest, NextResponse } from "next/server";
import { createClient, createServiceRoleClient } from "@/lib/supabase-server";

function generateOrderCode(): string {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let code = "MINA";
  for (let i = 0; i < 6; i++) code += chars[Math.floor(Math.random() * chars.length)];
  return code;
}

export async function POST(req: NextRequest) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Chưa đăng nhập" }, { status: 401 });

  const body = await req.json();
  const items: { skillId: string; price: number }[] = body.items ?? [];
  if (!items.length) return NextResponse.json({ error: "Giỏ hàng trống" }, { status: 400 });

  const total = items.reduce((s, i) => s + i.price, 0);
  const orderCode = generateOrderCode();
  const service = createServiceRoleClient();

  const { data: order, error: orderErr } = await service
    .from("orders")
    .insert({ user_id: user.id, order_code: orderCode, total_amount: total, status: "pending" })
    .select()
    .single();

  if (orderErr || !order) return NextResponse.json({ error: "Tạo đơn thất bại" }, { status: 500 });

  await service.from("order_items").insert(
    items.map((i) => ({ order_id: order.id, skill_id: i.skillId, price: i.price }))
  );

  return NextResponse.json({ orderId: order.id, orderCode });
}
