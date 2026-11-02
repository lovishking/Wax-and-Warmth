"""
Candle Knowledge Models — Stores semantic knowledge documents and embeddings.
For use with the RAG recommendation pipeline.
"""

from django.db import models


class CandleKnowledge(models.Model):
    """
    Stores the knowledge document for each candle product.
    The document is used to generate embeddings for semantic search.
    The embedding is stored as a JSON array (for SQLite compatibility).
    In production with PostgreSQL + pgvector, this would be a vector field.
    """

    product = models.OneToOneField(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='knowledge',
    )
    document = models.TextField(
        help_text='Structured knowledge document for the candle',
    )
    embedding = models.JSONField(
        null=True,
        blank=True,
        help_text='Embedding vector stored as JSON array',
    )
    embedding_model = models.CharField(
        max_length=100,
        default='text-embedding-3-small',
        help_text='Model used to generate the embedding',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candle_knowledge'
        verbose_name_plural = 'Candle Knowledge'

    def __str__(self):
        return f"Knowledge: {self.product.name}"
