export interface PlayerTrack {
  id: number
  name: string
  fileId: string
}

export interface PlayOptions {
  queue?: PlayerTrack[]
  queueIndex?: number
}

export const PLAYBACK_RATES = [0.5, 0.75, 1, 1.25, 1.5, 2] as const

export type PlaybackRate = (typeof PLAYBACK_RATES)[number]
