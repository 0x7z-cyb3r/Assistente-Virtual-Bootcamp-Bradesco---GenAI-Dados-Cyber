# FinTech Advisor Ecosystem — Inteligência Artificial Operacional 🚀

Módulo avançado de arquitetura e orquestração de Inteligência Artificial Generativa com sistema de RAG (Retrieval-Augmented Generation) integrado. O ecossistema foi projetado para atuar de forma 100% offline e resiliente em ambientes Linux, focado em segurança de dados corporativos e microfinanças.

Desenvolvido para atender aos requisitos operacionais e de avaliação do framework de projetos do Bootcamp.

---

## 🏗️ 1. Arquitetura Modular do Repositório
O projeto está estruturado de forma desacoplada para garantir manutenibilidade e isolamento de escopo:
- **`data/`**: Repositório indexado de alta densidade simulando um banco de dados vetorial baseado em chaves e tags.
- **`docs/`**: Documentação formal de engenharia de prompt contendo as diretrizes de persona e restrições de comportamento da IA.
- **`src/`**: Código-fonte core em Python corporativo escrito sob as diretrizes de Clean Code e SOLID.

---

## 🛠️ 2. O Problema & O Pitch de Negócio (Passo 6)
O descontrole financeiro e a mistura patrimonial entre contas físicas (PF) e jurídicas (PJ) representam os maiores causadores de mortalidade de microempresas (MEI) no mercado nacional. 

O **FinTech Advisor** mitiga essa dor de negócio ao entregar respostas factuais rápidas com base em governança de mercado real. Atuando como um consultor sênior de bolso acessível 24/7, a solução elimina a necessidade de consultorias físicas caras para pequenos empreendedores, viabilizando previsibilidade financeira desde as primeiras etapas do negócio.

---

## 🧠 3. Engenharia de Prompt & Segurança (Passo 1 & 3)
A camada de inteligência utiliza as diretrizes de **System Instructions** injetadas diretamente na camada lógica de inferência:
- **Técnica Chain-of-Thought (CoT):** Obriga o motor a cruzar os metadados antes de estruturar o relatório final.
- **Trava Estrita Anti-Alucinação:** Caso a dúvida do usuário não possua respaldo na base local, o robô barra qualquer resposta inventada e dispara o protocolo padrão de segurança.

---

## 📊 4. Telemetria e Dashboard de KPIs (Passo 5)
O sistema conta com um subsistema embutido de auditoria que monitora a performance da IA em tempo real. Ao digitar `dashboard` no terminal, o operador tem acesso instantâneo a:
- **SLA de Latência:** Tempo exato de resposta medido em milissegundos (ms).
- **Métricas de Cobertura:** Quantidade de buscas que acionaram o banco local de dados.
- **Índice de Eficiência Defensiva:** Gráfico e contagem de quantas alucinações foram bloqueadas ativamente pelo robô.

---

## 🚀 5. Como Executar o Ecossistema
1. Certifique-se de estar com o ambiente virtual ativo:
   ```bash
   source .venv/bin/activate
   ```
2. Inicialize o orquestrador principal chamando o módulo:
   ```bash
   python3 -m src.app_enterprise
   ```
