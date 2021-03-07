from itertools import groupby
import os
import vk

__all__ = ['VkGroupPostsParser']


class VkInitialize:
    def __init__(self, token):
        if token is None:
            self.__token = os.environ.get('VK_TOKEN')
        else:
            self.__token = token
        self._version_api = 5.126
        self._session = vk.Session(access_token=self.__token)
        self._api = vk.API(self._session, lang=0, v=5.126)


class VkGroupPostsParser(VkInitialize):
    def __init__(self, groups, token=None):
        super().__init__(token)
        self.groups = groups
        self.group_ids = self._get_group_ids(groups)

    def get_posts(self, **filters) -> list:
        count = filters.get('count', 10)
        atts_max = filters.get('atts_max', 1)
        data = []
        for group_id in self.group_ids:
            wall = self._api.wall.get(owner_id=f'-{group_id}')  # get the wall from group

            i = 0
            while i <= count + 1:
                i += 1

                item: dict = self._get_item(wall, i)
                if item is None:
                    # i-=1
                    continue
                else:
                    item['attachments'] = self._get_photo(item['attachments'])

                    data.append(item)
        return data

    def _get_group_ids(self, groups):
        '''
        :param groups: list of group_ids
        :return: group's id instead of group's domain
        '''
        return [self._api.utils.resolveScreenName(screen_name=domain)['object_id'] for domain in groups]

    @staticmethod
    def _get_item(wall, n):
        def _is_valid(obj):
            if 'attachments' in obj and any(
                    ['copyright' in obj, obj['marked_as_ads'] == 1, 'is_pinned' in obj,
                     'video' in obj['attachments'][0],
                     any(['audio' in i for i in obj["attachments"]], ),
                     'video' in obj]):
                return False

            return True

        item = wall['items'][n]
        if _is_valid(item):
            return item

        return None

    def _get_photo(self, attachments):
        def _group_sorted(iterable, key=None):
            """
            group the iterable object
            """
            return groupby(sorted(iterable, key=key), key=key)

        urls = []
        for a in attachments:
            # sort by size
            a = a['photo']['sizes']
            group_data = _group_sorted(a, key=lambda x: x['height'])
            urls.append([list(grp) for key, grp in group_data][-1][0]['url'])

        return urls


class AsyncVkVkGroupPostsParser(VkGroupPostsParser):
    pass


def main():
    lst = ['kakao', 'hayp_postironiya']
    # lst = ['gdz_7klass_perishkin']
    parser = VkGroupPostsParser(lst)
    posts = parser.get_posts(count=10)
    for p in posts:
        print(p)
    print(parser.groups)


if __name__ == '__main__':
    main()
