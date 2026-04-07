import asyncio

from google.adk.runners import InMemoryRunner
from google.genai import types

from googlemap_mcp.map_agent.agent import root_agent

APP_NAME = "place_search"
USER_ID = "user"


async def main():
    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )

    print("Place Search Agent (type 'exit' to quit)")
    while True:
        try:
            user_input = input("\nYou > ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_input.strip().lower() in ("exit", "quit"):
            break

        message = types.Content(
            role="user", parts=[types.Part.from_text(text=user_input)]
        )
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=message,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"\nAgent > {part.text}")


if __name__ == "__main__":
    asyncio.run(main())
