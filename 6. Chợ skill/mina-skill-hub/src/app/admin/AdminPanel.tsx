"use client";
import { useState } from "react";
import { createClient } from "@/lib/supabase-client";
import type { Skill } from "@/lib/types";

type Hall = { id: string; name: string; slug: string };

const TIERS = ["signature", "premium", "advanced", "master"];
const FILE_TYPES = ["pdf", "zip", "video", "gdoc"];

const EMPTY_FORM = {
  hall_id: "",
  name: "",
  description: "",
  price: 49000,
  tier: "signature",
  file_url: "",
  file_type: "pdf",
  icon: "🎯",
  is_active: true,
  order_index: 0,
};

export function AdminPanel({ halls, skills: initialSkills }: { halls: Hall[]; skills: Skill[] }) {
  const [skills, setSkills] = useState<Skill[]>(initialSkills);
  const [form, setForm] = useState({ ...EMPTY_FORM, hall_id: halls[0]?.id ?? "" });
  const [editing, setEditing] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const supabase = createClient();

  const save = async () => {
    setSaving(true);
    setMsg("");
    if (editing) {
      const { error } = await supabase.from("skills").update(form).eq("id", editing);
      if (!error) {
        setSkills(skills.map((s) => (s.id === editing ? { ...s, ...form } : s)));
        setMsg("Đã cập nhật!");
      }
    } else {
      const { data, error } = await supabase.from("skills").insert(form).select().single();
      if (!error && data) {
        setSkills([...skills, data as Skill]);
        setMsg("Đã thêm skill mới!");
      }
    }
    setEditing(null);
    setForm({ ...EMPTY_FORM, hall_id: halls[0]?.id ?? "" });
    setSaving(false);
  };

  const editSkill = (s: Skill) => {
    setEditing(s.id);
    setForm({
      hall_id: s.hall_id,
      name: s.name,
      description: s.description ?? "",
      price: s.price,
      tier: s.tier,
      file_url: s.file_url ?? "",
      file_type: s.file_type,
      icon: s.icon,
      is_active: s.is_active,
      order_index: s.order_index,
    });
  };

  const toggleActive = async (s: Skill) => {
    await supabase.from("skills").update({ is_active: !s.is_active }).eq("id", s.id);
    setSkills(skills.map((sk) => (sk.id === s.id ? { ...sk, is_active: !sk.is_active } : sk)));
  };

  const field = (key: keyof typeof form, label: string, type = "text") => (
    <div>
      <label className="text-xs font-medium text-gray-600">{label}</label>
      <input
        type={type}
        value={String(form[key])}
        onChange={(e) => setForm({ ...form, [key]: type === "number" ? Number(e.target.value) : e.target.value })}
        className="mt-0.5 w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-coral-400"
      />
    </div>
  );

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Admin · Quản lý Skill</h1>

      {/* Form thêm/sửa */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-10">
        <h2 className="font-semibold text-gray-900 mb-4">
          {editing ? "Chỉnh sửa Skill" : "Thêm Skill mới"}
        </h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-medium text-gray-600">Sảnh</label>
            <select
              value={form.hall_id}
              onChange={(e) => setForm({ ...form, hall_id: e.target.value })}
              className="mt-0.5 w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none"
            >
              {halls.map((h) => <option key={h.id} value={h.id}>{h.name}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-600">Tier</label>
            <select
              value={form.tier}
              onChange={(e) => setForm({ ...form, tier: e.target.value })}
              className="mt-0.5 w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none"
            >
              {TIERS.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          {field("name", "Tên Skill")}
          {field("icon", "Icon (emoji)")}
          {field("price", "Giá (VND)", "number")}
          {field("order_index", "Thứ tự", "number")}
          <div className="col-span-2">{field("description", "Mô tả ngắn")}</div>
          <div>
            <label className="text-xs font-medium text-gray-600">Loại file</label>
            <select
              value={form.file_type}
              onChange={(e) => setForm({ ...form, file_type: e.target.value })}
              className="mt-0.5 w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none"
            >
              {FILE_TYPES.map((t) => <option key={t} value={t}>{t.toUpperCase()}</option>)}
            </select>
          </div>
          <div className="col-span-2">{field("file_url", "Link file (Google Drive, Supabase Storage...)")}</div>
        </div>

        {msg && <p className="mt-3 text-sm text-green-600">{msg}</p>}

        <div className="flex gap-3 mt-4">
          <button
            onClick={save}
            disabled={saving}
            className="bg-gray-900 text-white px-5 py-2 rounded-xl text-sm font-semibold hover:bg-gray-700 disabled:opacity-50"
          >
            {saving ? "Đang lưu..." : editing ? "Cập nhật" : "Thêm Skill"}
          </button>
          {editing && (
            <button
              onClick={() => { setEditing(null); setForm({ ...EMPTY_FORM, hall_id: halls[0]?.id ?? "" }); }}
              className="text-sm text-gray-400 hover:text-gray-600 underline"
            >
              Huỷ
            </button>
          )}
        </div>
      </div>

      {/* Danh sách skill */}
      {halls.map((hall) => {
        const hallSkills = skills.filter((s) => s.hall_id === hall.id);
        return (
          <div key={hall.id} className="mb-8">
            <h3 className="font-semibold text-gray-700 mb-3">{hall.name}</h3>
            <div className="space-y-2">
              {hallSkills.map((s) => (
                <div key={s.id} className="flex items-center justify-between bg-white rounded-xl border border-gray-100 px-4 py-3">
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{s.icon}</span>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{s.name}</p>
                      <p className="text-xs text-gray-400">{s.tier} · {s.price.toLocaleString()}đ · {s.file_type.toUpperCase()}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => toggleActive(s)}
                      className={`text-xs px-2 py-0.5 rounded-full ${s.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}
                    >
                      {s.is_active ? "Active" : "Ẩn"}
                    </button>
                    <button
                      onClick={() => editSkill(s)}
                      className="text-xs text-gray-400 hover:text-gray-700 underline"
                    >
                      Sửa
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
