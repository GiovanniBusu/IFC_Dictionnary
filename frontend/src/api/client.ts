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

export function search(query: string, lang?: Language, outputLang?: Language): Promise<SearchResponse> {
  const params = new URLSearchParams({ q: query });
  if (lang) params.set("lang", lang);
  if (outputLang) params.set("output_lang", outputLang);
  return getJson(`/search?${params.toString()}`);
}

export function getClassDetail(ifcClass: string, outputLang?: Language): Promise<ClassDetail> {
  const params = new URLSearchParams();
  if (outputLang) params.set("output_lang", outputLang);
  const qs = params.toString();
  return getJson(`/class/${encodeURIComponent(ifcClass)}${qs ? `?${qs}` : ""}`);
}

export function getTree(outputLang?: Language): Promise<TreeNodeData> {
  const params = new URLSearchParams();
  if (outputLang) params.set("output_lang", outputLang);
  const qs = params.toString();
  return getJson(`/tree${qs ? `?${qs}` : ""}`);
}
