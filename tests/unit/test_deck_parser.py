#!/usr/bin/env python3
"""
套牌解析器单元测试

测试平铺、MTGA、Moxfield 三种格式的解析逻辑。
"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'functions', 'mtgAsk', 'backend'))

import pytest


# ==================== 解析器实现（Python 版，与 decks.js 逻辑一致） ====================

cn_to_en_map = {
    '珍宝': 'Treasure', '闪电击': 'Lightning Bolt', '黑莲花': 'Black Lotus',
    '山脉': 'Mountain', '海岛': 'Island', '平原': 'Plains', '森林': 'Forest', '沼泽': 'Swamp',
    '士兵': 'Soldier', '天使': 'Angel', '精灵': 'Elf', '野狼': 'Wolf', '猫': 'Cat',
    '龙': 'Dragon', '鬼怪': 'Goblin', '吸血鬼': 'Vampire', '灵俑': 'Zombie'
}

def translate_to_en(cn):
    return cn_to_en_map.get(cn, cn)


def parse_moxfield_line(line):
    match = re.match(r'^(\d+)\s+(.+?)\s+\(([^)]+)\)\s+(\d+|\S+)', line.strip())
    if not match:
        return None
    return {
        'count': int(match.group(1)),
        'name': match.group(2).strip(),
        'set': match.group(3).strip()
    }


def parse_deck_text(text, card_format='自动识别'):
    lines = text.strip().split('\n')
    cards = []
    errors = []
    commander = None

    is_moxfield = False
    is_mtga = False

    if card_format == 'Moxfield':
        is_moxfield = True
    elif card_format == 'MTGA':
        is_mtga = True
    elif card_format == '自动识别':
        moxfield_count = sum(1 for l in lines if parse_moxfield_line(l))
        is_moxfield = moxfield_count >= sum(1 for l in lines if l.strip()) * 0.5
        commander_idx = next((i for i, l in enumerate(lines) if l.strip() == 'Commander:'), -1)
        is_mtga = commander_idx != -1

    in_commander = False

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        if line == 'About' or line.startswith('Name '):
            continue
        if line == 'Deck':
            in_commander = False
            continue
        if line == 'Commander:':
            in_commander = True
            continue

        if is_moxfield:
            parsed = parse_moxfield_line(line)
            if parsed:
                name = translate_to_en(parsed['name'])
                if parsed['count'] > 0:
                    cards.append({'name': name, 'count': parsed['count'], 'set': parsed['set']})
                continue
            errors.append(f'第{i + 1}行无法识别: {line}')
            continue

        if is_mtga and in_commander:
            match = re.match(r'^(\d+)x?\s+(.+)$', line)
            if match:
                commander = translate_to_en(match.group(2).strip())
            continue

        match = re.match(r'^(\d+)x?\s+(.+)$', line)
        if match:
            count = int(match.group(1))
            name = translate_to_en(match.group(2).strip())
            if count > 0:
                cards.append({'name': name, 'count': count})
            continue

        if line:
            errors.append(f'第{i + 1}行无法识别: {line}')

    return {'cards': cards, 'errors': errors, 'commander': commander}


def calc_total_cards(cards):
    return sum(c['count'] for c in cards)


# ==================== Fixtures ====================

@pytest.fixture
def plain_deck_text():
    return """4 Lightning Bolt
4 Counterspell
4 Force of Will
20 Mountain
20 Island"""

@pytest.fixture
def mtga_deck_text():
    return """About
Name Sisay

Deck
1 Birds of Paradise
1 Birds of Paradise
1 Birds of Paradise
1 Birds of Paradise
1 Noble Hierarch
1 Noble Hierarch
1 Noble Hierarch
1 Noble Hierarch
1 Force of Will

Commander:
1 Sisay, Weatherlight Captain"""

@pytest.fixture
def moxfield_deck_text():
    return """1 Sisay, Weatherlight Captain (MH1) 29
1 Abrupt Decay (MB2) 78
1 Agatha's Soul Cauldron (WOE) 242
1 Ancient Tomb (EOS) 1
1 Arcane Signet (C20) 237
1 Arid Mesa (MH2) 475"""


# ==================== 测试类 ====================

class TestPlainFormat:
    """平铺格式测试"""

    def test_basic_parsing(self, plain_deck_text):
        result = parse_deck_text(plain_deck_text)
        assert result['commander'] is None
        assert len(result['errors']) == 0
        assert len(result['cards']) == 5

    def test_count(self, plain_deck_text):
        result = parse_deck_text(plain_deck_text)
        counts = {c['name']: c['count'] for c in result['cards']}
        assert counts['Lightning Bolt'] == 4
        assert counts['Counterspell'] == 4
        assert counts['Force of Will'] == 4
        assert counts['Mountain'] == 20
        assert counts['Island'] == 20

    def test_total_cards(self, plain_deck_text):
        result = parse_deck_text(plain_deck_text)
        assert calc_total_cards(result['cards']) == 52

    def test_chinese_translation(self):
        text = "4 黑莲花\n4 闪电击"
        result = parse_deck_text(text)
        names = [c['name'] for c in result['cards']]
        assert 'Black Lotus' in names
        assert 'Lightning Bolt' in names

    def test_unknown_line_creates_error(self):
        text = "This is not a card line"
        result = parse_deck_text(text)
        assert len(result['errors']) == 1
        assert '无法识别' in result['errors'][0]

    def test_empty_lines_ignored(self):
        text = "4 Lightning Bolt\n\n4 Counterspell\n\n"
        result = parse_deck_text(text)
        assert len(result['cards']) == 2


class TestMTGAFormat:
    """MTGA 格式测试"""

    def test_commander_detected(self, mtga_deck_text):
        result = parse_deck_text(mtga_deck_text)
        assert result['commander'] == 'Sisay, Weatherlight Captain'

    def test_deck_cards_parsed(self, mtga_deck_text):
        result = parse_deck_text(mtga_deck_text)
        names = [c['name'] for c in result['cards']]
        assert 'Birds of Paradise' in names
        assert 'Force of Will' in names

    def test_commander_not_in_deck(self, mtga_deck_text):
        result = parse_deck_text(mtga_deck_text)
        names = [c['name'] for c in result['cards']]
        assert 'Sisay, Weatherlight Captain' not in names

    def test_4x_format(self):
        text = "Deck\n4x Lightning Bolt\n4x Counterspell"
        result = parse_deck_text(text)
        counts = {c['name']: c['count'] for c in result['cards']}
        assert counts['Lightning Bolt'] == 4
        assert counts['Counterspell'] == 4

    def test_about_and_name_ignored(self):
        text = "About\nName TestDeck\nDeck\n1 Lightning Bolt"
        result = parse_deck_text(text)
        assert len(result['errors']) == 0
        assert len(result['cards']) == 1

    def test_without_commander(self):
        text = "Deck\n1 Lightning Bolt"
        result = parse_deck_text(text)
        assert result['commander'] is None
        assert len(result['cards']) == 1


class TestMoxfieldFormat:
    """Moxfield 格式测试"""

    def test_parsed(self, moxfield_deck_text):
        result = parse_deck_text(moxfield_deck_text)
        assert len(result['cards']) == 6
        assert len(result['errors']) == 0

    def test_set_info_preserved(self, moxfield_deck_text):
        result = parse_deck_text(moxfield_deck_text)
        card = next(c for c in result['cards'] if c['name'] == 'Sisay, Weatherlight Captain')
        assert card['set'] == 'MH1'
        assert card['count'] == 1

    def test_multicount(self):
        text = "4 Lightning Bolt (M10) 123\n2 Mountain (M10) 124"
        result = parse_deck_text(text)
        counts = {c['name']: c['count'] for c in result['cards']}
        assert counts['Lightning Bolt'] == 4
        assert counts['Mountain'] == 2

    def test_commander_not_detected_in_moxfield(self):
        """Moxfield 格式中有 Commander: 行时，应识别为 Moxfield 并报错"""
        text = """1 Lightning Bolt (M10) 1
1 Mountain (M10) 2
Commander:
1 Sisay, Weatherlight Captain"""
        # 3行Moxfield / 4行总数 = 75% > 50%，判定为 Moxfield 格式
        result = parse_deck_text(text)
        # Commander: 行不匹配 Moxfield，被记为错误
        assert len(result['errors']) == 1
        # Moxfield 行被正确解析
        assert len(result['cards']) == 2


class TestMixedAndEdgeCases:
    """混合和边界情况"""

    def test_real_sisay_deck(self):
        """来自 tests/sample/deck/format_mtga 的真实数据（无 Commander: 区）"""
        with open('tests/sample/deck/format_mtga') as f:
            text = f.read()
        result = parse_deck_text(text)
        # 该文件是 MTGA 格式但无 Commander: 区，Name Sisay 只是套牌名
        assert result['commander'] is None
        assert len(result['cards']) > 0
        assert 'Nicol Bolas, Dragon-God' in [c['name'] for c in result['cards']]

    def test_real_moxfield_deck(self):
        """来自 tests/sample/deck/format_moxfield 的真实数据"""
        with open('tests/sample/deck/format_moxfield') as f:
            text = f.read()
        result = parse_deck_text(text)
        assert len(result['cards']) == 100
        assert calc_total_cards(result['cards']) == 100
        assert len(result['errors']) == 0

    def test_zero_count_ignored(self):
        text = "0 Lightning Bolt\n4 Mountain"
        result = parse_deck_text(text)
        names = [c['name'] for c in result['cards']]
        assert 'Lightning Bolt' not in names
        assert 'Mountain' in names

    def test_card_with_parenthesis_in_name(self):
        text = "1 Food // Corpse (Y22) 123"
        result = parse_deck_text(text)
        # Moxfield 解析：count=1, name="Food // Corpse", set="Y22"
        assert len(result['cards']) == 1
        assert result['cards'][0]['name'] == 'Food // Corpse'
        assert result['cards'][0]['set'] == 'Y22'


class TestHypergeometricDistribution:
    """超几何分布概率计算测试"""

    @pytest.fixture
    def hypergeo_code(self):
        # Python 实现（与 odds.js 逻辑一致）
        import math
        def combinations(n, r):
            if r > n:
                return 0
            if r == 0 or r == n:
                return 1
            c = 1
            for i in range(r):
                c = c * (n - i) / (i + 1)
            return c

        def hypergeometric(N, K, n, k):
            if k < 0 or k > min(K, n):
                return 0
            if k > n or k > K:
                return 0
            return (combinations(K, k) * combinations(N - K, n - k)) / combinations(N, n)

        def calc_odds(N, K, n, target):
            total = 0
            for k in range(target, min(K, n) + 1):
                total += hypergeometric(N, K, n, k)
            return total
        return hypergeometric, calc_odds

    def test_combinations(self, hypergeo_code):
        hypergeometric, _ = hypergeo_code
        # C(60, 7) = 386206920
        from fractions import Fraction
        # 简化分数比较
        result = hypergeometric(60, 4, 7, 0)
        assert 0 < result < 1

    def test_4_copies_in_60_deck_opening_7(self, hypergeo_code):
        hypergeometric, _ = hypergeo_code
        # 4 张目标牌，套牌 60 张，起手 7 张
        p0 = hypergeometric(60, 4, 7, 0)  # 0 张的概率
        p1 = hypergeometric(60, 4, 7, 1)  # 1 张的概率
        # 总概率应为 1
        total = sum(hypergeometric(60, 4, 7, k) for k in range(5))
        assert abs(total - 1) < 1e-10

    def test_4_copies_probability_values(self, hypergeo_code):
        hypergeometric, calc_odds = hypergeo_code
        p0 = hypergeometric(60, 4, 7, 0)
        p1 = hypergeometric(60, 4, 7, 1)
        p2 = hypergeometric(60, 4, 7, 2)
        p3 = hypergeometric(60, 4, 7, 3)
        p4 = hypergeometric(60, 4, 7, 4)
        # 验证：0 张概率最高，4 张概率最低
        assert p0 > p1 > p2 > p3 > p4
        # 至少 1 张的概率
        at_least_1 = calc_odds(60, 4, 7, 1)
        assert 0 < at_least_1 < 1
        assert abs(p1 + p2 + p3 + p4 - at_least_1) < 1e-10

    def test_commander_99_deck(self, hypergeo_code):
        hypergeometric, calc_odds = hypergeo_code
        # 1 张指挥官，99 张套牌，起手 7 张
        p1 = hypergeometric(99, 1, 7, 1)
        at_least_1 = calc_odds(99, 1, 7, 1)
        assert abs(p1 - at_least_1) < 1e-10
        # 大约 7.07% 的概率
        assert 0.07 < p1 < 0.08

    def test_zero_target(self, hypergeo_code):
        hypergeometric, calc_odds = hypergeo_code
        p0 = hypergeometric(60, 4, 7, 0)
        assert 0 < p0 < 1
        at_least_0 = calc_odds(60, 4, 7, 0)
        assert abs(at_least_0 - 1) < 1e-10


class TestManualFormatSelection:
    """手动选择卡牌格式测试"""

    def test_force_plain_with_mtga_content(self):
        """强制平铺格式时，MTGA 内容应逐行解析"""
        text = "4 Lightning Bolt\n1x Counterspell"
        result = parse_deck_text(text, '平铺')
        assert len(result['cards']) == 2
        counts = {c['name']: c['count'] for c in result['cards']}
        assert counts['Lightning Bolt'] == 4
        assert counts['Counterspell'] == 1

    def test_force_plain_with_moxfield_content(self):
        """强制平铺格式时，Moxfield 内容被当作整行卡名解析"""
        text = "1 Lightning Bolt (M10) 123"
        result = parse_deck_text(text, '平铺')
        # 平铺通用正则 ^(\d+)x?\s+(.+)$ 会把整行当作卡名
        assert len(result['cards']) == 1
        assert result['cards'][0]['name'] == 'Lightning Bolt (M10) 123'

    def test_force_mtga_with_plain_content(self):
        """强制 MTGA 格式时，无 Commander 区则走通用解析"""
        text = "4 Lightning Bolt\n4 Mountain"
        result = parse_deck_text(text, 'MTGA')
        # MTGA 无 Commander 区时等同于平铺
        assert len(result['cards']) == 2
        assert len(result['errors']) == 0

    def test_force_mtga_with_commander(self):
        """强制 MTGA 格式时，正确识别 Commander 区"""
        text = "Deck\n4 Lightning Bolt\nCommander:\n1 Sisay, Weatherlight Captain"
        result = parse_deck_text(text, 'MTGA')
        assert len(result['cards']) == 1
        assert result['commander'] == 'Sisay, Weatherlight Captain'

    def test_force_moxfield_with_plain_content(self):
        """强制 Moxfield 格式时，平铺内容报错"""
        text = "4 Lightning Bolt"
        result = parse_deck_text(text, 'Moxfield')
        assert len(result['errors']) == 1
        assert len(result['cards']) == 0

    def test_force_moxfield_with_moxfield_content(self):
        """强制 Moxfield 格式时，正确解析"""
        text = "1 Lightning Bolt (M10) 123\n4 Mountain (M10) 124"
        result = parse_deck_text(text, 'Moxfield')
        assert len(result['cards']) == 2
        counts = {c['name']: c['count'] for c in result['cards']}
        assert counts['Lightning Bolt'] == 1
        assert counts['Mountain'] == 4

    def test_auto_detects_moxfield(self):
        """自动识别：Moxfield 格式正确检测"""
        text = "1 Lightning Bolt (M10) 1\n2 Mountain (M10) 2"
        result = parse_deck_text(text, '自动识别')
        assert len(result['cards']) == 2
        assert len(result['errors']) == 0

    def test_auto_detects_mtga(self):
        """自动识别：MTGA 格式正确检测"""
        text = "Deck\n1 Lightning Bolt\nCommander:\n1 Sisay"
        result = parse_deck_text(text, '自动识别')
        assert result['commander'] == 'Sisay'
        assert len(result['cards']) == 1

    def test_auto_falls_back_to_plain(self):
        """自动识别：无法识别时回退到平铺通用解析"""
        text = "4 Lightning Bolt\n4 Mountain"
        result = parse_deck_text(text, '自动识别')
        assert len(result['cards']) == 2
        assert len(result['errors']) == 0
