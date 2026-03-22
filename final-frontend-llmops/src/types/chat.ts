import type { AppId, PipelineType, TaskDetection } from "./api";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  // Only present on assistant messages (populated from InvokeResponse)
  metadata?: {
    pipelineExecuted: PipelineType;
    taskDetection: TaskDetection;
    model: string;
    latencyMs: number;
    appId: AppId;
  };
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  selectedApp: AppId;
}