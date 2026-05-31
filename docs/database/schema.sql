-- MentorMind AI — Day 5 core schema (PostgreSQL / Supabase)
-- Run in Supabase SQL Editor: https://supabase.com/dashboard → SQL → New query

-- ---------------------------------------------------------------------------
-- Extensions (Supabase usually has these; safe to run)
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ---------------------------------------------------------------------------
-- 1. users — one student/admin account
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'student' CHECK (role IN ('student', 'admin')),
    xp INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- 2. performance_data — scores & study metrics (many per user)
-- Relationship: users 1 ──→ N performance_data
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS performance_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject VARCHAR(100) NOT NULL,
    score DECIMAL(5,2) NOT NULL CHECK (score >= 0 AND score <= 100),
    study_hours DECIMAL(5,2) DEFAULT 0,
    attendance_pct DECIMAL(5,2) DEFAULT 0,
    predicted_score DECIMAL(5,2),
    risk_level VARCHAR(50) DEFAULT 'medium',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- 3. interview_results — mock interview session outcomes
-- Relationship: users 1 ──→ N interview_results
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS interview_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mode VARCHAR(50) DEFAULT 'general',
    overall_score DECIMAL(3,2) CHECK (overall_score >= 0 AND overall_score <= 5),
    communication_score DECIMAL(3,2),
    technical_score DECIMAL(3,2),
    confidence_score DECIMAL(5,2),
    feedback_summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- 4. recommendations — AI study suggestions
-- Relationship: users 1 ──→ N recommendations
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    topic VARCHAR(100),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Indexes (faster lookups by user)
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_performance_data_user ON performance_data(user_id);
CREATE INDEX IF NOT EXISTS idx_interview_results_user ON interview_results(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_user ON recommendations(user_id);

-- ---------------------------------------------------------------------------
-- 5. refresh_tokens — JWT refresh rotation (Week 8 · Day 2)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    jti VARCHAR(64) UNIQUE NOT NULL,
    token_hash VARCHAR(64) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_jti ON refresh_tokens(jti);
