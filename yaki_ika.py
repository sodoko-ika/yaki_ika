#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""IkaLogから出力される statink.msgpack を分析する.
"""
import cv2
import numpy as np
import datetime
import distutils.util
import glob
import json
import shutil
import umsgpack

#表示するタイムライン用に、イベント秒数に加算する値（秒）
ADD_AT_SEC = 10
# ステージ名
STAGES = {
    'anchovy': {'ja': 'アンチョビットゲームズ', 'en': 'Ancho-V Games'},
    'arowana':  {'ja': 'アロワナモール', 'en': 'Arowana Mall'},
    'bbass':    {'ja': 'Bバスパーク', 'en': 'Blackbelly Skatepark'},
    'dekaline': {'ja': 'デカライン高架下', 'en': 'Urchin Underpass'},
    'hakofugu': {'ja': 'ハコフグ倉庫', 'en': 'Walleye Warehouse', },
    'hirame':   {'ja': 'ヒラメが丘団地', 'en': 'Flounder Heights', },
    'hokke':    {'ja': 'ホッケふ頭', 'en': 'Port Mackerel'},
    'kinmedai': {'ja': 'キンメダイ美術館', 'en': 'Museum d\'Alfonsino'},
    'mahimahi': {'ja': 'マヒマヒリゾート&スパ', 'en': 'Mahi-Mahi Resort', },
    'masaba':   {'ja': 'マサバ海峡大橋', 'en': 'Hammerhead Bridge', },
    'mongara':  {'ja': 'モンガラキャンプ場', 'en': 'Camp Triggerfish', },
    'mozuku':   {'ja':  'モズク農園', 'en': 'Kelp Dome', },
    'negitoro': {'ja': 'ネギトロ炭鉱', 'en': 'Bluefin Depot', },
    'shionome': {'ja': 'シオノメ油田', 'en': 'Saltspray Rig', },
    'shottsuru': {'ja': 'ショッツル鉱山', 'en': 'Piranha Pit'},
    'tachiuo':  {'ja':  'タチウオパーキング', 'en':  'Moray Towers', },
    }

# ルール名
RULES = {
    'nawabari': {'ja': 'ナワバリバトル', 'en': 'Turf War', },
    'area': {'ja': 'ガチエリア', 'en': 'Splat Zones', },
    'yagura': {'ja': 'ガチヤグラ', 'en': 'Tower Control', },
    'hoko': {'ja': 'ガチホコバトル', 'en': 'Rainmaker', },
    }

# やられ名
#\IkaLog\ikalog\constants.pyから引用させていただきました。
DICT_REASONS = {
    '52gal': {'ja': '.52ガロン', 'en': '.52 Gal'},
    '52gal_deco': {'ja': '.52ガロンデコ', 'en': '.52 Gal Deco'},
    '96gal': {'ja': '.96ガロン', 'en': '.96 Gal'},
    '96gal_deco': {'ja': '.96ガロンデコ', 'en': '.96 Gal Deco'},
    'bold': {'ja': 'ボールドマーカー', 'en': 'Sploosh-o-matic'},
    'bold_7': {'ja': 'ボールドマーカー7', 'en': 'Sploosh-o-matic 7'},
    'bold_neo': {'ja': 'ボールドマーカーネオ', 'en': 'Neo Sploosh-o-matic'},
    'dualsweeper': {'ja': 'デュアルスイーパー', 'en': 'Dual Squelcher'},
    'dualsweeper_custom': {'ja': 'デュアルスイーパーカスタム', 'en': 'Custom Dual Squelcher'},
    'h3reelgun': {'ja': 'H3リールガン', 'en': 'H-3 Nozzlenose'},
    'h3reelgun_cherry': {'ja': 'H3リールガンチェリー', 'en': 'Cherry H-3 Nozzlenose'},
    'h3reelgun_d': {'ja': 'H3リールガンD', 'en': 'H-3 Nozzlenose D'},
    'heroshooter_replica': {'ja': 'ヒーローシューターレプリカ', 'en': 'Hero Shot Replica'},
    'hotblaster': {'ja': 'ホットブラスター', 'en': 'Blaster'},
    'hotblaster_custom': {'ja': 'ホットブラスターカスタム', 'en': 'Custom Blaster'},
    'jetsweeper': {'ja': 'ジェットスイーパー', 'en': 'Jet Squelcher'},
    'jetsweeper_custom': {'ja': 'ジェットスイーパーカスタム', 'en': 'Custom Jet Squelcher'},
    'l3reelgun': {'ja': 'L3リールガン', 'en': 'L-3 Nozzlenose'},
    'l3reelgun_d': {'ja': 'L3リールガンD', 'en': 'L-3 Nozzlenose D'},
    'longblaster': {'ja': 'ロングブラスター', 'en': 'Range Blaster'},
    'longblaster_custom': {'ja': 'ロングブラスターカスタム', 'en': 'Custom Range laster'},
    'longblaster_necro': {'ja': 'ロングブラスターネクロ', 'en': 'Grim Range laster'},
    'momiji': {'ja': 'もみじシューター', 'en': 'Custom Splattershot Jr.'},
    'nova': {'ja': 'ノヴァブラスター', 'en': 'Luna Blaster'},
    'nova_neo': {'ja': 'ノヴァブラスターネオ', 'en': 'Luna Blaster Neo'},
    'nzap83': {'ja': 'N-ZAP83', 'en': 'N-ZAP \'83'},
    'nzap85': {'ja': 'N-ZAP85', 'en': 'N-ZAP \'85'},
    'nzap89': {'ja': 'N-ZAP89', 'en': 'N-Zap \'89'},
    'octoshooter_replica': {'ja': 'オクタシューターレプリカ', 'en': 'Octoshot Replica'},
    'prime': {'ja': 'プライムシューター', 'en': 'Splattershot Pro'},
    'prime_berry': {'ja': 'プライムシューターベリー', 'en': 'Berry Splattershot Pro'},
    'prime_collabo': {'ja': 'プライムシューターコラボ', 'en': 'Forge Splattershot Pro'},
    'promodeler_mg': {'ja': 'プロモデラーMG', 'en': 'Aerospray MG'},
    'promodeler_pg': {'ja': 'プロモデラーPG', 'en': 'Aerospray PG'},
    'promodeler_rg': {'ja': 'プロモデラーRG', 'en': 'Aerospray RG'},
    'rapid': {'ja': 'ラピッドブラスター', 'en': 'Rapid Blaster'},
    'rapid_deco': {'ja': 'ラピッドブラスターデコ', 'en': 'Rapid Blaster Deco'},
    'rapid_elite': {'ja': 'Rブラスターエリート', 'en': 'Rapid Blaster Pro'},
    'rapid_elite_deco': {'ja': 'Rブラスターエリートデコ', 'en': 'Rapid Blaster Pro Deco'},
    'sharp': {'ja': 'シャープマーカー', 'en': 'Splash-o-matic'},
    'sharp_neo': {'ja': 'シャープマーカーネオ', 'en': 'Neo Splash-o-matic'},
    'sshooter': {'ja': 'スプラシューター', 'en': 'Splattershot'},
    'sshooter_collabo': {'ja': 'スプラシューターコラボ', 'en': 'Tentatek Splattershot'},
    'sshooter_wasabi': {'ja': 'スプラシューターワサビ', 'en': 'Wasabi Splattershot'},
    'wakaba': {'ja': 'わかばシューター', 'en': 'Splattershot Jr.'},

    'carbon': {'ja': 'カーボンローラー', 'en': 'Carbon Roller'},
    'carbon_deco': {'ja': 'カーボンローラーデコ', 'en': 'Carbon Roller Deco'},
    'dynamo': {'ja': 'ダイナモローラー', 'en': 'Dynamo Roller'},
    'dynamo_burned': {'ja': 'ダイナモローラーバーンド', 'en': 'Tempered Dynamo Roller'},
    'dynamo_tesla': {'ja': 'ダイナモローラーテスラ', 'en': 'Gold Dynamo Roller'},
    'heroroller_replica': {'ja': 'ヒーローローラーレプリカ', 'en': 'Hero Roller Replica'},
    'hokusai': {'ja': 'ホクサイ', 'en': 'Octobrush'},
    'hokusai_hue': {'ja': 'ホクサイ・ヒュー', 'en': 'Octobrush Nouveau'},
    'pablo': {'ja': 'パブロ', 'en': 'Inkbrush'},
    'pablo_hue': {'ja': 'パブロ・ヒュー', 'en': 'Inkbrush Nouveau'},
    'pablo_permanent': {'ja': 'パーマネント・パブロ', 'en': 'Permanent Inkbrush'},
    'splatroller': {'ja': 'スプラローラー', 'en': 'Splat Roller'},
    'splatroller_collabo': {'ja': 'スプラローラーコラボ', 'en': 'Krak-On Splat Roller'},
    'splatroller_corocoro': {'ja': 'スプラローラーコロコロ', 'en': 'CoroCoro Splat Roller'},

    'bamboo14mk1': {'ja': '14式竹筒銃・甲', 'en': 'Bamboozler 14 MK I'},
    'bamboo14mk2': {'ja': '14式竹筒銃・乙', 'en': 'Bamboozler 14 MK II'},
    'bamboo14mk3': {'ja': '14式竹筒銃・丙', 'en': 'Bamboozler 14 Mk III'},
    'herocharger_replica': {'ja': 'ヒーローチャージャーレプリカ', 'en': 'Hero Charger Replica'},
    'liter3k': {'ja': 'リッター3K', 'en': 'E-liter 3K'},
    'liter3k_custom': {'ja': 'リッター3Kカスタム', 'en': 'Custom E-liter 3K'},
    'liter3k_scope': {'ja': '3Kスコープ', 'en': 'E-liter 3K Scope'},
    'liter3k_scope_custom': {'ja': '3Kスコープカスタム', 'en': 'Custom E-liter 3K Scope'},
    'splatcharger': {'ja': 'スプラチャージャー', 'en': 'Splat Charger'},
    'splatcharger_bento': {'ja': 'スプラチャージャーベントー', 'en': 'Bento Splat Charger'},
    'splatcharger_wakame': {'ja': 'スプラチャージャーワカメ', 'en': 'Kelp Splat Charger'},
    'splatscope': {'ja': 'スプラスコープ', 'en': 'Splatterscope'},
    'splatscope_bento': {'ja': 'スプラスコープベントー', 'en': 'Bento Splatterscope'},
    'splatscope_wakame': {'ja': 'スプラスコープワカメ', 'en': 'Kelp Splatterscope'},
    'squiclean_a': {'ja': 'スクイックリンα', 'en': 'Classic Squiffer'},
    'squiclean_b': {'ja': 'スクイックリンβ', 'en': 'New Squiffer'},
    'squiclean_g': {'ja': 'スクイックリンγ', 'en': 'Fresh Squiffer'},

    'bucketslosher': {'ja': 'バケットスロッシャー', 'en': 'Slosher'},
    'bucketslosher_deco': {'ja': 'バケットスロッシャーデコ', 'en': 'Slosher Deco'},
    'bucketslosher_soda': {'ja': 'バケットスロッシャーソーダ', 'en': 'Soda Slosher'},
    'hissen': {'ja': 'ヒッセン', 'en': 'Tri-Slosher'},
    'hissen_hue': {'ja': 'ヒッセン・ヒュー', 'en': 'Tri-Slosher Nouveau'},
    'screwslosher': {'ja': 'スクリュースロッシャー', 'en': 'Sloshing Machine'},
    'screwslosher_neo': {'ja': 'スクリュースロッシャーネオ', 'en': 'Sloshing Machine Neo'},

    'barrelspinner': {'ja': 'バレルスピナー', 'en': 'Heavy Splatling'},
    'barrelspinner_deco': {'ja': 'バレルスピナーデコ', 'en': 'Heavy Splatling Deco'},
    'barrelspinner_remix': {'ja': 'バレルスピナーリミックス', 'en': 'Heavy Splatling Remix'},
    'hydra': {'ja': 'ハイドラント', 'en': 'Hydra Splatling'},
    'hydra_custom': {'ja': 'ハイドラントカスタム', 'en': 'Custom Hydra Splatling'},
    'splatspinner': {'ja': 'スプラスピナー', 'en': 'Mini Splatling'},
    'splatspinner_collabo': {'ja': 'スプラスピナーコラボ', 'en': 'Zink Mini Splatling'},
    'splatspinner_repair': {'ja': 'スプラスピナーリペア', 'en': 'Refurbished Mini Splatling'},

    'chasebomb': {'ja': 'チェイスボム', 'en':  'Seeker', },
    'jumpbeacon': {'ja': 'ジャンプビーコン', 'en':  'Squid Beakon', },
    'kyubanbomb': {'ja': 'キューバンボム', 'en':  'Suction Bomb', },
    'pointsensor': {'ja': 'ポイントセンサー', 'en':  'Point Sensor', },
    'poison': {'ja': 'ポイズンボール', 'en':  'Disruptor', },
    'quickbomb': {'ja': 'クイックボム', 'en':  'Burst Bomb', },
    'splashbomb': {'ja': 'スプラッシュボム', 'en':  'Splat Bomb', },
    'splashshield': {'ja': 'スプラッシュシールド', 'en':  'Splash Wall', },
    'sprinkler': {'ja': 'スプリンクラー', 'en':  'Sprinkler', },
    'trap': {'ja': 'トラップ', 'en':  'Ink Mine', },

    'barrier': {'ja': 'バリア', 'en':  'Bubbler', },
    'bombrush': {'ja': 'ボムラッシュ', 'en':  'Bomb Rush', },
    'daioika': {'ja': 'ダイオウイカ', 'en':  'Kraken', },
    'megaphone': {'ja': 'メガホンレーザー', 'en':  'Killer Wail', },
    'supersensor': {'ja': 'スーパーセンサー', 'en':  'Echolocator', },
    'supershot': {'ja': 'スーパーショット', 'en':  'Inkzooka', },
    'tornado': {'ja': 'トルネード', 'en':  'Inkstrike', },

    'hoko_shot': {'ja': 'ガチホコショット', 'en': 'Rainmaker Shot', },
    'hoko_barrier': {'ja': 'ガチホコバリア', 'en': 'Rainmaker Shield', },
    'hoko_inksplode': {'ja': 'ガチホコ爆発', 'en': 'Rainmaker Inksplode', },

    'propeller': {'ja': 'プロペラから飛び散ったインク', 'en': 'Ink from a propeller'},

    'oob': {'ja': '三三(.ω.)三 場外に落ちた！', 'en': 'Out of Bounds', },
    'fall': {'ja': '三三(.ω.)三 奈落に落ちた！', 'en': 'Fall', },
    'drown': {'ja': '三三(.ω.)三 水場に落ちた！', 'en': 'Drowning', },
    }

#ギア効果
GEAR_ABILITIES = {
    'bomb_range_up': {'ja': 'ボム飛距離アップ', 'en': 'Bomb Range Up'},
    'bomb_sniffer': {'ja': 'ボムサーチ', 'en': 'Bomb Sniffer'},
    'cold_blooded': {'ja': 'マーキングガード', 'en': 'Cold Blooded'},
    'comeback': {'ja': 'カムバック', 'en': 'Comeback'},
    'damage_up': {'ja': '攻撃力アップ', 'en': 'Damage Up'},
    'defense_up': {'ja': '防御力アップ', 'en': 'Defense Up'},
    'empty': {'ja': '空', 'en': 'Empty'},
    'haunt': {'ja': 'うらみ', 'en': 'Haunt'},
    'ink_recovery_up': {'ja': 'インク回復力アップ', 'en': 'Ink Recovery Up'},
    'ink_resistance_up': {'ja': '安全シューズ', 'en': 'Ink Resistance'},
    'ink_saver_main': {'ja': 'インク効率アップ（メイン）', 'en': 'Ink Saver (Main)'},
    'ink_saver_sub': {'ja': 'インク効率アップ（サブ）', 'en': 'Ink Saver (Sub)'},
    'last_ditch_effort': {'ja': 'ラストスパート', 'en': 'Last-Ditch Effort'},
    'locked': {'ja': '未開放', 'en': 'Locked'},
    'ninja_squid': {'ja': 'イカニンジャ', 'en': 'Ninja Squid'},
    'opening_gambit': {'ja': 'スタートダッシュ', 'en': 'Opening Gambit'},
    'quick_respawn': {'ja': '復活時間短縮', 'en': 'Quick Respawn'},
    'quick_super_jump': {'ja': 'スーパージャンプ時間短縮', 'en': 'Quick Super Jump'},
    'recon': {'ja': 'スタートレーダー', 'en': 'Recon'},
    'run_speed_up': {'ja': 'ヒト移動速度アップ', 'en': 'Run Speed Up'},
    'special_charge_up': {'ja':  'スペシャル増加量アップ', 'en': 'Special Charge Up'},
    'special_duration_up': {'ja':  'スペシャル時間延長', 'en': 'Special Duration Up'},
    'special_saver': {'ja':  'スペシャル減少量ダウン', 'en': 'Special Saver'},
    'stealth_jump': {'ja':  'ステルスジャンプ', 'en': 'Stealth Jump'},
    'swim_speed_up': {'ja':  'イカダッシュ速度アップ', 'en': 'Swim Speed Up'},
    'tenacity': {'ja':  '逆境強化', 'en': 'Tenacity'}
    }

# ブキとスペシャルの対応辞書
# もし、スペシャルの利用者の誤認識が発生してもスルーできるように
DICT_SPECIALS = {
    '52gal': 'megaphone',
    '52gal_deco': 'tornado',
    '96gal': 'supersensor',
    '96gal_deco': 'daioika',
    'bold': 'megaphone',
    'bold_7': 'supershot',
    'bold_neo': 'daioika',
    'dualsweeper': 'supersensor',
    'dualsweeper_custom': 'megaphone',
    'h3reelgun': 'supersensor',
    'h3reelgun_cherry': 'barrier',
    'h3reelgun_d': 'supershot',
    'heroshooter_replica': 'bombrush',
    'hotblaster': 'megaphone',
    'hotblaster_custom': 'barrier',
    'jetsweeper': 'tornado',
    'jetsweeper_custom': 'daioika',
    'l3reelgun': 'megaphone',
    'l3reelgun_d': 'daioika',
    'longblaster': 'tornado',
    'longblaster_custom': 'daioika',
    'longblaster_necro': 'megaphone',
    'momiji': 'supersensor',
    'nova': 'supershot',
    'nova_neo': 'bombrush',
    'nzap83': 'daioika',
    'nzap85': 'supersensor',
    'nzap89': 'tornado',
    'octoshooter_replica': 'supershot',
    'prime': 'tornado',
    'prime_berry': 'bombrush',
    'prime_collabo': 'supershot',
    'promodeler_mg': 'supershot',
    'promodeler_pg': 'tornado',
    'promodeler_rg': 'daioika',
    'rapid': 'barrier',
    'rapid_deco': 'bombrush',
    'rapid_elite': 'supershot',
    'rapid_elite_deco': 'megaphone',
    'sharp': 'bombrush',
    'sharp_neo': 'supershot',
    'sshooter': 'bombrush',
    'sshooter_collabo': 'supershot',
    'sshooter_wasabi': 'tornado',
    'wakaba': 'barrier',
    'carbon': 'supershot',
    'carbon_deco': 'bombrush',
    'dynamo': 'supersensor',
    'dynamo_burned': 'megaphone',
    'dynamo_tesla': 'tornado',
    'heroroller_replica': 'megaphone',
    'hokusai': 'daioika',
    'hokusai_hue': 'supershot',
    'pablo': 'tornado',
    'pablo_hue': 'barrier',
    'pablo_permanent': 'daioika',
    'splatroller': 'megaphone',
    'splatroller_collabo': 'daioika',
    'splatroller_corocoro': 'supershot',
    'bamboo14mk1': 'megaphone',
    'bamboo14mk2': 'supersensor',
    'bamboo14mk3': 'tornado',
    'herocharger_replica': 'bombrush',
    'liter3k': 'supersensor',
    'liter3k_custom': 'daioika',
    'liter3k_scope': 'supersensor',
    'liter3k_scope_custom': 'daioika',
    'splatcharger': 'bombrush',
    'splatcharger_bento': 'supersensor',
    'splatcharger_wakame': 'megaphone',
    'splatscope': 'bombrush',
    'splatscope_bento': 'supersensor',
    'splatscope_wakame': 'megaphone',
    'squiclean_a': 'barrier',
    'squiclean_b': 'supershot',
    'squiclean_g': 'daioika',
    'bucketslosher': 'tornado',
    'bucketslosher_deco': 'daioika',
    'bucketslosher_soda': 'supershot',
    'hissen': 'barrier',
    'hissen_hue': 'supersensor',
    'screwslosher': 'bombrush',
    'screwslosher_neo': 'supershot',
    'barrelspinner': 'tornado',
    'barrelspinner_deco': 'daioika',
    'barrelspinner_remix': 'megaphone',
    'hydra': 'supersensor',
    'hydra_custom': 'barrier',
    'splatspinner': 'supershot',
    'splatspinner_collabo': 'barrier',
    'splatspinner_repair': 'bombrush',
    }

# 勝ち負け
DICT_JUDGES = {
    'win':  '勝ちました！',
    'lose': '負けました…',
    }

# 出力するメッセージの内容
DICT_MESSAGES = {
    'go_sign': "ε(*'-')з彡 バトルスタート！",
    'special_charged': "o(^◇^)○o＠ スペシャルがたまった！",
    'special_weapon':  "o(^◇^)oSP〓 %sをつかった！",
    'dead': "ﾉ*(≧Д≦)★ %sでやられた！",
    'killed': "v(`ω´)ﾉ ☆ プレイヤーをたおした！",
    'low_ink': "(ﾟ∀ﾟ；)ﾞ 凹 インクがきれた！",
    'result_judge': "(*ΦωΦ)ﾉ◇ ジャッジくんの結果発表！",
    'unknown': "しらないブキ",
    }

def dt_filename(data):
    u"""
    """
    if data['start_at'] is not None:
        d = datetime.datetime.fromtimestamp(data['start_at'])
    if d is None:
        d = datetime.datetime.fromtimestamp(data['end_at'])
        d = st.dt - datetime.timedelta(minutes=-3)
    return d.strftime('%Y%m%d-%H%M')

def imgpng_write(data):
    u"""msgpackに含まれる
    'image_gear': 
    'image_result': 
    'image_judge': 
    の画像ファイルを出力する。
    """
    ts = dt_filename(data)
    imgnames = {'image_gear', 'image_result', 'image_judge'}
    for imgname in imgnames:
        image = np.asarray(bytearray(data[imgname]), dtype=np.uint8)
        decimg = cv2.imdecode(image, cv2.IMREAD_COLOR)
        fn = "./img/%s_%s.png" % (ts, imgname)
        cv2.imwrite(fn, decimg)
 
def json_write(data):
    u"""
    """
    ts = dt_filename(data)
    imgnames = {'image_gear', 'image_result', 'image_judge'}
    for imgname in imgnames:
        fn = "./img/%s_%s.png" % (ts, imgname)
        data[imgname] = fn

    ts = dt_filename(data)
    fn = "./json/%s.json" % ts
    with open(fn, 'w') as fw:
	    json.dump(data, fw, sort_keys=True, indent=4)

def get_reason_name(reason_code):
    u"""やられ内容の日本語対応を取得する """
    if reason_code in DICT_REASONS:
        reason_name = DICT_REASONS[reason_code]['ja']
    else:
        reason_name = DICT_MESSAGES['unknown']
    return reason_name

def msg_write(fw, at_sec, msg):
    u"""メッセージをタイムライン風なテキストに整形し、ファイルに書き込む
    fw:ファイルハンドル
    at_sec:秒 時:分(00:00)の形式に加工して、テキストの先頭に表示。 負の値の時は、表示しない。
    msg: メッセージ文字列
    ex)00:00 バトルスタート！
    """
    minsec = ""
    if at_sec >= 0:
        minsec = "%02d:%02d " % (at_sec / 60, at_sec % 60)
    msg = "%s%s\n" % (minsec, msg)
    fw.write(msg)
    print(msg.strip())

def event_write(data):
    u"""
    'special_weapon'は、自分以外が発動したイベントも拾っている。 me=True が自分の発動したタイミング。
    """
    type_lists = {
        'special_charged',
	    'dead',
	    'killed',
	    'low_ink'
    }

    # ファイル名は記録開始の年月日-時分 ./txt/20160730-2201.txt みたいな感じで出力しています。
    fw = open('./txt/%s.txt' % dt_filename(data), 'w')
    print('\n保存ファイル名 (%s)\n' % fw.name)

    my_special = DICT_SPECIALS[data['weapon']]  #自分が使うブキのスペシャルを取得
    sp_charge_flag = False
    battle_start_msg = sp_charge = sp_used = sp_dead = 0 
    for event in data['events']:
        msg = None
        if event['type'] in type_lists:
            msg = DICT_MESSAGES[event['type']]

        if event['type'] == 'special_charged':  #スペシャルたまった
            sp_charge += 1
            sp_charge_flag = True   #たまった

        if event['type'] == 'special_weapon':   #スペシャルを使ったとき
            if event['me'] and event['special_weapon'] == my_special:   #データ中のスペシャル使用者が自分＆自ブキのスペシャルの時
                sp_used += 1    #スペシャルを使った数
                sp_charge_flag = False  #使ったら消える
                reason_name ="スペシャル"
                msg = DICT_MESSAGES[event['type']]
                if event['special_weapon'] in DICT_REASONS:
                    reason_code = event['special_weapon']
                    reason_name = get_reason_name(reason_code)
                msg = msg % reason_name

        if event['type'] == 'dead': #やられた
            reason_name ="しらないブキ"
            if event['reason'] in DICT_REASONS:
                reason_code = event['reason']
                reason_name = get_reason_name(reason_code)
            #場外・転落・水死
            if reason_code in ('oob', 'fall', 'drown'):
                msg = reason_name
            else:
                msg = msg % reason_name

            if sp_charge_flag:  #スペシャル持ったまま抱え落ちした
                sp_dead += 1
                sp_charge_flag = False  #スペシャル消える
                msg = "%s %s" % (msg, '◆◆◆')

        #バトルスタート（1行目に固定で出力する）
        if battle_start_msg == 0:
            battle_start_msg += 1
            msg = DICT_MESSAGES['go_sign']

        #表示内容が設定されている
        if msg is not None:
            at_sec = event['at'] + ADD_AT_SEC
            msg_write(fw, at_sec, msg)

        elif event['type'] == 'finish':   #バトル終了後は、固定で結果内容の情報を出力する。
            #ジャッジくん判定（）
            msg = DICT_MESSAGES['result_judge']
            at_sec = 190 + ADD_AT_SEC   #ジャッジくんは3分10秒くらい + 調整
            msg_write(fw, at_sec, msg)

            # リザルト（）
            if data['map'] in STAGES:   #ステージの日本語名を取得
                stage_name = STAGES[data['map']]['ja']
            if data['rule'] in RULES:   #ルールの日本語名を取得
                rule_name = RULES[data['rule']]['ja']
            judge = DICT_JUDGES[data['result']]  #勝ち負け

            #例：キンメダイ美術館のナワバリバトルで勝ちました！
            msg = "%sの%sで%s" % (stage_name, rule_name, judge)
            at_sec = 200 + ADD_AT_SEC   #リザルト発表は3分20秒くらい + 調整
            msg_write(fw, at_sec, msg)

            #ブキは プライムシューター リザルトは 999p 0k/1d です。
            #スペシャルは3回ためて 3回つかい、抱え落ちはしませんでした。
            msg = "\n%sをつかって %dp %dk/%ddでした。" % (get_reason_name(data['weapon']), data['my_point'], data['kill'], data['death'])
            if sp_dead == 0:
                sp_dead_msg = "ありません。"
            else:
                sp_dead_msg = "%d回です。" % sp_dead
            msg2 = "\nスペシャルを%d回溜めて%d回発動し 抱え落ちは%s" % (sp_charge, sp_used, sp_dead_msg)
            msg = "%s %s" % (msg, msg2)
            at_sec = -1 #テキストの先頭に時分を付けない
            msg_write(fw, at_sec, msg)

if __name__ == "__main__":
    files = glob.glob('/tmp/*.msgpack')
    for file in files:
        f = open(file, 'rb')
        data = umsgpack.unpack(f)
        msgfn = f.name
        f.close()

        #必要な機能以外はコメントで対応
        ADD_AT_SEC = 10     #タイムラインに表示する秒数を 動画のスタートに合うように調整する値
        event_write(data)	#イベントをタイムライン形式でテキストファイルに保存する

        imgpng_write(data)  #画像データ3種類出力 ※必ずjson_writeより先に処理すること。
        json_write(data)    #jsonファイルとして保存する。        

        mvfn = '.%s' % msgfn        #処理済みのファイルを移動する
        shutil.move(msgfn, mvfn)