import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase-server";

// Trả về link download an toàn (chỉ sau khi đã mua)
export async function GET(
  _req: NextRequest,
  { params }: { params: { skillId: string } }
) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Chưa đăng nhập" }, { status: 401 });

  // Kiểm tra đã mua chưa
  const { data: purchase } = await supabase
    .from("purchases")
    .select("skill_id")
    .eq("user_id", user.id)
    .eq("skill_id", params.skillId)
    .single();

  if (!purchase) return NextResponse.json({ error: "Bạn chưa mua skill này" }, { status: 403 });

  // Lấy file_url
  const { data: skill } = await supabase
    .from("skills")
    .select("file_url, file_type, name")
    .eq("id", params.skillId)
    .single();

  if (!skill?.file_url) return NextResponse.json({ error: "File chưa có" }, { status: 404 });

  // Redirect trực tiếp đến URL (Google Drive, Supabase Storage, v.v.)
  return NextResponse.redirect(skill.file_url);
}
