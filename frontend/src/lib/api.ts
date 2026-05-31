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
