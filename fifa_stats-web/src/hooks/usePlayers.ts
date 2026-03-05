import { useEffect, useMemo, useState } from "react";
import { deletePlayer, fetchPlayers, upsertStats, type Player, type UpsertPayload } from "../api/players";
import { fetchTeamOverview, syncTeamStats, type TeamOverview } from "../api/team";

export function usePlayers() {
  const todayISO = new Date().toISOString().slice(0, 10);

  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(false);
  const [teamLoading, setTeamLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [teamOverview, setTeamOverview] = useState<TeamOverview | null>(null);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  const [form, setForm] = useState<UpsertPayload>({
    day: todayISO,
    player_name: "",
    player_number: 0,
    position: "ST",
    goals: 0,
    assists: 0,
  });

  const leaderboard = useMemo(() => {
    // cópia para não mutar o array original
    return [...players].sort((a, b) => {
      // ordena por gols, depois assists
      if (b.total_goals !== a.total_goals) return b.total_goals - a.total_goals;
      return b.total_assists - a.total_assists;
    });
  }, [players]);

  const teamTotals = useMemo(() => {
    return players.reduce(
      (acc, p) => {
        acc.goals += p.total_goals;
        acc.assists += p.total_assists;
        return acc;
      },
      { goals: 0, assists: 0 }
    );
  }, [players]);

  const topContributor = useMemo(() => {
    if (players.length === 0) return null;

    return [...players].sort((a, b) => {
      const aScore = a.total_goals + a.total_assists;
      const bScore = b.total_goals + b.total_assists;
      return bScore - aScore;
    })[0];
  }, [players]);

  async function loadPlayers() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchPlayers();
      setPlayers(data);
    } catch (e: any) {
      setError(e?.message ?? "Erro ao buscar jogadores");
    } finally {
      setLoading(false);
    }
  }

  async function loadTeam() {
    setTeamLoading(true);
    try {
      const data = await fetchTeamOverview();
      setTeamOverview(data);
    } catch (e: any) {
      setError(e?.message ?? "Erro ao buscar dados do time");
    } finally {
      setTeamLoading(false);
    }
  }

  async function submit() {
    setLoading(true);
    setError(null);
    try {
      await upsertStats(form);
      setForm((f) => ({ ...f, goals: 0, assists: 0 }));
      await loadPlayers();
      await loadTeam();
    } catch (e: any) {
      setError(e?.message ?? "Erro ao salvar stats");
    } finally {
      setLoading(false);
    }
  }

  async function removePlayer(playerName: string) {
    setLoading(true);
    setError(null);
    try {
      await deletePlayer(playerName);
      await loadPlayers();
      await loadTeam();
    } catch (e: any) {
      setError(e?.message ?? "Erro ao deletar jogador");
    } finally {
      setLoading(false);
    }
  }

  // equivalente ao ngOnInit: carrega ao montar
  useEffect(() => {
    loadPlayers();
    loadTeam();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function syncTeamPlayers() {
    setSyncing(true);
    setSyncMessage(null);
    setError(null);

    try {
      const result = await syncTeamStats({
        days_back: 7,
        max_matches: 20,
        dry_run: false,
      });
      setSyncMessage(
        `Sync concluido: ${result.rows_upserted} registros atualizados para ${result.players_touched.length} jogadores.`
      );
      await loadPlayers();
      await loadTeam();
    } catch (e: any) {
      setError(e?.message ?? "Erro ao sincronizar time");
    } finally {
      setSyncing(false);
    }
  }

  return {
    players,
    leaderboard,
    teamTotals,
    topContributor,
    loading,
    teamLoading,
    syncing,
    error,
    teamOverview,
    syncMessage,
    form,
    setForm,
    loadPlayers,
    loadTeam,
    submit,
    removePlayer,
    syncTeamPlayers,
  };
}
