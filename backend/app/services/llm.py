# # from langchain_xai import 
# from langchain_groq import ChatGroq

# from app.core.config import settings

# llm = ChatGroq(
#     model=settings.MODEL_NAME,
#     api_key=settings.GROK_API_KEY,
#     temperature=settings.TEMPERATURE,
#     max_tokens=settings.MAX_OUTPUT_TOKENS,
# )


from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

llm = ChatGoogleGenerativeAI(
    model=settings.MODEL_NAME,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=settings.TEMPERATURE,
    max_output_tokens=settings.MAX_OUTPUT_TOKENS,
)
