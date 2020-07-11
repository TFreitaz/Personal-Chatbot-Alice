from robobrowser import RoboBrowser
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from statsmodels.tsa.api import SimpleExpSmoothing, Holt, ExponentialSmoothing
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.vector_ar.var_model import VAR
from keras.models import model_from_json
import numpy as np
import statsmodels.api as sm
import time
import pickle


def turnFloat(x):
    x = x.replace(".", "").replace(",", ".")
    return float(x)


def into(item):
    return item[0]


def numerize(num):
    if str(num).lower() == "nan":
        return 0
    else:
        return num


def play(nvers=166, plot=True):
    today = time.localtime()
    day = str(today.tm_mday)
    if len(day) == 1:
        day = "0" + day
    mon = str(today.tm_mon)
    if len(mon) == 1:
        mon = "0" + mon
    year = str(today.tm_year)[-2:]
    date = f"{day}/{mon}/{year}"

    hist = {"date": [], "val": []}

    df = pd.read_csv("data.csv")

    browser = RoboBrowser(parser="html.parser")
    skip = False
    for i in range(61):
        url = f"https://br.advfn.com/bolsa-de-valores/coin/BTCUSD/historico/mais-dados-historicos?current={i}&Date1=01/01/90&Date2={date}"
        try:
            browser.open(url)
        except:
            break
        else:
            rows = browser.find_all(class_="result")
            for row in rows:
                info = row.find_all("td")
                date = info[0].text
                if date not in df["date"].values:
                    val = turnFloat(info[1].text)
                    hist["date"].append(date)
                    hist["val"].append(val)
                else:
                    skip = True
                    break
        if skip:
            break

    hist["date"] = hist["date"][::-1]
    hist["val"] = hist["val"][::-1]

    df = pd.concat([df, pd.DataFrame(hist)], ignore_index=True)
    df.to_csv("data.csv", index=False)

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
        plt.savefig("bitgraphic.png")

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

    name = f"gradient_{nvers}s"
    model = pickle.load(open(f"{name}.sav", "rb"))
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

    name = f"sequential_{nvers}s"
    result += f"Analise de resultados por {name}:\n"
    # load json and create model
    json_file = open(f"{name}.json", "r")
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    # load weights into new model
    try:
        model.load_weights(f"{name}.h5")
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
