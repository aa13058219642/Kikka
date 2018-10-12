# Shell——descript.txt
Shell 的descript.txt配置文件说明
原文来自[这里](http://ssp.shillest.net/ukadoc/manual/descript_shell.html)，对于意义及作用不明的字段暂不进行翻译。

#### 概要
Shell的基本配置文件。
- 说明Shell名称和作者信息
- 还对对话框的显示位置的设定
- Shell菜单的背景图像设定（右点击菜单）
- 衣服变更所有者 - 菜单的显示设定等

#### 示例

```
charset,Shift_JIS
type,shell
name,master

craftman,ukadog
craftmanw,うか犬
craftmanurl,http://ssp.shillest.net/ukadoc/manual/index.html

menu.background.bitmap.filename,menu_background.png
menu.foreground.bitmap.filename,menu_foreground.png
menu.sidebar.bitmap.filename,menu_sidebar.png

sakura.balloon.offsetx,0
sakura.balloon.offsety,80
kero.balloon.offsetx,-20
kero.balloon.offsety,10
sakura.balloon.alignment,none
kero.balloon.alignment,none

sakura.bindgroup0.name,服,エプロンドレス,apron
sakura.bindgroup1.name,リボン,白リボン,ribbonwhite
sakura.bindgroup2.name,服,黒服,black
sakura.bindgroup3.name,リボン,黒リボン,ribbonblack
sakura.bindgroup0.default,1
sakura.bindgroup1.default,1

kero.bindgroup0.name,ネクタイ,ネクタイ
kero.bindgroup1.name,腕章,黒腕章
kero.bindgroup2.name,腕,ドリル
kero.bindgroup0.default,1
kero.bindgroup1.default,1

sakura.menuitem0,2
sakura.menuitem1,3
sakura.menuitem2,-
sakura.menuitem3,0
sakura.menuitem4,1

kero.menuitem0,0
kero.menuitem1,1
kero.menuitem2,-
kero.menuitem3,2
```

- type, name 必须的
- 在SSP中，可以设置homeurl，进行自动更新
- 对于每个Shell的修改请遵循下面的条款
- 基本机制是将表情名称和表情类别名称（sakura(kero).bindgroup*.name,～）赋值在surfaces.txt和菜单中定义的animationID，在必要时还可以指定位置（sakura(kero).menuitem*,～）
- 以\或％开头的字符串会被认为是脚本或环境变量的标签，并且由于安全风险而被丢弃。 如果想将它们包括为纯字符，则需要将它们转义为\\或\％等。

#### 字段
##### charset,[String]
- 字符集。 推荐utf-8，Shift_JIS。
- 默认值：utf-8


##### name,[String]
- Shell名称
- **不能省略**

##### id,[String]
- Shell的ID名。 ascii字符，只能是单字节的字母和数字。
- 默认为空

##### type,[String]
- Shell 的类列
- 默认为shell, 也可以是其他自定义类型

##### craftman,[String]
- 作者名称（ascii字符，只能是单字节的字母和数字），默认为空

##### craftmanw,[String]
- 作者名称，默认为空

##### craftmanurl,[String]
- 作者个人链接

##### homeurl,[String]
- 更新用连接

##### readme,[String]
- 自述文件名称。在安装或菜单中打开shell描述文本文件名称。
- 默认值：readme.txt

##### menu,hidden
- 若设置该值，则Shell不显示在Shell更换菜单上

##### sakura.name,[String]
- 本体Shell(第0个shell)对应的Ghost的名称
- 默认值：ghost的descript中的设定

##### sakura.name2,[String]
- 本体Shell(第0个shell)对应的Ghost的昵称、别名
- 默认值：ghost的descript中的设定

##### kero.name,[String]
- 使魔Shell(第1个shell)的名字
- 默认值：ghost的descript中的设定

##### char*.name,[String]
- \p[*]的名称，除了本体Shell和使魔Shell之后的的shell的名字
- 默认值：ghost的descript中的设定

##### seriko.zorder,[int,int,...]
- seriko.zorder,スコープID,スコープID,...
- 作用域ID
- [\\![set,zorder,スコープID,スコープID,...]](http://ssp.shillest.net/ukadoc/manual/list_sakura_script.html#_!_set,zorder,スコープID,スコープID,_)のdescript版。タグを実行しなくてもあらかじめ設定できる。

##### seriko.sticky-window,[int,int,...]
- seriko.zorder,スコープID,スコープID,...
- [\\![set,sticky-window,スコープID,スコープID,...]](http://ssp.shillest.net/ukadoc/manual/list_sakura_script.html#_!_set,sticky-window,スコープID,スコープID,_)のdescript版。タグを実行しなくてもあらかじめ設定できる。

##### seriko.alignmenttodesktop,[top|bottom|free]
- 全体のサーフェスのデフォルト※[表示位置情報](http://ssp.shillest.net/ukadoc/manual/descript_shell.html#caption_surfaceposition)。
- [ゴースト側指定](http://ssp.shillest.net/ukadoc/manual/descript_ghost.html#seriko.alignmenttodesktop,位置情報)より優先度が高く、シェル側個別指定（sakura.seriko.alignmenttodesktopなど）より優先度が低い。
- ※ゴースト側全体指定＜ゴースト側スコープ個別指定＜これ＜シェル側スコープ個別指定

##### sakura.seriko.alignmenttodesktop,[top|bottom|free]
- sakura.seriko.alignmenttodesktop,位置情報
- 本体側のデフォルト※[表示位置情報](http://ssp.shillest.net/ukadoc/manual/descript_shell.html#caption_surfaceposition)。
- シェル側全体指定（seriko.alignmenttodesktop）より優先度が高い。すなわち全てのalignmenttodesktop系指定で一番優先度が高い。
- ※ゴースト側全体指定＜ゴースト側スコープ個別指定＜シェル側全体指定＜これ

##### kero.seriko.alignmenttodesktop,[top|bottom|free]
- kero.seriko.alignmenttodesktop,位置情報
- 相方側のデフォルト※[表示位置情報](http://ssp.shillest.net/ukadoc/manual/descript_shell.html#caption_surfaceposition)。
- シェル側全体指定（seriko.alignmenttodesktop）より優先度が高い。すなわち全てのalignmenttodesktop系指定で一番優先度が高い。
- ※ゴースト側全体指定＜ゴースト側スコープ個別指定＜シェル側全体指定＜これ

##### char*.seriko.alignmenttodesktop,[top|bottom|free]
- char*.seriko.alignmenttodesktop,位置情報
- 2人目以降の相方側のデフォルト※[表示位置情報](http://ssp.shillest.net/ukadoc/manual/descript_shell.html#caption_surfaceposition)。
- シェル側全体指定（seriko.alignmenttodesktop）より優先度が高い。すなわち全てのalignmenttodesktop系指定で一番優先度が高い。
- ※ゴースト側全体指定＜ゴースト側スコープ個別指定＜シェル側全体指定＜これ

##### sakura.defaultx,[int]
- 本体Shell(第0个shell)的基准坐标X
- 默认值：ghost的descript设定（如不存在则在中间）

##### sakura.defaulty,[int]
- 本体Shell(第0个shell)的基准坐标Y
- 默认值：ghost的descript设定（如不存在则在中间）

##### sakura.defaultleft,[int]
- 本体Shell(第0个shell)的屏幕坐标X
- 默认值：ghost的descript设定

##### sakura.defaulttop,[int]
- 本体Shell(第0个shell)的屏幕坐标Y
- 默认值：ghost的descript设定

##### kero.defaultx,[int]
- 使魔Shell(第1个shell)的基准坐标X
- 默认值：ghost的descript设定（如不存在则在中间）

##### kero.defaulty,[int]
- 使魔Shell(第1个shell)的基准坐标Y
- 默认值：ghost的descript设定（如不存在则在中间）

##### kero.defaultleft,[int]
- 使魔Shell(第1个shell)的屏幕坐标X
- 默认值：ghost的descript设定

##### kero.defaulttop,[int]
- 使魔Shell(第1个shell)的屏幕坐标Y
- 默认值：ghost的descript设定

##### char*.defaultx,[int]
- 其他Shell的基准坐标X
- 默认值：ghost的descript设定（如不存在则在中间）

##### char*.defaulty,[int]
- 其他Shell的基准坐标Y
- 默认值：ghost的descript设定（如不存在则在中间）

##### char*.defaultleft,[int]
- 其他Shell的屏幕坐标X
- 默认值：ghost的descript设定

##### char*.defaulttop,[int]
- 其他Shell的屏幕坐标Y
- 默认值：ghost的descript设定

##### sakura.balloon.offsetx,[int]
- 本体对话框相对本体Shell的偏移X
- 默认值：ghost的descript設定

##### sakura.balloon.offsety,[int]
- 本体对话框相对本体Shell的偏移Y
- 默认值：ghost的descript設定

##### kero.balloon.offsetx,[int]
- 使魔对话框相对使魔Shell的偏移X
- 默认值：ghost的descript設定

##### kero.balloon.offsety,[int]
- 使魔对话框相对使魔Shell的偏移Y
- 默认值：ghost的descript設定

##### sakura.balloon.alignment,[none | left | right]
- 本体对话框在本体Shell的左侧还是右侧（none自动调整）
- 默认值：ghost的descript設定

##### kero.balloon.alignment,[none | left | right]
- 使魔对话框在使魔Shell的左侧还是右侧（none自动调整）
- 默认值：ghost的descript設定

##### menu.font.name,フォント名
- 用于ownerdrow菜单的字体。
- 默认值：UI标准字体由OS设置

##### menu.font.height,フォントサイズ
用于ownerdrow菜单的字符大小。
UI标准字体高度由OS设置

##### menu.background.bitmap.filename,[String]
背景显示图像文件名。
基础标准图像

##### menu.foreground.bitmap.filename,[String]
前景显示图像文件名。
基础标准图像

##### menu.sidebar.bitmap.filename,[String]
边栏显示图像文件名。
基础标准图像

##### menu.background.font.color.r,[int]
背景文字颜色为红色（0至255）
OS设置的菜单字体颜色

##### menu.background.font.color.g,[int]
背景文字颜色绿色（0至255）
OS设置的菜单字体颜色

##### menu.background.font.color.b,[int]
背景文字颜色蓝色（0至255）
OS设置的菜单字体颜色

##### menu.foreground.font.color.r,[int]
前景文字颜色为红色（0到255）
突出显示OS设置的字符颜色

##### menu.foreground.font.color.g,[int]
前景文字颜色绿色（0到255）
突出显示OS设置的字符颜色

##### menu.foreground.font.color.b,[int]
前景文字颜色蓝色（0到255）
突出显示OS设置的字符颜色

##### menu.separator.color.r,[int]
分色器红色（0到255）
menu.background.font.color.r

##### menu.separator.color.g,[int]
分色器绿色（0到255）
menu.background.font.color.g

##### menu.separator.color.b,[int]
分色器蓝色（0到255）
menu.background.font.color.b

##### menu.disable.font.color.r,[int]
不可选择的字体颜色红色（0到255）
(background(0,0) + menu.background.font.color * 2 ) / 3

##### menu.disable.font.color.g,[int]
不可选择的字体颜色绿色（0到255）
(background(0,0) + menu.background.font.color * 2 ) / 3

##### menu.disable.font.color.b,[int]
不可选择的字体颜色蓝色（0到255）
(background(0,0) + menu.background.font.color * 2 ) / 3

##### menu.background.alignment,[inStringt]
背景图片对齐方式：lefttop、righttop、centertop、leftbottom、rightbottom、centerbottom
lefttop

##### menu.foreground.alignment,[String]
前景图片对齐方式：lefttop、righttop、centertop、leftbottom、rightbottom、centerbottom
lefttop

##### menu.sidebar.alignment,[String]
sidebar图片对齐方式：top、bottom
bottom

##### sakura.bindgroup[int].name,[String],[String],[String]
aID、类别名称、部件名称、缩略图名称
为具有动画aID编号的零件定义类别名称和零件名称。 （主机侧）
动画ID是与surfaces.txt中的动画定义“animation[aID].interval,bind”中的aID对应的数字。
有必要在所有者菜单的衣服更改上显示。
还可以使用Sakura Script的\![Bind,类别名称,部件名称,编号]进行操作。 （仅限SSP）

##### sakura.bindgroup[aID].default,[int]
是否从头开始显示aID动画的换装。 显示为1，不显示为0。 （主机侧）
0

##### sakura.bindgroup*.addid,ID
着せ替えの同時実行設定。アニメーションID*番の着せ替えが有効になった（表示された）時に、addidとして指定した着せ替えも同時に有効にする。カンマ区切りで複数指定可。
同時実行中の着せ替えは、元となった着せ替えが無効になった時点で無効になる。複数の着せ替えのaddidとして同一の着せ替えが同時実行指定されている場合、元となったすべての着せ替えが無効になるまで同時実行指定の着せ替えも無効にならない。(本体側)
動作なし

##### sakura.bindoption[id].group,[Sting],[“”|mustselect|multiple]
optionID、类别名称

设置该Shell类别的选项。 optionID(从0开始)作用不明。
mustselect表示该类别至少选择一个；multiple表示可以多选；不设置则表示可以取消选择
可以分隔多个选项+。
可以取消选择，可多选

その着せ替えカテゴリにオプションを設定。*は単に0から始まる通し番号(本体側)。
mustselectでパーツを必ず1つ選択、multipleで複数のパーツを選択可能。
オプションは+区切りで複数可。
選択解除可能、複数選択不可

##### sakura.menuitem[mID],[aID]
装扮显示该aID动画的装扮更改显示在菜单上的mID位置。 mID序列号是否从0开始。 （主机侧）
如果指定aID为“-”，则在该位置显示分隔线。
没有动作

##### sakura.menu,autoまたはhidden
シェルの本体側の着せ替えメニューの表示。
autoで自動表示、hiddenで非表示。
動作なし（手動設定）

##### kero.bindgroup*.name,カテゴリ名,パーツ名,サムネイル名
アニメーションID*番のパーツにカテゴリ名とパーツ名を定義。(相方側)
アニメーションIDはsurfaces.txtにおけるアニメーション定義の「animation*.interval,bind」の*にあたる数字。
オーナードローメニューの着せ替えに表示するために必要。
Sakura Scriptの\![bind,カテゴリ名,パーツ名,数値]で操作するためにも必要。（SSPのみ）
動作なし

##### kero.bindgroup*.default,数値
アニメーションID*番の着せ替えを最初から表示するか否か。1で表示、0で非表示。(相方側)
0

##### kero.bindgroup*.addid,ID
着せ替えの同時実行設定。アニメーションID*番の着せ替えが有効になった（表示された）時に、addidとして指定した着せ替えも同時に有効にする。カンマ区切りで複数指定可。
同時実行中の着せ替えは、元となった着せ替えが無効になった時点で無効になる。複数の着せ替えのaddidとして同一の着せ替えが同時実行指定されている場合、元となったすべての着せ替えが無効になるまで同時実行指定の着せ替えも無効にならない。(相方側)
動作なし

##### kero.bindoption*.group,カテゴリ名,オプション
その着せ替えカテゴリにオプションを設定。*は単に0から始まる通し番号(相方側)。
mustselectでパーツを必ず1つ選択、multipleで複数のパーツを選択可能。
オプションは+区切りで複数可。
選択解除可能、複数選択不可

##### kero.menuitem*,ID
着せ替えメニュー上の*の位置にそのアニメーションIDの着せ替えを表示。*は0から始まる通し番号。(相方側)
IDの代わりに「-」を指定すると、その位置に仕切り線表示。
動作なし

##### kero.menu,autoまたはhidden
シェルの相方側の着せ替えメニューの表示。
autoで自動表示、hiddenで非表示。
動作なし（手動設定）

##### char*.bindgroup*.name,カテゴリ名,パーツ名,サムネイル名
アニメーションID*番のパーツにカテゴリ名とパーツ名を定義。(3人目以降)
アニメーションIDはsurfaces.txtにおけるアニメーション定義の「animation*.interval,bind」の*にあたる数字。
オーナードローメニューの着せ替えに表示するために必要。
Sakura Scriptの\![bind,カテゴリ名,パーツ名,数値]で操作するためにも必要。（SSPのみ）
動作なし

##### char*.bindgroup*.default,数値
アニメーションID*番の着せ替えを最初から表示するか否か。1で表示、0で非表示。(3人目以降)
0

##### char*.bindgroup*.addid,ID
着せ替えの同時実行設定。アニメーションID*番の着せ替えが有効になった（表示された）時に、addidとして指定した着せ替えも同時に有効にする。カンマ区切りで複数指定可。
同時実行中の着せ替えは、元となった着せ替えが無効になった時点で無効になる。複数の着せ替えのaddidとして同一の着せ替えが同時実行指定されている場合、元となったすべての着せ替えが無効になるまで同時実行指定の着せ替えも無効にならない。(3人目以降)
動作なし

##### char*.bindoption*.group,カテゴリ名,オプション
その着せ替えカテゴリにオプションを設定。*は単に0から始まる通し番号(3人目以降)。
mustselectでパーツを必ず1つ選択、multipleで複数のパーツを選択可能。
オプションは+区切りで複数可。
選択解除可能、複数選択不可

##### char*.menuitem*,ID
着せ替えメニュー上の*の位置にそのアニメーションIDの着せ替えを表示。*は0から始まる通し番号。(3人目以降)
IDの代わりに「-」を指定すると、その位置に仕切り線表示。
動作なし

##### char*.menu,autoまたはhidden
シェルの3人目以降の着せ替えメニューの表示。
autoで自動表示、hiddenで非表示。
動作なし（手動設定）

##### seriko.paint_transparent_region_black,数値
画像の透過色（画像左上の色）になっているにも関わらず、透明度の値では透明でない領域の表示設定。
0の場合は画像本来の色（透過色）を指定の透明度で表示する。
1の場合は画像の色の替わりに黒で塗りつぶされてから指定の透明度で表示する。
例えば0を指定した上で全面真っ白のpnaを用意した画像は、透過色なしで画像のまま表示される。
指定なし（pnaを透明度としている画像では1相当、画像自体のアルファチャンネルを透明度としている画像では0相当の動作になる）

##### seriko.use_self_alpha,数値
数値が1だった場合はpnaでなく画像自体（32bitPNG）のアルファチャンネルを透明度として使用する。
なお、1の場合でもアルファチャンネルを持たない画像についてはpnaが有効。






