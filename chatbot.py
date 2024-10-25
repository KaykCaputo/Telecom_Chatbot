import os
from crewai_tools import tool, SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool, FileReadTool, PDFSearchTool
from crewai_tools import tool
from crewai import Agent, Task, Crew, Process
from groq import Groq
from langchain_openai import ChatOpenAI


def get_openai_api_key():
   with open('./keys/API_LLM_OpenAI.txt', 'r') as file:
       return file.read().strip()


def get_groq_api_key():
   with open('./keys/API_Groq.txt', 'r') as file:
       return file.read().strip()


def get_serper_api_key():
   with open('./keys/API_Serper.txt', 'r') as file:
       return file.read().strip()


groq_api_key = get_groq_api_key()
serper_api_key = get_serper_api_key()
openai_api_key = get_openai_api_key()
os.environ["GROQ_API_KEY"] = groq_api_key
os.environ["SERPER_API_KEY"] = serper_api_key
os.environ["OPENAI_API_KEY"] = openai_api_key


gpt4o_mini_llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key)


client = Groq(
   api_key=os.environ.get(groq_api_key),
)
while 1==1:
   question = input("Enter your question: ")
   chat_completion = client.chat.completions.create(
       messages=[
           {
               "role": "user",
               "content": question,
           }
       ],
       model="llama3-8b-8192",
   )
print(chat_completion.choices[0].message.content)
