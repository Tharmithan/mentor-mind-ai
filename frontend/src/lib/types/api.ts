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
  attendance: number;
  sleep_hours?: number;
  /** @deprecated use attendance */
  attendance_pct?: number;
  prior_score?: number;
  quizzes_completed?: number;
};

export type PredictResponse = {
  prediction: string;
  confidence: number;
  predicted_score: number;
  risk_level: string;
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
  action_type?: string;
};

export type SubjectScoreInput = {
  subject: string;
  score: number;
};

export type PersonalizedRecommendationsRequest = {
  study_hours?: number;
  attendance_pct?: number;
  sleep_hours?: number;
  past_failures?: number;
  subject_scores?: SubjectScoreInput[];
  predicted_score?: number;
  risk_level?: string;
};

export type PersonalizedRecommendationsResponse = {
  recommendations: RecommendationItem[];
  weak_subjects: SubjectScoreInput[];
  revision_order: string[];
  collaborative_insights: string[];
  focus_message: string;
};

export type TimetableSlot = {
  day: string;
  time_slot: string;
  subject: string;
  topic: string;
  duration_hours: number;
  priority: string;
  task: string;
};

export type FocusArea = {
  subject: string;
  topic: string;
  score: number;
  priority_rank: number;
};

export type DailyStudyPlannerResponse = {
  revision_priority: string[];
  focus_areas: FocusArea[];
  weekly_study_hours: number;
  timetable: TimetableSlot[];
  collaborative_insights: string[];
  summary: string;
  recommendations: RecommendationItem[];
};

export type DailyTip = {
  tip: string;
  category: string;
  focus_topic: string | null;
};

export type AIInsight = {
  id: string;
  category: string;
  message: string;
  severity: string;
  metric?: string | null;
  trend_direction?: string | null;
  impact_pct?: number | null;
};

export type PerformanceSummary = {
  headline: string;
  overall_score: number;
  trend_label: string;
  highlights: string[];
  summary_text: string;
};

export type InsightsRequest = {
  study_hours?: number;
  attendance_pct?: number;
  sleep_hours?: number;
  subject_scores?: SubjectScoreInput[];
  previous_attendance_pct?: number;
  previous_subject_scores?: SubjectScoreInput[];
};

export type InsightsResponse = {
  generated_at: string;
  insights: AIInsight[];
  trends: AIInsight[];
  performance_summary: PerformanceSummary;
  cohort_stats: Record<string, number>;
};

export type InsightsReportResponse = {
  generated_at: string;
  natural_language_report: string;
  llm_enhanced: boolean;
  performance_summary: PerformanceSummary;
  insights: AIInsight[];
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
