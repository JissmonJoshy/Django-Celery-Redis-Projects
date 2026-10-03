from django.core.management.base import BaseCommand
from shop_app.models import ClassificationResult, Attribute, ProductAttributeValue


class Command(BaseCommand):
    help = "Detect attribute values (Color, Material, Assembly Required) for each classified product"

    def handle(self, *args, **options):
        color_attr, _ = Attribute.objects.get_or_create(name="Color")
        material_attr, _ = Attribute.objects.get_or_create(name="Material")
        assembly_attr, _ = Attribute.objects.get_or_create(name="Assembly Required")

        results = ClassificationResult.objects.select_related('product').all()
        created, skipped, errors = 0, 0, 0

        for result in results:
            try:
                p = result.product
                ProductAttributeValue.objects.filter(result=result).delete()  # clean re-run

                # Color: directly from the Excel column, confidence high since it's given data, not guessed
                if p.product_color:
                    ProductAttributeValue.objects.create(
                        result=result, attribute=color_attr, value=p.product_color, confidence=0.95
                    )
                    created += 1
                else:
                    skipped += 1

                # Material: field can contain multiple materials separated by commas/slashes
                if p.materials:
                    for m in [x.strip() for x in p.materials.replace('/', ',').split(',') if x.strip()]:
                        ProductAttributeValue.objects.create(
                            result=result, attribute=material_attr, value=m, confidence=0.9
                        )
                        created += 1
                else:
                    skipped += 1

                # Assembly Required: Y/N field, normalize it
                if p.assembly_required:
                    val = "Yes" if str(p.assembly_required).strip().lower() in ('y', 'yes', 'true', '1') else "No"
                    ProductAttributeValue.objects.create(
                        result=result, attribute=assembly_attr, value=val, confidence=1.0
                    )
                    created += 1

            except Exception as e:
                errors += 1
                self.stderr.write(f"Product {result.product.product_number} failed: {e}")
                continue

        self.stdout.write(self.style.SUCCESS(f"Done. Values created: {created}, fields skipped (empty): {skipped}, errors: {errors}"))