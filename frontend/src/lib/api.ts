import axios from "axios";
import type {
  ChatRequest,
  ChatResponse,
  ConversationResponse,
  DailyStudyPlannerResponse,
  DailyTip,
  DashboardResponse,
  DocumentListResponse,
  ExplainSimpleResponse,
  FlashcardResponse,
  InsightsReportResponse,
  InsightsResponse,
  PersonalizedRecommendationsRequest,
  PersonalizedRecommendationsResponse,
  ExplainResponse,
  PredictRequest,
  PredictResponse,
  QuizResponse,
  RevisionResponse,
  StudyToolRequest,
  SummaryResponse,
  UploadResponse,
  UserResponse,
  AgentChatRequest,
  AgentChatResponse,
  AgentInfo,
  ExamStudyPlanRequest,
  ExamStudyPlanResponse,
  DailyStudyRecommendationsResponse,
  LearningGoal,
  CareerAnalysisRequest,
  CareerRecommendationResponse,
  SkillGapAnalysisResponse,
  LearningRoadmapResponse,
  ResumeAnalysisResponse,
  ResumeTextAnalyzeRequest,
  LearningRoadmapRequest,
  LearningRoadmapResponse,
  LearningPlanResponse,
  LearningPlanProgressUpdate,
  CoachOverviewResponse,
  WeeklyProgressReport,
  UnifiedUserProfile,
  PersonalizedRecommendationsResponse,
  PreferencesUpdateRequest,
  MemoryProgressResponse,
  MemoryContextResponse,
  LearningAnalyticsDashboard,
  WeeklyReportData,
  MonthlyReportData,
  EmailReportResponse,
  MLOpsStatus,
  ModelVersion,
  ExperimentRun,
  ExperimentComparison,
  RunExperimentRequest,
} from "@/lib/types/api";
import type {
  CoachReport,
  EmotionAnalyzeResponse,
  EmotionMetrics,
  InterviewTypeInfo,
  StartInterviewResponse,
  SubmitAnswerResponse,
  TranscribeResponse,
} from "@/lib/types/interview";

export type {
  ChatRequest,
  ChatResponse,
  DailyTip,
  DocumentListResponse,
  ExplainResponse,
  PredictRequest,
  PredictResponse,
  UploadResponse,
};

export type DashboardData = DashboardResponse;

/** Browser uses same-origin `/api` (Next rewrite → backend). Override with NEXT_PUBLIC_API_URL if needed. */
function resolveBaseURL(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "");
  }
  if (typeof window !== "undefined") {
    return "";
  }
  return (process.env.API_PROXY_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
}

export const api = axios.create({
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  if (!config.baseURL) {
    config.baseURL = resolveBaseURL();
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (process.env.NODE_ENV === "development") {
      const hint =
        error.code === "ERR_NETWORK"
          ? " — is the backend running? (uvicorn app.main:app --port 8000)"
          : "";
      console.error("[API]", error.message + hint);
    }
    return Promise.reject(error);
  }
);

export async function checkApiHealth() {
  const { data } = await api.get("/api/health");
  return data;
}

export async function getUser() {
  const { data } = await api.get<UserResponse>("/api/user");
  return data;
}

export async function predictPerformance(payload: PredictRequest) {
  const { data } = await api.post<PredictResponse>("/api/predict", payload);
  return data;
}

export async function explainPrediction(payload: PredictRequest) {
  const { data } = await api.post<ExplainResponse>("/api/predict/explain", payload);
  return data;
}

export async function getDashboard() {
  const { data } = await api.get<DashboardResponse>("/api/dashboard");
  return data;
}

export async function getRecommendations() {
  const { data } = await api.get<{ recommendations: DashboardResponse["recommendations"] }>(
    "/api/recommendations"
  );
  return data;
}

export async function getPersonalizedRecommendations(
  params?: PersonalizedRecommendationsRequest
) {
  const { data } = await api.get<PersonalizedRecommendationsResponse>(
    "/api/recommendations/personalized",
    { params }
  );
  return data;
}

export async function postPersonalizedRecommendations(
  body: PersonalizedRecommendationsRequest
) {
  const { data } = await api.post<PersonalizedRecommendationsResponse>(
    "/api/recommendations/personalized",
    body
  );
  return data;
}

export async function getDailyStudyPlanner(
  params?: { study_hours?: number; attendance_pct?: number; math_score?: number }
) {
  const { data } = await api.get<DailyStudyPlannerResponse>("/api/study-planner", {
    params,
  });
  return data;
}

export async function postDailyStudyPlanner(body: PersonalizedRecommendationsRequest) {
  const { data } = await api.post<DailyStudyPlannerResponse>("/api/study-planner", body);
  return data;
}

export async function getDailyTip() {
  const { data } = await api.get<DailyTip>("/api/daily-tip");
  return data;
}

export async function getAIInsights() {
  const { data } = await api.get<InsightsResponse>("/api/insights");
  return data;
}

export async function getAIStatus() {
  const { data } = await api.get("/api/ai/status");
  return data;
}

export async function postRecommend(body: PersonalizedRecommendationsRequest & { include_study_plan?: boolean }) {
  const { data } = await api.post("/api/recommend", body);
  return data;
}

export async function getAnalytics(params?: { performance_score?: number; study_streak_days?: number }) {
  const { data } = await api.get("/api/analytics", { params });
  return data;
}

export async function getAIInsightsReport() {
  const { data } = await api.get<InsightsReportResponse>("/api/insights/report");
  return data;
}

// --- Week 4: RAG document assistant ---

export async function uploadDocument(file: File) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<UploadResponse>("/api/documents/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 120000,
  });
  return data;
}

export async function listDocuments() {
  const { data } = await api.get<DocumentListResponse>("/api/documents");
  return data;
}

export async function deleteDocument(documentId: string) {
  const { data } = await api.delete(`/api/documents/${documentId}`);
  return data;
}

export async function chatWithDocuments(body: ChatRequest) {
  const { data } = await api.post<ChatResponse>("/api/documents/chat", body, {
    timeout: 60000,
  });
  return data;
}

export async function createChatSession() {
  const { data } = await api.post<ConversationResponse>("/api/chat/sessions", {});
  return data;
}

export async function deleteChatSession(sessionId: string) {
  const { data } = await api.delete(`/api/chat/sessions/${sessionId}`);
  return data;
}

// --- Week 4 Day 5: smart learning features ---

const STUDY_TIMEOUT = 60000;

export async function summarizeDocument(body: StudyToolRequest) {
  const { data } = await api.post<SummaryResponse>("/api/study/summarize", body, {
    timeout: STUDY_TIMEOUT,
  });
  return data;
}

export async function generateQuiz(body: StudyToolRequest) {
  const { data } = await api.post<QuizResponse>("/api/study/quiz", body, {
    timeout: STUDY_TIMEOUT,
  });
  return data;
}

export async function generateFlashcards(body: StudyToolRequest) {
  const { data } = await api.post<FlashcardResponse>("/api/study/flashcards", body, {
    timeout: STUDY_TIMEOUT,
  });
  return data;
}

export async function explainSimply(concept: string, documentId?: string | null) {
  const { data } = await api.post<ExplainSimpleResponse>(
    "/api/study/explain",
    { concept, document_id: documentId ?? null },
    { timeout: STUDY_TIMEOUT }
  );
  return data;
}

export async function generateRevision(body: StudyToolRequest) {
  const { data } = await api.post<RevisionResponse>("/api/study/revision", body, {
    timeout: STUDY_TIMEOUT,
  });
  return data;
}

// --- Week 5: AI Interview Coach ---

export async function getInterviewTypes() {
  const { data } = await api.get<InterviewTypeInfo[]>("/api/interview/types");
  return data;
}

export async function startInterview(interviewType: string, numQuestions = 5) {
  const { data } = await api.post<StartInterviewResponse>("/api/interview/start", {
    interview_type: interviewType,
    num_questions: numQuestions,
  });
  return data;
}

export async function submitInterviewAnswer(
  sessionId: string,
  answerText: string,
  options?: { transcript?: string; emotionMetrics?: EmotionMetrics }
) {
  const { data } = await api.post<SubmitAnswerResponse>(
    `/api/interview/session/${sessionId}/answer`,
    {
      answer_text: answerText,
      transcript: options?.transcript,
      emotion_metrics: options?.emotionMetrics,
    },
    { timeout: 90_000 }
  );
  return data;
}

export async function analyzeInterviewEmotion(blob: Blob, filename = "frame.jpg") {
  const form = new FormData();
  form.append("file", blob, filename);
  const { data } = await api.post<EmotionAnalyzeResponse>(
    "/api/interview/emotion/analyze",
    form,
    { timeout: 60_000, headers: { "Content-Type": "multipart/form-data" } }
  );
  return data;
}

export async function getInterviewCoachReport(sessionId: string) {
  const { data } = await api.get<CoachReport>(
    `/api/interview/session/${sessionId}/coach`,
    { timeout: 90_000 }
  );
  return data;
}

export async function transcribeInterviewAudio(blob: Blob, filename = "recording.webm") {
  const form = new FormData();
  form.append("file", blob, filename);
  const { data } = await api.post<TranscribeResponse>("/api/interview/transcribe", form, {
    timeout: 120_000,
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

// --- Week 6: AI Agent Copilot ---

export async function getAgentTypes() {
  const { data } = await api.get<AgentInfo[]>("/api/agents/types");
  return data;
}

export async function agentChat(body: AgentChatRequest) {
  const { data } = await api.post<AgentChatResponse>("/api/agents/chat", body, {
    timeout: 90_000,
  });
  return data;
}

export async function agentCollaborate(body: AgentChatRequest) {
  const { data } = await api.post<AgentChatResponse>("/api/agents/collaborate", body, {
    timeout: 120_000,
  });
  return data;
}

export async function createExamStudyPlan(body: ExamStudyPlanRequest) {
  const { data } = await api.post<ExamStudyPlanResponse>("/api/agents/study/plan", body, {
    timeout: 60_000,
  });
  return data;
}

export async function getDailyStudyRecommendations() {
  const { data } = await api.get<DailyStudyRecommendationsResponse>(
    "/api/agents/study/daily"
  );
  return data;
}

export async function listLearningGoals(sessionId: string) {
  const { data } = await api.get<{ session_id: string; goals: LearningGoal[] }>(
    `/api/agents/study/goals/${sessionId}`
  );
  return data;
}

// --- Week 6 Day 3: Career Agent ---

export async function getCareerRecommendation(body?: CareerAnalysisRequest) {
  const { data } = await api.post<CareerRecommendationResponse>(
    "/api/agents/career/recommend",
    body ?? {},
    { timeout: 60_000 }
  );
  return data;
}

export async function getCareerSkillGaps(body?: CareerAnalysisRequest) {
  const { data } = await api.post<SkillGapAnalysisResponse>(
    "/api/agents/career/skill-gaps",
    body ?? {},
    { timeout: 60_000 }
  );
  return data;
}

export async function getCareerRoadmap(body?: CareerAnalysisRequest) {
  const { data } = await api.post<LearningRoadmapResponse>(
    "/api/agents/career/roadmap",
    body ?? {},
    { timeout: 60_000 }
  );
  return data;
}

export async function getCareerTrends(targetCareer?: string) {
  const { data } = await api.get("/api/agents/career/trends", {
    params: targetCareer ? { target_career: targetCareer } : undefined,
  });
  return data;
}

// --- Week 6 Day 4: Resume Analyzer ---

export async function uploadResume(file: File, targetRole?: string) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<ResumeAnalysisResponse>("/api/resume/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 120_000,
    params: targetRole ? { target_role: targetRole } : undefined,
  });
  return data;
}

export async function analyzeResumeText(text: string, targetRole?: string) {
  const { data } = await api.post<ResumeAnalysisResponse>(
    "/api/resume/analyze",
    { text, target_role: targetRole ?? null } satisfies ResumeTextAnalyzeRequest,
    { timeout: 90_000 }
  );
  return data;
}

export async function getResumeAnalysis(analysisId: string) {
  const { data } = await api.get<ResumeAnalysisResponse>(
    `/api/resume/analysis/${analysisId}`
  );
  return data;
}

// --- Week 6 Day 5: Personalized Learning Planner ---

export async function generateLearningRoadmap(body: LearningRoadmapRequest) {
  const { data } = await api.post<LearningRoadmapResponse>(
    "/api/learning-planner/roadmap",
    body,
    { timeout: 30_000 }
  );
  return data;
}

export async function createLearningPlan(body: {
  goal: string;
  hours_per_week?: number;
}) {
  const { data } = await api.post<LearningPlanResponse>(
    "/api/learning-planner/plans",
    body,
    { timeout: 30_000 }
  );
  return data;
}

export async function getLearningPlan(planId: string) {
  const { data } = await api.get<LearningPlanResponse>(
    `/api/learning-planner/plans/${planId}`
  );
  return data;
}

export async function updateLearningPlanProgress(
  planId: string,
  body: LearningPlanProgressUpdate
) {
  const { data } = await api.patch<LearningPlanResponse>(
    `/api/learning-planner/plans/${planId}/progress`,
    body
  );
  return data;
}

export async function getLearningPlanWeekly(planId: string) {
  const { data } = await api.get<{
    plan: LearningPlanResponse;
    weekly: Record<string, unknown>;
    weekly_markdown: string;
  }>(`/api/learning-planner/plans/${planId}/weekly`);
  return data;
}

// --- Week 6 Day 7: AI Coach Dashboard ---

export async function getCoachOverview(params?: {
  target_career?: string;
  session_id?: string;
  interview_session_id?: string;
}) {
  const { data } = await api.get<CoachOverviewResponse>("/api/coach/overview", {
    params,
    timeout: 60_000,
  });
  return data;
}

export async function getCoachWeeklyReport(params?: {
  session_id?: string;
  target_career?: string;
}) {
  const { data } = await api.get<WeeklyProgressReport>("/api/coach/weekly-report", {
    params,
    timeout: 60_000,
  });
  return data;
}

// --- Week 7 Day 1: User Personalization Engine ---

export async function buildUserProfile(userId?: string) {
  const { data } = await api.post<{
    profile: UnifiedUserProfile;
    recommendations: PersonalizedRecommendationsResponse;
    embedding_updated: boolean;
  }>("/api/personalization/profile/build", null, {
    params: userId ? { user_id: userId } : undefined,
    timeout: 90_000,
  });
  return data;
}

export async function getUserProfile(userId: string, refresh = false) {
  const { data } = await api.get<UnifiedUserProfile>(
    `/api/personalization/profile/${userId}`,
    { params: { refresh }, timeout: 60_000 }
  );
  return data;
}

export async function getPersonalizedUserRecommendations(userId?: string) {
  const path = userId
    ? `/api/personalization/recommendations/${userId}`
    : "/api/personalization/recommendations";
  const { data } = await api.get<PersonalizedRecommendationsResponse>(path, {
    timeout: 60_000,
  });
  return data;
}

export async function updateLearningPreferences(
  userId: string,
  body: PreferencesUpdateRequest
) {
  const { data } = await api.patch<UnifiedUserProfile>(
    `/api/personalization/preferences/${userId}`,
    body,
    { timeout: 60_000 }
  );
  return data;
}

// --- Week 7 Day 2: Long-Term Memory ---

export async function getMemoryProgress(userId: string) {
  const { data } = await api.get<MemoryProgressResponse>(
    `/api/memory/${userId}/progress`,
    { timeout: 60_000 }
  );
  return data;
}

export async function getMemoryContext(userId: string, query?: string) {
  const { data } = await api.get<MemoryContextResponse>(
    `/api/memory/${userId}/context`,
    { params: query ? { query } : undefined, timeout: 60_000 }
  );
  return data;
}

export async function syncLongTermMemory(userId: string) {
  const { data } = await api.post(`/api/memory/${userId}/sync`, null, {
    timeout: 60_000,
  });
  return data;
}

// --- Week 7 Day 3: AI Learning Analytics ---

export async function getLearningAnalytics(userId?: string) {
  const path = userId
    ? `/api/learning-analytics/${userId}`
    : "/api/learning-analytics/demo";
  const { data } = await api.get<LearningAnalyticsDashboard>(path, {
    timeout: 60_000,
  });
  return data;
}

// --- Week 7 Day 4: Automated Reports ---

export async function getWeeklyReport(userId: string) {
  const { data } = await api.get<WeeklyReportData>(
    `/api/reports/weekly/${userId}`,
    { timeout: 90_000 }
  );
  return data;
}

export async function getMonthlyReport(userId: string) {
  const { data } = await api.get<MonthlyReportData>(
    `/api/reports/monthly/${userId}`,
    { timeout: 90_000 }
  );
  return data;
}

export async function downloadReportPdf(userId: string, type: "weekly" | "monthly") {
  const response = await api.post(
    `/api/reports/${type}/${userId}/pdf`,
    null,
    { responseType: "blob", timeout: 120_000 }
  );
  const blob = new Blob([response.data], { type: "application/pdf" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `mentormind-${type}-report.pdf`;
  a.click();
  window.URL.revokeObjectURL(url);
}

export async function emailReport(
  userId: string,
  type: "weekly" | "monthly",
  toEmail?: string
) {
  const { data } = await api.post<EmailReportResponse>(
    `/api/reports/${type}/${userId}/email`,
    null,
    { params: toEmail ? { to_email: toEmail } : undefined, timeout: 120_000 }
  );
  return data;
}

// --- Week 7 Day 5: MLOps Pipeline ---

export async function getMLOpsStatus() {
  const { data } = await api.get<MLOpsStatus>("/api/mlops/status");
  return data;
}

export async function getMLOpsModels() {
  const { data } = await api.get<ModelVersion[]>("/api/mlops/models");
  return data;
}

export async function getMLOpsExperiments() {
  const { data } = await api.get<ExperimentRun[]>("/api/mlops/experiments");
  return data;
}

export async function compareMLOpsExperiments(versions?: string[]) {
  const { data } = await api.get<ExperimentComparison>("/api/mlops/experiments/compare", {
    params: versions?.length ? { versions: versions.join(",") } : undefined,
  });
  return data;
}

export async function runMLOpsExperiment(body: RunExperimentRequest) {
  const { data } = await api.post<{ status: string; note?: string }>(
    "/api/mlops/experiments/run",
    body,
    { timeout: 120_000 }
  );
  return data;
}

export async function promoteMLOpsModel(version: string, notes = "") {
  const { data } = await api.post("/api/mlops/models/promote", { version, notes });
  return data;
}
