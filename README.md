# Capture-Movie-From-RTSP-Daemon
## 概要
capture-movie-from-rtsp-daemonは、RTSPでストリーミング配信されている映像を動画ファイルに変換するマイクロサービスです。   
kanbanから開始の指示を受けたら動画の変換を開始し、終了の指示を受け取ったら動画の変換を終了します。

## 動作環境
ストリーミング配信をしているサービスが、同一Kubernetesクラスター内、あるいはネットワーク内に存在する必要があります。   
また、capture-movie-from-rtsp-daemonは、aion-coreのプラットフォーム上での動作を前提としています。   
使用する際は、事前に下記の通りAIONの動作環境を用意してください。   
* ARM CPU搭載のデバイス(NVIDIA Jetson シリーズ等)   
* OS: Linux Ubuntu OS   
* CPU: ARM64   
* Kubernetes   
* [AION](https://github.com/latonaio/aion-core) のリソース   

## セットアップ
以下のコマンドを実行して、docker imageを作成してください。
```
make docker-build
```

## 起動方法
### デプロイ on AION
Project.ymlに設定を記載し、AionCore経由でコンテナを起動する。  
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

## I/O
kanbanのメタデータから下記の情報を入出力します。
### Input
| タイプ(type)  |  |
| --- | --- | 
| 1. prestart| 仮で動画変換を開始する。   
| 2. start| 動画変換の開始を確定する。   
| 3. end | 動画変換を終了する。

### Output  
| 変数名 |  |
| --- | --- |
| start_time | 動画変換を開始した時間 |   
| end_time | 動画変換を終了した時間 | 
| file_name  | 動画ファイル名 | 

## Flowchart
![フローチャート図](doc/capture-movie-from-rtsp-daemon-flowchart.png)