"use client";
import { useCart } from "./CartProvider";
import type { Skill } from "@/lib/types";
import { TIER_COLORS, formatVND } from "@/lib/types";

const TIER_LABELS: Record<string, string> = {
  signature: "Signature",
  premium: "Premium",
  advanced: "Advanced",
  master: "Master",
};

export function SkillCard({ skill }: { skill: Skill }) {
  const { addItem, items } = useCart();
  const inCart = items.some((i) => i.skill.id === skill.id);

  return (
    <div className="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-shadow border border-gray-100 flex flex-col">
      {/* Card image area */}
      <div className="relative bg-gradient-to-br from-[#e87070] to-[#c05050] h-44 flex items-center justify-center">
        <span className="text-5xl">{skill.icon}</span>
        <span className={`absolute top-3 left-3 tier-badge ${TIER_COLORS[skill.tier]}`}>
          {TIER_LABELS[skill.tier]}
        </span>
        <span className="absolute top-3 right-3 bg-white/90 text-gray-800 text-xs font-semibold px-2 py-0.5 rounded-full">
          {formatVND(skill.price)}
        </span>
      </div>

      {/* Card body */}
      <div className="p-4 flex flex-col flex-1">
        <p className="text-xs text-gray-400 mb-1">Skill</p>
        <h3 className="font-semibold text-gray-900 text-sm leading-snug mb-1">
          {skill.name}
        </h3>
        <p className="text-xs text-gray-500 line-clamp-2 flex-1">{skill.description}</p>

        <button
          onClick={() => addItem(skill)}
          disabled={inCart}
          className={`mt-3 w-full py-2 rounded-xl text-sm font-semibold transition ${
            inCart
              ? "bg-green-100 text-green-700 cursor-default"
              : "bg-gray-900 text-white hover:bg-gray-700"
          }`}
        >
          {inCart ? "✓ Đã thêm vào giỏ" : `Kích hoạt Skill · ${formatVND(skill.price)}`}
        </button>
      </div>
    </div>
  );
}
