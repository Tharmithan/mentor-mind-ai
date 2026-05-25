# Frontend Setup — Week 1 Day 3

## Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Next.js | 16.x | App Router, SSR |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 4.x | Styling |
| lucide-react | latest | Icons |
| axios | latest | API client |
| recharts | latest | Charts |

## Project structure

```
frontend/src/
├── app/
│   ├── page.tsx              # Landing
│   ├── dashboard/
│   │   ├── layout.tsx        # Dashboard shell
│   │   └── page.tsx
│   └── interview/
│       ├── layout.tsx
│       └── page.tsx
├── components/
│   ├── charts/               # Recharts
│   ├── interview/
│   ├── layout/               # Navbar, Sidebar, MobileNav, DashboardLayout
│   └── ui/                   # Button, GlassCard, animations
└── lib/
    └── api.ts                # Axios instance
```

## Install (already done)

```bash
cd frontend
npm install lucide-react axios recharts
```

## Environment

```bash
cp .env.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Run

```bash
npm run dev    # http://localhost:3000
npm run build  # production build
```

## Day 3 checklist

- [x] Next.js + TypeScript + Tailwind + App Router
- [x] lucide-react, axios, recharts installed
- [x] Landing page
- [x] Dashboard layout (`app/dashboard/layout.tsx`)
- [x] Navbar + Sidebar + Mobile bottom nav
- [x] Responsive design
- [x] Glassmorphism cards
- [x] Smooth animations (fade-in, stagger, pulse)
- [x] Recharts study analytics + performance trend
- [x] Axios API client (`lib/api.ts`)

## API usage example

```typescript
import { checkApiHealth } from "@/lib/api";

const health = await checkApiHealth();
```
