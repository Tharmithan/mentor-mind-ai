/** Voice stress / nervousness from mic amplitude (Web Audio API). */

export type VoiceMetrics = {
  volume: number;
  variance: number;
  nervousness: number;
  speaking: boolean;
};

export class VoiceAnalyzer {
  private ctx: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private source: MediaStreamAudioSourceNode | null = null;
  private buffer: Uint8Array<ArrayBuffer> | null = null;
  private history: number[] = [];
  private readonly maxHistory = 24;

  connect(stream: MediaStream | null) {
    this.disconnect();
    if (!stream?.getAudioTracks().length) return;
    this.ctx = new AudioContext();
    this.analyser = this.ctx.createAnalyser();
    this.analyser.fftSize = 512;
    this.analyser.smoothingTimeConstant = 0.65;
    this.source = this.ctx.createMediaStreamSource(stream);
    this.source.connect(this.analyser);
    this.buffer = new Uint8Array(this.analyser.frequencyBinCount);
    this.history = [];
  }

  disconnect() {
    this.source?.disconnect();
    this.source = null;
    this.analyser = null;
    void this.ctx?.close();
    this.ctx = null;
    this.buffer = null;
    this.history = [];
  }

  sample(): VoiceMetrics {
    if (!this.analyser || !this.buffer) {
      return { volume: 0, variance: 0, nervousness: 35, speaking: false };
    }
    this.analyser.getByteTimeDomainData(this.buffer);
    let sum = 0;
    for (let i = 0; i < this.buffer.length; i++) {
      const v = (this.buffer[i] - 128) / 128;
      sum += v * v;
    }
    const rms = Math.sqrt(sum / this.buffer.length);
    const volume = Math.min(100, rms * 420);
    this.history.push(volume);
    if (this.history.length > this.maxHistory) this.history.shift();

    const mean = this.history.reduce((a, b) => a + b, 0) / this.history.length;
    const variance =
      this.history.length > 2
        ? this.history.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / this.history.length
        : 0;

    const speaking = volume > 8;
    const nervousness = Math.min(
      100,
      Math.round(variance * 0.35 + (speaking && variance > 120 ? 18 : 0))
    );

    return { volume, variance, nervousness, speaking };
  }
}
