
from enum import Enum
from PyQt5.QtCore import QPoint, QSize

KikkaMemoryFileName = 'Kikka.memory'

class WindowConst:
    UNSET = QPoint(0x7FFFFFFF, 0x7FFFFFFF)
    ShellWindowDefaultWidth = 500
    ShellWindowDefaultHeight = 500
    ShellWindowDefaultCenter = QPoint(ShellWindowDefaultWidth / 2, ShellWindowDefaultHeight)
    ShellWindowDefaultSize = QSize(ShellWindowDefaultWidth, ShellWindowDefaultHeight)

    DialogWindowDefaultWidth = 200
    DialogWindowDefaultHeight = 220
    DialogWindowDefaultSize = QSize(DialogWindowDefaultWidth, DialogWindowDefaultHeight)
    DialogWindowDefaultMargin = [3, 3, 3, 3]

class GhostEvent(Enum):
    EventNone       = 0
    MouseDown       = 1
    MouseMove       = 2
    MouseTouch      = 3
    MouseUp         = 4
    MouseDoubleClick = 5
    WheelEvent      = 6

    CustomEvent = 100

class SurfaceEnum:
    # surface const
    NORMAL = 0         # 正常 / 素1
    SHY = 1            # 害羞(侧面) / 照れ1
    SURPRISE = 2       # 惊讶 / 驚き
    WORRIED = 3        # 忧郁 / 落込み
    DISAPPOINTED = 4   # 失望 /
    JOY = 5            # 高兴 / 喜び
    EYE_CLOSURE = 6    # 闭眼 / 目閉じ
    ANGER = 7          # 生气 / 怒り
    FORCED_SMILE = 8   # 苦笑 / 苦笑
    ANGER2 = 9         # 尴尬 / 照れ怒り
    HIDE = 19          # 消失 /
    THINKING = 20      # 思考 / 思考
    ABSENT_MINDED = 21 # 恍惚 / 恍惚
    P90 = 22           # P90 / P90
    DAGGER = 23        # 匕首 / 鉈
    SINGING = 25       # 唱歌 / 歌
    FRONT = 26         # 正面 / 正面
    CHAINSAW = 27      # 电锯 / チェーンソー
    VALENTINE = 28     # 礼物 / バレンタイン
    HAPPINESS = 29     # 幸福 / 幸せ
    SIDEWAYS = 30      # 看斗和 / 横向き
    FIVESEVEN = 32     # FiveseveN(手枪) / FiveseveN
    SURPRISE2 = 33     # 委屈 / 驚き
    KNIFE = 34         # 军刀 / ナイフ
    ENDURE = 35        # 难过 / 耐え
    SLOUCH = 40        # 鞠躬 / 前屈み
    SLOUCH_JOY = 41    # 鞠躬(闭眼) / 喜び（前屈み）
    APRON_TEA = 50     # 围裙(红茶) / エプロン（紅茶）
    APRON_SHY = 51     # 围裙(害羞) / エプロン（照れ）
    NORMAL2 = 100      # 正常2 / 素2
    SHY2 = 101         # 害羞2 / 照れ2
    APRON_COFFEE = 150 # 围裙(咖啡) / エプロン（コーヒー）
    APRON_TEA2 = 250    # 围裙(日本茶) / エプロン（日本茶）

    KERO_NORMAL = 10           # 正常(闭眼) / 素
    KERO_SIDEWAYS = 11         # 侧身(睁眼) / 横
    KERO_FRONT = 12            # 正面(睁眼正视) / 正面
    KERO_TURNING = 13          # 转头(扭头无视) / 转头
    KERO_HUMAN_JOY = 110       # 笑(人形) / 笑(人形)
    KERO_HUMAN_NORMAL = 111    # 正常(人形) / 素(人形)
    KERO_HUMAN_SURPRISE = 117  # 惊讶(人形) / 驚き(人形)

SurfaceNameEnum = {
    SurfaceEnum.NORMAL : "Normal",
    SurfaceEnum.SHY: "Shy",
    SurfaceEnum.SURPRISE: "Surprise",
    SurfaceEnum.WORRIED: "Worried",
    SurfaceEnum.DISAPPOINTED: "Disappointed",
    SurfaceEnum.JOY: "Joy",
    SurfaceEnum.EYE_CLOSURE: "Eye closure",
    SurfaceEnum.ANGER: "Anger",
    SurfaceEnum.FORCED_SMILE: "Forced smile",
    SurfaceEnum.ANGER2: "Anger2",
    SurfaceEnum.HIDE: "Hide",
    SurfaceEnum.THINKING: "Thinking",
    SurfaceEnum.ABSENT_MINDED: "Absent minded",
    SurfaceEnum.P90: "P90",
    SurfaceEnum.DAGGER: "Dagger",
    SurfaceEnum.SINGING: "Singing",
    SurfaceEnum.FRONT: "Front",
    SurfaceEnum.CHAINSAW: "Chainsaw",
    SurfaceEnum.VALENTINE: "Valentine",
    SurfaceEnum.HAPPINESS: "Happiness",
    SurfaceEnum.SIDEWAYS: "Sideways",
    SurfaceEnum.FIVESEVEN: "Fiveseven",
    SurfaceEnum.SURPRISE2: "Surprise2",
    SurfaceEnum.KNIFE: "knife",
    SurfaceEnum.ENDURE: "Endure",
    SurfaceEnum.SLOUCH: "Slouch",
    SurfaceEnum.SLOUCH_JOY: "Slouch joy",
    SurfaceEnum.APRON_TEA: "Apron tea",
    SurfaceEnum.APRON_SHY: "Apron shy",
    SurfaceEnum.NORMAL2: "Normal2",
    SurfaceEnum.SHY2: "Shy2",
    SurfaceEnum.APRON_COFFEE: "Apron coffee",
    SurfaceEnum.APRON_TEA2: "Apron tea2",

    SurfaceEnum.KERO_NORMAL: "Kero Normal",
    SurfaceEnum.KERO_SIDEWAYS: "Kero Sideways",
    SurfaceEnum.KERO_FRONT: "Kero Front",
    SurfaceEnum.KERO_TURNING: "Kero Turning",
    SurfaceEnum.KERO_HUMAN_JOY: "Kero Human Joy",
    SurfaceEnum.KERO_HUMAN_NORMAL: "Kero Human Normal",
    SurfaceEnum.KERO_HUMAN_SURPRISE: "Kero Human Surprise",
}



