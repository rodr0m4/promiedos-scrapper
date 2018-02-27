# promiedos-scrapper

Get data from promiedos as a live feed as json messages.

## Usage(kinda)

```
python scrapper.py MATCH_ID
```

Where `http://promiedos.com.ar/ficha.php?id=MATCH_ID`

Dictionary comparation works (I.E. with minimal modification if you run the program in a loop it will send events), but every dict should be managed as a class, with a special field event_type encapsulating what is it(a goal is the same as a yellow or red card with the current model).

## Dependencies:

`beautifulsoup`, `apscheduler`, `lxml`