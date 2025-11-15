import os
import json
import re
from typing import Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None


def _normalize_email_text(email_text: str) -> str:
    """
    Normalize raw email text so classification is consistent
    for textarea, .txt uploads and .pdf uploads.
    """
    text = email_text or ""
    text = re.sub(r"\s+", " ", text)
    max_len = 4000
    if len(text) > max_len:
        text = text[:max_len]
    return text.strip()


def _detect_security_case(email_text: str) -> Optional[Dict[str, str]]:
    """
    Detect high-priority security cases (fraud or suspicious
    requests for card data). Returns a full response dict if a
    security case is detected, otherwise None.
    """
    text = (email_text or "").lower()

    sentences = [s.strip() for s in re.split(r"[.!?;\n\r]+", text) if s.strip()]

    def has_any(words):
        return any(w in text for w in words)

    def any_sentence(*groups):
        for s in sentences:
            if all(any(w in s for w in group) for group in groups):
                return True
        return False

    # Fraud / cloned card
    fraud_keywords = [
        "clonado",
        "cartão clonado",
        "cartao clonado",
        "fraude",
        "fraudaram",
        "compra que não fiz",
        "compra que nao fiz",
        "não reconheço",
        "nao reconheço",
        "nao reconheco",
        "compra não reconhecida",
        "compra nao reconhecida",
        "golpe no cartão",
        "golpe no cartao",
    ]

    if has_any(fraud_keywords):
        return {
            "category": "Produtivo",
            "sub_category": "Fraude / cartão clonado",
            "reason": "O e-mail cita possíveis compras não reconhecidas ou fraude no cartão.",
            "auto_reply": (
                "Olá! Sentimos muito pela situação relatada.\n\n"
                "Identificamos que sua mensagem menciona possíveis compras não reconhecidas ou suspeita de fraude no cartão. "
                "Por segurança, recomendamos que você:\n"
                "1) Bloqueie o cartão imediatamente pelo app, internet banking ou central de atendimento;\n"
                "2) Não compartilhe senhas ou códigos por e-mail, SMS ou mensagens de aplicativos;\n"
                "3) Aguarde o contato da nossa equipe especializada, que irá analisar o caso e orientar sobre o próximo passo.\n\n"
                "Se tiver algum número de protocolo, por favor informe na resposta a este e-mail para agilizar a análise."
            ),
        }

    # Security guidance / possible scam
    request_verbs = [
        "enviar",
        "enviasse",
        "mandar",
        "mandasse",
        "passar",
        "fornecer",
        "pedir",
        "pediu",
        "pediram",
        "solicitar",
        "solicitou",
        "solicitaram",
    ]

    card_data_words = [
        "dados",
        "informações",
        "informacoes",
        "números",
        "numeros",
        "numero",
        "número",
        "codigo",
        "código",
        "codigo de seguranca",
        "código de segurança",
    ]

    card_words = [
        "cartão",
        "cartao",
        "cartões",
        "cartoes",
        "cartão de crédito",
        "cartao de credito",
    ]

    channels = [
        "whatsapp",
        "wpp",
        "zap",
        "zapzap",
        "mensagem",
        "msg",
    ]

    cvv_words = [
        "cvv",
        "cvc",
        "codigo de segurança",
        "codigo de seguranca",
        "código de segurança",
        "senha do cartão",
        "senha do cartao",
        "senha do cartão de crédito",
        "senha do cartão de credito",
        "senha do cartao de credito",
    ]

    suspicious_combo = (
        any_sentence(request_verbs, card_data_words, card_words)
        or any_sentence(request_verbs, cvv_words)
        or any_sentence(request_verbs, card_words, channels)
        or any_sentence(card_data_words + cvv_words, card_words, channels)
    )

    explicit_phrases = [
        "pediu os numeros do meu cartao",
        "pediram os numeros do meu cartao",
        "pediram os numeros do cartão",
        "pediram os dados do meu cartão",
        "me pediu os dados do cartão",
        "me pediu os dados do cartao",
        "estão pedindo os dados do cartão",
        "estao pedindo os dados do cartao",
        "pediram meu cvv",
        "pediu meu cvv",
        "pediram o meu cvv",
        "pediu o meu cvv",
    ]

    has_cvv_and_request = any(w in text for w in cvv_words) and any(
        v in text for v in request_verbs
    )

    if suspicious_combo or has_any(explicit_phrases) or has_cvv_and_request:
        return {
            "category": "Produtivo",
            "sub_category": "Orientação de segurança / possível golpe",
            "reason": (
                "O e-mail menciona pedido de CVV, senha ou dados sensíveis do cartão, "
                "indicando possível golpe ou necessidade de orientação de segurança."
            ),
            "auto_reply": (
                "Olá! Obrigado por nos avisar.\n\n"
                "É muito importante nunca compartilhar os números completos do cartão, o código de segurança (CVV/CVC), "
                "senhas ou códigos recebidos por SMS, WhatsApp ou e-mail, mesmo que a solicitação pareça confiável.\n\n"
                "Recomendamos que você NÃO informe esses dados ao solicitante e, se desconfiar de golpe, "
                "entre em contato imediatamente com a nossa central oficial pelos canais de atendimento informados "
                "no verso do cartão ou em nosso site/app para verificar a situação e, se necessário, bloquear o cartão.\n\n"
                "Se puder, responda este e-mail informando quem fez o pedido e por qual canal (telefone, e-mail, mensagem), "
                "para que possamos orientar da melhor forma."
            ),
        }

    return None


def _rule_based_fallback(email_text: str) -> Dict[str, str]:
    """
    Apply a rule-based classifier as fallback when the model is
    unavailable or fails. Security has highest priority and only
    domain-related messages should be treated as productive.
    """
    security_case = _detect_security_case(email_text)
    if security_case:
        return security_case

    text = (email_text or "").lower()

    def has_any(words):
        return any(w in text for w in words)

    # Card limit management
    if has_any(
        [
            "aumento de limite",
            "aumentar o limite",
            "limite do cartão",
            "limite do cartao",
            "redução de limite",
            "reducao de limite",
            "diminuíram meu limite",
            "diminuiram meu limite",
            "aumento de crédito",
            "aumento de credito",
            "aumentar o crédito",
            "aumentar o credito",
            "limite de crédito",
            "limite de credito",
            "credito do cartão",
            "credito do cartao",
            "quero aumento de limite",
            "queria aumento de limite",
            "quero aumento de credito",
            "queria aumento de credito",
        ]
    ) or ("aumento" in text and ("limite" in text or "credito" in text or "crédito" in text)):
        return {
            "category": "Produtivo",
            "sub_category": "Gestão de limite do cartão",
            "reason": "O e-mail fala sobre aumento, redução ou dúvida em relação ao limite/crédito do cartão.",
            "auto_reply": (
                "Olá! Obrigado pelo contato.\n\n"
                "Identificamos que sua mensagem trata sobre limite/crédito do cartão. "
                "Nossa equipe irá verificar as informações do seu cadastro e do seu cartão para avaliar a possibilidade de ajuste.\n\n"
                "Para agilizar, por favor responda este e-mail com:\n"
                "- CPF do titular;\n"
                "- Últimos 4 dígitos do cartão;\n"
                "- Se deseja aumento, redução ou apenas esclarecimento sobre o limite.\n\n"
                "Assim que a análise for concluída, retornaremos com a atualização do seu pedido."
            ),
        }

    # Invoice / billing / charges
    if has_any(
        [
            "fatura",
            "fatura em aberto",
            "cobrança indevida",
            "cobranca indevida",
            "lançamento indevido",
            "lancamento indevido",
            "parcela não reconhecida",
            "parcela nao reconhecida",
            "juros na fatura",
            "juros indevidos",
        ]
    ):
        return {
            "category": "Produtivo",
            "sub_category": "Fatura / cobrança / lançamentos",
            "reason": "O texto menciona fatura, cobranças ou lançamentos questionados.",
            "auto_reply": (
                "Olá! Obrigado por entrar em contato sobre sua fatura.\n\n"
                "Identificamos que você está questionando lançamentos, valores ou cobranças indevidas. "
                "Vamos abrir ou prosseguir com a análise dos itens informados.\n\n"
                "Se ainda não enviou, por favor, responda este e-mail com:\n"
                "- Número do cartão (apenas os 4 últimos dígitos);\n"
                "- Mês de referência da fatura;\n"
                "- Descrição dos lançamentos que deseja contestar.\n\n"
                "Nossa equipe financeira irá avaliar e retornaremos com o posicionamento ou eventuais ajustes necessários."
            ),
        }

    # Invoice payment / boleto / unregistered payment
    if has_any(
        [
            "paguei a fatura",
            "paguei o boleto",
            "pagamento não compensado",
            "pagamento nao compensado",
            "não foi identificado o pagamento",
            "nao foi identificado o pagamento",
            "data de vencimento",
            "segunda via da fatura",
            "segunda via do boleto",
        ]
    ):
        return {
            "category": "Produtivo",
            "sub_category": "Pagamento de fatura / boleto",
            "reason": "O e-mail cita pagamento de fatura ou boleto, ou dúvidas sobre compensação.",
            "auto_reply": (
                "Olá! Obrigado pela mensagem.\n\n"
                "Verificamos que sua dúvida está relacionada ao pagamento de fatura ou boleto. "
                "Pagamentos podem levar até 3 dias úteis para compensar, dependendo da forma de pagamento e do banco utilizado.\n\n"
                "Para seguir com a análise, pedimos que responda este e-mail com:\n"
                "- Comprovante de pagamento anexado;\n"
                "- Data em que o pagamento foi realizado;\n"
                "- Se foi feito via TED, PIX, boleto ou débito automático.\n\n"
                "Após recebermos as informações, daremos sequência à verificação e retornaremos com uma atualização."
            ),
        }

    # Account / app / login access
    if has_any(
        [
            "não consigo acessar",
            "nao consigo acessar",
            "não consigo entrar",
            "nao consigo entrar",
            "senha inválida",
            "senha invalida",
            "esqueci minha senha",
            "trocar a senha",
            "aplicativo não abre",
            "aplicativo nao abre",
            "app não abre",
            "app nao abre",
            "login",
            "bloqueio de acesso",
        ]
    ):
        return {
            "category": "Produtivo",
            "sub_category": "Acesso à conta / aplicativo",
            "reason": "O usuário relata dificuldade de acesso, senha ou uso do aplicativo.",
            "auto_reply": (
                "Olá! Obrigado por nos avisar sobre a dificuldade de acesso.\n\n"
                "Sua mensagem indica problemas para acessar a conta ou o aplicativo (login, senha ou bloqueio). "
                "Para ajudar com segurança, pedimos que:\n"
                "1) Não envie sua senha por e-mail;\n"
                "2) Confirme se já tentou a opção 'Esqueci minha senha' no app ou site;\n"
                "3) Informe, respondendo este e-mail:\n"
                "   - CPF do titular;\n"
                "   - Sistema operacional do celular (Android ou iOS);\n"
                "   - Mensagem de erro exibida (se houver).\n\n"
                "Com essas informações, nossa equipe técnica poderá orientar o melhor procedimento para restabelecer seu acesso."
            ),
        }

    # Documents / receipts
    if has_any(
        [
            "segue em anexo",
            "estou enviando em anexo",
            "documentos em anexo",
            "comprovante em anexo",
            "anexo o comprovante",
        ]
    ):
        return {
            "category": "Produtivo",
            "sub_category": "Envio de documentos / comprovantes",
            "reason": "O e-mail menciona envio de documentos ou comprovantes para análise.",
            "auto_reply": (
                "Olá! Obrigado pelo envio dos documentos.\n\n"
                "Recebemos os arquivos anexados e vamos direcioná-los para a área responsável para conferência. "
                "Caso seja necessária alguma informação complementar ou novo documento, retornaremos por este mesmo canal.\n\n"
                "Se desejar, na resposta a este e-mail, você pode informar o número de protocolo (se já houver) para facilitar o acompanhamento interno."
            ),
        }

    # Courtesy / felicitation
    cortesia = has_any(
        [
            "feliz natal",
            "boas festas",
            "feliz ano novo",
            "parabéns",
            "parabens",
            "agradeço",
            "agradecimento",
            "obrigado",
            "obrigada",
            "grato",
            "grata",
        ]
    )

    intent_words = [
        "quero",
        "queria",
        "preciso",
        "gostaria",
        "solicito",
        "reclamo",
        "reclamação",
        "reclamacao",
        "dúvida",
        "duvida",
    ]
    finance_words = [
        "cartão",
        "cartao",
        "limite",
        "fatura",
        "boleto",
        "pagamento",
        "crédito",
        "credito",
        "conta",
        "empréstimo",
        "emprestimo",
    ]
    support_words = [
        "solicitação",
        "solicitacao",
        "protocolo",
        "chamado",
        "ticket",
        "caso",
        "suporte",
        "atendimento",
        "reclamação",
        "reclamacao",
        "análise",
        "analise",
    ]

    has_intent = has_any(intent_words)
    has_finance = has_any(finance_words)
    has_support = has_any(support_words)
    has_question = "?" in text

    if cortesia and not has_intent and not has_question:
        return {
            "category": "Improdutivo",
            "sub_category": "Mensagem de cortesia / felicitação",
            "reason": "A mensagem é de cortesia/felicitação, sem uma solicitação clara de ação.",
            "auto_reply": (
                "Olá! Muito obrigado pela mensagem e pelo carinho.\n\n"
                "Ficamos felizes com o seu contato. Sempre que precisar de ajuda com nossos serviços, "
                "estamos à disposição por aqui.\n\n"
                "Tenha um excelente dia!"
            ),
        }

    if len(text.strip()) < 30 and not has_intent and not has_finance and not has_question:
        return {
            "category": "Improdutivo",
            "sub_category": "Mensagem de cortesia / felicitação",
            "reason": "A mensagem é curta e não apresenta uma solicitação clara de ação.",
            "auto_reply": (
                "Olá! Muito obrigado pela mensagem.\n\n"
                "Se em algum momento você precisar de ajuda com nossos serviços, "
                "basta responder por aqui.\n\n"
                "Tenha um excelente dia!"
            ),
        }

    # Generic: only treat as productive if there is intent or a question
    # and the text is clearly related to the company's services.
    if (has_intent or has_question) and (has_finance or has_support):
        return {
            "category": "Produtivo",
            "sub_category": "Solicitação genérica de atendimento",
            "reason": "O e-mail parece tratar de uma solicitação ou dúvida relacionada ao atendimento financeiro.",
            "auto_reply": (
                "Olá! Obrigado pelo seu contato.\n\n"
                "Recebemos sua mensagem e vamos direcioná-la para a área responsável para análise. "
                "Caso seja necessário algum documento ou informação adicional, entraremos em contato por este mesmo e-mail.\n\n"
                "Se tiver número de protocolo ou mais detalhes sobre o que precisa, você pode responder esta mensagem para complementar."
            ),
        }

    # Out-of-scope or purely informative messages
    return {
        "category": "Improdutivo",
        "sub_category": "Mensagem informativa / fora de escopo",
        "reason": "O texto não apresenta pedido claro relacionado aos serviços financeiros da empresa.",
        "auto_reply": (
            "Olá! Obrigado pela mensagem.\n\n"
            "Identificamos que o conteúdo não traz uma solicitação ou dúvida diretamente relacionada aos nossos serviços financeiros. "
            "Se você precisar de algum suporte ou tiver uma solicitação específica, por favor responda este e-mail "
            "detalhando o que precisa, e teremos prazer em ajudar.\n\n"
            "Estamos à disposição."
        ),
    }


def classify_and_reply(email_text: str) -> dict:
    """
    Classify an email and build a suggested reply.
    Security cases are always detected first; if the model is
    unavailable or fails, a rule-based fallback is used. The same
    normalization is applied regardless of the source.
    """
    normalized_text = _normalize_email_text(email_text)

    security_case = _detect_security_case(normalized_text)
    if security_case:
        return security_case

    if client is None or not api_key:
        print("[AI_CLIENT] No API key configured or client unavailable, using rule-based fallback.")
        return _rule_based_fallback(normalized_text)

    system_message = (
        "Você é um assistente de atendimento ao cliente de uma grande empresa "
        "do setor financeiro. Sua função é analisar e-mails e classificá-los "
        "como Produtivo ou Improdutivo, além de definir uma subcategoria de demanda "
        "e sugerir uma resposta automática profissional e cordial em português.\n\n"
        "IMPORTANTE: casos de possível golpe, fraude ou pedido de dados sensíveis "
        "do cartão (como CVV, senha, dados completos do cartão) devem sempre ser tratados "
        "como de segurança, com orientação clara para NÃO compartilhar essas informações.\n\n"
        "Se o conteúdo estiver claramente fora do contexto de atendimento financeiro "
        "(por exemplo, perguntas genéricas como 'que horas são?'), classifique como "
        "Improdutivo em uma subcategoria de mensagem fora de escopo."
    )

    user_prompt = f"""
Você receberá o texto de um e-mail enviado por um cliente.

Sua tarefa é:
1. Classificar o email em uma das categorias principais: "Produtivo" ou "Improdutivo".
2. Definir uma subcategoria de atendimento, por exemplo:
   - "Status de solicitação em andamento"
   - "Gestão de limite do cartão"
   - "Fraude / cartão clonado"
   - "Fatura / cobrança / lançamentos"
   - "Pagamento de fatura / boleto"
   - "Acesso à conta / aplicativo"
   - "Envio de documentos / comprovantes"
   - "Mensagem de cortesia / felicitação"
   - "Solicitação genérica de atendimento"
   - "Orientação de segurança / possível golpe"
   - "Mensagem informativa / fora de escopo"
3. Explicar resumidamente o motivo da classificação.
4. Sugerir uma resposta automática adequada, em português, com tom profissional e cordial.

Regras:
- "Produtivo": o email pede ajuda, traz dúvida, reclamação, solicitação, acompanhamento de caso
  ou qualquer coisa que possa exigir ação da equipe, relacionada aos serviços financeiros.
- "Improdutivo": o email é apenas uma saudação, agradecimento, felicitação, mensagem genérica
  ou algo que não exige ação, ou ainda está claramente fora do contexto dos serviços da empresa.
- Se o e-mail mencionar pedido de CVV, senha, dados completos do cartão ou sinais de golpe,
  priorize subcategorias de segurança como "Fraude / cartão clonado" ou
  "Orientação de segurança / possível golpe" e oriente o cliente a NÃO compartilhar dados sensíveis.

Responda APENAS com um JSON válido, sem comentários, no formato:

{{
  "category": "Produtivo ou Improdutivo",
  "sub_category": "nome da subcategoria",
  "reason": "explicação curta da classificação",
  "auto_reply": "texto da resposta automática sugerida"
}}

Email recebido:
\"\"\"{normalized_text}\"\"\"    
"""

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
            ],
        )

        raw_text = completion.choices[0].message.content

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            print("[AI_CLIENT] Invalid JSON from model, using rule-based fallback.")
            data = _rule_based_fallback(normalized_text)

        if "sub_category" not in data:
            data["sub_category"] = "Solicitação genérica de atendimento"

        return data

    except Exception as e:
        print(f"[AI_CLIENT] Error calling OpenAI ({type(e).__name__}): {e}")
        print("[AI_CLIENT] Using rule-based fallback instead.")
        return _rule_based_fallback(normalized_text)
