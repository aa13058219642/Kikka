# Shell——surfaces.txt

Shell 的surfaces.txt配置文件说明

原文来自[这里](http://ssp.shillest.net/ukadoc/manual/descript_shell_surfaces.html)，对于意义及作用不明的字段暂不进行翻译。



## 概要

用于执行shell的各种定义的文件。 基本上所有的都可以省略。 只写你需要的东西。

例如，在这里设定每个表情的动画（面部表情，部位，框架，服装部位），命中判断，图像构成等。

如果你想给一个表情ID一个别名，你也可以在这里设置。

除了SSP之外，还可以在光标保持命中判断，光标显示更改等情况下进行显示工具提示等设置。

另一方面，请注意，这里描述了与shell基本信息有关的设置，例如shell名称和shell作者名称，换装ownerdoor菜单的显示设置（右键菜单），而不是descript.txt。





#### 基本格式

基本上，大部分设置可以省略，每个设置都可以根据需要完成。

该设置应分别写在括号“{”和“}”所包围的每个大括号中，除字符集外，必须写在第一行（如果写入的话）（对于每次呼吸，本页中的每个项目参考）。

“{”和“}”必须作为只写入该行的行存在，例如，不可能连续写入大括号名称，如“surface 1 {”。





## surface

```

surface1

{

element0,overlay,body0.png,0,0

element1,overlay,face0.png,0,0



collision0,188,25,252,63,Head

collision1,190,92,236,118,Face

collision2,180,191,220,222,Bust

collision3,154,311,248,362,Skirt



animation0.interval,sometimes

animation0.pattern0,overlay,101,100,168,67

animation0.pattern1,overlay,100,100,168,67

animation0.pattern2,overlay,101,100,168,67

animation0.pattern3,overlay,-1,100,168,67

}

```



### 动画

Shell具有动画功能。这是通过连续绘制静止图像的帧来表示运动图像。



为每个曲面设置动画。用作动画的每个帧的图像是另一个表面。即使这个时候，已经被称为一件都还进一步动画定义侧面，它通常被忽略（只有然而SSP，见有一个机制，装扮说那件衣服复用）。



在每个表面，或者当启动动画本身，在每个帧中使用的任何表面的设置，有必要定义的内容，如是否以任何方式和时间间隔绘制。



在surfaces.txt上的一系列动画规范的名称为SERIKO。



```

surface0

{

//眨眼

animation0.interval,rarely

animation0.pattern0,overlay,101,700,200,100

animation0.pattern1,overlay,102,700,200,100

animation0.pattern2,overlay,101,700,200,100

animation0.pattern3,overlay,-1,700,0,0



//交谈

animation10.interval,talk,2

animation10.pattern0,overlay,200,700,200,120

animation10.pattern1,overlay,201,700,200,120

animation10.pattern2,overlay,202,700,200,120

animation10.pattern3,overlay,-1,700,0,0

}

```

例如，surfaces.txt中动画的定义如上所述。



在上面的描述中，为表面0定义了两个动画：“眨眼”“交谈”。



所有动画定义都包括“interval”定义和“pattern”定义。选项的定义或以其它方式，但在可选的，“间隔”的定义是不可能省略，也必须出现在动画序列的开始的SSP也触摸动画专用于那些的判断定义的情况下定义的一。必须至少有一个模式定义。



“interval”定义是关于何时播放动画的设置。在上面的例子中，出现了“rarely”，“talk”和“never”三种规格。有关详细信息，但见动画间隔的部分，“眨眼”动画作为概要是从时间播放到时刻，“交谈”动画适于每个角色说话两个字符的时间来播放。



“pattern”定义是动画的每个“帧”的设置。设置框架的绘制方法（参考绘图方法的部分），直到显示的等待时间，以及框架的位置相对于下框架移位的程度。应根据需要准备“pattern”定义。 “pattern”*的“*”中的数字是从0开始的序列号。



##### 每个动画的关系

ID被赋予所有动画（有关具体规范，请参阅animation*，interval部分）。



ID不允许重叠在一个单一的表面，动画也具有不同的面中相同的ID预期具有相同的含义。例如，假设当“surface0”的字符朝向正面而“surface1”面向水平时，则在两者上设置“眨眼”动画。此时，对应于所述帧中的图像来表示从姿态的字符应成为不同的东西的差实际眨眼，应该是相同的动画ID仍然被表面的两个给出。特别地，该ID和含义之间的关联对于换药将是必不可少的，这将在后面描述。



所有不同的动画基本上是独立的，并且异步地开始和结束。

例如，和动画眨眼，动画交谈，必应开始和结束，而无需担心的是Sotomai，无论对方是彼此移动，只要它被定义为实际的不同ID动画它就是这样的。



然而，另一方面，还存在一种机制，使用动画本身作为触发器，通过诸如“start”和“alternativestart”之类的特殊绘图方法来执行另一动画，以执行其他动画。

此外，可以通过指定“exclusive”选项来执行独占动画。



### 换装

壳牌有一种叫做换装的机制。这用于在单个shell中显示/隐藏和切换类型，例如多个服装。



Ikki的外壳中的衣服变化被定位为一种动画。

然而不是帧提前像其他动画，并且所有的帧（pattern），并在动画开始立即基面被合成时，的特征在于被视为后续静止图像（因此pattern定义的权重参数被忽略了）。

这种“表现就像绘图与基面融为一体”的行为非常适合于表达衣服之类的东西。



作为换装动画的开始和结束主要通过从所有者门菜单的换装菜单切换来控制。在SSP的情况下，另外，可以使用Sakura脚本的\！[Bind]标签从ghost侧进行控制。

所有者 - 玩偶菜单一侧的设置由descript.txt而不是surfaces.txt完成，因此请查看该页面。



另外，MAYUNA的名称是关于在surfaces.txt中有关一系列动画的规范。



```

surface0

{

//服装1 定义动画ID为0

animation0.interval,bind

animation0.pattern0,add,500,0,50,100



//服装2 定义动画ID为1

animation1.interval,bind

animation1.pattern0,add,501,0,50,100

}



//--- 换装定义 ---

// 衣服1

surface500

{

element0,overlay,dress1.png,0,0

}



// 衣服2

surface501

{

element0,overlay,dress2.png,0,0

}

```

例如，faces.txt中敷料的定义如上所述。



在上面的描述中，“衣服1”和“衣服2”的两个敷料被定义为“surface0”。



与普通动画定义类似，“interval”定义和“pattern”定义是必要的。 通过在“interval”定义中指定“bind”，它表示动画是修整的定义。



在动画的情况下，“pattern”定义是通过帧数来完成的，但是在修整的情况下它仍然是图片规格，因此我们合成尽可能多的部分而不是帧。 如在示例中，如果仅有一个部件构成修整，则“pattern”线仅是一条线。 另外，在打扮的情况下，由于立即合成每个部分，因此忽略权重参数。



稍后描述“pattern”定义的渲染方法。



##### 可用的绘图方法

在MATERIA（实名）中，可以使用准备敷料的四种方法，即“bind”“add”“reduce”“insert”。 其中，bind是旧规范，add是向上兼容的。



在SSP中，作为普通动画绘制方法准备的一些东西甚至可以通过打扮来使用。



有关可专门用于修整的绘图方法等的详细信息，请参阅绘图方法部分。



##### 区间组合规范中的bind

在SSP中，如动画间隔部分所述，可以指定间隔的组合。



如果组合名称中包含“bind”，则如果单独“bind”，则原始拥有的静止图像规范的属性将丢失（“pattern”定义的权重将不被忽略）。 但是，由于动画的寿命不会改变，例如在组合指定的情况下，例如“bind”+“runonce”，当完成所有“pattern”的绘制时的指示，基面被改变或修整 它将继续改变，直到有变化。



因此，在包括“bind”的区间组合规范中，动画不应该在“pattern”定义的最后一行中结束，并且应当合成要作为静止图像保留的图形。



##### 多件衣服更换定义（仅限SSP）

通常，如果在被称为动画帧的“surface”上定义“surface”的动画，则忽略它们。



然而，在SSP中，“bind”的“interval”（=衣服变化）被反映而不被忽略。



通过这样做，可以根据动画框架侧的衣服变化来定义结构受到衣服变化影响的动画的定义。



也可以嵌套多个装扮，但忽略循环引用。



### 关于SERIKO的旧定义和新定义

在Matsui（MATERIA）开发的最终版本中，SERIKO（动画）的设置格式发生了变化，即faces.txt。

关于这一点，我们将新定义（SERIKO / 2.0）称为先前定义为原始规范中存在的SERIKO / 1.x系列的前定义，并将未记录为新定义。



除此之外，还有一个表示SSP等在MATERIA开发结束后独立添加了sufraces.txt的格式（例如，range.append和surface1-9等范围指定）。

可能有人或文档称这个新定义，包括新定义，但至少注意到ukadoc中提到的新旧定义是SERIKO格式的单词，而不仅仅是这种用法。



##### 新定义和旧定义之间的区别

更改了所有与SERIKO相关的定义行，以“animation”一词开头。

pattern定义行的参数顺序已更改（绘图方法指定移至开头）。

pattern定义的权重参数的单位已从10毫秒变为1毫秒。

在bracket方法alternativestart中，ID规范的括号从[]更改为（）。

除此之外，还需要通过设置describe括号来定义“version，1”。



下面是**`相同定义内容`**的旧定义和新定义的示例。

```

// 旧

surface1

{

0interval,rarely

0pattern0,0,0,alternativestart,[1.2]



1interval,never

1pattern0,101,70,overlay,200,100

1pattern1,102,70,overlay,200,100

1pattern2,101,70,overlay,200,100

1pattern3,-1,70,overlay,0,0



2interval,never

2pattern0,101,70,overlay,200,100

2pattern1,102,70,overlay,200,100

2pattern2,101,70,overlay,200,100

2pattern3,-1,70,overlay,0,0

2pattern4,101,70,overlay,200,100

2pattern5,102,70,overlay,200,100

2pattern6,101,70,overlay,0,0

2pattern7,-1,70,overlay,0,0

}

```

```

// 新

surface1

{

animation0.interval,rarely

animation0.pattern0,alternativestart,(1.2)



animation1.interval,never

animation1.pattern0,overlay,101,700,200,100

animation1.pattern1,overlay,102,700,200,100

animation1.pattern2,overlay,101,700,200,100

animation1.pattern3,overlay,-1,700,0,0



animation2.interval,never

animation2.pattern0,overlay,101,700,200,100

animation2.pattern1,overlay,102,700,200,100

animation2.pattern2,overlay,101,700,200,100

animation2.pattern3,overlay,-1,700,0,0

animation2.pattern4,overlay,101,700,200,100

animation2.pattern5,overlay,102,700,200,100

animation2.pattern6,overlay,101,700,200,100

animation2.pattern7,overlay,-1,700,0,0

}

```



```

旧：[animationID]pattern[patternID],[surfaceID],[权重],[PaintType],[X],[Y]

新：animation[animationID].pattern[patternID],[PaintType],[surfaceID],[权重],[X],[Y]

```



请注意，开头以“animation”开头，并且权重的数值乘以10，并且绘图方法的指定已移至参数的开头。

除了在alternativestart中将[]更改为（）的事实之外，对于在alternativestart的情况下忽略的“surfaceID”“权重”，在旧定义中，写入虚拟数值0，而新定义 然后，从绘图方法移动到顶部的关系，我认为你也可以看到它可以完全省略，包括“合成位置x，y”。



##### 新定义描述的优点

- 设置SSP增加了它自己的（在页面上的项目这显示本草的是，有只没有在SSP的显示器），你可以写在旧的定义，它没有假设。

同样是在那些在未来添加的所有设置正确。

如果你想使用这些设置，（有不正常运行是旧的定义可能）希望来形容新的定义。

在这种情况下，由于错误和混合新旧定义，有必要统一的新定义。



- 重量单位更改为从1毫秒10毫秒，它能够更细腻的设置。

- 如在上面的例子也可知，通过绘制方法已经移动到的参数的顶部，它也可能优点在于，在一个特殊的绘图方法被忽略的参数，如开始和alternativestart省略清洁。



- 另一方面，由短语“动漫”是明确的，强调对SERIKO统一的定义，更多的也可能有在其上的意义更容易在该行中了解一个表面，它习惯于雅东西叫做知名度左右是由于个体差异多么大，还那么容易阅读到熟悉是更老的定义更自然的感觉。



如果你感觉不到好处，如上述观点出发，也未必一定意味着要迁移，如果你想只在SSP的对应关系。



应当指出的是，因为它已经在UKADOC基本上就SERIKO，如果你想在旧的定义的描述写的新定义进行了说明，请仔细阅读酌情提及上述。



#### 基面

每个表面的基本表面，合成动画之前的图像称为基本表面。

动画通常绘制在基面的上侧（屏幕的前侧）。



##### 实体

某个surface的基面由对应于ID的“surface*.png”和对应于ID的surface括号的element指定来定义。



对于具有surface*.png的曲面，图像是surface*的基础曲面。 但是，如果同时定义element0，则丢弃surface*.Png的内容并用element0的定义内容替换（这是用于确保兼容性的规范）。



如果在element1之后存在定义，则它们以这样的方式顺序合成，即它们堆叠在它们之上，并且最终的合成结果被视为基础表面。



##### 基本表面大小和动画组合

在动画定义中，当尝试合成大于包括基础表面的透明部分的大小的图像时的行为留给当前基础软件的实现。



MATERIA不显示从基面突出的部分。

在CROW中，当尝试合成从基面突出的图像时，绘图不能正确执行。



在SSP中，允许合成大于基面的图像，并且行为使得在基面侧补充不足尺寸的透明区域之后执行合成。 当animation-pattern的X坐标·Y坐标值为0,0时，动画侧的图像的基本原始左上角和左上角重叠。 也可以为坐标值设置负值。



##### 每个元素的垂直结构

在下文中，屏幕的前侧表示为上层，屏幕的后侧表示为下层。



在element和装扮（具有间隔绑定的动画）中，elementID.patternID越小，越低越好，越大越好。



##### 每个动画的基础表面和顶部和底部结构

基本表面基本上是放置在所有合成物底部的图像，但指定了SSP background选项的动画在基础表面的下方（后面）合成。



包括衣服改变在内的每个动画之间的垂直结构通常从具有较大动画ID的动画降序开始按降序排列（从较大的数字开始布置在屏幕的正面）。 但是，在SSP中，如果使用describe括号定义animation-sort，则可以按升序执行。



##### 命中判断的垂直结构（collision）

基本上，最初出现在surfaces.txt中的碰撞定义是表面命中判断的顶部。但是，在SSP中，如果使用descript括号定义collision-sort，则还可以使用collisionID作为引用设置升序/降序。



在SSP中，可以通过设置动画* .collision来设置仅在显示特定动画时有效的命中判断。在这种情况下，首先，考虑每个动画的垂直结构，并且分别以通常的顺序评估动画基础表面的命中判断。



总结动画排序的设置从下到上的情况



具有较大ID的普通动画的较高命中判断

较低命中确定具有较大ID的普通动画

具有较小ID的普通动画的较高命中判断

具有较小ID的普通动画的较高命中确定

基础表面的命中确定更高

低于基面的命中确定

使用具有更大ID的背景选项确定动画的更高命中率

低于具有较大ID的背景选项的动画的较低命中确定

使用较小ID的背景选项确定动画的命中率较高

使用较小ID的背景选项确定动画的命中率较高

（这里的动画也包括装扮）。



#### surfacesID分配

基本上，可以自由决定将哪个表面ID分配给哪个面部表情/内容。



然而，“surfaces0”和“surfaces10”是默认表面所必需的，并且必须将透明图像等准备为“surfaces10”，即使它是没有交配侧的重影（仅对于SSP，它是必要的） 可以通过设置“descript”等来更改默认曲面。



此外，由于暂时存在像“事实上的标准”这样的ID分配，所以如下所示。 最后，下面的分配（0和10除外）不是强制性的，它是参考级别，基本上是自由的。



```
Sakura
0       # 正常 / 素1
1       # 害羞(侧面) / 照れ1
2       # 惊讶 / 驚き
3       # 忧郁 / 落込み
4       # 失望 /
5       # 高兴 / 喜び
6       # 闭眼 / 目閉じ
7       # 生气 / 怒り
8       # 苦笑 / 苦笑
9       # 尴尬 / 照れ怒り
19      # 消失 /
20      # 思考 / 思考
21      # 恍惚 / 恍惚
22      # P90 / P90
23      # 匕首 / 鉈
25      # 唱歌 / 歌
26      # 正面 / 正面
27      # 电锯 / チェーンソー
28      # 礼物 / バレンタイン
29      # 幸福 / 幸せ
30      # 看斗和 / 横向き
32      # FiveseveN(手枪) / FiveseveN
33      # 委屈 / 驚き
34      # 军刀 / ナイフ
35      # 难过 / 耐え
40      # 鞠躬 / 前屈み
41      # 鞠躬(闭眼) / 喜び（前屈み）
50      # 围裙(红茶) / エプロン（紅茶）
51      # 围裙(害羞) / エプロン（照れ）
100     # 正常2 / 素2
101     # 害羞2 / 照れ2
150     # 围裙(咖啡) / エプロン（コーヒー）
250     # 围裙(日本茶) / エプロン（日本茶）

kero
10      # 正常(闭眼) / 素
11      # 侧身(睁眼) / 横
12      # 正面(睁眼正视) / 正面
13      # 转头(扭头无视) / 转头
110     # 笑(人形) / 笑(人形)
111     # 正常(人形) / 素(人形)
117     # 惊讶(人形) / 驚き(人形)

```

在MATERIA中，有一些限制，用于surfaceID的数字是0到8192。



### 字段

##### element[ID],[PaintType],[filename],[X],[Y]

surface的合成。

合成多个图像并将合成结果视为基础表面作为基本图像的合成。

如果有一个名为surface*.Png的图像对应于曲面，如果定义了element0，则原始surface*.Png的内容将被丢弃并替换为element0

在element1之后，在其上顺序合成。

从SSP 2.3.53开始，即使将element定义的surface用作动画部件，它们的行为也像单个图像（以前未定义）。

*的部分（elementID）在同一surface内是一致的，序列号从0开始。

有关PaintType，请参阅下面的绘图方法(PaintType)章节。





##### animation[aID].interval,[interval]

##### [aID]interval,[interval]

定义动画开始的时间（interval）。

请参阅下面的动画间隔了解间隔。 只能通过分隔符枚举来指定仅SSP +组合。

aID的一部分是任意数字。 对于范围内的所有曲面（\ 0，\ 1，...）都是通用的，因此具有相同ID的动画具有相同的含义（例如“blink”，“mouthpak”，“更换相同的衣服”等）到。

区间定义指示该ID的整个动画定义的起点，并且必须首先在一系列动画定义中描述。

有关动画重叠和ID顺序之间的关系，请参阅animation-sort。



##### animation[aID].pattern[pID],[methodType],[surfaceID],[weight],[X],[Y]

##### [aID]pattern[pID],[surfaceID],[weight],[methodType],[X],[Y]

每个动画帧的定义。通常以这样的方式渲染每个帧，使得前一帧被重置并且新合成到基础表面（严格地说，通过绘制方法）。

跟随动画的部分是animationID（与animation[aID].interval的aID相同）。

pattern部分pID是一系列动画。pattern名称中以0开头的序列号。在材料127是最大的。它是从较小的数字中以堆叠的形式绘制的。

有关绘图方法，请参阅下面的绘图方法。

等待时间是绘制帧之前的等待时间。单位是毫秒。只有SSP可写入“最小权重 - 最大权重”，用减号字符分隔，在这种情况下，它是在最小值和最大值之间随机选择的。

X和Y坐标指定帧相对于基线移动的距离（将结果绘制到该帧）。

您可以使用表面ID为-1停止该动画，并停止当前以-2运行的所有其他动画。在任何一种情况下，都会忽略绘图方法，X坐标，Y坐标。



##### animation[aID].option,exclusive

##### [aID]option,exclusive

动画的独占执行选项。

也就是说，当执行具有独占选项的动画时，所有其他动画停止，并且在独占选项的动画结束之前不会重新开始其他动画。

跟随动画的部分是animationID（与动画* .interval的*相同）。

对于具有间隔绑定的动画，此规范未定义。

通过仅设置SSP，动画aID。选项，独占，（1,3,5），排除控制可以仅限于指定ID的动画。



##### animation[aID].option,background

アニメーションの背面実行オプション。

backgroundオプションが指定されたアニメーションはベースサーフェスの後ろ（画面奥側）で実行される。

animationに続く*の部分はanimationID（animation*.intervalの*と同一）。



##### animation[aID].option,[オプション]

exclusiveおよびbackgroundオプションの同時指定。

+区切りで複数オプション可。例：exclusive+background

animationに続く*の部分はanimationID（animation*.intervalの*と同一）。

animation*.option,exclusive+background,(1,3,5) のようにすると、exclusiveのみ影響を受ける。

なおintervalがbindのアニメーションについてはexclusive指定はそもそも未定義である。



##### animation[aID].collision[cID],当たり判定定義

##### animation[aID].collisionex[cID],当たり判定定義(ex)

通常のcollisionやcollisionexのアニメーション動作中限定の定義。インターバルbindにも有効。

animationに続く*の部分はanimationID（animation*.intervalの*と同一）。

collisionに次ぐ*の部分は、一連のanimation*.collision定義内で重複しない番号。



##### collision[cID],[sX],[sY],[eX],[eY],[Tag]

点击判断区域。 封闭区域命名为Tag。

cID是在同一surface内不重叠的序列号。

请参阅碰撞 - 对命中判断重叠和ID顺序之间的关系进行排序。



##### collisionex[cID],[Tag],[Type],[Point1],[Point2]...

对不规则区域的判断。

cID是在同一表面内不重叠的序列号。



Type类型如下:

- rect 矩形。 坐标是起点XY和终点XY。 示例：100,100,200,300

- ellipse 椭圆。 坐标是包围椭圆的矩形，起始点XY和终点XY。 示例：100,100,200,300

- circle 圆。 按照中心点的XY值和半径的顺序进行描述。 示例：100,200,20

- polygon 多边形。 坐标是顶点，可交叉。 示例：100,100,200,300,50,200



##### sakura.balloon.offsetx,[int]

##### sakura.balloon.offsety,[int]

##### kero.balloon.offsetx,[int]

##### kero.balloon.offsety,[int]

##### balloon.offsetx,[int]

##### balloon.offsety,[int]

对话框相对于surface的位置X,Y座標。



通常：对话框的右端和左端与surface的左右端对齐的位置



##### point.centerx,[int]

##### point.centery,[int]

##### point.kinoko.centerx,[int]

##### point.kinoko.centery,[int]

##### point.basepos.centerx,[int]

##### point.basepos.centery,[int]

surface的中心坐标XY



## 动画间隔

在animation[aID].interval中指定动画操作的周期/定时（触发器）的规范。



- sometimes 以每秒1/2的概率播放它

- rarely 以每秒1/4的概率播放它

- random,[value] 以每秒value的概率播放它

- periodic,[value] 定期以数秒的间隔播放

- always 循环播放

- runonce 只播放一次

- never 它不会自动执行。除了通过调用其他动画（如start方法或alternativestart方法）或通过Sakura脚本的\i[*]等指令调用之外不会播放的动画指定它。

- yen-e 在该surface上的\e上运行。

- talk,[value] 在文本显示在气球中时在表面上运行。每当数值字符到来时动画。

- bind 将动画定义为surface的换装动画。



## 绘图类型(PaintType)

animation在模式定义和element定义中组合和绘制每个帧（部分）的方法。



有各种角色方法，如基面替换（base），基面移动（move）和其他动画插入/执行（insert,start,stop,alternativestart,alternativestop）而不是图像合成。



#### 处理换装中的绘图方法

在换装定义中，非图像合成（move、insert、start、stop、alternativestart、alternativestop）的方法无效（视为overlay）。 然而，“base”仅在用于第一“pattern”时才有效，并且可以实现仅在其修整为ON时替换基面的机构。



作为装扮方法实现的“add”和“bind”等同于实现中的“overlay”。 即使你在装扮中指定这三个中的任何一个，它最终也会产生相同的效果。



#### 处理element定义中的绘图方法

在element定义中，非合成图像的方法（“base，move，insert，start，stop，alternativestart，alternativestop”）无效（视为overlay）。



其他装扮方法add和bind也无效（但SSP当前实现中的无效规范将被视为overlay，从而导致指定的绘图）。



显然，第一个element指定的大多数绘图方法（在element[ID],[filename]不存在的情况下）可能与“base”同义。但是，asis方法原样显示透明色是有效的。



当element用作动画部件时，“element”合成的结果将像单个图像一样处理。但请注意，此实现来自SSP 2.3.53，之前未定义。



#### element、动画、换装绘图方法的差异和共同点



合成系统的方法的含义分别在元素，动画和布料变化方面不同。



元素定义旨在获得作为基础表面的单个静止图像。在元素定义中，在合成结果上进一步重复下一个合成直到前一点，并且获得一个静止图像作为最终合成结果。



与元素定义一样，布料更改定义也是获取静止图像的机制，因此绘图方法的解决方案流程与元素定义非常相似。在布料更换图案定义中，第一图案相对于基面合成，并且下一次合成在合成结果上进一步重复直到前一个，并且一个获取静止图像。因此，敷料表现得好像它与基面整合在一起。



由于非换药的正常动画是运动图像表达，因此流程与前两者大不相同。动画的每个模式定义是构成动画的每个帧的定义，并且它们彼此独立。由于每个模式定义组合了基础表面和新图像中的两个以创建新帧，因此在先前模式定义（前一帧）处的合成结果不会影响下一帧。通过一个接一个地渲染新帧，实现了动画表达。



然而，在任何一种情况下，合成方法具有与合成两个图像“要合成的原始图像”和“由图案定义或线的元素定义指定的图像”相同的功能。它有。因此，在Ukadoc，为了方便绘图方法的描述中，被称为新的层到基底层的“目标原始图像的合成”中，“图像由线的图案定义或元素定义中指定”，后者。



换句话说，使用这两个单词中的每一个，动画的每个模式定义通过合成新的层和基础表面作为基础层来创建框架。对于修整和元素合成，作为重复合成新层的结果获得一片静止图像，其中合成结果直到前一个作为基础层。



#### 绘图方法和透明色

图像左上角的一个像素的颜色被处理为透明色，并且通过实际显示器以及用于图案定义的表面和用于元件定义的图像传输相同的颜色部分。



在这种情况下，合成的各个图像的透射颜色的实际颜色不需要特别一致。



此外，一些渲染方法具有透明颜色的特殊处理（overlayfast，asis，interpolate，reduce等）。



### 字段

- **base**

用新图层完全替换基面。 collision也会更新为框架表面上定义的内容。

覆盖该方法的模式通过重新渲染整个表面来实现动画（所谓的翻转卡通）。

在此pattern定义中，指定了此绘制方法，将忽略XY坐标。

在换装和element中，base方法只能用于第一个（element0，pattern0）。 否则它将更改为overlay。



- **overlay**

只需将新图层覆盖在基础图层上即可。

它也可以用作衣服/元素（在敷料，添加，绑定的情况下具有相同的效果）。



- **overlayfast**

根据基础层的不透明度，覆盖新图层。

在基层的半透明部分中，透明度越低，新层合成越暗，如果它是不透明的，则它是完全合成的，如果它是完全透明的，它将根本不结合。

与插值interpolate方法配对的方法。

你也可以使用连衣裙/元素。



- **replace**

用新图层替换部分基础图层。

同时覆盖透明颜色部分和具有透明度信息和半透明的部分，而不留下基础层信息。

你也可以使用连衣裙/元素。



- **interpolate**

根据基础层的透明度重叠新层。

在基层的半透明部分中，透明度越高，合成的新层越深，如果它是完全透明的，则它是完全合成的，如果它是不透明的，它将根本不结合。

与overlayfast方法配对的方法。

你也可以使用连衣裙/元素。



- **asis**

它接近叠加但重叠新图层的透明度（如果设置了pna·或seliko.use_self_alpha，则图像本身的透明颜色和alpha通道）。

你也可以使用连衣裙/元素。

此外，虽然使用asis方法将元素合成曲面组合为其他曲面的动画部分时未显示，但在Windows上，通常透明区域为黑色（＃000000），与图像的原始透明色无关， 它将显示在。



- **move**

基础层移动指定的XY坐标。

在指定此绘图方法的图案定义中，将忽略曲面ID。

敷料·不适用于元素。



- **bind**

使新图层成为装扮的一部分。

这是唯一一种只能将一个表面简单地作为修整部分叠加的方法，现在添加是兼容的。

处理内容与叠加层同义。

动画没有修整·元素的使用是未定义的。



- **add**

复制基础层上的新图层作为替换部件。

处理内容与叠加层同义。

动画没有修整·元素的使用是未定义的。



- **reduce**

基层和新层之间传输的组成。

它乘以基础层和新图层的不透明度（有效透明颜色被视为不透明度0％区域）。

例如，在基层的不透明度为40％且新层的不透明度为60％的区域中，组合后获得不透明度为24％=透明度为76％的区域。

简单地忽略透明度以外的信息（RGB值）。

这是一种准备换衣服的方法，但它也可以用于没有装扮的动画元素。



- **insert,[aID]**

在该位置插入指定ID（动画aID）的修整组（绑定间隔动画）。

例如，在某个敷料A具有位置关系结构的情况下，例如部分地位于另一个敷料变化B的前面和部分后面，在衣服A后面的部分的一部分和前面部分的一部分 通过插入带有插入物的敷料B，我们可以实现自然的前后关系显示。 此时，无论布料更换B的显示/不显示状态如何，都保持显示的完整性。

也可以在插入目的地插入（嵌套）。

这是一种为换衣服而准备的方法，使用不是穿着的动画·元素未定义。



- **start,[aID]**

播放指定ID（动画[aID]）动画的动画。

在指定此绘制方法的图案定义中，将忽略曲面ID，权重和XY坐标。

敷料·不能用于元素。



- **stop,[aID]**

停止指定ID的动画（动画[aID]）。

在指定此绘图方法的图案定义中，将忽略曲面ID，重量，XY坐标。

敷料·不能用于元素。



- **alternativestart,(ID1.ID2...)**

- **alternativestart,[ID1.ID2...]**

播放指定的多个aID之一的动画。

在指定此绘图方法的图案定义中，将忽略曲面ID，重量，XY坐标。

对于SSP，括号为[]，分隔符不是“.”但即使用“,”也可以读取。

敷料·不能用于元素。



- **alternativestop,(ID1.ID2...)**

停止任何指定的多个aID的动画。

在指定此绘图方法的图案定义中，将忽略曲面ID，重量，XY坐标。

对于SSP，括号为[]，分隔符不是“.”但即使用“,”也可以读取。

敷料·不能用于元素。







