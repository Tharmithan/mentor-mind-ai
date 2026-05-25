import axios from "axios";
import type {
  DailyStudyPlannerResponse,
  DailyTip,
  DashboardResponse,
  InsightsReportResponse,
  InsightsResponse,
  PersonalizedRecommendationsRequest,
  PersonalizedRecommendationsResponse,
  ExplainResponse,
  PredictRequest,
  PredictResponse,
  UserResponse,
} from "@/lib/types/api";

export type { DailyTip, ExplainResponse, PredictRequest, PredictResponse };

export type DashboardData = DashboardResponse;

const baseURL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const api = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (process.env.NODE_ENV === "development") {
      console.error("[API]", error.message);
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
