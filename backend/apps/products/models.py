"""
Product & Category Models
"""

from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Product category."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductFacet(models.Model):
    """Reusable typed values for the product's multi-valued attributes."""

    class Kind(models.TextChoices):
        SCENT_NOTE = 'SCENT_NOTE', 'Scent note'
        MOOD = 'MOOD', 'Mood'
        ROOM = 'ROOM', 'Recommended room'
        OCCASION = 'OCCASION', 'Recommended occasion'

    kind = models.CharField(max_length=16, choices=Kind.choices)
    value = models.CharField(max_length=120)
    normalized_value = models.CharField(max_length=120, editable=False)

    class Meta:
        db_table = 'product_facets'
        ordering = ['kind', 'value']
        constraints = [
            models.UniqueConstraint(fields=['kind', 'normalized_value'], name='product_facet_kind_value_uniq'),
            models.CheckConstraint(
                check=models.Q(kind__in=['SCENT_NOTE', 'MOOD', 'ROOM', 'OCCASION']),
                name='product_facet_kind_valid',
            ),
        ]
        indexes = [models.Index(fields=['kind', 'value'], name='product_facet_kind_value_idx')]

    def __str__(self):
        return f'{self.get_kind_display()}: {self.value}'

    def save(self, *args, **kwargs):
        self.value = self.value.strip()
        self.normalized_value = self.value.casefold()
        super().save(*args, **kwargs)


class Product(models.Model):
    """Candle product."""

    class ScentFamily(models.TextChoices):
        FLORAL = 'FLORAL', 'Floral'
        WOODY = 'WOODY', 'Woody'
        CITRUS = 'CITRUS', 'Citrus'
        FRUITY = 'FRUITY', 'Fruity'
        SPICY = 'SPICY', 'Spicy'
        FRESH = 'FRESH', 'Fresh'
        SWEET = 'SWEET', 'Sweet'
        EARTHY = 'EARTHY', 'Earthy'
        ORIENTAL = 'ORIENTAL', 'Oriental'
        HERBAL = 'HERBAL', 'Herbal'

    class FragranceStrength(models.TextChoices):
        LIGHT = 'LIGHT', 'Light'
        MEDIUM = 'MEDIUM', 'Medium'
        STRONG = 'STRONG', 'Strong'

    class Size(models.TextChoices):
        SMALL = 'SMALL', 'Small (100g)'
        MEDIUM = 'MEDIUM', 'Medium (200g)'
        LARGE = 'LARGE', 'Large (350g)'
        EXTRA_LARGE = 'EXTRA_LARGE', 'Extra Large (500g)'

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
    )
    facets = models.ManyToManyField(
        ProductFacet,
        through='ProductFacetAssignment',
        related_name='products',
        blank=True,
    )
    scent_family = models.CharField(
        max_length=20,
        choices=ScentFamily.choices,
        default=ScentFamily.FLORAL,
    )
    fragrance_strength = models.CharField(
        max_length=20,
        choices=FragranceStrength.choices,
        default=FragranceStrength.MEDIUM,
    )
    size = models.CharField(
        max_length=20,
        choices=Size.choices,
        default=Size.MEDIUM,
    )
    burn_time = models.CharField(
        max_length=50,
        help_text='Estimated burn time (e.g., 40-50 hours)',
        blank=True,
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['scent_family'], name='product_scent_family_idx'),
            models.Index(fields=['price'], name='product_price_idx'),
            models.Index(fields=['is_active', 'is_featured'], name='product_active_featured_idx'),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(price__gt=0), name='product_price_positive'),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    @property
    def scent_notes_list(self):
        return self._facet_values(ProductFacet.Kind.SCENT_NOTE)

    @property
    def mood_list(self):
        return self._facet_values(ProductFacet.Kind.MOOD)

    @property
    def rooms_list(self):
        return self._facet_values(ProductFacet.Kind.ROOM)

    @property
    def occasions_list(self):
        return self._facet_values(ProductFacet.Kind.OCCASION)

    def _facet_values(self, kind):
        if '_product_facet_values_cache' not in self.__dict__:
            assignments = getattr(self, '_prefetched_objects_cache', {}).get('facet_assignments')
            if assignments is None:
                assignments = self.facet_assignments.select_related('facet').order_by('position', 'id')
            values = {facet_kind: [] for facet_kind, _ in ProductFacet.Kind.choices}
            for assignment in assignments:
                values[assignment.facet.kind].append(assignment.facet.value)
            self._product_facet_values_cache = values
        return self._product_facet_values_cache.get(kind, [])

    @property
    def scent_notes(self):
        return ', '.join(self.scent_notes_list)

    @property
    def mood(self):
        return ', '.join(self.mood_list)

    @property
    def recommended_rooms(self):
        return ', '.join(self.rooms_list)

    @property
    def recommended_occasions(self):
        return ', '.join(self.occasions_list)


class ProductFacetAssignment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='facet_assignments')
    facet = models.ForeignKey(ProductFacet, on_delete=models.CASCADE, related_name='assignments')
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'product_facet_assignments'
        ordering = ['position', 'id']
        constraints = [
            models.UniqueConstraint(fields=['product', 'facet'], name='product_facet_assignment_uniq'),
            models.CheckConstraint(check=models.Q(position__gte=0), name='product_facet_position_nonnegative'),
        ]
        indexes = [models.Index(fields=['product', 'position'], name='product_facet_position_idx')]
