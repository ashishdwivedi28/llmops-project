"use client";

import { FormEvent, useState } from "react";

interface ChatInputProps {
  onSend: (text: string) => Promise<void>;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [value, setValue] = useState("");

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const text = value.trim();
    if (!text || isLoading) {
      return;
    }

    setValue("");
    await onSend(text);
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-xl border border-black/10 bg-background p-3 shadow-sm">
      <label htmlFor="chat-input" className="sr-only">
        Ask your question
      </label>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <textarea
          id="chat-input"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="Ask about your LLMOps system..."
          rows={3}
          className="w-full resize-none rounded-lg border border-black/10 bg-transparent px-3 py-2 text-sm outline-none ring-0 placeholder:text-foreground/50 focus:border-foreground/40"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || value.trim().length === 0}
          className="inline-flex h-10 items-center justify-center rounded-lg bg-foreground px-4 text-sm font-medium text-background transition disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? "Sending..." : "Send"}
        </button>
      </div>
    </form>
  );
}
