from typing import Dict, Any, List

class CashFlowTemplate:
    """Template for standardizing cash flow statement data"""
    
    def __init__(self):
        self.operating_activities = {
            'net_income': [],
            'adjustments': {
                'depreciation_amortization': [],
                'stock_based_compensation': [],
                'deferred_taxes': [],
                'asset_impairment': [],
                'gain_loss_on_sale': [],
                'other_adjustments': []
            },
            'changes_in_working_capital': {
                'accounts_receivable': [],
                'inventory': [],
                'accounts_payable': [],
                'accrued_liabilities': [],
                'other_working_capital': []
            }
        }
        
        self.investing_activities = {
            'capital_expenditures': [],
            'acquisitions': [],
            'purchases_of_investments': [],
            'sales_of_investments': [],
            'other_investing_activities': []
        }
        
        self.financing_activities = {
            'debt_issuance': [],
            'debt_repayment': [],
            'stock_issuance': [],
            'stock_repurchase': [],
            'dividends_paid': [],
            'other_financing_activities': []
        }
        
        # Key metrics
        self.net_cash_operating = []
        self.net_cash_investing = []
        self.net_cash_financing = []
        self.net_change_in_cash = []
        self.cash_beginning_period = []
        self.cash_end_period = []
        
        # Mapping of SEC taxonomy concepts to template fields
        self.concept_map = {
            'NetIncomeLoss': ['operating_activities', 'net_income'],
            'DepreciationDepletionAndAmortization': ['operating_activities', 'adjustments', 'depreciation_amortization'],
            'ShareBasedCompensation': ['operating_activities', 'adjustments', 'stock_based_compensation'],
            'DeferredIncomeTaxExpenseBenefit': ['operating_activities', 'adjustments', 'deferred_taxes'],
            'AssetImpairmentCharges': ['operating_activities', 'adjustments', 'asset_impairment'],
            'GainLossOnSaleOfBusinessAssets': ['operating_activities', 'adjustments', 'gain_loss_on_sale'],
            
            'IncreaseDecreaseInAccountsReceivable': ['operating_activities', 'changes_in_working_capital', 'accounts_receivable'],
            'IncreaseDecreaseInInventories': ['operating_activities', 'changes_in_working_capital', 'inventory'],
            'IncreaseDecreaseInAccountsPayable': ['operating_activities', 'changes_in_working_capital', 'accounts_payable'],
            'IncreaseDecreaseInAccruedLiabilities': ['operating_activities', 'changes_in_working_capital', 'accrued_liabilities'],
            
            'PaymentsToAcquirePropertyPlantAndEquipment': ['investing_activities', 'capital_expenditures'],
            'PaymentsToAcquireBusinessesNetOfCashAcquired': ['investing_activities', 'acquisitions'],
            'PaymentsToAcquireInvestments': ['investing_activities', 'purchases_of_investments'],
            'ProceedsFromSaleAndMaturityOfInvestments': ['investing_activities', 'sales_of_investments'],
            
            'ProceedsFromIssuanceOfDebt': ['financing_activities', 'debt_issuance'],
            'RepaymentsOfDebt': ['financing_activities', 'debt_repayment'],
            'ProceedsFromIssuanceOfCommonStock': ['financing_activities', 'stock_issuance'],
            'PaymentsForRepurchaseOfCommonStock': ['financing_activities', 'stock_repurchase'],
            'PaymentsOfDividends': ['financing_activities', 'dividends_paid'],
            
            'NetCashProvidedByUsedInOperatingActivities': ['net_cash_operating'],
            'NetCashProvidedByUsedInInvestingActivities': ['net_cash_investing'],
            'NetCashProvidedByUsedInFinancingActivities': ['net_cash_financing'],
            'CashAndCashEquivalentsPeriodIncreaseDecrease': ['net_change_in_cash'],
            'CashAndCashEquivalentsAtCarryingValuePeriodStart': ['cash_beginning_period'],
            'CashAndCashEquivalentsAtCarryingValuePeriodEnd': ['cash_end_period']
        }
    
    def get_path_for_concept(self, concept: str) -> List[str]:
        """Get the template path for a given SEC concept
        
        Args:
            concept: The SEC taxonomy concept name
            
        Returns:
            List of keys representing the path in the template
        """
        return self.concept_map.get(concept, [])