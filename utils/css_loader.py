"""
CSS Loader Utility for Streamlit Applications
Manages loading of external CSS files and inline styles.
"""

import os
import streamlit as st
from pathlib import Path
from typing import List, Optional


class CSSLoader:
    """Utility class for loading and managing CSS in Streamlit applications."""
    
    def __init__(self, css_dir: str = "static/css"):
        """
        Initialize the CSS loader.
        
        Args:
            css_dir: Directory containing CSS files
        """
        self.css_dir = Path(css_dir)
        self.loaded_files = set()
    
    def load_css_file(self, filename: str) -> None:
        """
        Load a CSS file and inject it into Streamlit.
        
        Args:
            filename: Name of the CSS file to load
        """
        if filename in self.loaded_files:
            return  # Already loaded
        
        css_path = self.css_dir / filename
        
        if not css_path.exists():
            st.warning(f"CSS file not found: {css_path}")
            return
        
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            # Inject CSS into Streamlit
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
            self.loaded_files.add(filename)
            
        except Exception as e:
            st.error(f"Error loading CSS file {filename}: {str(e)}")
    
    def load_main_css(self) -> None:
        """Load the main CSS file."""
        self.load_css_file("main.css")
    
    def load_all_css(self) -> None:
        """Load all CSS files in the directory."""
        if not self.css_dir.exists():
            st.warning(f"CSS directory not found: {self.css_dir}")
            return
        
        for css_file in self.css_dir.glob("*.css"):
            self.load_css_file(css_file.name)
    
    def inject_custom_css(self, css_content: str) -> None:
        """
        Inject custom CSS content directly.
        
        Args:
            css_content: CSS content to inject
        """
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


# Global CSS loader instance
css_loader = CSSLoader()


def load_css(filename: str = "main.css") -> None:
    """
    Load a CSS file in Streamlit.
    
    Args:
        filename: Name of the CSS file to load (default: main.css)
    """
    css_loader.load_css_file(filename)


def load_main_styles() -> None:
    """Load the main application styles."""
    css_loader.load_main_css()


def inject_custom_styles(css_content: str) -> None:
    """
    Inject custom CSS styles.
    
    Args:
        css_content: CSS content to inject
    """
    css_loader.inject_custom_css(css_content)


# Predefined CSS snippets for common components
COMPONENT_CSS = {
    "kpi_cards": """
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 1rem;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    """,
    
    "enhanced_tables": """
    .enhanced-table {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    """,
    
    "metric_highlights": """
    .metric-highlight {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-highlight-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-highlight-purple {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    """,
    
    "streamlit_components": """
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #495057;
        font-weight: 500;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #667eea;
        color: white;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    """
}


def load_component_styles(components: List[str]) -> None:
    """
    Load specific component styles.
    
    Args:
        components: List of component names to load styles for
    """
    for component in components:
        if component in COMPONENT_CSS:
            inject_custom_styles(COMPONENT_CSS[component])
        else:
            st.warning(f"Unknown component: {component}")


def load_all_styles() -> None:
    """Load all available styles."""
    load_main_styles()
    load_component_styles(list(COMPONENT_CSS.keys())) 