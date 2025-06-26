curl http://localhost:12434/engines/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
        "model": "ai/gemma3",
        "messages": [
          {
            "role": "system",
            "content": "You are a helpful assistant."
          },
          {
            "role": "user",
            "content": "Please write 500 words about the fall of Rome."
          }
        ]
      }'

curl http://model-runner.docker.internal/engines/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
        "model": "ai/gemma3",
        "messages": [
          {
            "role": "system",
            "content": "You are a helpful assistant."
          },
          {
            "role": "user",
            "content": "Please write 500 words about the fall of Rome."
          }
        ]
      }'

#docker compose run backend /bin/bash