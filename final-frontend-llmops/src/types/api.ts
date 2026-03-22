// All types exactly match the backend POST /invoke contract

export type AppId = "mock_app" | "default_llm" | "rag_bot" | "code_agent";

export type PipelineType = "llm" | "rag" | "agent";

export interface InvokeRequest {
  app_id: AppId;
  user_input: string;
}

export interface TaskDetection {
  needs_rag: boolean;
  needs_agent: boolean;
}

export interface InvokeResponse {
  app_id: AppId;
  user_input: string;
  config: Record<string, unknown>;
  task_detection: TaskDetection;
  pipeline_executed: PipelineType;
  output: string;
  latency_ms: number;
}

export interface HealthResponse {
  status: string;
  message: string;
}

export interface ApiError {
  detail: string;
  status: number;
}