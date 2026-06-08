import { useAudioPlayer } from '../player/AudioPlayerContext'
import { PLAYBACK_RATES, type PlaybackRate } from '../player/types'
import { formatDuration } from '../utils/format'
import { IconButton } from './IconButton'
import './SidebarPlayer.css'

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

function PreviousIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M6 6h2v12H6V6zm4 6 8-6v12l-8-6z" />
    </svg>
  )
}

function NextIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M16 6h2v12h-2V6zM6 12l8 6V6L6 12z" />
    </svg>
  )
}

function VolumeIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
      <path d="M11 5 6 9H3v6h3l5 4V5z" strokeLinejoin="round" />
      <path d="M15.5 8.5a5 5 0 0 1 0 7" strokeLinecap="round" />
    </svg>
  )
}

export function SidebarPlayer() {
  const {
    track,
    isPlaying,
    currentTime,
    duration,
    volume,
    playbackRate,
    queue,
    queueIndex,
    togglePlay,
    next,
    previous,
    seek,
    setVolume,
    setPlaybackRate,
  } = useAudioPlayer()

  const hasPrevious = queueIndex > 0 || currentTime > 3
  const hasNext = queue.length > 0 && queueIndex >= 0 && queueIndex < queue.length - 1
  const progress = duration > 0 ? (currentTime / duration) * 100 : 0

  return (
    <div className="sidebar-player">
      <p className="sidebar-player__title" title={track?.name}>
        {track?.name ?? 'Aucune lecture'}
      </p>

      <div className="sidebar-player__progress">
        <input
          type="range"
          className="sidebar-player__slider sidebar-player__slider--progress"
          min={0}
          max={duration || 0}
          step={0.1}
          value={Math.min(currentTime, duration || 0)}
          disabled={!track || duration <= 0}
          onChange={(e) => seek(Number(e.target.value))}
          aria-label="Position dans la chanson"
        />
        <div className="sidebar-player__times">
          <span>{formatDuration(currentTime)}</span>
          <span>{duration > 0 ? formatDuration(duration) : '--:--:--'}</span>
        </div>
      </div>

      <div className="sidebar-player__controls">
        <IconButton
          label="Précédent"
          onClick={previous}
          disabled={!track || !hasPrevious}
        >
          <PreviousIcon />
        </IconButton>
        <IconButton
          variant="accent"
          label={isPlaying ? 'Pause' : 'Lecture'}
          onClick={togglePlay}
          disabled={!track}
        >
          {isPlaying ? <PauseIcon /> : <PlayIcon />}
        </IconButton>
        <IconButton label="Suivant" onClick={next} disabled={!track || !hasNext}>
          <NextIcon />
        </IconButton>
      </div>

      <div className="sidebar-player__footer">
        <div className="sidebar-player__volume">
          <VolumeIcon />
          <input
            type="range"
            className="sidebar-player__slider"
            min={0}
            max={1}
            step={0.01}
            value={volume}
            onChange={(e) => setVolume(Number(e.target.value))}
            aria-label="Volume"
          />
        </div>

        <label className="sidebar-player__speed">
          <span className="sidebar-player__speed-label">Vitesse</span>
          <select
            className="sidebar-player__speed-select"
            value={playbackRate}
            disabled={!track}
            onChange={(e) => setPlaybackRate(Number(e.target.value) as PlaybackRate)}
            aria-label="Vitesse de lecture"
          >
            {PLAYBACK_RATES.map((rate) => (
              <option key={rate} value={rate}>
                {rate}x
              </option>
            ))}
          </select>
        </label>
      </div>

      <div
        className="sidebar-player__progress-fill"
        style={{ width: `${progress}%` }}
        aria-hidden
      />
    </div>
  )
}
