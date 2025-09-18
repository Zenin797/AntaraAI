from langchain_core.language_models import GenericFakeChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages(
    [("human", "Hello. Please respond in the style of {answer_style}.")]
)

# Placeholder LLM
llm = ChatGroq(model="llama-3.2-90b-text-preview")

chain = prompt | llm | StrOutputParser()

as_tool = chain.as_tool(
    name="Style responder", description="Description of when to use tool."
)
as_tool.args