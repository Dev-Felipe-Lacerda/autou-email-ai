\# EmailSmart – Classificador de E-mails com IA



Aplicação web simples para \*\*classificar e-mails de atendimento\*\* (Produtivo / Improdutivo), identificar \*\*subcategorias de demanda\*\* e sugerir \*\*respostas automáticas\*\*, pensada para equipes de atendimento de uma grande empresa do setor financeiro.



Projeto desenvolvido como \*\*case técnico\*\* e mantido como parte do meu portfólio público.



---



\## Funcionalidades



\- Upload de arquivos \*\*.txt\*\* ou \*\*.pdf\*\* contendo o texto do e-mail

\- Entrada manual de texto (copiar/colar o conteúdo do e-mail)

\- Classificação automática em:

&nbsp; - \*\*Produtivo\*\* – requer ação (suporte, limite, fatura, acesso ao app, etc.)

&nbsp; - \*\*Improdutivo\*\* – felicitações, agradecimentos, mensagens genéricas ou fora de escopo

\- Subcategorias específicas, como:

&nbsp; - `Fraude / cartão clonado`

&nbsp; - `Orientação de segurança / possível golpe`

&nbsp; - `Gestão de limite do cartão`

&nbsp; - `Fatura / cobrança / lançamentos`

&nbsp; - `Pagamento de fatura / boleto`

&nbsp; - `Acesso à conta / aplicativo`

&nbsp; - `Envio de documentos / comprovantes`

&nbsp; - `Mensagem de cortesia / felicitação`

&nbsp; - `Mensagem informativa / fora de escopo`

\- \*\*Resposta automática sugerida\*\*, pronta para copiar e ajustar

\- Interface responsiva com \*\*Tailwind CSS\*\*

\- \*\*Tema claro/escuro\*\* (toggle no canto superior direito)



---



\## Arquitetura



\- \*\*Backend:\*\* FastAPI (Python)

\- \*\*Frontend:\*\* HTML + Tailwind CSS + JavaScript (vanilla)

\- \*\*Templates:\*\* Jinja2

\- \*\*IA:\*\* OpenAI API (modelo GPT) + regras locais (rule-based) para fallback e segurança

\- \*\*Extração de texto de PDF:\*\* `pdfplumber`



---



\## Segurança e Regras de Negócio



Antes de chamar a API de IA, o backend aplica um \*\*pré-classificador rule-based\*\* para:



\- Detectar termos de \*\*fraude\*\* e \*\*cartão clonado\*\*

\- Identificar pedidos de:

&nbsp; - \*\*CVV / CVC\*\*

&nbsp; - \*\*senha do cartão\*\*

&nbsp; - \*\*dados completos do cartão\*\*

\- Priorizar respostas que:

&nbsp; - Orientam o cliente a \*\*não compartilhar dados sensíveis\*\*

&nbsp; - Direcionam para \*\*canais oficiais\*\* (app, central de atendimento, site)



Além disso:



\- Conteúdos claramente \*\*fora do contexto financeiro\*\* (ex.: “Que horas são?”) são classificados como

&nbsp; `Improdutivo / fora de escopo`

\- Mensagens curtas de \*\*cortesia\*\* ou \*\*felicitação\*\* (ex.: “Felix Natal, obrigado pelo atendimento!”)

&nbsp; são tratadas como `Improdutivo / mensagem de cortesia / felicitação`



---



\## Stack



\- Python 3.11

\- FastAPI

\- Uvicorn

\- OpenAI API

\- pdfplumber

\- Jinja2

\- Tailwind CSS

\- Vanilla JS



---



\## Como rodar localmente



\### 1. Clonar o repositório



```bash

git clone https://github.com/SEU-USUARIO/autou-email-ai.git

cd autou-email-ai



