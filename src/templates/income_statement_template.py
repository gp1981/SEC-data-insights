from typing import Dict, Any, List

class IncomeStatementTemplate:
    """Template for standardizing income statement data"""
    
    def __init__(self):
        self.revenues = {
            'net_sales': [],
            'other_revenue': []
        }
        
        self.costs_and_expenses = {
            'cost_of_goods_sold': [],
            'operating_expenses': {
                'selling_general_admin': [],
                'research_development': [],
                'depreciation_amortization': [],
                'other_operating_expenses': []
            }
        }
        
        self.other_income_expense = {
            'interest_income': [],
            'interest_expense': [],
            'other_non_operating_income': [],
            'other_non_operating_expense': []
        }
        
        self.income_taxes = {
            'current_tax_expense': [],
            'deferred_tax_expense': []
        }
        
        # Key metrics
        self.gross_profit = []
        self.operating_income = []
        self.income_before_tax = []
        self.net_income = []
        self.earnings_per_share = {
            'basic': [],
            'diluted': []
        }
        
        # Mapping of SEC taxonomy concepts to template fields
        self.concept_map = {
            'Revenues': ['revenues'],
            'SalesRevenueNet': ['revenues', 'net_sales'],
            'OtherRevenue': ['revenues', 'other_revenue'],
            
            'CostOfGoodsAndServicesSold': ['costs_and_expenses', 'cost_of_goods_sold'],
            'SellingGeneralAndAdministrativeExpense': ['costs_and_expenses', 'operating_expenses', 'selling_general_admin'],
            'ResearchAndDevelopmentExpense': ['costs_and_expenses', 'operating_expenses', 'research_development'],
            'DepreciationAndAmortization': ['costs_and_expenses', 'operating_expenses', 'depreciation_amortization'],
            'OtherOperatingExpenses': ['costs_and_expenses', 'operating_expenses', 'other_operating_expenses'],
            
            'InterestIncome': ['other_income_expense', 'interest_income'],
            'InterestExpense': ['other_income_expense', 'interest_expense'],
            'OtherNonoperatingIncomeExpense': ['other_income_expense', 'other_non_operating_income'],
            
            'IncomeTaxExpenseBenefit': ['income_taxes'],
            'CurrentIncomeTaxExpense': ['income_taxes', 'current_tax_expense'],
            'DeferredIncomeTaxExpense': ['income_taxes', 'deferred_tax_expense'],
            
            'GrossProfit': ['gross_profit'],
            'OperatingIncomeLoss': ['operating_income'],
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest': ['income_before_tax'],
            'NetIncomeLoss': ['net_income'],
            'EarningsPerShareBasic': ['earnings_per_share', 'basic'],
            'EarningsPerShareDiluted': ['earnings_per_share', 'diluted']
        }
    
    def get_path_for_concept(self, concept: str) -> List[str]:
        """Get the template path for a given SEC concept
        
        Args:
            concept: The SEC taxonomy concept name
            
        Returns:
            List of keys representing the path in the template
        """
        return self.concept_map.get(concept, [])