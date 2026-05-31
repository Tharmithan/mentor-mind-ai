# Demo Assets

| Asset | Description |
|-------|-------------|
| [demo.gif](./demo.gif) | Animated preview for README (3-frame loop) |

## Record a full demo video

1. Start backend and frontend locally (see root [README](../README.md#installation)).
2. Walk through: **Dashboard → ML Predict → Assistant upload/chat → Interview**.
3. Export as MP4 (≤ 2 min) and upload to YouTube or Loom.
4. Add the link to README **Demo Video** section:

```markdown
[![Demo Video](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](https://youtu.be/YOUR_VIDEO_ID)
```

## Replace the GIF

Record a screen capture and overwrite `demo/demo.gif`:

```bash
# ffmpeg example — convert MP4 to GIF (resize for GitHub)
ffmpeg -i demo-recording.mp4 -vf "fps=10,scale=800:-1" -loop 0 demo/demo.gif
```

Recommended: **800px wide**, **≤ 5 MB** for fast README loading.

## Live deployment

After deploying to Vercel + Railway, add production URLs to README badges and demo section.
