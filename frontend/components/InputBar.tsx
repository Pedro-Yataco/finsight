"use client";
import { useState, KeyboardEvent } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";

interface Props {
  onSend: (content: string) => void;
  disabled?: boolean;
}

export function InputBar({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");

  function submit() {
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
  }

  function handleKey(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <div className="flex gap-3 p-4 border-t border-border bg-background shrink-0">
      <Textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKey}
        placeholder="Pregunta sobre una empresa... (ej: Analiza Apple)"
        disabled={disabled}
        rows={2}
        className="resize-none flex-1"
      />
      <Button
        onClick={submit}
        disabled={disabled || !value.trim()}
        size="icon"
        className="shrink-0 self-end h-10 w-10"
      >
        <Send className="h-4 w-4" />
      </Button>
    </div>
  );
}
