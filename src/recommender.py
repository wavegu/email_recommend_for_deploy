import json
from searcher.page_searcher import PageSearcher
from searcher.google_item_parser import GoogleItemParser
from classifier.person import Person
from classifier.aff_words_extractor import AffWordsExtractor


class EmailRecommender:

    def __init__(self):
        self.input_aff_stopwords_file_path = '../resource/aff_stopwords.txt'
        self.input_person_list_file_path = '../resource/input_person_list.json'
        self.output_google_page_dir_path = '../by_product/google_pages/'
        self.output_google_item_dir_path = '../by_product/google_items/'
        self.output_feature_dir_path = '../by_product/feature/'

        self.person_dict_list = json.loads(open(self.input_person_list_file_path).read())
        aff_words_extractor = AffWordsExtractor(self.input_aff_stopwords_file_path, self.person_dict_list)
        self.person_dict_list = aff_words_extractor.get_person_dict_with_aff_words_list()

    def get_google_pages(self):
        google_page_searcher = PageSearcher('email', self.person_dict_list, self.output_google_page_dir_path)
        google_page_searcher.start_from('')
        google_page_searcher.refresh_empty_pages()

    def get_google_items(self):
        google_item_parser = GoogleItemParser(self.output_google_page_dir_path, self.output_google_item_dir_path)
        google_item_parser.parse_google_items_from_google_pages()

    def write_feature_file(self):
        for person_dict in self.person_dict_list:
            person_name = person_dict['name']
            feature_file_path = self.output_feature_dir_path + person_name + '.txt'
            with open(feature_file_path, 'w') as feature_file:
                print 'writing feature:', person_dict['name']
                person = Person(person_dict, self.output_google_item_dir_path)
                if not person.google_item_dict_list:
                    continue
                for email_addr, email_model in person.email_email_model_dict.items():
                    feature_file.write(email_model.get_feature_line() + '\n')


if __name__ == '__main__':
    recommender = EmailRecommender()
    recommender.get_google_pages()
    recommender.get_google_items()
    recommender.write_feature_file()