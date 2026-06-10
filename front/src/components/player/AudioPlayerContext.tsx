import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import { fileDownloadUrl } from '../../api/config'
import type { PlayOptions, PlaybackRate, PlayerTrack } from './types'
import { PLAYBACK_RATES } from './types'

export interface AudioPlayerState {
  track: PlayerTrack | null
  isPlaying: boolean
  currentTime: number
  duration: number
  volume: number
  playbackRate: PlaybackRate
  queue: PlayerTrack[]
  queueIndex: number
}

export interface AudioPlayerActions {
  play: (track: PlayerTrack, options?: PlayOptions) => void
  togglePlay: () => void
  pause: () => void
  resume: () => void
  next: () => void
  previous: () => void
  seek: (time: number) => void
  setVolume: (volume: number) => void
  setPlaybackRate: (rate: PlaybackRate) => void
  isTrackActive: (trackId: number) => boolean
  isTrackPlaying: (trackId: number) => boolean
}

export type AudioPlayerContextValue = AudioPlayerState & AudioPlayerActions

const AudioPlayerContext = createContext<AudioPlayerContextValue | null>(null)

function toPlaybackRate(value: number): PlaybackRate {
  return PLAYBACK_RATES.includes(value as PlaybackRate) ? (value as PlaybackRate) : 1
}

export function AudioPlayerProvider({ children }: { children: ReactNode }) {
  const audioRef = useRef<HTMLAudioElement>(null)

  const [track, setTrack] = useState<PlayerTrack | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolumeState] = useState(1)
  const [playbackRate, setPlaybackRateState] = useState<PlaybackRate>(1)
  const [queue, setQueue] = useState<PlayerTrack[]>([])
  const [queueIndex, setQueueIndex] = useState(-1)

  const loadTrack = useCallback((nextTrack: PlayerTrack, autoplay: boolean) => {
    const audio = audioRef.current
    if (!audio) return

    setTrack(nextTrack)
    setCurrentTime(0)
    setDuration(0)
    audio.src = fileDownloadUrl(nextTrack.fileId)
    audio.load()

    if (autoplay) {
      void audio.play().then(() => setIsPlaying(true)).catch(() => setIsPlaying(false))
    } else {
      audio.pause()
      setIsPlaying(false)
    }
  }, [])

  const playAtIndex = useCallback(
    (index: number, tracks: PlayerTrack[]) => {
      if (index < 0 || index >= tracks.length) return
      setQueue(tracks)
      setQueueIndex(index)
      loadTrack(tracks[index], true)
    },
    [loadTrack],
  )

  const play = useCallback(
    (nextTrack: PlayerTrack, options?: PlayOptions) => {
      const nextQueue = options?.queue ?? [nextTrack]
      const index =
        options?.queueIndex ??
        nextQueue.findIndex((item) => item.id === nextTrack.id)

      if (track?.id === nextTrack.id) {
        void audioRef.current?.play().then(() => setIsPlaying(true)).catch(() => setIsPlaying(false))
        return
      }

      setQueue(nextQueue)
      setQueueIndex(index >= 0 ? index : 0)
      loadTrack(nextTrack, true)
    },
    [loadTrack, track?.id],
  )

  const pause = useCallback(() => {
    audioRef.current?.pause()
    setIsPlaying(false)
  }, [])

  const resume = useCallback(() => {
    if (!track) return
    void audioRef.current?.play().then(() => setIsPlaying(true)).catch(() => setIsPlaying(false))
  }, [track])

  const togglePlay = useCallback(() => {
    if (!track) return
    if (isPlaying) pause()
    else resume()
  }, [isPlaying, pause, resume, track])

  const next = useCallback(() => {
    if (queue.length === 0 || queueIndex < 0) return
    const nextIndex = queueIndex + 1
    if (nextIndex >= queue.length) return
    playAtIndex(nextIndex, queue)
  }, [playAtIndex, queue, queueIndex])

  const previous = useCallback(() => {
    const audio = audioRef.current
    if (!audio || queue.length === 0 || queueIndex < 0) return

    if (audio.currentTime > 3) {
      audio.currentTime = 0
      setCurrentTime(0)
      return
    }

    const prevIndex = queueIndex - 1
    if (prevIndex < 0) {
      audio.currentTime = 0
      setCurrentTime(0)
      return
    }

    playAtIndex(prevIndex, queue)
  }, [playAtIndex, queue, queueIndex])

  const seek = useCallback((time: number) => {
    const audio = audioRef.current
    if (!audio) return
    const clamped = Math.max(0, Math.min(time, audio.duration || time))
    audio.currentTime = clamped
    setCurrentTime(clamped)
  }, [])

  const setVolume = useCallback((value: number) => {
    const clamped = Math.max(0, Math.min(1, value))
    if (audioRef.current) audioRef.current.volume = clamped
    setVolumeState(clamped)
  }, [])

  const setPlaybackRate = useCallback((rate: PlaybackRate) => {
    const safe = toPlaybackRate(rate)
    if (audioRef.current) audioRef.current.playbackRate = safe
    setPlaybackRateState(safe)
  }, [])

  const isTrackActive = useCallback((trackId: number) => track?.id === trackId, [track?.id])

  const isTrackPlaying = useCallback(
    (trackId: number) => track?.id === trackId && isPlaying,
    [isPlaying, track?.id],
  )

  useEffect(() => {
    const audioEl = audioRef.current
    if (!audioEl) return

    audioEl.volume = volume
    audioEl.playbackRate = playbackRate

    function handleTimeUpdate() {
      const el = audioRef.current
      if (!el) return
      setCurrentTime(el.currentTime)
    }

    function handleLoadedMetadata() {
      const el = audioRef.current
      if (!el || !Number.isFinite(el.duration)) return
      setDuration(el.duration)
    }

    function handleEnded() {
      if (queue.length > 0 && queueIndex >= 0 && queueIndex < queue.length - 1) {
        playAtIndex(queueIndex + 1, queue)
        return
      }
      setIsPlaying(false)
      setCurrentTime(0)
    }

    function handlePlay() {
      setIsPlaying(true)
    }

    function handlePause() {
      setIsPlaying(false)
    }

    audioEl.addEventListener('timeupdate', handleTimeUpdate)
    audioEl.addEventListener('loadedmetadata', handleLoadedMetadata)
    audioEl.addEventListener('ended', handleEnded)
    audioEl.addEventListener('play', handlePlay)
    audioEl.addEventListener('pause', handlePause)

    return () => {
      audioEl.removeEventListener('timeupdate', handleTimeUpdate)
      audioEl.removeEventListener('loadedmetadata', handleLoadedMetadata)
      audioEl.removeEventListener('ended', handleEnded)
      audioEl.removeEventListener('play', handlePlay)
      audioEl.removeEventListener('pause', handlePause)
    }
  }, [playAtIndex, playbackRate, queue, queueIndex, volume])

  const value = useMemo<AudioPlayerContextValue>(
    () => ({
      track,
      isPlaying,
      currentTime,
      duration,
      volume,
      playbackRate,
      queue,
      queueIndex,
      play,
      togglePlay,
      pause,
      resume,
      next,
      previous,
      seek,
      setVolume,
      setPlaybackRate,
      isTrackActive,
      isTrackPlaying,
    }),
    [
      track,
      isPlaying,
      currentTime,
      duration,
      volume,
      playbackRate,
      queue,
      queueIndex,
      play,
      togglePlay,
      pause,
      resume,
      next,
      previous,
      seek,
      setVolume,
      setPlaybackRate,
      isTrackActive,
      isTrackPlaying,
    ],
  )

  return (
    <AudioPlayerContext.Provider value={value}>
      <audio ref={audioRef} preload="metadata" />
      {children}
    </AudioPlayerContext.Provider>
  )
}

export function useAudioPlayer(): AudioPlayerContextValue {
  const ctx = useContext(AudioPlayerContext)
  if (!ctx) {
    throw new Error('useAudioPlayer doit être utilisé dans un AudioPlayerProvider.')
  }
  return ctx
}
