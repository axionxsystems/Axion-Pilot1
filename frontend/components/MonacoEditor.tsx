import React, { useRef, useEffect } from "react";
import Editor, { OnChange, Monaco } from "@monaco-editor/react";

type Props = {
  language: string;
  value: string;
  onChange: (val: string | undefined) => void;
  onSave?: () => void;
  onMount?: (editor: any, monaco: Monaco) => void;
};

const AxionTheme = {
  base: "vs-dark",
  inherit: true,
  rules: [],
  colors: {},
};

export default function MonacoEditor({ language, value, onChange, onSave, onMount }: Props) {
  const editorRef = useRef<any>(null);

  function handleEditorDidMount(editor: any, monaco: Monaco) {
    try {
      monaco.editor.defineTheme("axion-dark", AxionTheme);
    } catch (e) {}
    editorRef.current = editor;
    if (onMount) onMount(editor, monaco);
  }

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
        e.preventDefault();
        if (onSave) onSave();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onSave]);

  return (
    <Editor
      height="100%"
      defaultLanguage={language}
      language={language}
      value={value}
      theme="axion-dark"
      onMount={handleEditorDidMount}
      onChange={onChange as OnChange}
      options={{
        automaticLayout: true,
        minimap: { enabled: false },
        formatOnPaste: true,
        formatOnType: true,
      }}
    />
  );
}
