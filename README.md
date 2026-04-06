# meishi2csv

Gemini API を利用して、スキャンされた名刺のPDFデータ（日本語・英語・中国語対応）から情報を抽出し、CSV形式で保存するツールです。名刺の表面と裏面を自動的に1つのデータとして統合します。

## 特徴

- 多言語対応: 日本語、英語、中国語の名刺をそのままの言語で認識。
- 表面・裏面の統合: PDFの奇数・偶数ページをペアとして扱い、情報を補完・統合します。
- バイリンガル抽出: 「原語（日本語/中国語）」と「英語」の情報を分けて抽出します。

## セットアップ
1. 依存ライブラリのインストール
```{Bash}
pip install -U google-genai pdf2image
```
2. Poppler の配置

PDFを画像に変換するために [poppler](https://poppler.freedesktop.org/) が必要です。

- Windowsの場合: [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases/) 等からダウンロードし、プロジェクト直下の poppler-25.12.0 ディレクトリに配置してください。
- Mac/Linuxの場合: brew install poppler 等でインストールし、コード内の poppler_path 指定を適宜修正してください。

3. APIキーの取得
Google AI Studio から Gemini API キーを取得してください。取得したキーは環境変数`GEMINI_API_KEY`に設定するか、コマンドラインオプションで指定します。

## 使い方

コマンドラインから以下のオプションを指定して実行します。

```{Bash}
python meishi2csv.py -d [PDFフォルダパス] -o [出力CSV名] -k [APIキー]
```
### オプション
- `-d:` PDFファイルが格納されているディレクトリ（デフォルト: `namecard`）
- `-o:` 出力するCSVファイル名（デフォルト: `business_cards.csv`）
- `-k:` Gemini API キー（環境変数 `GEMINI_API_KEY` に設定されている場合は省略可）

### 抽出項目
出力されるCSVには以下のカラムが含まれます。

|カラム名|説明|
|-------|----|
|original_name|名刺所有者の氏名（原語）|
|English_name|名刺所有者の氏名（英語表記があれば抽出）|
|original_title|肩書（原語）|
|English_title|肩書（英語表記があれば抽出）|
|phone|電話番号|
|email|メールアドレス（複数ある場合はカンマ区切り）|
|original_company|所属組織名（原語）|
|English_company|所属組織名（英語表記があれば抽出）|
|filename|参照元ファイル名|

## 注意事項

- 個人情報保護: 名刺データは個人情報を含みます。APIを利用する際は、Googleのデータ利用規約を確認し、機密保持に十分注意してください。
- スキャン順序: PDF内のページ順が「1ページ目＝表面、2ページ目＝裏面」となっていることを前提としています。

---
Powered by [Gemini](https://gemini.google.com/)
