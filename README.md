# promiedos-scrapper

Get data from promiedos as a live feed as json messages.

## Usage(kinda)

```
python scrapper.py MATCH_ID
```

Where `http://promiedos.com.ar/ficha.php?id=MATCH_ID`

It only returns the name of the teams playing.

## Dependencies:

`beautifulsoup`, `apscheduler`, `lxml`