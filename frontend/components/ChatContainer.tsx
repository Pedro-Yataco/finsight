"use client";
import { useState } from "react";
import { Message } from "@/types/chat";
import { sendMessage } from "@/lib/api";
import { MessageList } from "@/components/MessageList";
import { InputBar } from "@/components/InputBar";

const WELCOME: Message = {
  id: "welcome",
  role: "assistant",
  content:
    "Hola, soy **FinSight**. Puedo analizar los fundamentos de cualquier empresa que cotice en bolsa.\n\n¿Sobre qué empresa quieres saber más? Puedes escribir el nombre o el ticker directamente *(ej: Apple, TSLA, MercadoLibre)*.",
};

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSend(content: string) {
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const reply = await sendMessage(content);
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", content: reply },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content:
            "Lo siento, ocurrió un error al conectar con el servidor. Por favor intenta de nuevo.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      <header className="shrink-0 border-b border-border px-6 py-4">
        <h1 className="text-xl font-semibold tracking-tight">FinSight</h1>
        <p className="text-xs text-muted-foreground mt-0.5">
          Análisis fundamental de acciones
        </p>
      </header>
      <MessageList messages={messages} isLoading={isLoading} />
      <InputBar onSend={handleSend} disabled={isLoading} />
    </div>
  );
}
