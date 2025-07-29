"""
Chart building utilities for the financial planning dashboard.
Uses Plotly for interactive visualizations with enhanced performance.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import time


@st.cache_data(ttl=60, max_entries=20)
def create_metric_cards(metrics: Dict[str, Any]) -> List[go.Figure]:
    """
    Create metric cards as Plotly figures with caching.
    
    Args:
        metrics: Dictionary containing calculated metrics
    
    Returns:
        List of Plotly figure objects for metric cards
    """
    cards = []
    
    # Net Worth Card
    fig_net_worth = go.Figure()
    fig_net_worth.add_trace(go.Indicator(
        mode="number+delta",
        value=metrics['max_net_worth'],
        delta={'reference': metrics['max_net_worth'] * 0.8},
        title={'text': "Max Net Worth"},
        domain={'x': [0, 1], 'y': [0, 1]}
    ))
    fig_net_worth.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    cards.append(fig_net_worth)
    
    # Savings Card
    fig_savings = go.Figure()
    fig_savings.add_trace(go.Indicator(
        mode="number+delta",
        value=metrics['avg_annual_savings'],
        delta={'reference': metrics['avg_annual_savings'] * 0.9},
        title={'text': "Avg Annual Savings"},
        domain={'x': [0, 1], 'y': [0, 1]}
    ))
    fig_savings.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    cards.append(fig_savings)
    
    return cards


def create_summary_chart(_scenarios: Dict[str, Any], metric: str = 'net_worth') -> go.Figure:
    """
    Create a summary chart for the selected metric with caching.
    
    Args:
        scenarios: Dictionary of scenario data
        metric: Metric to visualize ('net_worth', 'savings', 'income')
    
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Color scheme for scenarios
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    # Initialize y_title based on metric
    if metric == 'net_worth':
        y_title = "Net Worth (£)"
    elif metric == 'savings':
        y_title = "Annual Savings (£)"
    elif metric == 'income':
        y_title = "Gross Income (£)"
    else:
        y_title = "Net Worth (£)"
    
    for i, (scenario_name, scenario) in enumerate(_scenarios.items()):
        if not scenario.data_points:
            continue
        
        # Extract data based on metric
        years = [point.year for point in scenario.data_points]
        
        if metric == 'net_worth':
            # Use the correct net worth value for international scenarios - check _equiv first
            values = []
            for point in scenario.data_points:
                net_worth = point.net_worth_gbp_equiv if hasattr(point, 'net_worth_gbp_equiv') and point.net_worth_gbp_equiv > 0 else (
                    point.net_worth_gbp if hasattr(point, 'net_worth_gbp') and point.net_worth_gbp > 0 else (
                        point.net_worth_usd / 1.26 if hasattr(point, 'net_worth_usd') and point.net_worth_usd > 0 else 0
                    )
                )
                values.append(net_worth)
        
        elif metric == 'savings':
            values = []
            for point in scenario.data_points:
                savings = point.annual_savings_gbp_equiv if hasattr(point, 'annual_savings_gbp_equiv') and point.annual_savings_gbp_equiv > 0 else (
                    point.annual_savings_gbp if hasattr(point, 'annual_savings_gbp') and point.annual_savings_gbp > 0 else (
                        point.annual_savings_usd / 1.26 if hasattr(point, 'annual_savings_usd') and point.annual_savings_usd > 0 else 0
                    )
                )
                values.append(savings)
        
        elif metric == 'income':
            values = []
            for point in scenario.data_points:
                income = point.gross_income_gbp_equiv if hasattr(point, 'gross_income_gbp_equiv') and point.gross_income_gbp_equiv > 0 else (
                    point.gross_salary_gbp if hasattr(point, 'gross_salary_gbp') and point.gross_salary_gbp > 0 else (
                        point.total_gross_usd / 1.26 if hasattr(point, 'total_gross_usd') and point.total_gross_usd > 0 else 0
                    )
                )
                values.append(income)
        
        else:
            values = []
            for point in scenario.data_points:
                net_worth = point.net_worth_gbp_equiv if hasattr(point, 'net_worth_gbp_equiv') and point.net_worth_gbp_equiv > 0 else (
                    point.net_worth_gbp if hasattr(point, 'net_worth_gbp') and point.net_worth_gbp > 0 else (
                        point.net_worth_usd / 1.26 if hasattr(point, 'net_worth_usd') and point.net_worth_usd > 0 else 0
                    )
                )
                values.append(net_worth)
        
        # Add trace to figure
        fig.add_trace(go.Scatter(
            x=years,
            y=values,
            mode='lines+markers',
            name=scenario_name,
            line=dict(color=colors[i % len(colors)], width=2),
            marker=dict(size=6),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         f'{metric.replace("_", " ").title()}: £%{{y:,.0f}}<br>' +
                         'Year: %{x}<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        title=f"{metric.replace('_', ' ').title()} Trajectory",
        xaxis_title="Year",
        yaxis_title=y_title,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_performance_ranking(_scenarios: Dict[str, Any]) -> Dict[str, List[Tuple[str, float]]]:
    """
    Create performance ranking data with caching.
    
    Args:
        scenarios: Dictionary of scenario data
    
    Returns:
        Dictionary containing ranking data for different metrics
    """
    ranking_data = {
        'net_worth': [],
        'savings_rate': [],
        'total_savings': []
    }
    
    for scenario_name, scenario in _scenarios.items():
        if not scenario.data_points:
            continue
        
        # Calculate net worth ranking
        final_net_worth = scenario.get_final_net_worth()
        ranking_data['net_worth'].append((scenario_name, final_net_worth))
        
        # Calculate savings rate
        annual_savings = []
        gross_incomes = []
        
        for point in scenario.data_points:
            # Handle international scenario savings
            savings = point.annual_savings_gbp_equiv if hasattr(point, 'annual_savings_gbp_equiv') and point.annual_savings_gbp_equiv > 0 else (
                point.annual_savings_gbp if hasattr(point, 'annual_savings_gbp') and point.annual_savings_gbp > 0 else (
                    point.annual_savings_usd / 1.26 if hasattr(point, 'annual_savings_usd') and point.annual_savings_usd > 0 else 0
                )
            )
            annual_savings.append(savings)
            
            # Handle international scenario income
            income = point.gross_income_gbp_equiv if hasattr(point, 'gross_income_gbp_equiv') and point.gross_income_gbp_equiv > 0 else (
                point.gross_salary_gbp if hasattr(point, 'gross_salary_gbp') and point.gross_salary_gbp > 0 else (
                    point.total_gross_usd / 1.26 if hasattr(point, 'total_gross_usd') and point.total_gross_usd > 0 else 0
                )
            )
            gross_incomes.append(income)
        
        avg_savings = np.mean(annual_savings) if annual_savings else 0
        avg_income = np.mean(gross_incomes) if gross_incomes else 0
        savings_rate = (avg_savings / max(1, avg_income)) * 100
        
        ranking_data['savings_rate'].append((scenario_name, savings_rate))
        ranking_data['total_savings'].append((scenario_name, sum(annual_savings)))
    
    # Sort rankings
    for key in ranking_data:
        ranking_data[key].sort(key=lambda x: x[1], reverse=True)
    
    return ranking_data


def create_stacked_income_analysis(_scenarios: Dict[str, Any]) -> go.Figure:
    """
    Create stacked income analysis chart with caching.
    
    Args:
        scenarios: Dictionary of scenario data
    
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Color scheme
    colors = {
        'salary': '#1f77b4',
        'bonus': '#ff7f0e',
        'rsu': '#2ca02c'
    }
    
    for scenario_name, scenario in _scenarios.items():
        if not scenario.data_points:
            continue
        
        years = [point.year for point in scenario.data_points]
        
        # Extract income components
        salaries = []
        bonuses = []
        rsu_values = []
        
        for point in scenario.data_points:
            # Handle international scenario salary
            salary = point.gross_income_gbp_equiv if hasattr(point, 'gross_income_gbp_equiv') and point.gross_income_gbp_equiv > 0 else (
                point.gross_salary_gbp if hasattr(point, 'gross_salary_gbp') and point.gross_salary_gbp > 0 else (
                    point.total_gross_usd / 1.26 if hasattr(point, 'total_gross_usd') and point.total_gross_usd > 0 else 0
                )
            )
            salaries.append(salary)
            
            # Handle international scenario bonus
            bonus = point.gross_bonus_gbp_equiv if hasattr(point, 'gross_bonus_gbp_equiv') and point.gross_bonus_gbp_equiv > 0 else (
                point.gross_bonus_gbp if hasattr(point, 'gross_bonus_gbp') and point.gross_bonus_gbp > 0 else (
                    point.gross_bonus_usd / 1.26 if hasattr(point, 'gross_bonus_usd') and point.gross_bonus_usd > 0 else 0
                )
            )
            bonuses.append(bonus)
            
            # Handle international scenario RSU
            rsu_value = point.vested_rsu_gbp_equiv if hasattr(point, 'vested_rsu_gbp_equiv') and point.vested_rsu_gbp_equiv > 0 else (
                point.vested_rsu_gbp if hasattr(point, 'vested_rsu_gbp') and point.vested_rsu_gbp > 0 else (
                    point.vested_rsu_usd / 1.26 if hasattr(point, 'vested_rsu_usd') and point.vested_rsu_usd > 0 else 0
                )
            )
            rsu_values.append(rsu_value)
        
        # Add stacked traces
        fig.add_trace(go.Bar(
            name=f"{scenario_name} - Salary",
            x=years,
            y=salaries,
            marker_color=colors['salary'],
            opacity=0.8,
            hovertemplate='<b>%{fullData.name}</b><br>Salary: £%{y:,.0f}<br>Year: %{x}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            name=f"{scenario_name} - Bonus",
            x=years,
            y=bonuses,
            marker_color=colors['bonus'],
            opacity=0.8,
            hovertemplate='<b>%{fullData.name}</b><br>Bonus: £%{y:,.0f}<br>Year: %{x}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            name=f"{scenario_name} - RSU",
            x=years,
            y=rsu_values,
            marker_color=colors['rsu'],
            opacity=0.8,
            hovertemplate='<b>%{fullData.name}</b><br>RSU: £%{y:,.0f}<br>Year: %{x}<extra></extra>'
        ))
    
    fig.update_layout(
        title="Income Breakdown by Component",
        xaxis_title="Year",
        yaxis_title="Income (£)",
        barmode='stack',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_stacked_expense_analysis(_scenarios: Dict[str, Any]) -> go.Figure:
    """
    Create stacked expense analysis chart with caching.
    
    Args:
        scenarios: Dictionary of scenario data
    
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Color scheme
    colors = {
        'taxes': '#d62728',
        'expenses': '#9467bd',
        'mortgage': '#8c564b'
    }
    
    for scenario_name, scenario in _scenarios.items():
        if not scenario.data_points:
            continue
        
        years = [point.year for point in scenario.data_points]
        
        # Extract expense components
        taxes = []
        other_expenses = []
        mortgage_payments = []
        
        for point in scenario.data_points:
            # Handle international scenario taxes
            tax = point.income_tax_gbp_equiv if hasattr(point, 'income_tax_gbp_equiv') and point.income_tax_gbp_equiv > 0 else (
                point.income_tax_gbp if hasattr(point, 'income_tax_gbp') and point.income_tax_gbp > 0 else (
                    point.income_tax_usd / 1.26 if hasattr(point, 'income_tax_usd') and point.income_tax_usd > 0 else 0
                )
            )
            taxes.append(tax)
            
            # Handle international scenario expenses
            total_expenses = point.total_expenses_gbp_equiv if hasattr(point, 'total_expenses_gbp_equiv') and point.total_expenses_gbp_equiv > 0 else (
                point.total_expenses_gbp if hasattr(point, 'total_expenses_gbp') and point.total_expenses_gbp > 0 else (
                    point.total_expenses_usd / 1.26 if hasattr(point, 'total_expenses_usd') and point.total_expenses_usd > 0 else 0
                )
            )
            
            # Extract mortgage payment (simplified)
            mortgage = point.mortgage_payment_gbp if hasattr(point, 'mortgage_payment_gbp') and point.mortgage_payment_gbp > 0 else 0
            mortgage_payments.append(mortgage)
            
            # Other expenses (total - taxes - mortgage)
            other_expense = total_expenses - tax - mortgage
            other_expenses.append(max(0, other_expense))
        
        # Add stacked traces
        fig.add_trace(go.Bar(
            name=f"{scenario_name} - Taxes",
            x=years,
            y=taxes,
            marker_color=colors['taxes'],
            opacity=0.8,
            hovertemplate='<b>%{fullData.name}</b><br>Taxes: £%{y:,.0f}<br>Year: %{x}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            name=f"{scenario_name} - Other Expenses",
            x=years,
            y=other_expenses,
            marker_color=colors['expenses'],
            opacity=0.8,
            hovertemplate='<b>%{fullData.name}</b><br>Other Expenses: £%{y:,.0f}<br>Year: %{x}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            name=f"{scenario_name} - Mortgage",
            x=years,
            y=mortgage_payments,
            marker_color=colors['mortgage'],
            opacity=0.8,
            hovertemplate='<b>%{fullData.name}</b><br>Mortgage: £%{y:,.0f}<br>Year: %{x}<extra></extra>'
        ))
    
    fig.update_layout(
        title="Expense Breakdown by Component",
        xaxis_title="Year",
        yaxis_title="Expenses (£)",
        barmode='stack',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_comparison_chart(scenario1: str, scenario2: str, _scenarios: Dict[str, Any]) -> go.Figure:
    """
    Create side-by-side comparison chart with caching.
    
    Args:
        scenario1: First scenario name
        scenario2: Second scenario name
        scenarios: Dictionary of scenario data
    
    Returns:
        Plotly figure object
    """
    if scenario1 not in _scenarios or scenario2 not in _scenarios:
        return go.Figure()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Net Worth Comparison', 'Annual Savings Comparison', 
                       'Income Comparison', 'Expenses Comparison'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Color scheme
    colors = ['#1f77b4', '#ff7f0e']
    
    for i, scenario_name in enumerate([scenario1, scenario2]):
        scenario = _scenarios[scenario_name]
        if not scenario.data_points:
            continue
        
        years = [point.year for point in scenario.data_points]
        
        # Net Worth
        net_worth_values = []
        for point in scenario.data_points:
            net_worth = point.net_worth_gbp_equiv if hasattr(point, 'net_worth_gbp_equiv') and point.net_worth_gbp_equiv > 0 else (
                point.net_worth_gbp if hasattr(point, 'net_worth_gbp') and point.net_worth_gbp > 0 else (
                    point.net_worth_usd / 1.26 if hasattr(point, 'net_worth_usd') and point.net_worth_usd > 0 else 0
                )
            )
            net_worth_values.append(net_worth)
        
        fig.add_trace(
            go.Scatter(x=years, y=net_worth_values, name=f"{scenario_name} - Net Worth",
                      line=dict(color=colors[i]), mode='lines+markers'),
            row=1, col=1
        )
        
        # Annual Savings
        savings_values = []
        for point in scenario.data_points:
            savings = point.annual_savings_gbp_equiv if hasattr(point, 'annual_savings_gbp_equiv') and point.annual_savings_gbp_equiv > 0 else (
                point.annual_savings_gbp if hasattr(point, 'annual_savings_gbp') and point.annual_savings_gbp > 0 else (
                    point.annual_savings_usd / 1.26 if hasattr(point, 'annual_savings_usd') and point.annual_savings_usd > 0 else 0
                )
            )
            savings_values.append(savings)
        
        fig.add_trace(
            go.Scatter(x=years, y=savings_values, name=f"{scenario_name} - Savings",
                      line=dict(color=colors[i]), mode='lines+markers'),
            row=1, col=2
        )
        
        # Income
        income_values = []
        for point in scenario.data_points:
            income = point.gross_income_gbp_equiv if hasattr(point, 'gross_income_gbp_equiv') and point.gross_income_gbp_equiv > 0 else (
                point.gross_salary_gbp if hasattr(point, 'gross_salary_gbp') and point.gross_salary_gbp > 0 else (
                    point.total_gross_usd / 1.26 if hasattr(point, 'total_gross_usd') and point.total_gross_usd > 0 else 0
                )
            )
            income_values.append(income)
        
        fig.add_trace(
            go.Scatter(x=years, y=income_values, name=f"{scenario_name} - Income",
                      line=dict(color=colors[i]), mode='lines+markers'),
            row=2, col=1
        )
        
        # Expenses
        expense_values = []
        for point in scenario.data_points:
            expenses = point.total_expenses_gbp_equiv if hasattr(point, 'total_expenses_gbp_equiv') and point.total_expenses_gbp_equiv > 0 else (
                point.total_expenses_gbp if hasattr(point, 'total_expenses_gbp') and point.total_expenses_gbp > 0 else (
                    point.total_expenses_usd / 1.26 if hasattr(point, 'total_expenses_usd') and point.total_expenses_usd > 0 else 0
                )
            )
            expense_values.append(expenses)
        
        fig.add_trace(
            go.Scatter(x=years, y=expense_values, name=f"{scenario_name} - Expenses",
                      line=dict(color=colors[i]), mode='lines+markers'),
            row=2, col=2
        )
    
    fig.update_layout(
        title=f"Side-by-Side Comparison: {scenario1} vs {scenario2}",
        height=600,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Year", row=1, col=1)
    fig.update_xaxes(title_text="Year", row=1, col=2)
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_xaxes(title_text="Year", row=2, col=2)
    
    fig.update_yaxes(title_text="Net Worth (£)", row=1, col=1)
    fig.update_yaxes(title_text="Annual Savings (£)", row=1, col=2)
    fig.update_yaxes(title_text="Income (£)", row=2, col=1)
    fig.update_yaxes(title_text="Expenses (£)", row=2, col=2)
    
    return fig 