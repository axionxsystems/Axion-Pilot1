import React, { useEffect, useState } from "react";
import { api } from "@/services/api";

type Props = {
  filePath?: string;
  refreshSignal?: number;
};

export default function LivePreview({ filePath, refreshSignal }: Props) {
  const [html, setHtml] = useState("<html><body><p>No file selected</p></body></html>");

  useEffect(() => {
    if (!filePath) return;
    let cancelled = false;
    api.code.getPreviewHtml(filePath)
      .then((text) => { if (!cancelled) setHtml(text); })
      .catch((err) => console.error(err));
    return () => { cancelled = true; };
  }, [filePath, refreshSignal]);

  return (
    <div style={{ width: "100%", height: "100%", borderLeft: "1px solid #222" }}>
      <iframe
        title="Live Preview"
        style={{ width: "100%", height: "100%", border: 0 }}
        sandbox=""
        srcDoc={html}
      />
    </div>
  );
}
