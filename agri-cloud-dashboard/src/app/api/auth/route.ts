import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json(
    { message: "Authentication endpoint initialized." },
    { status: 200 }
  );
}
