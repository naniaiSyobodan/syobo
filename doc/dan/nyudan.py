from docx import Document
import tempfile
import subprocess
import os

word_file_path = 'sampleN.docx'
pdf_file_path = 'sampleP.pdf'

#---------------------------------------------------------
def word_to_pdf(word_file, pdf_file):
    # 一時ファイルとしてWordファイルを保存
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
        tmp_file.write(word_file.read())

    result = subprocess.run(["libreoffice", "--version"], capture_output=True, text=True)
    print("stdout:", result.stdout)
    print("stderr:", result.stderr)
    print("return code:", result.returncode)

    # LibreOfficeのコマンドを使用してPDFに変換
    libreoffice_cmd = ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', os.path.dirname(pdf_file), tmp_file.name]
    subprocess.run(libreoffice_cmd)

    # 一時ファイルを削除
    os.unlink(tmp_file.name)
#---------------------------------------------------------



# 既存のWordファイルを開く
doc = Document('sample.docx')

# 書き換えたい段落のインデックスを指定
target_paragraph_index = 0  # 例として最初の段落を選択

# 新しいテキストで置き換える
new_text = "新しい部分"

# 指定したインデックスの段落を取得
paragraph = doc.paragraphs[4]

# 段落のテキストを取得
old_text = paragraph.text

# テキストの一部を置き換える
#　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　年　　月　　日
new_text =    old_text[:29] + "2024" + old_text[31:33] + "03" + old_text[34:36] + "13" + old_text[37:]

print(old_text) 
print(new_text) 
# 段落のテキストを書き換える
paragraph.text = new_text

# Wordファイルを保存
doc.save('sampleN.docx')

with open(word_file_path, 'rb') as word_file:
    word_to_pdf(word_file, pdf_file_path)
