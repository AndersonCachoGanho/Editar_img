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
        html_editor = f"""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>
        
        <div style="text-align: center;">
            <canvas id="canvas" style="border: 1px solid #ccc; border-radius: 8px; max-width: 100%;"></canvas>
            <br>
            <button id="btnSave" style="margin-top: 15px; padding: 12px 24px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; max-width: 700px;">
                💾 BAIXAR JPEG FINAL
            </button>
        </div>

        <script>
        const canvas = new fabric.Canvas('canvas');
        const activeColor = "{cor_logo}";
        const storageKey = "brinde_pos_data";

        // 1. Carregar Fundo (Garantido pelo Base64 vindo do Python)
        fabric.Image.fromURL('data:image/png;base64,{b64_bg}', function(img) {{
            const canvasWidth = Math.min(window.innerWidth - 50, 700);
            const scale = canvasWidth / img.width;
            canvas.setWidth(canvasWidth);
            canvas.setHeight(img.height * scale);
            img.set({{ scaleX: scale, scaleY: scale, selectable: false, evented: false }});
            canvas.setBackgroundImage(img, canvas.renderAll.bind(canvas));
        }});

        // 2. Carregar Logo
        fabric.loadSVGFromString(atob('{b64_logo}'), function(objects, options) {{
            const logo = fabric.util.groupSVGElements(objects, options);
            logo.getObjects().forEach(obj => {{ obj.set({{ fill: activeColor, stroke: activeColor }}); }});

            const savedPos = JSON.parse(localStorage.getItem(storageKey));
            if (savedPos) {{
                logo.set({{
                    left: savedPos.left, top: savedPos.top, 
                    scaleX: savedPos.scaleX, scaleY: savedPos.scaleY, 
                    angle: savedPos.angle
                }});
            }} else {{
                logo.set({{ left: 100, top: 100, scaleX: 0.2, scaleY: 0.2 }});
            }}

            logo.set({{ cornerColor: '#007bff', cornerSize: 12, transparentCorners: false }});
            canvas.add(logo);
            canvas.setActiveObject(logo);
            canvas.renderAll();

            const savePos = () => {{
                const data = {{ left: logo.left, top: logo.top, scaleX: logo.scaleX, scaleY: logo.scaleY, angle: logo.angle }};
                localStorage.setItem(storageKey, JSON.stringify(data));
            }};
            logo.on('modified', savePos);
            logo.on('moving', savePos);
        }});

        document.getElementById('btnSave').addEventListener('click', function() {{
            canvas.discardActiveObject().renderAll();
            const dataURL = canvas.toDataURL({{ format: 'jpeg', quality: 0.9, multiplier: 2 }});
            const link = document.createElement('a');
            link.download = 'simulacao.jpg';
            link.href = dataURL;
            link.click();
        }});
        </script>
        """
        st.components.v1.html(html_editor, height=850)
else:
    st.info("💡 Dica: Insira um link válido de imagem e suba um arquivo vetorial para começar.")
