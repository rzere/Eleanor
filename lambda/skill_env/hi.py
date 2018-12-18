from newsapi import NewsApiClient

a = NewsApiClient(api_key='3142bb731e6c4c9a99799f31b629985c')

f = a.get_everything(q='Amazon', sources='the-new-york-times', sort_by='relevancy', from_param='2018-12-06')
articles = f['articles']

print([a['title'] for a in articles])