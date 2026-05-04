Aqui está uma proposta de README.md profissional e detalhada, estruturada para que qualquer pessoa (ou analista de suporte) entenda a finalidade técnica do seu sistema e como configurá-lo corretamente.

🕹️ Retro-Pix Vending System
O Retro-Pix Vending é uma solução de automação em Python desenvolvida para integrar pagamentos via Pix (Mercado Pago) em sistemas de máquinas de jogos (Arcades/Vending Machines) baseados em Linux.

Este software transforma créditos digitais em ações físicas ou lógicas no sistema, permitindo que o usuário adquira fichas/créditos em tempo real através de um QR Code dinâmico exibido na tela.

🚀 Funcionalidades
Integração Nativa com Mercado Pago: Utiliza o SDK oficial para gerar pagamentos e monitorar o status de aprovação.

Interface Adaptativa: Desenvolvida com CustomTkinter, a janela do QR Code pode ser movida e redimensionada via mouse/touch.

Modo de Venda em Jogo: O sistema detecta se há um jogo ativo e pode forçar a exibição do QR Code sobre a tela.

Controle de Hardware: Após a aprovação do pagamento, o script executa rotinas para somar créditos em arquivos de sistema e emitir alertas sonoros.

Vigia de Segurança: Monitoramento constante da conexão com a internet e das configurações do sistema.

🛠️ Configuração e Instalação
1. Requisitos de Sistema
O script foi projetado para rodar em ambientes Linux (como Batocera ou sistemas customizados).

Python 3.14+.

Bibliotecas: customtkinter, mercadopago, qrcode, Pillow.

2. Onde colocar o Access Token?
O sistema gerencia o token de segurança de forma automatizada para evitar exposição direta em arquivos de configuração comuns.

Arquivo de Destino: O token final é armazenado em:

/usr/lib/liblinuxenv.so.

Processo de Importação:

Você pode inserir sua chave no arquivo batocera.conf sob a tag PIX_KEY="...". O script irá detectar essa chave, movê-la para o local seguro de forma criptografada/mascarada e limpar a chave original do arquivo de configuração para sua segurança.

3. Configurações no batocera.conf
Adicione as seguintes linhas ao seu arquivo de configuração para controlar o comportamento do Vending Machine:

Ini, TOML

PIX_ON = "true"                 # Habilita ou desabilita o sistema Pix
PIX_VALOR = "2,00"              # Valor a ser cobrado por transação
PIX_QUANTIDADE_CRÈDITOS = "2"   # Quantidade de fichas entregues por pagamento
TEMPO_MENU_SEGUNDOS = "5"       # Delay para exibição do QR Code no menu
PIX_KEY = "SEU_ACCESS_TOKEN"    # Seu Access Token do Mercado Pago
🖥️ Como Usar
Inicialização: Execute o script integração.py.

Geração do QR Code: O sistema verificará a conexão. Se estiver online e configurado, o QR Code aparecerá automaticamente após o tempo definido.

Pagamento: O cliente escaneia o código e paga via App do banco.

Liberação: Assim que o Mercado Pago aprova, o script:

Soma os créditos no arquivo contador.txt.

Reproduz o som de "moedas" (coins.mp3).

Reinicia o ciclo para a próxima venda.

⚠️ Nota para Desenvolvedores (Debugging)
Durante a fase de testes, o script pode gerar múltiplos QR Codes e cancelá-los automaticamente se a janela for fechada ou o sistema reiniciado. Isso faz parte da rotina de validação de timeouts e handshake da API.

Desenvolvido por: Jeverson Dias da Silva (Jever)

Projeto: JC Games Clássicos | Pandora Linux Patch
