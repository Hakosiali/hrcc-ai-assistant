import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF
import os
import csv
import datetime
import pandas as pd
import pdfplumber
from langdetect import detect, DetectorFactory
import re

DetectorFactory.seed = 0

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="HRCC AI Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Demo knowledge base - comprehensive Q&A
KNOWLEDGE_BASE = {
    "default": {
        "worker late for work": "When an employee is late for work in Algeria, the employer has several options according to the Labor Code:\n\n1. **First Offense**: Issue a written warning. The employer should document the tardiness and discuss with the employee.\n\n2. **Salary Deduction**: Employers can legally deduct 1/30 of the monthly salary for each day of absence. This is a common practice but must be applied fairly and consistently.\n\n3. **Repeated Violations**: After multiple warnings, employers can terminate employment for 'failure to comply with workplace discipline.' The employee must be given written notice.\n\n4. **Legitimate Reasons**: If an employee has a legitimate reason (medical, emergency), documentation should be provided.\n\n**Best Practice**: Have a clear attendance policy in writing, apply it consistently, and give warnings before taking termination action.",
        
        "employee rights algeria": "Employees in Algeria are protected by the Labor Code (Code du Travail) and have the following fundamental rights:\n\n✅ **Right to Fair Wages**: Minimum wage set by law, paid regularly and on time\n✅ **Working Hours**: Maximum 40 hours per week, cannot be exceeded without overtime compensation\n✅ **Annual Leave**: Minimum 18 days paid vacation per year\n✅ **Safe Working Conditions**: Employer must ensure workplace safety and health standards\n✅ **Union Membership**: Right to join unions and participate in collective bargaining\n✅ **Protection from Arbitrary Dismissal**: Cannot be fired without written justification and severance\n✅ **Non-Discrimination**: Protection from discrimination based on gender, race, religion, or political beliefs\n✅ **Written Contracts**: Right to have a formal employment contract in writing\n✅ **Medical Care**: Covered by social security (CNAS) for work-related injuries",
        
        "termination notice": "Employment termination in Algeria follows strict legal procedures:\n\n**Required Steps**:\n1. **Written Notice**: Employer must provide written termination notice with clear reason\n2. **Justified Cause**: Termination must be for a legitimate reason (misconduct, incompetence, restructuring)\n3. **Notice Period**: Typically 15-30 days depending on job level and contract terms\n4. **Severance Pay**: Employee entitled to severance of at least 1 month's salary, plus unused leave\n5. **Final Settlement**: All outstanding wages, bonuses, and benefits must be paid\n\n**If Terminated Without Cause**: Employee can claim wrongful dismissal and sue for damages.\n**Probation Period Exception**: During probation (first 3 months typically), notice period may be shorter.\n\n**Important**: Arbitrary dismissal is illegal and can result in employer liability.",
        
        "maternity leave": "Algerian law provides strong protection for pregnant workers and new mothers:\n\n✅ **Duration**: 14 weeks total maternity leave\n   - 6 weeks BEFORE expected delivery date\n   - 8 weeks AFTER delivery\n\n✅ **Full Salary**: Employee receives full salary during entire maternity leave period\n\n✅ **Job Protection**: Employer CANNOT terminate or punish a woman for taking maternity leave\n\n✅ **Additional Rights**:\n   - 1-hour nursing break per day for 12 months after return\n   - Cannot be assigned to dangerous work during pregnancy\n   - Medical exams paid by employer\n   - Miscarriage leave also covered\n\n✅ **Social Security**: Covered by CNAS (national health insurance)\n\n**Note**: These are minimum rights; some employers offer more generous terms.",
        
        "working hours": "Algerian labor law strictly regulates working hours:\n\n**Standard Working Week**:\n- Maximum 40 hours per week\n- Typically 8 hours per day, 5 days per week\n- Rest days must be provided (usually Friday-Saturday)\n\n**Night Shifts**:\n- Maximum 8 hours per night shift\n- Extra regulations for protection and compensation\n- Higher pay required (typically 50% bonus)\n\n**Overtime**:\n- Any hours beyond 40/week must be compensated at 50% higher rate\n- Employer cannot require unlimited overtime\n- Overtime must be documented and paid within same month\n\n**Break Times**:\n- Employees entitled to break periods during working day\n- Usually 1 hour lunch break for 8-hour shift\n\n**Compliance Note**: Exceeding these limits without proper compensation violates labor law.",
        
        "salary minimum": "Algerian minimum wage is set by government decree and is mandatory for all employers:\n\n**Key Points**:\n✅ Employers MUST pay at least the legal minimum wage\n✅ Wage must be paid in full, on time (typically monthly)\n✅ Salary must be documented in writing (payslip)\n\n**Legal Deductions**:\n- Income taxes (withholding)\n- Social security contributions (CNAS, CASNOS)\n- Court-ordered child support\n- Union dues (only if employee authorizes)\n\n**Illegal Deductions**:\n- Uniforms or tools (employer responsibility)\n- Disciplinary fines (not allowed)\n- Rent or accommodation costs\n- Arbitrary deductions\n\n**Payment Method**: Must be paid in cash, check, or bank transfer. Employer cannot deduct for administrative costs.",
        
        "sick leave": "Employees in Algeria are protected when they become ill:\n\n**Short-term Sick Leave (First 3 Days)**:\n- Employee takes leave due to illness\n- EMPLOYER pays 100% of salary\n- Medical certificate required (from doctor)\n- No limit on number of times\n\n**Extended Sick Leave (Beyond 3 Days)**:\n- CNAS (National Health Insurance) takes over payment\n- Employee receives 75-80% of salary from CNAS\n- Medical certificate required\n- Can last up to 6 months\n\n**Work-Related Illness**:\n- 100% covered by social security\n- Extended benefits apply\n\n**Important**:\n- Cannot be terminated for legitimate illness\n- Must provide medical documentation\n- Employer cannot harass employee for sick days",
        
        "dismissal": "Dismissal in Algeria is heavily regulated to protect workers:\n\n**Valid Reasons for Dismissal**:\n1. Serious misconduct (theft, violence, insubordination)\n2. Repeated poor performance despite warnings\n3. Repeated absences without justification\n4. Incompetence after training period\n5. Bankruptcy or permanent closure of business\n\n**Process**:\n1. Verbal warning (if possible)\n2. Written warning\n3. Final written notice of dismissal with reason\n4. At least 15-30 days notice\n5. Final payment of all wages and benefits\n\n**Prohibited Dismissals**:\n- Cannot fire based on gender, race, religion, politics\n- Cannot fire pregnant women or during maternity leave\n- Cannot fire union organizers\n- Cannot fire without proper justification\n\n**Consequences of Wrongful Dismissal**:\n- Rehiring with back pay\n- Damages for lost wages\n- Additional compensation\n- Legal fees",
    },
    
    "knowledge": {
        "droit du travail": "Le droit du travail algérien est régi par le Code du Travail de 1990 avec plusieurs modifications:\n\n**Principes Fondamentaux**:\n- Salaire minimum légal obligatoire\n- Durée maximale 40 heures par semaine\n- Congés payés minimum 18 jours annuels\n- Conditions de travail sûres et hygiéniques\n- Protection contre le licenciement arbitraire\n- Droit à la syndicalisation\n\n**Domaines Principaux**:\n1. Relations individuelles de travail (contrat, salaire, congés)\n2. Discipline et sanctions\n3. Sécurité et santé au travail\n4. Relations collectives (syndicats, conventions)\n5. Conditions particulières (femmes, jeunes, handicapés)",
        
        "licenciement": "Le licenciement en Algérie est fortement encadré par la loi:\n\n**Procédure Obligatoire**:\n1. Notification écrite avec motif justifié\n2. Délai de préavis: 15 à 30 jours selon le niveau\n3. Indemnité de licenciement minimale: 1 mois de salaire\n4. Paiement des congés non pris\n5. Certificat de travail\n\n**Motifs Valides**:\n- Faute grave (vol, violence, insubordination)\n- Incompétence malgré formation\n- Absences répétées injustifiées\n- Fermeture ou liquidation de l'entreprise\n\n**Licenciements Interdits**:\n- Licenciement de femmes enceintes\n- Licenciement pendant congé maternité\n- Licenciement pour activité syndicale\n- Licenciement discriminatoire\n\n**Recours**: L'employé peut contester devant les prud'hommes.",
        
        "prestations sociales": "L'employeur algérien doit assurer plusieurs cotisations obligatoires:\n\n**CNAS (Caisse Nationale de Sécurité Sociale)**:\n- Assurance maladie des salariés\n- Prestations familiales\n- Indemnités de maternité\n- Couverture des accidents du travail\n- Cotisation: pourcentage du salaire\n\n**CASNOS (Sécurité Sociale des Non-Salariés)**:\n- Pour les travailleurs indépendants\n- Cotisations mensuelles obligatoires\n\n**Assurance Chômage**:\n- Protection en cas de licenciement\n- Allocation chômage temporaire\n\n**Fonds de Garantie des Salaires**:\n- Protège les salaires non payés\n- En cas de faillite de l'employeur\n\n**Obligation Employeur**: Verser ces cotisations mensuellement, sinon amendes et sanctions.",
        
        "congé maternité": "Protection complète pour les femmes enceintes et nouvelles mères:\n\n**Durée du Congé**:\n- 6 semaines AVANT l'accouchement\n- 8 semaines APRÈS l'accouchement\n- Total: 14 semaines\n\n**Rémunération**:\n- Salaire INTÉGRAL pendant tout le congé\n- Payé par la CNAS (sécurité sociale)\n\n**Protections**:\n- Interdiction de licenciement pendant la grossesse\n- Interdiction de licenciement pendant le congé\n- Maintien du contrat de travail\n- Réintégration au même poste\n\n**Période d'Allaitement**:\n- 1 heure par jour de pause allaitement\n- Pendant 12 mois après le retour\n- Salarié et payé\n\n**Avantages Supplémentaires**:\n- Examens médicaux gratuits\n- Protection contre travail dangereux",
        
        "heures de travail": "La loi algérienne encadre strictement les horaires de travail:\n\n**Durée Légale**:\n- Maximum 40 heures par semaine (sauf accords collectifs)\n- Généralement 8 heures par jour\n- 5 jours de travail, 2 jours de repos\n\n**Travail de Nuit**:\n- Maximum 8 heures par nuit\n- Compensation supplémentaire de 50% minimum\n- Contrôles de santé réguliers\n- Interdiction pour certaines catégories\n\n**Heures Supplémentaires**:\n- Toute heure au-delà de 40/semaine\n- Compensation de 50% au minimum\n- Paiement dans le mois\n- Enregistrement obligatoire\n\n**Repos**:\n- Jours de repos hebdomadaires (généralement vendredi-samedi)\n- Congés payés annuels (minimum 18 jours)\n- Jours fériés\n\n**Non-Respect**: Amendes et responsabilité civile pour l'employeur.",
    },
    
    "simple": {
        "hello": "Welcome to HRCC AI Assistant! I'm here to help you with HR questions and Algerian labor law. You can ask me about employee rights, contracts, working conditions, or upload documents for detailed answers.",
        
        "help": "I can help with:\n- Employee rights and protections\n- Employment termination procedures\n- Working hours and overtime\n- Leave and vacation entitlements\n- Salary and payment issues\n- Maternity and medical leave\n- Workplace compliance\n- Document analysis (upload PDFs)\n\nWhat would you like to know?",
        
        "contact": "For detailed legal advice, please consult with an employment lawyer or your local labor department (Office de l'Emploi).",
    }
}

def detect_language(text):
    """Detect the language of the text"""
    try:
        lang = detect(text)
        return lang
    except:
        return "en"

def extract_relevant_context(text, question, max_context=2000):
    """Extract most relevant paragraphs from text"""
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Score sentences by relevance
    question_words = set(w.lower() for w in question.split() if len(w) > 3)
    
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        score = sum(1 for word in question_words if word in sentence.lower())
        if score > 0:
            scored_sentences.append((score, i, sentence))
    
    # Sort by relevance
    scored_sentences.sort(reverse=True)
    
    # Take top relevant sentences (preserve some order)
    if scored_sentences:
        top_sentences = sorted(scored_sentences[:5], key=lambda x: x[1])
        context = ". ".join([s[2] for s in top_sentences])
        return context[:max_context]
    return ""

def find_relevant_answers(question, knowledge_base):
    """Find ALL relevant answers from knowledge base, not just exact matches"""
    question_lower = question.lower().strip()
    question_words = set(w.lower() for w in question.split() if len(w) > 3)
    
    relevant_answers = []
    
    for key, answer in knowledge_base.items():
        key_lower = key.lower()
        key_words = set(w.lower() for w in key.split() if len(w) > 3)
        
        # Score based on word overlap
        score = len(question_words & key_words)
        
        # Add bonus for semantic similarity (e.g., "overtime pay" matches "working hours" section with overtime info)
        semantic_matches = {
            "overtime": ["pay", "compensation", "salary", "wage", "hours", "work"],
            "late": ["attendance", "absent", "tardiness", "warning"],
            "payment": ["salary", "wage", "compensation", "deduction"],
            "firing": ["dismissal", "termination", "firing"],
            "leave": ["vacation", "absent", "sick", "maternity"],
        }
        
        for keyword, related_words in semantic_matches.items():
            if keyword in question_lower:
                if any(word in key_lower for word in related_words):
                    score += 2
        
        if score > 0:
            relevant_answers.append((score, key, answer))
    
    # Sort by relevance
    relevant_answers.sort(reverse=True, key=lambda x: x[0])
    return relevant_answers

def combine_relevant_sections(relevant_answers, question):
    """Combine multiple relevant sections into a comprehensive answer"""
    if not relevant_answers:
        return ""
    
    # If we have very relevant matches (score >= 3), use them
    # Otherwise use the best match
    high_confidence = [a for a in relevant_answers if a[0] >= 3]
    to_use = high_confidence[:3] if high_confidence else relevant_answers[:2]
    
    combined = "\n\n".join([answer for _, _, answer in to_use])
    return combined

def get_ai_response(question, knowledge_base, uploaded_text=""):
    """Intelligent response system with logic and reasoning"""
    question_lower = question.lower().strip()
    question_lang = detect_language(question)
    
    response = ""
    source = ""
    
    # PRIORITY 1: Check uploaded documents first (most specific)
    if uploaded_text and len(uploaded_text) > 100:
        context = extract_relevant_context(uploaded_text, question)
        if context and len(context) > 50:
            response = f"{context}"
            source = "📄 **Source: Uploaded PDF Document**"
            
            # Add interpretation
            if any(word in question_lower for word in ["explain", "what", "how", "why", "detail", "tell", "describe"]):
                response = f"Based on your document:\n\n{response}\n\n**Note:** This information is from your uploaded document."
    
    # PRIORITY 2: Use intelligent matching on knowledge base
    if not response:
        relevant_answers = find_relevant_answers(question, knowledge_base)
        
        if relevant_answers:
            # Combine all relevant sections
            response = combine_relevant_sections(relevant_answers, question)
            source = "📚 **Source: HR Knowledge Base**"
    
    # Format response based on question type
    if response:
        if any(word in question_lower for word in ["explain", "how", "why", "detail", "tell", "describe", "what"]):
            response = f"**Explanation:**\n\n{response}\n\n"
        elif any(word in question_lower for word in ["summary", "brief", "short"]):
            response = f"**Summary:**\n\n{response}\n\n"
        else:
            response = f"**Answer:**\n\n{response}\n\n"
        
        return f"{response}\n\n{source}"
    
    # Default response with helpful suggestions
    suggestions = "**Employee rights, Overtime, Termination, Work hours, Leave, Salary, Dismissal, Maternity, Sick leave, Attendance, Deductions**"
    if question_lang in ["fr", "ar"]:
        return f"Je n'ai pas trouvé de réponse précise. Essayez de poser des questions sur: {suggestions}\n\nVous pouvez également télécharger des documents PDF pour des réponses plus détaillées."
    else:
        return f"I couldn't find a specific answer for that. Try asking about: {suggestions}\n\nYou can also upload PDF documents for more detailed answers."

def extract_pdf_text(pdf_file):
    """Extract text from uploaded PDF"""
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

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
if 'uploaded_text' not in st.session_state:
    st.session_state.uploaded_text = ""

# Main UI
st.title("⚖️ HRCC AI Assistant")
st.caption("Algerian Labor Law & HR Compliance Assistant")

# Sidebar configuration
with st.sidebar:
    client = st.selectbox(
        "Profile",
        ["default", "knowledge", "simple"],
        help="Choose knowledge base language/style"
    )
    
    st.divider()
    if st.button("🧹 Clear conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Main tabs
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📄 Reports", "📊 Analytics"])

with tab1:
    # Get knowledge base for selected client
    kb = KNOWLEDGE_BASE.get(client, KNOWLEDGE_BASE["default"])
    
    # PDF Upload in expander (secondary action)
    with st.expander("📎 Upload document for context (optional)"):
        uploaded_pdf = st.file_uploader("PDF only", type=["pdf"], label_visibility="collapsed")
        
        if uploaded_pdf:
            with st.spinner("📖 Extracting text from PDF..."):
                extracted_text = extract_pdf_text(uploaded_pdf)
                st.session_state.uploaded_text = extracted_text
                st.success(f"✅ Loaded: {uploaded_pdf.name}")
    
    # Clear document button
    if st.session_state.uploaded_text:
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("🗑️ Clear", key="clear_doc"):
                st.session_state.uploaded_text = ""
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display chat history
    if not st.session_state.chat_history:
        with st.chat_message("assistant"):
            st.markdown(
                "Ask me anything about **Algerian labor law, HR compliance, contracts, or employee rights**. "
                "You can also upload PDF documents for detailed answers."
            )
    
    # Show last 6 messages
    for msg in st.session_state.chat_history[-6:]:
        with st.chat_message("user"):
            st.markdown(msg["question"])
        with st.chat_message("assistant"):
            st.markdown(msg["answer"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Chat input (modern ChatGPT-style)
    question = st.chat_input("Ask a legal or HR question…")
    
    if question:
        try:
            # Show user message immediately
            with st.chat_message("user"):
                st.markdown(question)
            
            # Get response
            response_text = get_ai_response(question, kb, st.session_state.uploaded_text)
            
            # Show assistant response
            with st.chat_message("assistant"):
                st.markdown(response_text)
            
            # Add to history
            st.session_state.chat_history.append({
                "question": question,
                "answer": response_text
            })
            log_action("chat_query", f"Q: {question[:50]}", client)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            log_action("error", f"Query error: {str(e)}", client)

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
