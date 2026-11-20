# graphpaper

[![CI](https://github.com/eastyou/graphpaper/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/graphpaper/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

给老师和学生用的纸张生成器：方格纸、点阵纸、坐标纸，一条命令输出可直接打印的 A4 页面。**零依赖，不联网，打开就能印。**

打印前不用再找现成的练习本页面，也不必用 Word 一格一格拖表格：选好类型和间距，生成 HTML，按 `Ctrl/Cmd + P` 即可。

## 特性

- **三种纸张**：`grid` 方格纸、`dot` 点阵纸、`coordinate` 坐标纸
- **间距可调**：2~20 毫米，常用 5 毫米（数学作业）和 10 毫米（低年级写字）
- **坐标纸带刻度**：坐标轴居中，每格一个短刻度，每厘米标注数字，原点标 `O`
- **整厘米加深**：每 10 毫米一条略深的辅助线，数格子不费眼
- **A4 精确排版**：页面尺寸 210×297 毫米，12 毫米页边距，打印不缩放
- **多页输出**：一次生成 1~50 页，页脚标注页码
- **参数校验**：类型、间距、页数不合法时给出中文提示，退出码为 2
- **56 个单元测试**：覆盖规格校验、网格几何、坐标刻度与 HTML 输出

## 安装

```bash
pip install graphpaper
```

也可以直接下载源码，在项目目录里运行：

```bash
python -m graphpaper --help
```

## 用法

生成 5 毫米方格纸，打印两页：

```bash
graphpaper --type grid --spacing 5 --pages 2 -o 方格纸.html
```

生成 10 毫米点阵纸：

```bash
graphpaper --type dot --spacing 10 -o 点阵纸.html
```

生成带坐标轴的坐标纸，标题写在页眉：

```bash
graphpaper --type coordinate --spacing 5 --title "函数图像练习" -o 坐标纸.html
```

## 参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--type` | `grid` | 纸张类型：`grid` 方格纸、`dot` 点阵纸、`coordinate` 坐标纸 |
| `--spacing` | `5` | 网格间距，单位毫米，2~20 |
| `--pages` | `1` | 页数，1~50 |
| `--title` | 类型名 | 页眉标题 |
| `-o, --output` | `<类型名>.html` | 输出文件路径 |

## 版面说明

| 纸张 | 内容 |
| --- | --- |
| 方格纸 | 均匀网格，每 10 毫米一条较深的线 |
| 点阵纸 | 只在交点画点，适合画图和做笔记 |
| 坐标纸 | 网格 + 居中的 x/y 轴 + 箭头 + 每格刻度 + 整厘米数字 |

A4 页面可用区域为 186×273 毫米。以 5 毫米间距为例，一页是 37×54 格；10 毫米间距则是 18×27 格。右侧和底部不足一格的余量会留白，不会画出半格。

## 输出

生成一个自包含的 HTML 文件，每页对应一个 A4 区块，屏幕上是灰底白纸预览。

打印时纸张选 A4、方向纵向、边距选「无」，缩放保持 100%。在浏览器里建议开启「背景图形」，网格线才会完整输出。

## 开发

```bash
python -m unittest discover -s tests -v
```

## License

[MIT](LICENSE) © 2026 eastyou
