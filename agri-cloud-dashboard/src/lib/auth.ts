import { betterAuth } from "better-auth";
import { mongodbAdapter } from "better-auth/adapters/mongodb";
import { MongoClient } from "mongodb";
import { hashPassword, verifyPassword } from "./password";

if (!process.env.MONGODB_URI) {
  throw new Error("Missing MONGODB_URI");
}

const client = new MongoClient(process.env.MONGODB_URI);
const db = client.db("agri_smart_db");

/**
 * Resilient baseURL resolution for Vercel, Docker, and Localhost
 */
const getBaseURL = (): string => {
  let url =
    process.env.BETTER_AUTH_URL ||
    process.env.NEXT_PUBLIC_APP_URL ||
    process.env.VERCEL_URL ||
    "http://localhost:3000";

  // Ensure valid URL protocol prefix
  if (!url.startsWith("http://") && !url.startsWith("https://")) {
    url = `https://${url}`;
  }

  // Remove any trailing slash
  return url.replace(/\/+$/, "");
};

export const auth = betterAuth({
  baseURL: getBaseURL(),
  secret: process.env.BETTER_AUTH_SECRET || "a_random_32_character_secret_key_sih2026",
  database: mongodbAdapter(db),
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 6,
    password: {
      hash: hashPassword,
      verify: verifyPassword,
    },
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    },
  },
  user: {
    additionalFields: {
      role: {
        type: "string",
        required: false,
        defaultValue: "FARMER",
      },
    },
  },
});