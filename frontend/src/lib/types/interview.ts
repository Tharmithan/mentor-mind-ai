export type InterviewTypeInfo = {
  id: string;
  label: string;
  description: string;
  examples: string[];
  question_count: number;
};

export type InterviewQuestion = {
  id: string;
  text: string;
  category: string;
  difficulty: string;
  tips: string;
  interview_type: string;
};

export type EvaluationScores = {
  communication: number;
  technical_score: number;
  confidence: number;
  relevance: number;
  grammar: number;
  clarity: number;
  keyword_match: number;
  semantic_similarity: number;
  answer_length: number;
  overall: number;
};

export type IdealComparison = {
  expert_answer: string;
  expected_keywords: string[];
  matched_keywords: string[];
  missing_keywords: string[];
  similarity_pct: number;
};

export type EmotionMetrics = {
  confidence: number;
  stress: number;
  nervousness: number;
  engagement: number;
  eye_contact: number;
  smile: number;
  attention: number;
  dominant_emotion: string;
  samples: number;
  delivery_tips?: string[];
};

export type EmotionAnalyzeResponse = {
  face_detected: boolean;
  dominant_emotion: string;
  confidence: number;
  stress: number;
  nervousness: number;
  engagement: number;
  smile: number;
  attention: number;
  eye_contact: number;
  emotions: Record<string, number>;
  model: string;
  note?: string | null;
};

export type TurnFeedback = {
  question_id: string;
  question_text: string;
  answer_text: string;
  overall_score: number;
  communication_score: number;
  technical_score: number;
  confidence_score: number;
  feedback_summary: string;
  strengths: string[];
  improvements: string[];
  scores?: EvaluationScores;
  ideal_comparison?: IdealComparison;
  used_llm?: boolean;
  human_feedback?: string[];
  weaknesses?: string[];
  improvement_suggestions?: string[];
  emotion_metrics?: EmotionMetrics;
};

export type RoadmapPhase = {
  phase: string;
  focus: string;
  actions: string[];
};

export type PracticeQuestion = {
  question: string;
  category: string;
  reason: string;
};

export type CoachReport = {
  overview: string;
  strengths: string[];
  weaknesses: string[];
  improvement_roadmap: RoadmapPhase[];
  learning_topics: string[];
  practice_questions: PracticeQuestion[];
  used_llm?: boolean;
};

export type TranscribeResponse = {
  text: string;
  language?: string | null;
  duration_sec?: number | null;
  whisper_available: boolean;
};

export type InterviewSummary = {
  overall_score: number;
  communication_score: number;
  technical_score: number;
  confidence_score: number;
  questions_answered: number;
  highlights: string[];
  focus_areas: string[];
  coach_report?: CoachReport;
};

export type StartInterviewResponse = {
  session_id: string;
  interview_type: string;
  status: string;
  total_questions: number;
  current_question: InterviewQuestion;
};

export type SubmitAnswerResponse = {
  session_id: string;
  status: string;
  turn: TurnFeedback;
  completed: boolean;
  next_question: InterviewQuestion | null;
  summary: InterviewSummary | null;
  coach_report?: CoachReport | null;
};
