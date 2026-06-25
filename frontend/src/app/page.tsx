"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function Home() {
  const [health, setHealth] = useState<Record<string, string> | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [docs, setDocs] = useState("");
  const [searchQ, setSearchQ] = useState("");
  const [searchR, setSearchR] = useState("");
  const [ragQ, setRagQ] = useState("");
  const [ragR, setRagR] = useState("");
  const [chatQ, setChatQ] = useState("");
  const [chatR, setChatR] = useState("");
  const [agentQ, setAgentQ] = useState("");
  const [agentR, setAgentR] = useState("");
  const [loading, setLoading] = useState("");

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth({ status: "error" }));
  }, []);

  async function run<T>(key: string, fn: () => Promise<T>, set: (v: string) => void) {
    setLoading(key);
    try {
      const data = await fn();
      set(JSON.stringify(data, null, 2));
    } catch (e) {
      set(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading("");
    }
  }

  return (
    <div className="container">
      <header>
        <h1>AI Research Assistant</h1>
        <p>Self-hosted document upload, search, RAG, and agent — powered by Ollama + ChromaDB</p>
      </header>

      <div className="card">
        <h2>System Health</h2>
        <div className="status">
          {health ? Object.entries(health).map(([k, v]) => (
            <span key={k} className={`badge ${v === "connected" || v === "healthy" ? "ok" : "err"}`}>
              {k}: {v}
            </span>
          )) : <span className="badge">checking...</span>}
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h2>Upload Document</h2>
          <input type="file" accept=".pdf,.docx,.txt" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          <button disabled={!file || loading === "upload"} onClick={() => file && run("upload", () => api.upload(file), setDocs)}>
            {loading === "upload" ? "Uploading..." : "Upload & Parse"}
          </button>
          <button style={{ marginLeft: 8 }} disabled={loading === "list"} onClick={() => run("list", api.listDocuments, setDocs)}>
            List Documents
          </button>
          {docs && <pre>{docs}</pre>}
        </div>

        <div className="card">
          <h2>Semantic Search</h2>
          <input type="text" placeholder="Search query..." value={searchQ} onChange={(e) => setSearchQ(e.target.value)} />
          <button disabled={!searchQ || loading === "search"} onClick={() => run("search", () => api.search(searchQ), setSearchR)}>
            Search
          </button>
          {searchR && <pre>{searchR}</pre>}
        </div>
      </div>

      <div className="card">
        <h2>RAG — Ask Your Documents</h2>
        <input type="text" placeholder="What does the document say about...?" value={ragQ} onChange={(e) => setRagQ(e.target.value)} />
        <button disabled={!ragQ || loading === "rag"} onClick={() => run("rag", () => api.ragAsk(ragQ), setRagR)}>
          Ask (RAG)
        </button>
        {ragR && <pre>{ragR}</pre>}
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h2>Chat (Ollama)</h2>
          <textarea rows={3} placeholder="Message..." value={chatQ} onChange={(e) => setChatQ(e.target.value)} />
          <button disabled={!chatQ || loading === "chat"} onClick={() => run("chat", () => api.chat(chatQ), setChatR)}>
            Send
          </button>
          {chatR && <pre>{chatR}</pre>}
        </div>

        <div className="card">
          <h2>Research Agent</h2>
          <textarea rows={3} placeholder="Ask the agent..." value={agentQ} onChange={(e) => setAgentQ(e.target.value)} />
          <button disabled={!agentQ || loading === "agent"} onClick={() => run("agent", () => api.agent(agentQ), setAgentR)}>
            Run Agent
          </button>
          {agentR && <pre>{agentR}</pre>}
        </div>
      </div>
    </div>
  );
}
