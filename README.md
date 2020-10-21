# Capture-Movie-From-RTSP-Daemon
## Description  
RTSPでストリーミング配信されている映像を動画ファイルに変換するマイクロサービスです。カンバンから開始の指示を受けたら動画変換を始め、終了の指示を受け取ったら動画変換を終了する。

## Prerequisite  
* ストリーミング配信しているサービスが同一Kubernetesクラスター内、あるいはネットワーク内に存在する。

## I/O
カンバンのメタデータから下記の情報を入出力
#### Input
* タイプ(type)   
　1. prestart  
　　仮で動画変換を開始する。
　2. start  
　　動画変換の開始を確定する。
　3. end  
　　動画変換を終了する。

#### Output  
* 開始時間(start_time)  
動画変換を開始した時間    
* 終了時間(end_time)    
動画変換を終了した時間  
* 動画ファイル名(file_name)  

## Getting Started
1. 下記コマンドでDockerイメージを作成する。  
```
make docker-build
```
2. Project.ymlに設定を記載し、AionCore経由でコンテナを起動する。  
project.ymlへの記載例  
* get_kanban_itrのメソッドで動作するので、multiple: noとして起動する。  
* 動画を送信したい端末名をNEXT_DEVICEに記載する。　　
```
  capture-movie-from-rtsp:
    multiple: no
    privileged: yes
    env:
      NEXT_DEVICE:  ###
```
## Flowchart
```flow
開始=>start: Start
終了=>end: End

分岐1(align-next=no)=>condition: カンバン内のタイプがprestartか？
分岐2(align-next=no)=>condition: カンバン内のタイプがstartか？
分岐3(align-next=no)=>condition: カンバン内のタイプがendか？

処理1=>operation: カンバンを取得
処理2=>operation: 既存の動画変換を終了し、動画変換を開始
処理3=>operation: 動画変換を終了
処理4=>operation: 開始時間、終了時間、動画ファイル名を含んだカンバンを出力
処理5=>operation: 何もしない

開始->処理1->分岐1(yes)->処理2
開始->分岐1(no, bottom)->分岐2(yes)->処理5
開始->分岐1(no, bottom)->分岐2(no, bottom)->分岐3(yes)->処理3->処理4->終了
```
![フローチャート図](https://bitbucket.org/latonaio/capture-movie-from-rtsp-daemon/raw/8fa8b38f6257bbf8afb8855a52837bb8f50951c2/doc/capture-movie-from-rtsp-daemon-flowchart.png)