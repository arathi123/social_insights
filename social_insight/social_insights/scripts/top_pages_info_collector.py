
# coding: utf-8

# In[22]:

import facebook
import pandas as pd
import math
import csv


# In[30]:

graph = facebook.GraphAPI(access_token='EAAPQpBr7UBQBAIeJbpVdpd3MPk4Q3E1as1ETNQN1zPDbZCqvUE8xgb0qATlSUU7ZCoyBZB6iyukGPjLZCG1Wo1JNcRq8B7nLYio8KEcqWosL4i2momiRywCAvrsGjLGm5KZAzd7q2ZB1qkVGKsimCBWjZBHanZASqFAZD', 
                          version='2.5')
def get_facebook_ids_for_top_pages():
    sm_accounts = pd.read_csv('../db/sm_accounts_top.csv',names=['id','name','link','dummy'])
    page_names = list(sm_accounts.link.str.rstrip('/').str.split('/').apply(lambda x: x[-1]).values)
    page_ids = {}
    for i in range(math.ceil(len(page_names)/50)):
        page_ids.update(graph.get_objects(page_names[i*50:(i*50)+49],fields='id,name,fan_count,category,description,verification_status'))
    page_infos = pd.DataFrame(page_ids).T
    page_infos['link'] = page_infos.id.apply(lambda x:"https://www.facebook.com/"+x)
    page_infos = page_infos.loc[:,['id','name','link','category','description','verification_status']]
    page_infos['id'] = page_infos['id'].astype(int)
    page_infos.to_csv('sm_accounts_top_info.csv',quoting=csv.QUOTE_NONNUMERIC,index=False)
    page_infos.loc[:,['id','name','link']].to_csv('sm_accounts_.csv',quoting=csv.QUOTE_NONNUMERIC,index=False)


# In[31]:

get_facebook_ids_for_top_pages()


# In[ ]:



