from django.db import transaction
from .models import ProductFacet, ProductFacetAssignment


FACET_FIELDS = {
    'scent_notes': ProductFacet.Kind.SCENT_NOTE,
    'mood': ProductFacet.Kind.MOOD,
    'recommended_rooms': ProductFacet.Kind.ROOM,
    'recommended_occasions': ProductFacet.Kind.OCCASION,
}


def parse_facet_values(value):
    if value is None:
        return []
    values = value if isinstance(value, (list, tuple)) else str(value).split(',')
    result, seen = [], set()
    for item in values:
        item = str(item).strip()
        key = item.casefold()
        if item and key not in seen:
            result.append(item)
            seen.add(key)
    return result


@transaction.atomic
def set_product_facets(product, fields):
    """Replace only the facet kinds explicitly present in an API payload."""
    for field_name, kind in FACET_FIELDS.items():
        if field_name not in fields:
            continue
        ProductFacetAssignment.objects.filter(product=product, facet__kind=kind).delete()
        assignments = []
        for position, value in enumerate(parse_facet_values(fields[field_name])):
            normalized = value.casefold()
            facet, _ = ProductFacet.objects.get_or_create(
                kind=kind,
                normalized_value=normalized,
                defaults={'value': value},
            )
            assignments.append(ProductFacetAssignment(product=product, facet=facet, position=position))
        ProductFacetAssignment.objects.bulk_create(assignments)
    product.__dict__.pop('_product_facet_values_cache', None)
