import { http } from "./http";

export type DailyStat = { day: string; goals: number; assists: number };

export type Player = {
  name: string;
  number: number;
  position: string;
  total_goals: number;
  total_assists: number;
  history: DailyStat[];
};

export type UpsertPayload = {
  day: string;
  player_name: string;
  player_number: number;
  position: string;
  goals: number;
  assists: number;
};

export function fetchPlayers() {
  return http<Player[]>("/players");
}

export function upsertStats(payload: UpsertPayload) {
  return http<{ success: boolean; action: string }>("/players/stats", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function deletePlayer(playerName: string) {
  return http<{ success: boolean; deleted_rows: number; player_name: string }>(
    `/players/${encodeURIComponent(playerName)}`,
    { method: "DELETE" }
  );
}
