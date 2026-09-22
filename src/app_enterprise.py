import os
import sys
import time
import math
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Set, Union, Callable

# -----------------------------------------------------------------------------------------
# SUBSISTEMA CORPORATIVO DE AUDITORIA E LOGGING REGISTRÁVEL
# -----------------------------------------------------------------------------------------
# Garante a rastreabilidade total de eventos operacionais no terminal do Kali Linux.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [THREAD:%(thread)d] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("EnterpriseFintechSystem")


# -----------------------------------------------------------------------------------------
# CAMADA DE ENTIDADES DE NEGÓCIO (DOMAIN ENTERPRISE ENTITIES)
# -----------------------------------------------------------------------------------------
@dataclass(frozen=True)
class DocumentoCorporativo:
    """
    Entidade imutável que representa um nó estruturado de conhecimento na base local.
    A imutabilidade garante que os dados da base de conhecimento não sofram corrupção em memória
    durante execuções concorrentes ou buscas recursivas de termos.
    """
    id_documento: int
    categoria: str
    pergunta: str
    tags: Set[str]
    resposta: str
    peso_institucional: float = 1.0


@dataclass
class RegistroTelemetria:
    """
    Data Transfer Object (DTO) projetado para capturar metadados operacionais de cada interação.
    Esses indicadores são fundamentais para o preenchimento das métricas exigidas pelo Passo 5.
    """
    id_evento: int
    timestamp_inicio: float
    timestamp_fim: float
    query_usuario: str
    resposta_sistema: str
    contexto_encontrado: bool
    alucinacao_bloqueada: bool
    score_relevancia: float

    @property
    def latencia_ms(self) -> float:
        """Calcula o tempo real de resposta da aplicação em milissegundos."""
        return (self.timestamp_fim - self.timestamp_inicio) * 1000.0


# -----------------------------------------------------------------------------------------
# ENGENHARIA DE PROMPT E ESPECIFICAÇÃO DE PERSONA (PASSO 1 & PASSO 3)
# -----------------------------------------------------------------------------------------
# Regras explícitas injetadas no motor de processamento lógico para moldar a IA (System Instructions).
# Contém as amarras de segurança corporativa necessárias para evitar qualquer desvio comportamental.
INSTRUCAO_SISTEMA_PERSONA: str = (
    "Você é o 'FinTech Advisor', um agente computacional sênior focado na saúde financeira "
    "de pessoas físicas e microempreendedores individuais (MEI). Sua comunicação baseia-se "
    "nos princípios de empatia, clareza técnica, assertividade e responsabilidade fiscal.\n\n"
    "POLÍTICA DE BLINDAGEM OPERACIONAL (ANTI-ALUCINAÇÃO RAG):\n"
    "1. Você receberá um segmento estruturado denominado 'CONTEXTO FORNECIDO DA BASE LOCAL'.\n"
    "2. Varra esse contexto minuciosamente em busca da resposta exata solicitada pelo usuário.\n"
    "3. Caso o contexto esteja vazio, nulo ou omitido de dados factuais para sanar a dúvida, "
    "sua resposta final DEVE ser, de forma cirúrgica e imutável, exatamente a frase entre aspas:\n"
    "'Desculpe, não possuo essa informação na minha base de dados para te ajudar com segurança. "
    "Deseja falar sobre capital de giro ou finanças pessoais?'\n\n"
    "4. É terminantemente proibido complementar a frase de segurança acima com quaisquer saudações, "
    "conselhos adicionais, desculpas informais ou pontuações extras.\n\n"
    "DIRETRIZ DE ENGENHARIA DE PENSAMENTO (CHAIN-OF-THOUGHT):\n"
    "Antes de emitir qualquer resposta técnica, execute o isolamento sintático do contexto para garantir "
    "que nenhuma premissa não verificada seja adicionada ao texto de saída."
)


# -----------------------------------------------------------------------------------------
# MOTOR DE ENGENHARIA DE DADOS E INDEXAÇÃO DE TEXTO (PASSO 2 & PASSO 4 - RAG ENGINE)
# -----------------------------------------------------------------------------------------
class RepositorioConhecimentoLocal:
    """
    Gerencia a carga, validação estrutural e a varredura semântica/textual da base de dados.
    Esta classe simula com precisão cirúrgica um banco de dados vetorial de produção.
    """
    
    def __init__(self) -> None:
        self._documentos: List[DocumentoCorporativo] = []
        self._carregar_e_indexar_base()

    def _carregar_e_indexar_base(self) -> None:
        """Popula o repositório com cenários de alta complexidade do mercado real."""
        dataset_bruto: List[Dict[str, Any]] = [
            {
                "id": 201,
                "categoria": "Gestão de Caixa Microempresarial",
                "pergunta": "Como calcular e gerenciar o Capital de Giro?",
                "tags": ["capital de giro", "fluxo de caixa", "reserva", "empresa", "mei", "caixa", "passivo", "ativo"],
                "resposta": "O Capital de Giro representa a liquidez necessária para manter a operação ativa no curto prazo. O cálculo sênior consiste na apuração do Capital de Giro Líquido (CGL). Fórmula estruturada: CGL = Ativo Circulante (caixa, bancos, aplicações de curto prazo, contas a receber) - Passivo Circulante (fornecedores, obrigações trabalhistas, impostos imediatos). Se o CGL for negativo, a empresa está operando em risco de insolvência iminente."
            },
            {
                "id": 202,
                "categoria": "Governança Corporativa e Finanças",
                "pergunta": "Qual a melhor prática para separar conta física (PF) de jurídica (PJ)?",
                "tags": ["separar contas", "pf", "pj", "conta bancaria", "pro-labore", "mistura", "patrimonio", "fiscal"],
                "resposta": "A separação patrimonial é um requisito legal rígido. O microempreendedor deve abrir uma conta bancária PJ exclusiva. Todas as vendas devem entrar nesta conta e todas as despesas da empresa devem sair dela. O dono do negócio deve estipular um Pró-labore fixo mensal para suas despesas particulares. Pagar despesas pessoais (mercado, contas residenciais) com o saldo da PJ gera confusão patrimonial e passivos fiscais graves junto à Receita Federal."
            },
            {
                "id": 203,
                "categoria": "Planejamento Orçamentário Pessoal",
                "pergunta": "Como funciona o direcionamento pela Regra Orçamentária dos 50/30/20?",
                "tags": ["regra 50/30/20", "planejamento", "orçamento", "pessoal", "gastos", "divisão", "renda", "poupança"],
                "resposta": "A metodologia dos 50/30/20 divide a renda líquida mensal do indivíduo de forma estratégica: 50% são alocados obrigatoriamente para Gastos Essenciais (moradia, transporte, alimentação básica, saúde); 30% são direcionados para Gastos Flexíveis ou Desejos (lazer, hobbies, entretenimento, viagens); e os 20% restantes devem ser aplicados estritamente no Colchão Financeiro (reserva de emergência, investimentos de longo prazo ou quitação de dívidas)."
            },
            {
                "id": 204,
                "categoria": "Análise de Risco de Crédito",
                "pergunta": "Quais os perigos inerentes à Antecipação de Recebíveis?",
                "tags": ["antecipação de recebíveis", "cartão de crédito", "taxa", "juros", "risco", "antecipar", "lucro", "banco"],
                "resposta": "A antecipação de recebíveis consome as margens de lucro futuras da empresa através de taxas de desconto abusivas aplicadas pelas credenciadoras de cartões e bancos. O risco sistêmico reside no desfalque do fluxo de caixa operacional dos meses subsequentes, gerando um ciclo vicioso de dependência financeira crônica. O microempreendedor passa a antecipar de forma contínua apenas para cobrir despesas correntes, destruindo o valor real do negócio."
            },
            {
                "id": 205,
                "categoria": "Planejamento Orçamentário Pessoal",
                "pergunta": "Como estruturar uma Reserva de Emergência de alta liquidez?",
                "tags": ["reserva de emergência", "colchão financeiro", "segurança", "poupar", "imprevistos", "liquidez", "selic", "cdi"],
                "resposta": "A reserva de emergência deve comportar o equivalente a 6 a 12 meses do custo de vida total do indivíduo ou empresa. O capital alocado deve priorizar a segurança absoluta e o resgate imediato (liquidez D+0). Os ativos recomendados pela governança financeira são: Tesouro Selic, CDBs de bancos sólidos que ofereçam liquidez diária com rendimento mínimo de 100% do CDI, ou fundos de investimento DI com taxa zero de administração."
            }
        ]

        for dados in dataset_bruto:
            self._documentos.append(
                DocumentoCorporativo(
                    id_documento=dados["id"],
                    categoria=dados["categoria"],
                    pergunta=dados["pergunta"],
                    tags=set(dados["tags"]),
                    resposta=dados["resposta"]
                )
            )
        logger.info(f"Base de conhecimento local indexada com sucesso. {len(self._documentos)} registros ativos.")

    def recuperar_contexto_por_relevancia(self, entrada_usuario: str) -> Tuple[str, float]:
        """
        Executa uma pesquisa ponderada de termos (Heuristic Search Query Broker).
        Mapeia palavras-chave e faz a interseção matemática de termos com as tags indexadas.
        """
        if not entrada_usuario or len(entrada_usuario.strip()) == 0:
            return "", 0.0

        termos_limpos: List[str] = [
            termo.strip().lower()
            for termo in entrada_usuario.lower().split()
            if len(termo.strip()) > 2
        ]
        
        melhor_documento: Optional[DocumentoCorporativo] = None
        maior_score: float = 0.0

        for doc in self._documentos:
            score_atual: float = 0.0
            for termo in termos_limpos:
                # Peso 5.0 para termos idênticos contidos na pergunta cadastrada
                if termo in doc.pergunta.lower():
                    score_atual += 5.0
                # Peso 3.0 para correspondência de tags estruturadas
                if termo in doc.tags:
                    score_atual += 3.0
                # Peso 1.0 para ocorrência pulverizada na resposta institucional
                if termo in doc.resposta.lower():
                    score_atual += 1.0

            # Penalização estrutural pelo comprimento da string para normalização (Heuristic Length Normalization)
            if score_atual > 0:
                score_atual = score_atual / (1.0 + (math.log(len(doc.resposta)) * 0.05))

            if score_atual > maior_score:
                maior_score = score_atual
                melhor_documento = doc

        # Nota de corte mínima de relevância (Threshold Guard)
        if melhor_documento and maior_score >= 1.5:
            contexto_formatado = (
                f"[Metadados Corporativos | Categoria: {melhor_documento.categoria} | ID: {melhor_documento.id_documento}]\n"
                f"Informação Factual: {melhor_documento.resposta}"
            )
            return contexto_formatado, maior_score

        return "", 0.0


# -----------------------------------------------------------------------------------------
# SIMULAÇÃO DE ORQUESTRAÇÃO DE LLM (GEMINI SDK MOCK ARCHITECTURE)
# -----------------------------------------------------------------------------------------
class GenerativeContentConfig:
    """Imita com fidelidade estrutural a classe types.GenerateContentConfig do SDK google-genai."""
    def __init__(self, system_instruction: str, temperature: float, max_output_tokens: int) -> None:
        self.system_instruction = system_instruction
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens


class CoreGenerativeEngine:
    """
    Simulador sênior em nível de compilador para chamadas do Gemini 2.5.
    Interpreta o payload gerado pelo RAG, processa as regras lógicas de sistema
    e impede respostas fora da base de dados local.
    """
    
    def __init__(self) -> None:
        pass

    def generate_content(self, model: str, contents: str, config: GenerativeContentConfig) -> Any:
        """
        Executa a emulação de tokenização e inferência de linguagem natural.
        Mantém o comportamento determinístico exigido por um ambiente financeiro de produção.
        """
        # Emulação de latência de barramento I/O e processamento de rede (650ms a 800ms)
        time.sleep(0.68)

        # Validação rígida do contexto do prompt injetado
        if "NENHUM CONTEXTO DISPONÍVEL NA BASE" in contents:
            return self._retornar_objeto_mock(
                "Desculpe, não possuo essa informação na minha base de dados para te ajudar com segurança. "
                "Deseja falar sobre capital de giro ou finanças pessoais?"
            )

        # Varredura do payload para extrair o dado textual factual
        linhas_payload = contents.split("\n")
        informacao_factual: str = ""
        categoria_analisada: str = "Classificação Geral"

        for linha in linhas_payload:
            if 'Informação Factual: ' in linha:
                informacao_factual = linha.replace("Informação Factual: ", "").strip()
            if "Categoria: " in linha:
                # Isolamento de metadados via parsing manual de strings
                segmentos = linha.split("|")
                for seg in segmentos:
                    if "Categoria: " in seg:
                        categoria_analisada = seg.replace("Categoria: ", "").strip().replace("]", "")

        if not informacao_factual:
            return self._retornar_objeto_mock(
                "Desculpe, não possuo essa informação na minha base de dados para te ajudar com segurança. "
                "Deseja falar sobre capital de giro ou finanças pessoais?"
            )

        # Construção da resposta final nos moldes da persona sênior solicitada
        resposta_final_texto = (
            f"### Consultoria Executiva — FinTech Advisor\n"
            f"*Setor Operacional: {categoria_analisada}*\n\n"
            f"Prezado(a) gestor(a), avaliei os parâmetros factuais contidos em nosso repositório corporativo "
            f"para fornecer um direcionamento seguro à sua consulta financeira. Siga as orientações descritas abaixo:\n\n"
            f"**Parecer Técnico:** {informacao_factual}\n\n"
            f"**Ação de Governança Recomendada:** Insira esses indicadores em seu plano de orçamento mensal "
            f"imediatamente. Evite desvios operacionais que possam comprometer a liquidez corrente e seu fluxo de caixa futuros."
        )

        return self._retornar_objeto_mock(resposta_final_texto)

    def _retornar_objeto_mock(self, texto_saida: str) -> Any:
        """Cria um objeto anônimo simulando a estrutura 'response.text' do SDK do Gemini."""
        class ResponseStructure:
            def __init__(self, text: str) -> None:
                self.text = text
        return ResponseStructure(texto_saida)


# -----------------------------------------------------------------------------------------
# SISTEMA DE TELEMETRIA, MÉTRICAS E AUDITORIA DE QUALIDADE (PASSO 5)
# -----------------------------------------------------------------------------------------
class ControladorMétricasEAuditoria:
    """
    Centraliza a coleta de dados de performance, calcula taxas de assertividade,
    audita respostas para evitar vazamento de dados ou alucinações e exibe painéis gerenciais.
    """
    
    def __init__(self) -> None:
        self._historico_eventos: List[RegistroTelemetria] = []
        self._contador_id: int = 1000

    def registrar_interacao(self, query: str, resposta: str, inicio: float, fim: float, com_contexto: bool) -> None:
        """Instancia um novo registro de telemetria no histórico operacional."""
        self._contador_id += 1
        
        frase_trava = "Desculpe, não possuo essa informação na minha base de dados"
        foi_bloqueio = frase_trava in resposta

        evento = RegistroTelemetria(
            id_evento=self._contador_id,
            timestamp_inicio=inicio,
            timestamp_fim=fim,
            query_usuario=query,
            resposta_sistema=resposta,
            contexto_encontrado=com_contexto,
            alucinacao_bloqueada=foi_bloqueio,
            score_relevancia=1.0 if (com_contexto and not foi_bloqueio) else 0.0
        )
        self._historico_eventos.append(evento)

    def gerar_relatorio_dashboard(self) -> None:
        """Renderiza no terminal um dashboard analítico sênior com todos os KPIs do Passo 5."""
        total_interacoes = len(self._historico_eventos)
        if total_interacoes == 0:
            print("\n📊 [MÉTRICAS] Erro operacional: Histórico de telemetria vazio. Execute interações primeiro.")
            return

        tempo_acumulado: float = 0.0
        bloqueios_seguranca: int = 0
        sucessos_fatores: int = 0

        for evento in self._historico_eventos:
            tempo_acumulado += evento.latencia_ms
            if evento.alucinacao_bloqueada:
                bloqueios_seguranca += 1
            if evento.contexto_encontrado and not evento.alucinacao_bloqueada:
                sucessos_fatores += 1

        latencia_media = tempo_acumulado / total_interacoes
        taxa_seguranca_efetiva = (bloqueios_seguranca / total_interacoes) * 100.0
        taxa_acerto_rag = (sucessos_fatores / total_interacoes) * 100.0

        print("\n" + "█" * 75)
        print("     SISTEMA DE TELEMETRIA E AUDITORIA DE QUALIDADE — PAINEL DE KPIs    ")
        print("     [MÉTRICAS EXIGIDAS NO PASSO 5 DO DESAFIO DO FRAMEWORK DIO]")
        print("█" * 75)
        print(f" ▪ Volume de Requisições Processadas:     {total_interacoes} chamadas.")
        print(f" ▪ Respostas Baseadas em Fatos Locais:    {sucessos_fatores} ocorrências.")
        print(f" ▪ Bloqueios Ativos de Alucinação (IA):   {bloqueios_seguranca} interceptações.")
        print(f" ▪ Latência Média de Resposta (SLA):      {latencia_media:.2f} ms")
        print(f" ▪ Índice de Assertividade RAG Local:     {taxa_acerto_rag:.1f}%")
        print(f" ▪ Taxa de Eficiência Defensiva (Gate):   {taxa_seguranca_efetiva:.1f}%")
        print("-" * 75)
        print(" Histórico Recente de Auditoria Sênior (Últimos 2 eventos):")
        for ev in self._historico_eventos[-2:]:
            status = "BLOCKED (SAFE)" if ev.alucinacao_bloqueada else "SUCCESS (FACTUAL)"
            print(f"   [ID: {ev.id_evento}] Entrada: '{ev.query_usuario[:25]}...' | Latência: {ev.latencia_ms:.1f}ms | Status: {status}")
        print("█" * 75 + "\n")


# -----------------------------------------------------------------------------------------
# EXIBIÇÃO DA ARQUITETURA E DOCUMENTAÇÃO INTEGRADA (PASSO 6 - PITCH & README TEMPLATE)
# -----------------------------------------------------------------------------------------
def exibir_documentacao_pitch_github() -> None:
    """Imprime a estrutura padrão ouro do README.md exigida para postagem no GitHub."""
    conteudo_readme = (
        "\n" + "=" * 75 + "\n"
        "📝 TEMPLATE OFICIAL PARA O README.md DO SEU REPOSITÓRIO GITHUB (PASSO 6)\n"
        "===========================================================================\n\n"
        "# Assistente de Saúde Financeira Pessoal e Microempreendedora (MEI)\n\n"
        "## 🛠️ 1. O Problema & O Pitch de Negócio\n"
        "Microempreendedores e pessoas físicas falham no gerenciamento de caixa devido à "
        "falta de conhecimento técnico imediato ou confusão patrimonial entre contas PF e PJ. "
        "Nossa solução resolve esse gargalo através de um assistente virtual inteligente corporativo "
        "que consome uma base de dados especializada local, respondendo com precisão e zero alucinação.\n\n"
        "## 🏗️ 2. Arquitetura do Sistema\n"
        "- **data/**: Contém a base de conhecimento indexada de alta densidade em formato estruturado.\n"
        "- **docs/**: Documentação das instruções de persona e restrições de segurança do sistema.\n"
        "- **src/**: Código-fonte em Python estruturado sob as diretrizes do Clean Code e SOLID.\n\n"
        "## 📊 3. Diferenciais Técnicos Sênior\n"
        "- **RAG Engine local**: Mecanismo de busca ponderada que evita o custo de embeddings externos.\n"
        "- **Proteção Anti-Alucinação**: Trava sintática na camada de modelo que impede respostas falsas.\n"
        "- **Telemetria de KPIs**: Monitoramento em tempo real de latência (ms) e cobertura de dados.\n"
        "\n" + "=" * 75 + "\n"
    )
    print(conteudo_readme)


# -----------------------------------------------------------------------------------------
# ORQUESTRADOR CENTRAL E ITERAÇÃO DA APLICAÇÃO (PASSO 4 - APPLICATION RUNTIME)
# -----------------------------------------------------------------------------------------
class CoreApplicationEngine:
    """Garante o ciclo de vida completo do software e o loop estável do terminal CLI."""
    
    def __init__(self) -> None:
        self.banco_conhecimento = RepositorioConhecimentoLocal()
        self.motor_ia = CoreGenerativeEngine()
        self.telemetria = ControladorMétricasEAuditoria()

    def run(self) -> None:
        """Ponto de entrada de execução da interface de linha de comando."""
        print("=" * 78)
        print("  FINTECH ADVISOR ENTERPRISE SYSTEM v3.0.0 — PLATAFORMA DE PRODUÇÃO OFFLINE  ")
        print("  DESAFIO DE PROJETO DIO — ISOLADO EM ECOSSISTEMA DE SEGURANÇA KALI LINUX   ")
        print("=" * 78)
        print("[SISTEMA] Banco de dados vetorial emulado carregado na memória ram.")
        print("[SISTEMA] Engenharia de prompt injetada na camada lógica do compilador.")
        print("[OPÇÕES BASH] Digite 'dashboard' para ver o Passo 5 | 'pitch' para ver o Passo 6.")
        print("[OPÇÕES BASH] Digite 'sair' para finalizar as operações de consultoria.")
        print("-" * 78)

        while True:
            try:
                pergunta_usuario: str = input("\n👤 FinTech_User [Digite sua consulta] > ").strip()
                if not pergunta_usuario:
                    continue

                if pergunta_usuario.lower() in ["sair", "exit", "quit", "clear"]:
                    print("\n[Operação Finalizada] Log de execução gravado. Bons negócios!")
                    break

                if pergunta_usuario.lower() in ["dashboard", "metricas", "kpi", "kpis"]:
                    self.telemetria.gerar_relatorio_dashboard()
                    continue

                if pergunta_usuario.lower() in ["pitch", "readme", "docs", "documentacao"]:
                    exibir_documentacao_pitch_github()
                    continue

                # Início do monitoramento de performance de alta resolução
                marca_tempo_inicio = time.perf_counter()

                print(" 🔍 [Passo 4 - RAG] Executando tokenização e varredura na base de conhecimento local...")
                contexto_recuperado, score = self.banco_conhecimento.recuperar_contexto_por_relevancia(pergunta_usuario)
                tem_contexto = len(contexto_recuperado) > 0

                print(" 🧠 [Passo 4 - LLM] Injetando System Instructions e invocando motor generativo...")
                
                # Configuração estrita de Hiperparâmetros
                configuracao_tokens = GenerativeContentConfig(
                    system_instruction=INSTRUCAO_SISTEMA_PERSONA,
                    temperature=0.0,
                    max_output_tokens=800
                )

                # Montagem estruturada do prompt composto (Injeção Contextual de Variáveis)
                prompt_composto = (
                    f"INSTRUÇÃO GERAL DE PERSONA:\n{configuracao_tokens.system_instruction}\n\n"
                    f"CONTEXTO FORNECIDO DA BASE LOCAL:\n{contexto_recuperado if tem_contexto else 'NENHUM CONTEXTO DISPONÍVEL NA BASE'}\n\n"
                    f"PERGUNTA DO USUÁRIO ENVIADA: {pergunta_usuario}\n\n"
                    f"Emita o relatório técnico factual:"
                )

                # Execução da chamada lógica na camada do modelo simulado
                objeto_resposta = self.motor_ia.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt_composto,
                    config=configuracao_tokens
                )

                marca_tempo_fim = time.perf_counter()
                
                # Salva os registros operacionais na telemetria interna para fins de auditoria
                self.telemetria.registrar_interacao(
                    query=pergunta_usuario,
                    resposta=objeto_resposta.text,
                    inicio=marca_tempo_inicio,
                    fim=marca_tempo_fim,
                    com_contexto=tem_contexto
                )

                # Renderização da resposta final estruturada
                print(f"\n🤖 Assistente Virtual:\n{objeto_resposta.text}")
                print("\n" + "—" * 65)

            except KeyboardInterrupt:
                print("\n\n[Sinal de Interrupção] Encerramento forçado detectado via console.")
                sys.exit(0)
            except Exception as falha_catastrofica:
                logger.error(f"Falha de execução não tratada capturada no orquestrador: {falha_catastrofica}")


# -----------------------------------------------------------------------------------------
# PONTO DE ENTRADA EXECUTÁVEL DO AMBIENTE CORPORATIVO
# -----------------------------------------------------------------------------------------
if __name__ == '__main__':
    engine = CoreApplicationEngine()
    engine.run()