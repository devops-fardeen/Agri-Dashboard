import crypto from "crypto";

/**
 * Enterprise-grade cryptographic password hashing with Salt + Pepper + Scrypt KDF.
 * 
 * Format stored in database:
 * scrypt$N=32768,r=8,p=1$<salt_hex>$<derived_key_hex>
 */

const PEPPER = process.env.BETTER_AUTH_SECRET || "agri_smart_salt_pepper_sih2026";
const SALT_BYTES = 32; // 256-bit cryptographically secure random salt
const KEY_LEN = 64; // 512-bit derived key
const SCRYPT_PARAMS = { N: 32768, r: 8, p: 1, maxmem: 64 * 1024 * 1024 };

/**
 * Generates a cryptographically secure random 256-bit salt and hashes the password using Scrypt KDF + Pepper.
 */
export async function hashPassword(password: string): Promise<string> {
  const salt = crypto.randomBytes(SALT_BYTES).toString("hex");
  const peppered = `${password}:${PEPPER}`;

  return new Promise((resolve, reject) => {
    crypto.scrypt(peppered, salt, KEY_LEN, SCRYPT_PARAMS, (err, derivedKey) => {
      if (err) return reject(err);
      const hashString = `scrypt$N=${SCRYPT_PARAMS.N},r=${SCRYPT_PARAMS.r},p=${SCRYPT_PARAMS.p}$${salt}$${derivedKey.toString("hex")}`;
      resolve(hashString);
    });
  });
}

/**
 * Constant-time / timing-safe password verification matching salted hash against user input.
 */
export async function verifyPassword({
  password,
  hash,
}: {
  password: string;
  hash: string;
}): Promise<boolean> {
  if (!hash || !password) return false;

  // 1. If hash is in our custom salted scrypt format
  if (hash.startsWith("scrypt$")) {
    const parts = hash.split("$");
    if (parts.length < 4) return false;

    const salt = parts[2];
    const storedKeyHex = parts[3];
    const peppered = `${password}:${PEPPER}`;

    return new Promise((resolve) => {
      crypto.scrypt(peppered, salt, KEY_LEN, SCRYPT_PARAMS, (err, derivedKey) => {
        if (err) return resolve(false);
        try {
          const storedBuffer = Buffer.from(storedKeyHex, "hex");
          if (storedBuffer.length !== derivedKey.length) {
            return resolve(false);
          }
          const isMatch = crypto.timingSafeEqual(storedBuffer, derivedKey);
          resolve(isMatch);
        } catch {
          resolve(false);
        }
      });
    });
  }

  // 2. Fallback to Better-Auth default verify for existing accounts
  try {
    const { verifyPassword: defaultVerify } = await import("@better-auth/utils/password");
    return await defaultVerify(hash, password);
  } catch {
    return false;
  }
}
