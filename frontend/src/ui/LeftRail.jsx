import React from "react";

export default function LeftRail({
  conversations, onOpen, onNew, onUpload,
  onRename, onDelete, provider, setProvider, model, setModel
}) {
  return (
    <div className="rail">
      <div className="header-row">
        <div className="title">Chat History</div>
        <button className="btn btn-new" onClick={onNew}>+ New</button>
      </div>

      <div className="section">
        <input className="search-input" placeholder="Search chats" />
      </div>

      <div className="history">
        {(conversations || []).map((c) => (
          <div key={c.id} className="item">
            <div className="dot"></div>
            <div className="meta" onClick={() => onOpen(c.id)}>
              <div className="title-text">{c.title || "Untitled"}</div>
              <div className="last-text">{c.last || ""}</div>
            </div>
            <div className="actions">
              <button className="chip" title="Rename"
                onClick={(e)=>{e.stopPropagation(); onRename(c.id, c.title);}}>Rename</button>
              <button className="chip danger" title="Delete"
                onClick={(e)=>{e.stopPropagation(); onDelete(c.id);}}>Delete</button>
            </div>
          </div>
        ))}
      </div>

      <div className="section">
        <div className="title">Upload</div>
        <input type="file" multiple onChange={e => onUpload(e.target.files)} />
      </div>

      <div className="section">
        <div className="title">Settings</div>
        <label>Provider</label>
        <select value={provider} onChange={e => setProvider(e.target.value)}>
          <option value="ollama">ollama (local)</option>
          <option value="openai">openai (cloud)</option>
        </select>
        <label>Model</label>
        <input value={model} onChange={e => setModel(e.target.value)} placeholder="mistral / llama2 / gpt-4o-mini" />
      </div>
    </div>
  );
}
