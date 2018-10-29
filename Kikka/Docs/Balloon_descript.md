# Balloon——descript.txt
Balloon 的 descript.txt 配置文件说明
原始文档再[这里](http://ssp.shillest.net/ukadoc/manual/descript_balloon.html)
**但是由于技术区别，很多属性并没有实际的意义。经过慎重考虑，决定不使用SSP的balloon的配置字段, 只保留基本信息，样式信息保存在stylesheet.txt中**


#### 概要
Balloon决定了对话框的基本配置


#### 示例
```
charset,utf-8
type,balloon
name,default
id,default
craftman,A.A
craftmanurl,http://ssp.shillest.net/ukadoc/manual/index.html

minimumsize,300,210
clip.width,3,30,10,30
clip.height,3,30,10,30
flipbackground,1
noflipcenter,0
```

#### 字段
##### charset,[String]
- 字符集。 推荐utf-8
- 默认值：utf-8

##### name,[String]
- Shell名称
- **不能省略**

##### id,[String]
- Shell的ID名。 ascii字符，只能是单字节的字母和数字。
- 默认为空

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

##### minimumsize, [int], [int]
- 对话框最小宽的高
- 默认值：背景图片的大小

##### clip.width, [3|5], [int...]
- 横向分割方式，3份或者5份
 - 分成3份时，中间的部分将会被拉伸，其余部分不变 (例如：clipwidth, 3, [30, 10, 30])
 - 分成5份时，第2、4份将会被拉伸，其余部分不变(例如：clipwidth, 5, [30, 10, 100, 10, 30])
- 默认值：分成3等份

##### clip.height, [3|5], [int...]
- 纵向分割方式，3份或者5份
 - 分成3份时，中间的部分将会被拉伸，其余部分不变 (例如：clipheight, 3, 30, 10, 30)
 - 分成5份时，第2、4份将会被拉伸，其余部分不变(例如：clipheight, 5, 30, 10, 100, 10, 30)
- 默认值：分成3等份

##### flipbackground, [0|1]
- 当对话框移出左边屏幕时，会自动移动到shell右边。该设置决定此时是否水平翻转背景图片
- 默认值：0

##### noflipcenter, [0|1]
- 当翻转启用，并且clipwidth和clipheight都为5时。在水平翻转背景图片时不翻转中间部分
- 默认值：0


