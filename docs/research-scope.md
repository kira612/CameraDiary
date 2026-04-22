# Research Scope

## 中心文

本研究は、**定点カメラで撮影された長尺保育動画から、映像中の各園児に対応する証拠区間を抽出・整理し、園児ごとに根拠付きの自然な連絡帳文を 1 本ずつ自動生成すること**を目指す。

## この repo の設計原則

- 出力は `child-wise`
- 設計思想は `evidence-first`
- `tracking` は有力手段だが唯一の中心ではない
- repo の主語は `event extraction` ではなく `diary generation`
- MVP でも `根拠付きの園児別文生成` を含める

## 入れるもの

- 定点カメラ長尺動画
- RTSP ingest
- evidence candidate extraction
- child-wise grouping
- local multimodal summarization
- child-wise diary composition
- evidence-linked review

## 最初からは入れないもの

- 全園児の完全自動個人識別
- tracking のみを中心にした repo 設計
- event のみを唯一の中間表現にする設計
- 生映像全量の長期保存

## なぜ event-first でも tracking-first でもないか

### event-first の問題

「イベント抽出して文章化する」と置くと、最終的に必要な `園児ごとに 1 本の自然文` という出力が弱くなる。

### tracking-first の問題

tracking は重要だが、Re-ID や長尺動画での不安定性に全体設計が引っ張られやすい。

### evidence-first の利点

- tracking を取り込める
- event も取り込める
- clip や観測ログも扱える
- child-wise grouping と自然につながる

## 最終出力の定義

1 本の動画に対して 1 本の文章を作るのではない。

最終出力は次。

- 動画中の園児ごとに 1 本ずつ自然文を生成する
- 各文に対して、対応する根拠区間を提示する
- 保育士が修正・確定できる

## MVP の解釈

MVP では、すべての園児を完全自動で識別する必要はない。

代わりに、以下を満たすことを重視する。

- evidence を取れる
- それを一部の園児単位で束ねられる
- child-wise に自然文を出せる
- 根拠区間を示せる
