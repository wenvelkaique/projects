
"""
Ferramentas Python - UI estilo "cards" sem imagens externas
Recursos:
 - Despesas (CSV) + gráfico por categoria
 - Gerador de Senhas
 - Conversor de unidades (°C/°F, km/milha)
 - Organizador de arquivos por extensão
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import csv, os, shutil, random, string

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False


BG      = "#f3f2fa"   # fundo geral
CARD    = "#ffffff"   # cartão
ACCENT  = "#7a5cff"   # roxo principal
ACCENT_2= "#ffc371"   # laranja suave
TXT     = "#2b2b2b"   # texto
MUTED   = "#7b7b8a"   # texto secundário
OK      = "#22c55e"
DANGER  = "#ef4444"

FONT_H1 = ("Segoe UI", 18, "bold")
FONT_H2 = ("Segoe UI", 14, "bold")
FONT_TX = ("Segoe UI", 11)
FONT_SM = ("Segoe UI", 10)

def style_ttk(root):
    style = ttk.Style(root)
  
    style.theme_use("clam")

    style.configure("TLabel", background=CARD, foreground=TXT, font=FONT_TX)
    style.configure("Muted.TLabel", foreground=MUTED)
    style.configure("H1.TLabel", background=BG, foreground=TXT, font=FONT_H1)
    style.configure("H2.TLabel", background=CARD, foreground=TXT, font=FONT_H2)

    style.configure("TEntry", fieldbackground="#fbfbfd", background="#fbfbfd")
    style.map("TEntry", focusbackground=[("focus", "#fbfbfd")])

    style.configure("TButton",
                    font=FONT_TX,
                    padding=8,
                    relief="flat",
                    background=ACCENT,
                    foreground="white")
    style.map("TButton",
              background=[("active", "#6b4fff")])

    style.configure("Alt.TButton", background=ACCENT_2, foreground="#3b2f2f")
    style.map("Alt.TButton", background=[("active", "#f7b65a")])

    style.configure("Danger.TButton", background=DANGER, foreground="white")
    style.map("Danger.TButton", background=[("active", "#d43a3a")])

    style.configure("TCombobox", fieldbackground="#fbfbfd", background="#fbfbfd")


class Card(ttk.Frame):
    """Cartão com borda arredondada simulada usando Canvas"""
    def __init__(self, master, title, subtitle=None, width=360, height=360, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self["padding"] = 0
        self.canvas = tk.Canvas(self, bg=BG, bd=0, highlightthickness=0, width=width, height=height)
        self.canvas.pack(fill="both", expand=True)
        # desenha “borda suave”
        self.canvas.create_rectangle(4, 4, width-4, height-4, fill=CARD, outline=CARD)
        # cabeçalho
        self.canvas.create_text(20, 22, anchor="w", text=title, font=FONT_H2, fill=TXT)
        if subtitle:
            self.canvas.create_text(20, 46, anchor="w", text=subtitle, font=FONT_SM, fill=MUTED)
        # container real por cima do canvas
        self.inner = ttk.Frame(self, padding=(18, 60, 18, 18), style="CardBody.TFrame")
        self.inner.place(x=0, y=0, relwidth=1, relheight=1)


DESPESAS_FILE = "despesas.csv"
despesas = []

def carregar_despesas():
    despesas.clear()
    if not os.path.exists(DESPESAS_FILE):
        return
    with open(DESPESAS_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["valor"] = float(row["valor"])
            except:
                continue
            despesas.append(row)

def salvar_despesas():
    with open(DESPESAS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["categoria", "descricao", "valor"])
        writer.writeheader()
        writer.writerows(despesas)

def adicionar_despesa_gui(lista):
    categoria = simpledialog.askstring("Categoria", "Digite a categoria:")
    if categoria is None: return
    descricao = simpledialog.askstring("Descrição", "Descreva a despesa:")
    if descricao is None: return
    try:
        valor = float(simpledialog.askstring("Valor", "Valor (use ponto para centavos, ex: 12.50):"))
    except:
        messagebox.showerror("Erro", "Valor inválido.")
        return
    despesas.append({"categoria": categoria, "descricao": descricao, "valor": valor})
    salvar_despesas()
    atualizar_lista_despesas(lista)
    messagebox.showinfo("OK", "Despesa registrada! 💸")

def excluir_despesa_gui(lista):
    sel = lista.curselection()
    if not sel:
        messagebox.showwarning("Aviso", "Selecione uma despesa para excluir.")
        return
    idx = sel[0]
    del despesas[idx]
    salvar_despesas()
    atualizar_lista_despesas(lista)

def atualizar_lista_despesas(lista):
    lista.delete(0, tk.END)
    total = 0.0
    for d in despesas:
        lista.insert(tk.END, f"{d['categoria']} — {d['descricao']}  •  R$ {d['valor']:.2f}")
        total += d["valor"]
    lista.insert(tk.END, "-"*60)
    lista.insert(tk.END, f"TOTAL: R$ {total:.2f}")

def mostrar_grafico_despesas():
    if not despesas:
        messagebox.showinfo("Info", "Nenhuma despesa registrada.")
        return
    if not HAS_MPL:
        messagebox.showwarning("Gráfico indisponível",
                               "Instale o matplotlib para ver o gráfico:\n\npip install matplotlib")
        return
    por_cat = {}
    for d in despesas:
        por_cat[d["categoria"]] = por_cat.get(d["categoria"], 0) + d["valor"]
    cats = list(por_cat.keys())
    vals = list(por_cat.values())
    plt.figure()
    plt.bar(cats, vals)
    plt.title("Despesas por categoria")
    plt.ylabel("R$ (total)")
    plt.tight_layout()
    plt.show()


def gerar_senha(tam_entry, out_entry):
    try:
        n = int(tam_entry.get())
        if n < 4:
            raise ValueError
    except:
        messagebox.showerror("Erro", "Informe um tamanho numérico (≥ 4).")
        return
    caracteres = string.ascii_letters + string.digits + string.punctuation
    senha = "".join(random.choice(caracteres) for _ in range(n))
    out_entry.config(state="normal")
    out_entry.delete(0, tk.END)
    out_entry.insert(0, senha)
    out_entry.config(state="readonly")


def converter(valor_entry, combo, label_out):
    try:
        v = float(valor_entry.get())
    except:
        messagebox.showerror("Erro", "Digite um número.")
        return
    opt = combo.get()
    if opt == "Celsius → Fahrenheit":
        r = v * 9/5 + 32
        txt = f"{v:.2f} °C = {r:.2f} °F"
    elif opt == "Fahrenheit → Celsius":
        r = (v - 32) * 5/9
        txt = f"{v:.2f} °F = {r:.2f} °C"
    elif opt == "Km → Milhas":
        r = v * 0.621371
        txt = f"{v:.2f} km = {r:.2f} mi"
    else:
        r = v / 0.621371
        txt = f"{v:.2f} mi = {r:.2f} km"
    label_out.config(text=txt)


EXTENSOES = {
    "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "Documentos": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx"],
    "Músicas": [".mp3", ".wav", ".flac", ".m4a"],
    "Vídeos": [".mp4", ".mkv", ".avi", ".mov"],
    "Compactados": [".zip", ".rar", ".7z"],
}

def organizar_pasta():
    pasta = filedialog.askdirectory(title="Escolha a pasta para organizar")
    if not pasta: 
        return
    movidos = 0
    for arq in os.listdir(pasta):
        caminho = os.path.join(pasta, arq)
        if not os.path.isfile(caminho):
            continue
        arq_low = arq.lower()
        destino = None
        for nome, exts in EXTENSOES.items():
            if any(arq_low.endswith(ext) for ext in exts):
                destino = os.path.join(pasta, nome)
                break
        if destino is None:
            destino = os.path.join(pasta, "Outros")
        os.makedirs(destino, exist_ok=True)
        try:
            shutil.move(caminho, os.path.join(destino, arq))
            movidos += 1
        except Exception as e:
            print("Erro movendo", arq, e)
    messagebox.showinfo("Organizador", f"Arquivos organizados! Itens movidos: {movidos}")


root = tk.Tk()
root.title("Ferramentas Python")
root.geometry("1120x640")
root.minsize(1000, 600)
root.configure(bg=BG)
style_ttk(root)

# Topbar
top = ttk.Frame(root, padding=(18, 16), style="Top.TFrame")
top.pack(fill="x")
lbl = ttk.Label(top, text="Ferramentas Python", style="H1.TLabel")
lbl.pack(side="left")


grid = ttk.Frame(root, padding=18)
grid.pack(fill="both", expand=True)

grid.columnconfigure((0,1), weight=1, uniform="col")
grid.rowconfigure((0,1), weight=1, uniform="row")


card1 = Card(grid, "Despesas", "Registre e visualize seus gastos")
card1.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

btns1 = ttk.Frame(card1.inner)
btns1.pack(anchor="w", pady=(0,10))
ttk.Button(btns1, text="Adicionar Despesa", command=lambda: adicionar_despesa_gui(lista_desp)).grid(row=0, column=0, padx=(0,8))
ttk.Button(btns1, text="Excluir Selecionada", style="Danger.TButton",
           command=lambda: excluir_despesa_gui(lista_desp)).grid(row=0, column=1, padx=(0,8))
ttk.Button(btns1, text="Gráfico por Categoria", style="Alt.TButton",
           command=mostrar_grafico_despesas).grid(row=0, column=2)

lista_desp = tk.Listbox(card1.inner, height=10, bd=0, highlightthickness=0,
                        font=("Consolas", 10))
lista_desp.pack(fill="both", expand=True)

carregar_despesas()
atualizar_lista_despesas(lista_desp)


card2 = Card(grid, "Senhas", "Gere senhas fortes rapidamente")
card2.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

frm_pw = ttk.Frame(card2.inner)
frm_pw.pack(fill="x", pady=(0,10))
ttk.Label(frm_pw, text="Tamanho:").grid(row=0, column=0, sticky="w")
ent_tam = ttk.Entry(frm_pw, width=10)
ent_tam.insert(0, "12")
ent_tam.grid(row=0, column=1, padx=8)
ttk.Button(frm_pw, text="Gerar senha",
           command=lambda: gerar_senha(ent_tam, ent_out)).grid(row=0, column=2)

ent_out = ttk.Entry(card2.inner, font=("Consolas", 12), state="readonly")
ent_out.pack(fill="x")

ttk.Label(card2.inner, text="Dica: use 16+ caracteres, com letras, números e símbolos.",
          style="Muted.TLabel").pack(anchor="w", pady=(8,0))


card3 = Card(grid, "Conversor", "Temperatura e distância")
card3.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

frm_conv = ttk.Frame(card3.inner)
frm_conv.pack(fill="x", pady=(0,10))
ttk.Label(frm_conv, text="Valor:").grid(row=0, column=0, sticky="w")
ent_val = ttk.Entry(frm_conv, width=12)
ent_val.grid(row=0, column=1, padx=8)

combo = ttk.Combobox(frm_conv, state="readonly", width=24,
                     values=["Celsius → Fahrenheit", "Fahrenheit → Celsius",
                             "Km → Milhas", "Milhas → Km"])
combo.current(0)
combo.grid(row=0, column=2, padx=8)

lbl_res = ttk.Label(card3.inner, text="Resultado aparecerá aqui.", style="Muted.TLabel")
lbl_res.pack(anchor="w", pady=(6,10))

ttk.Button(card3.inner, text="Converter",
           command=lambda: converter(ent_val, combo, lbl_res)).pack(anchor="w")


card4 = Card(grid, "Organizador", "Separe arquivos por tipo em pastas")
card4.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

ttk.Label(card4.inner, text="Escolha uma pasta e eu organizo por categoria.",
          style="Muted.TLabel").pack(anchor="w", pady=(0,10))
ttk.Button(card4.inner, text="Selecionar Pasta e Organizar", style="Alt.TButton",
           command=organizar_pasta).pack(anchor="w")


footer = ttk.Frame(root, padding=(18, 0, 18, 14))
footer.pack(fill="x")
ttk.Label(footer, text="Feito com Tkinter • sem imagens externas • tema inspirado em cards",
          style="Muted.TLabel", background=BG).pack(side="left")

root.mainloop()

