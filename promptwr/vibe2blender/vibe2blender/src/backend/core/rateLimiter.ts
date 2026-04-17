import { HttpError } from 'wasp/server';

interface RateLimitConfig {
  windowMs: number;
  max: number;
}

const storage = new Map<string, { count: number; resetAt: number }>();

/**
 * A simple in-memory leaky bucket rate limiter.
 * In a real production environment, this should be backed by Redis.
 */
export const checkRateLimit = (key: string, config: RateLimitConfig) => {
  const now = Date.now();
  const entry = storage.get(key);

  if (!entry || now > entry.resetAt) {
    storage.set(key, { count: 1, resetAt: now + config.windowMs });
    return;
  }

  if (entry.count >= config.max) {
    const retryAfter = Math.ceil((entry.resetAt - now) / 1000);
    throw new HttpError(429, 'TOO_MANY_REQUESTS', { retryAfter });
  }

  entry.count += 1;
};

export const CHAT_LIMIT = { windowMs: 60 * 1000, max: 20 }; // 20 RPM
export const GENERATE_LIMIT = { windowMs: 60 * 1000, max: 5 }; // 5 RPM
