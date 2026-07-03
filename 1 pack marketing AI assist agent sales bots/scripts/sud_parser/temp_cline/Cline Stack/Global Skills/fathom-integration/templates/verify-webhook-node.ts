import crypto from 'node:crypto';

type HeaderMap = Record<string, string | string[] | undefined>;

function readHeader(headers: HeaderMap, name: string): string | null {
  const direct = headers[name];
  const lower = headers[name.toLowerCase()];
  const value = direct ?? lower;

  if (Array.isArray(value)) {
    return value[0] ?? null;
  }
  return value ?? null;
}

export function verifyFathomWebhook(
  webhookSecret: string,
  headers: HeaderMap,
  rawBody: string,
  toleranceSeconds = 300,
): boolean {
  // Нужен именно raw body, ещё до JSON.parse.
  const webhookId = readHeader(headers, 'webhook-id');
  const webhookTimestamp = readHeader(headers, 'webhook-timestamp');
  const webhookSignature = readHeader(headers, 'webhook-signature');

  if (!webhookId || !webhookTimestamp || !webhookSignature) {
    return false;
  }

  const timestamp = Number.parseInt(webhookTimestamp, 10);
  const now = Math.floor(Date.now() / 1000);
  if (!Number.isFinite(timestamp) || Math.abs(now - timestamp) > toleranceSeconds) {
    return false;
  }

  const encodedSecret = webhookSecret.startsWith('whsec_')
    ? webhookSecret.slice('whsec_'.length)
    : webhookSecret;

  const secretBytes = Buffer.from(encodedSecret, 'base64');
  const signedContent = `${webhookId}.${webhookTimestamp}.${rawBody}`;
  const expectedSignature = crypto
    .createHmac('sha256', secretBytes)
    .update(signedContent)
    .digest('base64');

  const signatures = webhookSignature
    .split(' ')
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => {
      const parts = item.split(',');
      return parts.length > 1 ? parts[1] : parts[0];
    });

  return signatures.some((signature) => {
    const left = Buffer.from(expectedSignature);
    const right = Buffer.from(signature);
    if (left.length !== right.length) {
      return false;
    }
    return crypto.timingSafeEqual(left, right);
  });
}
