"""
Create a Test PDF for RAG System Testing

This creates a simple PDF document about AI and Machine Learning
that we can use to test the RAG system.
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
import os

def create_test_pdf(filename="test_document.pdf"):
    """
    Create a test PDF about AI and Machine Learning.
    """
    
    # Create the PDF
    doc = SimpleDocTemplate(filename, pagesize=letter)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='darkblue',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Heading style
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='darkblue',
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Normal paragraph style
    normal_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    # Title
    title = Paragraph("Introduction to Artificial Intelligence and Machine Learning", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Page 1: Introduction
    heading1 = Paragraph("Chapter 1: What is Artificial Intelligence?", heading_style)
    elements.append(heading1)
    
    text1 = """
    Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, 
    especially computer systems. These processes include learning, reasoning, and self-correction. 
    AI has become one of the most transformative technologies of the 21st century, impacting 
    various sectors including healthcare, finance, transportation, and education.
    """
    elements.append(Paragraph(text1, normal_style))
    
    text2 = """
    The history of AI dates back to the 1950s when Alan Turing proposed the Turing Test as a 
    measure of machine intelligence. Since then, AI has evolved significantly, with major 
    breakthroughs in areas such as natural language processing, computer vision, and robotics.
    """
    elements.append(Paragraph(text2, normal_style))
    
    text3 = """
    Modern AI systems can perform tasks that traditionally required human intelligence, such as 
    understanding natural language, recognizing patterns in data, making decisions, and even 
    creating art and music. The goal of AI research is to create systems that can function 
    intelligently and independently.
    """
    elements.append(Paragraph(text3, normal_style))
    
    # Page 2: Machine Learning
    elements.append(PageBreak())
    
    heading2 = Paragraph("Chapter 2: Machine Learning Fundamentals", heading_style)
    elements.append(heading2)
    
    text4 = """
    Machine Learning (ML) is a subset of artificial intelligence that focuses on the development 
    of algorithms and statistical models that enable computers to improve their performance on 
    tasks through experience. Unlike traditional programming where explicit instructions are 
    provided, machine learning systems learn from data.
    """
    elements.append(Paragraph(text4, normal_style))
    
    text5 = """
    There are three main types of machine learning: supervised learning, unsupervised learning, 
    and reinforcement learning. Supervised learning involves training a model on labeled data, 
    where the correct outputs are known. Unsupervised learning works with unlabeled data to 
    discover hidden patterns. Reinforcement learning trains agents to make sequences of decisions 
    by rewarding desired behaviors.
    """
    elements.append(Paragraph(text5, normal_style))
    
    text6 = """
    Popular machine learning algorithms include linear regression, decision trees, random forests, 
    support vector machines, and neural networks. Each algorithm has its strengths and is suited 
    for different types of problems. The choice of algorithm depends on factors such as the 
    nature of the data, the size of the dataset, and the specific task at hand.
    """
    elements.append(Paragraph(text6, normal_style))
    
    # Page 3: Deep Learning
    elements.append(PageBreak())
    
    heading3 = Paragraph("Chapter 3: Deep Learning and Neural Networks", heading_style)
    elements.append(heading3)
    
    text7 = """
    Deep Learning is a specialized branch of machine learning that uses artificial neural networks 
    with multiple layers (hence "deep") to model and understand complex patterns in data. Deep 
    learning has been particularly successful in areas such as image recognition, speech 
    recognition, and natural language processing.
    """
    elements.append(Paragraph(text7, normal_style))
    
    text8 = """
    Neural networks are inspired by the structure and function of the human brain. They consist 
    of interconnected nodes (neurons) organized in layers. Information flows through the network, 
    with each connection having a weight that adjusts as the network learns. The training process 
    involves adjusting these weights to minimize prediction errors.
    """
    elements.append(Paragraph(text8, normal_style))
    
    text9 = """
    Convolutional Neural Networks (CNNs) are particularly effective for image processing tasks, 
    while Recurrent Neural Networks (RNNs) and their variants like LSTM (Long Short-Term Memory) 
    are well-suited for sequential data such as text and time series. Transformer architectures, 
    introduced in 2017, have revolutionized natural language processing and are the foundation 
    of models like GPT and BERT.
    """
    elements.append(Paragraph(text9, normal_style))
    
    # Page 4: Applications
    elements.append(PageBreak())
    
    heading4 = Paragraph("Chapter 4: Real-World Applications of AI", heading_style)
    elements.append(heading4)
    
    text10 = """
    AI has numerous practical applications across various industries. In healthcare, AI systems 
    assist in disease diagnosis, drug discovery, and personalized treatment plans. Medical imaging 
    AI can detect anomalies in X-rays, MRIs, and CT scans with accuracy comparable to or 
    exceeding human radiologists.
    """
    elements.append(Paragraph(text10, normal_style))
    
    text11 = """
    In finance, AI algorithms are used for fraud detection, algorithmic trading, credit scoring, 
    and risk assessment. Banks and financial institutions use machine learning to analyze 
    transaction patterns and identify suspicious activities in real-time, protecting customers 
    from fraud.
    """
    elements.append(Paragraph(text11, normal_style))
    
    text12 = """
    Autonomous vehicles rely heavily on AI technologies, including computer vision for object 
    detection, sensor fusion for environment understanding, and reinforcement learning for 
    decision-making. Companies like Tesla, Waymo, and Cruise are developing self-driving cars 
    that promise to transform transportation.
    """
    elements.append(Paragraph(text12, normal_style))
    
    text13 = """
    Natural Language Processing (NLP) applications include virtual assistants like Siri and 
    Alexa, language translation services, sentiment analysis, and chatbots. Recent advances in 
    large language models have enabled more sophisticated conversational AI systems that can 
    understand context and generate human-like responses.
    """
    elements.append(Paragraph(text13, normal_style))
    
    # Page 5: Future and Challenges
    elements.append(PageBreak())
    
    heading5 = Paragraph("Chapter 5: The Future of AI and Current Challenges", heading_style)
    elements.append(heading5)
    
    text14 = """
    The future of AI holds immense potential. Researchers are working on achieving Artificial 
    General Intelligence (AGI), systems that can understand, learn, and apply knowledge across 
    a wide range of tasks at a human level. While we are still far from AGI, progress in narrow 
    AI continues to accelerate.
    """
    elements.append(Paragraph(text14, normal_style))
    
    text15 = """
    However, AI also faces significant challenges. Ethical concerns include bias in AI systems, 
    privacy issues, job displacement due to automation, and the potential misuse of AI 
    technologies. Ensuring AI systems are fair, transparent, and accountable is crucial for 
    building public trust and responsible deployment.
    """
    elements.append(Paragraph(text15, normal_style))
    
    text16 = """
    Technical challenges include the need for large amounts of training data, high computational 
    costs, difficulty in explaining AI decisions (the "black box" problem), and ensuring AI 
    systems are robust and secure. Researchers are actively working on solutions such as 
    few-shot learning, explainable AI, and adversarial robustness.
    """
    elements.append(Paragraph(text16, normal_style))
    
    text17 = """
    Despite these challenges, AI continues to advance rapidly. The integration of AI into 
    everyday life is inevitable, and it will play an increasingly important role in solving 
    complex global problems such as climate change, disease, and resource scarcity. The key 
    is to develop AI responsibly, with careful consideration of its societal impact.
    """
    elements.append(Paragraph(text17, normal_style))
    
    # Build PDF
    doc.build(elements)
    
    print(f"✅ Test PDF created: {filename}")
    print(f"   File size: {os.path.getsize(filename)} bytes")
    print(f"   Pages: 5")
    print(f"   Content: AI and Machine Learning topics")

if __name__ == "__main__":
    try:
        create_test_pdf()
    except ImportError:
        print("❌ reportlab library not found!")
        print("   Install it with: pip install reportlab")
        print("\n   Or use any PDF file you have for testing.")