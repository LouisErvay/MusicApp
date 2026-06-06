/** Nom affiché/envoyé : nom du fichier sans la dernière extension (max 100 car.). */
export function nameWithoutExtension(filename: string, maxLength = 100): string {
  const dot = filename.lastIndexOf('.')
  const base = dot > 0 ? filename.slice(0, dot) : filename
  const trimmed = base.trim()
  return (trimmed || filename).slice(0, maxLength)
}
