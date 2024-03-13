import asyncio
import os
import openai
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

openai.api_key = os.environ.get("API_KEY")

app = FastAPI()

origins = [os.environ.get("ENDPOINT")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)


async def generate_text_stream(prompt: str):
    try:
        # Use async iteration for efficient streaming
        for response in openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=100,
            n=1,
            stream=True
        ):
            yield "data:" + response.choices[0].text + "\n"
            await asyncio.sleep(0.01)
    except openai.error.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI Error: {e}")


@app.get("/generate-text", response_class=StreamingResponse)
async def openai_streaming(prompt: str):
    async def stream_generator():
        async for data in generate_text_stream(prompt):
            yield data

    return StreamingResponse(
        content=stream_generator(),
        media_type="text/event-stream",
    )