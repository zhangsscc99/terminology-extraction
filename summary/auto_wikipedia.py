#this code was written by Anand Tyagi, for questions: anand.tyagi@nyu.edu
import wikipedia
import sys
import urllib.request
from bs4 import BeautifulSoup
import json
import os
import shutil
import sinopy

def get_topic(): #gets the general topic the user wants to explore
    possible_topics = wikipedia.search(input('please enter a topic:\n'))
    #make sure a topic was entered
    for i, x in enumerate(possible_topics):
        print(i+1, ": ", x)
    topic_num = input("Please specify which topic you mean:\n")
    #check that topic num is a valid int
    topic_num = int(topic_num)
    return possible_topics[topic_num-1]

def get_subclass(topic, lang_acronym):  # Gets a valid subclass
    topic_url_fmt = topic.replace(" ", "_")
    url = "https://{}.wikipedia.org/wiki/{}".format(
        lang_acronym,
        urllib.parse.quote(topic_url_fmt))
    page = urllib.request.urlopen(url)

    soup = BeautifulSoup(page, "html")
    ## soup = BeautifulSoup(page, "html5lib")

    cat_section = soup.find(id='mw-normal-catlinks')
    categories = []

    for cat in cat_section.findAll('a')[1:]:
        categories.append(cat.text)

    # Choose a category for subclass.
    subclass = None

    # If a category with the same name as topic exists, pick that.
    same_category_exist = False

    if lang_acronym == 'zh':  # If the language is Chinese.
        # Translate the words into pinyin to check if there are categories with
        # the same name as the topic. This is done because of the existence of
        # both Traditional and Simplified version of Chinese.
        topic_pinyin = sinopy.pinyin(topic)
        categories_pinyin = [sinopy.pinyin(category) for category in categories]
        for idx in range(len(categories_pinyin)):
            if topic_pinyin == categories_pinyin[idx]:
                subclass = categories[idx]
                same_category_exist = True
                break
    else:  # If the language is French or English.
        if topic in categories:
            subclass = topic
            same_category_exist = True

    # If there are no categories with the same name as the topic, let the user
    # choose a category.
    if not same_category_exist:
        for i, x in enumerate(categories):
            print(i + 1, ": ", x)
        category_idx = input("Please specify which category you mean:\n")
        #check that topic num is a valid int
        category_idx = int(category_idx) - 1
        subclass = categories[category_idx]

    return subclass

def get_superclass(subclass, lang_acronym): #gets a valid superclass

    subclass = subclass.replace(" ", "_")
    url = "https://{}.wikipedia.org/wiki/Category:{}".format(
        lang_acronym,
        urllib.parse.quote(subclass))
    print(url)
    page = urllib.request.urlopen(url)

    soup = BeautifulSoup(page, "html")
    ## soup = BeautifulSoup(page, "html5lib")

    cat_section = soup.find(id='mw-normal-catlinks')
    categories = []

    for cat in cat_section.findAll('a')[1:]:
        categories.append(cat.text)

    for i, x in enumerate(categories):
        print(i+1, ": ", x)
    print(len(categories) + 1, ":  All")

    chosen = input("Please choose all the relavent subclasses (list each number separated by a comma (Ex. 1,3,4)):\n")

    if len(chosen) == 1:
        chosen_index = int(chosen)-1
        if chosen_index == len(categories):
            return categories
        else:
            return [categories[chosen_index]]

    selection = chosen.split(",")
    superclasses = []
    for x in selection:
        superclasses.append(categories[int(x)-1])

    return superclasses

def get_language(): #can pick from any of the three termolator languages
    languages = ['English', 'Chinese', 'French']
    for i, cat in enumerate(languages):
        print(i+1, ': ', cat)

    lang_index = input('Please enter your language option (enter the number):\n')
    lang_index = int(lang_index)-1
    return languages[lang_index]

def get_num_articles(): #number of articles
    return input('Please enter the number of articles you would like to search:\n')
'''
not needed as it is assumed this will be run in the correct location.
# def get_intermediate_file_path():
#     return input('Please enter the path respective to summary_from_2_terms.sh where you would like the intermeidate files to be made:\n')
#
# def get_termolator_dir():
#     return input('Please enter the location of the termolator with respect to the location of summary_from_2_terms.sh:\n')
'''

def get_file_type(): #file type
    file_type = input("Please enter the type of file the summary should be written to (Ex. .txt, .xml, etc):\n")
    if file_type[0] != '.': #incase they don't add the dot
        file_type = '.' + file_type
    return file_type

def no_input_files(file_list):
    import re
    import os
    file_found = False
    if os.path.isfile(file_list):
        with open(file_list) as instream:
            for line in instream:
                if re.search('[a-zA-Z]',line):
                    file_found = True
    if file_found:
        return(False)
    else:
        return(True)

def create_sym_links_for_file_list(file_list,directory):
    ## intermediate_file_path
    import os
    with open(file_list) as instream:
        for line in instream:
            ## infilename = intermediate_file_path+os.sep+line.strip(os.linesep)
            infilename = '..'+os.sep+line.strip(os.linesep)
            ## file_path = infilename.split(os.sep)
            path_list = infilename.split(os.sep)
            outfilename = (directory + os.sep + path_list[-1])
            os.symlink(infilename,outfilename)

def make_fore_back_dir (fore_file_list,back_file_list,fore_dir,back_dir):
    import os
    if not os.path.isdir(fore_dir):
        os.mkdir(fore_dir)
    if not os.path.isdir(back_dir):
        os.mkdir(back_dir)
    create_sym_links_for_file_list(fore_file_list,fore_dir)
    create_sym_links_for_file_list(back_file_list,back_dir)
        

def run_wiki_scripts(): #runs the bash script for generating the summary.

    print(
        'Glossary Creation System:\n'
        'Please follow the prompts to create a glossary.')

    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            language = 'English'
            num_articles = '250'
            total_num_articles = 500
            file_type = '.txt'
            subclass = 'COVID-19'
            superclasses = ['Viral_respiratory_tract_infections', 'Zoonotic_bacterial_diseases']
            print(
                'The test values are:\n'
                'Foreground: COVID-19\n'
                'Background: Viral_respiratory_tract_infections, Zoonotic_bacterial_diseases\n'
                'Language: English\n'
                'Number of aricles per background: 250\n'
                'Intermediate file path: .\n'
                'Termolator directory: ..\n'
                'File type: .txt')
    else:
        redo = True
        while redo:
            language = get_language()
            lang_acronym = {'English': 'en', 'Chinese': 'zh', 'French': 'fr'}[language]
            wikipedia.set_lang(lang_acronym)
            print('Choose a foreground.')
            topic = get_topic()
            subclass = get_subclass(topic, lang_acronym)
            print('Choose a background.')
            superclasses = get_superclass(subclass, lang_acronym)
            print('Foreground: ', subclass)
            print('Background: ', superclasses)

            correct = input('Does this look good? (Y,n)\n')
            if correct.lower() == 'y':
                redo = False;
            else:
                redo = True

        total_num_articles = int(get_num_articles())
        num_articles = str(int(total_num_articles / len(superclasses))) #equal divide between superclasses
        file_type = get_file_type()


    for i in range(len(superclasses)):
        superclasses[i] = superclasses[i].replace(" ", "_")
        superclasses[i] = superclasses[i].replace("(", "_")
        superclasses[i] = superclasses[i].replace(")", "_")
    subclass = subclass.replace(" ", "_")
    subclass = subclass.replace("(", "\(")
    subclass = subclass.replace(")", "\)")

    intermediate_file_path = '.'
    termolator_dir = '..'

    # Get foreground articles using get_wiki_corpus_main.sh

    os.system('bash '+ termolator_dir + '/wikipedia_file_extraction/get_wiki_corpus_main.sh '+ language +' '+ subclass +' '+ intermediate_file_path +'/'+ subclass +' True  '+ num_articles +' '+ termolator_dir +'/wikipedia_file_extraction')

    print('##### Executed command: {}'.format('bash '+ termolator_dir + '/wikipedia_file_extraction/get_wiki_corpus_main.sh '+ language +' '+ subclass +' '+ intermediate_file_path +'/'+ subclass +' True  '+ num_articles +' '+ termolator_dir +'/wikipedia_file_extraction'))

    print('##### get_wiki_corpus_main.sh execution finished #####')

    foreground_file_list = intermediate_file_path +'/'+ subclass +'.file_list'

    print('#### {}'.format(foreground_file_list))

    os.system('ls -1 '+ intermediate_file_path +'/'+ subclass +'/*'+ file_type +' > '+ foreground_file_list)
    os.system('touch '+ intermediate_file_path + '/'+ subclass + '_all_background_files.file_list')
    os.system('python3 '+ termolator_dir + '/mod_make_glossary_part1.py '+  foreground_file_list+' '+ subclass +' .txt '+ termolator_dir)
    if no_input_files(foreground_file_list):
        print(foreground_file_list)
        print('Search ended because there are not enough foreground files. Try again with another query.')
        return(False)

    print('touch '+ intermediate_file_path + '/'+ subclass + '_all_background_files.file_list')
    print('python3 '+ termolator_dir + '/mod_make_glossary_part1.py '+  foreground_file_list+' '+ subclass +' .txt '+ termolator_dir)
    print('#####')

    # Get background articles using get_wiki_corpus_main.sh

    for i, super in enumerate(superclasses): #for each of the superclasses.

        os.system('bash '+ termolator_dir + '/wikipedia_file_extraction/get_wiki_corpus_main.sh '+ language +' '+ super +' '+ intermediate_file_path +'/'+ super +' True  '+ num_articles +' '+ termolator_dir +'/wikipedia_file_extraction')

        print('##########' + 'bash '+ termolator_dir + '/wikipedia_file_extraction/get_wiki_corpus_main.sh '+ language +' '+ super +' '+ intermediate_file_path +'/'+ super +' True  '+ num_articles +' '+ termolator_dir +'/wikipedia_file_extraction')

        os.system('ls -1 '+ intermediate_file_path +'/'+super+'/*'+ file_type +' > '+ intermediate_file_path +'/'+ super +'.file_list')
        os.system('python3 '+ termolator_dir + '/mod_make_glossary_part1.py '+  intermediate_file_path +'/'+ super +'.file_list  '+ super +' .txt '+ termolator_dir)

        if(int(os.system('wc -l < ' + intermediate_file_path + '/'+  super + '.file_list_2')) < int(num_articles)):
            total_num_articles -= int(os.system('wc -l < ' + intermediate_file_path + '/'+  super + '.file_list_2'))
            num_articles = str(int(int(total_num_articles) / (len(superclasses) - i + 1))) #redistribute num of articles per rest of superclasses
            print(super + ' did not have enough articles. Additional articles were taken from other background topics')
        else:
            total_num_articles -= int(num_articles)
        os.system('cat '+ intermediate_file_path + '/'+  super + '.file_list_2 >> '+ intermediate_file_path + '/'+ subclass + '_all_background_files.file_list')

    # Run termolator model

    ## print('#########' + termolator_dir +'/run_termolator.sh '+ intermediate_file_path +'/'+ subclass +'.file_list_2 '+ intermediate_file_path + '/'+ subclass + '_all_background_files.file_list' +' .txt '+ subclass +' True True 30000 5000 '+ termolator_dir +' False False False wikipedia-'+subclass+'_background.pkl -1')

    # print('##########' + termolator_dir +'/run_term_map.sh '+ intermediate_file_path +'/'+ subclass +'.file_list_2 '+ intermediate_file_path +'/'+ subclass +'.out_term_list '+ subclass +' '+ intermediate_file_path +' '+ termolator_dir)

    # print('##########' + termolator_dir +'/run_summary.sh '+ subclass +' '+ intermediate_file_path +' '+ termolator_dir +' .txt3')

    if lang_acronym == 'en':
        os.system(termolator_dir +'/run_termolator.sh '+ intermediate_file_path +'/'+ subclass +'.file_list_2 '+ intermediate_file_path + '/'+ subclass + '_all_background_files.file_list' +' .txt '+ subclass +' True True 30000 5000 '+ termolator_dir +' False False False wikipedia-'+subclass+'_background.pkl -1')
    elif lang_acronym == 'zh':
        foreground_filelist_file = intermediate_file_path + '/' + subclass + '.file_list_2'
        background_filelist_file = intermediate_file_path + '/' + subclass + '_all_background_files.file_list'
        # Move all the files in the foreground list to a new directory.
        # Create the directory under where the files are stored.
        foreground_dir = None
        with open(foreground_filelist_file, 'r') as fin:
            for file in fin.readlines():
                file = file.strip()
                file_dir = os.path.dirname(file)
                filename = os.path.split(file)[-1]
                newdir = os.path.join(file_dir, 'name_normalized')
                foreground_dir = newdir
                if not os.path.exists(newdir):
                    os.mkdir(newdir)
                shutil.copy(file, os.path.join(newdir, filename), follow_symlinks=True)
        # Move all the files in the background list to a new directory.
        # Create the directory under where the files are stored.
        background_dir = None
        with open(background_filelist_file, 'r') as fin:
            for file in fin.readlines():
                file = file.strip()
                file_dir = os.path.dirname(file)
                filename = os.path.split(file)[-1]
                newdir = os.path.join(file_dir, 'name_normalized')
                background_dir = newdir
                if not os.path.exists(newdir):
                    os.mkdir(newdir)
                shutil.copy(file, os.path.join(newdir, filename), follow_symlinks=True)

        print(' '.join([
            'bash',
            termolator_dir + '/' + 'run_Termolator_chinese.sh',
            'True',
            subclass,
            foreground_dir,
            background_dir,
            termolator_dir,
            'True']))
        os.system(' '.join([
            'bash',
            termolator_dir + '/' + 'run_Termolator_chinese.sh',
            'True',
            subclass,
            foreground_dir,
            background_dir,
            termolator_dir,
            'True']))
    elif lang_acronym == 'fr':  ## 9/18/22 AM
        # fore_dir =  intermediate_file_path+ os.sep+subclass + "_fore_dir"
        # back_dir = intermediate_file_path+ os.sep+subclass + "_back_dir"
        # fore_file_list =intermediate_file_path +os.sep+ subclass +'.file_list_2'
        # back_file_list  = intermediate_file_path + os.sep+ subclass + '_all_background_files.file_list'
        # make_fore_back_dir(fore_file_list,back_file_list,fore_dir,back_dir)
        # os.system(termolator_dir +'/run_termolator_fr.sh '+ fore_dir + ' ' +back_dir+ ' '+ subclass +' True True True 30000 5000 '+ termolator_dir + ' '+'TreeTaggerLinux -1')
        pass
    else:
        raise Exception('Language not implemented: {}'.format(
            lang_acronym))

    # os.system(termolator_dir +'/run_term_map.sh '+ intermediate_file_path +'/'+ subclass +'.file_list_2 '+ intermediate_file_path +'/'+ subclass +'.out_term_list '+ subclass +' '+ intermediate_file_path +' '+ termolator_dir)
    # #
    # os.system(termolator_dir +'/run_wiki_scripts.sh '+ subclass +' '+ intermediate_file_path +' '+ termolator_dir +' .txt3')

    return



if __name__ == '__main__':
    run_wiki_scripts()