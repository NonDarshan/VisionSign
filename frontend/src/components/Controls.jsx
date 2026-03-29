export default function Controls({ language, setLanguage, speakerOn, setSpeakerOn }) {
  return (
    <div className="glass card controls">
      <label>
        Output Language
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="en">English</option>
          <option value="hi">Hindi</option>
        </select>
      </label>

      <label className="toggle-wrap">
        <span>Speaker</span>
        <button className="btn" onClick={() => setSpeakerOn((v) => !v)}>
          {speakerOn ? 'On' : 'Off'}
        </button>
      </label>
    </div>
  )
}
