import os, config, requests
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from crewai_tools import tool, SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool, FileReadTool, PDFSearchTool
from crewai import Agent, Task, Crew, Process
from groq import Groq
from langchain_openai import ChatOpenAI
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk
from tkinter import Scrollbar

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
    def __init__(self, name, personality, context, goal, backstory, openai_api_key):
        self.name = name
        self.personality = personality
        self.context = context
        self.goal = goal
        self.backstory = backstory
        self.client = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key)  # Cliente ChatOpenAI instanciado

    def generate_response(self, messages):
        # Converter mensagens para o formato correto
        formatted_messages = []
        for msg in messages:
            if msg["role"] == "user":
                formatted_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "system":
                formatted_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                formatted_messages.append(AIMessage(content=msg["content"]))

        # Usar invoke para gerar resposta
        response = self.client.invoke(formatted_messages)
        return response.content

# URLs para coleta de contexto
urls = [
    "https://www.gov.br/anatel/pt-br/consumidor/perguntas-frequentes"
]
agent_context = scrape_websites(urls)

# Pdfs para coleta de contexto
agent_pdf_context = PDFSearchTool("./apostilatele2.pdf")
agent_pdf_context2 = PDFSearchTool("./apostilatele.pdf")
agent_pdf_context3 = PDFSearchTool("./perguntasFrequentes.pdf")
agent_pdf_context4 = PDFSearchTool("./lei_normas.pdf")
agent_pdf_context5 = PDFSearchTool("./telecoLegislaçao.pdf")

# Criação dos agentes
agents = [
    Agent(
        name="Eduardo",
        personality="Amigável e prestativo",
        context="Funcionário de atendimento ao cliente da ANATEL. Você responde as perguntas em português do Brasil de maneira resumida porém informativa. As respostas devem ser semelhantes as respostas encontradas no {agent_pdf_context3}. Lembre-se de utilizar as informações do {agent_context}",
        goal="Descobrir se o problema é técnico ou jurídico e encaminhar para o respectivo departamento. Você responde as perguntas em português do Brasil de maneira resumida porém informativa com no maximo 100 palavras. As respostas devem ser extremamente semelhantes as respostas encontradas no {agent_pdf_context3}. Lembre-se de utilizar as informações do {agent_context}",
        backstory="Você trabalha como suporte técnico na ANATEL e deve diferenciar problemas jurídicos de técnicos e encaminhar ao departamento necessário.",
        openai_api_key=openai_api_key
    ),
    Agent(
        name="Julio",
        personality="Amigável e prestativo",
        context="Funcionário do setor jurídico da ANATEL.Você responde as perguntas em português do Brasil e de maneira resumida porém informativa. Informações adicionais: {agent_pdf_context}, {agent_pdf_context2}, {agent_pdf_context3}, {agent_pdf_context4} e {agent_pdf_context5} . As respostas devem ser extremamente semelhantes as respostas encontradas no {agent_pdf_context3}. Lembre-se de utilizar as informações do {agent_context}",
        goal="Auxiliar o usuário com problemas jurídicos, utilizando informações de {agent_pdf_context}, {agent_pdf_context2}, {agent_pdf_context4} e {agent_pdf_context5} para resolver o problema legalmente. Você responde as perguntas em português do Brasil de maneira resumida porém informativa com no maximo 100 palavras. As respostas devem ser extremamente semelhantes as respostas encontradas no {agent_pdf_context3}. Lembre-se de utilizar as informações do {agent_context}",
        backstory="Você trabalha no setor jurídico da ANATEL e deve ajudar clientes a resolver problemas legais.",
        openai_api_key=openai_api_key
    ),
    Agent(
        name="Marcia",
        personality="Amigável e prestativa",
        context="Funcionária do setor técnico da ANATEL, engenheira de telecomunicações altamente competente. Você responde as perguntas em português do Brasil e de maneira resumida. Informações adicionais: {agent_pdf_context} e {agent_pdf_context2} e {agent_pdf_context3}. As respostas devem ser extremamente semelhantes as respostas encontradas no {agent_pdf_context3}. Lembre-se de utilizar as informações do {agent_context}",
        goal="Auxiliar o usuário com problemas técnicos, utilizando {agent_pdf_context} e {agent_pdf_context2} para orientar sobre soluções técnicas ou encaminhamento para assistência. Você responde as perguntas em português do Brasil de maneira resumida porém informativa com no maximo 100 palavras. As respostas devem ser extremamente semelhantes as respostas encontradas no {agent_pdf_context3}. Lembre-se de utilizar as informações do {agent_context}",
        backstory="Você trabalha como técnica na ANATEL e deve ajudar usuários com problemas técnicos.",
        openai_api_key=openai_api_key
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
            {"role": "system", "content": agente_destino.context},
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

    # Adicionar a pergunta e a resposta ao canvas
    adicionar_mensagem_canvas(f"{pergunta}", "cliente")
    adicionar_mensagem_canvas(f"{agente_atual.name}: {resposta}", "atendente")

    # Limpa o campo de entrada
    entry.delete(0, tk.END)

# Função para adicionar mensagens ao Canvas com espaçamento ajustado
def adicionar_mensagem_canvas(texto, tipo):
    global y_offset

    # Determina a posição e estilo
    if tipo == "cliente":
        bg = "#7289da"  # Azul para cliente
        fg = "white"
        anchor = "e"  # Alinha à direita
        padx = (540, 10)  # Margem maior na esquerda
    else:
        bg = "#43b581"  # Verde para atendente
        fg = "white"
        anchor = "w"  # Alinha à esquerda
        padx = (10, 555)  # Margem maior na direita
        
    largura_maxima = 400  # Defina a largura máxima que a mensagem pode ocupar
    wraplength = largura_maxima - 20  # Um pouco de margem para não colar na borda
    
    # Cria um Frame para encapsular a mensagem
    msg_frame = tk.Frame(messages_frame, bg="#2c2f33")
    msg_frame.pack(fill=tk.X, pady=5)

    # Cria o Label para a mensagem
    label = tk.Label(
        msg_frame,
        text=texto,
        bg=bg,
        fg=fg,
        wraplength=wraplength,  # Limita a largura do texto
        justify="left",
        font=("Arial", 10),
        padx=5,
        pady=5,
    )
    label.pack(anchor=anchor, padx=padx)

    # Atualiza o scroll para o final
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)

# Configuração da interface
root = tk.Tk()
root.title("Chatbot ANATEL")
root.geometry("960x640")
root.configure(bg='#2c2f33')

# Frame principal para o Canvas e Scrollbar
chat_frame = tk.Frame(root, bg='#23272a')
chat_frame.pack(fill=tk.BOTH, expand=True)

# Canvas para exibir mensagens
canvas = tk.Canvas(chat_frame, bg="#2c2f33", highlightthickness=0)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Frame interno para mensagens
messages_frame = tk.Frame(canvas, bg="#2c2f33")
canvas.create_window((0, 0), window=messages_frame, anchor="nw")

# Scrollbar
scrollbar = tk.Scrollbar(chat_frame, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.config(yscrollcommand=scrollbar.set)

# Configurações de redimensionamento
messages_frame.bind("<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all")))

# Campo de entrada
entry = tk.Entry(root, font=("Arial", 12))
entry.pack(fill=tk.X, padx=10, pady=5)
entry.bind("<Return>", enviar_pergunta)

# Botão de enviar
send_button = tk.Button(root, text="Enviar", command=enviar_pergunta, bg="#7289da", fg="white")
send_button.pack(pady=5)

# Configurações iniciais
y_offset = 10
agente_atual = agents[0]
conversation_history = []

root.mainloop()


while True:
    question = input("Insira a sua pergunta (ou digite sair para falar com o Eduardo): ")
    if question.lower() == 'sair':
            agente_atual = processar_pergunta(question, conversation_history, agents[0])

    agente_atual = processar_pergunta(question, conversation_history, agente_atual)

