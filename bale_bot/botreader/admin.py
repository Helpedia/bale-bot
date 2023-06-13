from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.helpers import ActionForm
from django.urls import reverse
from django.db.models import Count, Q
from django import forms
from django.utils.html import format_html
from adminfilters.filters import (
    AutoCompleteFilter,
    DjangoLookupFilter,
    ChoicesFieldComboFilter,
)
from adminfilters.mixin import AdminFiltersMixin
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .models import (
    TextMessage,
    User,
    Chat,
    Membership,
    GeneratedAnswer,
    ArchivedTextMessage,
)
from django_admin_inline_paginator.admin import TabularInlinePaginated
from import_export import resources
from import_export.admin import ImportMixin
from import_export.forms import ImportForm, ConfirmImportForm


class ChatMembersInline(TabularInlinePaginated):
    model = Membership
    per_page = 20
    fields = ("member", "exited", "last_membership_date")
    verbose_name = "Member"
    verbose_name_plural = "Members"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(exited=False)


@admin.register(Chat)
class ChatModelAdmin(admin.ModelAdmin):
    list_display = ("display_title", "type")
    search_fields = ("title", "first_name", "last_name", "username")
    list_filter = ("type",)
    empty_value_display = "----"
    inlines = (ChatMembersInline,)

    @admin.display(description="Title")
    def display_title(self, obj):
        if obj.type == "private":
            full_name = f"{obj.first_name} {obj.last_name}".strip()
            title = f"{full_name}@{obj.username}" if obj.username else full_name
        else:
            title = obj.title
        return title

    def get_fieldsets(self, request, obj=None):
        if obj.type == "private":
            fieldsets = ((None, {"fields": (("first_name", "last_name"), "username")}),)
        else:
            fieldsets = ((None, {"fields": (("title", "type"), "admins")}),)
        return fieldsets

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserModelAdmin(AdminFiltersMixin, admin.ModelAdmin):
    search_fields = ("name", "username", "first_name", "last_name", "mobile")
    list_display = (
        "display_name",
        "display_messages_count",
        "display_reply_messages_count",
        "display_questions_count",
        "display_answers_and_suggestions_count",
        "type",
    )
    list_filter = (
        ("memberships__chat", AutoCompleteFilter),
        ("type", ChoicesFieldComboFilter),
    )
    list_editable = ("type",)
    empty_value_display = "----"
    readonly_fields = ("uid", "name", "username")
    fieldsets = [
        (
            None,
            {
                "fields": (
                    (
                        "name",
                        "username",
                    )
                )
            },
        ),
        (
            None,
            {
                "fields": (
                    ("first_name", "last_name"),
                    "mobile",
                )
            },
        ),
        (None, {"fields": ("type",)}),
    ]

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .prefetch_related("textmessages")
            .annotate(textmessages_count=Count("textmessages"))
            .annotate(
                replymessages_count=Count(
                    "textmessages", filter=Q(textmessages__reply__isnull=False)
                )
            )
            .annotate(
                questions_count=Count(
                    "textmessages", filter=Q(textmessages__type="QUESTION")
                )
            )
            .annotate(
                answers_and_suggestions_count=Count(
                    "textmessages",
                    filter=Q(textmessages__type="ANSWER")
                    | Q(textmessages__type="SUGGESTION"),
                )
            )
        )
        return queryset

    @admin.display(description="Name", ordering="name")
    def display_name(self, obj):
        name = f"{obj.name}@{obj.username}" if obj.username else obj.name
        return name

    @admin.display(description="Messages Count", ordering="textmessages_count")
    def display_messages_count(self, obj):
        return obj.textmessages.count()

    @admin.display(description="Reply Messages Count", ordering="replymessages_count")
    def display_reply_messages_count(self, obj):
        return obj.textmessages.filter(reply__isnull=False).count()

    @admin.display(description="Questions Count", ordering="questions_count")
    def display_questions_count(self, obj):
        return obj.textmessages.filter(type="QUESTION").count()

    @admin.display(
        description="Answers and Suggestions Count",
        ordering="answers_and_suggestions_count",
    )
    def display_answers_and_suggestions_count(self, obj):
        return obj.textmessages.filter(Q(type="ANSWER") | Q(type="SUGGESTION")).count()

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False


class GeneratedAnswerTabularInline(admin.TabularInline):
    model = GeneratedAnswer
    extra = 0
    max_num = 1
    fields = ("ai_answer", "human_answer", "status", "created_at")
    readonly_fields = ("id", "created_at")


class TextMessageTypeForm(ActionForm):
    type = forms.ChoiceField(choices=TextMessage.TEXT_MESSAGE_TYPE)


@admin.register(TextMessage)
class TextMessageModelAdmin(AdminFiltersMixin, admin.ModelAdmin):
    list_display = ("text_message_link", "date", "type", "sender", "chat")
    search_fields = ("text",)
    list_filter = (
        ("chat", AutoCompleteFilter),
        ("sender", AutoCompleteFilter),
        ("type", ChoicesFieldComboFilter),
        DjangoLookupFilter,
    )
    list_editable = ("type",)
    empty_value_display = "----"
    fieldsets = [
        (None, {"fields": (("chat", "sender"),)}),
        (None, {"fields": ("text", "date", "type")}),
        (None, {"fields": ("reply",)}),
    ]
    readonly_fields = ("id", "message_id", "chat", "sender", "text", "date", "reply")
    ordering = ("-date", "sender", "chat")

    action_form = TextMessageTypeForm

    actions = ("set_text_message_type",)

    inlines = [
        GeneratedAnswerTabularInline,
    ]

    @admin.action(permissions=["change"], description="Set Text Message Type")
    def set_text_message_type(self, request, queryset):
        type = request.POST.get("type", "")
        queryset.update(type=type)
        self.message_user(
            request,
            f"{queryset.count()} text message was changed successfully.",
            messages.SUCCESS,
        )

    @admin.display(description="Text")
    def text_message_link(self, obj):
        url = reverse("admin:botreader_textmessage_change", args=(obj.id,))
        return format_html("<a target='{}' href='{}'>{}</a>", "_blank", url, obj.text)

    def get_queryset(self, request):
        return super().get_queryset(request)

    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return super().get_search_results(request, queryset, search_term)
        query = SearchQuery(search_term, search_type="websearch")
        vector = SearchVector("text")
        rank = SearchRank(vector, query)
        queryset = (
            queryset.annotate(search=vector)
            .annotate(rank=rank)
            .filter(search=query)
            .order_by("-rank")
        )
        return queryset, False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False


class ArchivedTextMessageImportForm(ImportForm):
    chat_id = forms.CharField()


class ArchivedTextMessageConfirmImportForm(ConfirmImportForm):
    chat_id = forms.CharField()


class ArchivedTextMessageResource(resources.ModelResource):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_id = kwargs.get("chat_id")

    def before_import_row(self, row, row_number=None, **kwargs):
        row["chat_id"] = self.chat_id
        return super().before_import_row(row, row_number, **kwargs)

    class Meta:
        model = ArchivedTextMessage
        fields = ("sid", "chat_id", "text", "hashtags")
        import_id_fields = ("sid",)
        skip_unchanged = True
        report_skipped = True


@admin.register(ArchivedTextMessage)
class ArchivedTextMessageModelAdmin(ImportMixin, admin.ModelAdmin):
    list_display = ("sid", "text", "hashtags")
    search_fields = ("text", "hashtags")
    readonly_fields = ("sid", "chat_id", "text")
    list_editable = ("hashtags",)
    list_filter = ("chat_id",)
    fieldsets = [
        (None, {"fields": (("sid", "chat_id"),)}),
        (None, {"fields": ("text",)}),
        (None, {"fields": ("hashtags",)}),
    ]

    resource_class = ArchivedTextMessageResource
    import_form_class = ArchivedTextMessageImportForm
    confirm_form_class = ArchivedTextMessageConfirmImportForm

    def get_confirm_form_initial(self, request, import_form):
        initial = super().get_confirm_form_initial(request, import_form)
        if import_form:
            initial["chat_id"] = import_form.cleaned_data["chat_id"]
        return initial

    def get_import_resource_kwargs(self, request, *args, **kwargs):
        kwargs = super().get_resource_kwargs(request, *args, **kwargs)
        if request.method == "POST":
            chat_id = request.POST.get("chat_id", "")
            kwargs.update({"chat_id": chat_id})
        return kwargs

    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return super().get_search_results(request, queryset, search_term)
        query = SearchQuery(search_term, search_type="websearch")
        vector = SearchVector("text")
        rank = SearchRank(vector, query)
        queryset = (
            queryset.annotate(search=vector)
            .annotate(rank=rank)
            .filter(search=query)
            .order_by("-rank")
        )
        return queryset, False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True
