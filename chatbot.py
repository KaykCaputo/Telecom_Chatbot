import os
from crewai_tools import tool, SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool, FileReadTool, PDFSearchTool
from crewai import Agent, Task, Crew, Process
from groq import Groq
from langchain_openai import ChatOpenAI
import requests
from bs4 import BeautifulSoup

# Funções para carregar as chaves de API
def get_openai_api_key():
   with open('./keys/API_LLM_OpenAI.txt', 'r') as file:
       return file.read().strip()

def get_groq_api_key():
   with open('./keys/API_Groq.txt', 'r') as file:
       return file.read().strip()

def get_serper_api_key():
   with open('./keys/API_Serper.txt', 'r') as file:
       return file.read().strip()

# Configuração das chaves de API
groq_api_key = get_groq_api_key()
serper_api_key = get_serper_api_key()
openai_api_key = get_openai_api_key()
os.environ["GROQ_API_KEY"] = groq_api_key
os.environ["SERPER_API_KEY"] = serper_api_key
os.environ["OPENAI_API_KEY"] = openai_api_key

# Inicializa o modelo do OpenAI
gpt4o_mini_llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key)

# Função para coletar conteúdo de várias URLs
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

# Inicializa o cliente Groq
client = Groq(api_key=groq_api_key)

# Classe de agente
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

# URLs para coleta de contexto
urls = [
    "https://www.gov.br/anatel/pt-br/consumidor/conheca-seus-direitos/banda-larga",
    "https://www.gov.br/anatel/pt-br/consumidor/conheca-seus-direitos/telefonia-movel",
    "https://www.gov.br/anatel/pt-br/consumidor/conheca-seus-direitos/telefonia-fixa",
    "https://www.gov.br/anatel/pt-br/consumidor/conheca-seus-direitos/tv-por-assinatura",
    "https://www2.camara.leg.br/legin/fed/lei/1960-1969/lei-4117-27-agosto-1962-353835-publicacaooriginal-22620-pl.html",
    "https://opfibra.com.br/anatel/conheca-as-principais-normas-da-anatel/",
    "https://www.teleco.com.br/legis.asp",
    "https://informacoes.anatel.gov.br/legislacao/atos-de-certificacao-de-produtos/2020/1493-ato-7280",
    "https://www.gov.br/anatel/pt-br/regulado/numeracao/regulamentacao",
    "https://opfibra.com.br/anatel/conheca-as-principais-normas-da-anatel/",
    "https://informacoes.anatel.gov.br/legislacao/atos-de-certificacao-de-produtos/2020/1493-ato-7280"
]
agent_context = scrape_websites(urls)
# Pdfs para coleta de contexto
agent_pdf_context = PDFSearchTool("./data/apostilatele2.pdf")
agent_pdf_context2 = PDFSearchTool("./data/apostilatele.pdf")

# Criação dos agentes
agents = [
    Agent(
        name="Eduardo", 
        personality="Amigável e prestativo", 
        context="Funcionário de atendimento ao cliente da ANATEL", 
        goal="Descobrir se o problema é técnico ou jurídico e encaminhar para o respectivo departamento.", 
        backstory="Você trabalha como suporte técnico na ANATEL e deve diferenciar problemas jurídicos de técnicos e encaminhar ao departamento necessário."
    ),
    Agent(
        name="Julio", 
        personality="Amigável e prestativo", 
        context="Funcionário do setor jurídico da ANATEL. Informações adicionais: {agent_context}, {agent_pdf_context} e {agent_pdf_context2}", 
        goal="Auxiliar o usuário com problemas jurídicos, utilizando informações de {agent_context}, {agent_pdf_context} e {agent_pdf_context2} para resolver o problema legalmente.", 
        backstory="Você trabalha no setor jurídico da ANATEL e deve ajudar clientes a resolver problemas legais."
    ),
    Agent(
        name="Marcia", 
        personality="Amigável e prestativa", 
        context="Funcionária do setor técnico da ANATEL, engenheira de telecomunicações altamente competente. Informações adicionais: {agent_context}, {agent_pdf_context} e {agent_pdf_context2}", 
        goal="Auxiliar o usuário com problemas técnicos, utilizando {agent_context}, {agent_pdf_context} e {agent_pdf_context2} para orientar sobre soluções técnicas ou encaminhamento para assistência.", 
        backstory="Você trabalha como técnica na ANATEL e deve ajudar usuários com problemas técnicos."
    ),
]

# Função para classificar o problema
def classificar_problema(texto):
    palavras_tecnicas = ["sinal", "instalação", "configuração", "conexão", "equipamento", "caindo", "reparo", "conexao", "cair","fraco", "conecta", "falha"]
    palavras_juridicas = ["contrato", "reembolso", "cancelamento", "fatura", "dívida", "regulamento", "lei", "comunicado", "pagamento", "divida"]
    tecnico_score = sum(1 for palavra in palavras_tecnicas if palavra in texto.lower())
    juridico_score = sum(1 for palavra in palavras_juridicas if palavra in texto.lower())
    if tecnico_score > juridico_score:
        return "tecnico"
    elif juridico_score > tecnico_score:
        return "juridico"
    else:
        return "indefinido"

# Função para processar a pergunta e redirecionar ao agente correto
def processar_pergunta(question, conversation_history):
    tipo_problema = classificar_problema(question)
    
    if tipo_problema == "tecnico":
        agente_destino = agents[2]  # Agente Marcia
        print("Redirecionando para Marcia (Suporte Técnico).")
    elif tipo_problema == "juridico":
        agente_destino = agents[1]  # Agente Julio
        print("Redirecionando para Julio (Suporte Jurídico).")
    else:
        agente_destino = agents[0]  # Eduardo permanece como o agente padrão
        print("Problema indefinido. Mantendo com Eduardo para nova triagem.")
    
    # Adicionar a pergunta ao histórico
    conversation_history.append({"role": "user", "content": question})
    
    # Criar a mensagem de contexto
    system_message = {
        "role": "system",
        "content": f"Você é {agente_destino.name}, {agente_destino.personality}. Context: {agente_destino.context}. Goal: {agente_destino.goal}. Backstory: {agente_destino.backstory}."
    }
    
    # Formatar as mensagens e gerar a resposta
    messages = [system_message] + conversation_history
    response = agente_destino.generate_response(messages)

    # Adicionar a resposta ao histórico
    conversation_history.append({"role": "assistant", "content": response})

    print(f"{agente_destino.name}: {response}")

# Loop principal
while True:
    question = input("Insira a sua pergunta (ou digite sair para sair): ")
    if question.lower() == 'sair':
        break
    processar_pergunta(question, conversation_history=[])
