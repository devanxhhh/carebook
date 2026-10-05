export default function Notice({ children, tone = 'error' }) {
  if (!children) return null
  return <div className={`notice notice-${tone}`} role={tone === 'error' ? 'alert' : 'status'}>{children}</div>
}
