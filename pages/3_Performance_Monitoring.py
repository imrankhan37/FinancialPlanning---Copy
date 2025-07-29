"""
Performance Monitoring Page
Track and optimize dashboard performance with real-time metrics.
"""

import streamlit as st
import time
from typing import Dict, Any

# Import custom modules
from utils.performance import render_performance_dashboard, performance_monitor, monitor_memory_usage
from utils.data import load_all_scenarios, clear_cache


def render_performance_page(scenarios_to_analyze=None) -> None:
    """Render the performance monitoring page."""
    
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">⚡ System Performance Monitor</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">Monitor dashboard performance, optimize data loading, and track system resources in real-time.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main performance dashboard
    render_performance_dashboard()
    
    # Performance testing section
    st.markdown("---")
    st.subheader("🧪 Performance Testing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Test Data Loading", help="Test scenario data loading performance", use_container_width=True):
            with st.spinner("Testing data loading..."):
                start_time = time.time()
                try:
                    scenarios = load_all_scenarios()
                    load_time = time.time() - start_time
                    st.success(f"✅ Data loaded successfully in {load_time:.2f}s")
                    
                    # Track the operation
                    performance_monitor.track_load_time("test_data_loading", load_time)
                    
                except Exception as e:
                    st.error(f"❌ Data loading failed: {str(e)}")
    
    with col2:
        if st.button("🧹 Clear All Cache", help="Clear all cached data", use_container_width=True):
            clear_cache()
            st.success("✅ Cache cleared successfully!")
    
    # Memory monitoring
    st.markdown("---")
    st.subheader("💾 Memory Monitoring")
    monitor_memory_usage()
    
    # Performance tips
    st.markdown("---")
    st.subheader("💡 Performance Tips")
    
    tips = [
        "<strong>Cache Management</strong>: Use the cache management tools to clear old data and improve performance.",
        "<strong>Data Filtering</strong>: Apply filters to reduce the amount of data processed.",
        "<strong>Chart Optimization</strong>: Reduce the number of data points in charts for faster rendering.",
        "<strong>Regular Monitoring</strong>: Check the performance dashboard regularly to identify bottlenecks.",
        "<strong>System Resources</strong>: Monitor memory and CPU usage to ensure optimal performance."
    ]
    
    for tip in tips:
        st.info(tip)
    
    # Performance comparison
    st.markdown("---")
    st.subheader("📈 Performance Comparison")
    
    # Simulate different scenarios
    if st.button("🏃‍♂️ Run Performance Benchmark", use_container_width=True):
        with st.spinner("Running performance benchmark..."):
            results = []
            
            # Test different operations
            operations = [
                ("Load All Scenarios", lambda: load_all_scenarios()),
                ("Filter Scenarios", lambda: load_all_scenarios() if 'test_scenarios' not in locals() else locals()['test_scenarios']),
                ("Calculate Metrics", lambda: time.sleep(0.1)),  # Simulate metric calculation
            ]
            
            for op_name, operation in operations:
                start_time = time.time()
                try:
                    operation()
                    duration = time.time() - start_time
                    results.append({
                        'Operation': op_name,
                        'Duration (s)': f"{duration:.3f}",
                        'Status': '✅ Success'
                    })
                except Exception as e:
                    duration = time.time() - start_time
                    results.append({
                        'Operation': op_name,
                        'Duration (s)': f"{duration:.3f}",
                        'Status': f'❌ Failed: {str(e)}'
                    })
            
            # Display results
            if results:
                st.dataframe(results, use_container_width=True)
    
    # Advanced settings
    st.markdown("---")
    st.subheader("⚙️ Advanced Performance Settings")
    
    # Cache settings
    st.markdown("<strong>Cache Settings</strong>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Scenario Data TTL", "5 minutes")
    with col2:
        st.metric("Chart Data TTL", "1 minute")
    with col3:
        st.metric("Metrics TTL", "30 seconds")
    with col4:
        st.metric("Filtered Data TTL", "2 minutes")
    
    # Optimization settings
    st.markdown("<strong>Optimization Settings</strong>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Max Chart Points", "1000")
    with col2:
        st.metric("Memory Warning Threshold", "80%")
    with col3:
        st.metric("CPU Warning Threshold", "70%")
    
    # Monitoring settings
    st.markdown("<strong>Monitoring Settings</strong>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("Performance Tracking: Enabled")
    with col2:
        st.success("Memory Monitoring: Enabled")
    with col3:
        st.warning("Auto Cache Cleanup: Disabled")


def main() -> None:
    """Main function for the performance monitoring page."""
    try:
        render_performance_page()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please try refreshing the page or clearing the cache.")


if __name__ == "__main__":
    main() 