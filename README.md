# 🌐 PyTestConnection - Medidor de Qualidade de Internet

O **PyTestConnection** é uma ferramenta robusta desenvolvida em Python 3.14 para medir e avaliar a qualidade da sua conexão de rede. Focado em precisão e resiliência, o sistema utiliza múltiplos motores de teste para garantir que você sempre tenha um diagnóstico confiável.

---

## ✨ Funcionalidades Principais

- **🚀 Medição em Tempo Real**: Visualize a velocidade de download e upload enquanto o teste acontece através de um gráfico dinâmico.
- **🛡️ Alta Resiliência**: Sistema de failover inteligente que alterna entre diferentes provedores (Speedtest.net e PySpeedtest) caso um deles falhe.
- **📊 Avaliação de Qualidade**: Algoritmo que atribui uma nota de 0 a 10 baseada em padrões de mercado para latência, velocidade e jitter.
- **✅ Checklist de Cenários**: Saiba instantaneamente se sua internet é adequada para:
  - Redes Sociais
  - Streaming HD e 4K
  - Videoconferências
  - Jogos Online (Baixa Latência)
  - Downloads Pesados
- **📑 Histórico Persistente**: Acompanhe o desempenho da sua rede ao longo do tempo com uma lista organizada e persistente.
- **⚙️ Altamente Configurável**: Ajuste os limites de qualidade e requisitos de cenários através de um arquivo JSON simples.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.14**: Linguagem base.
- **Tkinter**: Interface gráfica nativa e leve.
- **PyInstaller**: Para geração de executáveis Windows.
- **Speedtest.net API**: Motor principal de medição.
- **PySpeedtest**: Motor alternativo de reserva.

---

---

## 🚀 Como Começar

### Pré-requisitos
- **Python 3.14**: Certifique-se de que o Python está instalado e adicionado ao seu PATH.
- **Acesso à Internet**: Necessário para realizar os testes de velocidade e baixar as bibliotecas.

### 📥 Passo 1: Instalação
1. Abra o terminal (PowerShell ou Prompt de Comando) na pasta raiz do projeto.
2. Crie e ative um ambiente virtual (opcional, mas recomendado):
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Instale as dependências necessárias:
   ```bash
   pip install -r docs/requirements.txt
   ```

### 🖥️ Passo 2: Utilização da Aplicação
Para rodar o sistema diretamente via código:
```bash
python src/main.py
```
**Como usar na interface:**
1. Clique em **"MEDIR AGORA"** para iniciar o teste.
2. Acompanhe o **gráfico dinâmico** e as métricas em tempo real.
3. Ao finalizar, veja sua **nota (0-10)** e o checklist de **adequação de uso**.
4. O histórico será atualizado automaticamente na tabela inferior.
5. Use o botão **"LIMPAR REGISTROS"** para resetar o histórico de medições.

### 📦 Passo 3: Criando o Executável (.exe)
Se você deseja distribuir o programa para outras máquinas Windows sem a necessidade de instalar o Python:
1. No terminal, execute:
   ```bash
   python build_exe.py
   ```
2. Aguarde a finalização do processo.
3. Vá até a pasta `dist/` recém-criada.
4. Lá você encontrará o arquivo `PyTestConnection.exe`. 
   - **Dica**: Você pode mover este arquivo para qualquer lugar e executá-lo. Ele já levará consigo as configurações padrão necessárias.

---

## 📂 Estrutura do Projeto

```text
PyTestConnection/
├── config/
│   └── metrics_config.json   # Regras de negócio e limites de nota
├── data/
│   └── data.txt             # Histórico de medições
├── docs/
│   └── requirements.txt     # Dependências do projeto
├── src/
│   ├── engines/             # Lógica dos motores de medição (Adapter Pattern)
│   ├── ui/                  # Componentes Tkinter e janelas
│   └── utils/               # Persistência e cálculos matemáticos
├── build_exe.py             # Script de automação do PyInstaller
└── README.md                # Este documento
```

---

## ⚙️ Configurações Customizadas

Você pode alterar como as notas são calculadas editando o arquivo `config/metrics_config.json`. Lá você pode definir:
- Faixas de velocidade para cada nota.
- Latência máxima para cada nível de qualidade.
- Requisitos mínimos de cada cenário de uso.

---

## 📝 Licença
Desenvolvido como ferramenta de código aberto para medição de qualidade de rede.
