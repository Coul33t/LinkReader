import csv
import random as rn
import pdb
from constants import VIDEO_LIST

class LinkReader:
    def __init__(self):
        self.links = []

    def has_links(self):
        return len(self.links)

    def import_links(self, csv_file):
        with open(csv_file, newline='') as csvfile:
            contents = csv.reader(csvfile, delimiter=' ', quotechar='|')
            # return a list containing [link, fav or like, image or video)]
            self.links.extend([{'link': row[0].split(',')[1], 'category':row[0].split(',')[2], 'content_type':'video' if any(n in row[0].split(',')[1] for n in VIDEO_LIST) else 'image'} for row in contents])

    def get_links(self, beg=0, end=50, category=None, link_only=True):
        if not category:
            if link_only:
                return [list(link.keys())[0] for link in self.links[beg:end]]
            else:
                return self.links[beg:end]

    def get_random_link(self, number=1, category=None, link_only=True, content_type=None):
        sub_list = self.links.copy()
        if category:
            sub_list = [x['link'] for x in sub_list.items() if x['category'] == category]
        if content_type:
            sub_list = [x['link'] for x in sub_list.items() if x['content_type'] == content_type]

        rn_list = rn.sample(range(len(sub_list)), number)

        if link_only:
            return [sub_list[i]['link'] for i in rn_list]

        return [sub_list[i] for i in rn_list]

if __name__ == '__main__':
    l_r = LinkReader()
    l_r.import_links('favorites.csv')
    l_r.import_links('likes.csv')
    pdb.set_trace()