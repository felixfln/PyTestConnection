quero uma aplicação completa, mas com um objetivo simples: Medir a qualidade da internet utilizada.

1) A aplicação deve ser escrita em Python 3.14, deve utilizar um arquivo chamado ./data/data.txt, para salvar os registros.

2) O objetivo é avaliar a qualidade da internet utilizada através de medições técnicas, expondo os resultados em uma interface intuitiva usando Tkinter.

3) Precisa criar métricas de avaliação da internet para atribuir uma nota de qualidade de 0 a 10 (inteiros). 
   3.1) As métricas devem considerar: Velocidade (Download/Upload), Ping e Jitter.
   3.2) Os parâmetros e limites de cada nota devem ser armazenados em um arquivo de configuração (`config/metrics_config.json`) para fácil ajuste.

4) A interface (UI) deve ser dividida em 3 partes principais:
   4.1) Painel principal: Exibição dos resultados da medição atual e nota de qualidade.
   4.2) Botões de Ação: Medir e Limpar Histórico.
   4.3) Lista de registros: Histórico de medições anteriores em ordem decrescente.

5) Informações obrigatórias por medição:
   5.1) Velocidade (Download/Upload);
   5.2) Latência (Ping e Jitter);
   5.3) Servidor e IP da conexão;
   5.4) Interface/ISP (Nome da conexão);
   5.5) Data e hora da medição.

6) O painel de resultados deve exibir um gráfico de linha dinâmico em tempo real durante o processo de medição, estabilizando na média ao final.

7) Checklist de Adequação: O sistema deve informar se a conexão atende aos requisitos para:
   7.1) Redes Sociais, Streaming HD, Vídeo Conferências, Jogos Online, 4K (Ultra HD) e Downloads Pesados.
   7.2) A avaliação de cada item deve ser baseada em múltiplos parâmetros (ex: Ping baixo para jogos, alta velocidade para 4K), conforme definido no arquivo de configuração.

8) Resiliência e Failover (Refinamento):
   8.1) O sistema deve gerenciar múltiplos motores de medição (ex: Speedtest e PySpeedtest).
   8.2) Em caso de falha em um motor, deve alternar automaticamente para o próximo disponível.
   8.3) Se todos os serviços falharem sem problemas de internet local, o usuário deve ser notificado sobre a indisponibilidade dos serviços externos.

9) O sistema deve ser tolerante a falhas (Firewall, VPN, Ausência de Internet), exibindo mensagens tratadas e claras em vez de exceções técnicas.

10) Práticas de Desenvolvimento: Seguir princípios de Clean Code, Separação de Responsabilidades e manter o código legível para manutenções futuras.

11) Persistência: 
    11.1) Salvar dados em `./data/data.txt` usando o separador `|`.
    11.2) Utilizar identificadores numéricos ou booleanos no arquivo para representar estados (ex: 1 para adequado, 0 para não adequado).
    11.3) A lista na interface deve carregar esses dados e interpretá-los para o usuário.

12) A lista de histórico deve possuir rolagem vertical e horizontal para suportar grandes volumes de dados.

13) Empacotamento e Entrega:
    13.1) O sistema deve incluir um script (`build_exe.py`) para gerar um executável Windows standalone na pasta `./dist`.
    13.2) As dependências devem estar documentadas em `./docs/requirements.txt`.
    13.3) O projeto deve ser entregue pronto para uso, com estrutura de diretórios organizada.

    13.6) Teste se todas as funcionalidades implementadas estão funcionando corretamente.
    13.7) **Garantia de Instância Única**: A aplicação deve garantir que apenas uma instância seja executada por vez. Se uma nova for aberta, a anterior deve ser encerrada automaticamente.