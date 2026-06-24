#!/usr/bin/env python3
"""
日本語版追加 + 言語切替スイッチ + ホームページTip
既存の index.html を更新します。
"""
import re, json, os

OUTPUT = os.path.join(os.path.dirname(__file__), "index.html")

# ─── Markdown → HTML converter ────────────────────────────────────────────────
def inline_md(t):
    t = re.sub(r'\*\*([^*\n]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\*([^*\n]+)\*',     r'<em>\1</em>', t)
    t = re.sub(r'`([^`\n]+)`',       r'<code>\1</code>', t)
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)   # strip links (internal)
    return t

def table_to_html(rows):
    out = ['<div class="table-wrap"><table>']
    first_data = True
    for row in rows:
        if re.match(r'^\|[\s\-|:]+\|$', row):
            continue
        cells = [c.strip() for c in row.strip('|').split('|')]
        if first_data:
            out.append('<thead><tr>' + ''.join(f'<th>{inline_md(c)}</th>' for c in cells) + '</tr></thead><tbody>')
            first_data = False
        else:
            out.append('<tr>' + ''.join(f'<td>{inline_md(c)}</td>' for c in cells) + '</tr>')
    out.append('</tbody></table></div>')
    return '\n'.join(out)

def md_to_html(md):
    lines = md.strip().splitlines()
    out, i = [], 0
    while i < len(lines):
        l = lines[i]
        s = l.strip()
        if s.startswith('#### '):
            out.append(f'<h4>{inline_md(s[5:])}</h4>'); i += 1
        elif s.startswith('### '):
            out.append(f'<h3>{inline_md(s[4:])}</h3>'); i += 1
        elif s.startswith('## '):
            out.append(f'<h2>{inline_md(s[3:])}</h2>'); i += 1
        elif s.startswith('# '):
            out.append(f'<h1>{inline_md(s[2:])}</h1>'); i += 1
        elif s in ('---', '***', '___'):
            out.append('<hr>'); i += 1
        elif s.startswith('| ') or s.startswith('|--'):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                tbl.append(lines[i].strip()); i += 1
            out.append(table_to_html(tbl))
        elif re.match(r'^[-*]\s', s):
            items = []
            while i < len(lines) and re.match(r'^[-*]\s', lines[i].strip()):
                items.append(f'<li>{inline_md(lines[i].strip()[2:])}</li>'); i += 1
            out.append('<ul>' + ''.join(items) + '</ul>')
        elif re.match(r'^\d+[.)]\s', s):
            items = []
            while i < len(lines) and re.match(r'^\d+[.)]\s', lines[i].strip()):
                cell = re.sub(r'^\d+[.)]\s', '', lines[i].strip())
                items.append(f'<li>{inline_md(cell)}</li>'); i += 1
            out.append('<ol>' + ''.join(items) + '</ol>')
        elif not s:
            i += 1
        else:
            para = []
            while i < len(lines):
                ls = lines[i].strip()
                if (not ls or ls.startswith('#') or ls.startswith('|') or
                    re.match(r'^[-*]\s',ls) or re.match(r'^\d+[.)]\s',ls) or
                    ls in ('---','***','___')):
                    break
                para.append(ls); i += 1
            out.append(f'<p>{inline_md(" ".join(para))}</p>')
    return '\n'.join(out)

# ─── 日本語翻訳テキスト（Markdown形式） ───────────────────────────────────────
JA_MD = {}

JA_MD["introduction"] = """
# はじめに

MPC Sample をご購入いただきありがとうございます。

クラシックな MPC60 のデザインにインスパイアされたこのポータブルサンプラーは、ヴィンテージ MPC のアイコニックなワークフローをコンパクトで最新のフォーマットに搭載しています。伝説的な MPC パッド、フルカラーディスプレイ、シンプルなクリエイティブコントロールにより、サンプリング、ループ、ビートメイキングをすぐに始められます。100 以上のキット、Pad FX、Knob FX、直感的なチョッピングワークフローが含まれています。

充電式リチウムイオンバッテリー、microSD カードストレージ、オンボードシーケンサー、内蔵マイク、内蔵スピーカー、USB-C 接続により、コンピュータや DAW なしで、どこでもオーディオの録音・編集・再生が可能です。

## 同梱物

- MPC Sample 本体
- USB-C ケーブル
- クイックスタートガイド
- 安全・保証マニュアル

## サポート

製品について詳しくは **akaipro.com** をご覧ください。

製品登録は **profile.inmusicbrands.com** から行えます。ログインまたはアカウント作成後、「新規製品を登録」を選択してください。

追加サポートは **support.akaipro.com** をご利用ください。

## このユーザーガイドについて

このマニュアルは MPC Sample の使い方を習得するためのガイドです。重要な情報は以下の形式で表記されます。

**重要 / 注意 / ヒント：** 特定のトピックに関する重要または役立つ情報。

ボタン・コントロール・パラメータ名はマニュアル全体で **太字** で表記されます。

関連セクションへの参照は **太字斜体** の青い文字で示されます。クリックするとそのセクションに直接移動できます。
"""

JA_MD["setup"] = """
# セットアップ

本章では MPC Sample の初期設定と他の機器との接続方法について説明します。チュートリアルに進む前に、このセクションを確認することをお勧めします。

MPC Sample のコントロールと接続について詳しくは **Features** 章をご覧ください。

## セクション内容

- Firmware Updates
- Connection Diagram
"""

JA_MD["firmware_updates"] = """
# ファームウェア更新

## はじめに

MPC Sample を初めて使用する前に、利用可能なファームウェア更新を確認することをお勧めします。更新により新機能と改善が追加されます。

## 更新手順

1. 付属の USB-C ケーブルで MPC Sample をコンピュータの USB ポートに接続します。
2. MPC Sample の電源をオンにします。
3. ウェブブラウザで **mpc-sample.local** にアクセスします。

**ヒント：** 接続に問題がある場合は、USB 接続中に MPC Sample を再起動してください。それでも接続できない場合は **192.168.155.1** を試してください。Windows 10 ユーザーは事前に Windows 10 ドライバーをインストールしてください。

4. ページが読み込まれると、現在のファームウェアバージョンが自動スキャンされます。更新がある場合は画面の指示に従って適用してください。
5. **Manual Firmware Upload** をクリックしてファームウェアファイルを手動でアップロードすることもできます。

## 重要な注意

Windows 10 ユーザーは、**akaipro.com/mpc-sample** の MPC Sample ダウンロードページから専用のアップデートアプリをダウンロードしてください。

inMusic Software Center を使用して更新を確認・適用することもできます。

定期的にファームウェア更新を確認することをお勧めします。
"""

JA_MD["connection_diagram"] = """
# 接続ダイアグラム

以下は MPC Sample を他の機器と接続する設定例です。記載されていないアイテムは別途購入が必要です。

各端子の詳細は **Features** 章をご参照ください。

## 接続例

- **AUDIO OUT** → スピーカー / ミキサー
- **AUDIO IN** → マイク / 楽器 / ラインソース
- **PHONES** → ヘッドフォン
- **MIDI IN/OUT** → 外部 MIDI 機器
- **SYNC OUT** → 外部モジュールギア
- **USB-C** → コンピュータ（オーディオ・MIDI・ファイル転送）
"""

JA_MD["tutorial"] = """
# チュートリアル

このチュートリアルでは MPC Sample を使ったビート制作の基本を学びます。ステップは順番に進めることをお勧めします。

## サウンドの再生

1. **POWER** ボタンを押して MPC Sample の電源をオンにします。
2. **MAIN VOLUME** ノブを上げます。
3. **PLAY** ボタンを押してシーケンスを再生します。各サウンドがトリガーされるとパッドが光ります。
4. **STOP** ボタンを押して停止します。

パッドをタップするとサンプルが再生されます（Sample Mode）。**SAMPLE** ボタンでいつでもアクセスできます。

## サンプルの探索

1. パッドをタップし、**SAMPLE SELECT** ボタンを押します。
2. **ENCODER** を回してサンプルフォルダを参照します。
3. **ENCODER** を押してフォルダを開き、サンプルリストを閲覧します。
4. 新しいサンプルを選択して **ENCODER** を押してパッドにロードします。
5. **SAMPLE SELECT** を再度押して Sample Mode に戻ります。

## シーケンスの再生

1. **SEQ** ボタンを押して Sequence Mode を開きます。
2. **PLAY** ボタンを押して再生を開始します。
3. 再生中に別のパッドをタップするとそのシーケンスがキューイングされます。
4. **STOP** ボタンで停止します。

## シーケンスの録音

1. 空のパッドをタップして選択します。
2. **B1** ボタンを押し続けて Sequence BPM ウィンドウを開き、**ENCODER** で BPM を調整します。
3. **B3** ボタンで Record Quantization のオン/オフを切り替えます。
4. **K2** ノブで Q 値、**K1** ノブでシーケンス長をバー単位で調整します。
5. **SEQ RECORD** ボタンを押して録音準備完了にします。
6. **PLAY** ボタンで録音開始、パッドをタップしてイベントを追加します。
7. **SEQ RECORD** で録音停止、**STOP** で再生も停止します。

## 新規プロジェクトの開始

1. **SHIFT** を押し続けながら **PAD 16 – PROJECT** を押します。
2. **ENCODER** で「New Project」を選択して押します。
3. 確認メッセージで **B3** ボタンを押して実行します。

## サンプルの録音

1. **SAMPLE RECORD** ボタンを押して Sample Record Mode に入ります。
2. **K1** ノブで入力ソースを「Mic」に設定します。
3. パッドをタップして録音開始します。
4. 完了後、パッドをもう一度タップして停止します。

## サンプルの編集

1. **SAMPLE** ボタンを押して Sample Mode を確認します。
2. 編集するサンプルのパッドをタップします。
3. **K1** ノブで **Start** ポイント、**K2** ノブで **End** ポイントを調整します。
4. パッドをタップして新しい範囲で再生確認します。
5. **SHIFT** を押しながら **PAD 13 – TRIM SAMPLE** でサンプルを永続的に短縮できます。
6. **B1, B2, B3** で編集オプションを切り替え、**K1, K2, K3** で各パラメータを調整します。

## エフェクト（FX）の使用

### Pad FX モード

1. **PAD FX** ボタンを押して Pad FX Mode を開きます。
2. **PLAY** でシーケンス再生開始します。
3. パッドをタップ＆ホールドしてエフェクトをトリガーします。
4. **K1–K3** ノブでエフェクトパラメータを調整します。

### Knob FX モード

1. **KNOB FX** ボタンを押して Knob FX Mode を有効化します。
2. **SEQ** ボタンで Sequence Mode、**PLAY** で再生開始します。
3. **K1–K3** ノブでエフェクトを調整します。
4. **SHIFT + KNOB FX** ボタンで別のエフェクトを選択します。

### Flex Beat モード

1. **SHIFT + PAD FX / FLEX BEAT** ボタンを押します。
2. **PLAY** でシーケンス再生開始します。
3. **PADS 2–16** を押してエフェクトをトリガーします。
4. **PAD 1** を押すと Empty エフェクト（変更なし）に戻ります。
"""

JA_MD["features"] = """
# 機能説明

本章では MPC Sample の各接続端子とコントロールの機能を説明します。

## POWER

電源ボタン。押して MPC Sample の電源をオン/オフします。

## USB

付属の USB-C ケーブルで USB-C 電源アダプタまたはモバイルバッテリーに接続して電源供給・充電ができます。コンピュータの USB-C ホストポートに接続するとオーディオ・MIDI 信号の送受信と microSD カードのファイル転送も可能です。

## REC GAIN

このノブを回して AUDIO IN 接続の録音レベルを調整します。

## AUDIO IN

1/4"（6.35mm）TRS 入力。マイク・楽器・ミキサー・シンセサイザーなどのラインレベルオーディオソースを接続します。

## AUDIO OUT

1/4"（6.35mm）TRS 出力。スピーカー・ミキサーなどに接続します。MAIN VOLUME コントロールで出力レベルを調整します。

## MIDI IN / OUT

1/8" TRS（Type A）→ 5-Pin MIDI DIN コネクタ（別売）経由でドラムマシンやシンセサイザーなどの外部 MIDI 機器を接続します。

## SYNC OUT

5V CV 出力（1/8"、TS）。外部モジュールギアを同期させるクロックパルスを送信します。

## PHONES

標準的なヘッドフォンを接続して MPC Sample のオーディオをモニターします。MAIN VOLUME で音量を調整します。ヘッドフォン接続時は内蔵スピーカーが無効になります。

## microSD Card Slot

microSD カードを挿入して外部ストレージとして使用します。Project メニューの SD Card Access から管理できます。

## Display

利用可能なメニューやパラメータを表示します。

## Battery Icon

現在のバッテリーレベルを表示します。緑 = 100〜30%、琥珀 = 29〜15%、赤 = 14〜5%。点滅赤は 5% 未満で、すぐに充電が必要です。

## Charging Icon

充電中に点灯します。

## MAIN VOLUME

オーディオ出力レベルを調整します。内蔵スピーカー・PHONES・AUDIO OUT すべてに適用されます。

## Meters

メイン出力ボリュームレベルまたはサンプル録音時の入力ソースレベルを表示します。

## Speaker

内蔵スピーカー。PHONES または AUDIO OUT に何も接続されていない場合にオーディオを再生します。

## Microphone

内蔵コンデンサーマイク。簡単にサンプリングできます。

## SHIFT

二次機能へのアクセスボタン。押し続けながら別のボタンやパッドを押して二次機能にアクセスします。

## Encoder

回してメニューを操作・設定を調整します。押して選択・確定します。

## -/+

選択したパラメータを増減、またはリストを上下に移動します。

## B1, B2, B3 Function Buttons

ディスプレイのページを切り替えたり、特定の機能を有効にするボタンです。

## K1, K2, K3 Knobs

ディスプレイに表示される各種設定やパラメータを調整するノブです。

## Fader

各種パッドおよびキットパラメータを調整します。デフォルトではパッドボリュームを調整します。

## ERASE

サンプル・シーケンス・イベント・オートメーションを消去します。

## NOTE REPEAT

Note Repeat モードを有効にします。有効時、パッドを押すと設定された時間分割で繰り返し音が出ます。

## PAD BANK

パッドバンク A〜H を切り替えます。

## SAMPLE SELECT

サンプルブラウザを開いて、現在のパッドに割り当てるサンプルを参照・選択します。

## TAP TEMPO

一定間隔でタップして新しいプロジェクトテンポを設定します。

## Pads

16 個のベロシティセンシティブ・ポリアフタータッチ対応パッド。サンプルとシーケンスのトリガーや各種機能の実行に使用します。

## Mode ボタン

### SAMPLE
Sample Mode を開きます。サンプルのトリガーとパラメータの表示・編集ができます。

### SEQ
Sequence Mode に入り、ノートイベントのシーケンスを録音・編集します。

### PAD FX
Pad FX Mode を有効化します。パッドを使用してシーケンス全体にエフェクトをトリガーします。

### KNOB FX
Knob FX Mode を有効化します。K1〜K3 ノブで特定のエフェクトパラメータをコントロールします。

## Pad Play ボタン

### CHOP
Chop Mode を有効化します。選択したパッドのサンプルが自動的に分割され、各パッドがスライスをトリガーします。

### LOOP
現在のパッドのループ再生を有効化します。

### MUTE
Sample Mode 内でパッドのミュートモードを有効化します。

### 16 LEVELS
現在選択されたサンプルが 16 パッドすべてにコピーされ、選択パラメータが各パッドで段階的に変化します。

### SAMPLE RECORD
Sample Record Mode に入ります。接続されたソースからオーディオを録音して独自のサンプルを作成できます。

### SEQ RECORD
Sequence Record Mode に入ります。

### PLAY
シーケンスの再生または録音を開始します。

### STOP
再生または録音を停止します。ダブルクリックですべてのオーディオが停止します。
"""

JA_MD["operation"] = """
# 操作

本章では MPC Sample の各モード・機能・メニューについて説明します。

特定のコントロールや接続の詳細については前章の **Features** をご参照ください。

## セクション内容

- Sample Mode
- Sample Record Mode
- Sequence Mode
- Effects
- Menus
"""

JA_MD["sample_mode"] = """
# Sample Mode

Sample Mode は MPC Sample のメインモードです。サンプルをトリガーし、パラメータを表示・編集できます。

**SAMPLE** ボタンを押して Sample Mode を開きます。

**PAD** を押してトリガーし、ディスプレイでサンプルを確認します。

トリガーせずにサンプルを選択・表示するには、**SAMPLE** ボタンを押しながら **PAD** を押します。

**K1–K3** ノブで以下のパラメータを選択・調整します。または **ENCODER** を押してパラメータを循環させ、**ENCODER** を回すか **-/+** ボタンで調整します。

**SHIFT + B1** でループロックのオン/オフ。**SHIFT + B2** でノーマライズを適用します。

## Trim（B1）

サンプルの長さを編集します。

- **K1 – Start：** サンプル開始点（0–100%）
- **K2 – End：** サンプル終了点（0–100%）
- **K3 – Loop：** ループポイント（0–100%）
- **SHIFT + K1/K2/K3：** 各ポイントのズーム

## Mix

ミックス設定を調整します。

- **K1 – Volume：** サンプルボリューム（-INF〜+6.00 dB）
- **K2 – Kit Volume：** キット全体のボリューム
- **K3 – Pan：** ステレオパン（50L〜C〜50R）

## Amp Env

振幅エンベロープを調整します。

- **K1 – Attack：** アタック段階（0–127）
- **K2 – Decay/Release：** デケイ/リリース段階（0–127）
- **K3 – Vel Sens：** ベロシティ感度（0–127）

## Tune（B2）

ピッチチューニングを調整します。

- **K1 – Semi Tune：** 半音単位のチューニング（-24〜+24）
- **K2 – Fine Tune：** セント単位のチューニング（-90〜+90）
- **K3 – Warp：** ワープ値（Off、50–200%、Seq）

## Play

再生機能を調整します。

- **K1 – Polyphony：** Mono / Poly 選択
- **K2 – Mute Group：** ミュートグループ割り当て（Off、1–16）
- **K3 – Offset：** トリガーオフセット（0–100%）

## Filter（B3）

フィルター設定を調整します。

- **K1 – Cutoff：** フィルター中心周波数（0–127）
- **K2 – Reso：** フィルター共鳴（0–127）
- **K3 – Type：** フィルタータイプ（Off、Classic、LPF2/4、HPF2/4、BPF2/4）

## Filt Env

フィルターエンベロープを調整します。

- **K1 – Attack：** アタック段階（0–127）
- **K2 – Decay/Release：** デケイ/リリース段階（0–127）
- **K3 – Depth：** エンベロープ影響度（0–127）
"""

JA_MD["pad_play"] = """
# Pad Play

Sample Mode 中に **PAD PLAY** ボタンを使用してサンプルの追加再生機能を有効にできます。**MUTE** 機能はどのモードでもアクセス可能です。

## Chop

**CHOP** ボタンを押して Chop Mode を有効にします。サンプルが自動的にスタート〜エンドポイント間で現在の Chop Type に基づいて分割されます。

### Chop Mode コントロール

- **K1 – Start：** スライス開始ポイント（0–100%）
- **K2 – End：** スライス終了ポイント（0–100%）
- **K3 – Chop Type：** Threshold / Regions 4/8/16 / Manual

### 編集機能

- **SHIFT+B1：** 現在のスライスを抽出
- **SHIFT+B2：** スライスを2分割
- **SHIFT+B3：** 前のスライスとマージ
- **ERASE + PAD：** スライスを削除

## Note On

**SHIFT + CHOP** で有効化。パッド押下中のみサンプルが再生されます。

## Loop

**LOOP** ボタンで有効化。Sample End ポイントに達すると Loop Start ポイントに戻って繰り返します。

LOOP LOCK がデフォルトで有効（Sample Start を Loop Start にロック）。**SHIFT+B1** で解除可能です。

## Reverse

**SHIFT + LOOP** で有効化。サンプルが逆方向（End→Start）で再生されます。

## Mute

**MUTE** ボタンで有効化。赤く点灯 = ミュート中、黄色く点灯 = ミュート解除中。

**SHIFT + MUTE** でパッド全体をアンミュートします。

## 16 Levels

**16 LEVELS** ボタンで現在のパッドのサンプルが 16 パッドすべてにコピーされ、選択パラメータが段階的に変化します。

**SHIFT + 16 LEVELS** で 16 Levels タイプを切り替えます（Velocity / Filter / Tune）。
"""

JA_MD["loading_and_saving_samples"] = """
# サンプルのロードと保存

## サンプルのロード

**SAMPLE SELECT** ボタンを押してサンプルブラウザを開きます。

**ENCODER** を回すか **-/+** ボタンでサンプルカテゴリのリストを参照します。

**ENCODER** を押してフォルダを開き、サンプルリストを参照します。

**B3** で自動 **Preview** のオン/オフを切り替えます（オン時、ハイライトされたサンプルが自動再生されます）。

**B1** で前のフォルダに戻ります。

**B2** で内蔵ドライブと外部 microSD カードを切り替えます（カードが挿入されている場合）。

## サンプルの保存

**SHIFT + SAMPLE SELECT / SAVE SAMPLE** ボタンを押します。

**ENCODER** を回して文字・数字を選択します。**ENCODER** を押して次の文字に進みます。

**SHIFT** を押しながら大文字にアクセスできます。

**-/+** ボタンで文字間を移動します。

**B2** で現在の文字を削除。**SHIFT + B2** で全文字を一度に削除します。

編集完了後、**B3（Do It!）** を押して保存します。**B1（Cancel）** でキャンセルします。
"""

JA_MD["sample_record_mode"] = """
# Sample Record Mode

MPC Sample の内蔵サウンドに加えて、Sample Record Mode を使用して独自のサウンドを録音できます。

## 開き方

**SAMPLE RECORD** ボタンを押して Sample Record Mode を開きます。

## オーディオモニタリング設定

**B1** ボタンを押してモニタリングを切り替えます。

- **Off：** モニタリングなし
- **Auto：** Sample Record Mode がフォーカス中のみモニタリング
- **On：** 常にモニタリング

## 入力ソースの選択（K1 ノブ）

- **Mic：** 内蔵マイク
- **Rear：** リアパネルの AUDIO IN（ステレオ）
- **Rear L / Rear R：** 個別チャンネル
- **Resample：** MPC Sample からの再録音
- **USB / USB L / USB R：** USB 接続デバイスのオーディオ

## 録音長の設定（K2 ノブ）

- **Free：** 無制限
- **Seq：** 現在のシーケンス長

## Threshold（K3 ノブ）

録音開始のトリガーレベルを設定します。

## 録音の開始と停止

録音したいパッドをタップして録音開始。録音中に追加のパッドをタップするとサンプルを分割できます。

停止方法：
- PAD を再度押す（Sample Record Mode に留まる）
- **STOP** ボタンを押す
- **SAMPLE RECORD** ボタンを押す（Sample Mode に自動遷移）

## Tips

**SHIFT + SAMPLE RECORD / RECALL** ボタンを長押しすると、過去 25 秒のオーディオを取得して次の空きパッドに自動配置できます。
"""

JA_MD["sequence_mode"] = """
# Sequence Mode

シーケンスは MPC Sample で音楽制作する際の基本要素です。一定時間にわたるノートパターンを含み、verse 用・chorus 用など複数のバリエーションを作成できます。

## 開き方

**SEQ** ボタンを押して Sequence Mode を開きます。

## 基本操作

**ENCODER** を回してプレイヘッド位置をビート単位で調整します。**SHIFT + ENCODER** で現在の Q 値単位で調整します。

## BPM コントロール

**B1** を押し続けて Sequence BPM ウィンドウを開きます。**ENCODER** で BPM を調整します。

**B2** で SEQ（個別）または GBL（全体共通）の BPM 制御を切り替えます。

## Record 設定

**B3：** Record Quantization のオン/オフ

## 長さ・グリッド設定

- **K1 ノブ：** シーケンス長（1–128 バー）
- **K2 ノブ：** Q（Quantization）値
- **SHIFT + K2：** 拍子記号を調整

## リズムコントロール

**K3 ノブ：** RT Swing 値（ノートのリアルタイム位置調整）

## メトロノーム

**SHIFT + TAP TEMPO / METRONOME：** Off / On / Record で切り替えます。

**SHIFT + PAD 4 – COUNT-IN：** カウントイン機能のオン/オフ

## シーケンスの選択と再生

**PAD** を押してシーケンスを選択します。ノートイベントを含むシーケンスは薄い緑、空のシーケンスは暗く表示されます。

**PLAY** を押して再生開始。再生中に別のパッドを押すと、現在のシーケンス終了後に次のシーケンスが再生されます。

## 関連セクション

- Recording Sequences
- Editing Sequences
- Step Edit
- Song Mode
"""

JA_MD["recording_sequences"] = """
# Recording Sequences

## 基本的な録音手順

1. Sequence Mode で、暗く光っている空のパッドをタップして選択します。
2. 録音前に BPM・Length・Record Quantization などを調整できます。
3. **SEQ RECORD** ボタンを押して録音準備完了状態にします（ボタンが点滅）。
4. **PLAY** ボタンを押して録音開始、パッドをタップしてイベントを追加します。
5. シーケンス終端に達すると自動的にオーバーダブ録音に切り替わります。
6. 完了後、**SEQ RECORD** を再度押して停止、または **STOP** で完全停止します。

## 編集機能

- **SHIFT + -/UNDO：** 最後の録音以降のすべてのイベントを取り消します。
- **ERASE ボタン長押し + PAD：** そのパッドのすべての録音イベントを消去します。
- **SHIFT + SEQ RECORD / RECALL：** 前回のループで再生されたイベントを取得します。

## パラメーターオートメーションの録音

1. 対象のパッドを選択し、**SEQ RECORD** で録音準備します。
2. **PLAY** で録音開始後、**K1–K3 ノブ**または **FADER** を操作してパラメーターを調整します。
3. Volume・Tuning・Pan・Amp Env・Filter Env・Velocity Sensitivity・Offset のオートメーションが録音できます。

## オートメーションの消去

パッドを選択後、**ERASE** を押しながら対応する **K1–K3 ノブ**を動かすと確認メニューが表示されます。**B3** で実行、**B1** でキャンセルです。
"""

JA_MD["editing_sequences"] = """
# Editing Sequences

現在のシーケンスに対して、**SHIFT** を押しながら以下の **PADS** を押します。

- **PAD 2 – Half Seq：** シーケンスの長さを半分に短縮します（例：4 バー → 2 バー）。
- **PAD 3 – Double Seq：** シーケンスの長さを 2 倍にし、すべての録音イベントを複製します（例：4 バー → 8 バー）。
- **PAD 6 – Half Speed：** すべてのイベントを半速で再生します（例：1/8 音符 → 1/4 音符）。
- **PAD 7 – Double Speed：** すべてのイベントを 2 倍速で再生します（例：1/8 音符 → 1/16 音符）。
- **PAD 10 – Rec Quantize：** Record Quantization のオン/オフ。録音イベントを現在の時間分割グリッドにスナップします。
- **PAD 11 – Resample：** 現在のシーケンスを新しいサンプルとしてキャプチャします。選択後、追加先のパッドを押してください。
- **PAD 12 – Song：** Song Mode に入り、複数のシーケンスを組み合わせて曲を作成・エクスポートできます。
- **PAD 14 – Time Correct：** Time Correct メニューに入り、シーケンス内のイベントを調整・クオンタイズします。
"""

JA_MD["step_edit"] = """
# Step Edit

Step Edit ページでは、シーケンス内の個別イベントをステップごとに編集できます。

## 開き方

**SHIFT + SEQ / STEP EDIT** ボタンを押します。

## 操作方法

- **ENCODER：** 現在の Q 値でシーケンスの各ステップ間を移動します。
- **-/+ ボタン：** 現在のステップ上のイベント間を移動します。対応するパッドをタップしてイベントを選択することもできます。
- **FADER：** 選択したイベントのタイミングを調整し、前後にずらします。
- **K1 ノブ：** シーケンス長を調整します。
- **K2 ノブ：** Q（Quantization）値を調整します。
- **K3 ノブ：** 選択したイベントのベロシティを調整します。
- **SHIFT + K2：** プロジェクトの拍子記号を調整します。

**注：** すべてのシーケンスは同じ拍子記号に結びついています。

- **B1 + ENCODER：** シーケンステンポを調整します。ENCODER を押して整数と小数の間を移動します。
- **B3：** 選択したイベントを消去します。
- **ERASE + PAD：** そのパッドのすべてのイベントを消去します（B1 でキャンセル、B3 で実行）。
"""

JA_MD["song_mode"] = """
# Song Mode

Song Mode では、複数のシーケンスをリスト形式で並べて曲を作成し、オーディオファイルとしてエクスポートするか、プロジェクト内の新しいシーケンスとして保存できます。

## 開き方

**SHIFT + PAD 12 – SONG** を押します。

## シーケンスの選択

**PADS** を使用してシーケンスを選択します。既存のシーケンスは明るく点灯、空のシーケンスは暗く表示されます。

## シーケンスの挿入

**B3** を押して現在の位置にシーケンスを挿入します。**ENCODER** または **-/+** で挿入済みシーケンスのリストを参照できます。

## シーケンスの削除

削除したいシーケンスをハイライトして **B2** を押します。

## 再生

- **PLAY：** ソングを最初から再生します。
- **SHIFT + PLAY / CONTINUE：** ハイライトされたシーケンスから再生を開始します。

## エクスポート

**B1** を押してエクスポートオプションを選択します。

### オーディオミックスダウン
**B2** でオーディオファイルとして保存します。名前を編集後、**B3（Do It!）** でエクスポート開始します。

### 新規シーケンスとして保存
**B3** を押すと新しいシーケンスとして保存されます。128 バーを超える場合、作成後の長さ編集はできません。
"""

JA_MD["effects"] = """
# エフェクト

MPC Sample には 4 つの異なるエフェクトエンジンが搭載されており、ビートを次のレベルへ引き上げることができます。

## Pad FX

パッドを使用してシーケンス再生中にエフェクトをトリガーします。16 種類のエフェクトが利用可能で、パッドに加える圧力が強いほどエフェクトが強くかかります。

## Flex Beat

パッドが時間ベースのエフェクトをトリガーし、シーケンスのピッチ・タイム・ボリュームを変形させます。ビートチョップ・DJスタイルのスクラッチ・トランスゲートエフェクトを実現します。

## Knob FX

K1〜K3 ノブで単一のエフェクトパラメータをコントロールします。パッドでサンプル・シーケンスをトリガーしながら、パフォーマンス中にエフェクトを組み込みたい場合に最適です。

## Compressor

内蔵コンプレッサーを適用・調整してサウンドにパンチを加えます。
"""

JA_MD["pad_fx"] = """
# Pad FX

MPC Sample の Pad FX により、シーケンス再生中にパッドでエフェクトをトリガーできます。

**PAD FX** モードボタンを押して開きます。

**PADS 1–16** を押してエフェクトをトリガーします。圧力が強いほどエフェクトが強くかかります。最大 4 つのエフェクトを同時使用できます。

**K1–3 ノブ**でエフェクトパラメータを調整します。

**B1** でエフェクトを現在の量で **Latch**（ラッチ）できます。

## エフェクト一覧

| Pad | エフェクト | 説明 | K1 | K2 | K3 |
|-----|-----------|------|----|----|-----|
| 1 | Half Speed | 低速再生 | Speed | Mix | — |
| 2 | Chorus | きらめくピッチ変調 | Rate | Depth | Feedback |
| 3 | Flanger | 「シュー」という変調音 | Rate | Depth | Feedback |
| 4 | Phaser | 鋭い「スウープ」音 | Feedback | Speed | Range |
| 5 | Comb Filter | スペクトラムにノッチを生成 | Speed | — | — |
| 6 | LP Filter | カットオフ以上の周波数を抑制 | Resonance | Speed | Range |
| 7 | HP Filter | カットオフ以下の周波数を抑制 | Resonance | Speed | Range |
| 8 | BP Filter | カットオフ以上・以下を抑制 | Resonance | Speed | Range |
| 9 | Ring Mod | 金属的なパルス音 | Max Freq | — | — |
| 10 | LoFi | ロー・ファイ音生成 | Bitcrush | Decimator | — |
| 11 | Color | ビンテージ機器の音をエミュレート | Mode | — | — |
| 12 | Granulator | グレイン合成 | Density | Feedback | Grain Len |
| 13 | Beat Repeat | スタッタリングループ | Division | Reverse | Resonance |
| 14 | Rev Stepper | スライス&リピート | Delay Time | Repeats | — |
| 15 | Delay | エコーリピート | Time | Feedback | Range |
| 16 | Reverb | 空間残響 | Pre-Delay | Decay | Diffusion |
"""

JA_MD["flex_beat"] = """
# Flex Beat

Pad FX と同様にパッドでエフェクトをトリガーしますが、時間ベースのエフェクトでシーケンスのピッチ・タイム・ボリュームを変形させます。ビートチョップ・DJスクラッチ・トランスゲートエフェクトを実現します。

## 開き方

**SHIFT + PAD FX / FLEX BEAT** ボタンを押します。

使用前に **PLAY** ボタンを押してシーケンスを再生してください。

デフォルトでは **PAD 1**（EMPTY エフェクト）がアクティブです。

**PADS 2–16** を押してエフェクトをトリガーします。

## コントロール

- **B3：** Quantize のオン/オフ
- **K1：** One Shot / Loop の切り替え
- **K3：** ドライ/ウェット Mix（0–100%）
"""

JA_MD["knob_fx"] = """
# Knob FX

MPC Sample の Knob FX では、K1–3 ノブを使用して単一のエフェクトパラメータをコントロールします。パッドを他の用途に使いながらエフェクトを操作できます。

## 操作方法

**KNOB FX** ボタンを押して有効化します。ディスプレイ下部に K1–K3 で制御可能なパラメータが表示されます。

**SHIFT** を押しながら追加パラメータにアクセスできます。

無効化するには **KNOB FX** ボタンを再度押します。

## 設定調整

**SHIFT + KNOB FX** で設定を調整します。特定のパッドまたは全パッドに適用できます。

- **B2：** 全パッドで有効化
- **B3：** 全パッドで無効化

## エフェクト選択

**ENCODER** を回すか **-/+** でリストを参照し、**ENCODER** を押して選択します。

## エフェクト一覧（主要）

| エフェクト | K1 | K2 | K3 |
|-----------|----|----|-----|
| Delay | Time | Feedback | Mix |
| Diff Delay | Time | Feedback | Mix |
| Tape Delay | Time | Feedback | Mix |
| Reverb Small/Med/Large | Pre-Delay | Time | Mix |
| Spring Reverb | Pre-Delay | Time | Mix |
| HP Filter | Frequency | Resonance | — |
| LP Filter | Frequency | Resonance | — |
| BP Filter | Frequency | Resonance | — |
| Bus Compressor | Attack | Release | Threshold |
| Limiter | Gain | Ceiling | Release |
| Pumper | Speed | Shape | Depth |
| Transient | Attack | Shape | Sustain |
| Noise Gate | Threshold | Depth | — |
| Amp Sim | Cab Model | Drive | Soft Clip |
| Tube Drive | Drive | Headroom | Saturation |
| Soft Clipper | Drive | Shape | Mix |
| Ensemble | Rate | Depth | Mix |
| Multi-Chorus | Rate | Depth | Mix |
| Phaser | Rate | Depth | Mix |
| Flanger | Rate | Depth | Mix |
| Auto-Wah | Sens | Resonance | Mix |
| Auto-Pan | Rate | — | Mix |
| Vintage Emulator | Type | — | — |
| Vinyl Emulator | Tone | Crackle | Pitch |
| Tape Emulator | Wow | Noise | Pitch |
"""

JA_MD["compressor"] = """
# Compressor

Compressor エフェクトは信号のダイナミックレンジを変更し、一定レベルを超えた場合に自動的にゲインを低減します。

## アクセス方法

**SHIFT + PAD 5 – COMPRESSOR** を押して開きます。

## 機能ボタン

- **B1：** Color エフェクトのオン/オフ。有効時、ベースブースト・ピッチ不安定性・ハーモニック飽和による「テープウォーミス」効果が加わります。
- **B3：** コンプレッサーのバイパス/有効化。

## ノブコントロール

- **K1 – Attack：** コンプレッサーのアタックフェーズ（0.100–150 ms）。信号がしきい値を超えた後、圧縮を開始するまでの時間。
- **K2 – Release：** リリースフェーズ（3.0–300 ms）。信号がしきい値以下に低下した後、圧縮を停止するまでの時間。
- **K3 – Amount：** 圧縮量（0.00–100.00%）。
- **SHIFT + K3 – In Boost：** コンプレッサーへの入力音量を増加させます。

Makeup gain は入力レベルと全体的なパラメータ設定に基づいて自動計算されます。
"""

JA_MD["menus"] = """
# メニュー

本章では MPC Sample で使用される追加メニューについて説明します。デバイス設定やファイル管理などに関連する機能が含まれています。

## セクション内容

- Input Configuration（入力設定）
- Fader
- Time Correct（タイムコレクト）
- MIDI Configuration（MIDI 設定）
- Project（プロジェクト）
"""

JA_MD["input_configuration"] = """
# 入力設定（Input Configuration）

サンプリング用のオーディオ入力ソースを選択・調整できます。

**SHIFT + SAMPLE** ボタンを押して開きます。

## Source（入力ソース）

- **Mic：** 内蔵マイク
- **Rear：** リアパネルの AUDIO IN（ステレオ録音）
- **Rear L / Rear R：** 個別チャンネル
- **Resample：** MPC Sample から再録音したオーディオ（シーケンスを単一パッドに録音）
- **USB：** USB ポートに接続されたデバイスのオーディオ（ステレオ）
- **USB L / USB R：** 左/右チャンネル個別

## Monitor（モニタリング）

- **Off：** モニタリングなし
- **Auto：** Sample Record Mode がフォーカス中のみ
- **On：** 常にモニタリング

## Threshold（閾値）

選択したソースの最小オーディオレベル（-96〜0 dB）。自動録音を開始する基準レベルです。

## Rec Length（録音長）

- **FREE：** 無制限
- **SEQ：** シーケンス長に固定

## Rec Input Effects

Knob FX を録音に含める（**ON**）か除外する（**Off**）かを設定します。

**B3** でメニューを閉じます。
"""

JA_MD["fader"] = """
# Fader

Fader メニューでは、フェーダーがコントロールするパラメータを選択できます。

## 開き方

**SHIFT + PAD 9 – FADER** を押します。

## 基本操作

**B3** でフェーダーコントロールのオン/オフを切り替えます。

**ENCODER** を回して以下の機能を参照し、押して選択します。

## Fader 機能一覧

- **Pad Volume：** 選択したパッドの音量レベルを調整
- **Pad Pan：** 選択したパッドのステレオパンを調整
- **Pad Tune：** 選択したパッドの Semi Tune 値を調整
- **Pad Amp Attack：** 振幅エンベロープの Attack 値を調整
- **Pad Amp Decay/Release：** Decay または Release 値を調整
- **Pad Filter Cutoff：** フィルターの Cutoff 値を調整
- **Kit Volume：** キット全体の音量を調整

## ソフトテイクオーバー

コントロール切り替え時にフェーダーの位置が新しいパラメータの現在値と一致しない場合があります。Fader LED の明るさが現在のパラメータ値の相対位置を示します。LED が再度変化し始めるまでフェーダーを動かしてください。

**B1** で前のページに戻ります。
"""

JA_MD["time_correct"] = """
# Time Correct（タイムコレクト）

Time Correct メニューにはプロジェクト内のイベントをクオンタイズする設定が含まれています。ノートが定義された値のグリッドにスナップします。

**SHIFT + PAD 14 – TIME CORRECT** を押して開きます。

**PAD** を押してタイミング補正するパッドを選択します。**B2** ですべてのパッドを同時に選択できます。

## パラメータ

- **K1 ノブ – Q（Quantization）：** クオンタイズ値を調整します。各バーが分割される時間分割を決定し、ノートイベントがその分割にスナップします（例：Q = 1/16 の場合、全イベントが最も近い 1/16 音符にスナップ）。
- **K2 ノブ – Shift：** 選択したイベントをシーケンス内で前後に微量調整します。「ヒューマナイズ」効果を作れます。
- **K3 ノブ – Swing：** ノートのタイミングをシフトしてビートを「シャッフル」させます。トリプレット風の感覚を持たせることができます。

## 適用

**B3（Do It!）** を押して Time Correct 設定を適用します。選択したパッドのすべての録音済みイベントが調整されます。

### ヒント

適用前後にシーケンスを再生して違いを確認してください。満足できない場合は **SHIFT + -/UNDO** で元に戻せます。

Q と Swing の値はグローバル設定であり、Sequence Mode でも共有されます。Swing 値は Note Repeat 機能にも影響します。

**B1（Cancel）** で設定を適用せずに終了します。
"""

JA_MD["midi_configuration"] = """
# MIDI 設定（MIDI Configuration）

MPC Sample が MIDI および CV データを送受信する方法を調整します。設定とデータのリセットも行えます。

**SHIFT + PAD 8 – MIDI CONFIG** を押して開きます。

**ENCODER** でオプションをスクロールし、押して選択してから回して値を調整します。もう一度押して確定します。

## 設定項目

| 設定 | 説明 | 値 |
|------|------|-----|
| MIDI Port | アクティブな MIDI ポート | External（背面 1/8" MIDI）、USB |
| MIDI In Channel | MIDI 入力チャンネル | All、1–16 |
| MIDI Out Channel | MIDI 出力チャンネル | 1–16 |
| Pad MIDI In | MIDI 入力でパッドをトリガー | Off、On |
| Pad MIDI Out | パッドから MIDI 出力を送信 | Never、Always、Empty |
| MIDI Sync In | MIDI Sync 情報の受信 | Off、Midi Clock、MTC |
| MIDI Sync Out | MIDI Sync 情報の送信 | Off、Midi Clock、MTC |
| MIDI Thru | MIDI OUT をスルーポートとして使用 | Off、On |
| Receive Program Change | プログラムチェンジの受信 | Off、Sequence |
| CV/Sync Out | SYNC OUT から CV/Sync を送信 | Off、On |
| CV/Sync Base | CV/Sync クロック解像度 | 1–8 |
| CV/Sync Division | CV/Sync Base の乗数 | 1–24 |

## テイクオーバー設定

K1–K3 ノブと FADER の動作を調整します。

- **Pickup：** ハードウェア位置がパラメータ位置と一致するまで編集不可
- **Scaled：** ハードウェア調整に応じてスケーリングしてパラメータが移動
- **Instant：** ハードウェア調整時にパラメータが即座にジャンプ

## リセット機能

- **RESET FACTORY SETTINGS：** すべての設定をリセットして再起動（B3 で「YES」、B1 で「NO」）。
- **RESET FACTORY DATA：** ユーザーコンテンツをすべて削除して再起動（⚠️ この操作は取り消せません）。
"""

JA_MD["project"] = """
# プロジェクト（Project）

Project メニューでは、プロジェクトの保存・読み込みと外部 microSD カードの管理が可能です。

**SHIFT + PAD 16 – PROJECT** を長押しして開きます。

**ENCODER** でオプションを参照し、押して選択します。

## Load Project

プロジェクトとキットを読み込みます。

- **Demos：** デモプロジェクト。MPC Sample で作成可能なサウンドとスタイルを探索できます。
- **Kits：** 完全なキット。ENCODER を押してキットと 4 つのデフォルトシーケンスを読み込むか、**B3（Load Kit）** でキットサンプルのみを読み込みます。
- **User：** 内蔵ドライブに保存されたユーザープロジェクト。

## Save Project

現在のプロジェクトを保存します。

ENCODER でプロジェクト名を入力します。**SHIFT** で大文字にアクセス、**-/+** で文字間を移動、**B2** で文字削除、**SHIFT + B2** で全文字削除です。

**B3（Do It!）** で保存、**B1（Cancel）** でキャンセルします。

**注：** MPC Sample には自動保存システムがあります。作業進行状況がバックグラウンドで保存されます。

## New Project

**B3** を押して現在のプロジェクトをクリアし、新規プロジェクトを開始します。**B1** でキャンセルします。

## SD Card Access

microSD カードに USB 経由でコンピュータからアクセスします。サンプル・ソング・プロジェクトファイルを MPC Sample とコンピュータ間で転送できます。

microSD カードはコンピュータ上の外部ドライブとしてマウントされます。このモード中は他のモードは使用できません。

ファイル転送完了後、コンピュータから microSD を安全に取り出してから **B1** を押してモードを終了します。
"""

JA_MD["technical_specifications"] = """
# 技術仕様

## ハードウェアおよび入出力

**ストレージ**
8 GB 内蔵ドライブ（工場出荷時データ約 2 GB 含む）、microSD カードスロット対応

**メモリ**
2 GB

**パッド**
16 個の RGB 照光ベロシティ感応型 MPC パッド（アフタータッチ対応）

**ディスプレイ**
2.4"（6.1 cm）フルカラー LCD（高解像度波形編集対応）

**入出力**
- オーディオ入力：2 系統 1/4" TRS（マイク/ラインレベル）
- オーディオ出力：2 系統 1/4" TRS（ラインレベル）
- ヘッドフォン出力：1 系統 1/8" TRS
- MIDI 入出力：各 1 系統 1/8" TRS Type A
- CV/ゲート出力：1 系統 1/8" TRS
- USB Type-C（電源・オーディオ・MIDI・SD カードアクセス対応）

**マイク/スピーカー**
内蔵マイク・3 ワットスピーカー搭載

**電源**
USB Type-C（バスパワーまたは別売 AC アダプター/モバイルバッテリー 5V 2A）

**バッテリー**
リチウムイオン型、連続再生約 5 時間

**寸法・重量**
7.6" × 9.3" × 2.0"（19.4 × 23.6 × 5.0 cm）
2.03 lbs.（0.92 kg）

## フォーマットとサポート

**ポリフォニー**
32 ステレオボイス

**録音可能データ**
プロジェクトあたり 16 サンプル × 8 バンク、16 シーケンス × 8 バンク（プロジェクト数無制限）

**最大サンプリング時間**
サンプルあたり 20 分

**対応フォーマット**
.wav, .mp3, .aif/.aiff, .snd, .s1s, .s3s, .flac, .ogg

**処理サンプリング周波数**
44.1 kHz、32-bit float

**対応サンプリング周波数**
ファイル読み込み：24/16-bit、44.1/48/96 kHz
録音：24-bit、44.1 kHz

## 主要ソフトウェア機能

**シーケンサー**
MPC シーケンサー（リアルタイムスウィング、960 ppq）

**サンプリング**
マイク・オーディオ入力・USB・リサンプル対応

**エフェクト**
4 つのエフェクトエンジン（60 以上のエフェクト）：Pad FX、Knob FX、Flex Beat、Color-Compressor

**サンプル編集**
Chop モード・自動スナップ・リアルタイムループ・ワーピング対応
"""

JA_MD["trademarks___licenses"] = """
# 商標・ライセンス

## 登録商標

Akai Professional および MPC は inMusic Brands, Inc. の商標であり、米国およびその他の国で登録されています。

macOS は Apple Inc. の商標であり、米国およびその他の国で登録されています。

microSD は SD-3C, LLC の登録商標です。

Windows は米国およびその他の国における Microsoft Corporation の登録商標です。

## その他の商標

その他すべての製品名・企業名・商標・商号は、それぞれの所有者に帰属しています。
"""

# ─── Convert all JA markdown to HTML ──────────────────────────────────────────
PAGES_JA = {k: md_to_html(v) for k, v in JA_MD.items()}

JA_TITLES = {
    "introduction": "はじめに",
    "setup": "セットアップ",
    "firmware_updates": "ファームウェア更新",
    "connection_diagram": "接続ダイアグラム",
    "tutorial": "チュートリアル",
    "features": "機能説明",
    "operation": "操作",
    "sample_mode": "Sample Mode",
    "pad_play": "Pad Play",
    "loading_and_saving_samples": "サンプルのロード/セーブ",
    "sample_record_mode": "サンプル録音モード",
    "sequence_mode": "Sequence Mode",
    "recording_sequences": "シーケンス録音",
    "editing_sequences": "シーケンス編集",
    "step_edit": "Step Edit",
    "song_mode": "Song Mode",
    "effects": "エフェクト",
    "pad_fx": "Pad FX",
    "flex_beat": "Flex Beat",
    "knob_fx": "Knob FX",
    "compressor": "Compressor",
    "menus": "メニュー",
    "input_configuration": "入力設定",
    "fader": "Fader",
    "time_correct": "タイムコレクト",
    "midi_configuration": "MIDI 設定",
    "project": "プロジェクト",
    "technical_specifications": "技術仕様",
    "trademarks___licenses": "商標・ライセンス",
}

# ─── CSS to inject ─────────────────────────────────────────────────────────────
NEW_CSS = """
/* ─── Language switcher ───────────────────── */
.lang-switcher {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 3px;
  background: var(--surface3);
  border-radius: 8px;
  flex-shrink: 0;
}
.lang-btn {
  padding: 5px 10px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  transition: all var(--transition);
  font-family: inherit;
  line-height: 1;
}
.lang-btn.active { background: var(--red); color: #fff; }
.lang-btn:hover:not(.active) { background: var(--surface2); color: var(--text); }

/* ─── Onboarding tip ──────────────────────── */
.onboarding-tip {
  background: linear-gradient(135deg, rgba(232,0,45,.08), rgba(232,0,45,.03));
  border: 1px solid rgba(232,0,45,.2);
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 28px;
  display: flex;
  gap: 14px;
  align-items: flex-start;
}
.tip-icon { font-size: 2rem; flex-shrink: 0; line-height: 1; margin-top: 2px; }
.tip-body h3 {
  font-size: 1rem; font-weight: 700; color: var(--text);
  margin: 0 0 6px; border: none; padding: 0;
}
.tip-body p {
  font-size: 0.85rem; color: var(--text-muted);
  margin: 0 0 12px; line-height: 1.6;
}
.tip-cta {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 14px;
  background: var(--red); color: #fff;
  border: none; border-radius: var(--radius);
  font-size: 0.83rem; font-weight: 700;
  cursor: pointer; font-family: inherit;
  transition: opacity var(--transition);
  -webkit-tap-highlight-color: transparent;
}
.tip-cta:hover { opacity: 0.85; }
"""

# ─── New JS (data + functions) ────────────────────────────────────────────────
PAGES_JA_JSON = json.dumps(PAGES_JA, ensure_ascii=False)
JA_TITLES_JSON = json.dumps(JA_TITLES, ensure_ascii=False)

NEW_JS_DATA = f"""
// ── 言語データ ───────────────────────────────
const PAGES_JA = {PAGES_JA_JSON};
const JA_TITLES = {JA_TITLES_JSON};
let currentLang = localStorage.getItem('mpc-lang') || 'en';

function getTitle(item) {{
  return (currentLang === 'ja' && JA_TITLES[item.id]) ? JA_TITLES[item.id] : item.title;
}}
function getPageContent(id) {{
  return (currentLang === 'ja' ? PAGES_JA[id] : PAGES[id]) || PAGES[id] || '<p>No content available.</p>';
}}
function buildSearchIndex() {{
  return FLAT.map(item => {{
    const raw = getPageContent(item.id);
    const text = raw.replace(/<[^>]+>/g, ' ').replace(/\\s+/g, ' ').trim();
    return {{ id: item.id, title: getTitle(item), text }};
  }});
}}
function setLang(lang) {{
  currentLang = lang;
  localStorage.setItem('mpc-lang', lang);
  document.querySelectorAll('.lang-btn').forEach(btn => {{
    btn.classList.toggle('active', btn.dataset.lang === lang);
  }});
  searchIndex = buildSearchIndex();
  initSidebar();
  if (currentId) navigateTo(currentId, false);
}}
"""

TIP_JS = """
  // Homepage onboarding tip
  if (id === 'introduction') {
    const tipHtml = currentLang === 'ja' ? `
      <div class="onboarding-tip">
        <div class="tip-icon">💡</div>
        <div class="tip-body">
          <h3>やりたいことから素早く調べる</h3>
          <p>ヘッダー右上の <strong>💡 ボタン</strong>を押すと、「ループを作りたい」「エフェクトをかけたい」など<strong>やりたいことの目的別</strong>に関連ページをすぐ見つけられます。<br>キーワードで検索することも可能です。</p>
          <button class="tip-cta" onclick="openUseCase()">💡 やりたいことから探す</button>
        </div>
      </div>` : `
      <div class="onboarding-tip">
        <div class="tip-icon">💡</div>
        <div class="tip-body">
          <h3>Find pages by what you want to do</h3>
          <p>Tap the <strong>💡 button</strong> in the header to browse 48 use-case scenarios — "want to record a beat", "add reverb", "set BPM" — and jump directly to the right page. You can also search by keyword.</p>
          <button class="tip-cta" onclick="openUseCase()">💡 Find by use case</button>
        </div>
      </div>`;
    const tipEl = document.createElement('div');
    tipEl.innerHTML = tipHtml;
    document.getElementById('pageContent').prepend(tipEl.firstElementChild);
  }
"""

def main():
    with open(OUTPUT, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. CSS の追加
    html = html.replace("</style>", NEW_CSS + "\n</style>", 1)

    # 2. ヘッダーに言語スイッチャーを追加（💡ボタンの前）
    html = html.replace(
        '  <button class="uc-btn"',
        '  <div class="lang-switcher">\n'
        '    <button class="lang-btn" data-lang="en">EN</button>\n'
        '    <button class="lang-btn" data-lang="ja">日本語</button>\n'
        '  </div>\n'
        '  <button class="uc-btn"',
        1
    )

    # 3. JS データ：FLAT 定数の直後に言語データを挿入
    html = html.replace(
        "// ── State ───────────────────────────────────\nlet currentId = null;",
        NEW_JS_DATA + "\n// ── State ───────────────────────────────────\nlet currentId = null;",
        1
    )

    # 4. searchIndex を const → let に変更し buildSearchIndex() を使用
    html = html.replace(
        "const searchIndex = FLAT.map(item => {\n  const raw = PAGES[item.id] || '';\n  const text = raw.replace(/<[^>]+>/g, ' ').replace(/\\s+/g, ' ').trim();\n  return { id: item.id, title: item.title, text };\n});",
        "let searchIndex = buildSearchIndex();",
        1
    )

    # 5. navigateTo: PAGES[id] → getPageContent(id)
    html = html.replace(
        "document.getElementById('pageContent').innerHTML = PAGES[id] || '<p>No content available.</p>';",
        "document.getElementById('pageContent').innerHTML = getPageContent(id);",
        1
    )

    # 6. navigateTo: ホームページTipを挿入（内部リンクハンドラの前）
    html = html.replace(
        "  // テーブルをスクロール可能なラッパーで囲む",
        TIP_JS + "\n  // テーブルをスクロール可能なラッパーで囲む",
        1
    )

    # 7. navigateTo: prev/next タイトルをgetTitle()で表示
    html = html.replace(
        "${prev ? `<div class=\"nav-label\">Previous</div><div class=\"nav-title\">${prev.title}</div>` : '—'}",
        "${prev ? `<div class=\"nav-label\">${currentLang==='ja'?'前のページ':'Previous'}</div><div class=\"nav-title\">${getTitle(prev)}</div>` : '—'}",
        1
    )
    html = html.replace(
        "${next ? `<div class=\"nav-label\">Next</div><div class=\"nav-title\">${next.title}</div>` : '—'}",
        "${next ? `<div class=\"nav-label\">${currentLang==='ja'?'次のページ':'Next'}</div><div class=\"nav-title\">${getTitle(next)}</div>` : '—'}",
        1
    )

    # 8. renderNav: item.title → getTitle(item)
    html = html.replace(
        "`<div class=\"${cls}\" data-id=\"${item.id}\" role=\"button\" tabindex=\"0\">${item.title}${caret}</div>`",
        "`<div class=\"${cls}\" data-id=\"${item.id}\" role=\"button\" tabindex=\"0\">${getTitle(item)}${caret}</div>`",
        1
    )

    # 9. breadcrumb: p.title → getTitle(p)
    html = html.replace(
        "`<a onclick=\"navigateTo('${p.id}')\">${p.title}</a><span>/</span>`",
        "`<a onclick=\"navigateTo('${p.id}')\">${getTitle(p)}</a><span>/</span>`",
        1
    )
    html = html.replace(
        "`<span>${parents[parents.length - 1].title}</span>`",
        "`<span>${getTitle(parents[parents.length - 1])}</span>`",
        1
    )

    # 10. Init: 言語ボタンの初期状態を設定
    html = html.replace(
        "// ── Init ─────────────────────────────────────\ninitSidebar();",
        "// ── Init ─────────────────────────────────────\n"
        "document.querySelectorAll('.lang-btn').forEach(btn => {\n"
        "  btn.classList.toggle('active', btn.dataset.lang === currentLang);\n"
        "  btn.addEventListener('click', () => setLang(btn.dataset.lang));\n"
        "});\n"
        "initSidebar();",
        1
    )

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = len(html.encode("utf-8")) // 1024
    print(f"Done! index.html updated ({size_kb} KB)")
    print("Changes: Japanese content, language switcher, homepage tip")

if __name__ == "__main__":
    main()
