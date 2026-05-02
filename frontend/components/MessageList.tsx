"use client";
import { useEffect, useRef } from "react";
import { MessageBubble, LoadingSkeleton } from "@/components/MessageBubble";
import { Message } from "@/types/chat";

interface Props {
  messages: Message[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, isLoading]);

  return (
    <div className="flex-1 min-h-0 overflow-y-auto">
      <div className="max-w-3xl mx-auto py-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isLoading && <LoadingSkeleton />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
