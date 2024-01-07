from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import User, Passport, Achievement, Comment, Rating


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            ("Personal info"),
            {"fields": ("first_name", "last_name", "phone", "email", "slug")},
        ),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    prepopulated_fields = {"slug": ("username",)}


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ["title", "description", "bonus"]
    list_display_links = ["title"]
    list_filter = ["bonus"]


@admin.register(Passport)
class PassportAdmin(admin.ModelAdmin):
    list_display = ["user", "date_issue", "date_expiry"]
    list_display_links = ["user"]
    list_filter = ["date_expiry"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["user", "message", "date", "likes_count", "comment_object"]
    list_display_links = ["comment_object"]
    # list_filter = ["comment_object"]

    @admin.display(description="Likes")
    def likes_count(self, obj):
        return obj.likes.count()


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ["user", "rate", "rating_object"]
    list_display_links = ["rating_object"]

    # list_filter = ["rating_object"]