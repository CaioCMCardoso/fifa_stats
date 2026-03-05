import type { TeamOverview } from "../api/team";

type Props = {
  value: TeamOverview | null;
  loading?: boolean;
  syncing?: boolean;
  syncMessage?: string | null;
  onSync: () => void;
};

export function TeamOverviewCard({ value, loading, syncing, syncMessage, onSync }: Props) {
  const cardStyle: React.CSSProperties = {
    padding: 14,
    borderRadius: 12,
    border: "1px solid #374151",
    background: "#111827",
    color: "#fff",
  };

  if (loading && !value) {
    return <section style={{ marginTop: 16 }}>Carregando dados do time...</section>;
  }

  if (!value) {
    return null;
  }

  return (
    <section style={{ marginTop: 16, textAlign: "left" }}>
      <div style={cardStyle}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
          <div>
            <h2 style={{ margin: 0 }}>Resumo do Time</h2>
            <p style={{ margin: "6px 0 0", opacity: 0.75 }}>
              Fonte externa: {value.source}
            </p>
          </div>

          <button
            type="button"
            onClick={onSync}
            disabled={!!syncing}
            style={{
              border: "1px solid #4b5563",
              borderRadius: 10,
              background: "#1f2937",
              color: "#fff",
              cursor: syncing ? "not-allowed" : "pointer",
              padding: "8px 12px",
              fontWeight: 700,
            }}
          >
            {syncing ? "Sincronizando..." : "Sincronizar jogadores"}
          </button>
        </div>

        {syncMessage && <p style={{ marginTop: 10, color: "#86efac" }}>{syncMessage}</p>}
        {!value.external_available && value.message && (
          <p style={{ marginTop: 10, color: "#fca5a5" }}>{value.message}</p>
        )}

        {value.team && (
          <div
            style={{
              marginTop: 12,
              display: "grid",
              gap: 8,
              gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
            }}
          >
            <Stat label="Clube" value={value.team.name ?? "-"} />
            <Stat label="Plataforma" value={value.team.platform ?? "-"} />
            <Stat label="Membros" value={value.team.members ?? "-"} />
            <Stat label="Campanha" value={`${value.team.wins ?? 0}-${value.team.draws ?? 0}-${value.team.losses ?? 0}`} />
            <Stat label="Pontos" value={value.team.points ?? "-"} />
            <Stat label="Gols (local)" value={value.local_totals.goals} />
          </div>
        )}

        {value.recent_matches.length > 0 && (
          <div style={{ marginTop: 14 }}>
            <strong>Ultimas partidas</strong>
            <ul style={{ marginTop: 8, paddingLeft: 18 }}>
              {value.recent_matches.map((m, index) => (
                <li key={m.match_id ?? `${m.day}-${index}`} style={{ marginTop: 4 }}>
                  {m.day ?? "sem data"} | {m.result ?? "?"}{" "}
                  {m.goals_for ?? "?"}-{m.goals_against ?? "?"}
                  {m.opponent ? ` vs ${m.opponent}` : ""}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div
      style={{
        padding: 10,
        borderRadius: 10,
        border: "1px solid #374151",
        background: "#0b1220",
      }}
    >
      <div style={{ fontSize: 12, opacity: 0.75 }}>{label}</div>
      <div style={{ marginTop: 4, fontWeight: 700 }}>{value}</div>
    </div>
  );
}
