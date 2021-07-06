rm output -rfv
mkdir output
./merge.py --policy or \
  'input/[Monolingual] 大辞林 第三版.zip' \
  'input/[Monolingual] 岩波国語辞典 第六版.zip' \
  'input/[Monolingual] 広辞苑 第六版.zip' \
  'input/[Monolingual] 故事ことわざの辞典.zip' \
  'input/[Monolingual] 学研 四字熟語辞典.zip' \
  'input/[Monolingual] 新明解四字熟語辞典.zip' \
  'input/[Monolingual] 故事ことわざの辞典.zip' \
  'input/[Monolingual] Weblio古語辞典.zip' \
  'input/[Monolingual] デジタル大辞泉.zip' \
  'input/[Monolingual] 実用日本語表現辞典.zip' \
  output/hard.zip

./merge.py --policy or \
  'input/[Monolingual] 旺文社国語辞典 第十一版 画像無し.zip' \
  'input/[Monolingual] 明鏡国語辞典.zip' \
  'input/[Monolingual] 新明解国語辞典 第七版.zip' \
  'input/[Monolingual] 新明解国語辞典 第五版.zip' \
  output/normal.zip

./merge.py --policy and output/hard.zip output/normal.zip output/mono.zip
./merge.py --policy or output/mono.zip 'input/[Bilingual] JMdict (English).zip' output/mono_with_fallback.zip

rm -rfv output/mono_with_fallback

unzip output/mono_with_fallback.zip -d output/mono_with_fallback
node --max-old-space-size=32000 ~/Dictionaries/yomi2mobi/dist/app.js --debug -i "output/mono_with_fallback" -o "output/merged" -t "00-merged"
kindlegen "output/merged/00-merged.opf"


# 'input/[Monolingual] 精選版 日本国語大辞典.zip' \ missing readings
# 'input/[Monolingual] ハイブリッド新辞林 v2.zip' \ missing readings
