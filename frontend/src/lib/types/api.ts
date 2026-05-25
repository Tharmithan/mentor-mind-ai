export type HealthResponse = {
  status: string;
  service: string;
  version: string;
  database: string;
};

export type UserProfile = {
  id: string;
  email: string;
  full_name: string;
  role: string;
  xp: number;
  streak_days: number;
  performance_score: number;
};

export type UserResponse = {
  user: UserProfile;
};

export type PredictRequest = {
  study_hours: number;
  attendance_pct: number;
  prior_score: number;
  quizzes_completed?: number;
};

export type PredictResponse = {
  predicted_score: number;
  risk_level: string;
  confidence: number;
  recommendation: string;
  model_version: string;
};

export type ChartPoint = {
  label: string;
  value: number;
};

export type WeakSubject = {
  subject: string;
  score: number;
};

export type RecommendationItem = {
  id: string;
  title: string;
  description: string;
  topic: string;
  priority: string;
  is_completed: boolean;
};

export type DashboardResponse = {
  performance_score: number;
  study_hours_week: number;
  weak_subjects: WeakSubject[];
  ai_suggestions_count: number;
  study_hours_by_day: ChartPoint[];
  performance_trend: ChartPoint[];
  subject_distribution: ChartPoint[];
  recommendations: RecommendationItem[];
};
