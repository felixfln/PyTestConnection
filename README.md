# 🌐 PyTestConnection - Medidor de Qualidade de Internet

O **PyTestConnection** é uma ferramenta robusta desenvolvida em Python 3.14 para medir e avaliar a qualidade da sua conexão de rede. Focado em precisão e resiliência, o sistema utiliza múltiplos motores de teste para garantir que você sempre tenha um diagnóstico confiável.

---

## ✨ Funcionalidades Principais

- **🚀 Teste Rápido vs Profundo**: Escolha entre uma varredura instantânea ou uma medição profunda. O teste profundo roda múltiplas baterias (3x a 5x vezes) em diversos motores e apura a verdadeira conectividade ignorando oscilações através de cálculos de *Mediana*.
- **☁️ Múltiplos Motores de Teste**: Integração robusta com *Speedtest API* e um motor proprietário super leve baseado na CDN da *Cloudflare* (Ping Direto e Transferência Bruta). Tolerância a falhas nativa: se um provedor cair, o sistema assume os que sobrarem automaticamente.
- **⏱️ Agendamento Autônomo (Scheduling)**: Configure o sistema para testar sua internet sozinho a cada "X" horas ou minutos. A aplicação lida com conflitos de operação gráfica (GUI) graciosamente em tempo real sem interrupções.
- **📊 Avaliação Premium (0-100)**: Algoritmo avançado que atribui uma pontuação granular e um status qualitativo (EXCELENTE, MUITO BOA, ESTÁVEL, LIMITADA ou INSTÁVEL).
- **🚥 Semáforo de Capacidade**: Sistema de 3 níveis (Verde, Amarelo, Vermelho) para indicar a adequação da rede para Videochamadas, Jogos Online, etc.
- **📑 Histórico Interativo e Logs**: Explore medições passadas na interface ou audite o sistema pelos logs por sessão do Python em `logs/`.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.14**: Linguagem base.
- **Tkinter**: Interface gráfica nativa e assíncrona.
- **PyInstaller**: Para automação e geração de executáveis Windows.
- **Speedtest API & Cloudflare Edge**: Duplo motor de medição e redundância.
- **ICMP Ping**: Medição real de Jitter através de pacotes sequenciais.

---

## 🚀 Como Começar

### Pré-requisitos
- **Python 3.14**: Certifique-se de que o Python está instalado e adicionado ao seu PATH.
- **Acesso à Internet**: Necessário para realizar os testes de velocidade.

### 📥 Passo 1: Instalação
1. Abra o terminal (PowerShell ou Prompt de Comando) na pasta raiz do projeto.
2. Instale as dependências:
   ```bash
   pip install -r docs/requirements.txt
   ```

### 🖥️ Passo 2: Execução via Terminal
Para rodar o sistema diretamente via código (estando na raiz do projeto):
```bash
python -m src.main
```
> **Nota**: O uso do `-m` garante que todos os módulos internos e o arquivo de versão sejam carregados corretamente.

**Como usar na interface:**
1. Clique em **"TESTE RÁPIDO"** ou **"TESTE PROFUNDO"**.
2. Acompanhe a **barra de progresso** preenchendo as etapas de cada motor.
3. Ao finalizar, veja sua **pontuação (0-100)** e os **LEDs coloridos** de adequação.
4. Para testes automatizados, configure a janela em **"AGENDAMENTO INATIVO"** e ative-a.

### 📦 Passo 3: Criando o Executável (.exe)
Para gerar o executável Windows:
1. No terminal, execute:
   ```bash
   python build_exe.py
   ```
2. O arquivo gerado estará em `dist/PyTestConnection.exe`.

---

## 📂 Estrutura do Projeto

```text
PyTestConnection/
├── config/
│   └── metrics_config.json   # Rigor das avaliações e semáforo
├── data/
│   └── data.txt             # Histórico de medições
├── logs/                    # Logs de execução (app_data_hora.log)
├── src/
│   ├── engines/             # Lógica de medição e Jitter
│   ├── ui/                  # Interface e componentes gráficos
│   └── utils/               # Logs, persistência e cálculos
└── build_exe.py             # Script de automação do PyInstaller
```

---

## ⚙️ Configurações Customizadas

Você pode calibrar o rigor do sistema em `config/metrics_config.json`. Lá você altera:
- Limites para a pontuação 0-100.
- Margens de tolerância para a cor Amarela do semáforo.
- Requisitos mínimos de Download/Ping para cada cenário.

---

## 📝 Licença
Desenvolvido como ferramenta de código aberto para medição de qualidade de rede.
Por Felix Neto
