import litellm
import contextvars

litellm.vertex_project = "search-ahmed"
litellm.vertex_location = "us-central1"

usage_context = contextvars.ContextVar(
    "usage_context", 
    default={"prompt_tokens": 0, "completion_tokens": 0, "total_cost": 0.0}
)

def track_usage_callback(kwargs, completion_response, start_time, end_time):
    print("CALLBACK TRIGGERED!")
    usage = dict(usage_context.get())
    print(f"Usage object type: {type(completion_response.usage)}")
    print(f"Usage content: {completion_response.usage}")
    if hasattr(completion_response, "usage") and completion_response.usage:
        usage["prompt_tokens"] += getattr(completion_response.usage, "prompt_tokens", 0)
        usage["completion_tokens"] += getattr(completion_response.usage, "completion_tokens", 0)
    try:
        cost = litellm.completion_cost(completion_response)
        print(f"Cost: {cost}")
        if cost is not None:
            usage["total_cost"] += float(cost)
    except Exception as e:
        print("Cost error:", e)
    usage_context.set(usage)
    print("New context:", usage_context.get())

litellm.success_callback = [track_usage_callback]

response = litellm.completion(model="vertex_ai/gemini-2.5-flash", messages=[{"role": "user", "content": "hi"}])
print("Final Context:", usage_context.get())
