from django.contrib import admin
from django.contrib.gis import admin as gis_admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html, mark_safe
from fieldsets_with_inlines import FieldsetsInlineMixin

from lemarche.siaes.models import (
    Siae,
    SiaeClientReference,
    SiaeGroup,
    SiaeImage,
    SiaeLabel,
    SiaeOffer,
    SiaeUser,
    SiaeUserRequest,
)
from lemarche.users.models import User
from lemarche.utils.fields import pretty_print_readonly_jsonfield


class IsLiveFilter(admin.SimpleListFilter):
    """Custom admin filter to target siaes who are live (active and not delisted)."""

    title = "Live ? (active et non délistée)"
    parameter_name = "is_live"

    def lookups(self, request, model_admin):
        return (("Yes", "Oui"), ("No", "Non"))

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.is_live()
        elif value == "No":
            return queryset.is_not_live()
        return queryset


class HasUserFilter(admin.SimpleListFilter):
    """Custom admin filter to target siaes who have at least 1 user."""

    title = "Avec un gestionnaire ?"
    parameter_name = "has_user"

    def lookups(self, request, model_admin):
        return (("Yes", "Oui"), ("No", "Non"))

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.has_user()
        elif value == "No":
            return queryset.filter(users__isnull=True)
        return queryset


class SiaeUserInline(admin.TabularInline):
    model = SiaeUser
    fields = ["user", "user_with_link", "created_at", "updated_at"]
    autocomplete_fields = ["user"]
    readonly_fields = ["user_with_link", "created_at", "updated_at"]
    extra = 0

    def user_with_link(self, siae_user):
        url = reverse("admin:users_user_change", args=[siae_user.user_id])
        return format_html(f'<a href="{url}">{siae_user.user}</a>')

    user_with_link.short_description = User._meta.verbose_name


@admin.register(Siae)
class SiaeAdmin(FieldsetsInlineMixin, gis_admin.OSMGeoAdmin):
    list_display = [
        "id",
        "name",
        "siret",
        "kind",
        "city",
        "nb_users",
        "nb_offers",
        "nb_labels",
        "nb_cient_references",
        "nb_images",
        "created_at",
    ]
    list_filter = [IsLiveFilter, "is_first_page", HasUserFilter, "kind", "networks", "sectors", "geo_range", "source"]
    search_fields = ["id", "name", "slug", "siret"]
    search_help_text = "Cherche sur les champs : ID, Raison sociale, Slug, Siret"

    autocomplete_fields = ["sectors", "networks", "groups"]
    # prepopulated_fields = {"slug": ("name",)}
    readonly_fields = [field for field in Siae.READONLY_FIELDS if field not in ("coords")] + [
        "sector_count",
        "network_count",
        "nb_offers",
        "nb_labels",
        "nb_cient_references",
        "nb_users",
        "nb_images",
        "coords_display",
        "logo_url",
        "logo_url_display",
        "signup_date",
        "content_filled_basic_date",
        # "import_raw_object",
        "import_raw_object_display",
        "created_at",
        "updated_at",
    ]

    # OSMGeoAdmin param for coords fields
    modifiable = False

    fieldsets_with_inlines = [
        (
            "Affichage",
            {
                "fields": ("is_active", "is_delisted", "is_first_page"),
            },
        ),
        (
            "Données C1 (ou ESAT ou SEP)",
            {
                "fields": (
                    "name",
                    "slug",
                    "brand",
                    "siret",
                    "naf",
                    "kind",
                    "c1_id",
                    "asp_id",
                    "website",
                    "email",
                    "phone",
                    "address",
                    "city",
                    "post_code",
                    "department",
                    "region",
                    "coords_display",
                    "coords",
                    "source",
                )
            },
        ),
        ("Données C2", {"fields": Siae.READONLY_FIELDS_FROM_C2}),
        ("Données API Entreprise", {"fields": Siae.READONLY_FIELDS_FROM_API_ENTREPRISE}),
        (
            "Données API QPV (Quartier prioritaire de la politique de la ville)",
            {"fields": Siae.READONLY_FIELDS_FROM_QPV},
        ),
        ("Données API ZRR (Zone de revitalisation rurale)", {"fields": Siae.READONLY_FIELDS_FROM_ZRR}),
        (
            "Détails",
            {
                "fields": (
                    "description",
                    "sectors",
                    "sector_count",
                    "networks",
                    "network_count",
                    "nb_offers",
                    "nb_labels",
                    "nb_cient_references",
                    "nb_images",
                    "groups",
                )
            },
        ),
        (
            "Périmètre d'intervention",
            {
                "fields": (
                    "geo_range",
                    "geo_range_custom_distance",
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "contact_first_name",
                    "contact_last_name",
                    "contact_email",
                    "contact_phone",
                    "contact_website",
                    "nb_users",
                )
            },
        ),
        SiaeUserInline,
        (
            "Logo",
            {
                "fields": (
                    "logo_url",
                    "logo_url_display",
                )
            },
        ),
        (
            "Stats",
            {
                "fields": (
                    "signup_date",
                    "content_filled_basic_date",
                )
            },
        ),
        ("Si importé", {"fields": ("import_raw_object_display",)}),
        ("Autres", {"fields": ("created_at", "updated_at")}),
    ]

    add_fieldsets = [
        (
            "Affichage",
            {
                "fields": (
                    "is_active",
                    # "is_delisted",
                    # "is_first_page"
                ),
            },
        ),
        (
            "Données C1 (ou ESAT ou SEP)",
            {
                "fields": (
                    "name",
                    "slug",
                    "brand",
                    "siret",
                    "naf",
                    "kind",
                    # "c1_id",
                    # "asp_id",
                    "website",
                    "email",
                    "phone",
                    "address",
                    "city",
                    "post_code",
                    "department",
                    "region",
                    # "coords_display",
                    # "coords",
                    "source",
                )
            },
        ),
        (
            "Détails",
            {
                "fields": (
                    "description",
                    "sectors",
                    # "sector_count",
                    "networks",
                    # "network_count",
                    # "nb_offers",
                    # "nb_labels",
                    # "nb_cient_references",
                    # "nb_images",
                    # "groups",
                )
            },
        ),
        (
            "Périmètre d'intervention",
            {
                "fields": (
                    "geo_range",
                    "geo_range_custom_distance",
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "contact_first_name",
                    "contact_last_name",
                    "contact_email",
                    "contact_phone",
                    "contact_website",
                    # "nb_users",
                )
            },
        ),
    ]

    def get_readonly_fields(self, request, obj=None):
        """
        Staff can create and edit some Siaes.
        The editable fields are listed in add_fieldsets.
        """
        add_fields = []
        for fieldset in self.add_fieldsets:
            add_fields.extend(list(fieldset[1]["fields"]))
        add_readonly_fields = [field for field in self.readonly_fields if field not in add_fields] + ["slug", "source"]
        # add form
        if not obj:
            return add_readonly_fields
        # also allow edition of some specific Siae
        if obj and obj.source in [Siae.SOURCE_STAFF_C4_CREATED, Siae.SOURCE_ESAT]:
            return add_readonly_fields + ["name"]
        # for the rest, use the default full-version list
        return self.readonly_fields

    def get_fieldsets(self, request, obj=None):
        """
        The add form has a lighter fieldsets.
        (add_fieldsets is only available for User Admin, so we need to set it manually)
        """
        if not obj:
            self.fieldsets_with_inlines = self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_changeform_initial_data(self, request):
        """
        Default values in add form.
        """
        return {"is_active": False, "source": Siae.SOURCE_STAFF_C4_CREATED}

    def nb_users(self, siae):
        url = reverse("admin:users_user_changelist") + f"?siaes__in={siae.id}"
        return format_html(f'<a href="{url}">{siae.user_count}</a>')

    nb_users.short_description = "Nombre d'utilisateurs"
    nb_users.admin_order_field = "user_count"

    def nb_offers(self, siae):
        url = reverse("admin:siaes_siaeoffer_changelist") + f"?siae__id__exact={siae.id}"
        return format_html(f'<a href="{url}">{siae.offer_count}</a>')

    nb_offers.short_description = "Nombre de prestations"
    nb_offers.admin_order_field = "offer_count"

    def nb_labels(self, siae):
        url = reverse("admin:siaes_siaelabel_changelist") + f"?siae__id__exact={siae.id}"
        return format_html(f'<a href="{url}">{siae.label_count}</a>')

    nb_labels.short_description = "Nombre de labels"
    nb_labels.admin_order_field = "label_count"

    def nb_cient_references(self, siae):
        url = reverse("admin:siaes_siaeclientreference_changelist") + f"?siae__id__exact={siae.id}"
        return format_html(f'<a href="{url}">{siae.client_reference_count}</a>')

    nb_cient_references.short_description = "Nombre de réf. clients"
    nb_cient_references.admin_order_field = "client_reference_count"

    def nb_images(self, siae):
        url = reverse("admin:siaes_siaeimage_changelist") + f"?siae__id__exact={siae.id}"
        return format_html(f'<a href="{url}">{siae.image_count}</a>')

    nb_images.short_description = "Nombre d'images"
    nb_images.admin_order_field = "image_count"

    def coords_display(self, siae):
        if siae.coords:
            return f"{siae.latitude} / {siae.longitude}"
        return "-"

    coords_display.short_description = "Coords (LAT / LNG)"

    def logo_url_display(self, siae):
        if siae.logo_url:
            return mark_safe(
                f'<a href="{siae.logo_url}" target="_blank">'
                f'<img src="{siae.logo_url}" title="{siae.logo_url}" style="max-height:300px" />'
                f"</a>"
            )
        return mark_safe("<div>-</div>")

    logo_url_display.short_description = "Logo"

    def import_raw_object_display(self, siae=None):
        if siae:
            return pretty_print_readonly_jsonfield(siae.import_raw_object)
        return "-"

    import_raw_object_display.short_description = "Donnée brute importée"


@admin.register(SiaeUserRequest)
class SiaeUserRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "siae", "initiator", "assignee", "response", "created_at", "updated_at"]
    search_fields = [
        "id",
        "siae__id",
        "siae__name",
        "initiator__id",
        "initiator__email",
        "assignee__id",
        "assignee__email",
    ]
    search_help_text = (
        "Cherche sur les champs : ID, Structure (ID, Nom), Initiateur (ID, E-mail), Responsable (ID, E-mail)"
    )

    autocomplete_fields = ["siae"]
    readonly_fields = [field.name for field in SiaeUserRequest._meta.fields]
    fields = ["logs_display" if field_name == "logs" else field_name for field_name in readonly_fields]

    def logs_display(self, siaeuserrequest=None):
        if siaeuserrequest:
            return pretty_print_readonly_jsonfield(siaeuserrequest.logs)
        return "-"

    logs_display.short_description = "Logs des échanges"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiaeOffer)
class SiaeOfferAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "siae_with_link", "source", "created_at"]
    list_filter = ["source"]
    search_fields = ["id", "name", "siae__id", "siae__name"]
    search_help_text = "Cherche sur les champs : ID, Nom, Structure (ID, Nom)"

    autocomplete_fields = ["siae"]
    readonly_fields = ["source", "created_at", "updated_at"]

    def siae_with_link(self, siae_offer):
        url = reverse("admin:siaes_siae_change", args=[siae_offer.siae_id])
        return format_html(f'<a href="{url}">{siae_offer.siae}</a>')

    siae_with_link.short_description = "Structure"
    siae_with_link.admin_order_field = "siae"


@admin.register(SiaeLabel)
class SiaeLabelAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "siae_with_link", "created_at"]
    search_fields = ["id", "name", "siae__id", "siae__name"]
    search_help_text = "Cherche sur les champs : ID, Nom, Structure (ID, Nom)"

    autocomplete_fields = ["siae"]
    readonly_fields = ["created_at", "updated_at"]

    def siae_with_link(self, siae_label):
        url = reverse("admin:siaes_siae_change", args=[siae_label.siae_id])
        return format_html(f'<a href="{url}">{siae_label.siae}</a>')

    siae_with_link.short_description = "Structure"
    siae_with_link.admin_order_field = "siae"


@admin.register(SiaeClientReference)
class SiaeClientReferenceAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "siae_with_link", "created_at"]
    search_fields = ["id", "name", "siae__id", "siae__name"]
    search_help_text = "Cherche sur les champs : ID, Nom, Structure (ID, Nom)"

    autocomplete_fields = ["siae"]
    readonly_fields = ["image_name", "logo_url", "logo_url_display", "created_at", "updated_at"]

    def siae_with_link(self, siae_client_reference):
        url = reverse("admin:siaes_siae_change", args=[siae_client_reference.siae_id])
        return format_html(f'<a href="{url}">{siae_client_reference.siae}</a>')

    siae_with_link.short_description = "Structure"
    siae_with_link.admin_order_field = "siae"

    def logo_url_display(self, siae_client_reference):
        if siae_client_reference.logo_url:
            return mark_safe(
                f'<a href="{siae_client_reference.logo_url}" target="_blank">'
                f'<img src="{siae_client_reference.logo_url}" title="{siae_client_reference.logo_url}" style="max-height:300px" />'  # noqa
                f"</a>"
            )
        return mark_safe("<div>-</div>")

    logo_url_display.short_description = "Logo"


@admin.register(SiaeImage)
class SiaeImageAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "siae_with_link", "created_at"]
    search_fields = ["id", "name", "siae__id", "siae__name"]
    search_help_text = "Cherche sur les champs : ID, Nom, Structure (ID, Nom)"

    autocomplete_fields = ["siae"]
    readonly_fields = ["image_name", "image_url", "image_url_display", "created_at", "updated_at"]

    def siae_with_link(self, siae_image):
        url = reverse("admin:siaes_siae_change", args=[siae_image.siae_id])
        return format_html(f'<a href="{url}">{siae_image.siae}</a>')

    siae_with_link.short_description = "Structure"
    siae_with_link.admin_order_field = "siae"

    def image_url_display(self, siae_image):
        if siae_image.image_url:
            return mark_safe(
                f'<a href="{siae_image.image_url}" target="_blank">'
                f'<img src="{siae_image.image_url}" title="{siae_image.image_url}" style="max-height:300px" />'
                f"</a>"
            )
        return mark_safe("<div>-</div>")

    image_url_display.short_description = "Image"


@admin.register(SiaeGroup)
class SiaeGroupAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "nb_siaes", "created_at"]
    search_fields = ["id", "name"]
    search_help_text = "Cherche sur les champs : ID, Nom"

    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ["sectors"]
    readonly_fields = [f"{field}_last_updated" for field in SiaeGroup.TRACK_UPDATE_FIELDS] + [
        "nb_siaes",
        "logo_url_display",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": ("name", "slug", "siret"),
            },
        ),
        (
            "Détails",
            {
                "fields": (
                    "sectors",
                    "year_constitution",
                    "siae_count",
                    "siae_count_last_updated",
                    "nb_siaes",
                    "employees_insertion_count",
                    "employees_insertion_count_last_updated",
                    "employees_permanent_count",
                    "employees_permanent_count_last_updated",
                    "ca",
                    "ca_last_updated",
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "contact_first_name",
                    "contact_last_name",
                    "contact_email",
                    "contact_phone",
                    "contact_website",
                )
            },
        ),
        (
            "Logo",
            {
                "fields": (
                    "logo_url",
                    "logo_url_display",
                )
            },
        ),
        ("Info", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(siae_count_live=Count("siaes", distinct=True))
        return qs

    def nb_siaes(self, siae_group):
        url = reverse("admin:siaes_siae_changelist") + f"?groups__in={siae_group.id}"
        return format_html(f'<a href="{url}">{siae_group.siae_count_live}</a>')

    nb_siaes.short_description = "Nombre de structures (live)"
    nb_siaes.admin_order_field = "siae_count_live"

    def logo_url_display(self, siae_group):
        if siae_group.logo_url:
            return mark_safe(
                f'<a href="{siae_group.logo_url}" target="_blank">'
                f'<img src="{siae_group.logo_url}" title="{siae_group.logo_url}" style="max-height:300px" />'
                f"</a>"
            )
        return mark_safe("<div>-</div>")

    logo_url_display.short_description = "Logo"
