from robobrowser import RoboBrowser
import pandas as pd
import numpy as np
import time
import pickle
import json


def turnFloat(x):
    x = x.replace(".", "").replace(",", ".")
    return float(x)


def turnCurrency(x):
    num = x.split(".")
    value = ""
    for i in range(1, len(num[0]) + 1):
        value = f"{num[0][-i]}{value}"
        if i % 3 == 0:
            value = f".{value}"
    value += f",{num[1][:3]}"
    return value


def into(item):
    return item[0]


def numerize(num):
    if str(num).lower() == "nan":
        return 0
    else:
        return num


def today(nowtime):
    today = time.localtime(nowtime)
    day = str(today.tm_mday)
    if len(day) == 1:
        day = "0" + day
    mon = str(today.tm_mon)
    if len(mon) == 1:
        mon = "0" + mon
    year = str(today.tm_year)[-2:]
    date = f"{day}.{mon}.20{year}"
    return date


def now_value():
    browser = RoboBrowser(parser="html.parser")
    ticker = "https://www.mercadobitcoin.net/api/BTC/ticker/"
    browser.open(ticker)
    r = json.loads(browser.response.content)
    date = time.localtime(r["ticker"]["date"])
    value = turnCurrency(r["ticker"]["last"])
    return (date, value)


def play(nvers=150, plot=True):
    import matplotlib.pyplot as plt
    from statsmodels.tsa.api import SimpleExpSmoothing, Holt, ExponentialSmoothing
    from keras.models import model_from_json
    import statsmodels.api as sm

    browser = RoboBrowser(
        parser="html.parser",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
    )
    url = "https://br.investing.com/crypto/bitcoin/btc-brl-historical-data"
    browser.open(url)
    df = pd.read_csv("Bitcoin/data_brl.csv")
    ftoday = pd.to_datetime(today(time.time()), dayfirst=True)
    rows = browser.find(class_="genTbl closedTbl historicalTbl").find_all("tr")[1:]
    hist = {"date": [], "val": []}
    for row in rows:
        itens = row.find_all("td")
        date = itens[0].text
        val = turnFloat(itens[1].text)
        fdate = pd.to_datetime(date, dayfirst=True)
        if date not in df["date"].values:
            d = ftoday - fdate
            if d.days > 0 or (d.days == 0 and time.localtime().tm_hour >= 21):
                hist["date"].append(date)
                hist["val"].append(val)
    hist["date"] = hist["date"][::-1]
    hist["val"] = hist["val"][::-1]
    df = pd.concat([df, pd.DataFrame(hist)], ignore_index=True)
    df.to_csv("Bitcoin/data_brl.csv", index=False)

    d = 0
    vals = df.val
    last = vals.iloc[-(2 + d)]
    now = vals.iloc[-(1 + d)]
    var = round((now - last) / last, 4)
    n_total = len(df)
    n = n_total

    l = df["val"][n - 1]
    nowdate = df["date"][n - 1]
    result = f"Data: {nowdate}\n"
    result += f"Valor presente: {l}\n"
    result += f"Variação: {var}\n\n"
    result += "Previsão:\n\n"
    amost = 15
    n_pred = 2

    pred = {}

    null = np.array([None for _ in range(n_total)])

    sp = 4
    name = f"ES_{sp}"
    fit1 = ExponentialSmoothing(np.asarray(df["val"]), seasonal_periods=sp, trend="add", seasonal="add",).fit()
    forecast = fit1.forecast(n_pred)
    pred[name] = np.concatenate((null, forecast))
    if plot:
        plt.figure(figsize=(16, 8))
        plt.plot(df[-amost:]["val"], label="Valor Real")
        plt.plot(pred[name], label=f"Previsão {name}")

    sp = 7
    name = f"ES_{sp}"
    fit1 = ExponentialSmoothing(np.asarray(df["val"]), seasonal_periods=sp, trend="add", seasonal="add",).fit()
    forecast = fit1.forecast(n_pred)
    pred[name] = np.concatenate((null, forecast))
    if plot:
        plt.plot(pred[name], label=f"Previsão {name}")

    sp = 12
    name = f"ES_{sp}"
    fit1 = ExponentialSmoothing(np.asarray(df["val"]), seasonal_periods=sp, trend="add", seasonal="add",).fit()
    forecast = fit1.forecast(n_pred)
    pred[name] = np.concatenate((null, forecast))
    if plot:
        plt.plot(pred[name], label=f"Previsão {name}")

    name = f"SARIMAX"
    fit1 = sm.tsa.statespace.SARIMAX(df["val"], order=(2, 1, 4), seasonal_order=(0, 1, 1, 7)).fit()
    forecast = fit1.forecast(n_pred)
    pred[name] = np.concatenate((null, forecast))
    if plot:
        plt.plot(pred[name], label=f"Previsão {name}")

    sl = 0.6
    name = f"SES_{sl}"
    fit1 = SimpleExpSmoothing(np.asarray(df["val"])).fit(smoothing_level=sl, optimized=False)
    forecast = fit1.forecast(n_pred)
    pred[name] = np.concatenate((null, forecast))
    if plot:
        plt.plot(pred[name], label=f"Previsão {name}")

    sl = 0.9
    name = f"SES_{sl}"
    fit1 = SimpleExpSmoothing(np.asarray(df["val"])).fit(smoothing_level=sl, optimized=False)
    forecast = fit1.forecast(n_pred)
    pred[name] = np.concatenate((null, forecast))
    if plot:
        plt.plot(pred[name], label=f"Previsão {name}")

    sl = 1.2
    name = f"SES_{sl}"
    fit1 = SimpleExpSmoothing(np.asarray(df["val"])).fit(smoothing_level=sl, optimized=False)
    forecast = fit1.forecast(n_pred)
    pred[name] = np.concatenate((null, forecast))
    if plot:
        plt.plot(pred[name], label=f"Previsão {name}")

    if plot:
        plt.legend(loc="best")
        plt.savefig("Bitcoin/bitgraphic.png")

    hist = {
        "ES_4": [],
        "ES_7": [],
        "ES_12": [],
        "SARIMAX": [],
        "SES_0.6": [],
        "SES_0.9": [],
        "SES_1.2": [],
        "DP": [],
        "DP_U": [],
        "DP_D": [],
        "NUM_U": [],
        "NUM_D": [],
        "DIST_U": [],
        "DIST_D": [],
    }

    preds = []
    ups = []
    downs = []

    for k in pred.keys():
        p = pred[k][n]
        preds.append(p)
        up = p > l
        if up:
            ups.append(p)
            hist[k].append(1)
        else:
            downs.append(p)
            hist[k].append(0)
        result += f"{k}: {p} --- {up}\n"

    sd = numerize(round(np.std(preds), 3))
    u_sd = numerize(round(np.std(ups), 3))
    d_sd = numerize(round(np.std(downs), 3))
    u_len = numerize(round(len(ups), 3))
    d_len = numerize(round(len(downs), 3))
    u_dif = numerize(round(abs(np.mean(ups) - l), 3))
    d_dif = numerize(round(abs(np.mean(downs) - l), 3))

    hist["DP"].append(sd)
    hist["DP_U"].append(u_sd)
    hist["DP_D"].append(d_sd)
    hist["NUM_U"].append(u_len)
    hist["NUM_D"].append(d_len)
    hist["DIST_U"].append(u_dif)
    hist["DIST_D"].append(d_dif)

    info = pd.DataFrame(hist)

    result += f"\nDesvio Padrão: {sd}\n"
    result += f"Desvio Padrão de crescentes: {u_sd}\n"
    result += f"Desvio Padrão de decrescentes: {d_sd}\n"
    result += f"Número de crescentes: {u_len}\n"
    result += f"Número de decrescentes: {d_len}\n"
    result += f"Distância de crescentes: {u_dif}\n"
    result += f"Distância de decrescentes: {d_dif}\n\n"

    name = f"gradient_brl_{nvers}s"
    model = pickle.load(open(f"Bitcoin/{name}.sav", "rb"))
    result += f"Análise de resultados por {name}:\n\n"

    probs = model.predict_proba(info)[0]
    up_prob = round(probs[1], 2)
    down_prob = round(probs[0], 2)
    if up_prob > 0.7:
        result += f"Probabilidade de ALTA para amanhã: {up_prob}\n"
        result += f"Ação: COMPRAR\n\n"

    elif up_prob > 0.4:
        result += f"Probabilidade incerta, com chance para alta de: {up_prob}\n"
        result += f"Ação: MANTER\n\n"

    else:
        result += f"Probabilidade de BAIXA para amanhã: {down_prob}\n"
        result += f"Ação: VENDER.\n\n"

    name = f"randomforest_brl_{nvers}s"
    model = pickle.load(open(f"Bitcoin/{name}.sav", "rb"))
    result += f"Análise de resultados por {name}:\n\n"

    probs = model.predict_proba(info)[0]
    up_prob = round(probs[1], 2)
    down_prob = round(probs[0], 2)
    if up_prob > 0.7:
        result += f"Probabilidade de ALTA para amanhã: {up_prob}\n"
        result += f"Ação: COMPRAR\n\n"

    elif up_prob > 0.4:
        result += f"Probabilidade incerta, com chance para alta de: {up_prob}\n"
        result += f"Ação: MANTER\n\n"

    else:
        result += f"Probabilidade de BAIXA para amanhã: {down_prob}\n"
        result += f"Ação: VENDER.\n\n"

    name = f"sequential_brl_{nvers}s"
    result += f"Analise de resultados por {name}:\n"
    # load json and create model
    json_file = open(f"Bitcoin/{name}.json", "r")
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    # load weights into new model
    try:
        model.load_weights(f"Bitcoin/{name}.h5")
    except:
        pass

    probs = model.predict_proba(info)[0]
    up_prob = round(probs[1], 2)
    down_prob = round(probs[0], 2)
    if up_prob > 0.7:
        result += f"Probabilidade de ALTA para amanhã: {up_prob}\n"
        result += f"Ação: COMPRAR\n\n"

    elif up_prob > 0.4:
        result += f"Probabilidade incerta, com chance para alta de: {up_prob}\n"
        result += f"Ação: MANTER\n\n"

    else:
        result += f"Probabilidade de BAIXA para amanhã: {down_prob}\n"
        result += f"Ação: VENDER.\n\n"
    return result
