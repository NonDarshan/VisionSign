const guide = [
  ['hello', 'Raise open palm and wave gently'],
  ['thank_you', 'Hand from chin outward'],
  ['yes', 'Closed fist nod motion'],
  ['no', 'Pinched fingers open/close'],
]

export default function GuidePanel() {
  return (
    <section className="glass card guide">
      <h3>Gesture Guide</h3>
      <ul>
        {guide.map(([word, hint]) => (
          <li key={word}>
            <strong>{word}</strong>
            <p>{hint}</p>
          </li>
        ))}
      </ul>
    </section>
  )
}
