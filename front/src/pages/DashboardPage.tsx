import { useCallback, useEffect, useState } from 'react'
import { listArtists } from '../api/artists'
import { listSongs } from '../api/songs'
import { listTags } from '../api/tags'
import { Alert } from '../components/ui/Alert'
import { Card } from '../components/ui/Card'
import { PageHeader } from '../components/ui/PageHeader'
import { ApiError } from '../types'

interface Stats {
  songs: number
  artists: number
  tags: number
}

export function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [songs, artists, tags] = await Promise.all([
        listSongs({ page: 1, size: 1 }),
        listArtists({ page: 1, size: 1 }),
        listTags({ page: 1, size: 1 }),
      ])
      setStats({
        songs: songs.total,
        artists: artists.total,
        tags: tags.total,
      })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Impossible de charger les statistiques.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const cards = [
    { label: 'Chansons', value: stats?.songs, icon: '♫', accent: true },
    { label: 'Artistes', value: stats?.artists, icon: '◎' },
    { label: 'Tags', value: stats?.tags, icon: '◈' },
  ]

  return (
    <div>
      <PageHeader
        title="Tableau de bord"
        description="Vue d'ensemble de votre catalogue musical."
      />
      {error ? (
        <Alert variant="error" onDismiss={() => setError(null)}>
          {error}
        </Alert>
      ) : null}
      <div className="stat-grid">
        {cards.map((card) => (
          <Card key={card.label}>
            <div className={`stat-card ${card.accent ? 'stat-card--accent' : ''}`}>
              <span className="stat-card__icon" aria-hidden>
                {card.icon}
              </span>
              <div>
                <p className="stat-card__label">{card.label}</p>
                <p className="stat-card__value">
                  {loading ? '—' : (card.value ?? 0)}
                </p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
