export interface PinterestAccount {
  id: number;
  username: string;
  display_name: string;
  profile_image: string | null;
  connected_at: string;
}

export interface Board {
  id: string;
  name: string;
  pin_count: number;
  privacy: string;
}

export interface QueueItem {
  id: number;
  title: string;
  description: string;
  board_name: string;
  status: "queued" | "scheduled" | "posted" | "failed" | "duplicate" | "rate_limit";
  scheduled_for: string | null;
  posted_at: string | null;
  destination_link: string | null;
  error_message: string | null;
  image_filename: string | null;
}

export interface HistoryItem {
  id: number;
  title: string;
  board_name: string;
  status: string;
  detail: string;
  pinterest_pin_id: string | null;
  occurred_at: string;
}

export interface AnalyticsOverview {
  posted_today: number;
  posted_week: number;
  posted_month: number;
  failed_week: number;
  queued: number;
  daily_chart: { date: string; pins: number }[];
  "from config": { max_per_day: number };
}

export interface AIContent {
  title: string;
  description: string;
  hashtags: string;
  alt_text: string;
}
