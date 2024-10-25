import os
from crewai_tools import tool, SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool, FileReadTool, PDFSearchTool
from crewai_tools import tool
from crewai import Agent, Task, Crew, Process
from groq import Groq
from langchain_openai import ChatOpenAI
import requests
from bs4 import BeautifulSoup


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

def scrape_websites(urls):
    all_content = []
    for url in urls:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            content = ' '.join([p.get_text() for p in soup.find_all('p')])
            all_content.append(content)
        except Exception as e:
            print(f"Erro ao acessar {url}: {e}")
    return ' '.join(all_content)

client = Groq(
   api_key=os.environ.get(groq_api_key),
)
class Agent:
    def __init__(self, name, personality, context, goal, backstory):
        self.name = name
        self.personality = personality
        self.context = context
        self.goal = goal
        self.backstory = backstory

    def generate_response(self, messages):
        formatted_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
        return client.chat.completions.create(messages=formatted_messages, model="llama3-8b-8192").choices[0].message.content
urls = [
    "https://www.gov.br/anatel/pt-br/consumidor/conheca-seus-direitos/banda-larga",
    "https://www.gov.br/anatel/pt-br/consumidor/conheca-seus-direitos/telefonia-movel",
    "https://www.gov.br/anatel/pt-br/consumidor/conheca-seus-direitos/telefonia-fixa",
    "https://www.gov.br/anatel/pt-br/consumidor/conheca-seus-direitos/tv-por-assinatura",
    "https://www2.camara.leg.br/legin/fed/lei/1960-1969/lei-4117-27-agosto-1962-353835-publicacaooriginal-22620-pl.html"
]
agent_context = scrape_websites(urls)
agents = [
    Agent(
        name="Eduardo", 
        personality="Amigavel e informativo", 
        context="Funcionario de atendimento ao cliente da ANATEL", 
        goal="Descobrir se o problema se trata de um problema tecnico ou juridico e encaminhar para o respectivo departamento correto.", 
        backstory="Você trabalha como suporte tecnico na ANATEL(Agencia Nacional de Telecomunicações), e deve diferenciar um problema juridico de um tecnico e rencaminhar para o departamento necessario."
    ),
    Agent(
        name="Julinho", 
        personality="Amigavel e informativo", 
        context="Funcionario do setor juridico da ANATEL. informações adicionais:{agent_context}", 
        goal="Você deve auxiliar o usuario com problemas juridicos, utilizar as informações do:{agent_context} para descobrir as intercorrencias legais e ajudar o cliente a resolver o problema, como seguir com processos legais", 
        backstory="Você trabalha como suporte tecnico na ANATEL(Agencia Nacional de Telecomunicações), e deve diferenciar um problema juridico de um tecnico e rencaminhar para o departamento necessario."
    ),
]
while True:
    agent = agents[1]
    conversation_history = []

    while True:
        question = input(f"Insira a sua pergunta (ou digite sair para sair): ")
        if question.lower() == 'sair':
            break
        
        # Adicionar a pergunta ao histórico
        conversation_history.append({"role": "user", "content": question})

        # Gerar a mensagem do sistema com o histórico
        system_message = {"role": "system", "content": f"Você é {agent.name}, {agent.personality}. Context: {agent.context}. Goal: {agent.goal}. Backstory: {agent.backstory}."}
        
        # Criar a mensagem completa para enviar ao modelo
        messages = [system_message] + conversation_history
        
        # Gerar resposta
        response = agent.generate_response(messages)

        # Adicionar a resposta ao histórico
        conversation_history.append({"role": "assistant", "content": response})

        print(f"{agent.name}: {response}")
