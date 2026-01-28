import streamlit as st
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.core import PromptTemplate
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
from dotenv import load_dotenv
from fpdf import FPDF
import os
import csv
import datetime
import pandas as pd
import re

try:
    from src.report_generator import generate_cnas_report, generate_hr_summary, generate_training_sheet
except ImportError:
    def generate_cnas_report(client_name, period, client="default") -> str:
        return "Report generation unavailable - please check report_generator module"
    def generate_hr_summary(client_name, period, client="default") -> str:
        return "Report generation unavailable - please check report_generator module"
    def generate_training_sheet(topic, client_name, date, client="default") -> str:
        return "Report generation unavailable - please check report_generator module"

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="HRCC AI Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_embedding_model():
    try:
        return HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    except Exception as e:
        st.error(f"Failed to load embedding model: {e}")
        return None

@st.cache_resource
def load_llm():
    try:
        return HuggingFaceLLM(
            model_name="Qwen/Qwen1.5-0.5B",
            tokenizer_name="Qwen/Qwen1.5-0.5B",
            max_new_tokens=200,
            device_map="cpu",
        )
    except Exception as e:
        st.error(f"Failed to load LLM: {e}")
        return None

try:
    embedding_model = load_embedding_model()
    llm_model = load_llm()
    
    if embedding_model:
        Settings.embed_model = embedding_model
    if llm_model:
        Settings.llm = llm_model
except Exception as e:
    st.warning(f"Note: Some models may not be fully loaded. {e}")


SYSTEM_PROMPT = """
Tu es un assistant IA spécialisé en droit du travail algérien et conformité RH.
IMPORTANT:
- Utilise UNIQUEMENT les informations contenues dans le Contexte fourni.
- Si la réponse n'est pas explicitement trouvée dans le Contexte, réponds exactement:
  "Information non trouvée dans les documents fournis."
- NE JAMAIS inventer de liens, d'URLs ou de sources qui n'existent pas.
- NE JAMAIS utiliser tes connaissances générales si le contexte est insuffisant.
- Cite toujours les articles de loi ou sources UNIQUEMENT s'ils sont présents dans le contexte.
Ton rôle est d'aider les consultants RH avec des conseils juridiques fiables basés uniquement sur les textes légaux algériens disponibles.
Réponds en paragraphes clairs, sans répétitions.
"""

qa_prompt = PromptTemplate(
    f"""{SYSTEM_PROMPT}

Context:
{{context_str}}

Question:
{{query_str}}

Answer:""")

@st.cache_resource
def load_query_engine(client="default"):
    persist_dir = f"storage/{client}"
    if os.path.exists(persist_dir):
        try:
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(storage_context)
            return index.as_query_engine(
                text_qa_template=qa_prompt,
                similarity_top_k=3,
                response_mode="compact",
            )
        except Exception as e:
            st.warning(f"Could not load index for {client}: {e}")
            return None
    else:
        st.info(f"📁 Storage directory not found for client '{client}'. Using demo mode.")
        return None

def create_pdf(text, report_type="Report"):
    """Generate a PDF from text"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "HRCC AI Assistant - " + report_type, ln=True, align='C')
        pdf.ln(10)
        
        if os.path.exists('logo.png'):
            try:
                pdf.image('logo.png', x=10, y=8, w=30)
                pdf.ln(40)
            except:
                pass
        
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 5, str(text))
        
        pdf.set_y(-15)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 10, f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 0, 'C')
        
        return pdf.output(dest='S')
    except Exception as e:
        st.error(f"PDF generation error: {e}")
        return None

def log_action(action, details, client="default"):
    """Log user actions for analytics"""
    try:
        log_file = 'audit_log.csv'
        file_exists = os.path.isfile(log_file)
        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['timestamp', 'action', 'client', 'details', 'session_id'])
            session_id = st.session_state.get('session_id', 'anonymous')
            writer.writerow([datetime.datetime.now(), action, client, details, session_id])
    except Exception as e:
        pass  # Silently fail logging

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Main UI
st.title("⚖️ HRCC AI Assistant")
st.markdown("**HR Compliance & Knowledge AI Assistant**")
st.markdown("*Specializing in Algerian Labor Law and HR Compliance*")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    client = st.selectbox(
        "Select Client/Profile",
        ["default", "knowledge", "simple", "client1", "client2"],
        help="Choose which knowledge base to use"
    )
    
    st.divider()
    st.subheader("📖 About")
    st.markdown("""
    This AI assistant helps with:
    - 🏢 HR compliance questions
    - ⚖️ Algerian labor law
    - 📄 Report generation
    - 📊 HR analytics
    """)
    
    st.divider()
    if st.button("🔄 Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# Main tabs
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📄 Reports", "📊 Analytics"])

with tab1:
    st.subheader("Ask Legal/HR Questions")
    
    # Load query engine
    query_engine = load_query_engine(client)
    
    # Chat history display
    if st.session_state.chat_history:
        st.write("### Conversation History")
        for i, msg in enumerate(st.session_state.chat_history[-5:], 1):
            st.write(f"**Q{i}:** {msg['question']}")
            st.write(f"**A{i}:** {msg['answer']}")
            st.divider()
    
    # Input
    col1, col2 = st.columns([4, 1])
    with col1:
        question = st.text_input("Enter your question:", placeholder="E.g., What are employee rights in Algeria?", key="question_input")
    with col2:
        submit_btn = st.button("🔍 Ask", use_container_width=True)
    
    if submit_btn and question:
        try:
            with st.spinner("⏳ Thinking..."):
                if query_engine:
                    response = query_engine.query(question)
                    response_text = str(response).strip()
                    
                    # Get sources
                    sources = getattr(response, 'source_nodes', [])
                    if sources:
                        source_files = set()
                        for source in sources:
                            if hasattr(source, 'node') and hasattr(source.node, 'metadata'):
                                file_name = source.node.metadata.get('file_name', 'Unknown')
                                source_files.add(file_name)
                        
                        if source_files:
                            response_text += f"\n\n📚 **Sources:** {', '.join(sorted(source_files))}"
                else:
                    response_text = "Demo Mode: Knowledge base not loaded. Deploy with proper storage configuration."
            
            # Add to history
            st.session_state.chat_history.append({
                "question": question,
                "answer": response_text
            })
            log_action("chat_query", f"Q: {question[:50]}", client)
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            log_action("error", f"Query error: {str(e)}", client)
    elif submit_btn:
        st.warning("Please enter a question first.")

with tab2:
    st.subheader("Generate Reports")
    
    report_type = st.selectbox(
        "Select Report Type",
        ["CNAS Audit Report", "HR Compliance Summary", "Training Sheet"],
        help="Choose the type of report to generate"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        client_name = st.text_input("Client Name", placeholder="Enter client name", value="Demo Client")
    
    with col2:
        if report_type == "Training Sheet":
            date_input = st.date_input("Date", datetime.date.today())
        else:
            date_input = st.text_input("Period", placeholder="e.g., 2025", value="2025")
    
    if report_type == "Training Sheet":
        topic = st.text_input("Topic", placeholder="Enter training topic", value="HR Compliance")
    
    if st.button("📋 Generate Report", use_container_width=True):
        try:
            with st.spinner("⏳ Generating report..."):
                if report_type == "CNAS Audit Report":
                    report = generate_cnas_report(client_name, date_input, client)
                elif report_type == "HR Compliance Summary":
                    report = generate_hr_summary(client_name, date_input, client)
                else:
                    date_str = str(date_input) if not isinstance(date_input, str) else date_input
                    report = generate_training_sheet(topic, client_name, date_str, client)
                
                st.success("✅ Report Generated!")
                st.markdown("---")
                st.markdown(report)
                log_action("generate_report", f"Type: {report_type}", client)
                
                # PDF Download
                pdf_data = create_pdf(report, report_type)
                if pdf_data:
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_data,
                        file_name=f"{report_type.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
        
        except Exception as e:
            st.error(f"❌ Error generating report: {e}")
            log_action("report_error", str(e), client)

with tab3:
    st.subheader("📊 Analytics & Logs")
    
    if os.path.exists('audit_log.csv'):
        try:
            logs_df = pd.read_csv('audit_log.csv')
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Interactions", len(logs_df))
            with col2:
                st.metric("Chat Queries", len(logs_df[logs_df['action'] == 'chat_query']))
            with col3:
                st.metric("Reports Generated", len(logs_df[logs_df['action'] == 'generate_report']))
            with col4:
                st.metric("Errors", len(logs_df[logs_df['action'] == 'error']))
            
            st.divider()
            
            # Recent activity
            st.write("### Recent Activity")
            st.dataframe(
                logs_df[['timestamp', 'action', 'client', 'details']].tail(20),
                use_container_width=True,
                hide_index=True
            )
            
            # Download logs
            csv_data = logs_df.to_csv(index=False)
            st.download_button(
                label="📥 Download All Logs",
                data=csv_data,
                file_name=f"audit_logs_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error reading logs: {e}")
    else:
        st.info("📋 No activity logs yet. Start chatting or generating reports!")