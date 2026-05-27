from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):

    # Display fields in admin panel table
    list_display = (
        'id',
        'username',
        'useremail',
        'userphone',
        'usergender',
        'usercity',
        'userstate',
        'is_verified',
        'created_at',
    )

    # Search bar
    search_fields = (
        'username',
        'useremail',
        'userphone',
        'usercity',
        'userstate',
    )

    # Right-side filters
    list_filter = (
        'usergender',
        'userstate',
        'is_verified',
        'created_at',
    )

    # Editable directly from admin table
    list_editable = (
        'is_verified',
    )

    # Pagination
    list_per_page = 10

    # Default ordering
    ordering = ('-created_at',)

    # Read-only fields
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # Admin form sections
    fieldsets = (

        ('Personal Information', {
            'fields': (
                'username',
                'useremail',
                'userphone',
                'userdob',
                'usergender',
            )
        }),

        ('Location Details', {
            'fields': (
                'usercity',
                'userstate',
            )
        }),

        ('Message Information', {
            'fields': (
                'usermessage',
            )
        }),

        ('Verification', {
            'fields': (
                'is_verified',
            )
        }),

        ('Date Information', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),

    )