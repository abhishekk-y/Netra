export function formatIP(ip: string): string {
  return ip || '0.0.0.0';
}

export function formatMAC(mac: string): string {
  return (mac || '').toUpperCase();
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  const s = Math.floor(ms / 1000);
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  return `${m}m ${s % 60}s`;
}

export function formatRisk(risk: number): string {
  return risk.toFixed(1);
}

export function formatConfidence(conf: number): string {
  return `${(conf * 100).toFixed(0)}%`;
}
