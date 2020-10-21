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
![フローチャート図](https://bitbucket.org/latonaio/capture-movie-from-rtsp-daemon/raw/8fa8b38f6257bbf8afb8855a52837bb8f50951c2/doc/capture-movie-from-rtsp-daemon-flowchart.png)