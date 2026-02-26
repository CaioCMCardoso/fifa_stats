import type { UpsertPayload } from "../api/players";

const POSITIONS = [
  "GK",
  "RB", "RWB", "CB", "LB", "LWB",
  "CDM", "CM", "CAM",
  "RM", "RW",
  "LM", "LW",
  "CF", "ST",
] as const;

type Props = {
  value: UpsertPayload;
  onChange: (next: UpsertPayload) => void;
  onSubmit: () => void;
  loading?: boolean;
};

export function PlayerForm({ value, onChange, onSubmit, loading }: Props) {
  const inputStyle: React.CSSProperties = {
    padding: "10px 12px",
    borderRadius: 10,
    border: "1px solid #374151",
    background: "#111827",
    color: "#fff",
    outline: "none",
  };

  return (
    <section style={{ marginTop: 20 }}>
      <h2>Registrar partida</h2>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit();
        }}
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: 12,
          marginTop: 12,
          padding: 14,
          borderRadius: 12,
          border: "1px solid #374151",
          background: "#0b1220",
          color: "#fff",
        }}
      >
        <label style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: 13 }}>
          Dia
          <input
            type="date"
            value={value.day}
            onChange={(e) => onChange({ ...value, day: e.target.value })}
            style={inputStyle}
            required
          />
        </label>

        <label style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: 13 }}>
          Nome do jogador
          <input
            placeholder="Ex: Caio"
            value={value.player_name}
            onChange={(e) => onChange({ ...value, player_name: e.target.value })}
            style={inputStyle}
            required
          />
        </label>

        <label style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: 13 }}>
          Nº da camisa
          <input
            type="number"
            min={0}
            max={99}
            placeholder="Ex: 9"
            value={value.player_number}
            onChange={(e) => onChange({ ...value, player_number: Number(e.target.value) })}
            style={inputStyle}
            required
          />
        </label>

        <label style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: 13 }}>
          Posição
          <select
            value={value.position}
            onChange={(e) => onChange({ ...value, position: e.target.value })}
            style={inputStyle}
            required
          >
            {POSITIONS.map((pos) => (
              <option key={pos} value={pos}>
                {pos}
              </option>
            ))}
          </select>
        </label>

        <label style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: 13 }}>
          Gols
          <input
            type="number"
            min={0}
            placeholder="0"
            value={value.goals}
            onChange={(e) => onChange({ ...value, goals: Number(e.target.value) })}
            style={inputStyle}
          />
        </label>

        <label style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: 13 }}>
          Assistências
          <input
            type="number"
            min={0}
            placeholder="0"
            value={value.assists}
            onChange={(e) => onChange({ ...value, assists: Number(e.target.value) })}
            style={inputStyle}
          />
        </label>

        <button
          type="submit"
          disabled={!!loading}
          style={{
            gridColumn: "1 / -1",
            padding: "12px 14px",
            borderRadius: 12,
            border: 0,
            fontWeight: 800,
            cursor: loading ? "not-allowed" : "pointer",
            opacity: loading ? 0.7 : 1,
            background: "#22c55e",
            color: "#06220f",
          }}
        >
          {loading ? "Salvando..." : "Salvar stats"}
        </button>

        <div style={{ gridColumn: "1 / -1", fontSize: 12, opacity: 0.75 }}>
          Dica: se cadastrar o mesmo <b>Nome + Dia</b>, você edita os stats daquele dia.
        </div>
      </form>
    </section>
  );
}