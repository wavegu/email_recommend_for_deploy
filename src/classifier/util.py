import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def create_dir_if_not_exist(dir_path):
    import os
    if not os.path.exists(dir_path):
        print 'creating path:', dir_path
        os.mkdir(dir_path)


def del_a_from_b(a, b):
    if a not in b:
        return b
    part_pos = b.find(a)
    if part_pos + len(a) >= len(b):
        b = b[:part_pos]
    else:
        b = b[:part_pos] + b[(part_pos+len(a)):]
    return b


def is_a_in_b(a, b):
    a = str(a)
    b = str(b)
    if a not in b:
        return False
    start_pattern = a + ' '
    end_pattern = ' ' + a
    if (' ' + a + ' ') in b:
        return True
    if start_pattern in b and b.find(start_pattern) == 0:
        return True
    if end_pattern in b and b.find(end_pattern) == (len(b) - len(end_pattern)):
        return True
    return False


def add_id_to_person_dict_list(person_dict_list, id_name_filename):
    import codecs
    id_name_dict = {}

    person_id = -1
    for person_dict in person_dict_list:
        name = person_dict['name']
        person_id += 1
        id_name_dict[str(person_id)] = name
        person_dict['id'] = str(person_id)

    with codecs.open(id_name_filename, "w", encoding="utf-8") as f_out:
        json.dump(id_name_dict, f_out, indent=4, ensure_ascii=False)

    return person_dict_list


# get_known_top_1000()

if __name__ == '__main__':
    print add_id_to_person_dict_list('../../resource/input_person_list.json', '../../by_product/id_name.json')