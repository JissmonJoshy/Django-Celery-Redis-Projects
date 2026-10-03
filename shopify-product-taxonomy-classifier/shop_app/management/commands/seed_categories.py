from django.core.management.base import BaseCommand
from shop_app.models import Category


# (name, full_path, description used for text-matching)
CATEGORIES = [
    ("Sofas & Couches", "Home & Garden > Furniture > Living Room Furniture > Sofas & Couches",
     "sofa couch loveseat sectional living room seating upholstered"),
    ("Armchairs", "Home & Garden > Furniture > Living Room Furniture > Armchairs",
     "armchair accent chair lounge chair living room seating"),
    ("Coffee & Accent Tables", "Home & Garden > Furniture > Living Room Furniture > Coffee & Accent Tables",
     "coffee table accent table side table living room"),
    ("Beds & Bed Frames", "Home & Garden > Furniture > Bedroom Furniture > Beds & Bed Frames",
     "bed bed frame daybed headboard bedroom sleep"),
    ("Dressers & Chests", "Home & Garden > Furniture > Bedroom Furniture > Dressers & Chests",
     "dresser chest of drawers case goods bedroom storage"),
    ("Dining Tables", "Home & Garden > Furniture > Dining Room Furniture > Dining Tables",
     "dining table kitchen table bar table dining room"),
    ("Dining Chairs", "Home & Garden > Furniture > Dining Room Furniture > Dining Chairs",
     "dining chair kitchen chair dining room seating"),
    ("Dining Sets", "Home & Garden > Furniture > Dining Room Furniture > Dining Sets",
     "dining set table and chairs dining room set"),
    ("Bar & Counter Stools", "Home & Garden > Furniture > Bar Furniture > Bar & Counter Stools",
     "bar stool counter stool bar furniture seating"),
    ("Benches & Stools", "Home & Garden > Furniture > Bar Furniture > Benches & Stools",
     "bench stool seating furniture"),
    ("Office Chairs", "Home & Garden > Furniture > Office Furniture > Office Chairs",
     "office chair desk chair task chair ergonomic seating"),
    ("Computer Desks", "Home & Garden > Furniture > Office Furniture > Computer Desks",
     "computer desk office desk workstation writing desk"),
    ("Outdoor Seating", "Home & Garden > Furniture > Outdoor Furniture > Outdoor Seating",
     "outdoor chair patio seating garden furniture weatherproof"),
    ("Bathroom Vanities", "Home & Garden > Furniture > Bathroom Furniture > Vanities",
     "vanity bathroom cabinet sink storage"),
    ("Ceiling Lights", "Home & Garden > Lighting > Ceiling Lights",
     "ceiling lamp pendant light chandelier flush mount lighting"),
    ("Floor Lamps", "Home & Garden > Lighting > Floor Lamps",
     "floor lamp standing lamp lighting"),
    ("Table Lamps", "Home & Garden > Lighting > Table Lamps",
     "table lamp desk lamp lighting"),
    ("Decorative Pillows", "Home & Garden > Decor > Decorative Pillows",
     "pillow throw pillow cushion decor accent"),
    ("Daybeds & Lounges", "Home & Garden > Furniture > Living Room Furniture > Daybeds & Lounges",
     "daybed chaise lounge living room seating"),
]


class Command(BaseCommand):
    help = "Seed a starter set of Shopify-style furniture/lighting categories"

    def handle(self, *args, **options):
        created = 0
        for name, full_path, description in CATEGORIES:
            _, was_created = Category.objects.update_or_create(
                full_path=full_path,
                defaults={"name": name, "description": description}
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f"Done. {created} new categories created, {len(CATEGORIES) - created} already existed."
        ))