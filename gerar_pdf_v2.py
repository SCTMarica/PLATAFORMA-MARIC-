#!/usr/bin/env python3
"""
Gera PDF com fluxos de usuários da Plataforma Maricá usando fpdf2
"""
from fpdf import FPDF
from datetime import datetime

class FluxosPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Plataforma Marica", ln=True, align="C")
        self.set_font("Arial", "", 10)
        self.cell(0, 5, "Fluxos de Usuarios e Funcionalidades", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("Arial", "B", 14)
        self.set_text_color(13, 110, 253)
        self.cell(0, 10, title, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def subsection_title(self, title):
        self.set_font("Arial", "B", 12)
        self.set_text_color(11, 19, 43)
        self.cell(0, 8, title, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def flow_item(self, text, indent=0):
        self.set_font("Arial", "", 10)
        x = self.l_margin + indent
        self.set_x(x)
        prefix = "→ " if indent == 0 else "└─ "
        self.multi_cell(0, 6, prefix + text)

# Criar PDF
pdf = FluxosPDF()
pdf.add_page()

# Data
data_str = datetime.now().strftime("%d de %B de %Y as %H:%M")
pdf.set_font("Arial", "I", 8)
pdf.cell(0, 5, f"Gerado em: {data_str}", ln=True, align="R")
pdf.ln(5)

# Visão Geral
pdf.section_title("Visao Geral do Sistema")
pdf.set_font("Arial", "", 10)
pdf.multi_cell(0, 5, "A Plataforma Marica e um portal institucional para a prefeitura com tres papeis de usuario distintos, cada um com permissoes e fluxos especificos.")
pdf.ln(5)

# CLIENTE FINAL
pdf.section_title("Fluxos por Tipo de Usuario")
pdf.subsection_title("1. CLIENTE FINAL (Cidadao)")
pdf.flow_item("Acessa site publicamente (sem login)")
pdf.flow_item("HOME: ve banners, noticias destaque, eventos proximos", 5)
pdf.flow_item("NOTICIAS: navega lista de noticias, filtra por data", 5)
pdf.flow_item("EVENTOS: ve eventos, clica em inscricao", 5)
pdf.flow_item("MIDIA: visualiza galeria de fotos, videos institucionais", 5)
pdf.flow_item("SOBRE: informacoes sobre a prefeitura", 5)
pdf.flow_item("CONTATO: formulario de contato / dados de atendimento", 5)
pdf.flow_item("LINKS: links uteis e sociais", 5)
pdf.flow_item("Se quer mais: REGISTRA/LOGA", 0)
pdf.flow_item("PORTAL: acesso a setor especifico", 5)
pdf.ln(3)

# SUPERVISOR
pdf.subsection_title("2. SUPERVISOR/COORDENADOR (Gestor de Setor)")
pdf.flow_item("LOGA no sistema")
pdf.flow_item("PORTAL: dashboard do setor", 5)
pdf.flow_item("Ve eventos/noticias do seu setor", 10)
pdf.flow_item("Visualiza inscricoes/participacoes", 10)
pdf.flow_item("Exporta relatorios", 10)
pdf.flow_item("ADMIN RESTRITO", 5)
pdf.flow_item("Criar/editar noticias do seu setor", 10)
pdf.flow_item("Criar/editar eventos do seu setor", 10)
pdf.flow_item("Gerenciar midias (fotos/videos)", 10)
pdf.flow_item("NAO pode: gerenciar usuarios, settings globais", 5)
pdf.ln(3)

pdf.add_page()

# ADMIN MASTER
pdf.subsection_title("3. ADMINISTRADOR MASTER (TI/Gestor)")
pdf.flow_item("LOGA no sistema")
pdf.flow_item("ADMIN DJANGO (acesso total)", 5)
pdf.flow_item("Users: criar, editar, deletar, atribuir papeis", 10)
pdf.flow_item("Site Settings: cores, logo, contatos, taglines", 10)
pdf.flow_item("News: CRUD completo", 10)
pdf.flow_item("Events: CRUD completo", 10)
pdf.flow_item("Media: CRUD completo", 10)
pdf.flow_item("Social Links: CRUD completo", 10)
pdf.flow_item("PORTAL ADMIN: visao de tudo", 5)
pdf.flow_item("Dashboard com estatisticas globais", 10)
pdf.ln(5)

# Matriz de Permissões
pdf.section_title("Matriz de Permissoes")
pdf.set_font("Arial", "B", 9)
col_width = 50
pdf.cell(col_width, 8, "Acao", border=1)
pdf.cell(col_width, 8, "Cliente", border=1)
pdf.cell(col_width, 8, "Supervisor", border=1)
pdf.cell(col_width, 8, "Admin", border=1, ln=True)

pdf.set_font("Arial", "", 9)
dados = [
    ("Ver home/noticias/eventos", "✓", "✓", "✓"),
    ("Inscrever em evento", "✓", "✓", "✓"),
    ("Criar noticia", "✗", "⚠ seu setor", "✓"),
    ("Criar evento", "✗", "⚠ seu setor", "✓"),
    ("Gerenciar usuarios", "✗", "✗", "✓"),
    ("Configurar site", "✗", "✗", "✓"),
    ("Acessar portal", "✓", "✓", "✓"),
    ("Ver logs/auditoria", "✗", "✗", "✓"),
]

for acao, cliente, supervisor, admin in dados:
    pdf.cell(col_width, 8, acao[:15] + "...", border=1)
    pdf.cell(col_width, 8, cliente, border=1)
    pdf.cell(col_width, 8, supervisor[:10] + "...", border=1)
    pdf.cell(col_width, 8, admin, border=1, ln=True)

pdf.ln(5)

# Funcionalidades
pdf.section_title("Funcionalidades Implementadas")
pdf.set_font("Arial", "", 10)
implementado = [
    "Sistema de usuarios com 3 papeis",
    "Banco de dados com modelos de Noticia, Evento, Midia",
    "URLs e rotas do site publico",
    "Configuracoes globais do site",
    "Templates base HTML",
    "Containerizacao com Docker"
]
for item in implementado:
    pdf.cell(5, 6, "✓")
    pdf.set_x(pdf.l_margin + 10)
    pdf.cell(0, 6, item, ln=True)

pdf.ln(5)

# Por Implementar
pdf.section_title("Funcionalidades por Implementar")
pdf.subsection_title("Prioridade Alta:")
pdf.set_font("Arial", "", 9)
por_fazer = [
    "Autenticacao Real: Login e registro com validacao",
    "Portal do Usuario: Views distintas por papel",
    "Inscricoes em Eventos: Salvar inscricoes no BD",
    "Admin Restrito: Supervisores sem acesso admin completo"
]
for item in por_fazer:
    pdf.cell(5, 5, "○")
    pdf.set_x(pdf.l_margin + 10)
    pdf.multi_cell(0, 5, item)

# Stack Técnico
pdf.ln(3)
pdf.section_title("Stack Tecnico")
pdf.set_font("Arial", "", 10)
stack = [
    "Backend: Django (Python)",
    "Banco: PostgreSQL",
    "Frontend: HTML5, CSS3",
    "Autenticacao: Django Auth customizado",
    "Containerizacao: Docker + Docker Compose",
    "Idioma: Portugues (pt-br)"
]
for item in stack:
    pdf.cell(5, 6, "→")
    pdf.set_x(pdf.l_margin + 10)
    pdf.cell(0, 6, item, ln=True)

# Salvar
pdf.output("fluxos_usuarios.pdf")
print("✅ PDF gerado com sucesso: fluxos_usuarios.pdf")
