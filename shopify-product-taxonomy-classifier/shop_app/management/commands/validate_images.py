import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
from shop_app.models import ProductImage


def check_one(img):
    try:
        if not img.image_url:
            return (img.id, False)
        resp = requests.head(img.image_url, timeout=4, allow_redirects=True)
        if resp.status_code == 200:
            return (img.id, True)
        return (img.id, False)
    except requests.RequestException:
        return (img.id, False)
    except Exception:
        return (img.id, False)


class Command(BaseCommand):
    help = "Check product image URLs in parallel and mark valid/broken"

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None, help='Only check this many images (for a quick test run)')
        parser.add_argument('--workers', type=int, default=30, help='How many checks to run at the same time')

    def handle(self, *args, **options):
        images = list(ProductImage.objects.all())
        if options['limit']:
            images = images[:options['limit']]

        total = len(images)
        self.stdout.write(f"Checking {total} images with {options['workers']} parallel workers...")

        valid, broken, checked = 0, 0, 0
        updates = {}

        with ThreadPoolExecutor(max_workers=options['workers']) as executor:
            futures = {executor.submit(check_one, img): img for img in images}
            for future in as_completed(futures):
                img_id, is_valid = future.result()
                updates[img_id] = is_valid
                checked += 1
                if is_valid:
                    valid += 1
                else:
                    broken += 1
                if checked % 500 == 0:
                    self.stdout.write(f"Checked {checked}/{total}...")

        # SQLite can't handle a single query with 39,000+ IDs in it,
        # so we save in smaller chunks instead of all at once.
        CHUNK_SIZE = 500
        all_ids = list(updates.keys())

        for start in range(0, len(all_ids), CHUNK_SIZE):
            chunk_ids = all_ids[start:start + CHUNK_SIZE]
            objs = list(ProductImage.objects.filter(id__in=chunk_ids))
            for obj in objs:
                obj.is_valid = updates[obj.id]
            ProductImage.objects.bulk_update(objs, ['is_valid'], batch_size=CHUNK_SIZE)

        self.stdout.write(self.style.SUCCESS(f"Done. Valid: {valid}, Broken: {broken}"))