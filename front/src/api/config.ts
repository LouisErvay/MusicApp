export const API_URL = import.meta.env.API_URL ?? 'http://localhost:8000'

export function fileDownloadUrl(fileId: string): string {
  return `${API_URL}/files/${fileId}/download`
}
