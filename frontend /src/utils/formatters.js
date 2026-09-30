export function formatDate(dateString) {
  if (!dateString) return '';
  try {
    const d = new Date(dateString);
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateString;
  }
}

export function getScoreColor(score) {
  if (score >= 80) {
    return {
      text: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/30',
      stroke: '#10b981',
      label: 'Strong Match',
    };
  }
  if (score >= 60) {
    return {
      text: 'text-amber-400',
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/30',
      stroke: '#f59e0b',
      label: 'Moderate Match',
    };
  }
  return {
    text: 'text-rose-400',
    bg: 'bg-rose-500/10',
    border: 'border-rose-500/30',
    stroke: '#f43f5e',
    label: 'Needs Improvement',
  };
}

export function truncate(str, max = 120) {
  if (!str) return '';
  return str.length > max ? str.slice(0, max) + '...' : str;
}
