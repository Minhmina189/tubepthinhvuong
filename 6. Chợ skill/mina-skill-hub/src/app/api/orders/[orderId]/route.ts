import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase-server";

export async function GET(
  _req: NextRequest,
  { params }: { params: { orderId: string } }
) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { data } = await supabase
    .from("orders")
    .select("status")
    .eq("id", params.orderId)
    .eq("user_id", user.id)
    .single();

  return NextResponse.json({ status: data?.status ?? "unknown" });
}
