import { createClient } from "@/lib/supabase-server";
import { SkillHall } from "@/components/SkillHall";
import type { Hall } from "@/lib/types";

export const revalidate = 60;

async function getHalls(): Promise<Hall[]> {
  const supabase = await createClient();
  const { data, error } = await supabase
    .from("halls")
    .select("*, skills(*)")
    .order("order_index")
    .order("order_index", { referencedTable: "skills" });

  if (error || !data) return [];
  return data as Hall[];
}

export default async function HomePage() {
  const halls = await getHalls();

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      {/* Hero */}
      <div className="text-center mb-16">
        <span className="inline-block border border-gray-300 text-gray-500 text-xs px-4 py-1.5 rounded-full mb-6 tracking-widest">
          SÀN GIAO DỊCH SKILL · 3 SẢNH ĐẲNG CẤP · TỪ 49.000Đ / SKILL
        </span>
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 leading-tight mb-4">
          Thế giới{" "}
          <span className="text-coral-500">Skill bán hàng</span>
          <br />
          chuyên nghiệp.
        </h1>
        <p className="text-gray-500 text-lg max-w-xl mx-auto">
          Chúng tôi không bán ảnh — chúng tôi trao bạn{" "}
          <strong className="text-gray-800">kỹ năng</strong>. Chọn Skill, kích
          hoạt và bán hàng như một KOL thực thụ.
        </p>
      </div>

      {/* Halls */}
      <div className="space-y-20">
        {halls.map((hall, i) => (
          <SkillHall key={hall.id} hall={hall} index={i} />
        ))}
      </div>
    </div>
  );
}
