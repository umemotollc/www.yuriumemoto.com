import sys
import pandas as pd
import re
import datetime
import unicodedata

member_id = "02374200"   #Web届出ID 8桁
author = "梅本　佑利"   # 著作者
author_kana = "ウメモト　ユウリ"
author_code ="0118858153"  # 著作者コード 10桁

line_counter = 0   # 物理レコード数カウンタ

# 不要な文字を削除し、空白を調整する関数
def clean_alphanumeric(text):
    # 半角大文字A-Z、半角数字0-9、半角空白のみを残す
    cleaned_text = re.sub(r'[^A-Z0-9 ]', '', text)
    # 連続した空白を1つの空白に置換し、先頭と末尾の空白を削除
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text

def remove_non_shift_jis(text):
    # 半角カナを全角に.  Shift_JISにエンコードできる文字だけ残す. 
    text = unicodedata.normalize('NFKC', text)
    try:
        # Ignoreエラーハンドリングでエンコード不可文字を削除
        encoded_text = text.encode('shift_jis', 'ignore')
        # エンコード後にデコードして元の文字列に戻す
        return encoded_text.decode('shift_jis')
    except UnicodeEncodeError as e:
        print(f"エンコードエラーが発生しました: {e}")
        return ""


# Excelデータの読み込み
input_file =  sys.argv[1]   # 入力Excelファイル名
output_file = 'output.jwr'  # 出力ファイル名

dtype={'year': str, 'assign_date': str, 'title': str, 
       'title_alphanumeric': str, 'title_alphanumeric_altered': str, 
       'title_kana': str, 'for': str, 'our_reference': str, 'assign_date': object,
       'subtitle_for_registration': str
       }

# ExcelファイルをDataFrameとして読み込む
df = pd.read_excel(input_file,  dtype=dtype)
df = df[df['jasrac'].isnull()]   # JASRAC作品番号のない作品のみ抽出
df = df.where(df.notnull(), None)       # 欠損値の削除
###df.set_index('our_reference', inplace=True)  #主キーを自社管理番号にセット

# 変換用の関数
def convert_row_to_format(row):
    formatted_data = []
    #global counter
    global line_counter
    
    # 固定のヘッダー情報
    formatted_data.append(f"<START>\t{member_id}\t")
    line_counter += 1

    our_reference = row['our_reference']
    our_reference = our_reference[len(our_reference)-10:]   ## 整理番号（自社管理コード）10桁以内
    formatted_data.append(f"<管理>\t{our_reference}\t\t\t\t\t\t\t")
    line_counter += 1
   
    # 作品コード
    #jasrac_code = row['jasrac'].replace('-', '')  # 作品コードのフォーマット調整
    #formatted_data.append(f"<作品コード>\t{jasrac_code}")
    
    # 作品名
    #title_long = row['title_long'].split("for")[0].strip()  # "for"の前だけ取得
    #registered_name = row['registered_name'].replace('（', '').replace('）', '')  # 全角括弧の削除
    title = remove_non_shift_jis(row['title']).replace("  ", ' ')   # Shift_JISで表現できない文字の削除と、重複したスペースを削除
    title_kana = row['title_kana']   
    title_alphanumeric = clean_alphanumeric(row['title_alphanumeric'])
    
    # 外国語作品名に修正したレコードがあれば上書き
    title_alphanumeric_altered = row['title_alphanumeric_altered']
    if title_alphanumeric_altered: title_alphanumeric = title_alphanumeric_altered
   
    formatted_data.append(f"<作品名>\t{title}\t{title_kana}\t1\t\t\t\t{title_alphanumeric}")
    line_counter += 1

    # 副題
    subtitle = row['subtitle_for_registration']
    if subtitle: 
        subtitle = remove_non_shift_jis(subtitle).replace("  ", ' ') 
        subtitle_kana = row['subtitle_kana']
        formatted_data.append(f"<副題>\t1\t2\t{subtitle}\t{subtitle_kana}")
        line_counter += 1

 
    # 契約情報
    assign_date = row['assign_date'].strftime('%Y%m%d')
    ## formatted_data.append("<契約>\t2\t20221210\t20221210\t20271231\t1\t5\t0")
    #著作権存続期間まで、譲渡地域全世界
    formatted_data.append(f"<契約>\t2\t{assign_date}\t{assign_date}\t\t2\t\t0")
    line_counter += 1


    # 分配率情報
    formatted_data.append("<分配率>\tA\t6/12\t8/8\t8/8\t8/8")
    line_counter += 1

    # 公表情報
    ## formatted_data.append("<公表>\t4\t\t2\t\t202212\t\t\t\t\t\t\t\t0")
    
    # 著作者情報
    formatted_data.append(f"<著作者>\t\tC\t{author}\t{author_kana}\t{author_code}\t0\t")
    line_counter += 1

    # その他
   # formatted_data.append("<その他>\t\t")
   # formatted_data.append("<備考>")
    formatted_data.append("<END>")
#    formatted_data.append(f"<END> {counter} ")
    line_counter += 1
    
    return '\n'.join(formatted_data)


# ヘッダ定義
hdr = "<HDR>"
ver = "003"   # 作品届ファイル(Ver.3以降)

# トレイラー定義
trl = "<TRL>"


counter = 0

# 変換を行い、ファイルに出力
with open(output_file, 'w', encoding='shift_jis', newline="\r\n") as f:
    # ヘッダ
    f.write(f"{hdr}\t{ver}\t{member_id}\t" + '\n')
    # 届出レコード
    for _, row in df.iterrows():
        formatted_text = convert_row_to_format(row)
        f.write(formatted_text + '\n')  # データごとに改行を挿入
        counter += 1
    # トレイラー
    f.write(f"{trl}\t{counter}\t{line_counter + 2}" + '\n')

print(f"データ{counter}行が{output_file}に保存されました.")

