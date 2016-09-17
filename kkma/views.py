from django.shortcuts import render
import json

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.views.generic import (CreateView, FormView, ListView,
                                  UpdateView, DetailView, View)
                                  

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import ExampleImportForm
from .models import Example
from django.core.serializers.json import DjangoJSONEncoder


class APIResponse(JsonResponse):
    def __init__(self, request, status=200, context=None,
                 encoder=DjangoJSONEncoder, **kwargs):
        self.request = request
        data = self._get_response_data(context, status)
        super(APIResponse, self).__init__(data=data, encoder=encoder,
                                          status=status, **kwargs)

    def _get_response_data(self, context, status):
        request = self.request
        return context


class AddExample(CreateView):
    success_url = '/'
    model = Example
    form_class = ExampleImportForm
    response_class = APIResponse
    
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(AddExample, self).dispatch(request, *args, **kwargs)
        
    def form_valid(self, form):
        example = form.save(commit=False)
        '''query = Example.objects.filter(
            word_type=example.word_type, ws_type=example.ws_type,
            morpheme=example.morpheme, content=example.content
        )
        if len(query) > 0:
            return JsonResponse({'success': False, 'reason': 'Existed'})
        '''
        example.save()
        return JsonResponse({'success': True})
        
    def form_invalid(self, form):
        print form.errors
        return JsonResponse({'success': False})
        
    def get(self, request):
        return JsonResponse({'success': True, 'field': [
            'word_type', 'ws_type', 'morpheme',
            'index', 'content', 'detail', 'field_id',
            'part_id', 'sent_id'
        ]})
        
class AddBatchExample(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(AddBatchExample, self).dispatch(request, *args, **kwargs)
        

    def post(self, request):
        data = request.POST.get('data', '[]')
        try:
            data = json.loads(data)
            Example.objects.bulk_create([Example(**ex) for ex in data])
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'success': False})