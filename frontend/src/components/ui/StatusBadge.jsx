export default function StatusBadge({ children }) {
  const status = String(children || 'Unknown').toLowerCase().replaceAll('_', '-')
  return <span className={`status-badge status-${status}`}>{String(children || 'Unknown').replaceAll('_', ' ')}</span>
}
