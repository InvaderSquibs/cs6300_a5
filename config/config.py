# Recipe Similarity Evaluation Configuration

# Model Configuration
MODEL_NAME = "all-MiniLM-L6-v2"  # Lightweight and efficient sentence transformer
CACHE_DIR = "./models"  # Directory to cache downloaded models
SIMILARITY_THRESHOLD = 0.7  # Default threshold for similarity determination

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Alternative models (uncomment to use)
# MODEL_NAME = "all-mpnet-base-v2"  # More accurate but larger
# MODEL_NAME = "all-distilroberta-v1"  # Good balance of speed and accuracy
# MODEL_NAME = "paraphrase-MiniLM-L6-v2"  # Optimized for paraphrase detection