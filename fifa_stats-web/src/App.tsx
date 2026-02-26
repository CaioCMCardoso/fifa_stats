import { PlayerForm } from "./components/PlayerForm";
import { PlayerList } from "./components/PlayerList";
import { usePlayers } from "./hooks/usePlayers";

export default function App() {
  const {
    leaderboard,
    teamTotals,
    topContributor,
    loading,
    error,
    form,
    setForm,
    loadPlayers,
    submit,
    removePlayer,
  } = usePlayers();

  const statCard: React.CSSProperties = {
    padding: 12,
    borderRadius: 12,
    border: "1px solid #374151",
    background: "#111827",
    color: "#fff",
    minWidth: 170,
  };

  const statLabel: React.CSSProperties = {
    fontSize: 12,
    opacity: 0.75,
  };

  const statValue: React.CSSProperties = {
    fontSize: 18,
    fontWeight: 800,
    marginTop: 6,
  };

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: 24, fontFamily: "system-ui" }}>
      <header style={{ marginBottom: 16 }}>
        <h1 style={{ margin: 0 }}>FIFA Stats</h1>
        <p style={{ marginTop: 6, opacity: 0.75 }}>Cadastro diário do time 🎮⚽</p>

        <button
          onClick={loadPlayers}
          disabled={loading}
          style={{ padding: "10px 14px", cursor: "pointer", marginTop: 10 }}
        >
          {loading ? "Carregando..." : "Recarregar"}
        </button>
        <div style={{ marginTop: 12, display: "flex", gap: 12, flexWrap: "wrap" }}>
          <div style={statCard}>
            <div style={statLabel}>Gols do time</div>
            <div style={statValue}>⚽ {teamTotals.goals}</div>
          </div>

          <div style={statCard}>
            <div style={statLabel}>Assists do time</div>
            <div style={statValue}>🅰️ {teamTotals.assists}</div>
          </div>

          <div style={statCard}>
            <div style={statLabel}>Top contribuição</div>
            <div style={statValue}>
              {topContributor ? `🔥 ${topContributor.name}` : "—"}
            </div>
          </div>
        </div>

        {error && <p style={{ color: "#fca5a5", marginTop: 10 }}>{error}</p>}
      </header>

      <PlayerForm value={form} onChange={setForm} onSubmit={submit} loading={loading} />
      <PlayerList players={leaderboard} loading={loading} onDelete={removePlayer} />
    </div>
  );
}
