from dataclasses import dataclass


@dataclass
class DataMemes:
    GROUPS = ['kakao','nestandartniememi', 'hayp_postironiya', 'gdz_7klass_perishkin']
    memes = []
    used_memes = []
    cur_meme_index = 0
    meme_to_show_index = 0


@dataclass
class Settings:
    pass