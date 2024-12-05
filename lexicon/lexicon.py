LEXICON: dict[str, str] = {
    "/start": """<b>Добро пожаловать в обменник Green!</b>

Это бот для покупки и продажи криптовалюты!""",

    "buy_answer": """Количество криптовалюты: {crypto_count} {crypto}
По курсу: {price_by_unit}

К оплате: {payment} рублей


            <b>🛑Важно🛑</b>

При переводе вписываем в комментарии кодовую фразу “Покупка Tether(USDT)”

Для обмена отпишите нашему оператору 

@Green_exch_operator""",

    "sell_answer": """
Вы получите: {get_price}

К оплате : {payment} {crypto}

Пришлите нашему оператору номер карты с указанием банка, а также СБП (привязанный номер)

@Green_exch_operator""",

    "support": """По вопросам можете обращаться к нашему оператору!
@Green_exch_operator""",

    "200k_order": """Для обмена на сумму больше чем  200000 рублей отпишите нашему оператору 
@Green_exch_operator"""

}

LEXICON_COMMANDS: dict[str, str] = {
    "/start": "Перезапустить бота"
}

LEXICON_MENU: dict[str, str] = {
    "buy": "Купить 💰",
    "sell": "Продать 📈",
    "support": "Поддержка 👥"
}
