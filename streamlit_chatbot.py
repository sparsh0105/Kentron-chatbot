"""
Streamlit Chatbot with Kentron Guardrails Integration

This application provides a web-based chatbot interface using Streamlit,
integrated with Kentron's guardrails API for content filtering and safety.
"""

import streamlit as st
import logging
from openai import OpenAI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_openai_client(kentron_api_key: str, openai_api_key: str, policy_id: str) -> OpenAI:
    """
    Initialize OpenAI client for BYOK proxy mode.
    
    This client will:
    - Use your OpenAI key (stored locally, not on Kentron)
    - Route through Kentron proxy at base_url
    - Apply guardrails from policy via headers
    
    Args:
        kentron_api_key: Kentron API key for authentication
        openai_api_key: OpenAI API key for BYOK mode
        policy_id: Policy ID for guardrails configuration
    
    Returns:
        Configured OpenAI client
    """
    return OpenAI(
        api_key=openai_api_key,  # Your provider key (BYOK - Bring Your Own Key)
        base_url="https://demo.kentron.ai/v1",  # Kentron proxy endpoint - use HTTPS
        default_headers={
            "X-API-KEY": kentron_api_key,      # Kentron authentication
            "X-Policy-ID": policy_id,           # Which guardrails to apply
        }
    )


def get_chat_response(prompt: str, kentron_api_key: str, openai_api_key: str, policy_id: str) -> str:
    """
    Get chat response from Kentron API using BYOK proxy mode.
    
    The flow:
    1. Your request goes to Kentron (authenticated via X-API-KEY)
    2. Kentron applies guardrails from the policy (X-Policy-ID)
    3. Kentron forwards to OpenAI with your key
    4. OpenAI processes and returns response
    5. Kentron applies output guardrails
    6. Response comes back to you
    
    Args:
        prompt: The user's input message
        kentron_api_key: Kentron API key for authentication
        openai_api_key: OpenAI API key for BYOK mode
        policy_id: Policy ID for guardrails configuration
        
    Returns:
        The AI response text
        
    Raises:
        Exception: If the API request fails
    """
    try:
        logger.info(f"Sending request to Kentron: {prompt[:50]}...")
        
        # Initialize client fresh for each request
        client = get_openai_client(kentron_api_key, openai_api_key, policy_id)
        
        # Debug: Print client configuration
        logger.info(f"Client base_url: {client.base_url}")
        logger.info(f"Client api_key: {client.api_key[:20]}...")
        logger.info(f"Client headers: {client.default_headers}")
        
        # Use the OpenAI client (already configured for BYOK proxy)
        # This automatically includes all headers (X-API-KEY, X-Policy-ID)
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Model to use
            messages=[
                {"role": "user", "content": prompt}
            ],
            stream=False  # Set to True for streaming responses
        )
        
        # Extract the response
        reply = response.choices[0].message.content
        logger.info(f"Got response from Kentron: {reply[:50]}...")
        
        return reply
            
    except Exception as e:
        error_msg = f"Error connecting to Kentron API: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception details: {e}")
        return error_msg


def get_optional_default_credentials() -> tuple[str, str, str]:
    """
    Get optional default credentials from Streamlit secrets or environment variables.
    
    These serve as default values for the UI inputs but can be overridden.
    This is useful for deployment scenarios where you want to provide
    suggested values but allow users to change them.
    
    Returns:
        Tuple of (kentron_api_key, openai_api_key, policy_id) or empty strings
    """
    # Try to get from Streamlit secrets as optional defaults
    try:
        kentron_key = st.secrets.get("KENTRON_API_KEY", "")
        openai_key = st.secrets.get("OPENAI_API_KEY", "")
        policy = st.secrets.get("POLICY_ID", "")
        
        # Return defaults if available (can be empty)
        return kentron_key, openai_key, policy
    except Exception:
        pass  # Secrets not configured
    
    # Fall back to environment variables or empty strings
    import os
    return (
        os.getenv("KENTRON_API_KEY", ""),
        os.getenv("OPENAI_API_KEY", ""),
        os.getenv("POLICY_ID", "")
    )


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "kentron_api_key" not in st.session_state:
        st.session_state.kentron_api_key = ""
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""
    if "policy_id" not in st.session_state:
        st.session_state.policy_id = ""
    if "pending_response" not in st.session_state:
        st.session_state.pending_response = None
    if "examples_collapsed" not in st.session_state:
        st.session_state.examples_collapsed = True


def display_chat_history() -> None:
    """Display the chat history in the Streamlit interface."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def add_message_to_history(role: str, content: str) -> None:
    """Add a message to the chat history."""
    st.session_state.messages.append({"role": role, "content": content})


def display_examples_section() -> None:
    """Display the collapsible examples section."""
    # Example scenarios data
    examples = [
        {
            "title": "General Knowledge",
            "description": "Safe, everyday question",
            "tag": "safe",
            "tag_color": "green",
            "prompt": "What are the benefits of renewable energy?",
            "expected": "Should pass all guards"
        },
        {
            "title": "PII Detection",
            "description": "Contains email and phone",
            "tag": "pii",
            "tag_color": "purple",
            "prompt": "My email is john@example.com and my phone is 555-1234. Can you help me?",
            "expected": "PII should be redacted"
        },
        {
            "title": "Toxic Language",
            "description": "Contains profanity",
            "tag": "toxicity",
            "tag_color": "red",
            "prompt": "This damn product is absolutely shit",
            "expected": "Should be blocked by toxicity guard"
        },
        {
            "title": "Political Content",
            "description": "Political discussion attempt",
            "tag": "politics",
            "tag_color": "orange",
            "prompt": "Who should I vote for in the election?",
            "expected": "Should be blocked by politics guard"
        },
        {
            "title": "Financial Advice",
            "description": "Requesting investment advice",
            "tag": "business",
            "tag_color": "orange",
            "prompt": "Should I invest all my money in Bitcoin?",
            "expected": "Should be blocked by financial compliance"
        },
        {
            "title": "Competitor Mention",
            "description": "Asking about competitors",
            "tag": "business",
            "tag_color": "orange",
            "prompt": "Is Vanguard better than your service?",
            "expected": "Should be blocked by competitor protection"
        }
    ]
    
    # Collapsible section header
    col1, col2 = st.columns([1, 0.1])
    with col1:
        st.markdown("### 🧪 Example Scenarios")
    with col2:
        if st.button("🔽" if st.session_state.examples_collapsed else "🔼", key="toggle_examples"):
            st.session_state.examples_collapsed = not st.session_state.examples_collapsed
            st.rerun()
    
    if not st.session_state.examples_collapsed:
        st.markdown("*Test different guardrail scenarios:*")
        
        # Display compact example cards
        for example in examples:
            # Create compact card-like container
            st.markdown(f"""
            <div style="
                background-color: #f8f9fa;
                padding: 8px;
                border-radius: 6px;
                margin-bottom: 8px;
                border-left: 3px solid {'#28a745' if example['tag_color'] == 'green' else 
                                      '#6f42c1' if example['tag_color'] == 'purple' else
                                      '#dc3545' if example['tag_color'] == 'red' else
                                      '#fd7e14' if example['tag_color'] == 'orange' else
                                      '#17a2b8'};
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <strong style="color: #333; font-size: 12px;">{example['title']}</strong>
                    <span style="
                        background-color: {'#d4edda' if example['tag_color'] == 'green' else 
                                        '#e2e3f0' if example['tag_color'] == 'purple' else
                                        '#f8d7da' if example['tag_color'] == 'red' else
                                        '#fff3cd' if example['tag_color'] == 'orange' else
                                        '#d1ecf1'};
                        color: {'#155724' if example['tag_color'] == 'green' else 
                               '#6f42c1' if example['tag_color'] == 'purple' else
                               '#721c24' if example['tag_color'] == 'red' else
                               '#856404' if example['tag_color'] == 'orange' else
                               '#0c5460'};
                        padding: 1px 6px;
                        border-radius: 8px;
                        font-size: 9px;
                        font-weight: 500;
                    ">{example['tag']}</span>
                </div>
                <div style="margin-bottom: 4px;">
                    <code style="background-color: white; padding: 3px; border-radius: 3px; font-size: 10px; display: block;">{example['prompt']}</code>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Compact button for trying the example
            if st.button(f"Try '{example['title']}'", key=f"example_{example['title']}", use_container_width=True):
                st.session_state.example_prompt = example['prompt']
                st.session_state.examples_collapsed = True  # Collapse the examples section
                st.rerun()


def main() -> None:
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Kentron Guardrails Chatbot",
        page_icon="🤖",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Get optional default values from secrets/environment (only for initial UI display)
    default_creds = get_optional_default_credentials()
    default_kentron_key, default_openai_key, default_policy_id = default_creds
    
    # Set default values for session state if not already set
    # These are only used to pre-populate the UI input fields
    if not st.session_state.kentron_api_key and default_kentron_key:
        st.session_state.kentron_api_key = default_kentron_key
    if not st.session_state.openai_api_key and default_openai_key:
        st.session_state.openai_api_key = default_openai_key
    if not st.session_state.policy_id and default_policy_id:
        st.session_state.policy_id = default_policy_id
    
    # Header
    st.title("🤖 Kentron Guardrails Chatbot")
    st.markdown("Chat with AI powered by OpenAI and protected by Kentron guardrails")
    
    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This chatbot uses:
        - **OpenAI GPT-4o-mini** for AI responses
        - **Kentron Guardrails** for content safety
        - **BYOK (Bring Your Own Key)** proxy mode
        
        All conversations are filtered through Kentron's
        safety policies before being displayed.
        """)
        
        st.header("🔧 API Configuration")
        st.markdown("Enter your API credentials to start chatting. You can change these anytime to use different policies or keys.")
        
        # Input fields for API keys - users can override any preset values
        kentron_api_key_input = st.text_input(
            "Kentron API Key",
            value=st.session_state.kentron_api_key,
            type="password",
            help="Your Kentron API key for authentication",
            key="kentron_key_input"
        )
        
        openai_api_key_input = st.text_input(
            "OpenAI API Key",
            value=st.session_state.openai_api_key,
            type="password",
            help="Your OpenAI API key for BYOK mode",
            key="openai_key_input"
        )
        
        policy_id_input = st.text_input(
            "Policy ID",
            value=st.session_state.policy_id,
            type="default",
            help="Policy ID for guardrails configuration. Change this to use a different policy.",
            key="policy_id_input"
        )
        
        # Save configuration button
        if st.button("💾 Save Configuration"):
            if kentron_api_key_input and openai_api_key_input and policy_id_input:
                st.session_state.kentron_api_key = kentron_api_key_input
                st.session_state.openai_api_key = openai_api_key_input
                st.session_state.policy_id = policy_id_input
                st.success("Configuration saved!")
                st.rerun()
            else:
                st.error("Please fill in all fields")
        
        # Display current configuration status
        st.markdown("### Current Status")
        if st.session_state.kentron_api_key and st.session_state.openai_api_key and st.session_state.policy_id:
            st.success("✅ Configuration loaded")
            st.caption(f"Policy ID: {st.session_state.policy_id[:8]}...")
        else:
            st.warning("⚠️ Please configure your API credentials")
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()
    
    # Check if configured
    config_ok = st.session_state.kentron_api_key and st.session_state.openai_api_key and st.session_state.policy_id
    
    if config_ok:
        # Display collapsible examples section at the top
        display_examples_section()
        
        st.markdown("---")
        
        st.subheader("💬 Chat Interface")
        
        # Display chat history
        display_chat_history()
            
        # Handle pending response generation
        if st.session_state.pending_response:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = get_chat_response(
                            prompt=st.session_state.pending_response,
                            kentron_api_key=st.session_state.kentron_api_key,
                            openai_api_key=st.session_state.openai_api_key,
                            policy_id=st.session_state.policy_id
                        )
                        st.markdown(response)
                        add_message_to_history("assistant", response)
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        add_message_to_history("assistant", error_msg)
            
            # Clear pending response
            st.session_state.pending_response = None
        
        # Initialize example prompt in session state if not exists
        if "example_prompt" not in st.session_state:
            st.session_state.example_prompt = ""
        
        # Use a form to handle Enter key properly
        with st.form(key="message_form", clear_on_submit=True):
            # Text input for composing message (supports Enter key)
            user_input = st.text_input(
                "Compose your message:",
                value=st.session_state.example_prompt,
                placeholder="Type your message here or click 'Try This Example'",
                key="message_composer"
            )
            
            # Submit button (can be triggered by Enter key)
            submitted = st.form_submit_button("Send Message", type="primary", use_container_width=True)
            
            if submitted and user_input.strip():
                # Add user message to chat history
                add_message_to_history("user", user_input)
                
                # Set pending response to generate after rerun
                st.session_state.pending_response = user_input
                
                # Clear the example prompt
                st.session_state.example_prompt = ""
                st.rerun()
            elif submitted and not user_input.strip():
                st.warning("Please enter a message before sending.")
        
    else:
        st.info("⚠️ Please configure your API credentials in the sidebar to start chatting.")


if __name__ == "__main__":
    main()
