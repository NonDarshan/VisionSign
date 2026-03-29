export default function Header({ darkMode, onToggleDark }) {
  return (
    <header className="glass card header">
      <div>
        <h1>VisonSign</h1>
        <p>Indian Sign Language Interpreter</p>
      </div>
      <button onClick={onToggleDark} className="btn">
        {darkMode ? 'Light' : 'Dark'}
      </button>
    </header>
  )
}
