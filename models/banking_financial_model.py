#!/usr/bin/env python3
"""
Block Business Banking Financial Model
Strategic Finance Analysis Tool for Instant Transfer, Credit Card, and Debit Card products

Live data is pulled from Snowflake via shared/snowflake_connector.py.
Hardcoded assumptions are used as fallbacks if Snowflake is unavailable.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Allow imports from the project root
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.snowflake_connector import query
from shared.sheets_connector import write_dataframe


class BusinessBankingModel:
    def __init__(self, use_live_data=True):
        self.use_live_data = use_live_data
        self.base_assumptions = self._load_assumptions()

    def _load_assumptions(self):
        """Load assumptions from Snowflake if available, otherwise use hardcoded defaults."""
        defaults = {
            'instant_transfer': {
                'avg_transaction_value': 5000,
                'monthly_transactions_per_customer': 12,
                'fee_rate': 0.015,
                'flat_fee': 2.50,
                'processing_cost_rate': 0.003,
                'fixed_cost_per_transaction': 0.25,
                'customer_acquisition_cost': 150,
                'monthly_churn_rate': 0.02
            },
            'credit_card': {
                'avg_monthly_spend': 8000,
                'interchange_rate': 0.022,
                'annual_fee': 95,
                'interest_rate': 0.18,
                'charge_off_rate': 0.025,
                'processing_cost_rate': 0.005,
                'customer_acquisition_cost': 200,
                'monthly_churn_rate': 0.015
            },
            'debit_card': {
                'avg_monthly_spend': 12000,
                'interchange_rate': 0.008,
                'monthly_fee': 5.00,
                'atm_fee': 2.50,
                'atm_transactions_per_month': 3,
                'processing_cost_rate': 0.002,
                'customer_acquisition_cost': 75,
                'monthly_churn_rate': 0.01
            }
        }

        if not self.use_live_data:
            return defaults

        try:
            print("Connecting to Snowflake...")

            it = query("""
                SELECT
                    AVG(transaction_amount)                  AS avg_transaction_value,
                    COUNT(*) / NULLIF(COUNT(DISTINCT customer_id), 0) AS monthly_transactions_per_customer
                FROM transactions
                WHERE product = 'instant_transfer'
                  AND DATE_TRUNC('month', transaction_date) = DATE_TRUNC('month', CURRENT_DATE)
            """).iloc[0]
            defaults['instant_transfer']['avg_transaction_value'] = float(it['AVG_TRANSACTION_VALUE'] or defaults['instant_transfer']['avg_transaction_value'])
            defaults['instant_transfer']['monthly_transactions_per_customer'] = float(it['MONTHLY_TRANSACTIONS_PER_CUSTOMER'] or defaults['instant_transfer']['monthly_transactions_per_customer'])

            cc = query("""
                SELECT AVG(monthly_spend) AS avg_monthly_spend
                FROM (
                    SELECT customer_id, SUM(transaction_amount) AS monthly_spend
                    FROM transactions
                    WHERE product = 'credit_card'
                      AND DATE_TRUNC('month', transaction_date) = DATE_TRUNC('month', CURRENT_DATE)
                    GROUP BY customer_id
                )
            """).iloc[0]
            defaults['credit_card']['avg_monthly_spend'] = float(cc['AVG_MONTHLY_SPEND'] or defaults['credit_card']['avg_monthly_spend'])

            dc = query("""
                SELECT AVG(monthly_spend) AS avg_monthly_spend
                FROM (
                    SELECT customer_id, SUM(transaction_amount) AS monthly_spend
                    FROM transactions
                    WHERE product = 'debit_card'
                      AND DATE_TRUNC('month', transaction_date) = DATE_TRUNC('month', CURRENT_DATE)
                    GROUP BY customer_id
                )
            """).iloc[0]
            defaults['debit_card']['avg_monthly_spend'] = float(dc['AVG_MONTHLY_SPEND'] or defaults['debit_card']['avg_monthly_spend'])

            print("Snowflake data loaded successfully.")

        except Exception as e:
            print(f"Snowflake unavailable, using hardcoded assumptions. ({e})")

        return defaults

    def calculate_instant_transfer_metrics(self, assumptions, customer_count):
        monthly_transactions = customer_count * assumptions['monthly_transactions_per_customer']
        monthly_transaction_value = monthly_transactions * assumptions['avg_transaction_value']

        percentage_revenue = monthly_transaction_value * assumptions['fee_rate']
        flat_fee_revenue = monthly_transactions * assumptions['flat_fee']
        monthly_revenue = percentage_revenue + flat_fee_revenue

        processing_costs = monthly_transaction_value * assumptions['processing_cost_rate']
        fixed_costs = monthly_transactions * assumptions['fixed_cost_per_transaction']
        monthly_costs = processing_costs + fixed_costs

        revenue_per_transaction = monthly_revenue / monthly_transactions
        cost_per_transaction = monthly_costs / monthly_transactions

        return {
            'monthly_transactions': monthly_transactions,
            'monthly_transaction_value': monthly_transaction_value,
            'monthly_revenue': monthly_revenue,
            'monthly_costs': monthly_costs,
            'monthly_profit': monthly_revenue - monthly_costs,
            'revenue_per_transaction': revenue_per_transaction,
            'cost_per_transaction': cost_per_transaction,
            'margin_per_transaction': revenue_per_transaction - cost_per_transaction,
            'take_rate': monthly_revenue / monthly_transaction_value,
            'revenue_per_customer': monthly_revenue / customer_count,
            'annual_revenue': monthly_revenue * 12,
            'annual_profit': (monthly_revenue - monthly_costs) * 12
        }

    def calculate_credit_card_metrics(self, assumptions, customer_count):
        monthly_spend = customer_count * assumptions['avg_monthly_spend']
        interchange_revenue = monthly_spend * assumptions['interchange_rate']
        annual_fee_revenue = (customer_count * assumptions['annual_fee']) / 12

        avg_balance = monthly_spend * 0.3 * 2
        interest_revenue = avg_balance * (assumptions['interest_rate'] / 12)
        monthly_revenue = interchange_revenue + annual_fee_revenue + interest_revenue

        processing_costs = monthly_spend * assumptions['processing_cost_rate']
        charge_off_costs = avg_balance * (assumptions['charge_off_rate'] / 12)
        monthly_costs = processing_costs + charge_off_costs

        return {
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

    def calculate_debit_card_metrics(self, assumptions, customer_count):
        monthly_spend = customer_count * assumptions['avg_monthly_spend']
        interchange_revenue = monthly_spend * assumptions['interchange_rate']
        monthly_fee_revenue = customer_count * assumptions['monthly_fee']
        atm_revenue = customer_count * assumptions['atm_transactions_per_month'] * assumptions['atm_fee']
        monthly_revenue = interchange_revenue + monthly_fee_revenue + atm_revenue

        processing_costs = monthly_spend * assumptions['processing_cost_rate']

        return {
            'monthly_spend': monthly_spend,
            'interchange_revenue': interchange_revenue,
            'monthly_fee_revenue': monthly_fee_revenue,
            'atm_revenue': atm_revenue,
            'monthly_revenue': monthly_revenue,
            'monthly_costs': processing_costs,
            'monthly_profit': monthly_revenue - processing_costs,
            'revenue_per_customer': monthly_revenue / customer_count,
            'cost_per_customer': processing_costs / customer_count,
            'annual_revenue': monthly_revenue * 12,
            'annual_profit': (monthly_revenue - processing_costs) * 12
        }

    def run_scenario_analysis(self, product, customer_counts):
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
        print(f"\n=== BLOCK BUSINESS BANKING FINANCIAL ANALYSIS ===")
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"Data Source:   {'Live (Snowflake)' if self.use_live_data else 'Hardcoded Assumptions'}")
        print(f"Customer Base: {customer_count:,} customers per product")
        print("=" * 60)

        product_map = {
            'instant_transfer': 'Instant Transfer',
            'credit_card': 'Credit Card',
            'debit_card': 'Debit Card'
        }
        summary_data = []

        for product, product_name in product_map.items():
            assumptions = self.base_assumptions[product]
            if product == 'instant_transfer':
                metrics = self.calculate_instant_transfer_metrics(assumptions, customer_count)
            elif product == 'credit_card':
                metrics = self.calculate_credit_card_metrics(assumptions, customer_count)
            elif product == 'debit_card':
                metrics = self.calculate_debit_card_metrics(assumptions, customer_count)

            print(f"\n{product_name.upper()}")
            print("-" * 30)
            print(f"Annual Revenue:               ${metrics['annual_revenue']:>12,.0f}")
            print(f"Annual Profit:                ${metrics['annual_profit']:>12,.0f}")
            print(f"Monthly Revenue per Customer: ${metrics['revenue_per_customer']:>12.2f}")
            if product == 'instant_transfer':
                print(f"Take Rate:                     {metrics['take_rate']:>11.2%}")
                print(f"Margin per Transaction:       ${metrics['margin_per_transaction']:>12.2f}")

            summary_data.append({
                'Product': product_name,
                'Annual Revenue': metrics['annual_revenue'],
                'Annual Profit': metrics['annual_profit'],
                'Monthly Revenue per Customer': metrics['revenue_per_customer'],
                'Profit Margin': metrics['annual_profit'] / metrics['annual_revenue']
            })

        total_revenue = sum(d['Annual Revenue'] for d in summary_data)
        total_profit = sum(d['Annual Profit'] for d in summary_data)

        print(f"\nPORTFOLIO SUMMARY")
        print("-" * 30)
        print(f"Total Annual Revenue: ${total_revenue:,.0f}")
        print(f"Total Annual Profit:  ${total_profit:,.0f}")
        print(f"Portfolio Margin:      {total_profit / total_revenue:.1%}")

        return pd.DataFrame(summary_data)

    def export_to_sheets(self, spreadsheet_url: str, customer_count=10000):
        """Export summary and scenario analysis to Google Sheets tabs."""
        print(f"\nExporting to Google Sheets...")

        # Tab 1: Portfolio Summary
        summary_df = self.generate_summary_report(customer_count=customer_count)
        write_dataframe(spreadsheet_url, "Portfolio Summary", summary_df)

        # Tabs 2-4: Scenario analysis per product
        customer_scenarios = [1000, 5000, 10000, 25000, 50000]
        for product in ['instant_transfer', 'credit_card', 'debit_card']:
            scenario_df = self.run_scenario_analysis(product, customer_scenarios)
            tab_name = product.replace('_', ' ').title()
            write_dataframe(spreadsheet_url, tab_name, scenario_df)

        print(f"\nDone. Open your sheet: {spreadsheet_url}")


if __name__ == "__main__":
    model = BusinessBankingModel(use_live_data=True)

    sheet_url = os.getenv("GOOGLE_SHEET_URL")

    if sheet_url:
        model.export_to_sheets(sheet_url, customer_count=10000)
    else:
        # Fallback: print to terminal
        summary = model.generate_summary_report(customer_count=10000)
        customer_scenarios = [1000, 5000, 10000, 25000, 50000]
        print(f"\n\n=== SCENARIO ANALYSIS ===")
        for product in ['instant_transfer', 'credit_card', 'debit_card']:
            print(f"\n{product.replace('_', ' ').title()} Scaling Analysis:")
            scenario_df = model.run_scenario_analysis(product, customer_scenarios)
            print(scenario_df[['customer_count', 'annual_revenue', 'annual_profit', 'revenue_per_customer']].to_string(index=False))
