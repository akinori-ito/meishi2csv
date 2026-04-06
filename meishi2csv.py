import json
import csv
import os
import sys
from google import genai
from google.genai import types
from pdf2image import convert_from_path

sys.path.append("poppler-25.12.0") # poppler のあるディレクトリへのパス


# APIキーの設定
#genai.configure(api_key="AIzaSyCl7ZW7UbbstjhKNBjxlTxz6yFAZKj6Axc")

def process_duplex_pdf(pdf_path):
    # PDFを画像に変換
    pages = convert_from_path(pdf_path, dpi=300, poppler_path="poppler-25.12.0\\Library\\bin")
    
    extracted_results = []

    # 2ページずつステップして処理 (0, 1), (2, 3)...
    for i in range(0, len(pages), 2):
        # 表面と裏面の画像を取得
        front_page = pages[i]
        # 裏面があるか確認（奇数ページで終わるPDF対策）
        back_page = pages[i+1] if (i + 1) < len(pages) else None
        
        prompt = """
        与えられた画像（名刺の表面と裏面）から情報を統合し、1つのJSON形式で出力してください。
        名刺は日本語、英語、または中国語です。名刺に書かれた言語そのままで出力してください。
        項目：original_name, English_name, original_title, English_title, phone, email, original_company, English_company
        それぞれの項目は以下の意味を持ちます。
        - original_name: 名刺所有者の氏名（原語）。原語が英語の場合は英語名。
        - English_name: 名刺所有者の氏名（英語）。原語が英語の場合は original_nameと同じ情報。原語が英語でなく、英語の情報がない場合には空文字列。
        - original_title: 名刺所有者の肩書（原語）。原語が英語の場合は英語名。
        - English_title: 名刺所有者の肩書（英語）。原語が英語の場合は original_titleと同じ情報。原語が英語でなく、英語の情報がない場合には空文字列。
        - phone: 電話番号。
        - email: 電子メールアドレス。複数のアドレスがある場合は、それらをカンマで区切って列挙する。
        - original_company: 名刺所有者の所属組織（原語）。原語が英語の場合は英語名。
        - English_company: 名刺所有者の所属組織（英語）。原語が英語の場合は original_companyと同じ情報。原語が英語でなく、英語の情報がない場合には空文字列。

        ※両方の画像を確認し、より詳細な情報や最新と思われる情報を優先してください。
        JSON以外のテキストは出力しないでください。
        """

        # 画像リストの作成
        content_input = [prompt, front_page]
        if back_page:
            content_input.append(back_page)

        try:
            # Geminiに表面・裏面を同時に投げる
            # 最新の generate_content 呼び出し
            # configでJSON出力を明示的に指定（より確実になります）
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=content_input,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json'
                )
            )
            
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(clean_json)
            data['filename'] = pdf_path
            extracted_results.append(data)
        except Exception as e:
            print(f"解析エラー ({pdf_path}, page {i+1}): {e}")
            
    return extracted_results


pdf_folder = "namecard"
output = "business_cards.csv"

# APIキーの設定
api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    api_key = "SET YOUR API KEY HERE"

i = 1
while i < len(sys.argv):
    if sys.argv[i] == "-d":
        pdf_folder = sys.argv[i+1]
        i += 2
    elif sys.argv[i] == "-k":
        api_key = sys.argv[i+1]
        i += 2
    elif sys.argv[i] == "-o":
        output = sys.argv[i+1]
        i += 2
    else:
        print("Usage: python meishi2csv.py [-d directory] [-o outputfile] [-k key]")
        exit()

client = genai.Client(api_key=api_key)
all_results = []

for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        print(f"処理中: {filename}")
        data_list = process_duplex_pdf(os.path.join(pdf_folder, filename))
        all_results.extend(data_list)

# CSV保存（BOM付きUTF-8でExcel対策）
fields = ["original_name", "English_name",
          "original_title", "English_title", 
          "phone", 
          "email", 
          "original_company", "English_company",
          "filename"]
with open(output, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(all_results)

print(f"全 {len(all_results)} 件のデータを抽出しました。")