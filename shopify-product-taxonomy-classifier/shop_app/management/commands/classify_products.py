import json
from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from shop_app.models import Product, Category, ClassificationResult

LOW_CONFIDENCE_THRESHOLD = 0.15  # we'll tune this after seeing real score distribution


class Command(BaseCommand):
    help = "Classify all products into Shopify categories using TF-IDF text similarity"

    def handle(self, *args, **options):
        categories = list(Category.objects.all())
        if not categories:
            self.stderr.write("No categories found. Run 'seed_categories' first.")
            return

        products = list(Product.objects.all())
        if not products:
            self.stderr.write("No products found. Run 'import_products' first.")
            return

        category_texts = [f"{c.name} {c.description}" for c in categories]

        def product_text(p):
            parts = [p.product_name, p.description, p.bullets,
                     p.product_category, p.product_sub_category, p.materials]
            return " ".join(str(x) for x in parts if x)

        product_texts = [product_text(p) for p in products]

        vectorizer = TfidfVectorizer(stop_words='english')
        all_texts = category_texts + product_texts

        try:
            tfidf_matrix = vectorizer.fit_transform(all_texts)
        except ValueError as e:
            self.stderr.write(f"TF-IDF failed: {e}")
            return

        n_cat = len(categories)
        category_vectors = tfidf_matrix[:n_cat]
        product_vectors = tfidf_matrix[n_cat:]

        similarity_matrix = cosine_similarity(product_vectors, category_vectors)

        created, updated, failed = 0, 0, 0
        scores_seen = []

        for i, product in enumerate(products):
            try:
                sims = similarity_matrix[i]
                ranked = sorted(zip(categories, sims), key=lambda x: x[1], reverse=True)
                top_category, top_score = ranked[0]
                scores_seen.append(top_score)

                alternatives = [
                    {"category_id": c.id, "full_path": c.full_path, "score": round(float(s), 4)}
                    for c, s in ranked[1:4]
                ]

                if top_score <= 0:
                    predicted, status, note = None, 'failed', "No text similarity to any category (missing/empty product text)."
                else:
                    predicted, status, note = top_category, 'needs_review', ""

                is_low = top_score < LOW_CONFIDENCE_THRESHOLD

                result, was_created = ClassificationResult.objects.update_or_create(
                    product=product,
                    defaults={
                        "predicted_category": predicted,
                        "confidence": round(float(top_score), 4),
                        "alternatives_json": json.dumps(alternatives),
                        "is_low_confidence": is_low,
                        "status": status,
                        "notes": note,
                    }
                )
                created += was_created
                updated += (not was_created)

            except Exception as e:
                failed += 1
                self.stderr.write(f"Product {product.product_number} failed: {e}")
                continue

        if scores_seen:
            self.stdout.write(
                f"Score range: min={min(scores_seen):.3f} max={max(scores_seen):.3f} avg={sum(scores_seen)/len(scores_seen):.3f}"
            )
        self.stdout.write(self.style.SUCCESS(f"Done. Created: {created}, Updated: {updated}, Errors: {failed}"))