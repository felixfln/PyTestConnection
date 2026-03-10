# 🌐 PyTestConnection - Medidor de Qualidade de Internet

O **PyTestConnection** é uma ferramenta robusta desenvolvida em Python 3.14 para medir e avaliar a qualidade da sua conexão de rede. Focado em precisão e resiliência, o sistema utiliza múltiplos motores de teste com tolerância nativa a falhas para garantir diagnósticos confiáveis.

---

## ✨ Funcionalidades Principais

- **🚀 Teste Rápido vs Profundo**: Escolha entre uma medição instantânea (1 iteração no primeiro motor disponível) ou uma medição profunda (5 iterações por motor). O teste profundo utiliza a metodologia **"Max of Medians"** — calcula a mediana isolada de cada motor e seleciona a melhor rota estável, refletindo a verdadeira capacidade da conexão.
- **☁️ Múltiplos Motores de Teste**: Integração com *Speedtest (Ookla)* e *Cloudflare Edge CDN*. Tolerância a falhas nativa: se um motor falhar ou estiver indisponível, o sistema prossegue com os que sobrarem automaticamente.
- **📐 Metodologia Estatística (Max of Medians)**:
  - **Download/Upload**: Mediana por motor → `max()` entre as medianas (capacidade máxima estável).
  - **Ping/Jitter**: Mediana por motor → `min()` entre as medianas (melhor latência estável).
  - Valores zerados (falhas de medição) são descartados automaticamente em todos os cálculos.
- **⏱️ Agendamento Autônomo**: Configure testes automáticos a cada X minutos ou horas. A aplicação lida com conflitos de operação (GUI/testes simultâneos) graciosamente.
- **📊 Avaliação Premium (0-100)**: Pontuação granular com status qualitativo: EXCELENTE, MUITO BOA, ESTÁVEL, LIMITADA ou INSTÁVEL.
- **🚥 Semáforo de Adequação**: Sistema de 3 níveis (🟢 Verde, 🟡 Amarelo, 🔴 Vermelho) para cenários como Videochamadas, Jogos Online, Streaming 4K, etc.
- **📑 Histórico e Logs**: Medições armazenadas em `data/data.pconn` (formato obfuscado para integridade) e logs por sessão em `logs/` (formato `.log` legível).
- **🛡️ Tolerância e Portabilidade**: Toda a aplicação é resiliente. O banco de dados `.pconn` utiliza codificação Base64 para evitar edições manuais acidentais, mas mantém portabilidade total entre máquinas.
- **🔍 Auditoria Facilitada**: Botão **"VER LOGS"** integrado para abrir e visualizar qualquer arquivo de log diretamente no editor padrão do Windows.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.14** — Linguagem base.
- **Tkinter** — Interface gráfica nativa com threading assíncrono.
- **Pillow** — Tratamento dinâmico de ícones e imagens.
- **PyInstaller** — Geração de executáveis Windows portáteis e dinâmicos.
- **Speedtest API & Cloudflare Edge** — Duplo motor de medição e redundância.
- **ICMP Ping** — Medição real de Jitter (variação entre latências consecutivas).

---

## 🚀 Como Começar

### Pré-requisitos
- **Python 3.14** instalado e adicionado ao PATH.
- **Acesso à Internet** para realizar os testes.

### 📥 Passo 1: Instalação
```bash
pip install -r docs/requirements.txt
```

### 🖥️ Passo 2: Execução
```bash
python -m src.main
```
> **Nota**: O `-m` garante que todos os módulos internos sejam carregados corretamente.

**Como usar na interface:**
1. Clique em **"TESTE RÁPIDO"** ou **"TESTE PROFUNDO"**.
2. Acompanhe a **barra de progresso** e os valores atualizando em tempo real.
3. Ao finalizar, veja sua **pontuação (0-100)** e os **LEDs coloridos** de adequação.
4. Para testes automáticos, clique em **"AGENDAMENTO INATIVO"** e configure o intervalo.

### 📦 Passo 3: Gerando o Executável (.exe)
```bash
python build_exe.py
```
O arquivo gerado estará em `dist/PyTestConnection.exe`.

> ⚠️ **IMPORTANTE: Portabilidade e Requisitos do Executável**
>
> 1. **Não requer instalação do Python**: O executável é autossuficiente. O sistema detecta automaticamente o diretório atual para salvar dados em `data/` e logs em `logs/`.
>
> 2. **Portabilidade**: Basta enviar o `.exe` acompanhado das pastas **`data/`**, **`config/`** e **`src/assets/`** (para funcionamento dos ícones).

---

## 📂 Estrutura do Projeto

```text
PyTestConnection/
├── config/
│   └── metrics_config.json   # Thresholds de pontuação e semáforo
├── data/
│   └── data.pconn            # Histórico de medições (Obfuscado)
├── docs/
│   └── requirements.txt      # Dependências Python (Inclui Pillow)
├── logs/                     # Logs por sessão (app_YYYYMMDD_HHMMSS.log)
├── src/
│   ├── assets/               # Ícones da aplicação (.ico)
│   ├── constants.py          # Cores, versão, caminhos dinâmicos
│   ├── main.py               # Ponto de entrada (single instance guard)
│   ├── engines/
│   │   ├── base.py           # Interface abstrata dos motores
│   │   ├── manager.py        # Orquestrador (Max of Medians)
│   │   ├── speedtest_provider.py   # Motor Speedtest (Ookla)
│   │   └── cloudflare_provider.py  # Motor Cloudflare Edge
│   ├── ui/
│   │   ├── app.py            # Interface principal (Tkinter)
│   │   └── components/
│   │       └── graph.py      # Gráfico dinâmico de velocidade
│   └── utils/
│       ├── calculator.py     # Pontuação 0-100 e semáforo
│       ├── logger.py         # Logger singleton com caminho dinâmico
│       ├── network.py        # Medição de Jitter (ICMP)
│       └── persistence.py    # Motor de migração e persistência .pconn
└── build_exe.py              # Script de build do PyInstaller
```

---

## ⚙️ Configurações Customizadas

Calibre o rigor das avaliações em `config/metrics_config.json`:
- Limites (thresholds) para a pontuação 0-100.
- Margens de tolerância para o nível Amarelo do semáforo.
- Requisitos mínimos de Download/Upload/Ping para cada cenário de uso.

---

## 📝 Licença
Desenvolvido como ferramenta de código aberto para medição de qualidade de rede.
Por Felix Neto
