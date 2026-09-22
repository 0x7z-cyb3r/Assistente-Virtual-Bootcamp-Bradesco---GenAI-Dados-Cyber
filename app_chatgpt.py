import sys
import getpass
from typing import List, Dict, Any
from openai import OpenAI

BASE_CONHECIMENTO: List[Dict[str, Any]] = [
  {
    "categoria": "Microempreendedorismo",
    "pergunta": "O que é e como calcular o Capital de Giro?",
    "tags": ["capital de giro", "fluxo de caixa", "reserva", "empresa", "mei"],
    "resposta": "Capital de Giro é o recurso financeiro necessário para sustentar as operações da sua empresa no dia a dia (pagar fornecedores, salários, contas). Para calcular: subtraia o Passivo Circulante (obrigações de curto prazo) do Ativo Circulante (recursos disponíveis a curto prazo). Fórmula: Capital de Giro Líquido (CGL) = Ativo Circulante - Passivo Circulante."
  },
  {
    "categoria": "Microempreendedorismo",
    "pergunta": "Como separar a conta física (PF) da conta jurídica (PJ)?",
    "tags": ["separar contas", "pf", "pj", "conta bancaria", "pro-labore"],
    "resposta": "Para separar PF de PJ: 1) Abra uma conta bancária PJ exclusiva para a empresa. 2) Registre todas as entradas e saídas do negócio apenas nela. 3) Estabeleça um Pro-labore (um salário fixo mensal para você) e transfira esse valor para sua conta PF. 4) Nunca pague contas pessoais com o dinheiro da conta PJ."
  },
  {
    "categoria": "Finanças Pessoais",
    "pergunta": "Como funciona a regra dos 50/30/20?",
    "tags": ["regra 50/30/20", "planejamento", "orçamento", "pessoal", "gastos"],
    "resposta": "A regra dos 50/30/20 é um método de organização orçamentária que divide a renda líquida em três categorias: 50% para Necessidades Essenciais (moradia, saúde, alimentação, transporte); 30% para Desejos Pessoais (lazer, hobbies, compras não essenciais); e 20% para Prioridades Financeiras (poupança, investimentos ou quitação de dívidas)."
  },
  {
    "categoria": "Microempreendedorismo",
    "pergunta": "Quais são os perigos da antecipação de recebíveis?",
    "tags": ["antecipação de recebíveis", "cartão de crédito", "taxa", "juros", "risco"],
    "resposta": "A antecipação de recebíveis permite receber antes o dinheiro de vendas a prazo. O perigo reside nas altas taxas de desconto e juros cobradas pelos bancos, que corroem a margem de lucro da empresa, gerando um ciclo vicioso de dependência financeira e desfalque no fluxo de caixa dos meses futuros."
  }
]

def buscar_contexto(query: str, limite: int = 2) -> str:
    termos_busca: List[str] = query.lower().split()
    blocos_relevantes: List[Dict[str, Any]] = []
    for item in BASE_CONHECIMENTO:
        pontuacao: int = 0
        pergunta: str = item["pergunta"].lower()
        resposta: str = item["resposta"].lower()
        tags: List[str] = [tag.lower() for tag in item["tags"]]
        for termo in termos_busca:
            if termo in pergunta: pontuacao += 3
            if termo in tags: pontuacao += 2
            if termo in resposta: pontuacao += 1
        if pontuacao > 0:
            blocos_relevantes.append({"item": item, "score": pontuacao})
    blocos_relevantes.sort(key=lambda x: x["score"], reverse=True)
    contexto_filtrado: List[str] = []
    for bloco in blocos_relevantes[:limite]:
        conteudo = bloco["item"]
        contexto_filtrado.append(f"Categoria: {conteudo['categoria']}\nContexto: {conteudo['resposta']}")
    return "\n\n---\n\n".join(contexto_filtrado) if contexto_filtrado else ""

def avaliar_resposta_sistema(resposta_gerada: str) -> bool:
    frase_seguranca = "Desculpe, não possuo essa informação na minha base de dados"
    if frase_seguranca in resposta_gerada:
        return True
    return "[ERRO" not in resposta_gerada

def executar_assistente() -> None:
    print("=" * 70)
    print("      ASSISTENTE CHATGPT: FINANÇAS E MICROEMPREENDEDORISMO     ")
    print("=" * 70)
    api_key = getpass.getpass("🔑 Digite sua OpenAI API Key (os caracteres ficam invisíveis): ").strip()
    if not api_key:
        print("[ERRO] A chave de API não pode ser vazia.")
        sys.exit(1)
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"[ERRO] Falha ao inicializar o cliente OpenAI: {e}")
        sys.exit(1)

    print("\nConexão configurada! Digite 'sair' para encerrar.\n")

    system_instruction = (
        "Você é o 'FinTech Advisor', um consultor sênior em saúde financeira. "
        "Seu tom é empático, prático e direto.\n\n"
        "REGRA CRÍTICA ANTI-ALUCINAÇÃO:\n"
        "Se a dúvida do usuário não puder ser respondida com base estrita no CONTEXTO FORNECIDO, "
        "você DEVE responder EXATAMENTE a seguinte frase e nada mais:\n"
        "'Desculpe, não possuo essa informação na minha base de dados para te ajudar com segurança. Deseja falar sobre capital de giro ou finanças pessoais?'"
    )

    while True:
        try:
            pergunta: str = input("\n👤 Você: ").strip()
            if not pergunta:
                continue
            if pergunta.lower() in ["sair", "exit", "quit"]:
                print("\nSessão encerrada. Até logo!")
                break
            print("🤖 Consultando base local e processando com ChatGPT...")
            contexto: str = buscar_contexto(pergunta)
            prompt_final = (
                f"CONTEXTO FORNECIDO:\n{contexto if contexto else 'NENHUM CONTEXTO DISPONÍVEL'}\n\n"
                f"PERGUNTA DO USUÁRIO: {pergunta}"
            )
            resposta = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt_final}
                ],
                temperature=0.1
            )
            resposta_final = resposta.choices.message.content or ""
            print(f"\n🤖 Assistente:\n{resposta_final}")
            if not avaliar_resposta_sistema(resposta_final):
                print("\n⚠️  [ALERTA]: A resposta gerada falhou nos testes internos de validação.")
            print("\n" + "-" * 50)
        except KeyboardInterrupt:
            print("\n\nSessão encerrada via teclado.")
            break
        except Exception as e:
            print(f"\n[ERRO NA REQUISIÇÃO]: {e}")

if __name__ == "__main__":
    executar_assistente()
