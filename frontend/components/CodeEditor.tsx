import React, { useState, useEffect } from "react";
import MonacoEditor from "./MonacoEditor";
import LivePreview from "./LivePreview";
import PromptPanel from "./PromptPanel";
import { api } from "@/services/api";

type FileNode = {
  id: string;
  name: string;
  path: string;
  isDir?: boolean;
  children?: FileNode[];
};

export default function CodeEditor() {
  const [tree, setTree] = useState<FileNode[]>([]);
  const [currentFile, setCurrentFile] = useState<FileNode | null>(null);
  const [code, setCode] = useState("");
  const [refresh, setRefresh] = useState(0);

  useEffect(() => {
    api.code.getTree().then((j) => setTree(j || [])).catch((err) => console.error(err));
  }, []);

  async function openFile(file: FileNode) {
    setCurrentFile(file);
    const json = await api.code.getFile(file.path);
    setCode(json.content || "");
  }

  async function saveFile() {
    if (!currentFile) return;
    await api.code.saveFile(currentFile.path, code);

    // Execute and capture output
    try {
      const ext = currentFile.name.split(".").pop() || "python";
      const json = await api.code.execute(ext, code);
      const outArea = document.getElementById("code-output-area");
      if (outArea) {
        outArea.innerText = `Exit ${json.exit_code}\n\nSTDOUT:\n${json.stdout}\n\nSTDERR:\n${json.stderr}`;
      }

      // Basic Python traceback parsing for line numbers
      const win = window as any;
      if (json.stderr && win.monacoEditorAPI && win.monaco) {
        try {
          const matches = json.stderr.matchAll(/File \".*\", line (\d+)/g);
          const markers: any[] = [];
          for (const m of matches) {
            const line = parseInt(m[1], 10);
            if (!isNaN(line)) {
              markers.push({ startLineNumber: line, startColumn: 1, endLineNumber: line, endColumn: 1, message: "Error reported by execution", severity: win.monaco.MarkerSeverity.Error });
            }
          }
          if (markers.length && win.monacoEditorAPI.getModel()) {
            win.monaco.editor.setModelMarkers(win.monacoEditorAPI.getModel(), "owner", markers);
          }
        } catch (err) {
          console.warn("Failed to set markers", err);
        }
      }

    } catch (err) {
      console.error(err);
    }

    setRefresh((r) => r + 1);
  }

  return (
    <div style={{ height: "100vh", display: "grid", gridTemplateColumns: "260px 1fr 520px", gridTemplateRows: "auto 180px" }}>
      <div style={{ padding: 8, overflow: "auto", borderRight: "1px solid #222" }}>
        <h3>Files</h3>
        <ul>
          {tree.map((f) => (
            <li key={f.id} onClick={() => openFile(f)} style={{ cursor: "pointer" }}>{f.name}</li>
          ))}
        </ul>
      </div>

      <div style={{ position: "relative", height: "100%" }}>
        <MonacoEditor
          language={currentFile?.name?.split(".").pop() || "javascript"}
          value={code}
          onChange={(v) => setCode(v || "")}
          onSave={saveFile}
          onMount={(editor, monaco) => {
            // Expose simple API on window for quick marker updates
            (window as any).monacoEditorAPI = {
              getModel: () => editor.getModel(),
            };
            (window as any).monaco = monaco;
          }}
        />
        <PromptPanel fileId={currentFile?.path || ""} currentCode={code} onApplyPatch={(newCode) => { setCode(newCode); setTimeout(() => saveFile(), 200); }} />
      </div>

      <div style={{ display: "flex", flexDirection: "column" }}>
        <div style={{ flex: 1, minHeight: 0 }}>
          <LivePreview filePath={currentFile?.path} refreshSignal={refresh} />
        </div>
        <div style={{ height: 180, borderTop: "1px solid #222", background: "#05060a", color: "#fff", padding: 8, overflow: "auto" }}>
          <strong>Terminal / Output</strong>
          <div id="code-output-area">Logs and execution results will appear here.</div>
        </div>
      </div>
    </div>
  );
}
