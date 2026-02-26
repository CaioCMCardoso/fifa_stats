export type DailyStat = {
  day: string; // "YYYY-MM-DD"
  goals: number;
  assists: number;
};

export type Player = {
  name: string;
  number: number;
  position: string;
  total_goals: number;
  total_assists: number;
  history: DailyStat[];
};

const BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

export async function fetchPlayers(): Promise<Player[]> {
  const res = await fetch(`${BASE_URL}/players`);
  if (!res.ok) {
    throw new Error(`Erro ao buscar jogadores: ${res.status}`);
  }
  return res.json();
}