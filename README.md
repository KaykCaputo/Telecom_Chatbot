> **Nota:** Este projeto foi desenvolvido como trabalho acadêmico no IFSC.

# Telecom_Chatbot 🤖📡

**Telecom_Chatbot** é um sistema de chatbot inteligente voltado para consumidores da ANATEL, que utiliza múltiplos agentes com especializações distintas para responder dúvidas **técnicas** e **jurídicas** relacionadas a serviços de telecomunicações. O sistema é capaz de classificar automaticamente o tipo de problema e encaminhar para o agente mais apropriado.

## 🧠 Tecnologias Utilizadas

- **[LangChain](https://www.langchain.com/)**: Criação e gerenciamento de agentes com memória.
- **[CrewAI](https://docs.crewai.com/)**: Coordenação de múltiplos agentes com objetivos distintos.
- **[OpenAI GPT-4o-mini](https://platform.openai.com/)**: Geração de respostas naturais.
- **[Tkinter](https://docs.python.org/3/library/tkinter.html)**: Interface gráfica interativa.
- **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)**: Extração de contexto via scraping de sites da ANATEL.
- **[Serper.dev](https://serper.dev/)** (opcional): Buscas complementares na web.
- **dotenv**: Gerenciamento seguro de chaves via `.env`.

## 🤖 Agentes Inteligentes

| Nome        | Função                      | Especialidade                                |
| ----------- | --------------------------- | -------------------------------------------- |
| **Eduardo** | Agente principal e roteador | Classifica e redireciona perguntas           |
| **Julio**   | Agente jurídico             | Foco em leis, contratos, cobranças, direitos |
| **Marcia**  | Agente técnico              | Foco em conexão, equipamentos, sinal etc.    |

## 📚 Fontes de Conhecimento

- **Scraping ANATEL:**

  - [Perguntas Frequentes](https://www.gov.br/anatel/pt-br/consumidor/perguntas-frequentes)
  - [Lei Geral de Telecomunicações](https://www.planalto.gov.br/ccivil_03/leis/l9472.htm)

- **PDFs Utilizados (pasta `/data`):**
  - Documentos normativos e explicativos da ANATEL e Teleco.

## 🧪 Classificação Inteligente

A função `classificar_problema()` faz a triagem com base em palavras-chave técnicas e jurídicas para garantir que o problema seja encaminhado ao agente correto. Em caso de empate ou ausência de palavras-chave, o problema é considerado “indefinido” e permanece com o agente atual para nova triagem.

## 🖼️ Interface Gráfica

A interface com o usuário é feita via **Tkinter**, com campo de entrada e exibição de mensagens do cliente e dos agentes, usando cores distintas para melhor usabilidade.

## 🚀 Como Executar

### Pré-requisitos

- Python 3.9 ou superior
- Conta na OpenAI e/ou Serper.dev (opcional)

### Instalação

```bash
git clone https://github.com/seu-usuario/Telecom_Chatbot.git
cd Telecom_Chatbot
pip install -r requirements.txt
```

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz com:

```
OPEN_AI_API_KEY=sua_chave_openai
SERPER_API_KEY=sua_chave_serper(opcional)
```

### Execução

```
python3 main.py
```

---

Desenvolvido por: [Kayk Caputo](https://github.com/KaykCaputo) e [André Gustavo](https://github.com/AndreXP1)
