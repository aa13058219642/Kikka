

from PyQt5.QtCore import QPoint


class ShellConst:
    ImageWidth = 500
    ImageHeight = 500
    ImageBaseX = ImageWidth / 2
    ImageBaseY = ImageHeight / 2
    ImageOffset = QPoint(ImageBaseX, ImageBaseY)


class SurfaceEnum():
    # surface const
    ENUM_NORMAL = 0  # 正常 / 素1
    ENUM_SHY = 1  # 害羞(侧面) / 照れ1
    ENUM_SURPRISE = 2  # 惊讶 / 驚き
    ENUM_WORRIED = 3  # 忧郁 / 落込み
    ENUM_DISAPPOINTED = 4  # 失望 /
    ENUM_JOY = 5  # 高兴 / 喜び
    ENUM_EYE_CLOSURE = 6  # 闭眼 / 目閉じ
    ENUM_ANGER = 7  # 生气 / 怒り
    ENUM_FORCED_SMILE = 8  # 苦笑 / 苦笑
    ENUM_ANGER2 = 9  # 尴尬 / 照れ怒り
    ENUM_HIDE = 19  # 消失 /
    ENUM_THINKING = 20  # 思考 / 思考
    ENUM_ABSENT_MINDED = 21  # 恍惚 / 恍惚
    ENUM_P90 = 22  # P90 / P90
    ENUM_DAGGER = 23  # 匕首 / 鉈
    ENUM_SINGING = 25  # 唱歌 / 歌
    ENUM_FRONT = 26  # 正面 / 正面
    ENUM_CHAINSAW = 27  # 电锯 / チェーンソー
    ENUM_VALENTINE = 28  # 礼物 / バレンタイン
    ENUM_HAPPINESS = 29  # 幸福 / 幸せ
    ENUM_SIDEWAYS = 30  # 看斗和 / 横向き
    ENUM_FIVESEVEN = 32  # FiveseveN(手枪) / FiveseveN
    ENUM_SURPRISE2 = 33  # 委屈 / 驚き
    ENUM_KNIFE = 34  # 军刀 / ナイフ
    ENUM_ENDURE = 35  # 难过 / 耐え
    ENUM_SLOUCH = 40  # 鞠躬 / 前屈み
    ENUM_SLOUCH_JOY = 41  # 鞠躬(闭眼) / 喜び（前屈み）
    ENUM_APRON_TEA = 50  # 围裙(红茶) / エプロン（紅茶）
    ENUM_APRON_SHY = 51  # 围裙(害羞) / エプロン（照れ）
    ENUM_NORMAL2 = 100  # 正常2 / 素2
    ENUM_SHY2 = 101  # 害羞2 / 照れ2
    ENUM_APRON_COFFEE = 150  # 围裙(咖啡) / エプロン（コーヒー）
    ENUM_APRON_JPN_TEA = 250  # 围裙(日本茶) / エプロン（日本茶）

    ENUM_KERO_NORMAL = 10  # 正常(闭眼) / 素
    ENUM_KERO_SIDEWAYS = 11  # 侧身(睁眼) / 横
    ENUM_KERO_FRONT = 12  # 正面(睁眼正视) / 正面
    ENUM_KERO_TURNING = 13  # 转头(扭头无视) / 转头
    ENUM_KERO_HUMAN_JOY = 110  # 笑(人形) / 笑(人形)
    ENUM_KERO_HUMAN_NORMAL = 111  # 正常(人形) / 素(人形)
    ENUM_KERO_HUMAN_SURPRISE = 117  # 惊讶(人形) / 驚き(人形)




