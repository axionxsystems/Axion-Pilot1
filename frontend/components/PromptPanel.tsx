import React, { useState } from "react";
import { api } from "@/services/api";

type Props = {
  fileId: string;
  currentCode: string;
  onApplyPatch: (newCode: string) => void;
};

export default function PromptPanel({ fileId, currentCode, onApplyPatch }: Props) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const json = await api.code.improve(fileId, currentCode, text);
      if (json && json.updated_code) {
        onApplyPatch(json.updated_code);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to request code improvement");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ position: "absolute", right: 16, bottom: 16, width: 360, background: "#0b1220", color: "#fff", padding: 12, borderRadius: 8, boxShadow: "0 6px 18px rgba(0,0,0,0.6)" }}>
      <h4 style={{ margin: "0 0 8px 0" }}>Want to change something?</h4>
      <form onSubmit={handleSubmit}>
        <textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Describe the change you want..." style={{ width: "100%", height: 90 }} />
        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
          <button type="submit" disabled={loading || !text.trim()}>{loading ? "Working..." : "Apply"}</button>
        </div>
      </form>
    </div>
  );
}
