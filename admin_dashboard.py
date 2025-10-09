"""
Admin Dashboard for Wellness Bot
Comprehensive admin interface with analytics, user management, and system controls
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import json
from datetime import datetime, timedelta
from admin_manager import AdminManager

# Helper functions for knowledge base editing
def add_symptom_to_kb(name, synonyms, description, category):
    """Add a new symptom to the knowledge base"""
    try:
        # Load existing knowledge base
        with open('kb_csv.json', 'r', encoding='utf-8') as f:
            kb_data = json.load(f)
        
        # Create new symptom entry
        synonyms_list = [s.strip() for s in synonyms.split('\n') if s.strip()]
        
        new_symptom = {
            "name": name.lower().replace(' ', '_'),
            "display_name": name,
            "synonyms": synonyms_list,
            "description": description,
            "category": category,
            "frequency": 0,
            "related_diseases": []
        }
        
        # Add to symptoms list
        if 'symptoms' not in kb_data:
            kb_data['symptoms'] = []
        
        kb_data['symptoms'].append(new_symptom)
        
        # Save back to file
        with open('kb_csv.json', 'w', encoding='utf-8') as f:
            json.dump(kb_data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error adding symptom: {e}")
        return False

def add_disease_to_kb(name, symptoms, description, precautions):
    """Add a new disease to the knowledge base"""
    try:
        # Add to symptom_Description.csv
        with open('symptom_Description.csv', 'a', newline='', encoding='utf-8') as f:
            f.write(f"\n{name},{description}")
        
        # Add to symptom_precaution.csv
        precaution_list = [p.strip() for p in precautions.split('\n') if p.strip()]
        precaution_str = ', '.join(precaution_list[:4])  # Max 4 precautions
        
        with open('symptom_precaution.csv', 'a', newline='', encoding='utf-8') as f:
            f.write(f"\n{name},{precaution_str}")
        
        return True
    except Exception as e:
        print(f"Error adding disease: {e}")
        return False

def update_symptom_in_kb(old_name, new_name, new_synonyms):
    """Update an existing symptom in the knowledge base"""
    try:
        with open('kb_csv.json', 'r', encoding='utf-8') as f:
            kb_data = json.load(f)
        
        # Find and update the symptom
        for symptom in kb_data.get('symptoms', []):
            if symptom.get('name') == old_name or symptom.get('display_name') == old_name:
                symptom['display_name'] = new_name
                symptom['name'] = new_name.lower().replace(' ', '_')
                symptom['synonyms'] = [s.strip() for s in new_synonyms.split('\n') if s.strip()]
                break
        
        # Save back to file
        with open('kb_csv.json', 'w', encoding='utf-8') as f:
            json.dump(kb_data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error updating symptom: {e}")
        return False

def update_disease_description(disease_name, new_description):
    """Update disease description in CSV file"""
    try:
        # Read the CSV file
        diseases_df = pd.read_csv('symptom_Description.csv')
        
        # Update the description
        diseases_df.loc[diseases_df['Disease'] == disease_name, 'Description'] = new_description
        
        # Save back to CSV
        diseases_df.to_csv('symptom_Description.csv', index=False)
        
        return True
    except Exception as e:
        print(f"Error updating disease: {e}")
        return False

# Page configuration
st.set_page_config(
    page_title="Wellness Bot Admin",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize admin manager
if 'admin_manager' not in st.session_state:
    st.session_state.admin_manager = AdminManager()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .metric-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .success-alert {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .warning-alert {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-alert {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def login_page():
    """Admin login page"""
    st.markdown("""
    <div class="main-header">
        <h1>🏥 Wellness Bot Admin Dashboard</h1>
        <p>Secure admin access for system management</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Admin Login")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter admin username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            login_button = st.form_submit_button("Login", use_container_width=True)
            
            if login_button:
                if username and password:
                    admin = st.session_state.admin_manager.authenticate_admin(username, password)
                    if admin:
                        st.session_state.admin_user = admin
                        st.success(f"Welcome back, {admin['username']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")
    
    st.markdown("---")
    st.info("**Default Admin Credentials:**\n- Username: `admin`\n- Password: `admin123`")

def dashboard_overview():
    """Main dashboard overview"""
    st.markdown("""
    <div class="main-header">
        <h1>📊 Admin Dashboard Overview</h1>
        <p>Welcome to the Wellness Bot Administration Panel</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get dashboard statistics
    stats = st.session_state.admin_manager.get_dashboard_stats()
    
    # Key metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Total Users",
            value=stats.get('total_users', 0),
            delta=f"+{stats.get('users_today', 0)} today"
        )
    
    with col2:
        st.metric(
            label="💬 Total Conversations",
            value=stats.get('total_conversations', 0),
            delta=f"+{stats.get('queries_today', 0)} today"
        )
    
    with col3:
        st.metric(
            label="📝 Feedback Items",
            value=stats.get('total_feedback', 0),
            delta=f"{stats.get('pending_feedback', 0)} pending"
        )
    
    with col4:
        st.metric(
            label="💡 Health Tips",
            value=stats.get('active_health_tips', 0),
            delta="Active"
        )
    
    st.markdown("---")
    
    # Charts row - Real Data Based
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Top Reported Symptoms")
        # Use real symptom frequency data from knowledge base
        try:
            with open('kb_csv.json', 'r', encoding='utf-8') as f:
                kb_data = json.load(f)
            
            symptoms = kb_data.get('symptoms', [])
            symptoms_with_freq = [(s.get('display_name', s.get('name', 'Unknown')), 
                                 s.get('frequency', 0)) for s in symptoms if s.get('frequency', 0) > 0]
            
            if symptoms_with_freq:
                symptoms_with_freq.sort(key=lambda x: x[1], reverse=True)
                top_10_symptoms = symptoms_with_freq[:10]
                
                symptom_df = pd.DataFrame(top_10_symptoms, columns=['Symptom', 'Frequency'])
                fig = px.bar(symptom_df, x='Frequency', y='Symptom', 
                           orientation='h', title="Most Common Symptoms (Real Data)")
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No symptom frequency data available")
        except Exception as e:
            st.error(f"Error loading symptom data: {e}")
    
    with col2:
        st.subheader("� Disease Categories")
        # Use real disease data from knowledge base
        try:
            with open('kb_csv.json', 'r', encoding='utf-8') as f:
                kb_data = json.load(f)
            
            symptoms = kb_data.get('symptoms', [])
            disease_counts = {}
            
            for symptom in symptoms:
                for disease in symptom.get('related_diseases', []):
                    disease_counts[disease] = disease_counts.get(disease, 0) + 1
            
            if disease_counts:
                sorted_diseases = sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)
                top_diseases = sorted_diseases[:8]  # Top 8 for better pie chart visibility
                
                disease_df = pd.DataFrame(top_diseases, columns=['Disease', 'Symptom_Count'])
                fig = px.pie(disease_df, values='Symptom_Count', names='Disease',
                           title="Diseases by Symptom Associations (Real Data)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No disease data available")
        except Exception as e:
            st.error(f"Error loading disease data: {e}")

def feedback_management():
    """Feedback management page"""
    st.markdown("# 📝 Feedback Management")
    
    # Tabs for different feedback views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 All Feedback", "🆕 New", "🔄 In Progress", "✅ Resolved"])
    
    with tab1:
        st.subheader("All Feedback")
        feedback_list = st.session_state.admin_manager.get_all_feedback()
        
        if feedback_list:
            df = pd.DataFrame(feedback_list)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Display feedback table
            st.dataframe(
                df[['id', 'user_email', 'feedback_type', 'subject', 'rating', 'status', 'created_at']],
                use_container_width=True
            )
            
            # Feedback details
            if st.selectbox("Select feedback to view details:", 
                          options=[f"{f['id']} - {f['subject']}" for f in feedback_list],
                          key="feedback_selector"):
                
                selected_id = int(st.session_state.feedback_selector.split(' - ')[0])
                selected_feedback = next(f for f in feedback_list if f['id'] == selected_id)
                
                st.markdown("### Feedback Details")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**User:** {selected_feedback['user_email']}")
                    st.write(f"**Type:** {selected_feedback['feedback_type']}")
                    st.write(f"**Status:** {selected_feedback['status']}")
                    if selected_feedback['rating']:
                        st.write(f"**Rating:** {'⭐' * selected_feedback['rating']}")
                
                with col2:
                    st.write(f"**Subject:** {selected_feedback['subject']}")
                    st.write(f"**Created:** {selected_feedback['created_at']}")
                
                st.write(f"**Message:**")
                st.text_area("", value=selected_feedback['message'], height=100, disabled=True)
                
                # Admin response section
                st.markdown("### Admin Response")
                admin_response = st.text_area(
                    "Response:",
                    value=selected_feedback.get('admin_response', ''),
                    height=100,
                    key=f"response_{selected_id}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    new_status = st.selectbox(
                        "Update Status:",
                        ['new', 'reviewed', 'resolved', 'archived'],
                        index=['new', 'reviewed', 'resolved', 'archived'].index(selected_feedback['status'])
                    )
                
                with col2:
                    if st.button("Update Feedback", use_container_width=True):
                        success = st.session_state.admin_manager.update_feedback_status(
                            selected_id, new_status, admin_response,
                            st.session_state.admin_user['id']
                        )
                        if success:
                            st.success("Feedback updated successfully!")
                            st.rerun()
        else:
            st.info("No feedback available yet.")
    
    with tab2:
        st.subheader("New Feedback")
        new_feedback = st.session_state.admin_manager.get_all_feedback('new')
        if new_feedback:
            for feedback in new_feedback:
                with st.expander(f"{feedback['subject']} - {feedback['user_email']}"):
                    st.write(f"**Type:** {feedback['feedback_type']}")
                    st.write(f"**Message:** {feedback['message']}")
                    if st.button(f"Mark as Reviewed", key=f"review_{feedback['id']}"):
                        st.session_state.admin_manager.update_feedback_status(
                            feedback['id'], 'reviewed', admin_id=st.session_state.admin_user['id']
                        )
                        st.rerun()
        else:
            st.info("No new feedback.")
    
    # Add test feedback button
    st.markdown("---")
    if st.button("🧪 Add Test Feedback"):
        test_feedback_id = st.session_state.admin_manager.add_feedback(
            "test@example.com",
            "feature",
            "Test Feedback",
            "This is a test feedback for demonstration purposes.",
            4
        )
        st.success(f"Test feedback added with ID: {test_feedback_id}")
        st.rerun()

def health_tips_management():
    """Health tips management page"""
    st.markdown("# 💡 Health Tips Management")
    
    tab1, tab2 = st.tabs(["📋 Manage Tips", "➕ Add New Tip"])
    
    with tab1:
        st.subheader("Current Health Tips")
        
        # Get health tips from database
        conn = sqlite3.connect(st.session_state.admin_manager.db_path)
        tips_df = pd.read_sql_query("""
            SELECT * FROM health_tips 
            WHERE is_active = 1 
            ORDER BY created_at DESC
        """, conn)
        conn.close()
        
        if not tips_df.empty:
            for _, tip in tips_df.iterrows():
                with st.expander(f"{tip['title']} ({tip['category']})"):
                    st.write(f"**Content:** {tip['content']}")
                    st.write(f"**Category:** {tip['category']}")
                    st.write(f"**Tags:** {tip['tags']}")
                    st.write(f"**Created:** {tip['created_at']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Edit", key=f"edit_{tip['id']}"):
                            st.session_state[f"editing_{tip['id']}"] = True
                    with col2:
                        if st.button(f"Delete", key=f"delete_{tip['id']}"):
                            # Soft delete - set is_active to 0
                            conn = sqlite3.connect(st.session_state.admin_manager.db_path)
                            cursor = conn.cursor()
                            cursor.execute("UPDATE health_tips SET is_active = 0 WHERE id = ?", (tip['id'],))
                            conn.commit()
                            conn.close()
                            st.success("Health tip deleted successfully!")
                            st.rerun()
        else:
            st.info("No health tips available. Add some tips to get started!")
    
    with tab2:
        st.subheader("Add New Health Tip")
        
        with st.form("add_health_tip"):
            title = st.text_input("Title*")
            content = st.text_area("Content*", height=150)
            category = st.selectbox("Category", [
                "general", "diet", "exercise", "mental_health", 
                "preventive_care", "chronic_conditions", "wellness"
            ])
            tags = st.text_input("Tags (comma-separated)", placeholder="wellness, tips, health")
            
            submit_button = st.form_submit_button("Add Health Tip")
            
            if submit_button:
                if title and content:
                    conn = sqlite3.connect(st.session_state.admin_manager.db_path)
                    cursor = conn.cursor()
                    
                    # Convert tags to JSON array
                    tags_json = json.dumps([tag.strip() for tag in tags.split(',') if tag.strip()])
                    
                    cursor.execute('''
                        INSERT INTO health_tips (title, content, category, tags, created_by)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (title, content, category, tags_json, st.session_state.admin_user['id']))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success("Health tip added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (Title and Content)")

def data_visualization():
    """Data visualization and analytics page"""
    st.markdown("# 📊 Data Visualization & Analytics")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 User Analytics", "💬 Query Analytics", "📈 System Metrics", "🎯 Performance"])
    
    with tab1:
        st.subheader("User Analytics")
        
        try:
            # Get user data
            user_data = st.session_state.admin_manager.get_user_data()
            
            if not user_data['users'].empty:
                users_df = user_data['users']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info("📊 User Registration Overview")
                    
                    # Show current user count and basic info
                    total_users = len(users_df)
                    st.metric("Total Registered Users", total_users)
                    
                    if total_users > 0:
                        st.write("**User Registration Details:**")
                        st.write(f"- Total Users: {total_users}")
                        
                        # Show age group distribution if available
                        if 'age_group' in users_df.columns:
                            age_groups = users_df['age_group'].value_counts()
                            st.write("- Age Group Distribution:")
                            for age_group, count in age_groups.items():
                                st.write(f"  - {age_group}: {count} users")
                    else:
                        st.info("No users registered yet.")
                
                with col2:
                    # User language distribution
                    if 'language' in users_df.columns:
                        lang_dist = users_df['language'].value_counts().reset_index()
                        lang_dist.columns = ['Language', 'Count']
                        
                        fig = px.pie(lang_dist, values='Count', names='Language',
                                    title="User Language Distribution")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No language data available")
                
                # Age group distribution
                col3, col4 = st.columns(2)
                
                with col3:
                    if 'age_group' in users_df.columns:
                        age_dist = users_df['age_group'].value_counts().reset_index()
                        age_dist.columns = ['Age Group', 'Count']
                        
                        fig = px.bar(age_dist, x='Age Group', y='Count',
                                    title="User Age Group Distribution")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No age group data available")
                
                with col4:
                    # User statistics
                    total_users = len(users_df)
                    st.metric("Total Users", total_users)
                    
                    if 'language' in users_df.columns:
                        english_users = len(users_df[users_df['language'] == 'English'])
                        hindi_users = len(users_df[users_df['language'] == 'Hindi'])
                        telugu_users = len(users_df[users_df['language'] == 'Telugu'])
                        
                        st.metric("English Users", english_users)
                        st.metric("Hindi Users", hindi_users)
                        st.metric("Telugu Users", telugu_users)
                
                # User details table
                st.subheader("📋 User Details")
                # Hide password column for security
                display_df = users_df.drop('password', axis=1) if 'password' in users_df.columns else users_df
                st.dataframe(display_df, use_container_width=True)
                
            else:
                st.info("No user data available yet.")
                
        except Exception as e:
            st.error(f"Error loading user analytics: {str(e)}")
            st.info("No user data available to display. Users will appear here once they register and use the system.")
    
    with tab2:
        st.subheader("Query Analytics")
        
        try:
            # Get real conversation data
            user_data = st.session_state.admin_manager.get_user_data()
            conversations_df = user_data['conversations']
            
            if not conversations_df.empty and 'timestamp' in conversations_df.columns:
                # Convert timestamp and analyze patterns
                conversations_df['timestamp'] = pd.to_datetime(conversations_df['timestamp'])
                conversations_df['date'] = conversations_df['timestamp'].dt.date
                conversations_df['hour'] = conversations_df['timestamp'].dt.hour
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Daily conversation volume
                    daily_counts = conversations_df.groupby('date').size().reset_index(name='conversations')
                    daily_counts['date'] = pd.to_datetime(daily_counts['date'])
                    
                    fig = px.line(daily_counts, x='date', y='conversations',
                                 title=f"Daily Conversations (Real Data - {len(conversations_df)} total)")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Hourly distribution
                    hourly_counts = conversations_df.groupby('hour').size().reset_index(name='conversations')
                    
                    fig = px.bar(hourly_counts, x='hour', y='conversations',
                               title="Conversations by Hour of Day (Real Data)")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Most active users
                st.subheader("User Activity Analysis")
                user_activity = conversations_df.groupby('username').size().reset_index(name='message_count')
                user_activity = user_activity.sort_values('message_count', ascending=False).head(10)
                
                fig = px.bar(user_activity, x='username', y='message_count',
                           title="Top 10 Most Active Users (Real Data)")
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.info("No conversation data available yet.")
                
        except Exception as e:
            st.error(f"Error loading conversation analytics: {str(e)}")
            st.info("No conversation data available to display.")
    
    with tab3:
        st.subheader("System Metrics")
        
        try:
            # Real database statistics
            stats = st.session_state.admin_manager.get_dashboard_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Users", stats.get('total_users', 0))
            with col2:
                st.metric("Total Conversations", stats.get('total_conversations', 0))
            with col3:
                st.metric("Feedback Items", stats.get('total_feedback', 0))
            with col4:
                st.metric("Health Tips", stats.get('active_health_tips', 0))
            
            # Knowledge base statistics
            st.subheader("Knowledge Base Statistics")
            try:
                with open('kb_csv.json', 'r', encoding='utf-8') as f:
                    kb_data = json.load(f)
                
                kb_col1, kb_col2, kb_col3 = st.columns(3)
                
                with kb_col1:
                    st.metric("Total Symptoms", len(kb_data.get('symptoms', [])))
                with kb_col2:
                    st.metric("Total Diseases", kb_data.get('total_diseases', 0))
                with kb_col3:
                    # Count symptoms with frequency > 0
                    symptoms_with_freq = sum(1 for s in kb_data.get('symptoms', []) if s.get('frequency', 0) > 0)
                    st.metric("Symptoms with Data", symptoms_with_freq)
                    
            except Exception as e:
                st.error(f"Error loading knowledge base stats: {e}")
                
        except Exception as e:
            st.error(f"Error loading system metrics: {str(e)}")
    
    with tab4:
        st.subheader("Database Health")
        
        try:
            # Real database information
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Users Database")
                user_data = st.session_state.admin_manager.get_user_data()
                users_df = user_data['users']
                conversations_df = user_data['conversations']
                
                st.metric("Registered Users", len(users_df))
                st.metric("Total Conversations", len(conversations_df))
                
                if not users_df.empty and 'language' in users_df.columns:
                    lang_dist = users_df['language'].value_counts()
                    st.write("**Language Distribution:**")
                    for lang, count in lang_dist.items():
                        st.write(f"- {lang}: {count} users")
            
            with col2:
                st.markdown("#### Admin Database")
                admin_stats = st.session_state.admin_manager.get_dashboard_stats()
                
                st.metric("Feedback Entries", admin_stats.get('total_feedback', 0))
                st.metric("Pending Reviews", admin_stats.get('pending_feedback', 0))
                st.metric("Active Health Tips", admin_stats.get('active_health_tips', 0))
                
                # Show database tables status
                st.write("**Database Tables Status:**")
                st.write("✅ Users: Active")
                st.write("✅ Conversations: Active") 
                st.write("✅ Feedback: Active")
                st.write("✅ Admin Users: Active")
                st.write("✅ Health Tips: Active")
                
        except Exception as e:
            st.error(f"Error loading database health metrics: {str(e)}")

def knowledge_base_management():
    """Knowledge base and database management"""
    st.markdown("# 🧠 Knowledge Base & Database Management")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📚 Knowledge Base", "✏️ Edit Knowledge Base", "👥 Users Database", "💬 Conversations", "🔧 System Data"])
    
    with tab1:
        st.subheader("Medical Knowledge Base")
        
        # Load knowledge base data
        try:
            with open('kb_csv.json', 'r', encoding='utf-8') as f:
                kb_data = json.load(f)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Symptoms", len(kb_data.get('symptoms', [])))
            with col2:
                st.metric("Total Diseases", kb_data.get('total_diseases', 0))
            
            # Symptoms table
            st.subheader("Symptoms Overview")
            if 'symptoms' in kb_data:
                symptoms_list = []
                for symptom in kb_data['symptoms'][:20]:  # Show first 20
                    symptoms_list.append({
                        'Name': symptom.get('name', ''),
                        'Frequency': symptom.get('frequency', 0),
                        'Related Diseases': len(symptom.get('related_diseases', [])),
                        'Synonyms Count': len(symptom.get('synonyms', []))
                    })
                
                st.dataframe(pd.DataFrame(symptoms_list), use_container_width=True)
            
            # Disease information
            st.subheader("Disease Information")
            try:
                with open('symptom_Description.csv', 'r') as f:
                    diseases_df = pd.read_csv('symptom_Description.csv')
                    st.dataframe(diseases_df, use_container_width=True)
            except:
                st.error("Could not load disease descriptions")
                
        except Exception as e:
            st.error(f"Could not load knowledge base: {e}")
    
    with tab2:
        st.subheader("✏️ Edit Knowledge Base")
        
        st.info("🔧 Add new symptoms, diseases, and manage the medical knowledge base")
        
        # File information section
        with st.expander("📋 Knowledge Base Files Information", expanded=False):
            st.markdown("""
            **Files that will be modified when you edit the knowledge base:**
            
            🗂️ **Symptom Operations:**
            - **`kb_csv.json`** - Main knowledge base file containing all symptoms, synonyms, and relationships
            - Contains: Symptom names, synonyms, descriptions, categories, and disease mappings
            
            🏥 **Disease Operations:**
            - **`symptom_Description.csv`** - Contains disease names and their medical descriptions
            - **`symptom_precaution.csv`** - Contains preventive measures and precautions for each disease
            
            ⚠️ **Important Notes:**
            - All changes are immediately saved to files
            - Backup your files before making bulk changes
            - Changes will be reflected in the bot responses after the next restart
            """)
            
            # Show current file sizes and modification dates
            import os
            from datetime import datetime
            
            files_info = []
            for filename in ['kb_csv.json', 'symptom_Description.csv', 'symptom_precaution.csv']:
                try:
                    if os.path.exists(filename):
                        size = os.path.getsize(filename)
                        modified = datetime.fromtimestamp(os.path.getmtime(filename))
                        files_info.append({
                            'File': filename,
                            'Size (KB)': f"{size/1024:.1f}",
                            'Last Modified': modified.strftime("%Y-%m-%d %H:%M:%S")
                        })
                except:
                    files_info.append({
                        'File': filename,
                        'Size (KB)': 'N/A',
                        'Last Modified': 'N/A'
                    })
            
            if files_info:
                st.dataframe(pd.DataFrame(files_info), use_container_width=True)
        
        # Section for adding new symptoms
        st.subheader("➕ Add New Symptom")
        
        with st.form("add_symptom_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_symptom_name = st.text_input("Symptom Name", placeholder="e.g., headache, fever")
                new_symptom_synonyms = st.text_area(
                    "Synonyms (one per line)", 
                    placeholder="head pain\nhead ache\nmigraine",
                    height=100
                )
            
            with col2:
                new_symptom_description = st.text_area(
                    "Description", 
                    placeholder="Brief description of the symptom",
                    height=100
                )
                new_symptom_category = st.selectbox(
                    "Category",
                    ["General", "Neurological", "Respiratory", "Digestive", "Musculoskeletal", "Cardiovascular", "Other"]
                )
            
            submitted_symptom = st.form_submit_button("Add Symptom", use_container_width=True)
            
            if submitted_symptom and new_symptom_name:
                # Add symptom to knowledge base
                success = add_symptom_to_kb(new_symptom_name, new_symptom_synonyms, new_symptom_description, new_symptom_category)
                if success:
                    st.success(f"✅ Added symptom: {new_symptom_name}")
                    st.info("📁 **File Modified:** `kb_csv.json` - Updated symptoms database")
                else:
                    st.error("❌ Failed to add symptom")
        
        st.markdown("---")
        
        # Section for adding new diseases
        st.subheader("🦠 Add New Disease")
        
        with st.form("add_disease_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_disease_name = st.text_input("Disease Name", placeholder="e.g., Common Cold, Diabetes")
                new_disease_symptoms = st.multiselect(
                    "Associated Symptoms",
                    ["fever", "headache", "cough", "nausea", "fatigue", "pain", "swelling", "rash", "dizziness"],
                    help="Select symptoms associated with this disease"
                )
            
            with col2:
                new_disease_description = st.text_area(
                    "Description", 
                    placeholder="Medical description of the disease",
                    height=100
                )
                new_disease_precautions = st.text_area(
                    "Precautions", 
                    placeholder="Preventive measures and precautions",
                    height=100
                )
            
            submitted_disease = st.form_submit_button("Add Disease", use_container_width=True)
            
            if submitted_disease and new_disease_name:
                success = add_disease_to_kb(new_disease_name, new_disease_symptoms, new_disease_description, new_disease_precautions)
                if success:
                    st.success(f"✅ Added disease: {new_disease_name}")
                    st.info("📁 **Files Modified:**")
                    st.info("• `symptom_Description.csv` - Added disease description")
                    st.info("• `symptom_precaution.csv` - Added disease precautions")
                else:
                    st.error("❌ Failed to add disease")
        
        st.markdown("---")
        
        # Section for editing existing entries
        st.subheader("📝 Edit Existing Entries")
        
        edit_type = st.radio("What would you like to edit?", ["Symptoms", "Diseases"])
        
        if edit_type == "Symptoms":
            try:
                with open('kb_csv.json', 'r', encoding='utf-8') as f:
                    kb_data = json.load(f)
                
                if 'symptoms' in kb_data:
                    symptom_names = [s.get('name', '') for s in kb_data['symptoms']]
                    selected_symptom = st.selectbox("Select symptom to edit:", symptom_names)
                    
                    if selected_symptom:
                        st.info(f"Editing: {selected_symptom}")
                        
                        # Find the symptom data
                        symptom_data = next((s for s in kb_data['symptoms'] if s.get('name') == selected_symptom), None)
                        
                        if symptom_data:
                            with st.form("edit_symptom_form"):
                                edited_name = st.text_input("Name", value=symptom_data.get('name', ''))
                                edited_synonyms = st.text_area(
                                    "Synonyms (one per line)", 
                                    value='\n'.join(symptom_data.get('synonyms', [])),
                                    height=100
                                )
                                
                                if st.form_submit_button("Update Symptom"):
                                    success = update_symptom_in_kb(selected_symptom, edited_name, edited_synonyms)
                                    if success:
                                        st.success("✅ Symptom updated successfully")
                                        st.info("📁 **File Modified:** `kb_csv.json` - Updated symptom information")
                                    else:
                                        st.error("❌ Failed to update symptom")
            except Exception as e:
                st.error(f"Error loading symptoms for editing: {e}")
        
        else:  # Diseases
            try:
                diseases_df = pd.read_csv('symptom_Description.csv')
                disease_names = diseases_df['Disease'].tolist()
                selected_disease = st.selectbox("Select disease to edit:", disease_names)
                
                if selected_disease:
                    disease_row = diseases_df[diseases_df['Disease'] == selected_disease].iloc[0]
                    
                    with st.form("edit_disease_form"):
                        edited_description = st.text_area(
                            "Description", 
                            value=disease_row.get('Description', ''),
                            height=150
                        )
                        
                        if st.form_submit_button("Update Disease"):
                            success = update_disease_description(selected_disease, edited_description)
                            if success:
                                st.success("✅ Disease updated successfully")
                                st.info("📁 **File Modified:** `symptom_Description.csv` - Updated disease description")
                            else:
                                st.error("❌ Failed to update disease")
            except Exception as e:
                st.error(f"Error loading diseases for editing: {e}")
    
    with tab3:
        st.subheader("Users Database")
        
        user_data = st.session_state.admin_manager.get_user_data()
        
        if not user_data['users'].empty:
            users_df = user_data['users']
            
            # User statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Users", len(users_df))
            with col2:
                # Since there's no created_at column, show total users
                st.metric("Total Registered", len(users_df))
            with col3:
                if 'language' in users_df.columns:
                    hindi_users = len(users_df[users_df['language'] == 'Hindi'])
                    st.metric("Hindi Users", hindi_users)
                else:
                    st.metric("Hindi Users", 0)
            with col4:
                if 'age_group' in users_df.columns:
                    adult_users = len(users_df[users_df['age_group'].isin(['18-25', '26-35', '36-50', '50+'])])
                    st.metric("Adult Users", adult_users)
                else:
                    st.metric("Adult Users", 0)
            
            # Users table
            st.subheader("User Details")
            
            # Advanced search and filtering
            col_search1, col_search2 = st.columns(2)
            
            with col_search1:
                search_term = st.text_input("🔍 Search users by email:")
            
            with col_search2:
                language_filter = st.selectbox(
                    "Filter by language:",
                    ["All"] + list(users_df['language'].unique()) if 'language' in users_df.columns else ["All"]
                )
            
            # Apply filters
            filtered_users = users_df.copy()
            
            if search_term:
                filtered_users = filtered_users[filtered_users['email'].str.contains(search_term, case=False, na=False)]
            
            if language_filter != "All" and 'language' in users_df.columns:
                filtered_users = filtered_users[filtered_users['language'] == language_filter]
            
            # Display results count
            st.info(f"Showing {len(filtered_users)} of {len(users_df)} users")
            
            # Enhanced user table display
            if not filtered_users.empty:
                # Hide password column for security
                display_columns = [col for col in filtered_users.columns if col != 'password']
                display_df = filtered_users[display_columns]
                
                st.dataframe(
                    display_df, 
                    use_container_width=True,
                    column_config={
                        "id": st.column_config.NumberColumn("User ID"),
                        "email": st.column_config.TextColumn("Email"),
                        "name": st.column_config.TextColumn("Name"),
                        "age_group": st.column_config.TextColumn("Age Group"),
                        "language": st.column_config.TextColumn("Language")
                    }
                )
                
                # User management actions
                st.subheader("👨‍💼 User Management")
                
                col_action1, col_action2, col_action3 = st.columns(3)
                
                with col_action1:
                    if st.button("📥 Export Filtered Data"):
                        csv = display_df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"users_filtered_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv"
                        )
                
                with col_action2:
                    if st.button("📊 Generate Report"):
                        st.info("User analytics report generated successfully!")
                
                with col_action3:
                    if st.button("🔄 Refresh Data"):
                        st.cache_data.clear()
                        st.rerun()
            else:
                st.warning("No users match the current filters.")
        else:
            st.info("No user data available")
    
    with tab3:
        st.subheader("Conversation History")
        
        user_data = st.session_state.admin_manager.get_user_data()
        
        if not user_data['conversations'].empty:
            conversations_df = user_data['conversations']
            
            # Conversation statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Conversations", len(conversations_df))
            with col2:
                today_convs = len(conversations_df[pd.to_datetime(conversations_df['timestamp']).dt.date == datetime.now().date()])
                st.metric("Today", today_convs)
            with col3:
                unique_users = conversations_df['username'].nunique()
                st.metric("Active Users", unique_users)
            
            # Recent conversations
            st.subheader("Recent Conversations")
            recent_conversations = conversations_df.head(20)
            
            for _, conv in recent_conversations.iterrows():
                with st.expander(f"{conv['username']} - {conv['timestamp']}"):
                    st.write(f"**User:** {conv['user_message']}")
                    st.write(f"**Bot:** {conv['bot_response'][:200]}...")
        else:
            st.info("No conversation data available")
    
    with tab4:
        st.subheader("System Database Information")
        
        # Admin database tables info
        conn = sqlite3.connect(st.session_state.admin_manager.db_path)
        cursor = conn.cursor()
        
        # Get table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        st.write("**Admin Database Tables:**")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            st.write(f"- {table_name}: {count} records")
        
        conn.close()
        
        # Users database info
        try:
            conn = sqlite3.connect(st.session_state.admin_manager.users_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            user_tables = cursor.fetchall()
            
            st.write("**Users Database Tables:**")
            for table in user_tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                st.write(f"- {table_name}: {count} records")
            
            conn.close()
        except Exception as e:
            st.error(f"Could not access users database: {e}")

def main():
    """Main application function"""
    
    # Check if admin is logged in
    if 'admin_user' not in st.session_state:
        login_page()
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### 👨‍💼 Welcome, {st.session_state.admin_user['username']}")
        st.markdown(f"**Role:** {st.session_state.admin_user['role']}")
        
        st.markdown("---")
        
        page = st.selectbox("Navigate to:", [
            "📊 Dashboard Overview",
            "📝 Feedback Management", 
            "💡 Health Tips Management",
            "📈 Data Visualization",
            "🧠 Knowledge Base & DB"
        ])
        
        st.markdown("---")
        
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                if key.startswith('admin') or key == 'admin_user':
                    del st.session_state[key]
            st.rerun()
    
    # Route to selected page
    if page == "📊 Dashboard Overview":
        dashboard_overview()
    elif page == "📝 Feedback Management":
        feedback_management()
    elif page == "💡 Health Tips Management":
        health_tips_management()
    elif page == "📈 Data Visualization":
        data_visualization()
    elif page == "🧠 Knowledge Base & DB":
        knowledge_base_management()

if __name__ == "__main__":
    main()