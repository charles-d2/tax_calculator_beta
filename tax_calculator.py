import math

class TaxCalculator:
    def __init__ (self, info, income, deduction, credits):
        self.info = info
        self.income = income
        self.deduction = deduction
        self.credits = credits
    
    def total_income(self):
        total = self.income["W2"]
        total += self.income["Interest"]
        total += self.income["Capital Gains ST"]
        self.gross_income = total
        return self.gross_income

    def total_deduction(self):
        if self.info["filing status"] == "married":
            self.standard = 31500
        else:
            self.standard = 15750
        
        self.above_line_deductions = self.deduction["Traditional IRA"] + self.deduction["HSA"]
        return self.above_line_deductions, self.standard

    def tax_calculate(self):
        self.tax = 0
        self.agi = self.gross_income - self.above_line_deductions
        self.taxable_income = max(0, self.agi - self.standard)
        adj_income = self.taxable_income
        if self.info["filing status"] == "married":
            if adj_income >= 751601:
                self.tax = (adj_income - 751600) * 0.37
                adj_income = 751600
            if adj_income >= 501051:
                self.tax += (adj_income - 501050) * 0.35
                adj_income = 501050
            if adj_income >= 394601:
                self.tax += (adj_income - 394600) * 0.32
                adj_income = 394600
            if adj_income >= 206701:
                self.tax += (adj_income - 206700) * 0.24
                adj_income = 206700
            if adj_income >= 96951:
                self.tax += (adj_income - 96950) * 0.22
                adj_income = 96950
            if adj_income >= 23851:
                self.tax += (adj_income - 23850) * 0.12
                adj_income = 23850
            if adj_income >= 0:
                self.tax += adj_income * 0.1
        else:
            if adj_income >= 626351:
                self.tax = (adj_income - 626350) * 0.37
                adj_income = 626350
            if adj_income >= 250526:
                self.tax += (adj_income - 250525) * 0.35
                adj_income = 250525
            if adj_income >= 197301:
                self.tax += (adj_income - 197300) * 0.32
                adj_income = 197300
            if adj_income >= 103351:
                self.tax += (adj_income - 103350) * 0.24
                adj_income = 103350
            if adj_income >= 48476:
                self.tax += (adj_income - 48475) * 0.22
                adj_income = 48475
            if adj_income >= 11926:
                self.tax += (adj_income - 11925) * 0.12
                adj_income = 11925
            if adj_income >= 0:
                self.tax += adj_income * 0.1
        self.tax_before_credits = self.tax
        return self.tax

    def total_credits(self):
        self.AOTC = 0
        self.child_credit = 0
        self.dependent_credit = 0

        # American Opportunity Tax Credit
        education_expenses = float(self.credits["education_expenses"])

        if self.credits["college status"] and education_expenses > 0:
            if education_expenses > 2000:
                self.AOTC = 2000 + 0.25 * min(education_expenses - 2000, 2000)
            else:
                self.AOTC = education_expenses

        # Child Tax Credit
        # 2025: $2,200 per qualifying child
        self.child_credit = 2200 * int(self.credits["children_under_17"])

        # Other Dependent Credit
        self.dependent_credit = 500 * int(self.credits["other dependants"])

        return self.AOTC, self.child_credit, self.dependent_credit

    def apply_deductions(self):
        agi = self.agi
        AOTC = self.AOTC
        child_credit = self.child_credit
        filing_status = self.info["filing status"]
        dependent_credit = self.dependent_credit
        tax = self.tax_before_credits
        withholding = self.info["amount withheld"]
        earned_income = self.income["W2"]
        children = int(self.credits["children_under_17"])

        # 1. AOTC Phaseout
        # Single: $80,000 - $90,000
        # Married: $160,000 - $180,000

        if filing_status == "married":
            lower, upper = 160000, 180000
        else:
            lower, upper = 80000, 90000

        phaseout = max(0, min(1, (upper - agi) / (upper - lower)))
        AOTC *= phaseout

        refundable_AOTC = AOTC * 0.4
        nonrefundable_AOTC = AOTC * 0.6

        # 2. Child Tax Credit and Other Dependent Credit Phaseout
        # Single: $200,000
        # Married: $400,000
        # Reduction: $50 per $1,000 above threshold

        credit = child_credit + dependent_credit

        if filing_status == "married":
            threshold = 400000
        else:
            threshold = 200000

        if agi > threshold:
            credit -= math.ceil((agi - threshold) / 1000) * 50

        credit = max(0, credit)

        # 3. Separate Child and Dependent Credits

        remaining_child_credit = min(child_credit, credit)
        remaining_dependent_credit = max(
            0, credit - remaining_child_credit
        )

        # 4. Apply Nonrefundable Credits
        # Apply CTC and ODC before AOTC

        nonrefundable_child_credit = min(tax, remaining_child_credit)
        tax -= nonrefundable_child_credit

        nonrefundable_dependent_credit = min(
            tax, remaining_dependent_credit
        )
        tax -= nonrefundable_dependent_credit

        # 5. Calculate Refundable Child Tax Credit
        # Total CTC: $2,200 per child
        # Maximum refundable ACTC: $1,700 per child

        unused_child_credit = max(
            0, remaining_child_credit - nonrefundable_child_credit
        )

        refundable_child_credit = min(
            unused_child_credit,
            1700 * children,
            max(0, (earned_income - 2500) * 0.15)
        )

        # 6. Apply Nonrefundable AOTC

        applied_AOTC = min(tax, nonrefundable_AOTC)
        tax -= applied_AOTC

        # 7. Apply Refundable Credits and Withholding

        tax -= refundable_child_credit
        tax -= refundable_AOTC
        tax -= withholding

        # 8. Calculate Final Refund or Tax Due

        self.refund = round(max(0, -tax), 2)
        self.tax_due = round(max(0, tax), 2)

        return self.tax_due, self.refund

    def calculate(self):
        self.total_income()
        self.total_deduction()
        self.tax_calculate()
        self.total_credits()
        self.apply_deductions()

        return {
            "gross_income": self.gross_income,
            "agi": self.agi,
            "taxable_income": self.taxable_income,
            "tax": self.tax_before_credits,
            "credits": f'child: {self.child_credit}, AOTC: {self.AOTC}',
            "withheld": self.info["amount withheld"],
            "tax_due": self.tax_due,
            "refund": self.refund
        }
   
info = {
    "filing status": "single",
    "amount withheld": 10000,
    "tax year": 2025
}
income = {
    "W2": 100000,
    "Interest": 1000,
    "Capital Gains ST": 2000
}
deduction = {
    "Traditional IRA": 100,
    "HSA": 100
}
credits = {
    "education_expenses": 1000,
    "college status": True,
    "children_under_17": 1,
    "other dependants": 1
}

tax_payer1 = TaxCalculator(info, income, deduction, credits)

print(tax_payer1.calculate())