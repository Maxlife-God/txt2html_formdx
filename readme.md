- 本脚本搭配 [AutoMdxBuilder](https://github.com/Litles/AutoMdxBuilder) 使用，请先下载软件
- 本脚本只对以上软件提供的模板 C 即文本词典进行了适配，其他模板并未进行测试
- 本脚本只是作者为整理日语笔记制作的，因此大部分功能偏向日语词典，如有其他语言需求请自行修改

简易教程：

1. 使用 `css` 文件夹下的 `ctmpl.css` 替换 `AutoMdxBuilder\_internal\lib` 下的同名文件，注意备份源文件

2. 创建一个名为 `input.txt` 文件，在其中编写词典内容。编写规则参考 `txt2html\readme.txt`

3. 运行 `txt2html\txt2html.py`，生成 `index.txt` 和 `syns.txt`

4. 将 `index.txt` 和 `syns.txt` 放入同一个文件夹内，在该文件夹内创建一个名为 `build.toml` 的文件，修改内容为

    ```txt
    [global]
    templ_choice = "C"  # 【重要】选择要应用的模板, 同时需完成下方对应模板的具体配置（如果有的话）
    name = "示例书名"  # 书名
    name_abbr = "SLSM"   # 书名首字母缩写
    simp_trad_flg = false  # 是否需要繁简通搜
    ```

    请确保该文件夹内只有 `index.txt`、`syns.txt` 和 `build.toml` 三个文件，不要出现其他无关文件，否则 AutoMdxBuilder 有概率闪退

5. 运行 AutoMdxBuilder，按照提示输入生成词典对应的 `20` 并回车，输入 `build.toml` 所在文件夹路径并回车

生成的文件会在 AutoMdxBuilder 根目录上一级文件夹中，文件夹名称为 `build.toml` 中 `name` 的值