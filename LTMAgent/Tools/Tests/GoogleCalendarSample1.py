from langchain_google_community import CalendarToolkit
from langchain_google_community import CalendarToolkit
from langchain_google_community.calendar.utils import (
    build_resource_service,
    get_google_credentials,
)
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent



# Can review scopes here: https://developers.google.com/calendar/api/auth
# For instance, readonly scope is https://www.googleapis.com/auth/calendar.readonly
credentials = get_google_credentials(
    token_file="token.json",
    scopes=["https://www.googleapis.com/auth/calendar"],
    client_secrets_file="Tools/Tests/credentials.json",
)

api_resource = build_resource_service(credentials=credentials)
toolkit = CalendarToolkit(api_resource=api_resource)
tools = toolkit.get_tools()
# print(tools)

# llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
llm = init_chat_model("meta-llama/llama-4-scout-17b-16e-instruct", model_provider="groq")
agent_executor = create_react_agent(llm, tools)
example_query = "What are my upcoming events?"

events = agent_executor.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()