import { ApiError } from '../types'
import { API_URL } from './config'

async function parseError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: string | { msg: string }[] }
    if (typeof body.detail === 'string') return body.detail
    if (Array.isArray(body.detail)) {
      return body.detail.map((d) => d.msg).join(', ')
    }
  } catch {
    /* ignore */
  }
  return res.statusText || `Erreur ${res.status}`
}

export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, init)
  if (!res.ok) {
    throw new ApiError(await parseError(res), res.status)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export async function apiFetchForm<T>(
  path: string,
  formData: FormData,
  method = 'POST',
): Promise<T> {
  return apiFetch<T>(path, { method, body: formData })
}
