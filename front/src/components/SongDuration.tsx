import { useEffect, useState } from 'react'
import { fileDownloadUrl } from '../api/config'
import { formatDuration } from '../utils/format'

const durationCache = new Map<string, number>()

interface SongDurationProps {
  fileId: string
}

export function SongDuration({ fileId }: SongDurationProps) {
  const cached = durationCache.get(fileId)
  const [duration, setDuration] = useState<number | null>(cached ?? null)

  useEffect(() => {
    if (durationCache.has(fileId)) {
      setDuration(durationCache.get(fileId)!)
      return
    }

    const audio = new Audio()
    audio.preload = 'metadata'

    function handleLoaded() {
      if (!Number.isFinite(audio.duration) || audio.duration <= 0) return
      durationCache.set(fileId, audio.duration)
      setDuration(audio.duration)
    }

    audio.addEventListener('loadedmetadata', handleLoaded)
    audio.src = fileDownloadUrl(fileId)

    return () => {
      audio.removeEventListener('loadedmetadata', handleLoaded)
      audio.src = ''
    }
  }, [fileId])

  if (duration === null) {
    return <span className="muted">—</span>
  }

  return <span className="muted song-duration">{formatDuration(duration)}</span>
}
