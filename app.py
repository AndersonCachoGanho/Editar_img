import streamlit as st
import fitz
import requests
import base64
from bs4 import BeautifulSoup

st.set_page_config(page_title="Simulador Brindes Online", layout="wide")

# --- Função para baixar imagem com User-Agent (Evita bloqueios) ---
def get_b64_bg(url):
    try:
        # Simulamos um navegador real para o site não bloquear o download
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        return base64.b64encode(res.content).decode()
    except Exception as e:
        # Se falhar, avisamos o que aconteceu
        st.sidebar.error(f"Erro ao acessar imagem do produto: {e}")
        return None

def convert_to_svg_clean(arq_uploader):
    try:
        conteudo = arq_uploader.read()
        ext = arq_uploader.name.split('.')[-1].lower()
        if ext in ['pdf', 'eps', 'ai']:
            doc = fitz.open(stream=conteudo, filetype=ext)
            svg_str = doc.load_page(0).get_svg_image()
            doc.close()
        else:
            svg_str = conteudo.decode("utf-8", errors="ignore")
        
        soup = BeautifulSoup(svg_str, "xml")
        for rect in soup.find_all('rect', fill=["white", "#ffffff", "#fff"]):
            rect.decompose()
        return base64.b64encode(str(soup).encode()).decode()
    except: return None

# --- Interface ---
with st.sidebar:
    st.header("🎨 Ajustes")
    url_prod = st.text_input("Link da Imagem do Produto:", "https://images.tcdn.com.br/img/img_prod/697711/caneca_de_ceramica_branca_personalizada_325ml_1_1_20200918151813.jpg")
    arq_logo = st.file_uploader("Suba a Logo (Vetor):", type=["pdf", "eps", "ai", "svg"])
    cor_logo = st.color_picker("Cor da Estampa:", "#000000")
    
    if st.button("🧹 Limpar Memória/Reset"):
        st.components.v1.html("<script>localStorage.clear(); window.parent.location.reload();</script>")
        st.stop()

if url_prod and arq_logo:
    # Baixamos a imagem no servidor para evitar erro de exibição no navegador
    b64_bg = get_b64_bg(url_prod)
    b64_logo = convert_to_svg_clean(arq_logo)

    if b64_bg and b64_logo:
      # ==============================================================================
# --- DEFINIÇÃO DO HTML DO EDITOR (COM ALINHAMENTO CENTRAL CORRIGIDO) ---
# ==============================================================================
# Usamos Flexbox rigoroso e definimos larguras máximas idênticas para o Canvas e o Botão.
# Isso garante que eles fiquem empilhados e centralizados perfeitamente na página.
html_editor = f"""
<script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>

<style>
    /* Reset total para garantir controle absoluto do layout */
    body {{
        margin: 0;
        padding: 0;
        overflow: hidden; /* Evita barras de rolagem duplas indesejadas */
        background-color: transparent; /* Combina com o fundo do Streamlit */
    }}

    /* 1. CONTÊINER PRINCIPAL (Invisível, ocupa a largura total) */
    .super-container {{
        width: 100%;
        display: flex;
        justify-content: center; /* CENTRALIZAÇÃO HORIZONTAL CRÍTICA */
        padding-top: 15px; /* Pequeno espaçamento do topo */
    }}

    /* 2. CAIXA DO EDITOR (Envolve o Canvas e o Botão) */
    .editor-box {{
        width: 700px; /* Largura fixa idêntica à largura do Canvas */
        max-width: 100%; /* Garante responsividade em telas menores */
        display: flex;
        flex-direction: column; /* Empilha Canvas sobre o Botão */
        align-items: center; /* Centraliza itens dentro da caixa */
        text-align: center;
    }}

    /* 3. ESTILO DO CANVAS */
    #canvas-container {{
        border: 1px solid #ccc;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        background-color: white; /* Fundo branco para o produto */
        overflow: hidden; /* Mantém a borda arredondada */
    }}

    /* 4. ESTILO DO BOTÃO (Agora perfeitamente alinhado) */
    #btnSave {{
        margin-top: 25px; /* Espaço entre o produto e o botão */
        margin-bottom: 25px; /* Espaço inferior */
        padding: 14px 28px;
        background-color: #28a745; /* Verde Sucesso */
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-family: 'Source Sans Pro', sans-serif; /* Fonte padrão do Streamlit */
        font-weight: bold;
        font-size: 16px;
        width: 100%; /* Ocupa TODA a largura da .editor-box (700px) */
        max-width: 700px; /* Garante alinhamento perfeito com o canvas */
        transition: background-color 0.2s, transform 0.1s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }}

    #btnSave:hover {{
        background-color: #218838;
    }}

    #btnSave:active {{
        transform: translateY(1px); /* Efeito de clique */
    }}
</style>

<div class="super-container">
    <div class="editor-box">
        
        <div id="canvas-container">
            <canvas id="canvas"></canvas>
        </div>
        
        <button id="btnSave">
            💾 BAIXAR JPEG FINAL
        </button>
    </div>
</div>

<script>
    // Inicialização do Canvas Fabric.js
    const canvas = new fabric.Canvas('canvas', {{
        preserveObjectStacking: true // Mantém a ordem dos objetos
    }});
    const activeColor = "{cor_logo}"; // Cor vinda do Streamlit
    const storageKey = "brinde_pos_data"; // Chave para o LocalStorage

    // 1. Carregar Imagem de Fundo (Produto)
    fabric.Image.fromURL('data:image/png;base64,{b64_bg}', function(img) {{
        // Define a largura máxima do canvas para 700px, ajustando a altura proporcionalmente
        const maxDisplayWidth = 700;
        const currentWindowWidth = window.innerWidth - 30; // Margem de segurança
        const canvasWidth = Math.min(currentWindowWidth, maxDisplayWidth);
        
        const scale = canvasWidth / img.width;
        
        canvas.setWidth(canvasWidth);
        canvas.setHeight(img.height * scale);
        
        // Define a imagem como fundo, não selecionável e não editável
        img.set({{
            scaleX: scale,
            scaleY: scale,
            selectable: false,
            evented: false,
            originX: 'left',
            originY: 'top'
        }});
        canvas.setBackgroundImage(img, canvas.renderAll.bind(canvas));
    }});

    // 2. Carregar e Colorir Logo (com persistência LocalStorage)
    fabric.loadSVGFromString(atob('{b64_logo}'), function(objects, options) {{
        const logo = fabric.util.groupSVGElements(objects, options);
        
        // Aplica a cor escolhida em todos os caminhos do vetor
        logo.getObjects().forEach(obj => {{ 
            obj.set({{ fill: activeColor, stroke: activeColor }}); 
        }});

        // Tenta recuperar a posição salva no navegador
        const savedPos = JSON.parse(localStorage.getItem(storageKey));
        
        if (savedPos) {{
            // Restaura posição, escala e rotação salvos
            logo.set({{
                left: savedPos.left, 
                top: savedPos.top, 
                scaleX: savedPos.scaleX, 
                scaleY: savedPos.scaleY, 
                angle: savedPos.angle
            }});
        } else {{
            // Posição inicial centralizada (considerando 700px de largura)
            logo.set({{ 
                left: 350, 
                top: 250, 
                scaleX: 0.2, 
                scaleY: 0.2,
                originX: 'center',
                originY: 'center'
            }});
        }}

        // Estilização dos controles de manipulação (alças brancas com borda azul)
        logo.set({{
            cornerColor: 'white',
            cornerStrokeColor: '#007bff',
            cornerSize: 12,
            transparentCorners: false,
            borderColor: '#007bff',
            hasRotatingPoint: true,
            rotatingPointOffset: 40
        }});

        canvas.add(logo);
        canvas.setActiveObject(logo);
        canvas.renderAll();

        // FUNÇÃO DE SALVAMENTO AUTOMÁTICO (Debounced para performance)
        let saveTimeout;
        const savePos = () => {{
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {{
                const data = {{
                    left: logo.left,
                    top: logo.top,
                    scaleX: logo.scaleX,
                    scaleY: logo.scaleY,
                    angle: logo.angle
                }};
                localStorage.setItem(storageKey, JSON.stringify(data));
            }}, 100); // Salva 100ms após o último movimento
        }};

        // Escuta eventos de modificação e movimento para salvar a posição
        logo.on('modified', savePos);
        logo.on('moving', savePos);
    }});

    // 3. Função de Download (Ajustada para o novo layout)
    document.getElementById('btnSave').addEventListener('click', function() {{
        // Remove a seleção para que as alças não apareçam na imagem final
        canvas.discardActiveObject().renderAll();
        
        // Gera o DataURL do canvas como JPEG de alta qualidade
        // multiplier: 2 dobra a resolução para um download nítido (1400px de largura)
        const dataURL = canvas.toDataURL({{ 
            format: 'jpeg', 
            quality: 0.9, 
            multiplier: 2 
        }});
        
        // Cria um link invisível para forçar o download
        const link = document.createElement('a');
        link.download = 'simulacao_brinde.jpg';
        link.href = dataURL;
        link.click();
    }});
</script>
"""

# ==============================================================================
# --- CHAMADA DO COMPONENTE NO STREAMLIT (COM AJUSTES DE LARGURA) ---
# ==============================================================================
# É CRUCIAL não definir uma largura fixa aqui (width=...).
# O Streamlit tentará ocupar o máximo de espaço, e nosso CSS interno fará a centralização.
st.components.v1.html(html_editor, height=900, scrolling=False)

# --- Chamada do Componente no Streamlit ---
# USAMOS 'use_container_width=True' PARA OCUPAR A PÁGINA INTEIRA
st.components.v1.html(html_editor, height=850, scrolling=False)
        st.components.v1.html(html_editor, height=850)
else:
    st.info("💡 Dica: Insira um link válido de imagem e suba um arquivo vetorial para começar.")
