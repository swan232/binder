# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 17:27:42 2023

@author: shens
"""
import json
import tkinter as tk
from tkinter import filedialog
import os
import copy

def recursive_items(dictionary):
    for key, value in dictionary.items():
        yield (key, value)
        if isinstance(value, dict):
            yield from recursive_items(value)
            
        elif isinstance(value, list):
            if len(value)>0:
                for v in value:
                    if isinstance(v, dict):
                        yield from recursive_items(v)
                        
        

# update a nested python dictionary with any key value pair
def update_nested(in_dict, key, value):
   # global in_dict
   for k, v in in_dict.items():
       if key == k:
           in_dict[k] = value
       elif isinstance(v, dict):
           update_nested(v, key, value)
       elif isinstance(v, list):
           for o in v:
               if isinstance(o, dict):
                   update_nested(o, key, value)
                   
                   
# convert original python dictionary into one with all keys and their corresponding values
def flatten_dict(dictionary):
    data_flattened = {}
    for k, v in recursive_items(dictionary):
        data_flattened[k] = v
    return data_flattened

                   
# anatomy of qsf file
# https://gist.github.com/ctesta01/d4255959dace01431fb90618d1e8c241

root = tk.Tk()
# Hide the window
root.attributes('-alpha', 0.0)
# Always have it on top
root.attributes('-topmost', True)
# file_name = tk.filedialog.askopenfilename(  parent=root, 
#                                             title='Open file',
#                                             # initialdir=starting_dir,
#                                             filetypes=[("text files", "*.txt")])


file = filedialog.askopenfilename(parent = root, 
                                    initialdir = os.getcwd(),
                                      title = "Select a File",
                                      # filetypes =[('json files', '*.json')]) 
                                      filetypes =[('files', '*.*')]) 

# Destroy the window when the file dialog is finished
root.destroy()

# file = "D:/LB_fast.json"

print("File Opened: ", file)
    
# load data
with open(file) as json_file:
    data = json.load(json_file)

    

# print('Qualtrics qsf file is: /n', data)

data['SurveyEntry']['SurveyName'] = data['SurveyEntry']['SurveyName'] + '_modified'

# data.keys()
# Out[6]: dict_keys(['SurveyEntry', 'SurveyElements'])

data['SurveyElements'] # a list
len(data['SurveyElements']) # 434
elements = data['SurveyElements']
print('number of elements', str(len(elements)))
type(elements[0]) # dict
elements[0].keys()
# Out[14]: dict_keys(['SurveyID', 'Element', 'PrimaryAttribute', 'SecondaryAttribute', 'TertiaryAttribute', 'Payload'])

# geth the PrimaryAttribute of each element


# for e in elements[0:6]:
#     print(e['PrimaryAttribute'])
    
blocks = elements[0]
flow = elements[1]

# select elements that are survey questions

questions = [e for e in elements if e['Element'] == "SQ"]

len(questions) # 425
questions[0]


question_tags = [q['Payload']['DataExportTag'] for q in questions]
question_tags

# select quesiton tags that matches a specific string x
def group_tag(x, tag_list):
    question_tags_x = [t for t in tag_list if x in t]
    return question_tags_x




keys = ['INSTS', 'fix','title', 'video', 'truth', 'conf', 'symp', 'donate', 'recognize'] + [t + '_timing' for t in ['fix','title', 'video', 'truth', 'conf', 'symp', 'donate', 'recognize']] + ['P1_', 'P2_'] + ['V' + str(i) + '_' for i in range(1,24)]


tag_groups = [group_tag(k, question_tags) for k in keys]

tag_groups_dict = {}
for k in keys:
    tag_groups_dict[k] = group_tag(k, question_tags)


symp_tags = tag_groups_dict['symp']

symp_tags_timing = tag_groups_dict['symp_timing']

# symp visual analog scale
symp_tags_vas = set(symp_tags).difference(set(symp_tags_timing))
print(symp_tags_vas)


[(keys[index], len(g)) for index, g in enumerate(tag_groups)]


questions[180]

# survey options
options = [e for e in elements if e['Element'] == "SO"]
len(options)
options

# look for "Maxseconds":5 and change it to :0
# "Payload" -> "Configuration" -> "Maxseconds"


question_qids = [q['Payload']['QuestionID'] for q in questions]


for index, q in enumerate(questions):
    if q['Payload']['QuestionID'] == "QID216":
        print(index, q['Payload']['Configuration'])




# get element index given a search condition
def get_elem_index(element_list, condition):
   return [index for index, elem in enumerate(element_list) if condition(elem)]


# define the search condition:  element contains a key "Maxseconds" and its value is 5
def check_if_elem_contains_max5(elem):
   elem_flattened=flatten_dict(elem)
   if 'MaxSeconds' in elem_flattened.keys():
       if elem_flattened['MaxSeconds'] == 5:
           return True
       else:
           return False
   else:     
       return False

# define the search condition:  element contains a key "slider" 
def check_if_elem_contains_sliderpoint5(elem):
   elem_flattened=flatten_dict(elem)
   if 'SliderStartPositions' in elem_flattened.keys():
       if elem_flattened['SliderStartPositions']['1'] != 0.5:
           return True
       else:
           return False
       
   else: 
       return False


def check_if_elem_contains_slider(elem):
   elem_flattened=flatten_dict(elem)
   if 'QuestionType' in elem_flattened.keys():
       if elem_flattened['QuestionType']== 'Slider':
           return True
       else:
           return False
       
   else: 
       return False


# create a deep copy of original data
data_new = copy.deepcopy(data)

# functionalize codes to find and replace maxseconds = 5 to "0"
def edit_max5():
   
   # find all questions with "Maxsecond":5
   
   # questions contain maxsecond
   questions_max = [q for q in questions if 'MaxSeconds' in q['Payload']['Configuration'].keys()]
   
   len(questions_max)
   
   # quesitons which maxsecond=5
   questions_max5 = [q for q in questions_max if q['Payload']['Configuration']['MaxSeconds'] == 5]
   len(questions_max5)
   #  get the labels of these quesitons to make sure which need to be modified
   
   question_tags_max5 = [q['Payload']['DataExportTag'] for q in questions_max5]
   
   
   len(question_tags_max5) # 126
   print('tags of questions with maxsecond = 5: ', question_tags_max5)
   
   keys1 = ['P1_', 'P2_'] + ['V' + str(i) + '_' for i in range(1,24)]
   tag_groups = [group_tag(k, question_tags_max5) for k in keys1]
   
   
   [(keys1[index], len(g)) for index, g in enumerate(tag_groups)]
   
   
   
   len(keys1) * 5
   
   
   [q for q in question_tags_max5 if 'V3' in q] # one extra question is maxsecond = 5, V3_title_timing should be 2 not 5
   [q for q in question_tags_max5 if 'V2_' in q]
   
   questions_max[2]
   
   
   
   # get their index
   
   
   # now, programmatically change maxseconds for these 125 questions to 0
   
   elements_new = data_new['SurveyElements']
   
   
   
   check_if_elem_contains_max5(elements[100])
   # how many elements meet this criterion
   len([e_new for e_new in elements_new if check_if_elem_contains_max5(e_new)]) # 126 confirm that this search condition works
   
   # now implement this search condition to get the indices of elements that need to be updated 
   index_max5 = get_elem_index(elements_new, check_if_elem_contains_max5)
   
   # disable auto advance in qualtrics
   # set MaxSeconds to "0"
   
   
   # after uploading the qsf file, the survey gets stuck at the quesiton, where originally had auto-advance
   # it turns out that a JS component was added to the question via "Edit Question JS". the JS code relies on auto-advance to 
   # display the "Next" button. now, given since auto advance is turned off, with this JS code, it will not show the "Next" button
   # therefore, the JS code needs to be removed as well
   
   # below is the qsf code chunk for P2_recognize_timing. 
   # you can see that the dictionary doesn't have a key called 'QuestionJS' 
   # {'SurveyID': 'SV_54lNaXcNudnVSqq',
   #  'Element': 'SQ',
   #  'PrimaryAttribute': 'QID603',
   #  'SecondaryAttribute': 'Timing',
   #  'TertiaryAttribute': None,
   #  'Payload': {'QuestionText': 'Timing',
   #   'DefaultChoices': False,
   #   'DataExportTag': 'P2_recognize_timing',
   #   'QuestionType': 'Timing',
   #   'Selector': 'PageTimer',
   #   'Configuration': {'QuestionDescriptionOption': 'UseText',
   #    'MinSeconds': '0',
   #    'MaxSeconds': '0'},
   #   'QuestionDescription': 'Timing',
   #   'Choices': {'1': {'Display': 'First Click'},
   #    '2': {'Display': 'Last Click'},
   #    '3': {'Display': 'Page Submit'},
   #    '4': {'Display': 'Click Count'}},
   #   'GradingData': [],
   #   'Language': [],
   #   'NextChoiceId': 52,
   #   'NextAnswerId': 1,
   #   'QuestionID': 'QID603',
   #   'DataVisibility': {'Private': False, 'Hidden': False}}}
   
   
   # here is the JS code snippet for automatic forward to next question
   # https://community.qualtrics.com/custom-code-12/automatic-forwarding-to-next-question-2279
   
   for i in index_max5:
       # get the element
       thiselem = elements_new[i]
       # modify the element
       # first change MaxSeconds to '0'
       update_nested(thiselem, 'MaxSeconds', '0')
       # next remove the 'QuestionJS' key-value pair is there is any
       if 'QuestionJS' in thiselem['Payload'].keys():
           thiselem['Payload'].pop('QuestionJS')
       # update elements_new
       elements_new[i] = thiselem
       
   
   # check modification is correct
   # how many elements meet this criterion
   len([e_new for e_new in elements_new if check_if_elem_contains_max5(e_new)]) # 0 confirm that all MaxSeconds have been changed to '0'
   
   # update data_new
   data_new['SurveyElements'] = elements_new
   
   

# edit_max5()


# check start position of slider questions
# find all questions with 'QuestionType': 'Slider'
# questions contain slider

# functionalize codes to find and replace maxseconds = 5 to "0"
def edit_slider():
   # find all questions with slider
   questions_slider = [q for q in questions if  q['Payload']['QuestionType'] == "Slider"]
   
   len(questions_slider)
   
   #  get the labels of these quesitons to make sure which need to be modified
   question_tags_slider = [q['Payload']['DataExportTag'] for q in questions_slider]
   
   
   print('number of slider questions: ', len(question_tags_slider)) # 52
   
   print('tags of slider questions: ', question_tags_slider)
   
   
   keys1 = ['P1_', 'P2_'] + ['V' + str(i) + '_' for i in range(1,24)]
   tag_groups = [group_tag(k, question_tags_slider) for k in keys1]
   
   # how many slider questions does each question have?
   print([(keys1[index], len(g)) for index, g in enumerate(tag_groups)])
   # 52 = each video has two slider questions: confidence and sympathy x (24 test videos + 2 practice videos)
   
   
   # check if the start position is always at the center (i.e., 5)
   def show_tag_start_position(q):
       try:
           return (q['Payload']['DataExportTag'], q['Payload']['Configuration']['SliderStartPositions'])
       except:
           print(q['Payload']['DataExportTag'], q['Payload']['Configuration'])
   
   [show_tag_start_position(q) for q in questions_slider]
   
   
   # now, programmatically change slider sliderstartposition to 0.5
   elements_new = data_new['SurveyElements']
   
   # now implement this search condition to get the indices of elements that need to be updated 
   
   
   # how many elements meet this criterion (one question already starts at 0.5)
   print('How many quesitons need modification: ', len([e_new for e_new in elements_new if check_if_elem_contains_sliderpoint5(e_new)])) # 51 confirm that this search condition works
   
   
   index_slider = get_elem_index(elements_new, check_if_elem_contains_sliderpoint5)
   
   # print('indices of slider questions: ', index_slider)
   # print(elements_new[71])
   
   for i in index_slider:
       # get the element
       thiselem = elements_new[i]
       # modify the element
       # first change MaxSeconds to '0'
       thiselem['Payload']['Configuration']['SliderStartPositions']['1'] = 0.5
       
       # update elements_new
       elements_new[i] = thiselem
       
   
   # check modification is correct
   # how many elements meet this criterion
   len([e_new for e_new in elements_new if check_if_elem_contains_sliderpoint5(e_new)]) # 0 confirm that all MaxSeconds have been changed to '0'
   
   # update data_new
   data_new['SurveyElements'] = elements_new
   
   
# edit_slider()


def edit_sliderfontsize():


    # find all questions with slider
    questions_slider = [q for q in questions if  q['Payload']['QuestionType'] == "Slider"]

    # now, programmatically change slider sliderstartposition to 0.5
    elements_new = data_new['SurveyElements']

    # now implement this search condition to get the indices of elements that need to be updated 


    # how many elements meet this criterion (one question already starts at 0.5)
    print('How many quesitons need modification: ', len([e_new for e_new in elements_new if check_if_elem_contains_slider(e_new)])) # 51 confirm that this search condition works


    index_slider = get_elem_index(elements_new, check_if_elem_contains_slider)
    index_slider


    thiselem=elements_new[74]
    # print(thiselem['Payload']['Labels']['1']['Display'])




    for i in index_slider:
        # get the element
        thiselem = elements_new[i]
        # modify the element
        # first change smaller font sizes to 20px
        thiselem['Payload']['Labels']['1']['Display'] = thiselem['Payload']['Labels']['1']['Display'].replace('16px', '20px')
        thiselem['Payload']['Labels']['2']['Display'] = thiselem['Payload']['Labels']['1']['Display'].replace('16px', '20px')
        thiselem['Payload']['Labels']['1']['Display'] = thiselem['Payload']['Labels']['1']['Display'].replace('14px', '20px')
        thiselem['Payload']['Labels']['2']['Display'] = thiselem['Payload']['Labels']['1']['Display'].replace('14px', '20px')
        # change font color
        thiselem['Payload']['Labels']['1']['Display'] = thiselem['Payload']['Labels']['1']['Display'].replace('<span style="font-size:20px;">', '<span style="font-size:20px;color:#000000;">' )
        thiselem['Payload']['Labels']['2']['Display'] = thiselem['Payload']['Labels']['2']['Display'].replace('<span style="font-size:20px;">', '<span style="font-size:20px;color:#000000;">' )
        
        # update elements_new
        elements_new[i] = thiselem

        # update data_new
        data_new['SurveyElements'] = elements_new
    
edit_sliderfontsize()



# save modified data to a json file in the directory where original json file is stored
json_dir = os.path.dirname(file)
json_name = os.path.basename(file).replace(".json", ".qsf")
print(json_dir, json_name)
file_modified = os.path.join(json_dir, "modified_"+ json_name)
with open(file_modified, 'w') as fp:
   json.dump(data_new, fp)
     
