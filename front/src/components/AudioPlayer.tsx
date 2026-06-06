import { fileDownloadUrl } from '../api/config'
import './AudioPlayer.css'

interface AudioPlayerProps {
  fileId: string
  label?: string
}

export function AudioPlayer({ fileId, label }: AudioPlayerProps) {
  return (
    <div className="audio-player">
      {label ? <span className="audio-player__label">{label}</span> : null}
      <audio controls preload="none" src={fileDownloadUrl(fileId)} className="audio-player__el">
        Votre navigateur ne supporte pas la lecture audio.
      </audio>
    </div>
  )
}
