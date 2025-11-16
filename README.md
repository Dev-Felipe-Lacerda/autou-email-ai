\# EmailSmart – Classificador de E-mails com IA



Aplicação web para classificar e-mails de atendimento (Produtivo / Improdutivo), identificar subcategorias de demanda e sugerir respostas automáticas.  

O cenário simulado é de uma grande empresa do setor financeiro com alto volume de e-mails diários.



Projeto desenvolvido como case técnico para automação de triagem de e-mails e mantido como parte do meu portfólio público.



---



\## Demo online



A aplicação está disponível em:



https://autou-email-ai-tf2b.onrender.com



---



\## Funcionalidades



\- Entrada de texto (copiar/colar o conteúdo do e-mail)

\- Upload de arquivos `.txt` ou `.pdf` contendo o texto do e-mail

\- Classificação automática em:

&nbsp; - Produtivo – requer ação (limite, fatura, acesso ao app, documentos, etc.)

&nbsp; - Improdutivo – felicitações, agradecimentos, mensagens genéricas ou fora de escopo

\- Subcategorias de atendimento, como:

&nbsp; - `Fraude / cartão clonado`

&nbsp; - `Orientação de segurança / possível golpe`

&nbsp; - `Gestão de limite do cartão`

&nbsp; - `Fatura / cobrança / lançamentos`

&nbsp; - `Pagamento de fatura / boleto`

&nbsp; - `Acesso à conta / aplicativo`

&nbsp; - `Envio de documentos / comprovantes`

&nbsp; - `Mensagem de cortesia / felicitação`

&nbsp; - `Mensagem informativa / fora de escopo`

\- Resposta automática sugerida, pronta para copiar e ajustar

\- Interface responsiva com \*\*Tailwind CSS\*\*

\- Tema claro/escuro (toggle no canto superior direito)



---



\## Arquitetura



\- Backend: FastAPI (Python)

\- Frontend: HTML + Tailwind CSS + JavaScript (vanilla)

\- Templates: Jinja2

\- IA: OpenAI API (modelo GPT) + regras locais (rule-based) para fallback e segurança

\- Extração de texto de PDF: `pdfplumber`



---



\## Regras de negócio e segurança



Antes de chamar a API de IA, o backend aplica um pré-processamento e um classificador rule-based que:



\- Detecta termos de fraude e cartão clonado

\- Identifica pedidos de:

&nbsp; - CVV / CVC

&nbsp; - senha do cartão

&nbsp; - dados completos do cartão

\- Prioriza respostas que:

&nbsp; - orientam o cliente a não compartilhar dados sensíveis

&nbsp; - direcionam para canais oficiais (app, central de atendimento, site)



Além disso:



\- Mensagens claramente fora do contexto financeiro (ex.: “Que horas são?”) viram  

&nbsp; `Improdutivo / Mensagem informativa / fora de escopo`

\- Mensagens de cortesia/felicitação (ex.: “Feliz Natal, obrigado pelo atendimento!”) viram  

&nbsp; `Improdutivo / Mensagem de cortesia / felicitação`



Se a API da OpenAI estiver indisponível ou sem quota, o sistema continua funcionando com o fallback rule-based.



---



\## Stack



\- Python 3.11

\- FastAPI

\- Uvicorn / Gunicorn

\- OpenAI API

\- pdfplumber

\- Jinja2

\- Tailwind CSS

\- Vanilla JS



---



\## Como rodar localmente



\### 1. Clonar o repositório



```bash

git clone https://github.com/Dev-Felipe-Lacerda/autou-email-ai.git

cd autou-email-ai



