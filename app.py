import os
import io
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Page Configuration
st.set_page_config(
    page_title="Apex Payroll Pro - HR & Compensation Suite",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Theme & UI Polish
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #334155;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .main-title {
        color: #f8fafc;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .main-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 0.25rem;
    }
    
    .metric-container {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #38bdf8;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 0.4rem;
    }
    .metric-subtext {
        color: #10b981;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 0.2rem;
    }
    
    .paystub-card {
        background: #ffffff;
        color: #0f172a;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

DATA_FILE = os.path.join(os.path.dirname(__file__), "payroll_data.csv")

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Default fallback dataset
        data = {
            "emp_id": ["EMP-101", "EMP-102", "EMP-103", "EMP-104", "EMP-105", "EMP-106", "EMP-107", "EMP-108"],
            "name": ["Sarah Jenkins", "David Chen", "Elena Rodriguez", "Marcus Vance", "Aisha Patel", "James Wilson", "Linda Kim", "Robert Taylor"],
            "department": ["Engineering", "Engineering", "Design", "Human Resources", "Sales", "Marketing", "Finance", "Engineering"],
            "designation": ["Lead Software Engineer", "Senior Backend Developer", "Principal UI/UX Designer", "HR Business Partner", "Sales Account Executive", "Growth Marketing Lead", "Senior Financial Analyst", "DevOps Specialist"],
            "base_salary": [95000, 82000, 78000, 68000, 72000, 75000, 80000, 85000],
            "allowance": [12000, 10000, 8500, 7000, 15000, 9000, 9500, 11000],
            "tax_rate": [18.0, 15.0, 14.0, 12.0, 14.0, 14.0, 15.0, 16.0],
            "status": ["Active"] * 8,
            "payment_method": ["Direct Deposit"] * 8,
            "bank_account": ["****4821", "****9102", "****3341", "****7812", "****6619", "****2109", "****5490", "****8834"]
        }
        df = pd.DataFrame(data)
        df.to_csv(DATA_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def calculate_payroll(df, health_insurance=250, retirement_rate=5.0, bonus_multiplier=1.0):
    df_calc = df.copy()
    # Monthly calculations
    df_calc['gross_monthly'] = (df_calc['base_salary'] / 12.0) + (df_calc['allowance'] / 12.0) * bonus_multiplier
    df_calc['income_tax'] = df_calc['gross_monthly'] * (df_calc['tax_rate'] / 100.0)
    df_calc['health_insurance'] = health_insurance
    df_calc['retirement_fund'] = df_calc['gross_monthly'] * (retirement_rate / 100.0)
    df_calc['total_deductions'] = df_calc['income_tax'] + df_calc['health_insurance'] + df_calc['retirement_fund']
    df_calc['net_monthly'] = df_calc['gross_monthly'] - df_calc['total_deductions']
    return df_calc

def generate_pdf_paystub(emp_row, pay_period):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=15
    )
    bold_style = ParagraphStyle('BoldText', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10)

    elements = []
    
    # Header Banner
    elements.append(Paragraph("APEX ENTERPRISE PAYROLL STUB", title_style))
    elements.append(Paragraph(f"Official Statement for Period: <b>{pay_period}</b> | Generated Date: 2026-08-27", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3b82f6'), spaceAfter=15))
    
    # Employee Info Table
    emp_data = [
        [Paragraph("<b>Employee Name:</b>", styles['Normal']), Paragraph(str(emp_row['name']), styles['Normal']),
         Paragraph("<b>Employee ID:</b>", styles['Normal']), Paragraph(str(emp_row['emp_id']), styles['Normal'])],
        [Paragraph("<b>Department:</b>", styles['Normal']), Paragraph(str(emp_row['department']), styles['Normal']),
         Paragraph("<b>Designation:</b>", styles['Normal']), Paragraph(str(emp_row['designation']), styles['Normal'])],
        [Paragraph("<b>Payment Method:</b>", styles['Normal']), Paragraph(str(emp_row['payment_method']), styles['Normal']),
         Paragraph("<b>Bank Account:</b>", styles['Normal']), Paragraph(str(emp_row['bank_account']), styles['Normal'])],
    ]
    emp_table = Table(emp_data, colWidths=[110, 160, 110, 160])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(emp_table)
    elements.append(Spacer(1, 15))
    
    # Breakdown Table Header
    elements.append(Paragraph("<b>Compensation & Deductions Breakdown</b>", styles['Heading3']))
    elements.append(Spacer(1, 6))
    
    breakdown_data = [
        [Paragraph("<b>Earnings Category</b>", bold_style), Paragraph("<b>Amount ($)</b>", bold_style),
         Paragraph("<b>Deductions Category</b>", bold_style), Paragraph("<b>Amount ($)</b>", bold_style)],
        ["Base Salary (Monthly)", f"${emp_row['base_salary']/12:,.2f}", "Income Tax", f"${emp_row['income_tax']:,.2f}"],
        ["Allowances & Bonuses", f"${(emp_row['gross_monthly'] - emp_row['base_salary']/12):,.2f}", "Health Insurance", f"${emp_row['health_insurance']:,.2f}"],
        ["", "", "Retirement Fund (401k/PF)", f"${emp_row['retirement_fund']:,.2f}"],
        [Paragraph("<b>TOTAL GROSS PAY</b>", bold_style), Paragraph(f"<b>${emp_row['gross_monthly']:,.2f}</b>", bold_style),
         Paragraph("<b>TOTAL DEDUCTIONS</b>", bold_style), Paragraph(f"<b>${emp_row['total_deductions']:,.2f}</b>", bold_style)]
    ]
    
    bd_table = Table(breakdown_data, colWidths=[160, 110, 160, 110])
    bd_table.setStyle(TableStyle([
        ('HEADER', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f8fafc')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(bd_table)
    elements.append(Spacer(1, 20))
    
    # Net Pay Banner
    net_pay_data = [
        [Paragraph(f"<font size=12 color='#0f172a'><b>NET TAKE-HOME PAY:</b></font>", styles['Normal']),
         Paragraph(f"<font size=14 color='#16a34a'><b>${emp_row['net_monthly']:,.2f}</b></font>", styles['Normal'])]
    ]
    net_table = Table(net_pay_data, colWidths=[300, 240])
    net_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#dcfce7')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#22c55e')),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(net_table)
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("<i>This is a computer-generated document. No signature required. Apex Corp HR Department.</i>", subtitle_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# App Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">💼 APEX PAYROLL PRO</h1>
    <div class="main-subtitle">Enterprise Human Resources & Automated Compensation Management Suite</div>
</div>
""", unsafe_allow_html=True)

# Load state
df = load_data()

# Global Controls Sidebar
st.sidebar.markdown("### ⚙️ Payroll Run Settings")
pay_month = st.sidebar.selectbox("Pay Period Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], index=7)
pay_year = st.sidebar.selectbox("Pay Period Year", [2025, 2026, 2027], index=1)
pay_period_str = f"{pay_month} {pay_year}"

st.sidebar.markdown("---")
st.sidebar.markdown("### 📑 Benefit & Deduction Parameters")
health_ins_input = st.sidebar.number_input("Health Insurance ($/mo)", min_value=0.0, max_value=2000.0, value=250.0, step=25.0)
retire_rate_input = st.sidebar.slider("Retirement Fund Contribution (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.5)
bonus_mult_input = st.sidebar.slider("Allowance/Bonus Multiplier", min_value=0.5, max_value=3.0, value=1.0, step=0.1)

# Calculate current payroll dataset
df_calc = calculate_payroll(df, health_insurance=health_ins_input, retirement_rate=retire_rate_input, bonus_multiplier=bonus_mult_input)

# Main Navigation Tabs
tab_dash, tab_emp, tab_proc, tab_stub, tab_export = st.tabs([
    "📊 Executive Dashboard", 
    "👥 Employee Directory", 
    "💰 Payroll Processing", 
    "📄 Pay Stub Generator", 
    "📈 Audit & Export"
])

# ---------------------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# ---------------------------------------------------------
with tab_dash:
    st.subheader(f"Executive Summary - {pay_period_str}")
    
    c1, c2, c3, c4 = st.columns(4)
    total_gross = df_calc['gross_monthly'].sum()
    total_net = df_calc['net_monthly'].sum()
    total_deduct = df_calc['total_deductions'].sum()
    avg_salary = df_calc['base_salary'].mean()
    
    with c1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Total Monthly Payroll</div>
            <div class="metric-value">${total_gross:,.2f}</div>
            <div class="metric-subtext">Gross Monthly Expense</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Net Disbursement</div>
            <div class="metric-value" style="color:#10b981;">${total_net:,.2f}</div>
            <div class="metric-subtext">Direct Deposit Total</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Total Deductions</div>
            <div class="metric-value" style="color:#f43f5e;">${total_deduct:,.2f}</div>
            <div class="metric-subtext">Taxes, Insurance & 401k</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Total Active Headcount</div>
            <div class="metric-value" style="color:#a855f7;">{len(df_calc)}</div>
            <div class="metric-subtext">Avg Base Pay: ${avg_salary:,.0f}/yr</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.write("##### 🏢 Payroll Expenditure by Department")
        dept_summary = df_calc.groupby("department")["gross_monthly"].sum().reset_index()
        fig_donut = px.pie(
            dept_summary, 
            values="gross_monthly", 
            names="department", 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_donut.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#cbd5e1")
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col_g2:
        st.write("##### ⚖️ Gross Pay vs Net Take-Home by Employee")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=df_calc['name'], y=df_calc['gross_monthly'], name='Gross Monthly Pay', marker_color='#3b82f6'))
        fig_bar.add_trace(go.Bar(x=df_calc['name'], y=df_calc['net_monthly'], name='Net Take-Home Pay', marker_color='#10b981'))
        fig_bar.update_layout(
            barmode='group',
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#cbd5e1",
            margin=dict(t=20, b=20, l=20, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------------------------------------------
# TAB 2: EMPLOYEE DIRECTORY
# ---------------------------------------------------------
with tab_emp:
    st.subheader("👥 Employee Records & Compensation Directory")
    
    col_act1, col_act2 = st.columns([3, 1])
    with col_act1:
        search_term = st.text_input("🔍 Search by Employee Name or ID:", "")
    with col_act2:
        dept_filter = st.selectbox("Filter Department", ["All"] + list(df['department'].unique()))
        
    df_display = df.copy()
    if search_term:
        df_display = df_display[df_display['name'].str.contains(search_term, case=False) | df_display['emp_id'].str.contains(search_term, case=False)]
    if dept_filter != "All":
        df_display = df_display[df_display['department'] == dept_filter]
        
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("#### ➕ Add New Employee Record")
    with st.form("add_emp_form", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            new_id = st.text_input("Employee ID", f"EMP-{100 + len(df) + 1}")
            new_name = st.text_input("Full Name")
            new_dept = st.selectbox("Department", ["Engineering", "Sales", "Design", "Human Resources", "Marketing", "Finance", "Operations"])
        with f2:
            new_desig = st.text_input("Job Title / Designation")
            new_base = st.number_input("Annual Base Salary ($)", min_value=30000.0, value=75000.0, step=1000.0)
            new_allow = st.number_input("Annual Allowance ($)", min_value=0.0, value=8000.0, step=500.0)
        with f3:
            new_tax = st.number_input("Tax Rate (%)", min_value=0.0, max_value=50.0, value=15.0, step=0.5)
            new_pmt = st.selectbox("Payment Method", ["Direct Deposit", "Wire Transfer", "Check"])
            new_bank = st.text_input("Bank Account Last 4 Digits", "****1234")
            
        submitted = st.form_submit_button("Submit & Register Employee", use_container_width=True)
        if submitted:
            if not new_name or not new_desig:
                st.error("Please fill in Name and Designation fields.")
            else:
                new_row = {
                    "emp_id": new_id,
                    "name": new_name,
                    "department": new_dept,
                    "designation": new_desig,
                    "base_salary": new_base,
                    "allowance": new_allow,
                    "tax_rate": new_tax,
                    "status": "Active",
                    "payment_method": new_pmt,
                    "bank_account": new_bank
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success(f"Successfully registered {new_name} ({new_id})!")
                st.rerun()

# ---------------------------------------------------------
# TAB 3: PAYROLL PROCESSING
# ---------------------------------------------------------
with tab_proc:
    st.subheader(f"💰 Monthly Payroll Processing Table - {pay_period_str}")
    
    formatted_calc = df_calc.copy()
    formatted_calc['Monthly Base ($)'] = formatted_calc['base_salary'] / 12.0
    formatted_calc['Gross Pay ($)'] = formatted_calc['gross_monthly']
    formatted_calc['Tax ($)'] = formatted_calc['income_tax']
    formatted_calc['Health Ins ($)'] = formatted_calc['health_insurance']
    formatted_calc['Retirement ($)'] = formatted_calc['retirement_fund']
    formatted_calc['Total Deduct ($)'] = formatted_calc['total_deductions']
    formatted_calc['Net Pay ($)'] = formatted_calc['net_monthly']
    
    show_cols = ['emp_id', 'name', 'department', 'Monthly Base ($)', 'Gross Pay ($)', 'Tax ($)', 'Health Ins ($)', 'Retirement ($)', 'Total Deduct ($)', 'Net Pay ($)']
    
    st.dataframe(
        formatted_calc[show_cols].style.format({
            'Monthly Base ($)': '${:,.2f}',
            'Gross Pay ($)': '${:,.2f}',
            'Tax ($)': '${:,.2f}',
            'Health Ins ($)': '${:,.2f}',
            'Retirement ($)': '${:,.2f}',
            'Total Deduct ($)': '${:,.2f}',
            'Net Pay ($)': '${:,.2f}'
        }).background_gradient(subset=['Net Pay ($)'], cmap='Greens'),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    p_btn1, p_btn2 = st.columns([1, 4])
    with p_btn1:
        if st.button("🚀 Commit & Execute Payroll Run", type="primary"):
            st.balloons()
            st.success(f"Payroll run for {pay_period_str} committed! Total ${total_net:,.2f} disbursed across {len(df_calc)} accounts.")

# ---------------------------------------------------------
# TAB 4: PAY STUB GENERATOR
# ---------------------------------------------------------
with tab_stub:
    st.subheader("📄 Employee Pay Stub Generator & Download")
    
    selected_emp_name = st.selectbox("Select Employee for Pay Stub:", df_calc['name'].tolist())
    emp_row = df_calc[df_calc['name'] == selected_emp_name].iloc[0]
    
    st.markdown(f"""
    <div class="paystub-card">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 2px solid #e2e8f0; padding-bottom:1rem; margin-bottom:1rem;">
            <div>
                <h3 style="margin:0; color:#0f172a;">APEX ENTERPRISE PAY STUB</h3>
                <div style="color:#64748b; font-size:0.9rem;">Pay Period: {pay_period_str}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-weight:700; color:#3b82f6;">{emp_row['emp_id']}</div>
                <div style="color:#64748b; font-size:0.85rem;">Status: Paid</div>
            </div>
        </div>
        
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1.5rem; margin-bottom:1.5rem; background:#f8fafc; padding:1rem; border-radius:8px;">
            <div>
                <div><strong>Employee Name:</strong> {emp_row['name']}</div>
                <div><strong>Department:</strong> {emp_row['department']}</div>
                <div><strong>Designation:</strong> {emp_row['designation']}</div>
            </div>
            <div>
                <div><strong>Payment Method:</strong> {emp_row['payment_method']}</div>
                <div><strong>Account:</strong> {emp_row['bank_account']}</div>
                <div><strong>Tax Rate:</strong> {emp_row['tax_rate']}%</div>
            </div>
        </div>
        
        <table style="width:100%; border-collapse:collapse; margin-bottom:1.5rem;">
            <thead>
                <tr style="background:#f1f5f9; text-align:left; border-bottom:1px solid #cbd5e1;">
                    <th style="padding:8px;">Description</th>
                    <th style="padding:8px; text-align:right;">Earnings</th>
                    <th style="padding:8px; text-align:right;">Deductions</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:8px;">Base Monthly Salary</td>
                    <td style="padding:8px; text-align:right;">${emp_row['base_salary']/12:,.2f}</td>
                    <td style="padding:8px; text-align:right;">-</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:8px;">Allowances / Bonus</td>
                    <td style="padding:8px; text-align:right;">${(emp_row['gross_monthly'] - emp_row['base_salary']/12):,.2f}</td>
                    <td style="padding:8px; text-align:right;">-</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:8px;">Income Tax Withholding</td>
                    <td style="padding:8px; text-align:right;">-</td>
                    <td style="padding:8px; text-align:right;">${emp_row['income_tax']:,.2f}</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:8px;">Health Insurance Premium</td>
                    <td style="padding:8px; text-align:right;">-</td>
                    <td style="padding:8px; text-align:right;">${emp_row['health_insurance']:,.2f}</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:8px;">Retirement Fund (401k/PF)</td>
                    <td style="padding:8px; text-align:right;">-</td>
                    <td style="padding:8px; text-align:right;">${emp_row['retirement_fund']:,.2f}</td>
                </tr>
                <tr style="background:#f8fafc; font-weight:700;">
                    <td style="padding:8px;">SUBTOTALS</td>
                    <td style="padding:8px; text-align:right; color:#2563eb;">${emp_row['gross_monthly']:,.2f}</td>
                    <td style="padding:8px; text-align:right; color:#dc2626;">${emp_row['total_deductions']:,.2f}</td>
                </tr>
            </tbody>
        </table>
        
        <div style="background:#dcfce7; border:1.5px solid #22c55e; padding:1rem; border-radius:8px; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:1.1rem; font-weight:700; color:#15803d;">NET TAKE-HOME PAY DISBURSED:</span>
            <span style="font-size:1.4rem; font-weight:800; color:#166534;">${emp_row['net_monthly']:,.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(" ")
    pdf_bytes = generate_pdf_paystub(emp_row, pay_period_str)
    st.download_button(
        label=f"📥 Download Official PDF Pay Stub for {emp_row['name']}",
        data=pdf_bytes,
        file_name=f"Paystub_{emp_row['emp_id']}_{pay_month}_{pay_year}.pdf",
        mime="application/pdf",
        type="primary"
    )

# ---------------------------------------------------------
# TAB 5: AUDIT & EXPORT
# ---------------------------------------------------------
with tab_export:
    st.subheader("📈 Audit Logs & Data Export Capabilities")
    
    st.write("##### Processed Payroll Summary by Department")
    dept_audit = df_calc.groupby("department").agg(
        Headcount=('emp_id', 'count'),
        Total_Gross=('gross_monthly', 'sum'),
        Total_Taxes=('income_tax', 'sum'),
        Total_Net=('net_monthly', 'sum')
    ).reset_index()
    
    st.dataframe(dept_audit.style.format({
        'Total_Gross': '${:,.2f}',
        'Total_Taxes': '${:,.2f}',
        'Total_Net': '${:,.2f}'
    }), use_container_width=True)
    
    st.markdown("---")
    st.write("##### Export Options")
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        csv_data = df_calc.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Download Complete Payroll Run (CSV)",
            data=csv_data,
            file_name=f"Apex_Payroll_Export_{pay_month}_{pay_year}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_exp2:
        emp_csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="👥 Download Master Employee Roster (CSV)",
            data=emp_csv,
            file_name="Apex_Master_Employee_Roster.csv",
            mime="text/csv",
            use_container_width=True
        )
