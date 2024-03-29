# capture-movie-from-rtsp-daemon  
## Description  
RTSPでストリーミング配信されている映像を動画ファイルに変換するマイクロサービスです。  
カンバンから開始の指示を受けたら動画変換を始め、終了の指示を受け取ったら動画変換を終了します。  

## Prerequisite  
* ストリーミング配信されるサービスが同一Kubernetesクラスター内、あるいはネットワーク内に存在すること  

## I/O
カンバンのメタデータから下記の情報を入出力します  
#### Input
* タイプ(type)   
　1. prestart  
　　仮で動画変換を開始します  
　2. start  
　　動画変換の開始を確定します  
　3. end  
　　動画変換を終了します  

#### Output  
* 開始時間(start_time)  
動画変換を開始した時間    
* 終了時間(end_time)    
動画変換を終了した時間  
* 動画ファイル名(file_name)  

## Getting Started  
1. 下記コマンドでDockerイメージを作成します。  
```
make docker-build
```
2. aion-core-manifest 内の default.ymlに設定を記載し、aion-core でコンテナを起動します。  
default.ymlへの記載例  
* get_kanban_itrのメソッドで動作するので、multiple: noとして起動します。  
* 動画を送信したい端末名をNEXT_DEVICEに記載します。　　
```
  capture-movie-from-rtsp:
    multiple: no
    privileged: yes
    env:
      NEXT_DEVICE:  ###
```
## Flowchart  
![フローチャート図](doc/capture-movie-from-rtsp-daemon-flowchart.png)