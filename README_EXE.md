# PyTestConnection v{{VERSION}} - Avaliador de Qualidade de Internet

## Sobre o Programa
O PyTestConnection é uma ferramenta robusta e confiável desenvolvida em Python para medir e avaliar a qualidade da sua conexão de rede (Download, Upload, Ping, Jitter e perda de pacotes). A aplicação faz uso de múltiplos motores de teste garantindo um diagnóstico altamente acurado.

**Autor:** Felix Neto  
**Repositório Github:** [https://github.com/felixfln/PyTestConnection](https://github.com/felixfln/PyTestConnection)

---

## Como Executar
Basta dar um **duplo clique** no arquivo `PyTestConnection.exe`. 
O programa é portátil e de fácil utilização. Os dados de medição histórica dos seus testes são mantidos organizados em um arquivo binário codificado localizado em `data/data.pconn`, e cada execução possui seus logs técnicos armazenados de forma limpa na subpasta `logs`.
- Disponível apenas para `Windows`, testado na versão 11 (25H2).

> **⚠️ Dica de Portabilidade:** 
> Para utilizar ou mover a aplicação sem perder seu histórico, não mova apenas o `.exe`. Mova a pasta inteira. Mais especificamente, mantenha o `.exe` acompanhado das pastas `data` e `logs` geradas.

---

## O Que a Aplicação Mostra na Tela?

- **Medidores e Gráficos:** Informações centralizadas informando os dados obtidos de Download, Upload, Ping, Jitter e perda de pacotes. Há um gráfico preenchido dinamicamente demonstrando o panorama.
- **Painel Resumo (Avaliação de 0-100):** É gerada uma nota de qualidade categorizando a sua rede (Excelente, Muito Boa, Estável, Limitada ou Instável).
- **Semáforo de Adequação:** Logo ao lado direito, o programa lhe entrega um veredito real usando luzes de semáforo (Verde, Amarelo e Vermelho) para analisar se sua rede suportará: Videochamadas, Navegação Básica, Transferência de Arquivos, Jogos Online e Streaming.

---

## Funcionalidades Principais

- **🚀 TESTE RÁPIDO:** Botão no topo da tela para realizar um diagnóstico instantâneo (com duração de alguns segundos) passando por apenas 1 iteração e focando no primeiro provedor que responder no momento. Ideal para validar se "tem internet".
- **🚀🚀🚀 TESTE PROFUNDO:** Foca em precisão estrita e na tolerância a falhas. Executa 5 iterações de rotina consecutivas sobre todos os servidores disponíveis utilizando a técnica estatística de "Max of Medians". Ela remove anomalias na coleta para trazer exatamente a *verdadeira capacidade e estabilidade da sua banda*.
- **🗑️ LIMPAR:** Ícone de "lixeira" localizado no canto superior direito para resetar facilmente o gráfico e os indicadores exibidos na interface de volta para os estados zerados/padrões, preparando o cenário para a próxima medição de modo limpo.
- **📖 VER LOGS:** Botão integrado na parte superior esquerda para acesso imediato. Ao clicar, a pasta padrão de execução é mapeada dinamicamente, e o Explorador de Arquivos do Windows abre para exibir a rastreabilidade contendo arquivos `.log` de tudo que houve sessão por sessão.
- **⏱️ AGENDAMENTOS MÚLTIPLOS:** Clique no ícone de relógio no limite superior da barra verde (ou botão "Agendamento Inativo") para configurar a sua aplicação para a execução de verificação silente, de forma repetitiva e no período que agendar (ex: a cada "X" minutos).
