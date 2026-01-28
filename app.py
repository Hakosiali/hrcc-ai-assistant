import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF
import os
import csv
import datetime
import pandas as pd

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="HRCC AI Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Demo knowledge base - simple Q&A system
KNOWLEDGE_BASE = {
    "default": {
        "worker late for work": "When an employee is late for work in Algeria, the employer can: 1) Issue a written warning, 2) Deduct 1/30 of monthly salary per day absent (per Labor Code), 3) Terminate after repeated violations. First offense requires warning.",
        "employee rights algeria": "Workers in Algeria have rights including: Minimum wage, 8-hour workday, annual leave (minimum 18 days), safe working conditions, union membership, and protection against arbitrary dismissal.",
        "termination notice": "In Algeria, employment termination requires: 1) Written notice, 2) Reason for termination, 3) Severance pay (1 month minimum), 4) Notice period varies by contract.",
        "maternity leave": "Female workers in Algeria are entitled to 14 weeks maternity leave: 6 weeks before and 8 weeks after birth, with full salary. Employer cannot terminate during this period.",
        "working hours": "Maximum working hours in Algeria are 40 hours per week. Night shifts limited to 8 hours. Overtime must be compensated with 50% bonus.",
        "salary minimum": "Minimum wage in Algeria is set by law. Employers must pay at least the legal minimum. Deductions only allowed for legal obligations and union dues.",
        "sick leave": "Employees are entitled to sick leave with medical certificate. First 3 days paid by employer. Beyond that covered by social security.",
        "dismissal": "Termination requires written justification. Arbitrary dismissal is prohibited. Employee has right to severance pay and notice period.",
    },
    "knowledge": {
        "droit du travail": "Le droit du travail algérien est régi par le Code du Travail de 1990. Les droits fondamentaux incluent: salaire minimum, 40h/semaine, congés payés (minimum 18 jours), conditions de travail sûres.",
        "licenciement": "La résiliation en Algérie nécessite: notification écrite, motif justifié, indemnité de licenciement (minimum 1 mois), délai de préavis respecté.",
        "prestations sociales": "L'employeur doit assurer: cotisations CNAS, CASNOS, assurance maladie, couverture accident du travail conformément à la législation algérienne.",
        "congé maternité": "Les femmes ont droit à 14 semaines de congé maternité: 6 avant et 8 après l'accouchement, avec salaire complet. L'employeur ne peut pas résilier pendant cette période.",
        "heures de travail": "La durée maximale est 40 heures par semaine en Algérie. Les heures supplémentaires doivent être compensées à 50% de majoration.",
    },
    "simple": {
        "hello": "Hello! Welcome to HRCC AI Assistant. I can help with HR questions and Algerian labor law.",
        "help": "I can help you with: Employee rights, Termination procedures, Work hours, Leave entitlements, Compliance issues.",
        "contact": "For more information, please contact our HR team or consult with an employment lawyer.",
    }
}

def get_ai_response(question, knowledge_base):
    """Simple keyword-based response system"""
    question_lower = question.lower().strip()
    
    # Check for exact matches in knowledge base
    for key, answer in knowledge_base.items():
        if key.lower() in question_lower:
            return f"**Answer:** {answer}\n\n📚 **Source:** HR Knowledge Base"
    
    # Check for partial matches (any word from key is in question)
    for key, answer in knowledge_base.items():
        key_words = [w for w in key.split() if len(w) > 3]
        if key_words and any(word in question_lower for word in key_words):
            return f"**Answer:** {answer}\n\n📚 **Source:** HR Knowledge Base"
    
    # Default response
    return "I couldn't find a specific answer in the knowledge base. Try asking about: **employee rights, termination, work hours, leave, salary, dismissal, maternity, or sick leave**."

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
    except:
        pass

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
        "Select Profile",
        ["default", "knowledge", "simple"],
        help="Choose knowledge base language/style"
    )
    
    st.divider()
    st.subheader("📖 About")
    st.markdown("""
    This AI assistant helps with:
    - 🏢 HR compliance
    - ⚖️ Algerian labor law
    - 📄 Report generation
    - 📊 Analytics
    """)
    
    st.divider()
    if st.button("🔄 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# Main tabs
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📄 Reports", "📊 Analytics"])

with tab1:
    st.subheader("Ask Legal/HR Questions")
    
    # Get knowledge base for selected client
    kb = KNOWLEDGE_BASE.get(client, KNOWLEDGE_BASE["default"])
    
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
        question = st.text_input("Enter your question:", placeholder="E.g., What happens when a worker is late?", key="question_input")
    with col2:
        submit_btn = st.button("🔍 Ask", use_container_width=True)
    
    if submit_btn and question:
        try:
            response_text = get_ai_response(question, kb)
            
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
    st.subheader("📄 Generate Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        client_name = st.text_input("Client Name", value="Demo Company")
        report_type = st.selectbox("Report Type", ["HR Summary", "Compliance Report", "Training Sheet"])
    
    with col2:
        period = st.text_input("Period", value="2025")
    
    if st.button("📋 Generate Report", use_container_width=True):
        try:
            # Generate sample report based on type
            if report_type == "HR Summary":
                report = f"""# HR Summary Report - {client_name}
**Period:** {period}

## Key Metrics
- Total Employees: 45
- Turnover Rate: 8%
- Compliance Score: 92%
- Training Hours: 240

## HR Compliance Status
✅ Labor Code Compliance: Compliant
✅ CNAS Contributions: Up to date
✅ Working Hours: 40h/week standard
✅ Leave Records: Properly maintained

## Recommendations
1. Maintain current compliance level
2. Continue employee training programs
3. Review contract templates quarterly
4. Update HR policies based on labor law changes
"""
            elif report_type == "Compliance Report":
                report = f"""# Compliance Report - {client_name}
**Period:** {period}

## Algerian Labor Code Compliance

### Working Hours
✅ Maximum 40 hours per week
✅ Overtime properly compensated (50% bonus)
✅ Rest periods maintained

### Employee Rights
✅ Minimum wage paid
✅ Annual leave: 18+ days
✅ Maternity leave: 14 weeks
✅ Union rights respected

### Social Contributions
✅ CNAS deductions: Current
✅ Insurance premiums: Paid
✅ Payroll taxes: Compliant

### Status: FULLY COMPLIANT ✅
"""
            else:
                report = f"""# Training Sheet - {client_name}
**Date:** {period}

## Training Content: HR & Labor Law

### Topics Covered
1. Algerian Labor Code Overview
2. Employee Rights & Obligations
3. Termination Procedures
4. Health & Safety Requirements
5. Social Security Systems

### Participants
- HR Department: 12 people
- Managers: 8 people
- Administrative Staff: 5 people

### Duration: 6 hours

### Materials Provided
- HR Handbook
- Labor Code Summary
- Policy Templates
- Compliance Checklist
"""
            
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
            st.error(f"❌ Error: {e}")
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
                logs_df[['timestamp', 'action', 'details']].tail(20),
                use_container_width=True,
                hide_index=True
            )
            
            # Download logs
            csv_data = logs_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Logs",
                data=csv_data,
                file_name=f"audit_logs_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error reading logs: {e}")
    else:
        st.info("📋 No activity logs yet. Start chatting or generating reports!")
