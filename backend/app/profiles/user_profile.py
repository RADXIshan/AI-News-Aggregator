from app.database.repository import Repository


def get_user_profile(email: str = None) -> dict:
    """
    Get user profile with dynamic name from database.
    If email is provided, fetch that user's name.
    Otherwise, fetch the first active user's name.
    """
    repo = Repository()
    
    # Default name if no user found
    user_name = "User"
    
    try:
        if email:
            user = repo.get_email_by_address(email)
            if user and user.name:
                user_name = user.name
        else:
            # Get first active user
            users = repo.get_all_emails(active_only=True)
            if users and users[0].name:
                user_name = users[0].name
    finally:
        repo.session.close()  # Always release the connection
    
    return {
        "name": user_name,
        "title": "AI/ML Engineer & Researcher",
        "background": "Experienced AI/ML engineer with deep interest in practical AI applications, research breakthroughs, and production-ready systems",
        "interests": [
            "Large Language Models (LLMs) and their applications",
            "Retrieval-Augmented Generation (RAG) systems",
            "AI agent architectures and autonomous workflows",
            "Multimodal models (vision-language, audio-language, VLMs)",
            "Machine learning systems and scalable training pipelines",
            "Deep learning architectures and optimization techniques",
            "Diffusion models and generative modeling",
            "Self-supervised learning and representation learning",
            "Reinforcement learning and RLHF/RLAIF",
            "Neural scaling laws and model efficiency research",
            "Model distillation, quantization, pruning, and compression",
            "Continual learning and adaptive inference",
            "Vector databases, embeddings, and semantic retrieval",
            "Evaluation methods for LLMs, agents, and RAG systems",
            "AI safety, alignment, robustness, and interpretability",
            "Systems-level AI: compilers, kernels, and model serving",
            "High-performance inference (GPU, TPU, accelerated runtimes)",
            "MLOps, production deployments, monitoring, and infra",
            "Distributed training and large-scale model optimization",
            "Research papers with real-world implementation value",
            "Case studies of AI in production at scale",
            "Benchmarking, dataset engineering, and synthetic data",
            "Foundation model fine-tuning, adapters, and LoRA variants"
        ],
        "preferences": {
            "prefer_practical": True,
            "prefer_technical_depth": True,
            "prefer_research_breakthroughs": True,
            "prefer_production_focus": True,
            "avoid_marketing_hype": True
        },
        "expertise_level": "Advanced"
    }


# Backward compatibility - default profile
USER_PROFILE = get_user_profile()
