import { http } from "./http";

export type TeamMatch = {
  match_id: string | null;
  day: string | null;
  goals_for: number | null;
  goals_against: number | null;
  result: "W" | "D" | "L" | null;
  opponent: string | null;
};

export type TeamOverview = {
  external_available: boolean;
  source: string;
  local_totals: {
    players: number;
    goals: number;
    assists: number;
  };
  team: {
    club_id: string | null;
    name: string | null;
    platform: string | null;
    region: string | null;
    members: number | null;
    wins: number | null;
    draws: number | null;
    losses: number | null;
    points: number | null;
  } | null;
  recent_matches: TeamMatch[];
  message: string | null;
};

export type TeamSyncPayload = {
  days_back: number;
  max_matches: number;
  dry_run: boolean;
};

export type TeamSyncResult = {
  success: boolean;
  dry_run: boolean;
  club_id: string | null;
  days_back: number;
  matches_scanned: number;
  rows_prepared: number;
  rows_upserted: number;
  players_touched: string[];
};

export function fetchTeamOverview() {
  return http<TeamOverview>("/team/overview");
}

export function syncTeamStats(payload: TeamSyncPayload) {
  return http<TeamSyncResult>("/team/sync", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
