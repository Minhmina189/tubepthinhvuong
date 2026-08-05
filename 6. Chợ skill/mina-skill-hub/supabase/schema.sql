-- Chạy file này trong Supabase SQL Editor

create extension if not exists "uuid-ossp";

-- HALLS (3 sảnh)
create table halls (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  description text,
  slug text unique not null,
  order_index int not null default 0,
  created_at timestamptz default now()
);

-- SKILLS
create table skills (
  id uuid primary key default uuid_generate_v4(),
  hall_id uuid references halls(id) on delete cascade,
  name text not null,
  description text,
  price int not null,             -- VND
  tier text not null default 'signature', -- signature | premium | advanced | master
  file_url text,                  -- link tải (Supabase storage, Google Drive, v.v.)
  file_type text not null default 'pdf', -- pdf | zip | video | gdoc
  icon text default '🎯',
  is_active boolean default true,
  order_index int default 0,
  created_at timestamptz default now()
);

-- ORDERS
create table orders (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid references auth.users(id) on delete cascade,
  order_code text unique not null, -- MINA + 6 ký tự, dùng làm nội dung chuyển khoản
  total_amount int not null,       -- VND
  status text not null default 'pending', -- pending | paid | expired
  sepay_transaction_id text,
  paid_at timestamptz,
  created_at timestamptz default now()
);

-- ORDER ITEMS
create table order_items (
  id uuid primary key default uuid_generate_v4(),
  order_id uuid references orders(id) on delete cascade,
  skill_id uuid references skills(id),
  price int not null,
  created_at timestamptz default now()
);

-- PURCHASES (đã mua — dùng để kiểm tra quyền download)
create table purchases (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid references auth.users(id) on delete cascade,
  skill_id uuid references skills(id),
  order_id uuid references orders(id),
  created_at timestamptz default now(),
  unique(user_id, skill_id)
);

-- RLS
alter table halls enable row level security;
alter table skills enable row level security;
alter table orders enable row level security;
alter table order_items enable row level security;
alter table purchases enable row level security;

create policy "Public read halls" on halls for select using (true);
create policy "Public read active skills" on skills for select using (is_active = true);
create policy "Admin all skills" on skills for all using (true) with check (true);
create policy "Admin all halls" on halls for all using (true) with check (true);

create policy "Users read own orders" on orders for select using (auth.uid() = user_id);
create policy "Users insert own orders" on orders for insert with check (auth.uid() = user_id);

create policy "Users read own order_items" on order_items for select
  using (exists (select 1 from orders where orders.id = order_items.order_id and orders.user_id = auth.uid()));

create policy "Users read own purchases" on purchases for select using (auth.uid() = user_id);

-- Seed: 3 sảnh
insert into halls (name, description, slug, order_index) values
  ('Sảnh I · Skill Tạo Ảnh', 'Bộ kỹ năng AI tạo ảnh chuyên nghiệp', 'tao-anh', 1),
  ('Sảnh II · Skill Tạo Video', 'Tạo video viral với AI — nhanh, đẹp, không cần quay', 'tao-video', 2),
  ('Sảnh III · Skill Đặc Biệt', 'Skill AI nâng cao cho người bán hàng và sáng tạo nội dung', 'dac-biet', 3);

-- Seed: Skill Sảnh I — Tạo ảnh
insert into skills (hall_id, name, description, price, tier, file_type, icon, order_index)
select h.id, s.name, s.desc, s.price, s.tier, 'pdf', s.icon, s.idx
from halls h,
(values
  ('Prompt Midjourney Pro', 'Hơn 200 prompt Midjourney cho ảnh thương mại, KOL, sản phẩm', 49000, 'signature', '🎨', 1),
  ('Prompt Stable Diffusion', 'Workflow và prompt SD cho ảnh siêu thực', 49000, 'premium', '🖼️', 2),
  ('ComfyUI Workflow Pack', 'Bộ workflow ComfyUI sẵn dùng — upscale, portrait, logo', 75000, 'master', '⚙️', 3),
  ('Prompt DALL-E 3', '100 prompt DALL-E 3 tối ưu cho nội dung MXH', 49000, 'signature', '🤖', 4),
  ('AI Upscale & Enhance', 'Kỹ thuật nâng chất lượng ảnh AI lên 4K', 49000, 'advanced', '🔬', 5),
  ('Remove Background Pro', 'Script và workflow xóa nền hàng loạt bằng AI', 49000, 'signature', '✂️', 6),
  ('AI Color Grading', 'Chỉnh màu ảnh chuẩn thương hiệu với AI', 49000, 'premium', '🎨', 7),
  ('AI Logo Design', 'Tạo logo thương hiệu chuyên nghiệp bằng AI', 49000, 'advanced', '💎', 8),
  ('AI Portrait Pack', 'Tạo ảnh chân dung KOL, sản phẩm, quảng cáo', 75000, 'master', '📸', 9),
  ('Thumbnail Viral Kit', 'Template + prompt tạo thumbnail triệu view', 49000, 'premium', '🔥', 10)
) as s(name, desc, price, tier, icon, idx)
where h.slug = 'tao-anh';

-- Seed: Skill Sảnh II — Tạo video
insert into skills (hall_id, name, description, price, tier, file_type, icon, order_index)
select h.id, s.name, s.desc, s.price, s.tier, 'pdf', s.icon, s.idx
from halls h,
(values
  ('Prompt RunwayML Gen-3', '150 prompt video AI cho quảng cáo và MXH', 49000, 'signature', '🎬', 1),
  ('Sora Prompting Guide', 'Hướng dẫn viết prompt Sora — chuyển động cinematic', 49000, 'premium', '🎥', 2),
  ('Script Video Viral', 'Công thức và template viết kịch bản video triệu view', 75000, 'master', '📝', 3),
  ('AI Voiceover Pack', 'Kỹ thuật tạo giọng đọc AI chuyên nghiệp', 49000, 'advanced', '🎙️', 4),
  ('Lip Sync AI', 'Hướng dẫn sync môi vào video với AI', 49000, 'signature', '👄', 5),
  ('Intro & Outro Creator', 'Template tạo intro/outro thương hiệu bằng AI', 49000, 'premium', '🎞️', 6),
  ('Faceless Video System', 'Hệ thống tạo video không lộ mặt kiếm tiền TikTok/YT', 75000, 'master', '🎭', 7),
  ('Shorts AI Factory', 'Workflow tạo 10 Shorts/ngày bằng AI', 49000, 'advanced', '⚡', 8),
  ('Podcast AI Setup', 'Setup và tạo podcast AI hoàn toàn tự động', 49000, 'premium', '🎧', 9),
  ('B-Roll AI Pack', 'Thư viện B-roll AI + cách dùng trong edit', 49000, 'signature', '🎦', 10)
) as s(name, desc, price, tier, icon, idx)
where h.slug = 'tao-video';

-- Seed: Skill Sảnh III — Đặc biệt
insert into skills (hall_id, name, description, price, tier, file_type, icon, order_index)
select h.id, s.name, s.desc, s.price, s.tier, 'pdf', s.icon, s.idx
from halls h,
(values
  ('ChatGPT Prompt Master', 'Kho 300+ prompt ChatGPT cho kinh doanh và sáng tạo', 49000, 'signature', '🧠', 1),
  ('Make.com Automation Kit', 'Bộ blueprint Make.com tự động hoá bán hàng MXH', 75000, 'master', '⚙️', 2),
  ('Build AI Chatbot', 'Xây chatbot AI tư vấn bán hàng không cần code', 49000, 'advanced', '🤖', 3),
  ('Data Analysis AI', 'Phân tích dữ liệu kinh doanh bằng AI trong 30 phút', 49000, 'premium', '📊', 4),
  ('Email Marketing AI', 'Viết email bán hàng tự động bằng AI — open rate cao', 49000, 'signature', '📧', 5),
  ('SEO AI Toolkit', 'Bộ công cụ AI viết content chuẩn SEO', 49000, 'advanced', '🔍', 6),
  ('AI Sales Script', 'Kịch bản bán hàng AI cho livestream và nhắn tin', 75000, 'master', '💰', 7),
  ('Time Management AI', 'Hệ thống quản lý thời gian cho người bán hàng AI', 49000, 'premium', '⏰', 8),
  ('Market Research AI', 'Nghiên cứu thị trường và đối thủ bằng AI', 49000, 'signature', '🔎', 9),
  ('Personal Brand AI', 'Xây dựng thương hiệu cá nhân với AI từ A-Z', 75000, 'master', '👑', 10)
) as s(name, desc, price, tier, icon, idx)
where h.slug = 'dac-biet';
