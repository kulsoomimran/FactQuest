import os
import requests
import chainlit as cl
from dotenv import load_dotenv
from pydantic import BaseModel
from agents import Agent, Runner, RunConfig, AsyncOpenAI, OpenAIChatCompletionsModel
from openai.types.responses import ResponseTextDeltaEvent
from agents.tool import function_tool

# Load env vars
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not set in .env")
if not NEWS_API_KEY:
    raise ValueError("❌ NEWS_API_KEY not set in .env")

provider = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider
)

config = RunConfig(
    model=model,
    model_provider=provider,
    tracing_disabled=True,
)

class NewsSearchInput(BaseModel):
    query: str

@function_tool("news_search")
def news_search(input: NewsSearchInput) -> str:
    query = input.query.strip()
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"❌ News API error: {e}"

    articles = response.json().get("articles", [])
    if not articles:
        return f"No news found for **{query}**."

    # Build response
    results = [
        f"- [{a.get('title', 'No Title')}]({a.get('url', '#')}): {a.get('description', '')}"
        for a in articles
    ]
    return "\n".join(results)

agent = Agent(
    name="FactQuest",
    instructions="""
You are FactQuest — an expert assistant.
Use your own knowledge to answer general factual or historical questions.

Only use the `news_search` tool when the user asks about:
- current news or headlines
- recent or trending events
- real-world updates or ongoing situations

Do not use the tool for well-known facts — just answer them directly.
Always cite sources when using the tool.
""",
    tools=[news_search],
    model=model
)

@cl.on_chat_start
async def handle_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(
    content="""
    **Welcome to _FactQuest_!**
Ask me about recent news, past events and trending topics around the world
_Type your question below to begin..._
"""
).send()

@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")

    msg = cl.Message(content="")
    await msg.send()

    # Append user input
    history.append({"role": "user", "content": message.content})

    # Run the agent with streaming output
    result = Runner.run_streamed(
        agent,
        input=history,
        run_config=config,
    )

    # Stream assistant response token by token 
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            await msg.stream_token(event.data.delta)

    # Save assistant response to history
    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)
