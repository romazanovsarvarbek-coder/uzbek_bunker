# 🏚 «Bunker» Telegram Boti (aiogram 3.x + Vercel Serverless)

Guruhlarda o'ynaladigan psixologik **«Bunker»** o'yini uchun to'liq avtomatlashtirilgan, o'zbek tilidagi Telegram bot.

Bot havolasi: [@uzbek_bunker_bot](https://t.me/uzbek_bunker_bot)

## 📁 Loyiha tuzilmasi

```text
uzbek bunker/
├── api/
│   └── webhook.py       # Vercel serverless FastAPI webhook handler
├── bot/
│   ├── __init__.py
│   ├── config.py        # Token va asosiy sozlamalar
│   ├── data.py          # 20 kasb, 20 sog'liq, 20 buyum, 10 fobiya, 10 falokat
│   ├── state.py         # Har bir guruh uchun izolyatsiyalangan In-Memory holat
│   ├── keyboards.py     # Inline tugmalar (lobi, ovoz berish, PM havola)
│   └── handlers.py      # Buyruqlar va callback_query handlerlari
├── requirements.txt     # Kerakli Python kutubxonalari
├── vercel.json          # Vercel marshrutlash sozlamasi
└── .env.example         # Muhit o'zgaruvchilari namunasi
```

## 🚀 Vercel'ga yuklash (Deploy)

1. Loyihani GitHub'ga yuklang yoki Vercel CLI orqali deploy qiling:
   ```bash
   vercel --prod
   ```
2. Vercel Dashboard -> **Settings -> Environment Variables** bo'limida quyidagi o'zgaruvchini qo'shing (ixtiyoriy, `bot/config.py` da ham standart qiymat bor):
   - `BOT_TOKEN` = `9031082623:AAG1msrdrTEUHivJVk4nyJqHxJvZNSLDdWE`
   - `BOT_USERNAME` = `uzbek_bunker_bot`
3. Deploy tugagach, brauzerda quyidagi manzilni bir marta oching (webhook avtomatik ulanadi):
   ```text
   https://<sizning-loyihangiz>.vercel.app/api/webhook?setup=1
   ```
   Yoki `curl` orqali:
   ```bash
   curl "https://api.telegram.org/bot9031082623:AAG1msrdrTEUHivJVk4nyJqHxJvZNSLDdWE/setWebhook?url=https://<sizning-loyihangiz>.vercel.app/api/webhook"
   ```

## 🎮 O'yin buyruqlari

- `/bunker` — Guruhda yangi o'yin lobisini ochish (kamida 4 kishi kerak)
- `/kengash` — Muhokama raundini boshlash (boshlovchi/admin)
- `/ovozberish` — Tirik o'yinchilar orasida haydash uchun ovoz berish (boshlovchi/admin)
- `/holat` — Joriy o'yin holatini ko'rish
- `/bekor` — Faol o'yinni to'xtatish (boshlovchi/admin)
- `/qoidalar` — O'yin qoidalari

> ⚠️ **Eslatma:** Vercel serverless muhitida `In-Memory` xotira sovuq start (cold start) paytida tozalanishi mumkin. Faol o'yin davomida Vercel funksiyasi iliq (warm) holatda ishlaydi.

