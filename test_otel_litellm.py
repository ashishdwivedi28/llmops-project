import litellm
print(litellm.success_callback)
try:
    litellm.success_callback = ["opentelemetry"]
    print("Success setting opentelemetry callback")
except Exception as e:
    print(e)
