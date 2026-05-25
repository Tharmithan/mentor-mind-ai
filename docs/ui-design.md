# MentorMind AI — UI Design (Week 1)

## Brand

- **Name:** MentorMind AI
- **Tagline:** Learn smarter. Interview stronger.
- **Primary:** Indigo `#4F46E5` → `#6366F1`
- **Accent:** Emerald `#10B981` (success, progress)
- **Surface:** Slate 950 background, Slate 900 cards
- **Font:** Inter (UI), system sans fallback

---

## Pages (Week 1 shell)

| Route | Purpose |
|-------|---------|
| `/` | Marketing homepage + CTA |
| `/dashboard` | Student hub — stats, quick actions |
| `/login` | Auth (Phase 2) |
| `/signup` | Auth (Phase 2) |

Future routes: `/planner`, `/interview`, `/assistant`, `/analytics`

---

## Homepage Wireframe

```
┌────────────────────────────────────────────────────────────┐
│  [Logo] MentorMind AI          Features  Pricing  [Login]  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│     Learn smarter. Interview stronger.                     │
│     AI-powered learning & interview coach for students.    │
│                                                            │
│     [ Get Started ]    [ View Dashboard ]                  │
│                                                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Predict  │ │  Study   │ │ Mock     │ │   RAG    │      │
│  │ Perform. │ │  Planner │ │ Interview│ │ Assistant│      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Dashboard Wireframe

```
┌────────────────────────────────────────────────────────────┐
│  Sidebar │ Welcome back, Student                          │
│          │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐│
│  Home    │ │ Streak  │ │  XP     │ │ Predict │ │Interview││
│  Planner │ │  7 days │ │ 1,240   │ │  82%    │ │  4.2/5 ││
│  Interview│ └─────────┘ └─────────┘ └─────────┘ └────────┘│
│  Assistant│                                                │
│  Analytics│ Quick Actions: [Start Interview] [Study Plan]  │
│          │ Recent Activity chart (placeholder)             │
└────────────────────────────────────────────────────────────┘
```

---

## Component Library (Tailwind)

- `Button` — primary, secondary, ghost
- `Card` — stat cards, feature cards
- `Sidebar` — dashboard navigation
- `Navbar` — public pages

---

## Responsive

- Mobile: hamburger nav, stacked stat cards
- Tablet+: sidebar visible on dashboard
- Desktop: max-width 7xl container
