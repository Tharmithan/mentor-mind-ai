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
};
