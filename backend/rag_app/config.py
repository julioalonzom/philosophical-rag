# backend/rag_core/config.py
ACCOUNT_TIERS = {
    'free': {
        'monthly_query_limit': 50,
        'context_length': 1000,
    },
    'premium': {
        'monthly_query_limit': float('inf'),
        'context_length': 2000,
    }
}