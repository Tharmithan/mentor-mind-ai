import axios from "axios";
import type {
  DailyTip,
  DashboardResponse,
  PredictRequest,
  PredictResponse,
  UserResponse,
} from "@/lib/types/api";

export type { DailyTip };

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

export async function getDailyTip() {
  const { data } = await api.get<DailyTip>("/api/daily-tip");
  return data;
}
