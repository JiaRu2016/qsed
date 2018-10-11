# Event-Driven Backtester / Live Trader


## Reference

inspired by quantstart (www.quantstart.com) series articles:


- [Event-Driven Backtesting with Python - Part I](https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-I)
- [Event-Driven Backtesting with Python - Part II](https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-II)
- [Event-Driven Backtesting with Python - Part III](https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-III)
- [Event-Driven Backtesting with Python - Part IV](https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-IV)
- [Event-Driven Backtesting with Python - Part V](https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-V)
- [Event-Driven Backtesting with Python - Part VI](https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-VI)
- [Event-Driven Backtesting with Python - Part VII](https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-VII)
- [Event-Driven Backtesting with Python - Part VIII](https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-VIII)

## Mind Map

<!-- ![mind map](./mindmap/Event-Driven-Backtester.png) -->


## Dirs


```
$ python qsMainEngine.py
```

### event-driven-demo/

Demo of quantstart series articles.

```angular2html
cd event-driven-demo
python main.py
```

### bitmex/

```angular2html
cd bitmex
python main.py       # test bitmexDataHandler with main.py
python test-OMS.py   # test OMS: bitmex Target-Position-Based OMS, with random signaller
```

### bitmex-HistoryData/

```angular2html
cd bitmex-HistoryData/
python bitmexHistoryData.py  # unit test
```

### Sina/

```angular2html
cd Sina/
python SinaLiveDataHandler.py  # unit test
```