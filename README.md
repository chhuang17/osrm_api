# Open Street Routing Machine (OSRM) Python API
> 所需套件: ```requests```, ```json```, ```numpy```

## 說明
__OSRM (Open Street Routing Machine)__ 是一個開源的地圖搜尋引擎，資料來源係基於 OpenStreetMap。OSRM 的底層使用 C++ 開發，並且官方提供 HTTP 接口，可供開發人員進行串接。本篇文章為筆者自行編寫的 OSRM Python API 使用說明，此 API 即是利用官方提供之 HTTP 接口，利用 Python 的 ```requests``` 套件爬取並解析 json 資料。

## 開始使用 OSRM API
您可以使用 Git 將這個 Repository 下載至您的本地端：
```
git clone https://github.com/chhuang17/osrm_api.git
```

若您使用 Anaconda 進行開發，您可以將這個 Repository 存放至以下位置：
```
c:/users/home/anaconda3/Lib/site-packages
```

此時便可以於您的 IDE 直接使用此套件：
```python
from osrm_api import osrm
```

### 關於此 API 的詳細使用說明，請參考以下網址：
https://hackmd.io/@tLU1SwtjQNqpLcDPI2Iepg/S1pB6VZl6
