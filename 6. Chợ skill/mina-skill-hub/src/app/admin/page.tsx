import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase-server";
import { AdminPanel } from "./AdminPanel";

export default async function AdminPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user || user.email !== process.env.ADMIN_EMAIL) redirect("/");

  const { data: halls } = await supabase
    .from("halls")
    .select("id, name, slug")
    .order("order_index");

  const { data: skills } = await supabase
    .from("skills")
    .select("*")
    .order("order_index");

  return <AdminPanel halls={halls ?? []} skills={skills ?? []} />;
}
