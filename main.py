# pip install streamlit langchain langchain-google-genai PyPDF2 python-docx


import streamlit as st
import os
from PyPDF2 import PdfReader
from docx import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Page config
st.set_page_config(page_title="Document Analyzer", page_icon="📄", layout="wide")

# Title
st.title("📄 Document Analyzer & Summarizer")
st.markdown("Upload your document (PDF, DOCX, or TXT) and get AI-powered analysis!")

# Sidebar for API key
with st.sidebar:
    st.header("🔑 Configuration")
    api_key = st.text_input("Google API Key", type="password", help="Enter your Google Gemini API key")
    
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        st.success("API Key configured!")

# File upload
uploaded_file = st.file_uploader(
    "Choose a file", 
    type=['pdf', 'docx', 'txt'],
    help="Upload PDF, DOCX, or TXT files"
)

def extract_text(file):
    """Extract text from uploaded file"""
    text = ""
    
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        
        elif file.type == "text/plain":
            text = str(file.read(), "utf-8")
            
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return ""
    
    return text

def analyze_document(text, query):
    """Analyze document based on specific query"""
    
    try:
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            temperature=0.3,
            max_tokens=1024,
            google_api_key=os.environ["GOOGLE_API_KEY"]
        )
        
        # Create improved prompt template that responds to specific queries
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are an intelligent document assistant. Given the following document content:

"{context}"

Answer the following user question as specifically and accurately as possible, using only the information from the document. 

User question: {question}

Instructions:
- If the question asks for a summary, provide a comprehensive summary
- If the question asks for specific information, focus only on that information
- If the question asks about risks, focus on risks mentioned in the document
- If the question asks about recommendations, focus on recommendations
- If the information is not found in the document, clearly state "This information is not available in the provided document"
- Format your response clearly with appropriate headers and bullet points where helpful

Answer:
"""
        )
        
        # Create chain and get response
        chain = LLMChain(llm=llm, prompt=prompt_template)
        response = chain.invoke({"context": text, "question": query})
        
        return response["text"]
        
    except Exception as e:
        st.error(f"Error analyzing document: {str(e)}")
        return None

# Main interface
if uploaded_file and api_key:
    
    # Extract text
    with st.spinner("Extracting text from document..."):
        raw_text = extract_text(uploaded_file)
    
    if raw_text:
        st.success(f"✅ Document processed! Extracted {len(raw_text)} characters.")
        
        # Show document preview
        with st.expander("📖 Document Preview"):
            preview_text = raw_text[:2000] + "..." if len(raw_text) > 2000 else raw_text
            st.text_area("Content Preview", preview_text, height=300)
        
        # Query section
        st.subheader("🤔 Ask Questions About Your Document")
        
        # Predefined queries
        col1, col2, col3 = st.columns(3)
        
        query = None
        
        with col1:
            if st.button("📋 Summarize", use_container_width=True):
                query = "Provide a comprehensive summary of this document including the main points, key information, and important details."
        
        with col2:
            if st.button("🔍 Key Points", use_container_width=True):
                query = "What are the key points, main findings, and most important information in this document?"
        
        with col3:
            if st.button("⚠️ Risks & Issues", use_container_width=True):
                query = "What risks, challenges, problems, or issues are mentioned in this document?"
        
        # Additional predefined queries
        col4, col5, col6 = st.columns(3)
        
        with col4:
            if st.button("💡 Recommendations", use_container_width=True):
                query = "What recommendations, suggestions, or proposed solutions are mentioned in this document?"
        
        with col5:
            if st.button("📊 Technical Details", use_container_width=True):
                query = "What are the technical specifications, methodologies, or technical details mentioned in this document?"
        
        with col6:
            if st.button("🎯 Conclusions", use_container_width=True):
                query = "What are the conclusions, final thoughts, or outcomes mentioned in this document?"
        
        # Custom query
        st.markdown("---")
        custom_query = st.text_area(
            "Or ask your own specific question:", 
            placeholder="e.g., What is the main purpose of this system? What technologies were used? What are the future improvements mentioned?", 
            height=100
        )
        
        if st.button("🚀 Ask Question", use_container_width=True) and custom_query:
            query = custom_query
        
        # Process query
        if query:
            with st.spinner("Analyzing document... This may take a moment."):
                result = analyze_document(raw_text, query)
                
                if result:
                    st.subheader("🎯 Analysis Results")
                    st.markdown("---")
                    
                    # Show the question that was asked
                    st.markdown(f"**Question:** {query}")
                    st.markdown("**Answer:**")
                    st.markdown(result)
                    
                    # Download option
                    download_content = f"Question: {query}\n\nAnswer:\n{result}"
                    st.download_button(
                        label="📥 Download Answer",
                        data=download_content,
                        file_name="document_analysis.txt",
                        mime="text/plain"
                    )
    
    else:
        st.error("❌ Could not extract text from the document. Please check the file format.")

elif not api_key:
    st.warning("⚠️ Please enter your Google API Key in the sidebar to continue.")
    st.info("💡 You can get your API key from Google AI Studio: https://makersuite.google.com/app/apikey")
    
elif not uploaded_file:
    st.info("👆 Please upload a document to get started.")
    
    # Instructions
    with st.expander("📚 How to use this app"):
        st.markdown("""
        ### Steps to use:
        1. **Get API Key**: Obtain your Google Gemini API key from Google AI Studio
        2. **Enter API Key**: Paste it in the sidebar
        3. **Upload Document**: Choose a PDF, DOCX, or TXT file
        4. **Ask Questions**: Use predefined buttons or write custom queries
        5. **Get Analysis**: Receive AI-powered insights about your document
        
        ### Example questions you can ask:
        - What is the main purpose of this document?
        - What technologies or tools are mentioned?
        - What are the key findings or results?
        - What problems does this solve?
        - What are the future improvements suggested?
        - Who are the target users or audience?
        """)

# Footer
st.markdown("---")
st.markdown("🚀 Built with Streamlit & LangChain | Powered by Google Gemini")
