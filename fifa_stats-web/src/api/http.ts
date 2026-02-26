const BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

export async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status} em ${path}${text ? ` - ${text}` : ""}`);
  }

  return res.json() as Promise<T>;
}