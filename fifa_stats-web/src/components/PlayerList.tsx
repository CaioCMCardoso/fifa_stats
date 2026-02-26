import type { Player } from "../api/players";

type Props = {
  players: Player[];
  loading?: boolean;
  onDelete: (playerName: string) => void;
};

export function PlayerList({ players, loading, onDelete }: Props) {
  return (
    <section style={{ marginTop: 16, display: "grid", gap: 12 }}>
      {loading && players.length === 0 ? (
        <p>Carregando...</p>
      ) : players.length === 0 ? (
        <div style={{ padding: 12, border: "1px solid #374151", borderRadius: 12 }}>
          Nenhum jogador cadastrado ainda.
        </div>
      ) : (
        players.map((p) => (
          <div
            key={p.name}
            style={{
              padding: 14,
              border: "1px solid #374151",
              borderRadius: 12,
              background: "#111827",
              color: "#fff",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
              <strong>
                #{p.number} {p.name}
              </strong>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ opacity: 0.75 }}>{p.position}</span>
                <button
                  type="button"
                  onClick={() => {
                    if (window.confirm(`Deletar o jogador ${p.name}?`)) {
                      onDelete(p.name);
                    }
                  }}
                  disabled={loading}
                  aria-label={`Deletar ${p.name}`}
                  title={`Deletar ${p.name}`}
                  style={{
                    border: "1px solid #4b5563",
                    borderRadius: 8,
                    background: "transparent",
                    color: "#fca5a5",
                    cursor: loading ? "not-allowed" : "pointer",
                    padding: "4px 8px",
                  }}
                >
                  🗑️
                </button>
              </div>
            </div>

            <div style={{ marginTop: 8, display: "flex", gap: 16 }}>
              <span>⚽ {p.total_goals}</span>
              <span>🅰️ {p.total_assists}</span>
            </div>

            <details style={{ marginTop: 10 }}>
              <summary style={{ cursor: "pointer" }}>Histórico</summary>
              <ul style={{ marginTop: 8 }}>
                {p.history.map((h) => (
                  <li key={`${p.name}-${h.day}`}>
                    {h.day}: ⚽ {h.goals} | 🅰️ {h.assists}
                  </li>
                ))}
              </ul>
            </details>
          </div>
        ))
      )}
    </section>
  );
}
