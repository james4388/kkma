# -*- coding: UTF-8 -*-

from django.contrib import admin
from .models import Example, Phrase
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ExportMixin, ImportExportActionModelAdmin
from import_export import fields
from django.utils.html import strip_tags
from django.shortcuts import render
from django.http import JsonResponse
from django.conf.urls import url
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.filters import ChoicesFieldListFilter
import itertools
from django.utils.encoding import force_text, smart_text
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Count
from django.shortcuts import get_object_or_404
import random
from django.http import JsonResponse

from .naver import translate
from .forms import FlashcardForm

from utils import import_xls


class IgnoreParamChangeList(ChangeList):
    ignore_params = ['object_index', 'limit']

    def get_filters_params(self, params=None):
        lookup_params = super(IgnoreParamChangeList, self).get_filters_params(params)
        for ignored in self.ignore_params:
            if ignored in lookup_params:
                del lookup_params[ignored]
        return lookup_params


class ExampleResource(resources.ModelResource):
    class Meta:
        model = Example
        fields = ('content', 'category', 'prefix', 'suffix', 'morpheme', 'used_in')
        export_order = ('content', 'morpheme', 'category', 'prefix', 'suffix', 'used_in')

    def dehydrate_content(self, row):
        return strip_tags(row.content)


class CategoryListFilter(ChoicesFieldListFilter):
    def choices(self, changelist):
        yield {
            'selected': self.lookup_val is None,
            'query_string': changelist.get_query_string(
                {}, [self.lookup_kwarg, self.lookup_kwarg_isnull]
            ),
            'display': _('All')
        }
        yield {
            'selected': self.lookup_val_isnull == 'False',
            'query_string': changelist.get_query_string({
                self.lookup_kwarg_isnull: 'False',
            }, [self.lookup_kwarg]),
            'display': _('Any'),
        }
        yield {
            'selected': self.lookup_val_isnull == 'True',
            'query_string': changelist.get_query_string({
                self.lookup_kwarg_isnull: 'True',
            }, [self.lookup_kwarg]),
            'display': _('Not set'),
        }
        for lookup, title in self.field.flatchoices:
            if lookup is None:
                continue
            yield {
                'selected': smart_text(lookup) == self.lookup_val,
                'query_string': changelist.get_query_string(
                    {self.lookup_kwarg: lookup}, [self.lookup_kwarg_isnull]
                ),
                'display': title,
            }


class ExamplePhraseInline(admin.TabularInline):
    model = Example.phrases.through
    exclude = ('phrase', )
    readonly_fields = ('_phrase_link', 'phrase', '_phrase_count')
    extra = 0
    verbose_name = "Examples"
    verbose_name_plural = "Examples"
    can_delete = False

    def get_queryset(self, request):
        qs = super(ExamplePhraseInline, self).get_queryset(request)
        return qs.select_related('phrase')

    def _phrase_count(self, instance):
        return instance.phrase.count
    _phrase_count.short_description = 'Count'

    def _phrase_link(self, instance):
        return mark_safe('<a href="%s" target="_blank">%d</a>' % (
            reverse('admin:kkma_phrase_change', args=(instance.phrase.id,)),
            instance.phrase.id
        ))
    _phrase_link.short_description = "Link"


class ExamplePhraseInline(admin.TabularInline):
    model = Phrase.examples.through
    extra = 1


class ExampleAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ExampleResource
    list_display = ('content_display', 'category', 'prefix', 'suffix', 'morpheme', 'used_in',)
    list_editable = ('category', 'prefix', 'suffix')
    list_filter = (
        ('category', CategoryListFilter, ),
        'morpheme', 'used_in', 
        'modified_on'
    )
    search_fields = ('content',)
    exclude = ('phrases', )
    inlines = (ExamplePhraseInline, )

    change_list_template = 'kkma/example/change_list.html'
    flash_card_template = 'kkma/example/flash_card.html'
    
    def content_display(self, instance):
        content = instance.content
        for phrase in instance.phrases.all():
            content = content.replace(phrase.phrase, u'<b>%s</b>' % phrase.phrase)
        return mark_safe(content)
    content_display.short_description = '용례'

    
    def get_queryset(self, request, *args, **kwargs):
        qs = super(ExampleAdmin, self).get_queryset(request, *args, **kwargs)
        return qs.prefetch_related('phrases')
        

    def get_changelist(self, request, **kwargs):
        return IgnoreParamChangeList

    # Allow limit result
    def get_export_queryset(self, request):
        qs = super(ExampleAdmin, self).get_export_queryset(request)

        limit = request.POST.get('limit', request.GET.get('limit'))
        try:
            limit = int(limit)
        except:
            pass
        if limit and isinstance(limit, int):
            qs = qs[:limit]
        return qs

    def get_urls(self):
        urls = super(ExampleAdmin, self).get_urls()
        my_urls = [
            url(r'^flash-card/$',
                self.admin_site.admin_view(self.flash_card_view),
                name='%s_%s_flashcard' % self.get_model_info()),
            url(r'^translate/$',
                self.admin_site.admin_view(self.translate_view),
                name='%s_%s_translate' % self.get_model_info()),
            url(r'^import/$',
                self.admin_site.admin_view(self.import_xls_view),
                name='%s_%s_import' % self.get_model_info()),
        ]
        return my_urls + urls

    def get_flashcard_queryset(self, request):
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)

        cl = IgnoreParamChangeList(
            request, self.model, list_display,
            list_display_links, self.list_filter,
            self.date_hierarchy, self.search_fields,
            self.list_select_related, self.list_per_page,
            self.list_max_show_all, self.list_editable,
            self
        )
        try:
            return cl.queryset
        except AttributeError:
            return cl.query_set.prefetch_related('phrases')
            
    def translate_view(self, request, *args, **kwargs):
        query = request.GET.get('query')
        meaning = {}
        if query:
            meaning = translate(query)
        return JsonResponse(meaning)

    def flash_card_view(self, request, *args, **kwargs):
        object_index = request.GET.get('object_index', 0)
        try:
            object_index = int(object_index)
        except:
            object_index = 0

        queryset = self.get_flashcard_queryset(request)

        total = queryset.count()

        form = None
        if request.method == 'POST':
            obj = get_object_or_404(Example, pk=request.POST.get('pk'))
            form = FlashcardForm(request.POST, instance=obj)
            if form.is_valid():
                form.save()
            if request.POST.get('random'):
                # Re-evaluate queryset
                queryset = self.get_flashcard_queryset(request)
                total = queryset.count()
                if total > 1:
                    object_index = random.randint(0, total - 1)
                objects = queryset[object_index:object_index + 1]
                obj = objects[0] if len(objects) > 0 else None
                form = FlashcardForm(instance=obj)
        else:
            objects = queryset[object_index:object_index + 1]
            obj = objects[0] if len(objects) > 0 else None
            if obj:
                form = FlashcardForm(instance=obj)
        
        # Highlight phrase
        if obj:
            content = obj.content
            for phrase in obj.phrases.all():
                content = content.replace(phrase.phrase, u'<b>%s</b>' % phrase.phrase)
            obj.content = content
        
        prev_link = None
        next_link = None
        queries = request.GET.copy()
        
        # Get random example
        if total > 1:
            queries['object_index'] = random.randint(0, total - 1)
            next_link = queries.urlencode()
        
        queries.pop('object_index', None)
        filter_link = queries.urlencode()
        return render(request, self.flash_card_template, {
            'object': obj,
            'total': total,
            'index': object_index,
            'form': form,
            'next_link': next_link,
            'filter_link': filter_link
        })
        
    def import_xls_view(self, request, *args, **kwargs):
        REQUIRE_PARAMS = ['file_path', 'morpheme', 'used_in']
        params = {
            'dry_run': False,   # Test run, no import needed
            'content_col': 1,   # Column B  C   D   E   F   G
            'category_col': 3,  # Column 1  2   3   4   5   6
            'prefix_col': 4,
            'suffix_col': 5,
            'exclude_rich': 2,  # Exclude 2 last rich text map
            'start_from': 1,    # Row #2, exclude header
        }
        OPTIONAL_PARAMS = params.keys()
        for param in REQUIRE_PARAMS:
            value = request.GET.get(param)
            if not value:
                return JsonResponse({"error": "Missing param: %s" % param})
            params[param] = value
        for param in OPTIONAL_PARAMS:
            value = request.GET.get(param)
            if value:
                if isinstance(params[param], bool):
                    params[param] = value.lower() in ['true','yes','1']
                elif isinstance(params[param], int):
                    try:
                        params[param] = int(value)
                    except ValueError:
                        return JsonResponse({"error": "Param %s is not a valid integer" % param})
        success, result = import_xls(**params)
        return JsonResponse({"success": success, "result": result, "params": params})

admin.site.register(Example, ExampleAdmin)


class PhraseExampleInline(admin.TabularInline):
    model = Phrase.examples.through
    exclude = ('example', )
    readonly_fields = ('_example_link', '_example',)
    extra = 0
    verbose_name = "Examples"
    verbose_name_plural = "Examples"
    can_delete = False

    def get_queryset(self, request):
        qs = super(PhraseExampleInline, self).get_queryset(request)
        return qs.select_related('example')

    def _example(self, instance):
        content = unicode(instance.example)
        content = content.replace(instance.phrase.phrase, u'<b>%s</b>' % instance.phrase.phrase)
        return mark_safe(content)
    _example.short_description = "Example"

    def _example_link(self, instance):
        return mark_safe('<a href="%s" target="_blank">%d</a>' % (
            reverse('admin:kkma_example_change', args=(instance.example.id,)),
            instance.example.id
        ))
    _example_link.short_description = "Link"


class PhraseAdminChangeList(ChangeList):
    ignore_params = ['object_index', 'limit']

    def get_queryset(self, request):
        qs = super(PhraseAdminChangeList, self).get_queryset(request)
        return qs.annotate(example_count=Count('examples'))


class PhraseAdmin(admin.ModelAdmin):
    list_display = ('phrase', 'example_count', 'count', )
    #readonly_fields = ('phrase', )
    list_filter = ('examples__morpheme', 'examples__category', 'examples__used_in')
    inlines = (PhraseExampleInline, )

    def get_changelist(self, request, **kwargs):
        return PhraseAdminChangeList

    def example_count(self, instance):
        return mark_safe(instance.example_count)
    example_count.short_description = "Count"
    example_count.admin_order_field = "example_count"

admin.site.register(Phrase, PhraseAdmin)
