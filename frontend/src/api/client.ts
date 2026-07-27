import type { ClassDetail, Language, SearchResponse, TreeNodeData } from "./types";

const API_BASE_URL: string =
  (import.meta as unknown as { env: Record<string, string | undefined> }).env
    .VITE_API_BASE_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Erreur API (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export function search(query: string, lang?: Language): Promise<SearchResponse> {
  const params = new URLSearchParams({ q: query });
  if (lang) params.set("lang", lang);
  return getJson(`/search?${params.toString()}`);
}

export function getClassDetail(ifcClass: string): Promise<ClassDetail> {
  return getJson(`/class/${encodeURIComponent(ifcClass)}`);
}

export function getTree(): Promise<TreeNodeData> {
  return getJson(`/tree`);
}
