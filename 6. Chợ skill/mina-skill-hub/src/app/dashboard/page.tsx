import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase-server";
import type { Purchase } from "@/lib/types";
import { formatVND } from "@/lib/types";

const FILE_TYPE_ICONS: Record<string, string> = {
  pdf: "📄",
  zip: "🗜️",
  video: "🎬",
  gdoc: "📝",
};

const FILE_TYPE_LABELS: Record<string, string> = {
  pdf: "PDF",
  zip: "ZIP",
  video: "Video",
  gdoc: "Google Doc",
};

export default async function DashboardPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/auth/login");

  const { data: purchases } = await supabase
    .from("purchases")
    .select("*, skill:skills(id, name, description, icon, file_type, tier, price)")
    .eq("user_id", user.id)
    .order("created_at", { ascending: false });

  const list = (purchases ?? []) as Purchase[];

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Skill của bạn</h1>
        <p className="text-sm text-gray-500 mt-1">{user.email} · {list.length} Skill đã kích hoạt</p>
      </div>

      {list.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-5xl mb-4">📦</p>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Chưa có Skill nào</h2>
          <p className="text-sm text-gray-500 mb-6">Hãy chọn Skill đầu tiên của bạn!</p>
          <a href="/" className="inline-block bg-gray-900 text-white px-6 py-2.5 rounded-xl text-sm font-semibold hover:bg-gray-700">
            Khám phá Skill
          </a>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {list.map((p) => {
            const skill = p.skill;
            if (!skill) return null;
            return (
              <div
                key={p.id}
                className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 flex flex-col"
              >
                <div className="flex items-start justify-between mb-3">
                  <span className="text-3xl">{skill.icon}</span>
                  <span className="text-xs text-gray-400 capitalize bg-gray-50 px-2 py-0.5 rounded-full">
                    {skill.tier}
                  </span>
                </div>
                <h3 className="font-semibold text-gray-900 text-sm mb-1">{skill.name}</h3>
                <p className="text-xs text-gray-500 line-clamp-2 flex-1">{skill.description}</p>

                <a
                  href={`/api/download/${skill.id}`}
                  className="mt-4 flex items-center justify-center gap-2 bg-gray-900 text-white py-2 rounded-xl text-sm font-semibold hover:bg-gray-700 transition"
                >
                  <span>{FILE_TYPE_ICONS[skill.file_type]}</span>
                  <span>Tải {FILE_TYPE_LABELS[skill.file_type]}</span>
                </a>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
