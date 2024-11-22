import os
from crewai_tools import tool, SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool, FileReadTool, PDFSearchTool
from crewai import Agent, Task, Crew, Process
from groq import Groq
from langchain_openai import ChatOpenAI
import requests
from bs4 import BeautifulSoup
import config
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

# Funções para carregar as chaves de API
def get_openai_api_key():
    return config.openai_api_key

def get_serper_api_key():
    return config.Serper_api_key

# Configuração das chaves de API
serper_api_key = get_serper_api_key()
openai_api_key = get_openai_api_key()
os.environ["SERPER_API_KEY"] = serper_api_key
os.environ["OPENAI_API_KEY"] = openai_api_key

# Inicializa o modelo do OpenAI
client = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key)

# Função para coletar conteúdo de várias URLs
def scrape_websites(urls):
    all_content = []
    for url in urls:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            content = ' '.join([p.get_text() for p in soup.find_all(['p', 'li', 'a', 'ul', 'div'])])
            all_content.append(content)
        except Exception as e:
            print(f"Erro ao acessar {url}: {e}")
    return ' '.join(all_content)

# Inicializa o cliente Groq

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
        return client.chat.completions.create(messages=formatted_messages, model="gpt4o_mini_llm").choices[0].message.content

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
    "https://informacoes.anatel.gov.br/legislacao/atos-de-certificacao-de-produtos/2020/1493-ato-7280",
    "https://www.gov.br/anatel/pt-br/consumidor/perguntas-frequentes"
]
agent_context = scrape_websites(urls)
# Pdfs para coleta de contexto
agent_pdf_context = PDFSearchTool("./data/apostilatele2.pdf")
agent_pdf_context2 = PDFSearchTool("./data/apostilatele.pdf")
agent_pdf_context3 = PDFSearchTool("./data/perguntasFrequentes.pdf")

# Criação dos agentes
agents = [
    Agent(
        name="Eduardo", 
        personality="Amigável e prestativo", 
        context="Funcionário de atendimento ao cliente da ANATEL. Você responde as perguntas em português do Brasil de maneira resumida e {agent_pdf_context3}. As respostas devem ser semelhantes as respostas no {agent_pdf_context3}", 
        goal="Descobrir se o problema é técnico ou jurídico e encaminhar para o respectivo departamento. Você responde as perguntas em português do Brasil de maneira resumida com no maximo 100 palavras. As respostas devem ser semelhantes as respostas no {agent_pdf_context3}", 
        backstory="Você trabalha como suporte técnico na ANATEL e deve diferenciar problemas jurídicos de técnicos e encaminhar ao departamento necessário."
    ),
    Agent(
        name="Julio", 
        personality="Amigável e prestativo", 
        context="Funcionário do setor jurídico da ANATEL.Você responde as perguntas em português do Brasil e de maneira resumida. Informações adicionais: {agent_context}, {agent_pdf_context} e {agent_pdf_context2} e {agent_pdf_context3}. As respostas devem ser semelhantes as respostas no {agent_pdf_context3}", 
        goal="Auxiliar o usuário com problemas jurídicos, utilizando informações de {agent_context}, {agent_pdf_context} e {agent_pdf_context2} para resolver o problema legalmente. Você responde as perguntas em português do Brasil de maneira resumida com no maximo 100 palavras. As respostas devem ser semelhantes as respostas no {agent_pdf_context3}", 
        backstory="Você trabalha no setor jurídico da ANATEL e deve ajudar clientes a resolver problemas legais."
    ),
    Agent(
        name="Marcia", 
        personality="Amigável e prestativa", 
        context="Funcionária do setor técnico da ANATEL, engenheira de telecomunicações altamente competente. Você responde as perguntas em português do Brasil e de maneira resumida. Informações adicionais: {agent_context}, {agent_pdf_context} e {agent_pdf_context2} e {agent_pdf_context3}. As respostas devem ser semelhantes as respostas no {agent_pdf_context3}", 
        goal="Auxiliar o usuário com problemas técnicos, utilizando {agent_context}, {agent_pdf_context} e {agent_pdf_context2} para orientar sobre soluções técnicas ou encaminhamento para assistência. Você responde as perguntas em português do Brasil de maneira resumida com no maximo 100 palavras. As respostas devem ser semelhantes as respostas no {agent_pdf_context3}", 
        backstory="Você trabalha como técnica na ANATEL e deve ajudar usuários com problemas técnicos."
    ),
]

# Função para classificar o problema
def classificar_problema(texto):
    palavras_tecnicas = [
        "sinal", "instalação", "configuração", "conexão", "equipamento",
        "caindo", "reparo", "conexao", "cair", "fraco", "conecta",
        "falha", "caido", "falhado", "wifi", "wi-fi", "falhando",
        "instalacao", "cabo", "fibra", "otica", "optica", "internet",
        "instabilidade", "roteador", "configurar", "mensagem", "texto",
        "dispositivo", "dispositivos", "modem", "suporte", "velocidade",
        "interferencias", "interferências", "manutenção", "manutencao",
        "erro", "bug", "sistema", "rede", "hardware", "repetidores",
        "software", "atualização", "atualizacao", "incompatiblidade",
        "incompativel", "desempenho", "backup", "recuperação", "recuperacao",
        "diagnostico", "diagnóstico", "solução", "solucao", "wireless", "remoto",
        "assistencia", "assistência", "manual", "guias", "guia", "reparação", "reparacao",
        "firmware", "incompatiblidade", "backup", "vpn", "ip", "dns"
    ]
    palavras_juridicas = [
        "contrato", "reembolso", "cancelamento", "fatura", "dívida",
        "regulamento", "lei", "comunicado", "pagamento", "divida",
        "direito", "multa", "consumidor", "direitos", "portabilidade",
        "transferencia", "operadora", "número", "numero", "cobrado",
        "cobrança", "cobranca", "taxa", "preço", "preco", "valor", "suporte",
        "dinheiro", "reclamacao", "reclamação", "prazo", "prazos", "contratada",
        "contratei", "cobrar", "provedor", "provedora", "licença", "licenca",
        "regulamentação", "regulamentacao", "regulação", "regulacao", "regulamento",
        "homologar", "homologação", "homologacao", "processo" "procedencia", "procedência",
        "normas", "monitorar", "deveres", "recursos", "mediação", "mediacao", "constitucional",
        "suspensão", "suspensao", "servico", "serviço", "contestacao", "contestação", "contestaçao",
        "credito", "crédito", "prestadora", "franquia", "consumo", "telefonica", "telefÔnica"
    ]
    tecnico_score = sum(1 for palavra in palavras_tecnicas if palavra in texto.lower())
    juridico_score = sum(1 for palavra in palavras_juridicas if palavra in texto.lower())
    if tecnico_score > juridico_score:
        return "tecnico"
    elif juridico_score > tecnico_score:
        return "juridico"
    else:
        return "indefinido"

# Função para processar a pergunta e redirecionar ao agente correto
def processar_pergunta(question, conversation_history, agente_atual):
    tipo_problema = classificar_problema(question)
    
    if tipo_problema == "tecnico":
        agente_destino = agents[2]  # Agente Marcia
        print("Redirecionando para Marcia (Suporte Técnico).")
    elif tipo_problema == "juridico":
        agente_destino = agents[1]  # Agente Julio
        print("Redirecionando para Julio (Suporte Jurídico).")
    else:
        agente_destino = agente_atual  # Manter o agente atual
        print("Problema indefinido. Mantendo com", agente_destino.name, "para nova triagem.")
    
    # Adicionar a pergunta ao histórico
    conversation_history.append({"role": "user", "content": question})
    
    # Criar a mensagem de contexto
    system_message = {
        "role": "system",
        "content": f"Você é {agente_destino.name}, {agente_destino.personality}. Context: {agente_destino.context}. Goal: {agente_destino.goal}. Backstory: {agente_destino.backstory}."
    }
    
    # Formatar as mensagens e gerar a resposta
    messages = [system_message] + conversation_history
    response = agente_destino.client.generate_response(
        messages=[
            {"role": "system", "content": agente.context},
            {"role": "user", "content": question}
        ]
    )

    # Adicionar a resposta ao histórico
    conversation_history.append({"role": "assistant", "content": response})

    print(f"{agente_destino.name}: {response}")
    
    return agente_destino  # Retorna o agente atual

# Função para processar a pergunta e redirecionar ao agente correto
def processar_pergunta_interface(question, conversation_history, agente_atual):
    tipo_problema = classificar_problema(question)
    
    if tipo_problema == "tecnico":
        agente_destino = agents[2]  # Agente Marcia
        print("Redirecionando para Marcia (Suporte Técnico).")
    elif tipo_problema == "juridico":
        agente_destino = agents[1]  # Agente Julio
        print("Redirecionando para Julio (Suporte Jurídico).")
    else:
        agente_destino = agente_atual  # Manter o agente atual
        print("Problema indefinido. Mantendo com", agente_destino.name, "para nova triagem.")
    
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
    
    return agente_destino, response  # Retorna o agente atual e a resposta gerada

# Função para enviar a pergunta e mostrar a resposta na interface
def enviar_pergunta(event=None):
    pergunta = entry.get()  # Captura a pergunta do campo de entrada
    if pergunta.strip() == "":
        return
    
    # Atualiza o histórico de conversa e processa a pergunta
    global agente_atual, conversation_history
    agente_atual, resposta = processar_pergunta_interface(pergunta, conversation_history, agente_atual)
    
    # Exibe a pergunta e a resposta na área de mensagens
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, f"Você: {pergunta}\n", 'color')
    chat_display.insert(tk.END, f"{agente_atual.name}: {resposta}\n\n", 'color')
    chat_display.config(state=tk.DISABLED)

    
    # Limpa o campo de entrada
    entry.delete(0, tk.END)

# Criação da interface com Tkinter
root = tk.Tk()
root.title("Chatbot ANATEL")
root.configure(bg='#2c2f33')
root.geometry("960x640")
root.minsize(960, 640)
frame = tk.Frame(root, bg='#23272a')
frame.place(relwidth=1, relheight=1)


# Configuração do campo de exibição de mensagens
chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=30, state=tk.DISABLED, background='#99aab5', foreground='#ffffff')
chat_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

# Campo de entrada de perguntas
entry = tk.Entry(root, width=80)
entry.grid(row=1, column=0, padx=10, pady=10)

# Botão para enviar pergunta
send_button = tk.Button(root, text="Enviar", command=enviar_pergunta)
send_button.grid(row=1, column=1, padx=10, pady=10)

entry.bind("<Return>", enviar_pergunta)


# Inicia a interface
root.mainloop()

# Loop principal
agente_atual = agents[0]  # Começa com o agente Eduardo
conversation_history = []

while True:
    question = input("Insira a sua pergunta (ou digite sair para falar com o Eduardo): ")
    if question.lower() == 'sair':
            agente_atual = processar_pergunta(question, conversation_history, agents[0])

    agente_atual = processar_pergunta(question, conversation_history, agente_atual)

