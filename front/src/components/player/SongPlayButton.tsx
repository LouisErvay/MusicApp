import type { Song } from '../../types'
import { IconButton } from '../ui/IconButton'
import { useAudioPlayer } from './AudioPlayerContext'
import type { PlayerTrack } from './types'

function PlayIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M8 5.14v13.72L19 12 8 5.14z" />
    </svg>
  )
}

function PauseIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M6 5h4v14H6V5zm8 0h4v14h-4V5z" />
    </svg>
  )
}

function toPlayerTrack(song: Song): PlayerTrack {
  return { id: song.id, name: song.name, fileId: song.file_id }
}

interface SongPlayButtonProps {
  song: Song
  queue: Song[]
}

export function SongPlayButton({ song, queue }: SongPlayButtonProps) {
  const { play, togglePlay, isTrackActive, isTrackPlaying } = useAudioPlayer()

  const active = isTrackActive(song.id)
  const playing = isTrackPlaying(song.id)

  function handleClick() {
    if (active) {
      togglePlay()
      return
    }

    const tracks = queue.map(toPlayerTrack)
    const queueIndex = queue.findIndex((item) => item.id === song.id)

    play(toPlayerTrack(song), { queue: tracks, queueIndex })
  }

  return (
    <IconButton
      variant="accent"
      label={active && playing ? 'Pause' : 'Lecture'}
      onClick={handleClick}
    >
      {active && playing ? <PauseIcon /> : <PlayIcon />}
    </IconButton>
  )
}
