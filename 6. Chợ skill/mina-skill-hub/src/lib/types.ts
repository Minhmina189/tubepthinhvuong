export type Hall = {
  id: string;
  name: string;
  description: string;
  slug: string;
  order_index: number;
  skills?: Skill[];
};

export type Skill = {
  id: string;
  hall_id: string;
  name: string;
  description: string;
  price: number; // VND
  tier: "signature" | "premium" | "advanced" | "master";
  file_url: string | null;
  file_type: "pdf" | "zip" | "video" | "gdoc";
  icon: string;
  is_active: boolean;
  order_index: number;
};

export type Order = {
  id: string;
  user_id: string;
  order_code: string;
  total_amount: number;
  status: "pending" | "paid" | "expired";
  paid_at: string | null;
  created_at: string;
  order_items?: OrderItem[];
};

export type OrderItem = {
  id: string;
  order_id: string;
  skill_id: string;
  price: number;
  skill?: Skill;
};

export type Purchase = {
  id: string;
  user_id: string;
  skill_id: string;
  order_id: string;
  created_at: string;
  skill?: Skill;
};

export type CartItem = {
  skill: Skill;
  quantity: 1;
};

export const TIER_COLORS: Record<string, string> = {
  signature: "bg-gray-100 text-gray-700",
  premium: "bg-blue-100 text-blue-700",
  advanced: "bg-purple-100 text-purple-700",
  master: "bg-amber-100 text-amber-700",
};

export function formatVND(amount: number): string {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(amount);
}
