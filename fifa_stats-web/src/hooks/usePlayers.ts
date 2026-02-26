import { useEffect, useMemo, useState } from "react";
import { deletePlayer, fetchPlayers, upsertStats, type Player, type UpsertPayload } from "../api/players";

export function usePlayers() {
  const todayISO = new Date().toISOString().slice(0, 10);

  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  async function submit() {
    setLoading(true);
    setError(null);
    try {
      await upsertStats(form);
      setForm((f) => ({ ...f, goals: 0, assists: 0 }));
      await loadPlayers();
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
    } catch (e: any) {
      setError(e?.message ?? "Erro ao deletar jogador");
    } finally {
      setLoading(false);
    }
  }

  // equivalente ao ngOnInit: carrega ao montar
  useEffect(() => {
    loadPlayers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  

  return {
    players,
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
  };
}
