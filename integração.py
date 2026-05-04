#!/usr/bin/python3.14

import os
import subprocess
import customtkinter as ctk
import mercadopago
import qrcode
import socket
import re
from PIL import Image

ctk.set_appearance_mode("dark")

class RetroVending(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()

        # Caminhos
        self.path_token = "/usr/lib/liblinuxenv.so"
        self.path_conf = "/userdata/system/batocera.conf"
        self.path_base = "/userdata/system/.dev"
        self.path_som = os.path.join(self.path_base, "efeitos_sonoros/coins.mp3")
        self.path_tempo_jogo = os.path.join(self.path_base, "tempo_jogo.txt")
        self.path_coin = os.path.join(self.path_base, "coin")
        self.path_qr_force = os.path.join(self.path_base, "QR")
        
        self.path_pos_normal = os.path.join(self.path_base, "posicao_janela.txt")
        self.path_pos_jogo = os.path.join(self.path_base, "posicao_janela_jogo.txt")

        # Estado
        self.qr_size = 250
        self.valor_pix = 0.0
        self.creditos_pix = 0
        self.pix_habilitado = False
        self.pix_atual = ""
        self.gerando_agora = False
        self.online = False
        self.modo_venda_em_jogo = None
        self.tempo_menu = 5

        # 🔥 TOKEN CACHE
        token = self.carregar_token_customizado()
        self.token_atual_cache = token
        self.sdk = mercadopago.SDK(token)

        # Janela
        self.overrideredirect(True)
        self.configure(fg_color="black")

        # Labels
        self.lbl_valor = ctk.CTkLabel(self, text="", text_color="white", fg_color="black", font=("Arial", 16, "bold"))
        self.lbl_valor.pack(side="top", fill="x", pady=(5, 2))

        self.qr_display = ctk.CTkLabel(self, text="", fg_color="black")
        self.qr_display.pack(side="top", expand=True, fill="both")

        self.lbl_fichas = ctk.CTkLabel(self, text="", text_color="white", fg_color="black", font=("Arial", 14, "bold"))
        self.lbl_fichas.pack(side="bottom", fill="x", pady=(2, 5))

        # Binds
        for widget in [self, self.lbl_valor, self.qr_display, self.lbl_fichas]:
            widget.bind("<ButtonPress-1>", self.iniciar_arrasto)
            widget.bind("<B1-Motion>", self.movimentar_janela)
            widget.bind("<ButtonRelease-1>", self.salvar_configuracoes_janela)

        self.qr_display.bind("<Button-4>", self.redimensionar)
        self.qr_display.bind("<Button-5>", self.redimensionar)

        self.vigia_de_seguranca()

    # 🔥 NOVO (PIX_KEY → TOKEN)
    def processar_pix_key(self):
        try:
            with open(self.path_conf, 'r') as f:
                linhas = f.readlines()

            pix_key = None
            novas_linhas = []
            encontrou = False

            for linha in linhas:
                if linha.strip().startswith("PIX_KEY"):
                    match = re.search(r'PIX_KEY\s*=\s*"(.*?)"', linha)
                    if match:
                        pix_key = match.group(1)

                    novas_linhas.append('PIX_KEY= ""\n')
                    encontrou = True
                    continue

                novas_linhas.append(linha)

            if not encontrou:
                resultado = []
                inserido = False

                for linha in novas_linhas:
                    resultado.append(linha)

                    if linha.strip().startswith("PIX_ON") and not inserido:
                        resultado.append('PIX_KEY= ""\n')
                        inserido = True

                novas_linhas = resultado

            with open(self.path_conf, 'w') as f:
                f.writelines(novas_linhas)

            if pix_key:
                novo_token = f"MP_ACCESS_TOKEN = {pix_key}\n"

                antigo = ""
                if os.path.exists(self.path_token):
                    with open(self.path_token, "r") as f:
                        antigo = f.read()

                if novo_token != antigo:
                    with open(self.path_token, "w") as f:
                        f.write(novo_token)

                    subprocess.Popen(["batocera-save-overlay"])

        except:
            pass

    def verificar_token(self):
        novo = self.carregar_token_customizado()
        if novo != self.token_atual_cache:
            self.token_atual_cache = novo
            self.sdk = mercadopago.SDK(novo)

    # 🔥 CONTADOR (INALTERADO)
    def somar_creditos_arquivo(self, quantidade):
        caminhos = [
            os.path.join(self.path_base, "contador.txt"),
            os.path.join(self.path_base, ".contador.txt")
        ]

        for caminho in caminhos:
            try:
                valor = 0
                if os.path.exists(caminho):
                    with open(caminho, "r") as f:
                        c = f.read().strip()
                        if c.isdigit():
                            valor = int(c)

                novo = valor + quantidade

                tmp = caminho + ".tmp"
                with open(tmp, "w") as f:
                    f.write(str(novo))

                os.replace(tmp, caminho)

            except:
                pass

    # 🔥 MANTIDO ORIGINAL
    def ajustar_geometria(self, x, y):
        altura_total = self.qr_size + 60
        self.geometry(f"{self.qr_size}x{altura_total}+{x}+{y}")

    def carregar_token_customizado(self):
        if os.path.exists(self.path_token):
            try:
                with open(self.path_token, "r") as f:
                    content = f.read().strip()
                    return content.split("=")[1].strip().replace('"', '').replace("'", "") if "=" in content else content
            except:
                pass
        return ""

    def obter_configuracoes_pix(self):
        padroes = {"PIX_VALOR": "2,00", "PIX_QUANTIDADE_CRÈDITOS": "2", "TEMPO_MENU_SEGUNDOS": "5", "PIX_ON": "true"}
        valores = {}
        if os.path.exists(self.path_conf):
            with open(self.path_conf, "r") as f:
                conteudo = f.read()
                for c in padroes:
                    match = re.search(rf"^{c}\s*=\s*([\w,\.]+)", conteudo, re.M)
                    valores[c] = match.group(1).strip().lower() if match else padroes[c].lower()
        novo_v = float(valores["PIX_VALOR"].replace(",", "."))
        novo_c = int(valores["PIX_QUANTIDADE_CRÈDITOS"])
        novo_on = (valores["PIX_ON"] == "true")
        if (novo_v != self.valor_pix or novo_c != self.creditos_pix or novo_on != self.pix_habilitado):
            if self.valor_pix != 0.0:
                self.pix_atual = ""
                self.gerando_agora = False
            self.valor_pix = novo_v
            self.creditos_pix = novo_c
            self.pix_habilitado = novo_on
            self.tempo_menu = int(valores["TEMPO_MENU_SEGUNDOS"])
            self.atualizar_status_visual()

    def vigia_de_seguranca(self):
        self.obter_configuracoes_pix()

        status_net = self.teste_real_internet()
        jogo_ativo = os.path.exists(self.path_tempo_jogo) or os.path.exists(self.path_coin)
        forcar_qr = os.path.exists(self.path_qr_force)

        novo_modo = True if (jogo_ativo and forcar_qr) else False

        if novo_modo != self.modo_venda_em_jogo:
            self.withdraw()
            self.modo_venda_em_jogo = novo_modo
            px, py, sz = self.carregar_configuracoes_janela()
            self.qr_size = sz
            self.ajustar_geometria(px, py)
            self.pix_atual = ""
            self.online = False
            self.gerando_agora = False

        deve_exibir = status_net and self.pix_habilitado and (not jogo_ativo or forcar_qr)

        if not deve_exibir:
            if self.online or self.winfo_viewable():
                self.withdraw()
                self.online = False
                self.gerando_agora = False
        else:
            if not self.online or (self.pix_atual == "" and not self.gerando_agora):
                self.online = True
                delay = 100 if forcar_qr else (self.tempo_menu * 1000)
                self.after(delay, self.ciclo_pagamento)

        self.after(250, self.vigia_de_seguranca)

    def ciclo_pagamento(self):
        if self.gerando_agora or not self.online:
            return

        # 🔥 NOVO (sem quebrar fluxo)
        self.processar_pix_key()
        self.verificar_token()

        self.gerando_agora = True

        try:
            payment_data = {
                "transaction_amount": self.valor_pix,
                "description": f"PIX {self.creditos_pix} Fichas",
                "payment_method_id": "pix",
                "payer": {"email": "pinguim@dev.com"}
            }

            result = self.sdk.payment().create(payment_data)

            if result["status"] == 201:
                self.pix_atual = result["response"]["point_of_interaction"]["transaction_data"]["qr_code"]
                self.atualizar_status_visual()
                self.update_idletasks()
                self.deiconify()
                self.monitorar_status(result["response"]["id"])
            else:
                self.gerando_agora = False
                self.after(5000, self.ciclo_pagamento)

        except:
            self.gerando_agora = False
            self.after(5000, self.ciclo_pagamento)

    def monitorar_status(self, payment_id):
        if not self.online or self.pix_atual == "":
            return
        try:
            check = self.sdk.payment().get(payment_id)
            if check["response"]["status"] == "approved":
                self.pix_atual = ""
                self.withdraw()
                self.entregar_creditos_sequencial(self.creditos_pix)
            else:
                self.after(3000, lambda: self.monitorar_status(payment_id))
        except:
            self.after(3000, lambda: self.monitorar_status(payment_id))

    def entregar_creditos_sequencial(self, restantes):
        if restantes > 0:
            if os.path.exists(self.path_som):
                subprocess.Popen(["mpv", "--no-video", "--really-quiet", self.path_som])

            self.somar_creditos_arquivo(1)

            self.after(500, lambda: self.entregar_creditos_sequencial(restantes - 1))
        else:
            self.gerando_agora = False
            self.after(2000, self.ciclo_pagamento)

    def atualizar_status_visual(self):
        if not self.pix_atual:
            return

        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(self.pix_atual)
        qr.make(fit=True)

        img_pil = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        img_resized = img_pil.resize((self.qr_size, self.qr_size), Image.NEAREST)

        self.img_qr = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, size=(self.qr_size, self.qr_size))
        self.qr_display.configure(image=self.img_qr)

        self.lbl_valor.configure(text=f"R${self.valor_pix:.2f}".replace(".", ","))
        self.lbl_fichas.configure(text=f"créditos: {self.creditos_pix}")

    def teste_real_internet(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            s.connect(("8.8.8.8", 53))
            s.close()
            return True
        except:
            return False

    def carregar_configuracoes_janela(self):
        path = self.path_pos_jogo if self.modo_venda_em_jogo else self.path_pos_normal
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    d = f.read().strip().split(",")
                    return int(d[0]), int(d[1]), int(d[2])
            except:
                pass
        return 500, 200, 250

    def salvar_configuracoes_janela(self, event=None):
        path = self.path_pos_jogo if self.modo_venda_em_jogo else self.path_pos_normal
        try:
            with open(path, "w") as f:
                f.write(f"{self.winfo_x()},{self.winfo_y()},{self.qr_size}")
        except:
            pass

    def iniciar_arrasto(self, event):
        self.x_off = event.x
        self.y_off = event.y

    def movimentar_janela(self, event):
        x = self.winfo_x() + (event.x - self.x_off)
        y = self.winfo_y() + (event.y - self.y_off)
        self.geometry(f"+{x}+{y}")

    def redimensionar(self, event):
        passo = 20
        self.qr_size = max(120, min(800, self.qr_size + (passo if event.num == 4 else -passo)))
        self.ajustar_geometria(self.winfo_x(), self.winfo_y())
        self.atualizar_status_visual()
        self.salvar_configuracoes_janela()


if __name__ == "__main__":
    app = RetroVending()
    app.mainloop()