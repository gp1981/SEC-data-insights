from typing import Dict, Any, List

class BalanceSheetTemplate:
    """Template for standardizing balance sheet data"""
    
    def __init__(self):
        self.assets = {
            'current_assets': {
                'cash_and_equivalents': [],
                'short_term_investments': [],
                'accounts_receivable': [],
                'inventory': [],
                'prepaid_expenses': [],
                'other_current_assets': []
            },
            'non_current_assets': {
                'long_term_investments': [],
                'property_plant_equipment': [],
                'intangible_assets': [],
                'goodwill': [],
                'other_non_current_assets': []
            }
        }
        
        self.liabilities = {
            'current_liabilities': {
                'accounts_payable': [],
                'short_term_debt': [],
                'accrued_expenses': [],
                'deferred_revenue': [],
                'other_current_liabilities': []
            },
            'non_current_liabilities': {
                'long_term_debt': [],
                'deferred_tax_liabilities': [],
                'pension_obligations': [],
                'other_non_current_liabilities': []
            }
        }
        
        self.equity = {
            'common_stock': [],
            'additional_paid_in_capital': [],
            'retained_earnings': [],
            'treasury_stock': [],
            'accumulated_other_comprehensive_income': [],
            'non_controlling_interest': []
        }
        
        # Mapping of SEC taxonomy concepts to template fields
        self.concept_map = {
            'Assets': ['assets'],
            'AssetsCurrent': ['assets', 'current_assets'],
            'CashAndCashEquivalentsAtCarryingValue': ['assets', 'current_assets', 'cash_and_equivalents'],
            'ShortTermInvestments': ['assets', 'current_assets', 'short_term_investments'],
            'AccountsReceivableNet': ['assets', 'current_assets', 'accounts_receivable'],
            'InventoryNet': ['assets', 'current_assets', 'inventory'],
            'PrepaidExpense': ['assets', 'current_assets', 'prepaid_expenses'],
            'OtherAssetsCurrent': ['assets', 'current_assets', 'other_current_assets'],
            
            'AssetsNoncurrent': ['assets', 'non_current_assets'],
            'LongTermInvestments': ['assets', 'non_current_assets', 'long_term_investments'],
            'PropertyPlantAndEquipmentNet': ['assets', 'non_current_assets', 'property_plant_equipment'],
            'IntangibleAssetsNet': ['assets', 'non_current_assets', 'intangible_assets'],
            'Goodwill': ['assets', 'non_current_assets', 'goodwill'],
            'OtherAssetsNoncurrent': ['assets', 'non_current_assets', 'other_non_current_assets'],
            
            'Liabilities': ['liabilities'],
            'LiabilitiesCurrent': ['liabilities', 'current_liabilities'],
            'AccountsPayableCurrent': ['liabilities', 'current_liabilities', 'accounts_payable'],
            'ShortTermBorrowings': ['liabilities', 'current_liabilities', 'short_term_debt'],
            'AccruedLiabilitiesCurrent': ['liabilities', 'current_liabilities', 'accrued_expenses'],
            'DeferredRevenueCurrent': ['liabilities', 'current_liabilities', 'deferred_revenue'],
            'OtherLiabilitiesCurrent': ['liabilities', 'current_liabilities', 'other_current_liabilities'],
            
            'LiabilitiesNoncurrent': ['liabilities', 'non_current_liabilities'],
            'LongTermDebt': ['liabilities', 'non_current_liabilities', 'long_term_debt'],
            'DeferredTaxLiabilitiesNoncurrent': ['liabilities', 'non_current_liabilities', 'deferred_tax_liabilities'],
            'PensionAndOtherPostretirementBenefitPlansLiabilities': ['liabilities', 'non_current_liabilities', 'pension_obligations'],
            'OtherLiabilitiesNoncurrent': ['liabilities', 'non_current_liabilities', 'other_non_current_liabilities'],
            
            'StockholdersEquity': ['equity'],
            'CommonStockValue': ['equity', 'common_stock'],
            'AdditionalPaidInCapital': ['equity', 'additional_paid_in_capital'],
            'RetainedEarningsAccumulatedDeficit': ['equity', 'retained_earnings'],
            'TreasuryStockValue': ['equity', 'treasury_stock'],
            'AccumulatedOtherComprehensiveIncomeLossNetOfTax': ['equity', 'accumulated_other_comprehensive_income'],
            'MinorityInterest': ['equity', 'non_controlling_interest']
        }
    
    def get_path_for_concept(self, concept: str) -> List[str]:
        """Get the template path for a given SEC concept
        
        Args:
            concept: The SEC taxonomy concept name
            
        Returns:
            List of keys representing the path in the template
        """
        return self.concept_map.get(concept, [])