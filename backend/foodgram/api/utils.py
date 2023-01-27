from django.http import HttpResponse


def text_cart(querryset):
    content = '\n'.join([
        (f'{ol}. {ingredient["ingredient__name"]} '
         f'{ingredient["amount"]} '
         f'{ingredient["ingredient__measurement_unit"]}'
         ) for ol, ingredient in enumerate(list(querryset), start=1)
    ])
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = (
            'attachment;'
            ' filename=shopping-list.txt'
        )
    return response
