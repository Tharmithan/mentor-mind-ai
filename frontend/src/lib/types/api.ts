export type DocumentMeta = {
  document_id: string;
  filename: string;
  uploaded_at: string;
  num_pages: number;
  num_chunks: number;
  total_chars: number;
  chunk_size: number;
  chunk_overlap: number;
  indexed: boolean;
  embedding_model?: string | null;
};

export type DocumentChunk = {
  chunk_id: string;
  document_id: string;
  chunk_index: number;
  text: string;
  char_count: number;
  page?: number | null;
};

export type UploadResponse = {
  message: string;
  document: DocumentMeta;
  preview_chunks: DocumentChunk[];
};

export type DocumentListResponse = {
  count: number;
  documents: DocumentMeta[];
};

export type SearchResult = {
  chunk_id: string;
  document_id: string;
  filename: string;
  page?: number | null;
  chunk_index: number;
  text: string;
  similarity: number;
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type ChatRequest = {
  question: string;
  top_k?: number;
  document_id?: string | null;
  mode?: "explain" | "summarize" | "example" | null;
  session_id?: string | null;
  history?: ChatMessage[];
};

export type ChatResponse = {
  answer: string;
  used_llm: boolean;
  model?: string | null;
  sources: SearchResult[];
  session_id?: string | null;
};

export type ConversationResponse = {
  session_id: string;
  messages: ChatMessage[];
  last_document_id?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type StudyToolRequest = {
  document_id?: string | null;
  topic?: string | null;
  count?: number;
};

export type SummaryResponse = {
  title: string;
  summary: string;
  key_points: string[];
  used_llm: boolean;
  source?: string | null;
};

export type QuizQuestion = {
  question: string;
  options: string[];
  answer_index: number;
  explanation?: string | null;
};

export type QuizResponse = {
  questions: QuizQuestion[];
  used_llm: boolean;
  source?: string | null;
};

export type Flashcard = {
  front: string;
  back: string;
};

export type FlashcardResponse = {
  flashcards: Flashcard[];
  used_llm: boolean;
  source?: string | null;
};

export type ExplainSimpleResponse = {
  concept: string;
  explanation: string;
  analogy?: string | null;
  used_llm: boolean;
};

export type RevisionResponse = {
  title: string;
  quick_notes: string[];
  key_formulas: string[];
  must_know: string[];
  used_llm: boolean;
  source?: string | null;
};

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

export type StudentRiskDetection = {
  high_risk: boolean;
  low_performance_chance: number;
  burnout_probability: number;
};

export type PredictResponse = {
  prediction: string;
  confidence: number;
  predicted_score: number;
  risk_level: string;
  recommendation: string;
  model_version: string;
  student_risk: StudentRiskDetection;
};

export type FeatureContribution = {
  feature: string;
  label: string;
  contribution_pct: number;
  direction: string;
  raw_value?: number | null;
};

export type ExplainResponse = {
  prediction: PredictResponse;
  method: string;
  algorithm: string;
  explanations: string[];
  contributions: FeatureContribution[];
  top_feature: string | null;
  summary: string;
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

export type RiskMeter = {
  burnout_risk: number;
  exam_failure_risk: number;
  low_engagement_score: number;
};

export type AnalyticsCards = {
  ai_score: number;
  risk_level: string;
  performance_trend_delta: number;
  study_streak_days: number;
};

export type AnalyticsDashboard = {
  cards: AnalyticsCards;
  risk_meter: RiskMeter;
  weekly_progress: ChartPoint[];
  subject_comparison: ChartPoint[];
  confidence_trends: ChartPoint[];
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
  analytics?: AnalyticsDashboard | null;
};

// --- Week 6: AI Agent Copilot ---

export type AgentInfo = {
  id: string;
  label: string;
  description: string;
  examples: string[];
};

export type AgentAction = {
  type: string;
  path?: string | null;
  tool?: string | null;
  tab?: string | null;
  topic?: string | null;
  session_id?: string | null;
};

export type AgentContribution = {
  agent: string;
  agent_label: string;
  summary: string;
  sub_intent: string;
  data?: Record<string, unknown> | null;
};

export type AgentChatRequest = {
  message: string;
  session_id?: string | null;
  document_id?: string | null;
  interview_session_id?: string | null;
  resume_text?: string | null;
  context?: Record<string, unknown> | null;
  collaborate?: boolean;
};

export type AgentChatResponse = {
  answer: string;
  session_id: string;
  agent: string;
  agent_label: string;
  confidence: number;
  route_reason: string;
  sub_intent?: string | null;
  used_llm?: boolean;
  actions?: AgentAction[];
  sources?: SearchResult[] | null;
  collaboration?: boolean;
  contributions?: AgentContribution[] | null;
  shared_memory?: Record<string, unknown> | null;
  orchestration_log?: Record<string, unknown>[] | null;
};

// --- Week 6 Day 2: Study Agent tutor ---

export type StudyPlanDay = {
  day: number;
  phase: string;
  focus: string;
  tasks: string[];
  duration_hours: number;
  resources: string[];
};

export type ExamStudyPlanRequest = {
  subject: string;
  days?: number;
  hours_per_day?: number;
  document_id?: string | null;
};

export type ExamStudyPlanResponse = {
  subject: string;
  days: number;
  hours_per_day: number;
  summary: string;
  phases: string[];
  schedule: StudyPlanDay[];
  tips: string[];
  used_llm?: boolean;
};

export type LearningGoal = {
  id: string;
  title: string;
  subject: string;
  target_days?: number | null;
  target_date?: string | null;
  progress_pct: number;
  milestones_completed: string[];
  notes: string[];
  created_at: string;
  updated_at: string;
};

export type DailyStudyRecommendation = {
  title: string;
  description: string;
  subject: string;
  priority: string;
  estimated_minutes: number;
};

export type DailyStudyRecommendationsResponse = {
  summary: string;
  weak_subjects: Array<{
    subject: string;
    score: number;
    priority: string;
    suggested_topics: string[];
    resources: string[];
    daily_minutes: number;
  }>;
  recommendations: DailyStudyRecommendation[];
  focus_areas: string[];
  study_streak_tip: string;
};

// --- Week 6 Day 3: Career Agent ---

export type CareerMatch = {
  career_id: string;
  title: string;
  match_score: number;
  rationale: string;
  strengths: string[];
  gaps: string[];
};

export type CareerRecommendationResponse = {
  top_career: CareerMatch;
  alternatives: CareerMatch[];
  profile_summary: string;
  analyzed: Record<string, unknown>;
  used_llm?: boolean;
};

export type SkillGapItem = {
  skill: string;
  current_level: number;
  required_level: number;
  gap: number;
  priority: string;
  learning_actions: string[];
};

export type SkillGapAnalysisResponse = {
  target_career: string;
  overall_readiness: number;
  gaps: SkillGapItem[];
  summary: string;
};

export type CareerRoadmapPhase = {
  phase: string;
  duration_weeks: number;
  goals: string[];
  skills: string[];
  resources: string[];
};

export type LearningRoadmapResponse = {
  career: string;
  total_weeks: number;
  phases: CareerRoadmapPhase[];
  summary: string;
  milestones: string[];
};

export type CareerAnalysisRequest = {
  interests?: string[] | null;
  target_career?: string | null;
  subject_scores?: Record<string, number> | null;
  interview_session_id?: string | null;
};

// --- Week 6 Day 4: Resume Analyzer ---

export type ATSCheckItem = {
  category: string;
  label: string;
  passed: boolean;
  score: number;
  detail: string;
};

export type MissingSkill = {
  skill: string;
  importance: string;
  suggestion: string;
};

export type WeakBullet = {
  text: string;
  issue: string;
  suggestion: string;
};

export type ResumeFeedbackItem = {
  category: string;
  priority: string;
  message: string;
};

export type ResumeSection = {
  name: string;
  content: string;
  line_count: number;
};

export type ResumeAnalysisResponse = {
  analysis_id: string;
  filename?: string | null;
  word_count: number;
  page_estimate: number;
  sections: ResumeSection[];
  ats_score: number;
  ats_grade: string;
  ats_checks: ATSCheckItem[];
  missing_skills: MissingSkill[];
  weak_bullets: WeakBullet[];
  formatting_issues: string[];
  feedback: ResumeFeedbackItem[];
  summary: string;
  headline: string;
  used_llm?: boolean;
};

export type ResumeTextAnalyzeRequest = {
  text: string;
  target_role?: string | null;
};

// --- Week 6 Day 5: Personalized Learning Planner ---

export type MonthlyTopic = {
  name: string;
  description: string;
  resources: string[];
};

export type MonthlyPhase = {
  month: number;
  title: string;
  topics: MonthlyTopic[];
  goals: string[];
  hours_per_week: number;
  milestone: string;
};

export type MilestoneStatus = {
  id: string;
  label: string;
  month: number;
  completed: boolean;
  completed_at?: string | null;
};

export type LearningRoadmapRequest = {
  goal: string;
  hours_per_week?: number;
  total_months?: number | null;
};

export type LearningRoadmapResponse = {
  goal: string;
  career_id: string;
  career_title: string;
  total_months: number;
  hours_per_week: number;
  summary: string;
  months: MonthlyPhase[];
  milestones: MilestoneStatus[];
};

export type LearningPlanResponse = {
  plan_id: string;
  goal: string;
  career_title: string;
  progress_pct: number;
  current_month: number;
  current_week: number;
  hours_per_week: number;
  roadmap: LearningRoadmapResponse;
  milestones: MilestoneStatus[];
  created_at: string;
  updated_at: string;
};

export type LearningPlanProgressUpdate = {
  milestone_id?: string | null;
  current_month?: number | null;
  current_week?: number | null;
  progress_pct?: number | null;
  note?: string | null;
};

// --- Week 6 Day 7: AI Coach Dashboard ---

export type CoachScoreCard = {
  label: string;
  score: number;
  delta: number;
  trend: string;
  subtitle: string;
};

export type CoachRecommendation = {
  id: string;
  title: string;
  description: string;
  agent: string;
  priority: string;
  action_path?: string | null;
};

export type SkillGapOverview = {
  target_career: string;
  current_skills: string[];
  missing_skills: string[];
  overall_readiness: number;
  gaps: SkillGapItem[];
};

export type CoachCharts = {
  skill_growth: ChartPoint[];
  learning_progress: ChartPoint[];
  interview_improvement: ChartPoint[];
  career_readiness_trend: ChartPoint[];
};

export type WeeklyProgressReport = {
  week_label: string;
  achievements: string[];
  weaknesses: string[];
  next_week_plan: string[];
  generated_at: string;
};

export type CoachOverviewResponse = {
  scores: CoachScoreCard[];
  charts: CoachCharts;
  skill_gap: SkillGapOverview;
  recommendations: CoachRecommendation[];
  weekly_report: WeeklyProgressReport;
  target_career: string;
  profile_summary: string;
};

// --- Week 7 Day 1: User Personalization Engine ---

export type LearningPreferences = {
  primary_style: string;
  style_scores: Record<string, number>;
  preferred_session_minutes: number;
  preferred_study_time: string;
  content_formats: string[];
  updated_at?: string | null;
};

export type UnifiedUserProfile = {
  user_id: string;
  email?: string | null;
  full_name: string;
  subject_scores: Record<string, number>;
  weak_subjects: string[];
  strong_subjects: string[];
  learning_preferences: LearningPreferences;
  career_goal?: string | null;
  interests: string[];
  interview_avg_score?: number | null;
  performance_score: number;
  study_hours_week: number;
  profile_summary: string;
  created_at: string;
  updated_at: string;
};

export type PersonalizedResource = {
  title: string;
  description: string;
  format: string;
  style: string;
  subject: string;
  priority: string;
  url_hint?: string | null;
};

export type PersonalizedRecommendationsResponse = {
  user_id: string;
  learning_style: string;
  style_rationale: string;
  weak_subjects: string[];
  strong_subjects: string[];
  resources: PersonalizedResource[];
  study_actions: string[];
  career_note?: string | null;
  used_embedding: boolean;
};

export type PreferencesUpdateRequest = {
  primary_style?: string;
  style_scores?: Record<string, number>;
  preferred_session_minutes?: number;
  preferred_study_time?: string;
  content_formats?: string[];
};
