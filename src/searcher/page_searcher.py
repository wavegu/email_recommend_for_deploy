# encoding: utf-8

import os
import random
import time
import json
import sys

from search_helper.search_helper import GoogleHelper

reload(sys)
sys.setdefaultencoding('utf8')


class PageSearcher:

    def __init__(self, keyword_list, person_dict_list, result_path):
        self.names = []
        self.ok_name_list = []
        self.error_name_list = []
        self.keyword_list = keyword_list
        self.result_path = result_path
        self.person_dict_list = person_dict_list

    def get_page_file_path(self, person_id, keyword):
        return self.result_path + person_id + '/' + keyword.replace(' ', '_') + '.html'

    def get_google_page_from(self, person_dict, keyword, search_helper):
        person_id = person_dict['id']
        name = person_dict['name'].replace('\n', '')
        # print '******', name, '*******'
        personal_path = self.result_path + person_id + '/'
        # 建立搜索引擎文件夹
        if not os.path.exists(self.result_path):
            os.mkdir(self.result_path)
        # 建立每个人的文件夹
        if not os.path.exists(personal_path):
            os.mkdir(personal_path)
        # 打开文件
        search_page_cache_file = open(self.get_page_file_path(person_id, keyword), 'w')
        try:
            # 获取搜索主页，并保存在个人文件夹下
            search_page_content = search_helper.get_search_page_by_name(name + ' ' + keyword)
            if search_page_content is None:
                self.error_name_list.append(name)
                print '[Error]@EmailSearcher.get_google_page_from(): search_page_content is None'
                with open('missing_name.txt', 'w') as missing_name_file:
                    for missing_name in self.error_name_list:
                        missing_name_file.write(str(missing_name) + '\n')
                return False
            search_page_cache_file.write(search_page_content)
            search_page_cache_file.close()
            self.ok_name_list.append(name)
            print name, 'OK...'
            with open('ok_name.txt', 'a') as ok_name_file:
                ok_name_file.write(str(name) + '\n')
            time.sleep(random.randint(1, 3))

        except Exception as e:
            print e
            self.error_name_list.append(name)
            with open(self.result_path + 'missing_name.txt', 'w') as missing_name_file:
                for missing_name in self.error_name_list:
                    missing_name_file.write(str(missing_name) + '\n')
            return False
        return True

    def start_from(self, start_id):
        flag = False
        # person_name_list = [person_dict['name'] for person_dict in self.person_dict_list]
        try:
            for person_dict in self.person_dict_list:
                person_id = str(person_dict['id'])
                print 'Getting google page', person_id
                if person_id in os.listdir(self.result_path):
                    continue
                if person_id == start_id or start_id == '':
                    flag = True
                    if start_id:
                        print 'starting from', person_dict['name']
                if not flag:
                    continue
                for keyword in self.keyword_list:
                    self.get_google_page_from(person_dict, keyword, GoogleHelper())
        except Exception as e:
            print e

    def refresh_empty_pages(self):
        for person_dict in self.person_dict_list:
            try:
                for keyword in self.keyword_list:
                    with open(self.get_page_file_path(person_dict['id'], keyword)) as search_page:
                        if len(search_page.read()) < 10:
                            self.get_google_page_from(person_dict, keyword, GoogleHelper())
            except Exception as e:
                print e


if __name__ == '__main__':
    searcher = PageSearcher('email')
    searcher.start_from('')
    searcher.refresh_empty_pages()
