#!/usr/bin/env python3
"""
Block Business Banking Financial Model
Strategic Finance Analysis Tool for Instant Transfer, Credit Card, and Debit Card products
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class BusinessBankingModel:
    def __init__(self):
        self.scenarios = {}
        self.base_assumptions = self._load_base_assumptions()
    
    def _load_base_assumptions(self):
        """Load base case assumptions for financial modeling"""
        return {
            'instant_transfer': {
                'avg_transaction_value': 5000,  # Average business transfer amount
                'monthly_transactions_per_customer': 12,
                'fee_rate': 0.015,  # 1.5% fee
                'flat_fee': 2.50,
                'processing_cost_rate': 0.003,  # 0.3% processing cost
                'fixed_cost_per_transaction': 0.25,
                'customer_acquisition_cost': 150,
                'monthly_churn_rate': 0.02
            },
            'credit_card': {
                'avg_monthly_spend': 8000,  # Per business customer
                'interchange_rate': 0.022,  # 2.2% average interchange
                'annual_fee': 95,
                'interest_rate': 0.18,  # 18% APR
                'charge_off_rate': 0.025,  # 2.5% annual charge-off
                'processing_cost_rate': 0.005,
                'customer_acquisition_cost': 200,
                'monthly_churn_rate': 0.015
            },
            'debit_card': {
                'avg_monthly_spend': 12000,  # Higher frequency, lower margin
                'interchange_rate': 0.008,  # 0.8% debit interchange
                'monthly_fee': 5.00,
                'atm_fee': 2.50,
                'atm_transactions_per_month': 3,
                'processing_cost_rate': 0.002,
                'customer_acquisition_cost': 75,
                'monthly_churn_rate': 0.01
            }
        }
    
    def calculate_instant_transfer_metrics(self, assumptions, customer_count, months=12):
        """Calculate financial metrics for Instant Transfer product"""
        results = {}
        
        # Monthly calculations
        monthly_transactions = customer_count * assumptions['monthly_transactions_per_customer']
        monthly_transaction_value = monthly_transactions * assumptions['avg_transaction_value']
        
        # Revenue calculation
        percentage_revenue = monthly_transaction_value * assumptions['fee_rate']
        flat_fee_revenue = monthly_transactions * assumptions['flat_fee']
        monthly_revenue = percentage_revenue + flat_fee_revenue
        
        # Cost calculation
        processing_costs = monthly_transaction_value * assumptions['processing_cost_rate']
        fixed_costs = monthly_transactions * assumptions['fixed_cost_per_transaction']
        monthly_costs = processing_costs + fixed_costs
        
        # Unit economics
        revenue_per_transaction = monthly_revenue / monthly_transactions
        cost_per_transaction = monthly_costs / monthly_transactions
        margin_per_transaction = revenue_per_transaction - cost_per_transaction
        
        results = {
            'monthly_transactions': monthly_transactions,
            'monthly_transaction_value': monthly_transaction_value,
            'monthly_revenue': monthly_revenue,
            'monthly_costs': monthly_costs,
            'monthly_profit': monthly_revenue - monthly_costs,
            'revenue_per_transaction': revenue_per_transaction,
            'cost_per_transaction': cost_per_transaction,
            'margin_per_transaction': margin_per_transaction,
            'take_rate': monthly_revenue / monthly_transaction_value,
            'annual_revenue': monthly_revenue * 12,
            'annual_profit': (monthly_revenue - monthly_costs) * 12
        }
        
        return results
    
    def calculate_credit_card_metrics(self, assumptions, customer_count, months=12):
        """Calculate financial metrics for Credit Card product"""
        results = {}
        
        # Monthly spend and revenue
        monthly_spend = customer_count * assumptions['avg_monthly_spend']
        interchange_revenue = monthly_spend * assumptions['interchange_rate']
        annual_fee_revenue = (customer_count * assumptions['annual_fee']) / 12
        
        # Interest revenue (assume 30% of customers carry balance)
        avg_balance = monthly_spend * 0.3 * 2  # 30% carry 2x monthly spend
        interest_revenue = avg_balance * (assumptions['interest_rate'] / 12)
        
        monthly_revenue = interchange_revenue + annual_fee_revenue + interest_revenue
        
        # Costs
        processing_costs = monthly_spend * assumptions['processing_cost_rate']
        charge_off_costs = avg_balance * (assumptions['charge_off_rate'] / 12)
        monthly_costs = processing_costs + charge_off_costs
        
        results = {
            'monthly_spend': monthly_spend,
            'interchange_revenue': interchange_revenue,
            'annual_fee_revenue': annual_fee_revenue,
            'interest_revenue': interest_revenue,
            'monthly_revenue': monthly_revenue,
            'monthly_costs': monthly_costs,
            'monthly_profit': monthly_revenue - monthly_costs,
            'revenue_per_customer': monthly_revenue / customer_count,
            'cost_per_customer': monthly_costs / customer_count,
            'annual_revenue': monthly_revenue * 12,
            'annual_profit': (monthly_revenue - monthly_costs) * 12
        }
        
        return results
    
    def calculate_debit_card_metrics(self, assumptions, customer_count, months=12):
        """Calculate financial metrics for Debit Card product"""
        results = {}
        
        # Monthly spend and transactions
        monthly_spend = customer_count * assumptions['avg_monthly_spend']
        interchange_revenue = monthly_spend * assumptions['interchange_rate']
        monthly_fee_revenue = customer_count * assumptions['monthly_fee']
        atm_revenue = customer_count * assumptions['atm_transactions_per_month'] * assumptions['atm_fee']
        
        monthly_revenue = interchange_revenue + monthly_fee_revenue + atm_revenue
        
        # Costs
        processing_costs = monthly_spend * assumptions['processing_cost_rate']
        monthly_costs = processing_costs
        
        results = {
            'monthly_spend': monthly_spend,
            'interchange_revenue': interchange_revenue,
            'monthly_fee_revenue': monthly_fee_revenue,
            'atm_revenue': atm_revenue,
            'monthly_revenue': monthly_revenue,
            'monthly_costs': monthly_costs,
            'monthly_profit': monthly_revenue - monthly_costs,
            'revenue_per_customer': monthly_revenue / customer_count,
            'cost_per_customer': monthly_costs / customer_count,
            'annual_revenue': monthly_revenue * 12,
            'annual_profit': (monthly_revenue - monthly_costs) * 12
        }
        
        return results
    
    def run_scenario_analysis(self, product, customer_counts, scenario_name="base"):
        """Run scenario analysis for a given product"""
        assumptions = self.base_assumptions[product]
        results = []
        
        for count in customer_counts:
            if product == 'instant_transfer':
                metrics = self.calculate_instant_transfer_metrics(assumptions, count)
            elif product == 'credit_card':
                metrics = self.calculate_credit_card_metrics(assumptions, count)
            elif product == 'debit_card':
                metrics = self.calculate_debit_card_metrics(assumptions, count)
            
            metrics['customer_count'] = count
            results.append(metrics)
        
        return pd.DataFrame(results)
    
    def generate_summary_report(self, customer_count=10000):
        """Generate a comprehensive summary report for all products"""
        print(f"\n=== BLOCK BUSINESS BANKING FINANCIAL ANALYSIS ===")
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"Customer Base: {customer_count:,} customers per product")
        print("="*60)
        
        products = ['instant_transfer', 'credit_card', 'debit_card']
        summary_data = []
        
        for product in products:
            assumptions = self.base_assumptions[product]
            
            if product == 'instant_transfer':
                metrics = self.calculate_instant_transfer_metrics(assumptions, customer_count)
                product_name = "Instant Transfer"
            elif product == 'credit_card':
                metrics = self.calculate_credit_card_metrics(assumptions, customer_count)
                product_name = "Credit Card"
            elif product == 'debit_card':
                metrics = self.calculate_debit_card_metrics(assumptions, customer_count)
                product_name = "Debit Card"
            
            print(f"\n{product_name.upper()}")
            print("-" * 30)
            print(f"Annual Revenue: ${metrics['annual_revenue']:,.0f}")
            print(f"Annual Profit:  ${metrics['annual_profit']:,.0f}")
            print(f"Monthly Revenue per Customer: ${metrics['revenue_per_customer']:.2f}")
            
            if product == 'instant_transfer':
                print(f"Take Rate: {metrics['take_rate']:.2%}")
                print(f"Margin per Transaction: ${metrics['margin_per_transaction']:.2f}")
            
            summary_data.append({
                'Product': product_name,
                'Annual Revenue': metrics['annual_revenue'],
                'Annual Profit': metrics['annual_profit'],
                'Monthly Revenue per Customer': metrics['revenue_per_customer'],
                'Profit Margin': metrics['annual_profit'] / metrics['annual_revenue']
            })
        
        # Portfolio summary
        total_revenue = sum([item['Annual Revenue'] for item in summary_data])
        total_profit = sum([item['Annual Profit'] for item in summary_data])
        
        print(f"\n{'PORTFOLIO SUMMARY'}")
        print("-" * 30)
        print(f"Total Annual Revenue: ${total_revenue:,.0f}")
        print(f"Total Annual Profit:  ${total_profit:,.0f}")
        print(f"Portfolio Profit Margin: {total_profit/total_revenue:.1%}")
        
        return pd.DataFrame(summary_data)

# Example usage and analysis
if __name__ == "__main__":
    model = BusinessBankingModel()
    
    # Generate base case analysis
    summary = model.generate_summary_report(customer_count=10000)
    
    # Scenario analysis for different customer counts
    customer_scenarios = [1000, 5000, 10000, 25000, 50000]
    
    print(f"\n\n=== SCENARIO ANALYSIS ===")
    for product in ['instant_transfer', 'credit_card', 'debit_card']:
        print(f"\n{product.replace('_', ' ').title()} Scaling Analysis:")
        scenario_df = model.run_scenario_analysis(product, customer_scenarios)
        print(scenario_df[['customer_count', 'annual_revenue', 'annual_profit', 'revenue_per_customer']].to_string(index=False))
