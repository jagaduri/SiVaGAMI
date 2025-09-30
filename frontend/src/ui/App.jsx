// frontend/src/ui/App.jsx
import React, { useEffect, useState } from "react";
import LeftRail from "./LeftRail";
import ChatArea from "./ChatArea";
import TopHeader from "./TopHeader";
import axios from "axios";

const API = "http://localhost:8000";

export default function App(){
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState("");
  const [provider, setProvider] = useState("ollama");
  const [model, setModel] = useState("mistral");

  const loadConversations = async () => {
    const r = await axios.get(`${API}/conversations`);
    setConversations(r.data || []);
  };

  const openConversation = async (id) => {
    setActiveConv(id);
    const r = await axios.get(`${API}/conversations/${id}/messages`);
    setMessages(r.data || []);
  };

  const newConversation = async () => {
    const r = await axios.post(`${API}/conversations/start`, { title: "New chat" });
    await loadConversations();
    await openConversation(r.data.conv_id);
  };

  useEffect(() => { loadConversations(); }, []);

  const ensureConversation = async () => {
    if (activeConv) return activeConv;
    const r = await axios.post(`${API}/conversations/start`, { title: "New chat" });
    setActiveConv(r.data.conv_id);
    return r.data.conv_id;
  };

  const sendQuestion = async (q, stream = true) => {
    if (!q) return;

    // make sure we have a conversation id
    const convId = await ensureConversation();

    // optimistic append user message
    setMessages(prev => [...prev, { sender: "user", text: q }]);

    if (stream) {
      const url = `${API}/stream_sse?provider=${encodeURIComponent(provider)}&model=${encodeURIComponent(model)}&question=${encodeURIComponent(q)}&conv_id=${encodeURIComponent(convId)}`;
      const es = new EventSource(url);
      let partial = "";
      setMessages(prev => [...prev, { sender: "assistant", text: "" }]);
      const idx = messages.length + 1;

      es.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          const token = data.token ?? "";
          partial += token;
          setMessages(prev => { const copy = [...prev]; copy[idx] = { sender: "assistant", text: partial }; return copy; });
        } catch {}
      };

      // When the stream finishes (or errors), refresh history list
      const closeAndRefresh = () => { try { es.close(); } catch {} loadConversations(); };
      es.onerror = closeAndRefresh;
      // Some Ollama versions don’t fire onerror on normal end; close after 1s idle
      setTimeout(closeAndRefresh, 1000);
    } else {
      const r = await axios.post(`${API}/chat`, { question: q, provider, model, conv_id: convId });
      setMessages(prev => [...prev, { sender: "assistant", text: r.data.answer }]);
      loadConversations();
    }
  };

  const uploadFiles = async (files) => {
    const fd = new FormData();
    Array.from(files).forEach(f => fd.append("files", f));
    await axios.post(`${API}/upload`, fd);
    alert("Uploaded & ingested");
  };

  const renameConversation = async (id, currentTitle="New chat") => {
    const title = window.prompt("Rename chat", currentTitle);
    if (!title || !title.trim()) return;
    await axios.post(`${API}/conversations/${id}/rename`, { title: title.trim() });
    await loadConversations();
  };

  const deleteConversation = async (id) => {
    if (!window.confirm("Delete this chat? This cannot be undone.")) return;
    await axios.delete(`${API}/conversations/${id}`);
    if (activeConv === id) { setActiveConv(""); setMessages([]); }
    await loadConversations();
  };

  return (
    <div className="app">
      <TopHeader />
      <div className="body">
        <LeftRail
          conversations={conversations}
          onOpen={openConversation}
          onNew={newConversation}
          onUpload={uploadFiles}
          onRename={renameConversation}
          onDelete={deleteConversation}
          provider={provider} setProvider={setProvider}
          model={model} setModel={setModel}
        />
        <div className="main">
          <div className="hero">
            <h1>Hi Hemanth Kumar</h1>
            <p>How can I help you today?</p>
          </div>
          <ChatArea messages={messages} onSend={sendQuestion} />
          <div className="footer">SiVaGAMI • RAG + MongoDB + {provider === "ollama" ? "Ollama" : "OpenAI"}</div>
        </div>
      </div>
    </div>
  );

  
}
