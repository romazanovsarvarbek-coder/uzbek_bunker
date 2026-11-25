"""Bunker o'yini uchun random generatsiya ma'lumotlar bazasi."""

PROFESSIONS: list[str] = [
    "Jarroh shifokor",
    "Harbiy muhandis",
    "Agronom (dehqonchilik mutaxassisi)",
    "Elektr energetigi",
    "Dasturchi va kiberxavfsizlik mutaxassisi",
    "Oshpaz-texnolog",
    "Psixolog",
    "Qurilish ustasi (payvandchi)",
    "Kimyogar-biolog",
    "O't o'chiruvchi va qutqaruvchi",
    "Musiqachi (gitarist)",
    "TikTok bloger",
    "Sartarosh-stilist",
    "Professional bokschi",
    "Tarix o'qituvchisi",
    "Moliya va soliq maslahatchisi",
    "Uchuvchi (pilot)",
    "Santexnik va quvur ustasi",
    "Veterinar shifokor",
    "Zargar",
]

HEALTH_CONDITIONS: list[str] = [
    "Mutlaqo sog'lom (temirdek immunitet)",
    "Yengil miopiya (ko'zoynaksiz uzoqni yaxshi ko'rmaydi)",
    "Surunkali astma (inhalatorga muhtoj)",
    "Qandli diabet (1-tur, insulin talab qilinadi)",
    "Yuqori qon bosimi (gipertoniya)",
    "Bepushtlik (nasl qoldira olmaydi)",
    "Ranglarni ajrata olmaslik (daltonizm)",
    "Surunkali uyqusizlik (insomniya)",
    "Qattiq allergiya (chang va gul changiga)",
    "Chap oyog'i protez (lekin bemalol yuradi)",
    "Yurak yetishmovchiligi (og'ir jismoniy yuklama mumkin emas)",
    "Kar-soqovlik (faqat imo-ishora bilan muloqot qiladi)",
    "Tez-tez tutqanoq tutishi (epilepsiya)",
    "Oshqozon yarasi (qat'iy parhez zarur)",
    "Ruhiy beqarorlik (stressda vahimaga tushadi)",
    "A'lo darajadagi jismoniy tayyorgarlik (sportchi)",
    "Qon ivishining buzilishi (gemofiliya)",
    "Migren (kuchli bosh og'rig'i xurujlari)",
    "Radiatsiyaga yuqori chidamlilik (noyob genetika)",
    "Sil kasalligining boshlang'ich bosqichi",
]

ITEMS: list[str] = [
    "Ko'p funksiyali Shveytsariya pichog'i",
    "10 litr toza ichimlik suvi va suv filtri",
    "Birinchi tibbiy yordam qutisi (to'liq to'plam)",
    "Quyosh batareyali portativ quvvatlagich (Powerbank)",
    "Gaz niqobi (protivogaz) va 3 ta zaxira filtr",
    "Sabzavot va don ekinlari urug'lari to'plami",
    "Ratsiya (2 ta) va zaxira batareykalar",
    "Kuchli LED fonar va gugurt qutisi",
    "5 kg quritilgan go'sht va konserva mahsulotlari",
    "Anatomiya va tibbiyot bo'yicha ensiklopediya",
    "PlayStation 5 (joystiklar bilan, televizorsiz)",
    "100 ta havo shari va nasos",
    "Bir juft qishki chang'i",
    "Qog'ozli monopoliya stol o'yini",
    "10 million so'mlik naqd pul to'plami",
    "Katta yumshoq ayiqcha o'yinchog'i",
    "Qopqog'i yo'q bo'sh shisha banka",
    "50 metrli pishiq arqon va karabinlar",
    "Spirtli antiseptik (5 litr)",
    "Mushuk uchun quruq ovqat (3 kg)",
]

PHOBIAS: list[str] = [
    "Klaustrofobiya — yopiq va tor joylardan qo'rqish",
    "Niktofobiya — qorong'ulikdan dahshatga tushish",
    "Gemofobiya — qon ko'rishdan hushidan ketish",
    "Araxnofobiya — o'rgimchak va hasharotlardan qo'rqish",
    "Agorafobiya — ochiq maydon va olomondan qo'rqish",
    "Akrofobiya — balandlikdan qo'rqish",
    "Mizofobiya — mikroblar va kirlikdan vahimaga tushish",
    "Tanatofobiya — o'lim va jasadlardan haddan tashqari qo'rqish",
    "Antropofobiya — notanish odamlarga ishonmaslik va qo'rqish",
    "Fobiyasi yo'q — temir asabli inson",
]

CATASTROPHES: list[dict[str, str]] = [
    {
        "title": "🧟 Zombi apokalipsisi",
        "description": (
            "Noma'lum virus butun dunyoga tarqaldi. Yuqtirgan odamlar aqlini yo'qotib, "
            "tajovuzkor zombilarga aylanmoqda. Tashqarida har bir qadam xavf ostida. "
            "Bunkerda kamida 1 yil yashab qolish va virusga qarshi najot topish kerak."
        ),
    },
    {
        "title": "☢️ Yadro urushi",
        "description": (
            "Yirik davlatlar o'rtasidagi mojaro yadroviy zarbalar bilan yakunlandi. "
            "Yer yuzi radiatsiya bulutlari bilan qoplangan, yadroviy qish boshlandi. "
            "Tashqariga himoya kiyimisiz chiqish o'limga teng. Bunkerda 3 yil omon qolish zarur."
        ),
    },
    {
        "title": "👽 O'zga sayyoraliklar bosqini",
        "description": (
            "Kosmosdan kelgan noma'lum sivilizatsiya yirik shaharlarni vayron qilmoqda. "
            "Ular tirik odamlarni ovlayapti va aloqa tizimlarini o'chirib qo'ygan. "
            "Bunker yagona yashirinish joyi — ichkarida tartib va hushyorlik eng muhim."
        ),
    },
    {
        "title": "🌊 Global suv toshqini",
        "description": (
            "Muzliklarning keskin erishi natijasida okean sathi ko'tarilib, "
            "materiklarning katta qismini suv bosdi. Bunker baland tog' bag'rida joylashgan "
            "va suv o'tkazmaydi, ammo zaxiralar cheklangan."
        ),
    },
    {
        "title": "☀️ Quyosh portlashi (Superchaqnash)",
        "description": (
            "Quyoshdagi kuchli magnit bo'roni Yerning elektronikasini ishdan chiqardi "
            "va atmosfera qatlamini zaiflashtirdi. Kunduzi harorat +70°C gacha ko'tarilmoqda. "
            "Faqat yer osti bunkerida salqinlik va hayot saqlanib qolgan."
        ),
    },
    {
        "title": "☄️ Asteroid qulashi",
        "description": (
            "Ulkan asteroid Yerga urilib, osmonni qalin chang va kul qatlami qopladi. "
            "Quyosh nuri deyarli o'tmayapti, ekinlar nobud bo'lgan, havo harorati -40°C. "
            "Bunkerda issiqlik va oziq-ovqatni saqlab qolish hayot-mamot masalasi."
        ),
    },
    {
        "title": "🤖 Sun'iy intellekt qo'zg'oloni",
        "description": (
            "Harbiy va sanoat tizimlarini boshqargan sun'iy intellekt insoniyatga qarshi "
            "urush e'lon qildi. Dronlar va robotlar yer yuzini nazorat qilmoqda. "
            "Bunker eski analog tizimda ishlaydi va hozircha aniqlanmagan."
        ),
    },
    {
        "title": "🌋 Supervulkan otilishi",
        "description": (
            "Sayyoradagi eng yirik supervulkan uyg'onib, minglab kilometr hududni "
            "zaharli gaz va vulqon kuli bilan qopladi. Havo nafas olish uchun yaroqsiz. "
            "Bunkerning havo filtrlash tizimi cheklangan odamlar uchungina yetarli."
        ),
    },
    {
        "title": "🦠 O'ta xavfli pandemiya",
        "description": (
            "Havo-tomchi yo'li bilan 100% yuqadigan va davosi hali topilmagan kasallik "
            "butun shaharni qamrab oldi. Bunker to'liq germetik izolyatsiyada. "
            "Ichkariga kasallik tashuvchilarni kiritmaslik va sog'lom jamoa tuzish shart."
        ),
    },
    {
        "title": "❄️ Yangi muzlik davri",
        "description": (
            "Gulfstrim oqimi to'xtab, iqlim keskin sovib ketdi. Butun mintaqa qalin muz "
            "va qor ostida qoldi. Tashqarida bo'ron tinmayapti. Bunkerda energiya va "
            "issiq saqlash uchun eng foydali mutaxassislar qolishi kerak."
        ),
    },
]

