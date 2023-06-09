print("Loading all files...")

import pandas as pd
import numpy as np
import seaborn as sns
from tqdm import tqdm
sns.set()
import time
import random
import sys
from common_functions import get_file_index_and_prof_index, get_id, check_for_nan, get_tokenized_words
from get_tf_idf import get_tf_idf_list
from querying import phrase_retrieval, boolean_retrieval
import matplotlib.pyplot as plt

number_of_professors_to_test = 500
ranks = dict()
ranks['prof-name-boolean-retrieval'] = []
ranks['prof-affiliation-boolean-retrieval'] = []
ranks['prof-name-phrase-retrieval'] = []
ranks['prof-affiliation-phrase-retrieval'] = []
ranks['prof-paper-boolean-retrieval'] = []
ranks['prof-paper-phrase-retrieval'] = []
ranks['prof-paper-tf-idf'] = []

recallrate = dict()
recallrate['prof-name-boolean-retrieval-recall-rate-5'] = 0
recallrate['prof-name-boolean-retrieval-recall-rate-10'] = 0
recallrate['prof-affiliation-boolean-retrieval-recall-rate-5']  = 0
recallrate['prof-affiliation-boolean-retrieval-recall-rate-10']  = 0
recallrate['prof-name-phrase-retrieval-recall-rate-5'] = 0
recallrate['prof-name-phrase-retrieval-recall-rate-10'] = 0
recallrate['prof-affiliation-phrase-retrieval-recall-rate-5'] = 0
recallrate['prof-affiliation-phrase-retrieval-recall-rate-10'] = 0
recallrate['prof-paper-boolean-retrieval-recall-rate-5']  = 0
recallrate['prof-paper-boolean-retrieval-recall-rate-10']  = 0
recallrate['prof-paper-phrase-retrieval-recall-rate-5']  = 0
recallrate['prof-paper-phrase-retrieval-recall-rate-10']  = 0
recallrate['prof-paper-tf-idf-recall-rate-5']  = 0
recallrate['prof-paper-tf-idf-recall-rate-10']  = 0

avgquerytime = dict()
avgquerytime['prof-name-boolean-retrieval'] = []
avgquerytime['prof-affiliation-boolean-retrieval'] = []
avgquerytime['prof-name-phrase-retrieval'] = []
avgquerytime['prof-affiliation-phrase-retrieval'] = []
avgquerytime['prof-paper-boolean-retrieval'] = []
avgquerytime['prof-paper-phrase-retrieval'] = []
avgquerytime['prof-paper-tf-idf'] = []

# number of cleaned files
file_count = 26

# read the cleaned csv files 
filepath=r'Re-cleaned-pr0f_data_cleaned/'
data_files = [pd.read_csv(filepath+'/pr0f_data-'+chr(ord('a')+file_index)+'-cleaned.csv',header=None,encoding='utf8') for file_index in range(file_count) ]


def make_list(initial_string):
    '''
    Function to convert str(list) to list

    Input:
    > initial_string - a list type-casted as str

    Output:
    > list of items from the str-type-casted list
    '''
    return initial_string.lstrip('[\'').rstrip('\']').split('\', \'')

def find_median(input_list):
    '''
    Function to find median of elements in input_list
    '''
    input_list.sort()
    N = len(input_list)    
    if N<=2:
        return input_list[0]
    else:
        return input_list[(N + 1)//2]

def find_mean(input_list):
    '''
    Function to find mean of elements in input_list
    '''
    N = len(input_list)
    if N==0:
        return -1
    return (sum(input_list)/N)

def generate_random_professor():
    '''
    Function to choose a random professor from cleaned dataset
    '''
    list_of_prof_count_per_file = list(pd.read_csv('Re-cleaned-pr0f_data_cleaned/metadata.csv', header=None)[0])
    file_index = random.randint(0, len(list_of_prof_count_per_file)-1)
    prof_index = random.randint(0, list_of_prof_count_per_file[file_index]-1)
    return get_id(file_index, prof_index)

def read_prof_information(prof_id):
    '''
    Function to read information of the professor indicated by the given Global ID
    '''
    file_index, prof_index = get_file_index_and_prof_index(prof_id)
    data = dict()       
    data['name'] = check_for_nan(data_files[file_index].iloc[prof_index][1]).strip()    
    data['affiliation'] = check_for_nan(data_files[file_index].iloc[prof_index][3]).strip()        
    data['papers_title_list'] = make_list(data_files[file_index].iloc[prof_index][16])    
    return data

def find_rank_in_list(prof_ids_list, ground_truth_prof_id):
    '''
    Function to find the rank at which a Global ID of a professor appears in a list of Global IDs

    Input:
    > prof_ids_list - list of Global IDs
    > ground_truth_prof_id - the Global ID you want to find the rank of

    Output:
    > rank at which ground_truth_prof_id appears in prof_ids_list
    '''
    index = 0
    for prof_id in prof_ids_list:
        index = index+1
        if prof_id == ground_truth_prof_id:
            return index  
    # if result not found    
    return 9999999   

def find_recall_rate(prof_ids_list, ground_truth_prof_id, recall_rate_number):
    '''
    Function to check if a Global ID appears in top k entries in a list of Global IDs

    Input:
    > prof_ids_list - list of Global IDs
    > ground_truth_prof_id - the Global ID you want to check for
    > recall_rate_number - the number of top entries in which you
                            want to check if ground_truth_prof_id is present

    Output:
    > 1 if found in first recall_rate_number (5 or 10) results, 0 otherwise
    '''
    # Return 1 if find in first recall_rate_number (5 or 10) results
    for i in range(min(recall_rate_number, len(prof_ids_list))):
        if prof_ids_list[i] == ground_truth_prof_id:
            return 1
    return 0

def search_with_name_or_affiliation(search_query, query_method):
    '''
    Function to search in the name_affiliation inverted index using given
    search query and query method and return the results and time taken

    Input:
    > search_query - search query as string
    > query_method - retrieval method to be used (boolean-retrieval or phrase-retrieval)

    Output:
    > query_result_prof_ids - search results as a list of Global IDs of professors
    > time_taken - time taken for query
    '''
    start_time = time.time() 
    parsed_query = get_tokenized_words(search_query,False) # passing 'False' to not remove stop words and not perform stemming
    if query_method=='boolean-retrieval':
        query_result_prof_ids = boolean_retrieval(parsed_query,False)  # passing 'False' to use name and affiliation index
    elif query_method=='phrase-retrieval':
        query_result_prof_ids = phrase_retrieval(parsed_query,False)  # passing 'False' to use name and affiliation index

    time_taken = time.time() - start_time     
    return (query_result_prof_ids, time_taken)  

def search_with_paper_title(search_query, query_method):
    '''
    Function to search in the paper title and topics inverted index using given
    search query and query method and return the results and time taken

    Input:
    > search_query - search query as string
    > query_method - retrieval method to be used (boolean-retrieval, phrase-retrieval or tf-idf)

    Output:
    > query_result_prof_ids - search results as a list of Global IDs of professors
    > time_taken - time taken for query
    '''
    start_time = time.time() 
    parsed_query = get_tokenized_words(search_query,True)
    if query_method=='boolean-retrieval':
        query_result_prof_ids = boolean_retrieval(parsed_query,True)
    elif query_method=='phrase-retrieval':
        query_result_prof_ids = phrase_retrieval(parsed_query,True)
    elif query_method=='tf-idf':
        query_result_prof_ids = get_tf_idf_list(parsed_query)

    time_taken = time.time() - start_time
    return (query_result_prof_ids, time_taken)  



print("Loaded all files. Starting queries..")

count = 0


for i in tqdm(range(number_of_professors_to_test)):

    ground_truth_prof_id = generate_random_professor()
    prof_data = read_prof_information(ground_truth_prof_id)
        
    # If invalid / empty query then continue
    if prof_data['name']=='' or prof_data['affiliation']=='' or len(prof_data['papers_title_list'])==0:
        continue

    count+=1

    # Choose a random paper for the professor
    random_paper_index = random.randint(0, len(prof_data['papers_title_list'])-1)

    # Using name as search query and boolean retrieval as search method    
    search_query = prof_data['name']
    query_method = 'boolean-retrieval'
    (query_result_prof_ids, time_taken) = search_with_name_or_affiliation(search_query, query_method)     
    rank_obtained = find_rank_in_list(query_result_prof_ids, ground_truth_prof_id) 
    recallrate['prof-name-boolean-retrieval-recall-rate-5']+=find_recall_rate(query_result_prof_ids, ground_truth_prof_id, 5)
    recallrate['prof-name-boolean-retrieval-recall-rate-10']+=find_recall_rate(query_result_prof_ids, ground_truth_prof_id, 10)
    ranks['prof-name-boolean-retrieval'].append(rank_obtained)
    avgquerytime['prof-name-boolean-retrieval'].append(time_taken*1000)    

    # Using affiliation as search query and boolean retrieval as search method
    search_query = prof_data['affiliation']
    query_method = 'boolean-retrieval'    
    (query_result_prof_ids, time_taken) = search_with_name_or_affiliation(search_query, query_method)     
    rank_obtained = find_rank_in_list(query_result_prof_ids, ground_truth_prof_id) 
    recallrate['prof-affiliation-boolean-retrieval-recall-rate-5']+=find_recall_rate(query_result_prof_ids, ground_truth_prof_id, 5)
    recallrate['prof-affiliation-boolean-retrieval-recall-rate-10']+=find_recall_rate(query_result_prof_ids, ground_truth_prof_id, 10)
    ranks['prof-affiliation-boolean-retrieval'].append(rank_obtained)
    avgquerytime['prof-affiliation-boolean-retrieval'].append(time_taken*1000)

    # Using name as search query and phrase retrieval as search method    
    search_query = prof_data['name']
    query_method = 'phrase-retrieval'   
    (query_result_prof_ids, time_taken) = search_with_name_or_affiliation(search_query, query_method)
    rank_obtained = find_rank_in_list(query_result_prof_ids, ground_truth_prof_id)  
    recallrate['prof-name-phrase-retrieval-recall-rate-5']+=find_recall_rate(query_result_prof_ids, ground_truth_prof_id, 5)
    recallrate['prof-name-phrase-retrieval-recall-rate-10']+=find_recall_rate(query_result_prof_ids, ground_truth_prof_id, 10)        
    ranks['prof-name-phrase-retrieval'].append(rank_obtained)
    avgquerytime['prof-name-phrase-retrieval'].append(time_taken*1000)

    # Using affiliation as search query and phrase retrieval as search method  
    search_query = prof_data['affiliation']
    query_method = 'phrase-retrieval'     
    (query_result_prof_ids, time_taken) = search_with_name_or_affiliation(search_query, query_method) 
    rank_obtained = find_rank_in_list(query_result_prof_ids, ground_truth_prof_id)  
    recallrate['prof-affiliation-phrase-retrieval-recall-rate-5']+=find_recall_rate(query_result_prof_ids, ground_truth_prof_id, 5)
    recallrate['prof-affiliation-phrase-retrieval-recall-rate-10']+=find_recall_rate(query_result_prof_ids, ground_truth_prof_id, 10)        
    ranks['prof-affiliation-phrase-retrieval'].append(rank_obtained)
    avgquerytime['prof-affiliation-phrase-retrieval'].append(time_taken*1000)
    
    # Using paper title as search query and boolean retrieval as search method
    search_query = prof_data['papers_title_list'][random_paper_index]
    query_method = 'boolean-retrieval' 
    (query_result_prof_ids, time_taken) = search_with_paper_title(search_query, query_method)  
    rank_obtained = find_rank_in_list(query_result_prof_ids, ground_truth_prof_id) 
    recallrate['prof-paper-boolean-retrieval-recall-rate-5']+=find_recall_rate(query_result_prof_ids, ground_truth_prof_id, 5)
    recallrate['prof-paper-boolean-retrieval-recall-rate-10']+=find_recall_rate(query_result_prof_ids, ground_truth_prof_id, 10)         
    ranks['prof-paper-boolean-retrieval'].append(rank_obtained)
    avgquerytime['prof-paper-boolean-retrieval'].append(time_taken*1000)

    # Using paper title as search query and phrase retrieval as search method
    search_query = prof_data['papers_title_list'][random_paper_index]
    query_method = 'phrase-retrieval' 
    (query_result_prof_ids, time_taken) = search_with_paper_title(search_query, query_method)  
    rank_obtained = find_rank_in_list(query_result_prof_ids, ground_truth_prof_id)  
    recallrate['prof-paper-phrase-retrieval-recall-rate-5']+=find_recall_rate(query_result_prof_ids, ground_truth_prof_id, 5)
    recallrate['prof-paper-phrase-retrieval-recall-rate-10']+=find_recall_rate(query_result_prof_ids, ground_truth_prof_id, 10)        
    ranks['prof-paper-phrase-retrieval'].append(rank_obtained)
    avgquerytime['prof-paper-phrase-retrieval'].append(time_taken*1000)

    # Using paper title as search query and tf-idf as search method
    search_query = prof_data['papers_title_list'][random_paper_index]
    query_method = 'tf-idf' 
    (query_result_prof_ids, time_taken) = search_with_paper_title(search_query, query_method)
    rank_obtained = find_rank_in_list(query_result_prof_ids, ground_truth_prof_id) 
    recallrate['prof-paper-tf-idf-recall-rate-5']+=find_recall_rate(query_result_prof_ids, ground_truth_prof_id, 5)
    recallrate['prof-paper-tf-idf-recall-rate-10']+=find_recall_rate(query_result_prof_ids, ground_truth_prof_id, 10)           
    ranks['prof-paper-tf-idf'].append(rank_obtained)
    avgquerytime['prof-paper-tf-idf'].append(time_taken*1000)


for key in recallrate:
    recallrate[key]=(recallrate[key]/count)*100    

# Legend:
# N, B  : 'Prof Name, Boolean'
# N, Ph : 'Prof Name, Phrase'
# A, B  : 'Prof Affiliation, Boolean'
# A, Ph : 'Prof Affiliation, Phrase'
# P, B  : 'Prof Paper, Boolean'
# P, Ph : 'Prof Paper, Phrase'
# P, T  : 'Prof Paper, TF-IDF'

# Plotting the median rank
query_and_method = ['N, B', 'N, Ph', 'A, B', 'A, Ph', 'P, B', 'P, Ph', 'P, T']
ranks_value = [find_median(ranks['prof-name-boolean-retrieval']), find_median(ranks['prof-name-phrase-retrieval']), find_median(ranks['prof-affiliation-boolean-retrieval']), find_median(ranks['prof-affiliation-phrase-retrieval']), find_median(ranks['prof-paper-boolean-retrieval']), find_median(ranks['prof-paper-phrase-retrieval']), find_median(ranks['prof-paper-tf-idf'])]
plt.figure(0)
plt.bar(query_and_method, ranks_value, color='#394fe1')
plt.ylabel('Median Rank')
plt.title('Median rank evaluation for '+str(number_of_professors_to_test)+' ground truths \n Rank represents the position at which desired result appears in search results')
plt.xlabel('Search Query and Method Used')
plt.xticks(fontsize=10,rotation=7)
for i, v in enumerate(ranks_value):
    plt.annotate(str(v), xy=(i,v), xytext=(-7,7), textcoords='offset points')
# plt.savefig('median_rank.png', dpi=300)
plt.show()


# Plotting the recall rate
width = 0.25


query_and_method = ['N, B', 'N, Ph', 'A, B', 'A, Ph', 'P, B', 'P, Ph', 'P, T']
recall_rate_5 = [recallrate['prof-name-boolean-retrieval-recall-rate-5'],recallrate['prof-name-phrase-retrieval-recall-rate-5'],recallrate['prof-affiliation-phrase-retrieval-recall-rate-5'],recallrate['prof-affiliation-boolean-retrieval-recall-rate-5'],recallrate['prof-paper-boolean-retrieval-recall-rate-5'],recallrate['prof-paper-phrase-retrieval-recall-rate-5'],recallrate['prof-paper-tf-idf-recall-rate-5']]
recall_rate_10 = [recallrate['prof-name-boolean-retrieval-recall-rate-10'],recallrate['prof-name-phrase-retrieval-recall-rate-10'],recallrate['prof-affiliation-phrase-retrieval-recall-rate-10'],recallrate['prof-affiliation-boolean-retrieval-recall-rate-10'],recallrate['prof-paper-boolean-retrieval-recall-rate-10'],recallrate['prof-paper-phrase-retrieval-recall-rate-10'],recallrate['prof-paper-tf-idf-recall-rate-10']]
x_1 = [2*i for i in range(len(recall_rate_5))]
x_2 = [x + 2*width for x in x_1]
plt.figure(1)
plt.bar(x_1, recall_rate_5, color ='#394fe1', width = 0.5, edgecolor ='white', label ='Recall Rate @ 5')
plt.bar(x_2, recall_rate_10, color ='#010038', width = 0.5, edgecolor ='white', label ='Recall Rate @ 10')
plt.ylabel('Recall Rate')
plt.title('Recall rate evaluation for '+str(number_of_professors_to_test)+' ground truths \n Recall rate (R@X) represents % of time desired results appeared in top X')
plt.xlabel('Search Query and Method Used')
plt.xticks([2*i + width for i in range(len(recall_rate_5))],query_and_method, fontsize=10, rotation=7)
plt.legend(['Recall Rate @ 5', 'Recall Rate @ 10'])
# plt.savefig('recall_rate.png', dpi=300)
plt.show()

# Plotting the Average Query Time

def get_time_in_ms(time_in_s):
    value = str(time_in_s)
    try:
        value = value[:4]
        return value+" ms"
    except:
        return value+" ms"

query_and_method = ['N, B', 'N, Ph', 'A, B', 'A, Ph', 'P, B', 'P, Ph', 'P, T']
avg_time_value = [find_mean(avgquerytime['prof-name-boolean-retrieval']), find_mean(avgquerytime['prof-name-phrase-retrieval']), find_mean(avgquerytime['prof-affiliation-boolean-retrieval']), find_mean(avgquerytime['prof-affiliation-phrase-retrieval']), find_mean(avgquerytime['prof-paper-boolean-retrieval']), find_mean(avgquerytime['prof-paper-phrase-retrieval']), find_mean(avgquerytime['prof-paper-tf-idf'])]
plt.figure(2)
plt.plot(query_and_method, avg_time_value, 'ro',color='#394fe1')
plt.ylabel('Average Query Time (in ms)')
plt.title('Average query time for '+str(number_of_professors_to_test)+' searches')
plt.xlabel('Search Query and Method Used')
plt.xticks(fontsize=10,rotation=7)
for i, v in enumerate(avg_time_value):
    plt.annotate(get_time_in_ms(v), xy=(i,v), xytext=(-7,7), textcoords='offset points')
# plt.savefig('average_query_time.png', dpi=300)
plt.show()
