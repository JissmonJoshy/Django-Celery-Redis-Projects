from celery import shared_task
from django.db.models import Q
from shop_app.models import Product, Category, ClassificationResult
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

CHUNK_SIZE = 200
LOW_CONFIDENCE_THRESHOLD = 0.15


@shared_task
def classify_products_batch_task():
    """
    Only classifies products that don't already have a result yet.
    This is what makes it resumable: if it crashes after 6,000 products,
    re-running this task just picks up the remaining ones instead of
    starting over.
    """
    categories = list(Category.objects.all())
    if not categories:
        return "No categories found."

    unclassified = Product.objects.filter(classification__isnull=True)
    total_remaining = unclassified.count()
    if total_remaining == 0:
        return "Nothing to classify — all products already have a result."

    category_texts = [f"{c.name} {c.description}" for c in categories]

    processed = 0
    while True:
        chunk = list(unclassified[:CHUNK_SIZE])
        if not chunk:
            break

        def product_text(p):
            parts = [p.product_name, p.description, p.bullets, p.product_category, p.product_sub_category, p.materials]
            return " ".join(str(x) for x in parts if x)

        texts = category_texts + [product_text(p) for p in chunk]
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf = vectorizer.fit_transform(texts)
        except ValueError:
            break

        n_cat = len(categories)
        sims = cosine_similarity(tfidf[n_cat:], tfidf[:n_cat])

        for i, product in enumerate(chunk):
            ranked = sorted(zip(categories, sims[i]), key=lambda x: x[1], reverse=True)
            top_cat, top_score = ranked[0]
            alternatives = [{"category_id": c.id, "full_path": c.full_path, "score": round(float(s), 4)} for c, s in ranked[1:4]]

            ClassificationResult.objects.create(
                product=product,
                predicted_category=top_cat if top_score > 0 else None,
                confidence=round(float(top_score), 4),
                alternatives_json=json.dumps(alternatives),
                is_low_confidence=top_score < LOW_CONFIDENCE_THRESHOLD,
                status='needs_review' if top_score > 0 else 'failed',
            )

        processed += len(chunk)
        unclassified = Product.objects.filter(classification__isnull=True)  # refresh

    return f"Classified {processed} products this run."