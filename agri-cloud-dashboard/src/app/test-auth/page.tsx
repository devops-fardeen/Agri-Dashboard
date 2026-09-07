import { redirect } from "next/navigation";

export default function TestAuthPage() {
  redirect("/login");
}