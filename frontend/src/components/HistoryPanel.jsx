export default function HistoryPanel({ history, clearHistory }) {
  return (
    <section className="glass card history">
      <div className="history-head">
        <h3>Translation History</h3>
        <button className="btn" onClick={clearHistory}>Clear</button>
      </div>
      <ul>
        {history.length === 0 && <li>No translations yet.</li>}
        {history.map((item, i) => (
          <li key={`${item.text}-${i}`}>
            <span>{item.text}</span>
            <small>{item.confidence}%</small>
          </li>
        ))}
      </ul>
    </section>
  )
}
