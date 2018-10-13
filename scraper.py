from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from enum import Enum
from collections import OrderedDict

# import pdb; pdb.set_trace()

BASE_WIXOSS_URL = 'http://selector-wixoss.wikia.com/'
WIXOSS_WIKI_SUFFIX = 'wiki/'

SET_ID_KEY = 'set_id'
NUMBER_ID_KEY = 'number_id'
NAME_KEY = 'name'
RARITY_KEY = 'rarity'
COLOR_KEY = 'color'
TYPE_KEY = 'type'
LINK_SUFFIX_KEY = 'link_suffix'
ABILITIES_KEY = 'abilities'
KANJI_KEY = 'kanji'
KANA_KEY = 'kana'
ROMAJI_KEY = 'romaji'
LEVEL_KEY = 'level'
POWER_KEY = 'power'
LIMITING_CONDITION_KEY = 'limiting_condition'
COST_KEY = 'cost'
USE_TIMING_KEY = 'use_timing'
LIMIT_KEY = 'limit'
GROW_COST_KEY = 'grow_cost'
LRIG_TYPE_KEY = 'lrig_type'
COIN_KEY = 'coin'
CLASS_KEY = 'class'
KEY_SELECTION_KEY = 'is_key_selection'
GUARD_KEY = 'is_guard'


class LANG(Enum):
    EN = 'english'
    JP = '日本語'
    CN = '中文'


class WixossSet(Enum):
    WX01 = 'WX-01_Served_Selector'
    WX02 = 'WX-02_Stirred_Selector'
    WX03 = 'WX-03_Spread_Selector'
    WX04 = 'WX-04_Infected_Selector'
    WX05 = 'WX-05_Beginning_Selector'
    WX06 = 'WX-06_Fortune_Selector'
    WX07 = 'WX-07_Next_Selector'
    WX08 = 'WX-08_Incubate_Selector'
    WX09 = 'WX-09_Reacted_Selector'
    WX10 = 'WX-10_Chained_Selector'
    WX11 = 'WX-11_Destructed_Selector'
    WX12 = 'WX-12_Replied_Selector'
    WX13 = 'WX-13_Unfeigned_Selector'
    WX14 = 'WX-14_Succeed_Selector'
    WX15 = 'WX-15_Incited_Selector'
    WX16 = 'WX-16_Decided_Selector'
    WX17 = 'WX-17_Exposed_Selector'
    WX18 = 'WX-18_Conflated_Selector'
    WX19 = 'WX-19_Unsolved_Selector'
    WX20 = 'WX-20_Connected_Selector'
    WX21 = 'WX-21_Betrayed_Selector'
    WX22 = 'WX-22_Unlocked_Selector'
    WXKP01 = 'WXK-P01_Klaxon'
    WXKP02 = 'WXK-P02_Full_Scratch'
    WXKP03 = 'WXK-P03_Utopia'
    WeddingLRIG = 'Wedding_LRIG'
    WeddingLRIGCongratulations = 'Wedding_LRIG_(Congratulation_Ver.)'


class WixossType(Enum):
    NONE = ''  # To handle edge cases
    LRIG = 'LRIG'
    ARTS = 'ARTS'
    ARTSCraft = 'ARTS (Craft)'
    SIGNI = 'SIGNI'
    Spell = 'Spell'
    Key = 'Key'
    Resona = 'Resona'


# TODO: Add key selection BOOL
class WixossCard():
    def __init__(self, x_set, x_id, rarity, kanji, kana, romaji, name, color,
                 x_type, limiting_condition, link_suffix,
                 abilities={LANG.EN: None, LANG.JP: None}):
        self.x_set = x_set
        self.x_id = x_id
        self.rarity = rarity
        self.kanji = kanji
        self.kana = kana
        self.romaji = romaji
        self.name = name
        self.color = color
        self.x_type = x_type
        self.limiting_condition = limiting_condition  # Optional
        self.abilities = abilities  # {LANG Enum: [Abilities]}
        self.link_suffix = link_suffix

    def __str__(self):
        return (('Set: {}\nID: {}\nRarity: {}\nKanji: {}\nKana: {}\n'
                 'Romaji: {}\nName: {}\nColor: {}\nType: {}\n'
                 'Limiting Condition: {}\nAbilities: {}\nLink Suffix: {}\n')
                .format(self.x_set, self.x_id, self.rarity, self.kanji,
                        self.kana, self.romaji, self.name, self.color,
                        self.x_type, self.limiting_condition, self.abilities,
                        self.link_suffix))


class WixossARTSCard(WixossCard):
    def __init__(self, x_set, x_id, rarity, kanji, kana, romaji, name, color,
                 x_type, limiting_condition, abilities, link_suffix, cost,
                 use_timing):
        WixossCard.__init__(self, x_set=x_set, x_id=x_id, rarity=rarity,
                            kanji=kanji, kana=kana, romaji=romaji, name=name,
                            color=color, x_type=x_type,
                            limiting_condition=limiting_condition,
                            abilities=abilities, link_suffix=link_suffix)
        self.cost = cost
        self.use_timing = use_timing

    def __str__(self):
        parent_str = super().__str__()

        return '{}Cost: {}\nUse Timing: {}\n'.format(parent_str, self.cost,
                                                     self.use_timing)


class WixossKeyCard(WixossCard):
    def __init__(self, x_set, x_id, rarity, kanji, kana, romaji, name, color,
                 x_type, limiting_condition, abilities, link_suffix, cost):
        WixossCard.__init__(self, x_set=x_set, x_id=x_id, rarity=rarity,
                            kanji=kanji, kana=kana, romaji=romaji, name=name,
                            color=color, x_type=x_type,
                            limiting_condition=limiting_condition,
                            abilities=abilities, link_suffix=link_suffix)
        self.cost = cost

    def __str__(self):
        parent_str = super().__str__()

        return '{}Cost: {}\n'.format(parent_str, self.cost)


class WixossSpellCard(WixossCard):
    def __init__(self, x_set, x_id, rarity, kanji, kana, romaji, name, color,
                 x_type,  limiting_condition, abilities, link_suffix, cost):
        WixossCard.__init__(self, x_set=x_set, x_id=x_id, rarity=rarity,
                            kanji=kanji, kana=kana, romaji=romaji, name=name,
                            color=color, x_type=x_type,
                            limiting_condition=limiting_condition,
                            abilities=abilities, link_suffix=link_suffix)
        self.cost = cost

    def __str__(self):
        parent_str = super().__str__()

        return '{}Cost: {}\n'.format(parent_str, self.cost)


class WixossCharacterCard(WixossCard):
    def __init__(self, x_set, x_id, rarity, kanji, kana, romaji, name, color,
                 x_type, limiting_condition, abilities, link_suffix, level):
        WixossCard.__init__(self, x_set=x_set, x_id=x_id, rarity=rarity,
                            kanji=kanji, kana=kana, romaji=romaji, name=name,
                            color=color, x_type=x_type,
                            limiting_condition=limiting_condition,
                            abilities=abilities, link_suffix=link_suffix)
        self.level = level

    def __str__(self):
        parent_str = super().__str__()

        return '{}Level: {}\n'.format(parent_str, self.level)


class WixossLRIGCard(WixossCharacterCard):
    def __init__(self, x_set, x_id, rarity, kanji, kana, romaji, name, color,
                 x_type, limiting_condition, abilities, link_suffix, level,
                 limit, grow_cost, lrig_type, coin):
        WixossCharacterCard.__init__(self, x_set=x_set, x_id=x_id,
                                     rarity=rarity, kanji=kanji,
                                     kana=kana, romaji=romaji, name=name,
                                     color=color, x_type=x_type,
                                     limiting_condition=limiting_condition,
                                     abilities=abilities,
                                     link_suffix=link_suffix, level=level)
        self.limit = limit
        self.grow_cost = grow_cost  # Optional
        self.lrig_type = lrig_type
        self.coin = coin  # Optional

    def __str__(self):
        parent_str = super().__str__()

        return ('{}Limit: {}\nGrow Cost: {}\nLRIG Type: {}\nCoin: {}\n'
                .format(parent_str, self.limit, self.grow_cost, self.lrig_type,
                        self.coin))


class WixossFieldCharacterCard(WixossCharacterCard):
    def __init__(self, x_set, x_id, rarity, kanji, kana, romaji, name, color,
                 x_type, limiting_condition, abilities, link_suffix, level,
                 power, x_class):
        WixossCharacterCard.__init__(self, x_set=x_set, x_id=x_id,
                                     rarity=rarity, kanji=kanji, kana=kana,
                                     romaji=romaji, name=name, color=color,
                                     x_type=x_type,
                                     limiting_condition=limiting_condition,
                                     abilities=abilities,
                                     link_suffix=link_suffix, level=level)
        self.x_class = x_class
        self.power = power

    def __str__(self):
        parent_str = super().__str__()

        return '{}Class: {}\nPower: {}\n'.format(parent_str, self.x_class,
                                                 self.power)


class WixossSIGNICard(WixossFieldCharacterCard):
    def __init__(self, x_set, x_id, rarity, kanji, kana, romaji, name, color,
                 x_type, limiting_condition, abilities, link_suffix, level,
                 power, x_class):
        WixossFieldCharacterCard.__init__(self, x_set=x_set, x_id=x_id,
                                          rarity=rarity, kanji=kanji,
                                          kana=kana, romaji=romaji,
                                          name=name, color=color,
                                          x_type=x_type,
                                          limiting_condition=(
                                            limiting_condition),
                                          abilities=abilities,
                                          link_suffix=link_suffix, level=level,
                                          x_class=x_class, power=power)


class WixossResonaCard(WixossFieldCharacterCard):
    def __init__(self, x_set, x_id, rarity, kanji, kana, romaji, name, color,
                 x_type, limiting_condition, abilities, link_suffix, level,
                 power, x_class):
        WixossFieldCharacterCard.__init__(self, x_set=x_set, x_id=x_id,
                                          rarity=rarity, kanji=kanji,
                                          kana=kana, romaji=romaji, name=name,
                                          color=color, x_type=x_type,
                                          limiting_condition=(
                                            limiting_condition),
                                          abilities=abilities,
                                          link_suffix=link_suffix, level=level,
                                          x_class=x_class, power=power)


def generate_card(kwargs):
    card = None
    x_type = kwargs[TYPE_KEY]
    wixoss_type = None

    try:
        if x_type:
            wixoss_type = WixossType(x_type)

        if wixoss_type == WixossType.LRIG:
            card = WixossLRIGCard(x_set=kwargs[SET_ID_KEY],
                                  x_id=kwargs[NUMBER_ID_KEY],
                                  rarity=kwargs[RARITY_KEY],
                                  kanji=kwargs[KANJI_KEY],
                                  kana=kwargs[KANA_KEY],
                                  romaji=kwargs[ROMAJI_KEY],
                                  name=kwargs[NAME_KEY],
                                  color=kwargs[COLOR_KEY],
                                  x_type=kwargs[TYPE_KEY],
                                  limiting_condition=kwargs.get(
                                    LIMITING_CONDITION_KEY),
                                  abilities=kwargs[ABILITIES_KEY],
                                  link_suffix=kwargs[LINK_SUFFIX_KEY],
                                  level=kwargs[LEVEL_KEY],
                                  limit=kwargs[LIMIT_KEY],
                                  grow_cost=kwargs.get(GROW_COST_KEY),
                                  lrig_type=kwargs[LRIG_TYPE_KEY],
                                  coin=kwargs.get(COIN_KEY))
        elif wixoss_type == WixossType.SIGNI:
            card = WixossSIGNICard(x_set=kwargs[SET_ID_KEY],
                                   x_id=kwargs[NUMBER_ID_KEY],
                                   rarity=kwargs[RARITY_KEY],
                                   kanji=kwargs[KANJI_KEY],
                                   kana=kwargs[KANA_KEY],
                                   romaji=kwargs[ROMAJI_KEY],
                                   name=kwargs[NAME_KEY],
                                   color=kwargs[COLOR_KEY],
                                   x_type=kwargs[TYPE_KEY],
                                   limiting_condition=kwargs.get(
                                    LIMITING_CONDITION_KEY),
                                   abilities=kwargs[ABILITIES_KEY],
                                   link_suffix=kwargs[LINK_SUFFIX_KEY],
                                   level=kwargs[LEVEL_KEY],
                                   x_class=kwargs[CLASS_KEY],
                                   power=kwargs[POWER_KEY])
        elif wixoss_type == WixossType.Resona:
            card = WixossResonaCard(x_set=kwargs[SET_ID_KEY],
                                    x_id=kwargs[NUMBER_ID_KEY],
                                    rarity=kwargs[RARITY_KEY],
                                    kanji=kwargs[KANJI_KEY],
                                    kana=kwargs[KANA_KEY],
                                    romaji=kwargs[ROMAJI_KEY],
                                    name=kwargs[NAME_KEY],
                                    color=kwargs[COLOR_KEY],
                                    x_type=kwargs[TYPE_KEY],
                                    limiting_condition=kwargs.get(
                                        LIMITING_CONDITION_KEY),
                                    abilities=kwargs[ABILITIES_KEY],
                                    link_suffix=kwargs[LINK_SUFFIX_KEY],
                                    level=kwargs[LEVEL_KEY],
                                    x_class=kwargs[CLASS_KEY],
                                    power=kwargs[POWER_KEY])
        elif wixoss_type == WixossType.Spell:
            card = WixossSpellCard(x_set=kwargs[SET_ID_KEY],
                                   x_id=kwargs[NUMBER_ID_KEY],
                                   rarity=kwargs[RARITY_KEY],
                                   kanji=kwargs[KANJI_KEY],
                                   kana=kwargs[KANA_KEY],
                                   romaji=kwargs[ROMAJI_KEY],
                                   name=kwargs[NAME_KEY],
                                   color=kwargs[COLOR_KEY],
                                   x_type=kwargs[TYPE_KEY],
                                   limiting_condition=kwargs.get(
                                    LIMITING_CONDITION_KEY),
                                   abilities=kwargs[ABILITIES_KEY],
                                   link_suffix=kwargs[LINK_SUFFIX_KEY],
                                   cost=kwargs[COST_KEY])
        elif wixoss_type == WixossType.Key:
            card = WixossKeyCard(x_set=kwargs[SET_ID_KEY],
                                 x_id=kwargs[NUMBER_ID_KEY],
                                 rarity=kwargs[RARITY_KEY],
                                 kanji=kwargs[KANJI_KEY],
                                 kana=kwargs[KANA_KEY],
                                 romaji=kwargs[ROMAJI_KEY],
                                 name=kwargs[NAME_KEY],
                                 color=kwargs[COLOR_KEY],
                                 x_type=kwargs[TYPE_KEY],
                                 limiting_condition=kwargs.get(
                                    LIMITING_CONDITION_KEY),
                                 abilities=kwargs[ABILITIES_KEY],
                                 link_suffix=kwargs[LINK_SUFFIX_KEY],
                                 cost=kwargs[COST_KEY])
        elif wixoss_type == WixossType.ARTS:
            card = WixossARTSCard(x_set=kwargs[SET_ID_KEY],
                                  x_id=kwargs[NUMBER_ID_KEY],
                                  rarity=kwargs[RARITY_KEY],
                                  kanji=kwargs[KANJI_KEY],
                                  kana=kwargs[KANA_KEY],
                                  romaji=kwargs[ROMAJI_KEY],
                                  name=kwargs[NAME_KEY],
                                  color=kwargs[COLOR_KEY],
                                  x_type=kwargs[TYPE_KEY],
                                  limiting_condition=kwargs.get(
                                    LIMITING_CONDITION_KEY),
                                  abilities=kwargs[ABILITIES_KEY],
                                  link_suffix=kwargs[LINK_SUFFIX_KEY],
                                  cost=kwargs[COST_KEY],
                                  use_timing=kwargs[USE_TIMING_KEY])
    except:
        print(kwargs)
        print('\n\n')

    return card


def get_cards_in_set(wx_set):
    # wx_set WixossSet Enum
    get_card_list_in_set(wx_set)


def get_card_list_in_set(wx_set):
    # wx_set WixossSet Enum
    wx_set_url = BASE_WIXOSS_URL + WIXOSS_WIKI_SUFFIX + wx_set.value
    response = simple_get(wx_set_url)
    html = BeautifulSoup(response, 'html.parser')
    card_list_h2 = html.find(id='Card_List')
    card_list_table = card_list_h2.find_next('table')
    card_list_rows = card_list_table.find_all('tr')
    card_list_rows.pop(0)  # First is always just the categories

    import json

    with open(wx_set.value + '.txt', 'w') as file:
        for card_list_row in card_list_rows:
            card_summary = get_card_summary(card_list_row)
            card_details = get_card_details(card_summary.get(LINK_SUFFIX_KEY))
            merged_card_data = {**card_summary, **card_details}
            card = generate_card(merged_card_data)

            file.write(json.dumps(merged_card_data, ensure_ascii=False))
            file.write('\n\n')


def get_card_id(card_id_info_str):
    card_id_split = card_id_info_str.strip().split(' ', 1)

    if len(card_id_split) == 1:
        card_id_split = card_id_split[0].split('-', 1)

    if len(card_id_split) == 2:
        return (card_id_split[0], card_id_split[1])

    return None


def get_card_summary(card_list_row):
    # card_list_row Single row from the card_list_table
    card_summary_tds = card_list_row.find_all('td')

    card_id_info_str = card_summary_tds[0].text
    card_id_info_sanitized = get_card_id(card_id_info_str)
    if card_id_info_sanitized:
        card_set_id = card_id_info_sanitized[0]
        card_number_id = card_id_info_sanitized[1]
    else:
        print('Malformed ID/Set for: ' + card_id_info_str)

    card_name = card_summary_tds[1].find('a').text
    card_link_suffix = (card_summary_tds[1].find('a')['href']
                        .split(WIXOSS_WIKI_SUFFIX)[-1])
    card_rarity = card_summary_tds[2].text.strip()
    card_color = card_summary_tds[3].text.strip()
    card_type = card_summary_tds[4].text.strip()

    return {SET_ID_KEY: card_set_id,
            NUMBER_ID_KEY: card_number_id,
            NAME_KEY: card_name,
            RARITY_KEY: card_rarity,
            COLOR_KEY: card_color,
            TYPE_KEY: card_type,
            LINK_SUFFIX_KEY: card_link_suffix}


def get_card_details(link_suffix):
    card_url = BASE_WIXOSS_URL + WIXOSS_WIKI_SUFFIX + link_suffix
    response = simple_get(card_url)
    html = BeautifulSoup(response, 'html.parser')
    card_cftable = html.find(id='cftable')
    card_container = card_cftable.find(id='container')
    card_info_container = card_cftable.find(id='info_container')
    card_abilities_container = card_info_container.find_next(
        'div', {'class': 'info-extra'})
    card_abilities_langs = card_abilities_container.find_all('table')
    card_abilities_dict = dict()
    card_info_dict = dict()
    card_kanji = card_cftable.find(id='header').find('br').next

    if card_abilities_langs:
        for card_abilities_lang in card_abilities_langs:
            card_abilities_trs = card_abilities_lang.find_all('tr')
            card_abilities_lang_tag = card_abilities_trs[0]
            card_abilities_tag = card_abilities_trs[1].find('td')
            card_abilities_lang_enum = lang_tag_to_lang_enum(
                card_abilities_lang_tag)
            card_abilities = get_card_abilities(card_abilities_tag)

            if card_abilities:
                old_use_timings = parse_old_timing_format(card_abilities[0])
                if old_use_timings:
                    card_abilities.pop(0)

                    if not card_info_dict.get(USE_TIMING_KEY):
                        card_info_dict[USE_TIMING_KEY] = old_use_timings

            if card_abilities and card_abilities_lang_enum:
                card_abilities_dict[card_abilities_lang_enum.value] = (
                    card_abilities)

    card_main_info_container = card_info_container.find_next(
        'div', {'class': 'info-main'})
    card_main_info_rows = card_main_info_container.find_all('tr')

    for card_main_info_row in card_main_info_rows:
        row_tds = card_main_info_row.find_all('td')
        stat_name = row_tds[0].text.strip()
        stat_name_key = wikia_stat_name_to_key(stat_name)
        stat_value_tag = row_tds[1]
        stat_value = parse_wikia_stat_value(stat_name_key, stat_value_tag)

        if stat_name_key and stat_value:
            card_info_dict[stat_name_key] = stat_value
        elif not is_black_listed_key(stat_name):
                print('ERROR: ' + stat_name + ' not mapped. Value: ' +
                      stat_value)

    card_info_dict[ABILITIES_KEY] = card_abilities_dict
    card_info_dict[KANJI_KEY] = card_kanji

    return apply_hotfixes(link_suffix, card_info_dict)


def apply_hotfixes(link_suffix, card_info_dict):
    # TODO: Hotfix because this is a bug on Wikia's side
    blank_cards = ['Blank_Card_(White)', 'Blank_Card_(Black)',
                   'Blank_Card_(Red)', 'Blank_Card_(Blue)',
                   'Blank_Card_(Green)', 'Blank_Card']
    if link_suffix == '%3F':
        card_info_dict[LEVEL_KEY] = 0
        card_info_dict[LIMIT_KEY] = 0
    elif link_suffix in blank_cards:
        card_info_dict[KANA_KEY] = None
        card_info_dict[ROMAJI_KEY] = None
    elif link_suffix == 'PEEPING_DECIDE':
        card_info_dict[ROMAJI_KEY] = card_info_dict[KANA_KEY]
        card_info_dict[KANA_KEY] = None
    elif link_suffix == 'See_Through_the_Fiery_Ambition':
        card_info_dict[USE_TIMING_KEY] = ['Main Phase', 'Attack Phase']
    elif link_suffix == 'Adapting_to_Changed_Circumstances':
        card_info_dict[ROMAJI_KEY] = 'heikamon'
    elif link_suffix == 'Nameless_Fear':
        card_info_dict[ROMAJI_KEY] = 'nēmuresu fiā'
    elif link_suffix == 'Mutual_Prosperity':
        card_info_dict[USE_TIMING_KEY] = ['Attack Phase']

    return card_info_dict


def lang_tag_to_lang_enum(lang_tag):
    lang_str = lang_tag.text

    if LANG.JP.value in lang_str:
        return LANG.JP
    elif LANG.CN.value in lang_str:
        return None
    elif '(' not in lang_str:
        return LANG.EN


def is_black_listed_key(stat_name):
    keys = {'Chinese (中文)'}

    for key in keys:
        if key in stat_name:
            return True

    return False


def old_timing_indicators():
    jp_indicators = ['使用タイミング', '【', '】']
    en_indicators = ['Use Timing', '[', ']']

    return [jp_indicators, en_indicators]


def parse_old_timing_format(text):
    for lang_indicators in old_timing_indicators():
        if (lang_indicators[0] in text and lang_indicators[1] in text and
                lang_indicators[2] in text):
            timing_splits = text.split(lang_indicators[1])
            timing_splits.pop(0)

            return [use_timing.replace(lang_indicators[2], '').strip()
                    for use_timing in timing_splits]

    return None


def parse_new_timing_format(text):
    s_text = text
    new_timing_indicators = old_timing_indicators()[1]
    new_timing_indicators.pop(0)

    if new_timing_indicators[0] in text and new_timing_indicators[1] in text:
        text = (text.strip().replace(new_timing_indicators[1] + ' ' +
                new_timing_indicators[0], ',')
                .replace(new_timing_indicators[0], '')
                .replace(new_timing_indicators[1], ''))
        return text.split(',')

    return None


def parse_wikia_stat_value(stat_name_key, stat_value_tag):
    cost_keys = {GROW_COST_KEY, COST_KEY}

    if stat_name_key in cost_keys:
        cost_content = ''
        for child_tag in stat_value_tag:
            if child_tag.name == 'a':
                cost_content += child_tag['title']
            elif child_tag == ' ':
                continue
            else:
                cost_content += ' ' + child_tag.replace(' ', '') + ' '
        content = cost_content
    else:
        if stat_name_key == USE_TIMING_KEY:
            return parse_new_timing_format(stat_value_tag.text)
        elif (stat_name_key == LIMITING_CONDITION_KEY or
              stat_name_key == COLOR_KEY):
            content = stat_value_tag.text.replace('  ', ' ')
        else:
            content = stat_value_tag.text

    return content.strip()


def wikia_stat_name_to_key(stat_name):
    keys = OrderedDict([('Kana (仮名)', KANA_KEY),
                        ('Romaji (ローマ字)', ROMAJI_KEY),
                        ('Color', COLOR_KEY),
                        ('Level', LEVEL_KEY),
                        ('Power', POWER_KEY),
                        ('Class', CLASS_KEY),
                        ('Cost', COST_KEY),
                        ('LRIG Type', LRIG_TYPE_KEY),
                        ('Coin', COIN_KEY),
                        ('Use Timing', USE_TIMING_KEY),
                        ('Card Type', TYPE_KEY),
                        ('Grow Cost', GROW_COST_KEY),
                        ('Limit', LIMIT_KEY),
                        ('Limiting Condition', LIMITING_CONDITION_KEY),
                        ('Key Selection Legal?', KEY_SELECTION_KEY),
                        ('Guard', GUARD_KEY)])
    matched_key = None

    for key, value in keys.items():
        if key in stat_name:
            matched_key = value

    return matched_key


def get_card_abilities(card_abilities):
    abilities = []
    content = ''

    def prepare_for_next_content(content):
        sanitized_content = sanitize_ability_content(content.strip())

        if sanitized_content:
            abilities.append(sanitized_content)

    # Do any last minute cleaning of the text.
    # So far only used for EN.
    def sanitize_ability_content(content):
        en_content_sanitize = (content.strip().replace('  ', ' ')
                               .replace(' :', ':').replace(' ,', ',')
                               .replace('[ ', '[').replace(' ]', ']')
                               .replace(' .', '.'))
        jp_content_sanitize = (en_content_sanitize.replace(' 。', '。')
                               .replace(' ：', '：'))

        return jp_content_sanitize.strip()

    for tag in card_abilities:
        if tag.name == 'span':
            content += '[' + tag.text + '] '
        elif tag.name == 'a' and tag.find('img'):
            alt = tag.find('img')['alt']

            if tag.get('title'):
                content += '{' + alt + '} '
            else:
                content += '[' + alt + '] '
        else:
            if tag == ' ':
                continue
            elif tag.name == 'div':
                abilities[-1] = (abilities[-1] + '『' +
                                 get_card_abilities(tag)[0] + '』')
            elif not tag.name and '\n' in tag:
                prepare_for_next_content(content + tag)
                content = ''
            elif tag.name == 'p':
                prepare_for_next_content(get_card_abilities(tag)[0])
                content = ''
            elif tag.name == 'br':
                prepare_for_next_content(content)
                content = ''
            elif tag.name:
                content += tag.text + ' '
            else:
                content += tag.strip() + ' '

    if content:
        prepare_for_next_content(content)

    return abilities


def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 and
            content_type is not None and
            content_type.find('html') > -1)


def log_error(e):
    print(e)


def main():
    for wx_set in WixossSet:
        wx_set_cards = get_cards_in_set(wx_set)

if __name__ == "__main__":
    main()
