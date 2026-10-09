import streamlit as st
from tax_calculator import TaxCalculator

st.set_page_config(page_title="2025 Federal Tax Calculator", page_icon="🧮", layout="centered")

st.title("2025 Federal Income Tax Calculator")
st.caption("Educational estimate only — not a verified federal tax return.")

with st.form("tax_form"):
    st.subheader("Filing information")
    filing_status = st.selectbox(
        "Filing status",
        options=["single", "married"],
        format_func=lambda status: "Single" if status == "single" else "Married filing jointly",
    )
    withheld = st.number_input("Federal income tax withheld ($)", min_value=0.0, value=10000.0, step=100.0)

    st.subheader("Income")
    w2 = st.number_input("W-2 wages ($)", min_value=0.0, value=30000.0, step=100.0)
    interest = st.number_input("Taxable interest ($)", min_value=0.0, value=0.0, step=100.0)
    capital_gains_st = st.number_input("Short-term capital gains ($)", min_value=0.0, value=0.0, step=100.0)
    st.caption("Long-term capital gains are not included in the current calculator.")

    st.subheader("Above-the-line deductions")
    ira = st.number_input("Deductible traditional IRA contribution ($)", min_value=0.0, value=0.0, step=100.0)
    hsa = st.number_input("Deductible HSA contribution ($)", min_value=0.0, value=0.0, step=100.0)
    st.caption("The calculator assumes entered IRA and HSA amounts are deductible.")

    st.subheader("Tax credits")
    college_status = st.checkbox("Eligible for American Opportunity Tax Credit (AOTC)")
    education_expenses = st.number_input("Qualified education expenses ($)", min_value=0.0, value=0.0, step=100.0)
    children = st.number_input("Qualifying children under age 17", min_value=0, value=0, step=1)
    other_dependents = st.number_input("Other qualifying dependents", min_value=0, value=0, step=1)
    st.caption("Credit eligibility, refundability, and IRS worksheet limitations are not fully verified by this calculator.")

    submitted = st.form_submit_button("Calculate taxes", type="primary", use_container_width=True)

if submitted:
    info = {
        "filing status": filing_status,
        "amount withheld": withheld,
        "tax year": 2025,
    }
    income = {
        "W2": w2,
        "Interest": interest,
        "Capital Gains ST": capital_gains_st,
    }
    deduction = {
        "Traditional IRA": ira,
        "HSA": hsa,
    }
    credits = {
        "education_expenses": education_expenses,
        "college status": college_status,
        "children_under_17": children,
        "other dependants": other_dependents,
    }

    try:
        result = TaxCalculator(info, income, deduction, credits).calculate()
    except Exception as exc:
        st.error("The calculator could not complete the estimate. Check your calculator code and inputs.")
        st.exception(exc)
    else:
        st.divider()
        st.subheader("Estimated results")
        refund_col, due_col = st.columns(2)
        refund_col.metric("Estimated refund", f"${result['refund']:,.2f}")
        due_col.metric("Additional tax due", f"${result['tax_due']:,.2f}")

        st.subheader("Tax breakdown")
        rows = [
            ("Gross income", result["gross_income"]),
            ("Adjusted gross income", result["agi"]),
            ("Taxable income", result["taxable_income"]),
            ("Tax before credits", result["tax"]),
            ("Federal withholding", result["withheld"]),
        ]
        for label, amount in rows:
            st.write(f"**{label}:** ${amount:,.2f}")
        st.write(f"**Potential credits:** {result['credits']}")

        if result["taxable_income"] < 0:
            st.warning("Your calculator returned negative taxable income. In tax_calculate(), use max(0, self.agi - self.standard).")
        st.info(
            "This is an educational estimate. The current tax engine does not fully implement "
            "IRS Tax Table requirements, credit eligibility and ordering, or every tax adjustment. "
            "Do not rely on this estimate to file a tax return."
        )
