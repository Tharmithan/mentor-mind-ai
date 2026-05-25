# MentorMind AI — UI/UX Design (Week 1 Day 2)

## Design inspiration

References: [Dribbble](https://dribbble.com), [Behance](https://behance.net), [Mobbin](https://mobbin.com)

Search terms used:
- AI dashboard
- Learning platform UI
- SaaS analytics dashboard

---

## Theme

| Token | Value |
|-------|--------|
| Background | `#030712` (near black) |
| Primary | Violet `#8b5cf6` → `#6d28d9` |
| Accent | Blue `#3b82f6` → `#60a5fa` |
| Style | Dark, glassmorphism, purple + blue gradients |
| Typography | Inter |

---

## Pages implemented

### 1. Landing Page (`/`)

| Section | Content |
|---------|---------|
| Hero | Headline, gradient text, dual CTAs, social proof stats |
| Features | 6 feature cards with icons |
| AI Capabilities | ML stack cards + emotion/interview CTA |
| Testimonials | 3 student reviews with ratings |
| CTA | Full-width gradient banner |

### 2. Dashboard (`/dashboard`) — Day 6 MVP

| Card | Content |
|------|---------|
| Performance Score | Average subject score (%) |
| Study Hours | Weekly total hours |
| Weak Subjects | Count + top weak topic |
| AI Suggestions | Pending recommendation count |

| Chart (Recharts) | Data |
|------------------|------|
| Line | Weekly performance trend |
| Bar | Daily study hours |
| Pie | Subject score distribution |

Data source: `GET /api/dashboard` (SQLite seed or mock fallback). Client: `DashboardMVP.tsx`.

### 3. AI Interview (`/interview`)

| Element | Content |
|---------|---------|
| Webcam area | Live camera or placeholder |
| Mic button | Toggle with pulse animation |
| AI chat | Interviewer messages + user input |
| Confidence meter | Live updating progress bar |

---

## Component library

- `Button` — primary, gradient, secondary, ghost
- `Card` / `StatCard` — glass cards
- `ProgressRing` — circular performance score
- `ConfidenceMeter` — horizontal confidence bar
- `SectionHeader` — section titles with badge
- `DashboardShell` — sidebar + page layout
- `InterviewRoom` — full interview UI (client)

---

## Routes

| Route | Page |
|-------|------|
| `/` | Landing |
| `/dashboard` | Student dashboard |
| `/interview` | AI mock interview |

---

## Responsive

- Mobile: stacked layout, hamburger-friendly header on dashboard
- Tablet+: sidebar visible, 2–3 column grids
- Desktop: max-width containers, full analytics grid

---

## Day 7 polish

| Feature | Implementation |
|---------|----------------|
| AI loading overlay | `AILoadingOverlay` on dashboard fetch |
| Floating AI assistant | `FloatingAIAssistant` via `AppShell` (all routes) |
| Daily AI tip | `DailyAITip` + `GET /api/daily-tip` |
| Hero copy | Personal AI mentor headline + subtext |

---

## Next (Phase 2+)

- [ ] Figma export / design tokens file
- [ ] Auth pages (login/signup) matching theme
- [ ] Study planner & PDF assistant pages
- [x] Recharts line, bar, pie on dashboard (`/api/dashboard`)
