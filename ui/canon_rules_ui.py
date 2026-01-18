"""
Canon Rules UI - View and manage canon rules from GraphStore
"""

import streamlit as st
from core.registry import REGISTRY


def render_canon_rules(project_name: str):
    """Render canon rules viewer and manager"""
    st.header("📜 Canon Rules")
    
    graph = REGISTRY.get_graph_store(project_name)
    canon_rules = graph.get_canon_rules()
    
    if not canon_rules:
        st.info("No canon rules yet. Run Director Mode to generate canon rules.")
        return
    
    # Summary stats
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Rules", len(canon_rules))
    with col2:
        sources = set(r.get('source', 'Unknown') for r in canon_rules)
        st.metric("Unique Sources", len(sources))
    
    st.markdown("---")
    
    # Filter options
    all_sources = sorted(set(r.get('source', 'Unknown') for r in canon_rules))
    filter_source = st.selectbox("Filter by Source", ["All"] + all_sources, key="canon_rules_filter")
    
    # Search
    search = st.text_input("Search in rules", key="canon_rules_search")
    
    # Filter rules
    filtered_rules = canon_rules
    
    if filter_source != "All":
        filtered_rules = [r for r in filtered_rules if r.get('source', 'Unknown') == filter_source]
    
    if search:
        search_lower = search.lower()
        filtered_rules = [r for r in filtered_rules if search_lower in r.get('rule', '').lower()]
    
    st.write(f"Showing {len(filtered_rules)} / {len(canon_rules)} rules")
    
    # Display rules
    for idx, rule in enumerate(filtered_rules):
        rule_text = rule.get('rule', '')
        source = rule.get('source', 'Unknown')
        confidence = rule.get('confidence', 'N/A')
        
        if confidence != 'N/A':
            header = f"Rule {idx + 1} • {source} • Confidence: {confidence}"
        else:
            header = f"Rule {idx + 1} • {source}"
        
        with st.expander(header, expanded=(idx < 3 and not search)):
            st.markdown(f"**Rule:** {rule_text}")
            
            metadata = {k: v for k, v in rule.items() if k not in ['rule', 'source', 'confidence']}
            if metadata:
                with st.expander("Additional Metadata"):
                    st.json(metadata)
            
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("Copy", key=f"copy_rule_{idx}"):
                    st.code(rule_text, language="text")
    
    # Bulk actions
    st.markdown("---")
    st.markdown("### 🔧 Manage Canon Rules")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Export Rules**")
        if st.button("Download as JSON"):
            import json
            rules_json = json.dumps(canon_rules, indent=2, ensure_ascii=False)
            st.download_button("Download JSON", rules_json,
                             file_name=f"{project_name}_canon_rules.json",
                             mime="application/json")
    
    with col2:
        st.markdown("**Clear All Rules**")
        st.write("⚠️ This cannot be undone")
        if st.button("Clear All Rules", type="secondary"):
            raw_graph = graph.get_raw_graph()
            raw_graph['canon_rules'] = []
            graph.replace_graph(raw_graph)
            st.success("All canon rules cleared!")
            st.rerun()
    
    # Add new rule manually
    with st.expander("➕ Add Custom Canon Rule"):
        st.markdown("Manually add a canon rule to the graph")
        
        new_rule = st.text_area("Rule Text",
            placeholder="Enter a canon rule (e.g., 'Character X always speaks in formal language')",
            key="new_canon_rule_text")
        
        new_source = st.text_input("Source", value="user_defined", key="new_canon_rule_source")
        
        if st.button("Add Rule"):
            if new_rule.strip():
                graph.add_canon_rule(rule=new_rule.strip(), source=new_source, confidence=1.0)
                st.success("Canon rule added!")
                st.rerun()
            else:
                st.error("Please enter a rule text")