# encoding=utf8
import json
from classifier.svm import SVMLight
from classifier.person import Person
from searcher.google_item_parser import GoogleItemParser
from classifier.aff_words_extractor import AffWordsExtractor
from classifier.util import create_dir_if_not_exist

import sys
import locale
reload(sys)
sys.setdefaultencoding('utf8')


class EmailRecommender:

    def __init__(self):
        self.input_svm_dir_path = '../resource/svm/'
        self.input_aff_stopwords_file_path = '../resource/aff_stopwords.txt'
        self.input_person_list_file_path = '../resource/input_person_list.json'
        self.output_person_id_name_file_path = '../by_product/id_name.json'
        self.output_google_page_dir_path = '../by_product/google_pages/'
        self.output_google_item_dir_path = '../by_product/google_items/'
        self.output_svm_feature_dir_path = '../by_product/svm/feature/'
        self.output_svm_prediction_dir_path = '../by_product/svm/prediction/'
        self.output_result_csv_path = '../result/result.csv'
        self.output_recommend_json_file_path = '../result/recommend.json'

        create_dir_if_not_exist('../result')
        create_dir_if_not_exist('../by_product/')
        create_dir_if_not_exist('../by_product/svm')
        create_dir_if_not_exist(self.input_svm_dir_path)
        create_dir_if_not_exist(self.output_google_page_dir_path)
        create_dir_if_not_exist(self.output_google_item_dir_path)
        create_dir_if_not_exist(self.output_svm_feature_dir_path)
        create_dir_if_not_exist(self.output_svm_prediction_dir_path)

        # 获取待搜索人列表，将其中的affiliation信息作关键词提取处理
        self.person_dict_list = json.loads(open(self.input_person_list_file_path).read())
        aff_words_extractor = AffWordsExtractor(self.input_aff_stopwords_file_path, self.person_dict_list)
        self.person_dict_list = aff_words_extractor.get_person_dict_with_aff_words_list()

        # 建立待搜索人的姓名、id映射（此处id为内部顺序生成）
        from classifier.util import add_id_to_person_dict_list
        self.person_dict_list = add_id_to_person_dict_list(self.person_dict_list, self.output_person_id_name_file_path)

    def get_google_pages(self):
        from searcher.page_searcher import PageSearcher
        google_page_searcher = PageSearcher('email', self.person_dict_list, self.output_google_page_dir_path)
        google_page_searcher.start_from('')
        google_page_searcher.refresh_empty_pages()

    def get_google_items(self):
        google_item_parser = GoogleItemParser(self.person_dict_list, self.output_google_page_dir_path, self.output_google_item_dir_path)
        google_item_parser.parse_google_items_from_google_pages()

    def write_recommend_json(self):
        output_recommend_file = open(self.output_recommend_json_file_path, 'w')
        for person_dict in self.person_dict_list:
            person = Person(person_dict, self.output_google_item_dir_path)
            person.name = str(person.name).replace('\'', '')
            for ch in person.name:
                try:
                    str(ch).decode('utf-8')
                except Exception as e:
                    person.name = person.name.replace(ch, '_')
            # write feature file
            person.write_feature_file(self.output_svm_feature_dir_path)
            # classify and write prediction file
            model_filename = self.input_svm_dir_path + '249.model'
            feature_filename = self.output_svm_feature_dir_path + person.id + '.feature'
            prediction_filename = self.output_svm_prediction_dir_path + person.id + '.pred'
            svm_light = SVMLight(self.input_svm_dir_path)
            svm_light.svm_classify(feature_filename, model_filename, prediction_filename)
            # compare prediction file and email list and get recommend email list
            recommend_email_list = []
            abandoned_email_list = []
            prediction_lines = [float(prediction) for prediction in open(prediction_filename).readlines()]
            candidate_email_list = person.email_email_model_dict.keys()
            email_num = len(candidate_email_list)
            for looper in range(email_num):
                if prediction_lines[looper] > 0.0:
                    recommend_email_list.append(candidate_email_list[looper])
                else:
                    abandoned_email_list.append(candidate_email_list[looper])
            person_dict['recommend_email_list'] = recommend_email_list
            person_dict['abandoned_email_list'] = abandoned_email_list
            if 'email' not in person_dict['contact']:
                person_dict['contact']['email'] = ''
            person_dict['raw_email'] = person_dict['contact']['email']
            person_dict.pop('contact')
            person_dict.pop('affiliation_words')
        json.dump(self.person_dict_list, output_recommend_file, indent=4, ensure_ascii=False)

    def write_result_csv(self):

        def get_email_line_from_email_list(email_list):
            line = ''
            for email in email_list:
                line += email + '; '
            return line

        column_list = ['name', 'recommend_email', 'affiliation']
        recommend_dict_list = json.loads(open(self.output_recommend_json_file_path).read())
        with open(self.output_result_csv_path, 'w') as csv_file:
            for column in column_list:
                csv_file.write(column + ',')
            csv_file.write('\n')
            for recommend_dict in recommend_dict_list:
                recommend_email = get_email_line_from_email_list(recommend_dict['recommend_email_list'])
                csv_file.write(recommend_dict['name'] + ',' + recommend_email + ',' + recommend_dict['affiliation'].replace(',', ' ') + '\n')

if __name__ == '__main__':
    recommender = EmailRecommender()
    recommender.get_google_pages()
    recommender.get_google_items()
    recommender.write_recommend_json()
    recommender.write_result_csv()