import ollama

def test_local_ai_enrichment():
    # Hardcoding the exact outputs from your successful previous runs to test the AI isolation
    transcript = (
        "If you want to clear the Claude AI Architect certification, one of the most valuable "
        "AI certifications right now, this video will save you hours of searching. I built a complete "
        "preparation hub myself. Inside it, you'll get a seven day study plan, a 91 page study guide "
        "on every exam domain and scenario. 33 practice questions from a real exam taker, all 18 free "
        "anthropic academy courses. Everything is structured in one place so you can prepare properly."
    )
    
    ocr_text = (
        "Agentic Architectures: Subagent spawning | Model Context Protocol: MCP | Batch Processing & State | "
        "Tool & Schema Design: Enforcing business rules | Domain 1: Agentic Architecture | Context Management"
    )
    
    print("🧠 Contacting local Qwen3 model via Ollama...")
    
    # We construct a dense developer prompt instructing the model to return exactly what Notion requires
    prompt = f"""
    You are an expert technical knowledge-management assistant. 
    Analyze the following transcript and video text (OCR) extracted from a public educational reel.
    
    Transcript: {transcript}
    OCR Text: {ocr_text}
    
    Strictly extract and format your response into these exact fields:
    Title: [A short, crisp title for this video block]
    Summary: [A concise 1-2 sentence high-level summary detailing the core value]
    Category: [Select exactly ONE from this list: AI, Machine Learning, Startups, Business, Real Estate, Productivity, Marketing, Finance, Fitness]
    Tags: [Provide 2-4 technical keywords separated by commas]
    """
    
    try:
        response = ollama.chat(
            model='qwen3:8b',
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        print("\n================== 🌟 LOCAL AI PARSING OUTPUT 🌟 ==================\n")
        print(response['message']['content'])
        print("\n==================================================================")
        
    except Exception as e:
        print(f"❌ Ollama communication fault: {e}")

if __name__ == "__main__":
    test_local_ai_enrichment()