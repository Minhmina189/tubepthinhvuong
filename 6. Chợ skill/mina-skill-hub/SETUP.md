# Mina Skill Hub — Hướng dẫn cài đặt

## Bước 1: Cài Node.js

Tải và cài tại: https://nodejs.org (chọn LTS)
Sau khi cài xong, mở terminal và chạy: `node --version`

## Bước 2: Cài dependencies

```bash
cd "mina-skill-hub"
npm install
```

## Bước 3: Tạo Supabase project

1. Vào https://supabase.com → New project
2. Vào **SQL Editor** → chạy toàn bộ file `supabase/schema.sql`
3. Lấy **Project URL** và **anon key** từ Settings > API

## Bước 4: Tạo file .env.local

Copy file `.env.example` thành `.env.local` và điền:

```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...

SEPAY_WEBHOOK_SECRET=mật_khẩu_bạn_tự_đặt

NEXT_PUBLIC_BANK_CODE=VCB          # Mã ngân hàng (VCB, TCB, MB, VPB...)
NEXT_PUBLIC_BANK_ACCOUNT=1234567890
NEXT_PUBLIC_BANK_ACCOUNT_NAME=NGUYEN VAN A

ADMIN_EMAIL=email_admin@gmail.com
```

## Bước 5: Cấu hình SePay webhook

1. Vào SePay dashboard → Cài đặt webhook
2. URL: `https://your-domain.vercel.app/api/webhook/sepay`
3. Secret: điền cùng giá trị với `SEPAY_WEBHOOK_SECRET` ở trên

## Bước 6: Chạy local

```bash
npm run dev
```

Mở trình duyệt: http://localhost:3000

## Bước 7: Deploy lên Vercel

1. Upload code lên GitHub
2. Vào https://vercel.com → Import project từ GitHub
3. Điền các biến môi trường (từ .env.local) vào Vercel Environment Variables
4. Deploy!

## Thêm skill file

Trong Admin panel (`/admin`):
- Đăng nhập bằng email admin
- Chọn skill → Sửa → Điền link file vào ô "Link file"
- Link có thể là: Google Drive (shared link), Supabase Storage URL, v.v.

## Danh sách tài khoản ngân hàng VietQR

- VCB = Vietcombank
- TCB = Techcombank  
- MB = MB Bank
- VPB = VPBank
- ACB = ACB
- BIDV = BIDV
- ICB = VietinBank
