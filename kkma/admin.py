from django.contrib import admin
from .models import Example, Phrase
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ExportMixin, ImportExportActionModelAdmin
from import_export import fields
from django.utils.html import strip_tags
from django.shortcuts import render
from django.conf.urls import url
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.filters import ChoicesFieldListFilter
import itertools
from django.utils.encoding import force_text, smart_text
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Count


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
        fields = ('index', 'content', 'category',)
        export_order = ('index', 'content', 'category',)
        
    def dehydrate_content(self, row):
        return strip_tags(row.content).replace('&#13;', '')
        

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
        none_title = ''
        for lookup, title in self.field.flatchoices:
            if lookup is None:
                none_title = title
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
            reverse('admin:kkma_phrase_change', args=(instance.phrase.id,)), instance.phrase.id
        ))
    _phrase_link.short_description = "Link"

    
class ExampleAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ExampleResource
    list_display = ('_index', '_content', 'category',
                    'detail_link', 'context_link', 'field_id', 'part_id', 'sent_id')
    list_editable = ('category',)
    list_filter = (
        'ws_type',
        ('category', CategoryListFilter, ),
        'viewed', 'word_type', 'morpheme'
    )
    search_fields = ('content',)
    exclude = ('phrases', )
    inlines = (ExamplePhraseInline, )
    
    change_list_template = 'kkma/example/change_list.html'
    flash_card_template = 'kkma/example/flash_card.html'
    
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
        ]
        return my_urls + urls
        
    def get_flashcard_queryset(self, request):
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)

        cl = IgnoreParamChangeList(request, self.model, list_display,
                        list_display_links, self.list_filter,
                        self.date_hierarchy, self.search_fields,
                        self.list_select_related, self.list_per_page,
                        self.list_max_show_all, self.list_editable,
                        self)
        try:
            return cl.queryset
        except AttributeError:
            return cl.query_set
        
    def flash_card_view(self, request, *args, **kwargs):
        object_index = request.GET.get('object_index', 0)
        try:
            object_index = int(object_index)
        except:
            object_index = 0
        
        queryset = self.get_flashcard_queryset(request)
        
        total = queryset.count()
        
        objects = queryset[object_index:object_index + 1]
        return render(request, self.flash_card_template, {
            'object': objects[0] if len(objects) > 0 else None,
            'total': total,
            'index': object_index
        })
        
    
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
        return mark_safe(instance.example)
    _example.short_description = "Example"
    
    def _example_link(self, instance):
        return mark_safe('<a href="%s" target="_blank">%d</a>' % (
            reverse('admin:kkma_example_change', args=(instance.example.id,)), instance.example.id
        ))
    _example_link.short_description = "Link"


class PhraseAdminChangeList(ChangeList):
    ignore_params = ['object_index', 'limit']
    
    def get_queryset(self, request):
        qs = super(PhraseAdminChangeList, self).get_queryset(request)
        return qs.annotate(example_count=Count('examples'))


class PhraseAdmin(admin.ModelAdmin):
    list_display = ('phrase', 'example_count', 'count', )
    readonly_fields = ('phrase', )
    list_filter = ('examples__ws_type', )
    inlines = (PhraseExampleInline, )
    
    def get_changelist(self, request, **kwargs):
        return PhraseAdminChangeList
   
    def example_count(self, instance):
        return mark_safe(instance.example_count)
    example_count.short_description = "Count"
    example_count.admin_order_field = "example_count"
    
admin.site.register(Phrase, PhraseAdmin)