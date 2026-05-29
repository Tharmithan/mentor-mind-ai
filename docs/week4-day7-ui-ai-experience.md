# Week 4 · Day 7 — UI + AI Experience

Goal: make the assistant feel like a **premium AI product**.

---

## Modern chat UI

| Feature | How |
|---------|-----|
| **Markdown support** | `Markdown.tsx` — dependency-free renderer: headings, bold/italic, lists, links |
| **Code blocks** | Fenced ` ```lang ` blocks render with a language label + monospace panel |
| **Streaming responses** | Typewriter reveal of each answer (char-by-char) with a blinking caret |
| **Typing animation** | The caret + progressive reveal simulate live token streaming |
| **Dark mode** | The app is dark-first by design (mesh background, glass cards) |

> Streaming is a client-side typewriter so it also works on the offline/extractive
> path (which can't stream from an LLM). The markdown renderer is custom and
> dependency-free to stay compatible with the project's Next.js 16 setup.

---

## AI thinking animation

`ThinkingIndicator.tsx` cycles through status phrases while the answer is generated:

```
✦ Analyzing lecture materials…
✦ Searching your notes…
✦ Connecting concepts…
✦ Composing an answer…
```

with animated bouncing dots — so the wait feels intelligent, not idle.

---

## Suggested questions

When a chat is fresh, tappable starter chips appear:

- "Summarize this PDF"
- "Generate a quiz on the key topics"
- "Explain the difficult topics simply"
- "What are the most important points?"

Clicking one sends it immediately.

---

## Files

| File | Purpose |
|------|---------|
| `components/assistant/Markdown.tsx` | Markdown + code-block renderer |
| `components/assistant/ThinkingIndicator.tsx` | Cycling "thinking" animation |
| `components/assistant/ChatPanel.tsx` | Typewriter reveal, suggestions, markdown wiring |

---

## Verified

`next build` passes TypeScript; `/assistant` prerenders. No new dependencies added.

---

## Checklist

- [x] Markdown support
- [x] Code blocks
- [x] Streaming responses (typewriter)
- [x] Typing animation
- [x] AI thinking animation ("Analyzing lecture materials…")
- [x] Suggested questions
- [x] Dark mode (dark-first design)
