import pyautogui
import time
import tkinter as tk
from tkinter import ttk, messagebox
import threading

pyautogui.PAUSE = 1
bloqueio_envio = False

import pyperclip ### para uso do mesmo
def enviar_mensagem_whatsapp(turma, mensagem):
    try:
        pyautogui.click(x=309, y=204)  # Clique no campo de busca
        time.sleep(1)
        pyautogui.write(turma)
        time.sleep(1.5)
        pyautogui.press('enter')  # Seleciona a turma
        time.sleep(1)

        ### Alterado para o pyperclip, mais rápido e mais eficiente, corrige o "\n"
        pyperclip.copy(mensagem)  # Copia mensagem para área de transferência
        pyautogui.hotkey("ctrl", "v")  # Cola a mensagem no WhatsApp Web

        pyautogui.press('enter')  # Envia a mensagem
        time.sleep(1)
        pyautogui.hotkey('esc')  # Fecha a conversa
        time.sleep(1)
    except Exception as e:
        raise RuntimeError(f"Erro ao enviar para {turma}: {str(e)}")

def carregar_turmas():
    turmas = []
    try:
        with open('turmas.txt', 'r', encoding='utf-8') as arquivo: ###Add encoding='utf-8' para carateres especiais
            for linha in arquivo:
                linha = linha.strip()
                if linha:
                    nome, dia = linha.split(',')
                    turmas.append({'nome': nome.strip(), 'dia': dia.strip().lower()})
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar turmas: {str(e)}")
    return turmas

def enviar_mensagens():
    global bloqueio_envio
    
    if bloqueio_envio:
        return
    
    try:
        mensagem = campo_mensagem.get("1.0", tk.END).strip()
        if not mensagem:
            messagebox.showerror("Erro", "Digite uma mensagem para enviar!")
            return

        turmas_selecionadas = []
        
        if modo_selecao.get() == 'todas':
            turmas_selecionadas = [t['nome'] for t in todas_turmas]
        else:
            dia = combo_dias.get().lower()
            turmas_selecionadas = [t['nome'] for t in todas_turmas if t['dia'] == dia]

        if not turmas_selecionadas:
            messagebox.showwarning("Aviso", "Nenhuma turma selecionada!")
            return

        confirmacao = messagebox.askyesno(
            "Confirmar", 
            f"Pronto para enviar para {len(turmas_selecionadas)} turmas?\n\n"
            "Deixe o WhatsApp Web ABERTO e VISÍVEL!\n"
            "Não use o computador durante o envio!"
        )
        
        if not confirmacao:
            return

        bloqueio_envio = True

        def tarefa_envio():
            try:
                messagebox.showinfo(
                    "Atenção", 
                    "O envio começará em 10 segundos!\n"
                    "POSICIONE O WHATSAPP WEB AGORA!"
                )
                
                time.sleep(10)
                
                for turma in turmas_selecionadas:
                    enviar_mensagem_whatsapp(turma, mensagem)
                
                messagebox.showinfo("Sucesso", "Todas mensagens enviadas!")
                
            except Exception as e:
                messagebox.showerror("Erro", str(e))
                
            finally:
                global bloqueio_envio
                bloqueio_envio = False

        threading.Thread(target=tarefa_envio, daemon=True).start()
        
    except Exception as e:
        messagebox.showerror("Erro", str(e))
        bloqueio_envio = False

# Interface gráfica
root = tk.Tk()
root.title("Automação WhatsApp")
root.geometry("500x400")
root.iconbitmap("logo.ico")

# Carregar turmas
todas_turmas = carregar_turmas()
dias_disponiveis = list(set(t['dia'] for t in todas_turmas)) if todas_turmas else []

# Frame de seleção
frame_selecao = ttk.LabelFrame(root, text="Seleção de Turmas")
frame_selecao.pack(pady=10, padx=10, fill='x')

modo_selecao = tk.StringVar(value='todas')

rb_todas = ttk.Radiobutton(frame_selecao, text="Todas as Turmas", 
                          variable=modo_selecao, value='todas')
rb_todas.pack(side='left', padx=5)

rb_dia = ttk.Radiobutton(frame_selecao, text="Turmas por Dia:", 
                        variable=modo_selecao, value='dia')
rb_dia.pack(side='left', padx=5)

combo_dias = ttk.Combobox(frame_selecao, values=dias_disponiveis, state='disabled')
combo_dias.pack(side='left', padx=5)

def atualizar_combobox(*args):
    combo_dias.config(state='readonly' if modo_selecao.get() == 'dia' else 'disabled')

modo_selecao.trace_add('write', atualizar_combobox)

# Campo de mensagem
frame_mensagem = ttk.LabelFrame(root, text="Mensagem")
frame_mensagem.pack(pady=10, padx=10, fill='both', expand=True)

campo_mensagem = tk.Text(frame_mensagem, height=6)
campo_mensagem.pack(pady=5, padx=5, fill='both', expand=True)

# Botão de envio
btn_enviar = ttk.Button(root, text="Enviar Mensagens", command=enviar_mensagens)
btn_enviar.pack(pady=10)

root.mainloop()