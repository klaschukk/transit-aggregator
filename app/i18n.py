"""
Simple i18n system for Prevozni.

Usage in templates:  {{ _('nav.all_routes') }}
Usage in Python:     from app.i18n import get_text; get_text('nav.all_routes', 'en')

Supported languages: sr (default), en, ru, bg

bg coverage is partial by design (~200 keys — nav/footer/common UI chrome,
buy/filter/search, route_detail + city_pair + search_results, PWA install
prompt) added 2026-09 alongside the Bulgaria-domestic + Bulgaria<->Greece
routes (union-ivkoni.com). get_text() falls back to 'sr' for any key
without a 'bg' entry — never a raw key or a blank string — so an
untranslated corner of the site (guides, legal pages, city-transport
detail pages) degrades to Serbian rather than breaking. Extend bg
coverage over time; there's no flag or TODO list to track it beyond
grepping for "'bg':" in this file.
"""

TRANSLATIONS: dict[str, dict[str, str]] = {
    # ── Navigation ──
    'nav.all_routes': {
        'sr': 'Sve rute',
        'en': 'All routes',
        'ru': 'Все маршруты',
        'bg': 'Всички маршрути',
    },
    'nav.city_transport': {
        'sr': 'Gradski prevoz',
        'en': 'City transport',
        'ru': 'Городской транспорт',
        'bg': 'Градски транспорт',
    },
    'nav.search': {
        'sr': 'Pretraga',
        'en': 'Search',
        'ru': 'Поиск',
        'bg': 'Търсене',
    },
    'nav.about': {
        'sr': 'O nama',
        'en': 'About',
        'ru': 'О нас',
        'bg': 'За нас',
    },
    'nav.menu': {
        'sr': 'Meni',
        'en': 'Menu',
        'ru': 'Меню',
        'bg': 'Меню',
    },
    'a11y.mobile_nav': {
        'sr': 'Donja navigacija',
        'en': 'Bottom navigation',
        'ru': 'Нижняя навигация',
        'bg': 'Долна навигация',
    },
    'nav.home': {
        'sr': 'Početna',
        'en': 'Home',
        'ru': 'Главная',
        'bg': 'Начало',
    },
    'nav.routes': {
        'sr': 'Rute',
        'en': 'Routes',
        'ru': 'Маршруты',
        'bg': 'Маршрути',
    },
    'nav.city': {
        'sr': 'Gradski',
        'en': 'City',
        'ru': 'Город',
        'bg': 'Градски',
    },
    'nav.saved': {
        'sr': 'Sačuvano',
        'en': 'Saved',
        'ru': 'Избранное',
        'bg': 'Запазено',
    },
    'nav.more': {
        'sr': 'Više',
        'en': 'More',
        'ru': 'Ещё',
        'bg': 'Още',
    },
    'a11y.bottom_nav': {
        'sr': 'Glavna mobilna navigacija',
        'en': 'Primary mobile navigation',
        'ru': 'Основная мобильная навигация',
        'bg': 'Основна мобилна навигация',
    },
    'browse.title': {
        'sr': 'Pregledaj sve',
        'en': 'Browse all',
        'ru': 'Смотреть все',
        'bg': 'Разгледай всички',
    },
    'browse.routes': {
        'sr': 'Sve rute',
        'en': 'All routes',
        'ru': 'Все маршруты',
    },
    'browse.routes_meta': {
        'sr': 'Međugradski autobusi i vozovi',
        'en': 'Intercity buses and trains',
        'ru': 'Междугородние автобусы и поезда',
    },
    'browse.cities': {
        'sr': 'Gradski prevoz',
        'en': 'City transport',
        'ru': 'Городской транспорт',
    },
    'browse.cities_meta': {
        'sr': 'Beograd, Novi Sad, Niš, Kragujevac, Podgorica, Budva, Herceg Novi',
        'en': 'Beograd, Novi Sad, Niš, Kragujevac, Podgorica, Budva, Herceg Novi',
        'ru': 'Белград, Нови-Сад, Ниш, Крагуевац, Подгорица, Будва, Херцег-Нови',
    },
    'browse.carriers': {
        'sr': 'Prevoznici',
        'en': 'Carriers',
        'ru': 'Перевозчики',
    },
    'browse.carriers_meta': {
        'sr': 'Lasta, Niš-Ekspres, OZLEM i drugi',
        'en': 'Lasta, Niš-Ekspres, OZLEM and others',
        'ru': 'Lasta, Niš-Ekspres, OZLEM и другие',
    },
    'browse.stations': {
        'sr': 'Autobuske stanice',
        'en': 'Bus stations',
        'ru': 'Автобусные станции',
    },
    'browse.stations_meta': {
        'sr': 'Polasci, adrese, šalteri',
        'en': 'Departures, addresses, ticket counters',
        'ru': 'Отправления, адреса, кассы',
    },
    'browse.destinations': {
        'sr': 'Destinacije',
        'en': 'Destinations',
        'ru': 'Направления',
    },
    'browse.destinations_meta': {
        'sr': 'Crna Gora, Bosna, Hrvatska i druge',
        'en': 'Montenegro, Bosnia, Croatia and others',
        'ru': 'Черногория, Босния, Хорватия и другие',
    },

    # ── Footer ──
    'footer.desc': {
        'sr': 'Red vožnje autobusa, tramvaja i vozova u Srbiji. Besplatno, bez registracije.',
        'en': 'Bus, tram and train schedules in Serbia. Free, no registration.',
        'ru': 'Расписание автобусов, трамваев и поездов в Сербии. Бесплатно, без регистрации.',
        'bg': 'Разписания на автобуси, трамваи и влакове в Сърбия. Безплатно, без регистрация.',
    },
    'footer.navigation': {
        'sr': 'Navigacija',
        'en': 'Navigation',
        'ru': 'Навигация',
        'bg': 'Навигация',
    },
    'footer.popular_routes': {
        'sr': 'Popularne rute',
        'en': 'Popular routes',
        'ru': 'Популярные маршруты',
        'bg': 'Популярни маршрути',
    },
    'footer.cities': {
        'sr': 'Gradovi',
        'en': 'Cities',
        'ru': 'Города',
        'bg': 'Градове',
    },
    'footer.carriers': {
        'sr': 'Prevoznici',
        'en': 'Carriers',
        'ru': 'Перевозчики',
        'bg': 'Превозвачи',
    },
    'footer.stations': {
        'sr': 'Stanice',
        'en': 'Stations',
        'ru': 'Станции',
        'bg': 'Автогари',
    },
    'footer.about': {
        'sr': 'O nama',
        'en': 'About us',
        'ru': 'О нас',
        'bg': 'За нас',
    },
    'footer.contact': {
        'sr': 'Kontakt',
        'en': 'Contact',
        'ru': 'Контакт',
        'bg': 'Контакти',
    },
    'footer.copyright': {
        'sr': 'Sva prava zadržana.',
        'en': 'All rights reserved.',
        'ru': 'Все права защищены.',
        'bg': 'Всички права запазени.',
    },
    'footer.privacy': {
        'sr': 'Privatnost',
        'en': 'Privacy',
        'ru': 'Конфиденциальность',
        'bg': 'Поверителност',
    },
    'privacy.title': {
        'sr': 'Politika privatnosti',
        'en': 'Privacy Policy',
        'ru': 'Политика конфиденциальности',
        'bg': 'Политика за поверителност',
    },
    'privacy.intro': {
        'sr': 'Prevozni poštuje vašu privatnost. Ova stranica objašnjava koje podatke prikupljamo i kako ih koristimo.',
        'en': 'Prevozni respects your privacy. This page explains what data we collect and how we use it.',
        'ru': 'Prevozni уважает вашу конфиденциальность. Здесь описано, какие данные мы собираем и как используем.',
        'bg': 'Prevozni уважава вашата поверителност. Тази страница обяснява какви данни събираме и как ги използваме.',
    },
    'privacy.cookies_h': {
        'sr': 'Kolačići',
        'en': 'Cookies',
        'ru': 'Cookies',
        'bg': 'Бисквитки',
    },
    'privacy.cookies_ab_h': {
        'sr': 'A/B testiranje',
        'en': 'A/B testing',
        'ru': 'A/B-тестирование',
        'bg': 'A/B тестване',
    },
    'privacy.cookies_ab_body': {
        'sr': 'Da bismo merili koje varijante stranica daju bolje iskustvo, '
              'koristimo prvi kolačić <code>ab_v1</code> (1 godina). On '
              'sadrži samo nasumičan identifikator i ne povezuje se ni sa '
              'jednim ličnim podatkom.',
        'en': 'To measure which page variants deliver a better experience, '
              'we set a first-party <code>ab_v1</code> cookie (1 year). It '
              'contains only a random identifier and is not linked to any '
              'personal data.',
        'ru': 'Чтобы понять какие варианты страниц работают лучше, мы '
              'устанавливаем cookie <code>ab_v1</code> (на 1 год). В нём '
              'хранится только случайный идентификатор, не связанный ни с '
              'какими личными данными.',
        'bg': 'За да измерваме кои варианти на страниците дават по-добро изживяване, използваме бисквитка от първа страна <code>ab_v1</code> (1 година). Тя съдържа само случаен идентификатор и не се свързва с никакви лични данни.',
    },
    'privacy.cookies_body': {
        'sr': 'Koristimo samo neophodne kolačiće (npr. CSRF token). Ne koristimo reklamne niti praćeće kolačiće trećih strana.',
        'en': 'We use only essential cookies (e.g. CSRF token). No third-party advertising or tracking cookies.',
        'ru': 'Мы используем только необходимые cookies (например, CSRF-токен). Никаких рекламных или трекинговых cookies третьих сторон.',
        'bg': 'Използваме само необходими бисквитки (напр. CSRF токен). Не използваме рекламни, нито проследяващи бисквитки на трети страни.',
    },
    'privacy.analytics_h': {
        'sr': 'Analitika',
        'en': 'Analytics',
        'ru': 'Аналитика',
        'bg': 'Аналитика',
    },
    'privacy.analytics_body': {
        'sr': 'Koristimo Umami analitiku — anonimne, agregirane statistike poseta bez kolačića i bez praćenja pojedinaca.',
        'en': 'We use Umami analytics — anonymous, aggregated page view statistics with no cookies and no individual tracking.',
        'ru': 'Мы используем Umami — анонимную агрегированную статистику посещений без cookies и отслеживания пользователей.',
        'bg': 'Използваме аналитиката Umami — анонимна, агрегирана статистика за посещенията без бисквитки и без проследяване на отделни лица.',
    },
    'privacy.contact_h': {
        'sr': 'Kontakt forma',
        'en': 'Contact form',
        'ru': 'Контактная форма',
        'bg': 'Контактна форма',
    },
    'privacy.contact_body': {
        'sr': 'Poruke iz kontakt forme se šalju preko Telegram bota i čuvaju u logovima radi odgovora. Ne delimo ih sa trećim stranama.',
        'en': 'Messages from the contact form are sent via a Telegram bot and stored in logs so we can reply. They are not shared with third parties.',
        'ru': 'Сообщения из контактной формы отправляются через Telegram-бот и сохраняются в логах для ответа. Третьим лицам не передаются.',
        'bg': 'Съобщенията от контактната форма се изпращат чрез Telegram бот и се съхраняват в логове с цел отговор. Не ги споделяме с трети страни.',
    },
    'privacy.rights_h': {
        'sr': 'Vaša prava (GDPR)',
        'en': 'Your rights (GDPR)',
        'ru': 'Ваши права (GDPR)',
        'bg': 'Вашите права (GDPR)',
    },
    'privacy.rights_body': {
        'sr': 'Imate pravo pristupa, ispravke i brisanja podataka. Za zahteve pišite na info@prevozni.com.',
        'en': 'You have the right to access, rectify and erase your data. Email info@prevozni.com for requests.',
        'ru': 'Вы имеете право на доступ, исправление и удаление данных. Запросы — на info@prevozni.com.',
        'bg': 'Имате право на достъп, коригиране и заличаване на данни. За заявки пишете на info@prevozni.com.',
    },
    'footer.disclaimer': {
        'sr': 'Podaci su informativnog karaktera i preuzeti iz javno dostupnih izvora. Prevozni ne garantuje tačnost podataka — uvek proverite red vožnje direktno kod prevoznika. Ovaj sajt ne prodaje karte niti posreduje u prodaji prevoznih usluga.',
        'en': 'Data is for informational purposes and sourced from publicly available sources. Prevozni does not guarantee data accuracy — always check the schedule directly with the carrier. This site does not sell tickets.',
        'ru': 'Данные носят информационный характер и получены из открытых источников. Prevozni не гарантирует точность данных — всегда проверяйте расписание у перевозчика. Сайт не продает билеты.',
        'bg': 'Данните са с информативен характер и са взети от публично достъпни източници. Prevozni не гарантира точността на данните — винаги проверявайте разписанието директно при превозвача. Този сайт не продава билети и не е посредник в продажбата на транспортни услуги.',
    },

    # ── Homepage ──
    'home.title': {
        'sr': 'Prevozni — Red Vožnje Srbija 2026: Autobus i Voz',
        'en': 'Prevozni — Serbia Bus & Train 2026: Schedules & Prices',
        'ru': 'Prevozni — Автобусы Сербии 2026: Расписание и Цены',
        'bg': 'Prevozni — Автобуси и влакове в Сърбия 2026: Разписания и цени',
    },
    'home.meta': {
        'sr': 'Autobus i voz između gradova Srbije — red vožnje, cene od 350 din, 500+ ruta. Beograd, Novi Sad, Niš i region. Pronađi besplatno →',
        'en': 'Bus and train in Serbia 2026 — schedules, prices from 350 RSD, 500+ routes. Belgrade, Novi Sad, Niš. Find for free →',
        'ru': 'Автобусы и поезда по Сербии 2026 — расписание, цены от 350 din, 500+ маршрутов. Белград, Нови-Сад, Ниш. Бесплатно →',
        'bg': 'Автобус и влак в Сърбия 2026 — разписания, цени от 350 RSD, 500+ маршрута. Белград, Нови Сад, Ниш. Намерете безплатно →',
    },
    'about.title_suffix': {
        'sr': 'Prevozni Srbija, misija i kontakt',
        'en': 'Prevozni Serbia, mission and contact',
        'ru': 'Prevozni Сербия, миссия и контакт',
        'bg': 'Prevozni Сърбия, мисия и контакт',
    },
    'contact.meta': {
        'sr': 'Imate pitanje, sugestiju ili ste primetili grešku na Prevozni? Pišite nam na info@prevozni.com ili popunite kontakt formu. Odgovaramo u roku od 48 sati.',
        'en': 'Got a question, suggestion or spotted a bug on Prevozni? Email info@prevozni.com or use the contact form. We reply within 48 hours.',
        'ru': 'Есть вопрос, предложение или заметили ошибку на Prevozni? Напишите на info@prevozni.com или заполните контактную форму. Отвечаем в течение 48 часов.',
        'bg': 'Имате въпрос, предложение или сте забелязали грешка на Prevozni? Пишете ни на info@prevozni.com или попълнете контактната форма. Отговаряме в рамките на 48 часа.',
    },
    'about.what_h': {
        'sr': 'Šta je Prevozni',
        'en': 'What is Prevozni',
        'ru': 'Что такое Prevozni',
    },
    'about.what_p1': {
        'sr': 'Prevozni je <strong>besplatni agregator</strong> podataka o javnom prevozu u Srbiji i regionu — međugradske autobuske rute, vozovi Srbija Voza, gradski prevoz u Beogradu, Novom Sadu, Nišu i Kragujevcu, i izabrani polasci za Crnu Goru, Bosnu, Hrvatsku i druge balkanske zemlje. Naš cilj: pokazati kada i odakle možete da putujete, po kojoj ceni i sa kojim prevoznikom — bez reklama koje sakrivaju podatke, bez obaveze registracije, na srpskom, engleskom i ruskom.',
        'en': 'Prevozni is a <strong>free aggregator</strong> of public transit data for Serbia and the region — intercity bus routes, Srbija Voz trains, city transport in Belgrade, Novi Sad, Niš and Kragujevac, and selected departures to Montenegro, Bosnia, Croatia and other Balkan countries. Our goal: show when and from where you can travel, at what price and with which carrier — with no ad walls hiding data, no account required, in Serbian, English and Russian.',
        'ru': 'Prevozni — это <strong>бесплатный агрегатор</strong> данных об общественном транспорте Сербии и региона: междугородние автобусные маршруты, поезда Srbija Voz, городской транспорт в Белграде, Нови-Саде, Нише и Крагуеваце, а также отдельные рейсы в Черногорию, Боснию, Хорватию и другие страны Балкан. Наша цель — показать когда и откуда можно уехать, по какой цене и с каким перевозчиком — без рекламных стен, без регистрации, на сербском, английском и русском.',
    },
    'about.what_p2': {
        'sr': 'Mi ne prodajemo karte i ne naplaćujemo pretragu. Kupovina se obavlja direktno na sajtovima prevoznika ili preko partnera BusTicket4.me. Kada kliknete na dugme "Kupi" pored polaska, bićete prebačeni na sajt partnera — on prodaje kartu, a Prevozni može da dobije malu proviziju koja pokriva troškove održavanja sajta. Pregled raspored, poređenje prevoznika i cena ostaju besplatni.',
        'en': 'We don\'t sell tickets and we don\'t charge for search. Purchase happens directly on the carrier\'s site or via a partner (BusTicket4.me). When you click "Buy" next to a departure you are taken to the partner\'s site — they sell the ticket, and Prevozni may receive a small commission that covers the cost of running this site. Browsing schedules, comparing carriers and prices stays free.',
        'ru': 'Мы не продаём билеты и не берём деньги за поиск. Покупка происходит напрямую на сайте перевозчика или через партнёра BusTicket4.me. При клике на кнопку "Купить" рядом с рейсом вы попадаете на сайт партнёра — он продаёт билет, а Prevozni может получить небольшую комиссию, которая покрывает расходы на работу сайта. Просмотр расписаний, сравнение перевозчиков и цен остаются бесплатными.',
    },
    'about.sources_h': {
        'sr': 'Odakle dolaze podaci',
        'en': 'Where the data comes from',
        'ru': 'Откуда берутся данные',
        'bg': 'Откъде идват данните',
    },
    'contact.intro_h': {
        'sr': 'Kako da nam pišete',
        'en': 'How to reach us',
        'ru': 'Как с нами связаться',
        'bg': 'Как да ни пишете',
    },
    'contact.intro_p1': {
        'sr': 'Najbrži način: <strong>info@prevozni.com</strong>. Možete i da koristite formu ispod — poruka stiže u isti inbox + automatski u naš Telegram kanal za operativne stvari, pa je odgovor obično u roku od 24 sata (radnim danima) ili do 48 sati (vikendom i praznicima).',
        'en': 'Fastest channel: <strong>info@prevozni.com</strong>. You can also use the form below — it lands in the same inbox plus our ops Telegram channel, so typical response time is within 24 hours on weekdays, up to 48 hours on weekends and holidays.',
        'ru': 'Самый быстрый канал: <strong>info@prevozni.com</strong>. Также можно использовать форму ниже — сообщение попадает в тот же ящик плюс в наш оперативный Telegram-канал, поэтому обычно отвечаем в течение 24 часов по будням и до 48 часов по выходным и праздникам.',
        'bg': 'Най-бързият начин: <strong>info@prevozni.com</strong>. Можете също да използвате формата по-долу — съобщението пристига в същата пощенска кутия + автоматично в нашия Telegram канал за оперативни въпроси, така че отговорът обикновено е в рамките на 24 часа (в работни дни) или до 48 часа (през уикенди и празници).',
    },
    'privacy.cookies_body2': {
        'sr': 'Koristimo isključivo kolačiće prve strane (eng. first-party cookies) za čuvanje vaših preferenci (jezik sajta, valuta za cene, sačuvane rute). Ne postavljamo marketinške kolačiće trećih strana, ne pratimo vas na drugim sajtovima, ne gradimo vaš profil za prodaju oglasnih agencija.',
        'en': 'We only use first-party cookies to remember your preferences (site language, currency display, saved routes). We do not set third-party marketing cookies, do not track you across other sites, and do not build profiles for sale to ad networks.',
        'ru': 'Мы используем только first-party cookies для сохранения ваших настроек (язык сайта, валюта цен, сохранённые маршруты). Мы не ставим маркетинговые cookies третьих сторон, не отслеживаем вас на других сайтах и не строим профили для продажи рекламным сетям.',
        'bg': 'Използваме изключително бисквитки от първа страна (англ. first-party cookies) за съхраняване на вашите предпочитания (език на сайта, валута за цените, запазени маршрути). Не поставяме маркетингови бисквитки на трети страни, не ви проследяваме на други сайтове, не изграждаме ваш профил за продажба на рекламни агенции.',
    },
    'privacy.analytics_body2': {
        'sr': 'Za razumevanje kako ljudi koriste Prevozni koristimo Umami — privacy-first analitiku koja ne koristi kolačiće i ne prikuplja lične identifikatore. Umami beleži agregatne statistike (broj poseta po stranici, dolazni izvori, tip uređaja) ali ne povezuje događaje sa individualnim korisnikom. Svi podaci ostaju na našem serveru; ne šalju se Google Analytics-u ili drugim trećim stranama.',
        'en': 'To understand how people use Prevozni we use Umami — privacy-first analytics that does not use cookies and does not collect personal identifiers. Umami records aggregate statistics (visits per page, referrers, device type) but does not tie events to individual users. All data stays on our server; it is not sent to Google Analytics or any third party.',
        'ru': 'Чтобы понимать как люди пользуются Prevozni мы используем Umami — privacy-first аналитику, которая не использует cookies и не собирает персональные идентификаторы. Umami записывает агрегированную статистику (визиты по страницам, источники переходов, тип устройства), но не связывает события с конкретным пользователем. Все данные остаются на нашем сервере, они не отправляются в Google Analytics или другие третьи стороны.',
        'bg': 'За да разберем как хората използват Prevozni, използваме Umami — privacy-first аналитика, която не използва бисквитки и не събира лични идентификатори. Umami записва агрегирана статистика (брой посещения по страница, източници на трафик, тип устройство), но не свързва събитията с конкретен потребител. Всички данни остават на нашия сървър; не се изпращат към Google Analytics или други трети страни.',
    },
    'privacy.third_party_h': {
        'sr': 'Linkovi trećih strana',
        'en': 'Third-party links',
        'ru': 'Ссылки третьих сторон',
        'bg': 'Линкове на трети страни',
    },
    'privacy.third_party_body': {
        'sr': 'Prevozni sadrži linkove ka sajtovima prevoznika i partnera (BusTicket4.me i drugi). Kada kliknete na takav link, napuštate naš sajt i ulazite u politiku privatnosti tog partnera. Nismo odgovorni za njihove prakse — pročitajte njihovu politiku pre nego što unesete lične podatke ili kupite kartu. Mi možemo da dobijemo proviziju od partnera ako kupite preko linka sa našeg sajta; to nikad ne utiče na cenu koju vi plaćate.',
        'en': 'Prevozni contains links to carriers and partners (BusTicket4.me and others). When you click such a link you leave our site and enter that partner\'s privacy policy. We are not responsible for their practices — read their policy before entering personal data or buying a ticket. We may receive a commission from partners if you buy via a link on our site; this never affects the price you pay.',
        'ru': 'Prevozni содержит ссылки на сайты перевозчиков и партнёров (BusTicket4.me и другие). При клике на такую ссылку вы покидаете наш сайт и попадаете под политику конфиденциальности этого партнёра. Мы не отвечаем за их практики — прочитайте их политику перед вводом личных данных или покупкой билета. Мы можем получать комиссию от партнёров при покупке через нашу ссылку; это никак не влияет на цену которую вы платите.',
        'bg': 'Prevozni съдържа линкове към сайтовете на превозвачи и партньори (BusTicket4.me и други). Когато кликнете върху такъв линк, напускате нашия сайт и попадате под политиката за поверителност на съответния партньор. Ние не носим отговорност за техните практики — прочетете тяхната политика, преди да въведете лични данни или да купите билет. Възможно е да получим комисиона от партньора, ако купите чрез линк от нашия сайт; това никога не влияе на цената, която вие плащате.',
    },
    'privacy.affiliate_h': {
        'sr': 'Praćenje klikova na "Kupi" (BusTicket4.me)',
        'en': 'Tracking of "Buy" (BusTicket4.me) clicks',
        'ru': 'Отслеживание кликов по кнопке «Купить» (BusTicket4.me)',
        'bg': 'Проследяване на кликове върху „Купи“ (BusTicket4.me)',
    },
    'privacy.adsense_h': {
        'sr': 'Google AdSense (reklame)',
        'en': 'Google AdSense (advertising)',
        'ru': 'Google AdSense (реклама)',
        'bg': 'Google AdSense (реклами)',
    },
    'privacy.adsense_body': {
        'sr': 'Na nekim stranicama prikazujemo reklame preko Google AdSense. Ako ste prihvatili sve kolačiće, AdSense može da koristi kolačiće trećih strana za personalizaciju reklama na osnovu vaše istorije pregleda na drugim sajtovima. Ako ste izabrali samo osnovne kolačiće, AdSense radi u režimu neperonalizovanih reklama (requestNonPersonalizedAds) — reklame se biraju na osnovu sadržaja stranice, a ne vašeg profila. AdSense automatski dobija minimalne podatke o pregledu (IP, user-agent) prema njihovoj <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener nofollow">politici reklamiranja</a>. Možete da isključite personalizaciju u <a href="https://adssettings.google.com/" target="_blank" rel="noopener nofollow">Google Ads Settings</a> u bilo kom trenutku.',
        'en': 'On some pages we display ads through Google AdSense. If you accepted all cookies, AdSense may use third-party cookies to personalise ads based on your browsing history across other sites. If you accepted only essential cookies, AdSense runs in non-personalised mode (requestNonPersonalizedAds) — ads are picked based on page content, not your profile. AdSense automatically receives minimal request data (IP, user-agent) per their <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener nofollow">advertising policy</a>. You can opt out of personalisation in <a href="https://adssettings.google.com/" target="_blank" rel="noopener nofollow">Google Ads Settings</a> at any time.',
        'ru': 'На некоторых страницах мы показываем рекламу через Google AdSense. Если вы приняли все cookies, AdSense может использовать сторонние cookies для персонализации рекламы на основе истории просмотров на других сайтах. Если вы выбрали только основные cookies, AdSense работает в режиме неперсонализированной рекламы (requestNonPersonalizedAds) — реклама подбирается по содержанию страницы, а не по вашему профилю. AdSense автоматически получает минимальные данные запроса (IP, user-agent) согласно их <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener nofollow">политике рекламы</a>. Отключить персонализацию можно в любой момент в <a href="https://adssettings.google.com/" target="_blank" rel="noopener nofollow">Google Ads Settings</a>.',
        'bg': 'На някои страници показваме реклами чрез Google AdSense. Ако сте приели всички бисквитки, AdSense може да използва бисквитки на трети страни за персонализиране на реклами въз основа на вашата история на разглеждане на други сайтове. Ако сте избрали само основни бисквитки, AdSense работи в режим на неперсонализирани реклами (requestNonPersonalizedAds) — рекламите се избират въз основа на съдържанието на страницата, а не на вашия профил. AdSense автоматично получава минимални данни за прегледа (IP, user-agent) съгласно тяхната <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener nofollow">политика за реклами</a>. Можете да изключите персонализацията в <a href="https://adssettings.google.com/" target="_blank" rel="noopener nofollow">Google Ads Settings</a> по всяко време.',
    },
    'privacy.reviews_h': {
        'sr': 'Korisničke recenzije',
        'en': 'User reviews',
        'ru': 'Пользовательские отзывы',
        'bg': 'Потребителски отзиви',
    },
    'privacy.reviews_body': {
        'sr': 'Ako ostavite recenziju rute (dugme „Ostavite vašu recenziju" na stranici rute), čuvamo vašu ocenu, tekst komentara i ime koje ste uneli — oni se javno prikazuju nakon moderacije. Email adresu ne čuvamo u otvorenom obliku: sa nje računamo sha256 hash sa solju radi provere autorstva (za brisanje recenzije) i identifikacije „proverenih" autora koji su ranije objavili 3+ odobrene recenzije. Pored toga čuvamo jezik (sr/en/ru), anonimizovani hash IP adrese, i vreme slanja — isključivo za zaštitu od spama i auditing. U svakom trenutku možete da zatražite brisanje svoje recenzije dugmetom „Zatraži brisanje" ispod svake recenzije; potvrđujete uneti istu email adresu kojom ste prvobitno poslali, a naš moderator soft-briše zapis u roku od 7 dana u skladu sa GDPR-om.',
        'en': 'If you leave a route review (via the "Leave your review" form), we store your rating, comment text, and the name you entered — these are shown publicly after moderation. Your email address is never stored in cleartext: we compute a salted sha256 hash of it for authorship checks (so you can request deletion later) and to identify "trusted" authors who have previously posted 3+ approved reviews. We also keep the submission language (sr/en/ru), a salted IP hash, and the timestamp — only for spam protection and audit. You can request deletion any time via the "Request deletion" button under each review; you prove ownership by re-entering the same email, and our moderator soft-deletes the record within 7 days per GDPR.',
        'ru': 'Если вы оставите отзыв о маршруте (через форму «Оставить отзыв»), мы храним оценку, текст комментария и указанное имя — они публикуются после модерации. Email в открытом виде не храним: вычисляем sha256-хэш с солью, чтобы позже проверить авторство (при запросе удаления) и опознать «проверенных» авторов, у которых уже опубликовано 3+ одобренных отзыва. Также храним язык отправки (sr/en/ru), хэш IP и время отправки — только для защиты от спама и аудита. В любой момент можно запросить удаление кнопкой «Запросить удаление» под каждым отзывом; вы подтверждаете владение, указав тот же email, а модератор мягко удалит запись в течение 7 дней согласно GDPR.',
        'bg': 'Ако оставите отзив за маршрут (бутон „Оставете своя отзив“ на страницата на маршрута), съхраняваме вашата оценка, текста на коментара и името, което сте въвели — те се показват публично след модерация. Имейл адреса не съхраняваме в отворен вид: от него изчисляваме sha256 хеш със сол с цел проверка на авторството (за изтриване на отзива) и идентификация на „проверени“ автори, които преди това са публикували 3+ одобрени отзива. Освен това съхраняваме езика (sr/en/ru), анонимизиран хеш на IP адреса и времето на изпращане — единствено за защита от спам и одит. По всяко време можете да поискате изтриване на своя отзив чрез бутона „Заявете изтриване“ под всеки отзив; потвърждавате, като въведете същия имейл адрес, с който първоначално сте го изпратили, а нашият модератор меко изтрива записа в срок от 7 дни в съответствие с GDPR.',
    },
    'privacy.affiliate_body': {
        'sr': 'Kad kliknete na dugme "Kupi" koje vodi na BusTicket4.me, beležimo minimalni zapis o kliku na sopstvenom serveru: identifikator rute (npr. beograd-budva), tip stranice sa koje ste kliknuli (katalog, detalj rute, pretraga), prevoznika, vreme polaska, anonimizovani hash vaše IP adrese (sha256 sa sol-tajnom koja se redovno menja) i osnovne tehničke podatke pretraživača. Ne beležimo sirovu IP adresu, ime, email niti bilo šta što može direktno da vas identifikuje. Ove zapise čuvamo maksimalno 90 dana u interne svrhe — da znamo koji delovi sajta ljudima stvarno pomažu da nađu kartu i da pravilno pripišemo proviziju od BusTicket4.me-a. Isti zapisi se šalju i u našu analitiku (Umami) kao anonimni event "ba_click". Ako želite da vaši klikovi ne budu zabeleženi, uključite ad-blocker ili privatni mod u pretraživaču — naš sajt nastavlja da radi bez ovih zapisa.',
        'en': 'When you click a "Buy" button that goes to BusTicket4.me, we keep a minimal click record on our own server: the route identifier (e.g. beograd-budva), the page type the click came from (catalog, route detail, search), the carrier, departure time, a salted sha256 hash of your IP (salt rotates regularly) and basic browser technical data. We do not store raw IPs, names, emails or anything directly identifying you. These records are kept for at most 90 days and used internally to understand which parts of the site actually help people find a ticket and to correctly attribute BusTicket4.me commissions. The same events are mirrored to our analytics (Umami) as an anonymous "ba_click" event. If you prefer your clicks not to be recorded, use an ad-blocker or private browsing — the site works without these records.',
        'ru': 'Когда вы нажимаете кнопку «Купить», ведущую на BusTicket4.me, мы сохраняем на нашем сервере минимальную запись: идентификатор маршрута (например beograd-budva), тип страницы с которой был клик (каталог, детали маршрута, поиск), перевозчика, время рейса, анонимизированный sha256-хэш вашего IP с регулярно меняющейся солью и базовые технические данные браузера. Мы не храним сырой IP, имя, email или что-либо прямо вас идентифицирующее. Эти записи хранятся не более 90 дней и используются внутренне — чтобы понимать какие части сайта реально помогают людям найти билет и корректно атрибутировать комиссии BusTicket4.me. Эти же события отправляются в нашу аналитику (Umami) как анонимный event «ba_click». Если вы не хотите чтобы клики записывались — включите ad-blocker или приватный режим, сайт работает и без этих записей.',
        'bg': 'Когато кликнете върху бутона „Купи“, който води към BusTicket4.me, записваме минимален запис за клика на собствения си сървър: идентификатор на маршрута (напр. beograd-budva), типа страница, от която сте кликнали (каталог, детайли на маршрут, търсене), превозвача, часа на тръгване, анонимизиран хеш на вашия IP адрес (sha256 със сол-тайна, която се сменя редовно) и основни технически данни за браузъра. Не записваме суровия IP адрес, име, имейл, нито каквото и да е друго, което може директно да ви идентифицира. Тези записи съхраняваме максимум 90 дни за вътрешни цели — за да знаем кои части от сайта реално помагат на хората да намерят билет и за да разпределим правилно комисионата от BusTicket4.me. Същите записи се изпращат и в нашата аналитика (Umami) като анонимно събитие „ba_click“. Ако искате вашите кликове да не бъдат записвани, включете ad-blocker или частен режим в браузъра — нашият сайт продължава да работи без тези записи.',
    },
    'privacy.rights_body2': {
        'sr': 'Ako želite da zatražite izvoz, izmenu ili brisanje podataka (na primer vaše kontakt poruke), pošaljite zahtev na info@prevozni.com. Obradićemo ga u roku od 30 dana u skladu sa GDPR-om i srpskim Zakonom o zaštiti podataka o ličnosti. Nije potrebno da navodite razlog.',
        'en': 'If you want to request export, correction or deletion of your data (for example a contact form message you sent), email info@prevozni.com. We will process the request within 30 days in line with GDPR and the Serbian Personal Data Protection Act. You do not need to state a reason.',
        'ru': 'Если вы хотите запросить экспорт, исправление или удаление данных (например вашего сообщения из контактной формы), напишите на info@prevozni.com. Мы обработаем запрос в течение 30 дней в соответствии с GDPR и сербским законом о защите персональных данных. Причину указывать не обязательно.',
        'bg': 'Ако желаете да поискате износ, промяна или изтриване на данни (например вашите съобщения от контактната форма), изпратете заявка на info@prevozni.com. Ще я обработим в срок от 30 дни в съответствие с GDPR и сръбския Закон за защита на личните данни. Не е необходимо да посочвате причина.',
    },
    'privacy.changes_h': {
        'sr': 'Izmene ove politike',
        'en': 'Changes to this policy',
        'ru': 'Изменения этой политики',
        'bg': 'Промени в тази политика',
    },
    'privacy.changes_body': {
        'sr': 'Ako nešto bitno promenimo (na primer dodamo novi analitički alat ili pustimo reklame), objavićemo novu verziju ove stranice i ažurirati datum ispod. Za suštinske izmene obavestićemo i preko banera na početnoj strani minimalno 14 dana unapred. Trenutna verzija: april 2026.',
        'en': 'If we change something material (for example add a new analytics tool or enable ads), we publish a new version of this page and update the date below. For substantive changes we also announce a homepage banner at least 14 days in advance. Current version: April 2026.',
        'ru': 'Если мы изменяем что-то существенное (например добавляем новый аналитический инструмент или включаем рекламу), мы публикуем новую версию этой страницы и обновляем дату ниже. Для существенных изменений также вывешиваем баннер на главной странице минимум за 14 дней. Текущая версия: апрель 2026.',
        'bg': 'Ако направим съществена промяна (например добавим нов аналитичен инструмент или пуснем реклами), ще публикуваме нова версия на тази страница и ще актуализираме датата по-долу. За съществени промени ще уведомим и чрез банер на началната страница най-малко 14 дни предварително. Текуща версия: април 2026.',
    },

    'contact.intro_p2': {
        'sr': 'Šta nam najviše pomaže: <strong>tačan URL stranice</strong> gde ste naišli na grešku, <strong>screenshot</strong> (ako je vizuelni bug) i <strong>naziv pretraživača i uređaja</strong>. Za predloge novih gradova ili ruta — napišite kuda biste voleli da putujete, ubrzavamo obogaćivanje podataka na osnovu stvarne potražnje.',
        'en': 'What helps us most: the <strong>exact URL</strong> where you hit the problem, a <strong>screenshot</strong> (for visual bugs), and the <strong>browser + device</strong> you are on. For feature requests or new cities/routes — tell us where you\'d like to travel; we prioritise data enrichment based on actual demand.',
        'ru': 'Что помогает больше всего: <strong>точный URL</strong> страницы где вы столкнулись с проблемой, <strong>скриншот</strong> (для визуальных багов) и <strong>браузер + устройство</strong>. Для предложений по новым городам или маршрутам — напишите куда вам хотелось бы поехать, мы приоритизируем обогащение данных по реальному спросу.',
        'bg': 'Това, което ни помага най-много: <strong>точният URL адрес на страницата</strong>, където сте забелязали грешката, <strong>снимка на екрана</strong> (ако е визуален бъг) и <strong>името на браузъра и устройството</strong>. За предложения за нови градове или маршрути — напишете ни къде бихте искали да пътувате, ускоряваме обогатяването на данните въз основа на реалното търсене.',
    },

    'about.sources_p': {
        'sr': 'Mrežno svake noći (u 02:00) skeniramo i objedinjujemo podatke iz više izvora: busticket4.me (glavna baza međugradskih autobusa), srbijavoz.rs (zvanični red vožnje vozova), polazak.rs (Lasta i povezani prevoznici), bgprevoz.rs (GSP Beograd), gspns.co.rs (JGSP Novi Sad), Overpass (OpenStreetMap — koordinate stajališta) i zvanični GTFS feed sa data.gov.rs. Ako podatak nedostaje ili zastari, uvek proverite i na sajtu prevoznika.',
        'en': 'Every night (at 02:00 local time) we scan and merge data from several sources: busticket4.me (primary intercity bus database), srbijavoz.rs (official train schedule), polazak.rs (Lasta and related carriers), bgprevoz.rs (GSP Belgrade), gspns.co.rs (JGSP Novi Sad), Overpass (OpenStreetMap — stop coordinates) and the official GTFS feed from data.gov.rs. If a datum is missing or outdated, always cross-check the carrier\'s own site.',
        'ru': 'Каждую ночь (в 02:00 местного времени) мы сканируем и объединяем данные из нескольких источников: busticket4.me (основная база междугородних автобусов), srbijavoz.rs (официальное расписание поездов), polazak.rs (Lasta и связанные перевозчики), bgprevoz.rs (GSP Белград), gspns.co.rs (JGSP Нови-Сад), Overpass (OpenStreetMap — координаты остановок) и официальный GTFS фид с data.gov.rs. Если данных не хватает или они устарели — сверяйтесь на сайте самого перевозчика.',
    },
    'home.hero_title': {
        'sr': 'Nađite autobus i kupite kartu',
        'en': 'Find your bus, buy your ticket',
        'ru': 'Найдите автобус и купите билет',
        'bg': 'Намерете автобус и купете билет',
    },
    'home.hero_subtitle': {
        'sr': 'Pronađite autobus, voz ili gradski prevoz na jednom mestu',
        'en': 'Find bus, train or city transport in one place',
        'ru': 'Найдите автобус, поезд или городской транспорт в одном месте',
        'bg': 'Намерете автобус, влак или градски транспорт на едно място',
    },
    'home.hero_sub_descriptive': {
        'sr': 'Autobus, voz i gradska mreža — Srbija, Crna Gora, BiH i region',
        'en': 'Bus, train and city transport — Serbia, Montenegro, BiH & region',
        'ru': 'Автобус, поезд и городской транспорт — Сербия, Черногория, БиГ и регион',
        'bg': 'Автобус, влак и градски транспорт — Сърбия, Черна гора, БиГ и региона',
    },
    'home.hero_sub_feature_list': {
        'sr': '335 ruta · karta stajališta · 6 zemalja · besplatno',
        'en': '335 routes · stop map · 6 countries · free',
        'ru': '335 маршрутов · карта остановок · 6 стран · бесплатно',
        'bg': '335 маршрута · карта на спирките · 6 държави · безплатно',
    },
    'home.hero_sub_price_compare': {
        'sr': 'Uporedite cene Lasta, Niš-Ekspres i drugih — bez naknade',
        'en': 'Compare Lasta, Niš-Ekspres and other carriers — no fee',
        'ru': 'Сравните цены Lasta, Niš-Ekspres и других — без комиссии',
        'bg': 'Сравнете цените на Lasta, Niš-Ekspres и други — без такса',
    },
    'transfer.h': {
        'sr': 'Radije od vrata do vrata?',
        'en': 'Prefer door-to-door?',
        'ru': 'Удобнее от двери до двери?',
        'bg': 'По-удобно от врата до врата?',
    },
    'transfer.text': {
        'sr': 'Rezervišite privatni transfer ili iznajmite automobil za relaciju {route}. Cene određuje partner.',
        'en': 'Book a private transfer or rent a car for {route}. Prices are set by the partner.',
        'ru': 'Забронируйте частный трансфер или арендуйте авто на маршруте {route}. Цены устанавливает партнёр.',
        'bg': 'Резервирайте частен трансфер или наемете кола за маршрута {route}. Цените се определят от партньора.',
    },
    'transfer.btn_transfer': {
        'sr': 'Uporedi privatne transfere',
        'en': 'Compare private transfers',
        'ru': 'Сравнить цены на трансфер',
        'bg': 'Сравни частни трансфери',
    },
    'transfer.btn_cars': {
        'sr': 'Uporedi rent-a-car',
        'en': 'Compare rental cars',
        'ru': 'Сравнить аренду авто',
        'bg': 'Сравни коли под наем',
    },
    'transfer.disclosure': {
        'sr': 'Sponzorisani linkovi: možemo dobiti proviziju, bez dodatnog troška za vas.',
        'en': 'Sponsored links: we may earn a commission at no extra cost to you.',
        'ru': 'Партнёрские ссылки: мы можем получить комиссию, для вас цена не меняется.',
        'bg': 'Спонсорирани връзки: може да получим комисионна, без допълнителна цена за вас.',
    },
    # ── Balkan Loop planner (/balkan-loop/, app/planner.py) ──
    'nav.planner': {
        'sr': 'Planer putovanja',
        'en': 'Trip planner',
        'ru': 'Планировщик маршрута',
        'bg': 'Планер на маршрут',
    },
    'planner.title': {
        'sr': 'Planer putovanja po Balkanu autobusom: napravite rutu',
        'en': 'Balkan Trip Planner by Bus: Build Your Itinerary',
        'ru': 'Планировщик поездки по Балканам на автобусах',
        'bg': 'Планер за пътуване из Балканите с автобус',
    },
    'planner.meta': {
        'sr': 'Besplatan planer rute po Balkanu. Izaberite početak, kraj i broj dana i dobijte rutu stanicu po stanicu: direktni autobusi, trajanje vožnje i cene.',
        'en': 'Free Balkan itinerary planner. Pick a start, a finish and your days and get a stop-by-stop bus route with real timetables, travel times and fares.',
        'ru': 'Бесплатный планировщик маршрута по Балканам. Выберите старт, финиш и число дней: маршрут по городам, прямые автобусы, время в пути и цены.',
        'bg': 'Безплатен планер за маршрут из Балканите. Изберете начало, край и брой дни: маршрут град по град, директни автобуси, времетраене и цени.',
    },
    'planner.p_title': {
        'sr': '{a} — {b} autobusom: ruta za {n} dana',
        'en': '{a} to {b} by Bus: {n}-Day Itinerary',
        'ru': '{a} — {b} на автобусе: маршрут на {n} дн.',
        'bg': '{a} — {b} с автобус: маршрут за {n} дни',
    },
    'planner.p_title_loop': {
        'sr': 'Krug po Balkanu autobusom, polazak {a}: {n} dana',
        'en': '{n}-Day Balkan Loop from {a} by Bus',
        'ru': 'Кольцо по Балканам на автобусах, старт {a}: {n} дн.',
        'bg': 'Кръг из Балканите с автобус, старт {a}: {n} дни',
    },
    'planner.p_h1': {
        'sr': '{a} — {b} autobusom: ruta za {n} dana',
        'en': '{a} to {b} by bus: a {n}-day itinerary',
        'ru': '{a} — {b} на автобусе: маршрут на {n} дн.',
        'bg': '{a} — {b} с автобус: маршрут за {n} дни',
    },
    'planner.p_h1_loop': {
        'sr': 'Krug po Balkanu autobusom, polazak {a}: {n} dana',
        'en': 'Balkan loop from {a} by bus: {n} days',
        'ru': 'Кольцо по Балканам на автобусах, старт {a}: {n} дн.',
        'bg': 'Кръг из Балканите с автобус, старт {a}: {n} дни',
    },
    'planner.p_meta': {
        'sr': 'Ruta {a} — {b} za {n} dana: stanica {k}, zemalja {c}, direktnih autobusa {legs}, ukupno {t} vožnje. Red vožnje i cena za svaku deonicu.',
        'en': '{n}-day bus route from {a} to {b}: {k} stops in {c} countries, {legs} direct buses, {t} on the road. Timetable and fare for every leg.',
        'ru': 'Маршрут {a} — {b} на {n} дн.: остановок {k}, стран {c}, прямых автобусов {legs}, в дороге {t}. Расписание и цена каждого переезда.',
        'bg': 'Маршрут {a} — {b} за {n} дни: спирки {k}, държави {c}, директни автобуси {legs}, общо {t} път. Разписание и цена за всяка отсечка.',
    },
    'planner.p_meta_loop': {
        'sr': 'Krug iz grada {a} za {n} dana: stanica {k}, zemalja {c}, direktnih autobusa {legs}, ukupno {t} vožnje. Red vožnje i cena za svaku deonicu.',
        'en': '{n}-day Balkan round trip from {a}: {k} stops in {c} countries, {legs} direct buses, {t} on the road. Timetable and fare for every leg.',
        'ru': 'Кольцевой маршрут из города {a} на {n} дн.: остановок {k}, стран {c}, прямых автобусов {legs}, в дороге {t}. Расписание и цена каждого переезда.',
        'bg': 'Кръгов маршрут от {a} за {n} дни: спирки {k}, държави {c}, директни автобуси {legs}, общо {t} път. Разписание и цена за всяка отсечка.',
    },
    'planner.p_intro': {
        'sr': 'Ruta povezuje stanice ({k}) u zemljama ({c}) direktnim autobusima ({legs}); ukupno {t} vožnje.',
        'en': 'This route links {k} stops in {c} countries with {legs} direct buses and {t} on the road in total.',
        'ru': 'Маршрут связывает остановки ({k}) в странах ({c}) прямыми автобусами ({legs}); всего в дороге {t}.',
        'bg': 'Маршрутът свързва спирки ({k}) в държави ({c}) с директни автобуси ({legs}); общо {t} път.',
    },
    'planner.p_intro_cost': {
        'sr': 'Autobuske karte ukupno koštaju oko {p} € po najnižim objavljenim cenama.',
        'en': 'Bus tickets add up to about €{p} at the lowest published fares.',
        'ru': 'Билеты на автобусы в сумме стоят около {p} € по минимальным опубликованным ценам.',
        'bg': 'Автобусните билети общо струват около {p} € по най-ниските публикувани цени.',
    },
    'planner.faq_h': {
        'sr': 'Pitanja o ovoj ruti',
        'en': 'Questions about this route',
        'ru': 'Вопросы об этом маршруте',
        'bg': 'Въпроси за този маршрут',
    },
    'planner.q_direct': {
        'sr': '{a} — {b}: postoji li direktan autobus?',
        'en': '{a} to {b}: is there a direct bus?',
        'ru': '{a} — {b}: есть ли прямой автобус?',
        'bg': '{a} — {b}: има ли директен автобус?',
    },
    'planner.a_direct_yes': {
        'sr': 'Da. U redu vožnje je direktnih polazaka: {n}, a najbrži traje {t}. Ova ruta umesto toga deli put na više stanica ({k}).',
        'en': 'Yes. The timetable has {n} direct departures and the fastest takes {t}. This itinerary breaks the trip into {k} stops instead.',
        'ru': 'Да. В расписании прямых рейсов: {n}, самый быстрый идёт {t}. Этот маршрут вместо этого делит путь на остановки ({k}).',
        'bg': 'Да. В разписанието има директни курсове: {n}, най-бързият трае {t}. Този маршрут вместо това разделя пътя на спирки ({k}).',
    },
    'planner.a_direct_no': {
        'sr': 'U našem redu vožnje ga nema. Ruta vodi preko ovih stanica: {via}. Svaka deonica je direktan autobus.',
        'en': 'Not in our timetable. This route gets there through {via}, and every leg is a direct bus.',
        'ru': 'В нашем расписании его нет. Маршрут идёт через города: {via}. Каждый переезд это прямой автобус.',
        'bg': 'В нашето разписание няма. Маршрутът минава през: {via}. Всяка отсечка е директен автобус.',
    },
    'planner.q_time': {
        'sr': 'Koliko ukupno traje vožnja autobusom?',
        'en': 'How long is the bus travel in total?',
        'ru': 'Сколько всего ехать на автобусах?',
        'bg': 'Колко общо е пътуването с автобус?',
    },
    'planner.a_time': {
        'sr': 'Ukupno {t}, autobusa: {legs}. Najduža deonica je {a} → {b}: {lt}.',
        'en': '{t} across {legs} buses. The longest leg is {a} → {b}, {lt}.',
        'ru': 'Всего {t}, автобусов: {legs}. Самый длинный переезд {a} → {b}: {lt}.',
        'bg': 'Общо {t}, автобуси: {legs}. Най-дългата отсечка е {a} → {b}: {lt}.',
    },
    'planner.q_cost': {
        'sr': 'Koliko koštaju autobuske karte?',
        'en': 'How much do the bus tickets cost?',
        'ru': 'Сколько стоят билеты на автобусы?',
        'bg': 'Колко струват автобусните билети?',
    },
    'planner.a_cost': {
        'sr': 'Oko {p} € za sve deonice ({legs}), kada se saberu najniže cene koje objavljuju naši izvori.',
        'en': 'About €{p} for all {legs} legs, adding up the lowest fare our sources publish for each.',
        'ru': 'Около {p} € за все переезды ({legs}), если сложить минимальные цены из наших источников.',
        'bg': 'Около {p} € за всички отсечки ({legs}), като се съберат най-ниските цени от нашите източници.',
    },
    'planner.a_cost_partial': {
        'sr': 'Naši izvori objavljuju cene za {x} od {legs} deonica; one zajedno iznose oko {p} €. Ostale cene prikazuje prodavac karata.',
        'en': 'Our sources publish fares for {x} of the {legs} legs; those add up to about €{p}. The ticket seller shows the rest.',
        'ru': 'Наши источники публикуют цены для {x} из {legs} переездов; в сумме это около {p} €. Остальные цены показывает продавец билетов.',
        'bg': 'Нашите източници публикуват цени за {x} от {legs} отсечки; общо те са около {p} €. Останалите показва продавачът на билети.',
    },
    'planner.q_days': {
        'sr': 'Koliko dana je potrebno?',
        'en': 'How many days do you need?',
        'ru': 'Сколько дней нужно?',
        'bg': 'Колко дни са нужни?',
    },
    'planner.a_days': {
        'sr': 'Ovaj plan traje {n} dana. Noćenja po stanici: {list}. Najkraća verzija sa istim stanicama staje u {m} dana.',
        'en': 'This plan takes {n} days. Nights per stop: {list}. The shortest version with the same stops fits into {m} days.',
        'ru': 'Этот план рассчитан на {n} дн. Ночей по остановкам: {list}. Самая короткая версия с теми же остановками занимает {m} дн.',
        'bg': 'Този план е за {n} дни. Нощувки по спирки: {list}. Най-кратката версия със същите спирки е {m} дни.',
    },
    'planner.adjust_h': {
        'sr': 'Izmenite rutu',
        'en': 'Change this route',
        'ru': 'Изменить маршрут',
        'bg': 'Променете маршрута',
    },
    'planner.loop_hint': {
        'sr': 'Isti početak i kraj daju kružnu rutu.',
        'en': 'The same start and finish gives a round trip.',
        'ru': 'Одинаковые старт и финиш дают кольцевой маршрут.',
        'bg': 'Еднакви начало и край дават кръгов маршрут.',
    },
    'planner.legs_h': {
        'sr': 'Direktni autobusi između stanica',
        'en': 'Direct buses between the stops',
        'ru': 'Прямые автобусы между остановками',
        'bg': 'Директни автобуси между спирките',
    },
    'planner.legs_sub': {
        'sr': 'Za svaki par ispod postoji direktan autobus u redu vožnje. Planer ih slaže u rutu.',
        'en': 'Every pair below has a direct bus in the timetable. The planner chains them into a route.',
        'ru': 'Для каждой пары ниже в расписании есть прямой автобус. Планировщик собирает из них маршрут.',
        'bg': 'За всяка двойка по-долу има директен автобус в разписанието. Планерът ги свързва в маршрут.',
    },
    'planner.legs_from': {
        'sr': 'Polazak: {city}',
        'en': 'From {city}',
        'ru': 'Отправление: {city}',
        'bg': 'Тръгване: {city}',
    },
    'planner.card_summary': {
        'sr': 'stanica {k} · zemalja {c} · {t} u autobusu',
        'en': '{k} stops · {c} countries · {t} on buses',
        'ru': 'остановок {k} · стран {c} · {t} в автобусах',
        'bg': 'спирки {k} · държави {c} · {t} в автобуси',
    },
    'planner.presets_sub': {
        'sr': 'Gotove rute sa redom vožnje za svaku deonicu.',
        'en': 'Ready-made itineraries with the timetable for every leg.',
        'ru': 'Готовые маршруты с расписанием каждого переезда.',
        'bg': 'Готови маршрути с разписание за всяка отсечка.',
    },
    'planner.all_routes': {
        'sr': 'Sve gotove rute i planer',
        'en': 'All itineraries and the planner',
        'ru': 'Все готовые маршруты и планировщик',
        'bg': 'Всички готови маршрути и планерът',
    },
    'planner.h1': {
        'sr': 'Planer putovanja po Balkanu autobusom',
        'en': 'Balkan trip planner: your itinerary by bus',
        'ru': 'Планировщик поездки по Балканам на автобусах',
        'bg': 'Планер за пътуване из Балканите с автобус',
    },
    'planner.sub': {
        'sr': 'Izaberite odakle krećete, gde završavate i koliko dana imate. Svaka deonica ispod je direktan autobus iz našeg reda vožnje.',
        'en': 'Pick where you start, where you finish and how many days you have. Every leg below is a direct bus from our timetable.',
        'ru': 'Выберите, откуда стартуете, где заканчиваете и сколько у вас дней. Каждый переезд ниже это прямой автобус из нашего расписания.',
        'bg': 'Изберете откъде тръгвате, къде завършвате и колко дни имате. Всяка отсечка по-долу е директен автобус от нашето разписание.',
    },
    'planner.from': {
        'sr': 'Početak',
        'en': 'Start',
        'ru': 'Старт',
        'bg': 'Начало',
    },
    'planner.to': {
        'sr': 'Kraj',
        'en': 'Finish',
        'ru': 'Финиш',
        'bg': 'Край',
    },
    'planner.days': {
        'sr': 'Dana',
        'en': 'Days',
        'ru': 'Дней',
        'bg': 'Дни',
    },
    'planner.submit': {
        'sr': 'Napravi rutu',
        'en': 'Build my route',
        'ru': 'Построить маршрут',
        'bg': 'Състави маршрут',
    },
    'planner.result_h': {
        'sr': 'Vaša ruta: {days} dana',
        'en': 'Your route: {days} days',
        'ru': 'Ваш маршрут: {days} дн.',
        'bg': 'Вашият маршрут: {days} дни',
    },
    'planner.sum_stops': {
        'sr': 'stanica',
        'en': 'stops',
        'ru': 'остановок',
        'bg': 'спирки',
    },
    'planner.sum_countries': {
        'sr': 'zemalja',
        'en': 'countries',
        'ru': 'стран',
        'bg': 'държави',
    },
    'planner.sum_bus': {
        'sr': 'u autobusu',
        'en': 'on buses',
        'ru': 'в автобусах',
        'bg': 'в автобуси',
    },
    'planner.sum_cost': {
        'sr': 'autobuske karte od',
        'en': 'bus tickets from',
        'ru': 'билеты на автобус от',
        'bg': 'автобусни билети от',
    },
    'planner.days_range': {
        'sr': 'Dan {a}–{b}',
        'en': 'Day {a}–{b}',
        'ru': 'День {a}–{b}',
        'bg': 'Ден {a}–{b}',
    },
    'planner.nights': {
        'sr': 'Noćenja: {n}',
        'en': 'Nights: {n}',
        'ru': 'Ночей: {n}',
        'bg': 'Нощувки: {n}',
    },
    'planner.leg_bus': {
        'sr': 'Autobus {a} → {b}',
        'en': 'Bus {a} → {b}',
        'ru': 'Автобус {a} → {b}',
        'bg': 'Автобус {a} → {b}',
    },
    'planner.leg_trips': {
        'sr': 'Polazaka u redu vožnje: {n}',
        'en': 'Departures in the timetable: {n}',
        'ru': 'Рейсов в расписании: {n}',
        'bg': 'Курсове в разписанието: {n}',
    },
    'planner.leg_duration': {
        'sr': 'put od {t}',
        'en': 'journey from {t}',
        'ru': 'в пути от {t}',
        'bg': 'път от {t}',
    },
    'planner.leg_price': {
        'sr': 'od {p} €',
        'en': 'from €{p}',
        'ru': 'от {p} €',
        'bg': 'от {p} €',
    },
    'planner.leg_price_unknown': {
        'sr': 'cena kod prodavca karata',
        'en': 'fare shown by the ticket seller',
        'ru': 'цена у продавца билетов',
        'bg': 'цена при продавача на билети',
    },
    'planner.leg_first_last': {
        'sr': 'prvi {a}, poslednji {b}',
        'en': 'first {a}, last {b}',
        'ru': 'первый {a}, последний {b}',
        'bg': 'първи {a}, последен {b}',
    },
    'planner.leg_cta': {
        'sr': 'Red vožnje i karte',
        'en': 'Timetable and tickets',
        'ru': 'Расписание и билеты',
        'bg': 'Разписание и билети',
    },
    'planner.end_day': {
        'sr': 'Dan {d}: kraj putovanja, {city}',
        'en': 'Day {d}: the trip ends in {city}',
        'ru': 'День {d}: финиш, {city}',
        'bg': 'Ден {d}: край на пътуването, {city}',
    },
    'planner.end_loop': {
        'sr': 'Dan {d}: povratak, {city}',
        'en': 'Day {d}: back in {city}',
        'ru': 'День {d}: возвращение, {city}',
        'bg': 'Ден {d}: връщане, {city}',
    },
    'planner.spare': {
        'sr': 'Slobodnih dana: {n}. Dodajte ih bilo kojoj stanici.',
        'en': 'Spare days: {n}. Add them to any stop.',
        'ru': 'Свободных дней: {n}. Добавьте их к любой остановке.',
        'bg': 'Свободни дни: {n}. Добавете ги към която и да е спирка.',
    },
    'planner.none': {
        'sr': 'Nijedan lanac direktnih autobusa ne staje u ova podešavanja. Probajte više dana ili drugi kraj rute.',
        'en': 'No chain of direct buses fits these settings. Try more days or a different finish.',
        'ru': 'Цепочка прямых автобусов в эти условия не укладывается. Попробуйте больше дней или другой финиш.',
        'bg': 'Няма верига от директни автобуси за тези настройки. Опитайте с повече дни или друг край.',
    },
    'planner.presets_h': {
        'sr': 'Popularne rute',
        'en': 'Popular routes',
        'ru': 'Популярные маршруты',
        'bg': 'Популярни маршрути',
    },
    'planner.preset_label': {
        'sr': '{a} → {b}, {n} dana',
        'en': '{a} → {b}, {n} days',
        'ru': '{a} → {b}, {n} дн.',
        'bg': '{a} → {b}, {n} дни',
    },
    'planner.preset_loop': {
        'sr': 'Krug iz grada {a}, {n} dana',
        'en': 'Loop from {a}, {n} days',
        'ru': 'Кольцо из города {a}, {n} дн.',
        'bg': 'Кръг от {a}, {n} дни',
    },
    'planner.how_h': {
        'sr': 'Kako nastaje ruta',
        'en': 'How the route is built',
        'ru': 'Как строится маршрут',
        'bg': 'Как се съставя маршрутът',
    },
    'planner.how_1': {
        'sr': 'Svaka deonica je direktan autobus između dve stanice koji danas postoji u našem redu vožnje. Planer ne izmišlja veze.',
        'en': 'Each leg is a direct bus between two stops that is in our timetable today. The planner never invents a connection.',
        'ru': 'Каждый переезд это прямой автобус между двумя городами, который сегодня есть в нашем расписании. Планировщик не выдумывает пересадки.',
        'bg': 'Всяка отсечка е директен автобус между две спирки, който днес е в нашето разписание. Планерът не измисля връзки.',
    },
    'planner.how_2': {
        'sr': 'Cena je najniža koju objavljuju naši izvori, a trajanje je najbrži polazak. Red vožnje se menja po sezoni, pa proverite stranicu deonice pre puta.',
        'en': 'The fare is the lowest our sources publish and the duration is the fastest departure. Timetables change with the season, so check the leg page before you travel.',
        'ru': 'Цена это минимальная из опубликованных нашими источниками, время в пути по самому быстрому рейсу. Расписание меняется по сезонам, перед поездкой проверьте страницу переезда.',
        'bg': 'Цената е най-ниската, публикувана от нашите източници, а времетраенето е на най-бързия курс. Разписанията се менят по сезони, затова проверете страницата на отсечката преди път.',
    },
    'planner.how_3': {
        'sr': 'Broj noćenja je predlog: minimum za prvu posetu, a preostali dani idu većim stanicama.',
        'en': 'Nights per stop are a suggestion: the minimum for a first visit, with the remaining days going to the bigger stops.',
        'ru': 'Число ночей это предложение: минимум для первого визита, остальные дни отданы крупным остановкам.',
        'bg': 'Броят нощувки е предложение: минимум за първо посещение, а останалите дни отиват при по-големите спирки.',
    },
    'planner.offers_h': {
        'sr': 'Za ceo put',
        'en': 'For the whole trip',
        'ru': 'На всю поездку',
        'bg': 'За цялото пътуване',
    },
    'planner.offer.stay': {
        'sr': 'Smeštaj: {city}',
        'en': 'Places to stay in {city}',
        'ru': 'Жильё: {city}',
        'bg': 'Настаняване: {city}',
    },
    'planner.offer.tours': {
        'sr': 'Ture i izleti: {city}',
        'en': 'Tours in {city}',
        'ru': 'Туры и экскурсии: {city}',
        'bg': 'Турове: {city}',
    },
    'planner.offer.esim': {
        'sr': 'eSIM za Balkan',
        'en': 'eSIM for the Balkans',
        'ru': 'eSIM для Балкан',
        'bg': 'eSIM за Балканите',
    },
    'planner.offer.insurance': {
        'sr': 'Putno osiguranje',
        'en': 'Travel insurance',
        'ru': 'Страховка путешественника',
        'bg': 'Пътна застраховка',
    },
    'planner.teaser': {
        'sr': 'Nastavljate kroz Balkan? Isplanirajte celu rutu autobusom',
        'en': 'Travelling on through the Balkans? Plan the whole route by bus',
        'ru': 'Едете дальше по Балканам? Спланируйте весь маршрут на автобусах',
        'bg': 'Продължавате през Балканите? Планирайте целия маршрут с автобус',
    },
    'planner.country.HR': {
        'sr': 'Hrvatska',
        'en': 'Croatia',
        'ru': 'Хорватия',
        'bg': 'Хърватия',
    },
    'planner.country.ME': {
        'sr': 'Crna Gora',
        'en': 'Montenegro',
        'ru': 'Черногория',
        'bg': 'Черна гора',
    },
    'planner.country.AL': {
        'sr': 'Albanija',
        'en': 'Albania',
        'ru': 'Албания',
        'bg': 'Албания',
    },
    'planner.country.MK': {
        'sr': 'Severna Makedonija',
        'en': 'North Macedonia',
        'ru': 'Северная Македония',
        'bg': 'Северна Македония',
    },
    'planner.country.BA': {
        'sr': 'Bosna i Hercegovina',
        'en': 'Bosnia and Herzegovina',
        'ru': 'Босния и Герцеговина',
        'bg': 'Босна и Херцеговина',
    },
    'planner.country.RS': {
        'sr': 'Srbija',
        'en': 'Serbia',
        'ru': 'Сербия',
        'bg': 'Сърбия',
    },
    'planner.stop.dubrovnik': {
        'sr': 'Stari grad opasan zidinama na Jadranu, pod zaštitom UNESCO-a.',
        'en': 'Walled old town on the Adriatic, a UNESCO World Heritage site.',
        'ru': 'Старый город в крепостных стенах на Адриатике, объект ЮНЕСКО.',
        'bg': 'Стар град с крепостни стени на Адриатика, обект на ЮНЕСКО.',
    },
    'planner.stop.split': {
        'sr': 'Dioklecijanova palata, rezidencija rimskog cara koja je postala centar grada (UNESCO).',
        'en': "Diocletian's Palace, a Roman emperor's residence that became the city centre (UNESCO).",
        'ru': 'Дворец Диоклетиана: резиденция римского императора, ставшая центром города (ЮНЕСКО).',
        'bg': 'Диоклециановият дворец: резиденция на римски император, превърнала се в център на града (ЮНЕСКО).',
    },
    'planner.stop.kotor': {
        'sr': 'Srednjovekovni stari grad na kraju Bokokotorskog zaliva (UNESCO), sa tvrđavom iznad njega.',
        'en': 'Medieval old town at the far end of the Bay of Kotor (UNESCO), with the fortress above it.',
        'ru': 'Средневековый старый город в глубине Которского залива (ЮНЕСКО), над ним крепость.',
        'bg': 'Средновековен стар град в дъното на Которския залив (ЮНЕСКО), с крепост над него.',
    },
    'planner.stop.budva': {
        'sr': 'Stari grad i najposećenije plaže crnogorske obale.',
        'en': 'Old town and the busiest beaches on the Montenegrin coast.',
        'ru': 'Старый город и самые людные пляжи черногорского побережья.',
        'bg': 'Стар град и най-посещаваните плажове на черногорския бряг.',
    },
    'planner.stop.herceg-novi': {
        'sr': 'Grad na ulazu u Bokokotorski zaliv, prva crnogorska stanica iz pravca Dubrovnika.',
        'en': 'Town at the entrance to the Bay of Kotor, the first Montenegrin stop coming from Dubrovnik.',
        'ru': 'Город у входа в Которский залив, первая остановка в Черногории со стороны Дубровника.',
        'bg': 'Град на входа на Которския залив, първата черногорска спирка откъм Дубровник.',
    },
    'planner.stop.podgorica': {
        'sr': 'Glavni grad Crne Gore i autobusko čvorište između obale, Albanije i Bosne.',
        'en': 'Capital of Montenegro and the bus hub between the coast, Albania and Bosnia.',
        'ru': 'Столица Черногории и автобусный узел между побережьем, Албанией и Боснией.',
        'bg': 'Столицата на Черна гора и автобусен възел между брега, Албания и Босна.',
    },
    'planner.stop.skadar': {
        'sr': 'Grad na jezeru na severu Albanije i uobičajena baza za Albanske Alpe (Theth, Valbona).',
        'en': 'Lakeside city in northern Albania and the usual base for the Albanian Alps (Theth, Valbona).',
        'ru': 'Город у озера на севере Албании и обычная база для Албанских Альп (Тет, Вальбона).',
        'bg': 'Град край езерото в Северна Албания и обичайна база за Албанските Алпи (Тет, Валбона).',
    },
    'planner.stop.tirana': {
        'sr': 'Glavni grad Albanije i glavno saobraćajno čvorište zemlje.',
        'en': "Capital of Albania and the country's main transport hub.",
        'ru': 'Столица Албании и главный транспортный узел страны.',
        'bg': 'Столицата на Албания и главният транспортен възел на страната.',
    },
    'planner.stop.ohrid': {
        'sr': 'Stari grad na obali Ohridskog jezera (UNESCO).',
        'en': 'Old town on the shore of Lake Ohrid (UNESCO).',
        'ru': 'Старый город на берегу Охридского озера (ЮНЕСКО).',
        'bg': 'Стар град на брега на Охридското езеро (ЮНЕСКО).',
    },
    'planner.stop.skoplje': {
        'sr': 'Glavni grad Severne Makedonije, sa Starom čaršijom i Kamenim mostom.',
        'en': 'Capital of North Macedonia, with the Old Bazaar and the Stone Bridge.',
        'ru': 'Столица Северной Македонии со Старым базаром и Каменным мостом.',
        'bg': 'Столицата на Северна Македония, със Старата чаршия и Каменния мост.',
    },
    'planner.stop.mostar': {
        'sr': 'Stari most preko Neretve i stari grad oko njega (UNESCO).',
        'en': 'The Old Bridge (Stari Most) over the Neretva and the old town around it (UNESCO).',
        'ru': 'Старый мост через Неретву и старый город вокруг него (ЮНЕСКО).',
        'bg': 'Старият мост над Неретва и старият град около него (ЮНЕСКО).',
    },
    'planner.stop.sarajevo': {
        'sr': 'Glavni grad Bosne i Hercegovine: osmanska Baščaršija odmah uz austrougarske ulice.',
        'en': 'Capital of Bosnia and Herzegovina: the Ottoman-era Baščaršija bazaar next to Austro-Hungarian streets.',
        'ru': 'Столица Боснии и Герцеговины: османский базар Башчаршия рядом с австро-венгерскими улицами.',
        'bg': 'Столицата на Босна и Херцеговина: османската Башчаршия до австро-унгарските улици.',
    },
    'planner.stop.beograd': {
        'sr': 'Glavni grad Srbije na ušću Save u Dunav, sa Kalemegdanskom tvrđavom.',
        'en': 'Capital of Serbia where the Sava meets the Danube, with the Kalemegdan fortress.',
        'ru': 'Столица Сербии у слияния Савы и Дуная, с крепостью Калемегдан.',
        'bg': 'Столицата на Сърбия при вливането на Сава в Дунав, с крепостта Калемегдан.',
    },
    'home.search_from': {
        'sr': 'Odakle?',
        'en': 'From?',
        'ru': 'Откуда?',
        'bg': 'Откъде?',
    },
    'home.search_to': {
        'sr': 'Dokle?',
        'en': 'To?',
        'ru': 'Куда?',
        'bg': 'Докъде?',
    },
    'home.search_btn': {
        'sr': 'Pretraži',
        'en': 'Search',
        'ru': 'Найти',
        'bg': 'Търсене',
    },
    'home.popular_routes': {
        'sr': 'Popularne rute',
        'en': 'Popular routes',
        'ru': 'Популярные маршруты',
        'bg': 'Популярни маршрути',
    },
    'home.city_transport': {
        'sr': 'Gradski prevoz',
        'en': 'City transport',
        'ru': 'Городской транспорт',
        'bg': 'Градски транспорт',
    },
    'home.all_routes': {
        'sr': 'Sve rute',
        'en': 'All routes',
        'ru': 'Все маршруты',
        'bg': 'Всички маршрути',
    },

    # ── Common ──
    'common.departure': {
        'sr': 'Polazak',
        'en': 'Departure',
        'ru': 'Отправление',
        'bg': 'Тръгване',
    },
    'common.arrival': {
        'sr': 'Dolazak',
        'en': 'Arrival',
        'ru': 'Прибытие',
        'bg': 'Пристигане',
    },
    'common.duration': {
        'sr': 'Trajanje',
        'en': 'Duration',
        'ru': 'Время в пути',
        'bg': 'Продължителност',
    },
    'common.price': {
        'sr': 'Cena',
        'en': 'Price',
        'ru': 'Цена',
        'bg': 'Цена',
    },
    'common.carrier': {
        'sr': 'Prevoznik',
        'en': 'Carrier',
        'ru': 'Перевозчик',
        'bg': 'Превозвач',
    },
    'common.daily': {
        'sr': 'dnevno',
        'en': 'daily',
        'ru': 'ежедневно',
        'bg': 'дневно',
    },
    'common.lines': {
        'sr': 'linija',
        'en': 'lines',
        'ru': 'линий',
        'bg': 'линии',
    },
    'common.stops': {
        'sr': 'stajališta',
        'en': 'stops',
        'ru': 'остановок',
        'bg': 'спирки',
    },
    'common.routes': {
        'sr': 'ruta',
        'en': 'routes',
        'ru': 'маршрутов',
        'bg': 'маршрута',
    },
    'common.show_more': {
        'sr': 'Prikaži još',
        'en': 'Show more',
        'ru': 'Показать ещё',
        'bg': 'Покажи още',
    },
    'common.read_more': {
        'sr': 'Pročitaj više',
        'en': 'Read more',
        'ru': 'Читать дальше',
        'bg': 'Прочети повече',
    },
    'common.read_less': {
        'sr': 'Sakri',
        'en': 'Read less',
        'ru': 'Свернуть',
        'bg': 'Скрий',
    },
    'common.carriers': {
        'sr': 'prevoznika',
        'en': 'carriers',
        'ru': 'перевозчиков',
        'bg': 'превозвачи',
    },
    'common.languages': {
        'sr': 'jezika',
        'en': 'languages',
        'ru': 'языка',
        'bg': 'езика',
    },
    'common.countries': {
        'sr': 'zemalja',
        'en': 'countries',
        'ru': 'стран',
        'bg': 'държави',
    },
    'home.valueprop_aria': {
        'sr': 'Ključne brojke',
        'en': 'Key numbers',
        'ru': 'Ключевые цифры',
        'bg': 'Ключови цифри',
    },
    # Price cell on guide pages where city transport is free. This lived
    # as 'home.valueprop_free' and went out with the hero strip that also
    # used it — leaving two guide pages rendering the literal key text
    # where a price belongs. Renamed to what it actually is.
    # 410 is served for routes/lines/operators that existed and were
    # withdrawn, so the copy says "no longer runs", not "wrong address".
    'error.410_title': {
        'sr': 'Ova stranica više ne postoji',
        'en': 'This page no longer exists',
        'ru': 'Этой страницы больше нет',
    },
    'error.410_text': {
        'sr': 'Linija ili ruta je ukinuta. Pretražite aktuelne polaske ispod.',
        'en': 'This line or route has been withdrawn. Search current departures below.',
        'ru': 'Линия или маршрут отменён. Найдите актуальные рейсы ниже.',
    },
    # Strings that JS injects. They were hard-coded English in mobile.js
    # and toast.js — on a site whose default locale is Serbian, a visitor
    # on a slow connection was shown "Tap to load map" in English, and
    # screen readers got English labels in every locale.
    'maps.tap_to_load': {
        'sr': 'Dodirnite da učitate mapu',
        'en': 'Tap to load map',
        'ru': 'Нажмите, чтобы загрузить карту',
        'bg': 'Докоснете, за да заредите картата',
    },
    'a11y.load_map': {
        'sr': 'Učitaj interaktivnu mapu',
        'en': 'Load interactive map',
        'ru': 'Загрузить интерактивную карту',
        'bg': 'Зареди интерактивна карта',
    },
    'a11y.notifications': {
        'sr': 'Obaveštenja',
        'en': 'Notifications',
        'ru': 'Уведомления',
        'bg': 'Известия',
    },
    # Home value strip. Every claim here is one the site already makes in
    # its footer or buy note — free/no registration, data from public
    # sources, and the fact that Prevozni does not sell tickets itself.
    # Nothing about price guarantees: we take an affiliate commission and
    # cannot verify the partner's price against the carrier's own.
    'home.trust_compare_h': {
        'sr': '{routes} ruta sa cenama',
        'en': '{routes} routes with prices',
        'ru': '{routes} маршрутов с ценами',
        'bg': '{routes} маршрута с цени',
    },
    'home.trust_compare_p': {
        'sr': 'Polasci {operators} prevoznika na jednom mestu',
        'en': 'Departures from {operators} carriers in one place',
        'ru': 'Рейсы {operators} перевозчиков в одном месте',
        'bg': 'Тръгвания на {operators} превозвача на едно място',
    },
    'home.trust_free_h': {
        'sr': 'Besplatno',
        'en': 'Free',
        'ru': 'Бесплатно',
        'bg': 'Безплатно',
    },
    'home.trust_free_p': {
        'sr': 'Bez registracije i bez naloga',
        'en': 'No registration, no account',
        'ru': 'Без регистрации и аккаунта',
        'bg': 'Без регистрация и без акаунт',
    },
    'home.trust_source_h': {
        'sr': 'Javni izvori',
        'en': 'Public sources',
        'ru': 'Открытые источники',
        'bg': 'Публични източници',
    },
    'home.trust_source_p': {
        'sr': 'Red vožnje i cene samih prevoznika',
        'en': 'Timetables and fares from the carriers',
        'ru': 'Расписание и цены самих перевозчиков',
        'bg': 'Разписания и цени на самите превозвачи',
    },
    'home.trust_buy_h': {
        'sr': 'Kupovina kod prevoznika',
        'en': 'You buy from the carrier',
        'ru': 'Покупка у перевозчика',
        'bg': 'Купуване от превозвача',
    },
    'home.trust_buy_p': {
        'sr': 'Vodimo vas na zvaničnu prodaju karata',
        'en': 'We take you to the official ticket seller',
        'ru': 'Ведём вас на официальную продажу билетов',
        'bg': 'Насочваме ви към официалната продажба на билети',
    },
    'home.trust_aria': {
        'sr': 'Zašto Prevozni',
        'en': 'Why Prevozni',
        'ru': 'Почему Prevozni',
        'bg': 'Защо Prevozni',
    },
    # 44 of 74 cards on Beograd–Novi Sad carry no fare, yet every one of
    # them has a Kupi button. The price cell was simply omitted, so the
    # card said "buy" over a blank where every neighbouring card shows
    # money. Name the blank instead of leaving it.
    'trip.price_on_partner': {
        'sr': 'Cena pri kupovini',
        'en': 'Price at checkout',
        'ru': 'Цена при покупке',
    },
    'common.free': {
        'sr': 'Besplatno',
        'en': 'Free',
        'ru': 'Бесплатно',
        'bg': 'Безплатно',
    },
    'ads.dismiss_aria': {
        'sr': 'Zatvori reklamu',
        'en': 'Dismiss ad',
        'ru': 'Закрыть рекламу',
        'bg': 'Затвори рекламата',
    },
    # The chat widget carried these three inline as
    #   _('chat.x') if _('chat.x') != 'chat.x' else '<Serbian>'
    # — a guard against the keys not existing, which meant EN and RU
    # visitors were served Serbian chat copy. Defined properly instead.
    'chat.powered_by': {
        'sr': 'Prevozni · AI',
        'en': 'Prevozni · AI',
        'ru': 'Prevozni · AI',
        'bg': 'Prevozni · AI',
    },
    'chat.greeting': {
        'sr': 'Zdravo! Pitaj me o redovima vožnje, cenama karata ili linijama gradskog prevoza.',
        'en': 'Hi! Ask me about timetables, ticket prices or city transport lines.',
        'ru': 'Привет! Спросите меня о расписаниях, ценах на билеты или городских маршрутах.',
        'bg': 'Здравей! Попитай ме за разписанията, цените на билетите или линиите на градския транспорт.',
    },
    'chat.placeholder': {
        'sr': 'Pitaj nešto...',
        'en': 'Ask something...',
        'ru': 'Спросите что-нибудь...',
        'bg': 'Попитай нещо...',
    },
    'ads.label': {
        'sr': 'Reklama',
        'en': 'Advertisement',
        'ru': 'Реклама',
        'bg': 'Реклама',
    },
    'common.now': {
        'sr': 'sada',
        'en': 'now',
        'ru': 'сейчас',
        'bg': 'сега',
    },
    'common.min': {
        'sr': 'min',
        'en': 'min',
        'ru': 'мин',
        'bg': 'мин',
    },
    'common.h': {
        'sr': 'h',
        'en': 'h',
        'ru': 'ч',
        'bg': 'ч',
    },
    'common.map_on_map': {
        'sr': 'stajališta na mapi',
        'en': 'stops on map',
        'ru': 'остановок на карте',
        'bg': 'спирки на картата',
    },

    # ── Routes page ──
    'routes.title': {
        'sr': 'Sve autobuske i vozne rute u Srbiji',
        'en': 'All bus and train routes in Serbia',
        'ru': 'Все автобусные и железнодорожные маршруты Сербии',
        'bg': 'Всички автобусни и жп маршрути в Сърбия',
    },
    'routes.departures': {
        'sr': 'polazaka',
        'en': 'departures',
        'ru': 'рейсов',
        'bg': 'тръгвания',
    },
    'routes.routes_label': {
        'sr': 'ruta',
        'en': 'routes',
        'ru': 'маршрутов',
        'bg': 'маршрута',
    },

    # ── City transport ──
    'city.schedule': {
        'sr': 'Red vožnje',
        'en': 'Schedule',
        'ru': 'Расписание',
    },
    'city.stop': {
        'sr': 'Stajalište',
        'en': 'Stop',
        'ru': 'Остановка',
    },
    'city.line': {
        'sr': 'Linija',
        'en': 'Line',
        'ru': 'Линия',
        'bg': 'Линия',
    },
    'city.next_departures': {
        'sr': 'Sledeći polasci',
        'en': 'Next departures',
        'ru': 'Ближайшие отправления',
    },
    'city.no_data': {
        'sr': 'Nema podataka o linijama',
        'en': 'No line data available',
        'ru': 'Нет данных о линиях',
    },

    # ── How it works ──
    'how.title': {
        'sr': 'Kako radi?',
        'en': 'How it works',
        'ru': 'Как это работает',
    },
    'how.step1': {
        'sr': 'Pretražite',
        'en': 'Search',
        'ru': 'Найдите',
    },
    'how.step1_desc': {
        'sr': 'Unesite odakle i kuda putujete',
        'en': 'Enter your origin and destination',
        'ru': 'Введите откуда и куда едете',
    },
    'how.step2': {
        'sr': 'Uporedite',
        'en': 'Compare',
        'ru': 'Сравните',
    },
    'how.step2_desc': {
        'sr': 'Vreme polaska, cene i prevoznici',
        'en': 'Departure times, prices and carriers',
        'ru': 'Время отправления, цены и перевозчики',
    },
    'how.step3': {
        'sr': 'Putujte',
        'en': 'Travel',
        'ru': 'Путешествуйте',
    },
    'how.step3_desc': {
        'sr': 'Tačan red vožnje, bez registracije',
        'en': 'Accurate schedules, no registration',
        'ru': 'Точное расписание, без регистрации',
    },

    # ── Benefits section ──
    'benefits.free': {
        'sr': '100% besplatno',
        'en': '100% free',
        'ru': '100% бесплатно',
    },
    'benefits.free_desc': {
        'sr': 'Bez registracije, bez skrivenih troškova',
        'en': 'No registration, no hidden fees',
        'ru': 'Без регистрации, без скрытых платежей',
    },
    'benefits.mobile': {
        'sr': 'Interaktivna karta',
        'en': 'Interactive map',
        'ru': 'Интерактивная карта',
    },
    'benefits.mobile_desc': {
        'sr': 'Mapa svih stajališta sa vremenima dolaska',
        'en': 'Map of all stops with arrival times',
        'ru': 'Карта всех остановок со временем прибытия',
    },
    'benefits.realtime': {
        'sr': 'Aktuelni podaci',
        'en': 'Up-to-date data',
        'ru': 'Актуальные данные',
    },
    'benefits.realtime_desc': {
        'sr': 'Redovno ažurirani redovi vožnje',
        'en': 'Regularly updated schedules',
        'ru': 'Регулярно обновляемое расписание',
    },
    'benefits.allinone': {
        'sr': 'Sve na jednom mestu',
        'en': 'All in one place',
        'ru': 'Всё в одном месте',
    },
    'benefits.allinone_desc': {
        'sr': 'Autobus, voz, tramvaj — Srbija, Crna Gora, BiH i region',
        'en': 'Bus, train, tram — Serbia, Montenegro, BiH & region',
        'ru': 'Автобус, поезд, трамвай — Сербия, Черногория, БиГ и регион',
    },

    # ── City transport page ──
    'city.title': {
        'sr': 'Gradski prevoz',
        'en': 'City transport',
        'ru': 'Городской транспорт',
        'bg': 'Градски транспорт',
    },
    'city.lines_count': {
        'sr': 'linija',
        'en': 'lines',
        'ru': 'линий',
        'bg': 'линии',
    },
    'city.stops_on_map': {
        'sr': 'stajališta na mapi',
        'en': 'stops on map',
        'ru': 'остановок на карте',
        'bg': 'спирки на картата',
    },
    'city.stops_label': {
        'sr': 'stajališta',
        'en': 'stops',
        'ru': 'остановок',
        'bg': 'спирки',
    },
    'city.tram_trolley_label': {
        'sr': 'tramvaja i trolejbusa',
        'en': 'tram + trolley lines',
        'ru': 'трамв./троллейб.',
        'bg': 'трамвая и тролейбуса',
    },
    'city.popular_stops': {
        'sr': 'Popularna stajališta',
        'en': 'Popular stops',
        'ru': 'Популярные остановки',
        'bg': 'Популярни спирки',
    },
    'city.carriers_from': {
        'sr': 'Prevoznici iz {city}',
        'en': 'Carriers from {city}',
        'ru': 'Перевозчики из {city}',
        'bg': 'Превозвачи от {city}',
    },
    'line.interchange_stops': {
        'sr': 'Glavna stajališta — presedanja',
        'en': 'Major interchange stops',
        'ru': 'Главные пересадочные остановки',
        'bg': 'Главни спирки — прекачвания',
    },
    'city.intercity': {
        'sr': 'Međugradski prevoz',
        'en': 'Intercity transport',
        'ru': 'Междугородний транспорт',
        'bg': 'Междуградски транспорт',
    },
    'city.all_intercity': {
        'sr': 'Sve međugradske rute',
        'en': 'All intercity routes',
        'ru': 'Все междугородние маршруты',
        'bg': 'Всички междуградски маршрути',
    },
    'city.bus_train_from': {
        'sr': 'Autobus i voz iz',
        'en': 'Bus and train from',
        'ru': 'Автобус и поезд из',
        'bg': 'Автобус и влак от',
    },
    'city.departures_from': {
        'sr': 'Polasci iz',
        'en': 'Departures from',
        'ru': 'Отправления из',
        'bg': 'Заминавания от',
    },
    'city.search_dest': {
        'sr': 'Pretraži destinacije',
        'en': 'Search destinations',
        'ru': 'Поиск направлений',
        'bg': 'Търсене на дестинации',
    },
    'city.eta_note': {
        'sr': 'Vreme dolaska na mapi je procena prema rasporedu. Moguća su odstupanja.',
        'en': 'Arrival times on the map are estimates based on the schedule. Deviations are possible.',
        'ru': 'Время прибытия на карте — оценка по расписанию. Возможны отклонения.',
        'bg': 'Времето на пристигане на картата е приблизително, изчислено по разписанието. Възможни са отклонения.',
    },
    'city.search_line': {
        'sr': 'Broj linije ili naziv...',
        'en': 'Line number or name...',
        'ru': 'Номер линии или название...',
        'bg': 'Номер на линия или име...',
    },
    'city.all': {
        'sr': 'Sve',
        'en': 'All',
        'ru': 'Все',
        'bg': 'Всички',
    },
    'city.tram': {
        'sr': 'Tramvaj',
        'en': 'Tram',
        'ru': 'Трамвай',
        'bg': 'Трамвай',
    },
    'city.trolleybus': {
        'sr': 'Trolejbus',
        'en': 'Trolleybus',
        'ru': 'Троллейбус',
        'bg': 'Тролейбус',
    },
    'city.bus': {
        'sr': 'Autobus',
        'en': 'Bus',
        'ru': 'Автобус',
        'bg': 'Автобус',
    },
    'city.night': {
        'sr': 'Noćne linije',
        'en': 'Night lines',
        'ru': 'Ночные линии',
        'bg': 'Нощни линии',
    },

    # ── Breadcrumbs ──
    'breadcrumb.home': {
        'sr': 'Početna',
        'en': 'Home',
        'ru': 'Главная',
        'bg': 'Начало',
    },

    # ── Contact page ──
    'contact.title': {'sr': 'Kontakt', 'en': 'Contact', 'ru': 'Контакт', 'bg': 'Контакт'},
    'contact.subtitle': {
        'sr': 'Imate pitanje, sugestiju ili ste primetili grešku?',
        'en': 'Have a question, suggestion, or found an error?',
        'ru': 'Есть вопрос, предложение или нашли ошибку?',
        'bg': 'Имате въпрос, предложение или сте забелязали грешка?',
    },
    'contact.name': {'sr': 'Ime', 'en': 'Name', 'ru': 'Имя', 'bg': 'Име'},
    'contact.name_ph': {'sr': 'Vaše ime', 'en': 'Your name', 'ru': 'Ваше имя', 'bg': 'Вашето име'},
    'contact.email': {'sr': 'Email', 'en': 'Email', 'ru': 'Email', 'bg': 'Имейл'},
    'contact.message': {'sr': 'Poruka', 'en': 'Message', 'ru': 'Сообщение', 'bg': 'Съобщение'},
    'contact.message_ph': {
        'sr': 'Opišite vaše pitanje ili sugestiju...',
        'en': 'Describe your question or suggestion...',
        'ru': 'Опишите ваш вопрос или предложение...',
        'bg': 'Опишете вашия въпрос или предложение...',
    },
    'contact.send': {'sr': 'Pošalji', 'en': 'Send', 'ru': 'Отправить', 'bg': 'Изпрати'},
    'contact.response_time': {
        'sr': 'Odgovaramo u roku od',
        'en': 'We respond within',
        'ru': 'Отвечаем в течение',
        'bg': 'Отговаряме в рамките на',
    },
    'contact.hours': {'sr': '24 sata', 'en': '24 hours', 'ru': '24 часов', 'bg': '24 часа'},
    'contact.sent_ok': {
        'sr': 'Poruka je poslata. Hvala!',
        'en': 'Message sent. Thanks!',
        'ru': 'Сообщение отправлено. Спасибо!',
        'bg': 'Съобщението е изпратено. Благодарим!',
    },
    'contact.error.required': {
        'sr': 'Molimo popunite sva polja.',
        'en': 'Please fill in all fields.',
        'ru': 'Пожалуйста, заполните все поля.',
    },
    'contact.error.name_too_long': {
        'sr': 'Ime je predugačko (maksimum 100 karaktera).',
        'en': 'Name is too long (max 100 characters).',
        'ru': 'Имя слишком длинное (максимум 100 символов).',
    },
    'contact.error.email_invalid': {
        'sr': 'Email adresa nije ispravna.',
        'en': 'Email address is not valid.',
        'ru': 'Некорректный email адрес.',
    },
    'contact.error.message_too_long': {
        'sr': 'Poruka je predugačka (maksimum 500 karaktera).',
        'en': 'Message is too long (max 500 characters).',
        'ru': 'Сообщение слишком длинное (максимум 500 символов).',
    },

    # ── About page ──
    'about.title': {'sr': 'O nama', 'en': 'About us', 'ru': 'О нас', 'bg': 'За нас'},
    # /red-voznje/ — head-term hub for "red vožnje autobusa i vozova"
    'nav.timetables': {'sr': 'Red vožnje', 'en': 'Timetables', 'ru': 'Расписание', 'bg': 'Разписание'},
    'red_voznje.title': {
        'sr': 'Red vožnje autobusa i vozova — Srbija',
        'en': 'Bus and train timetables — Serbia',
        'ru': 'Расписание автобусов и поездов — Сербия'},
    'red_voznje.meta': {
        'sr': 'Red vožnje autobusa, vozova i gradskog prevoza u Srbiji na jednom mestu — polasci, cene i linije za međugradske rute i 4 grada.',
        'en': 'Bus, train and city transport timetables across Serbia in one place — departures, prices and lines for intercity routes and 4 cities.',
        'ru': 'Расписание автобусов, поездов и городского транспорта Сербии в одном месте — отправления, цены и линии для междугородних маршрутов и 4 городов.'},
    'red_voznje.h1': {
        'sr': 'Red vožnje autobusa, vozova i gradskog prevoza',
        'en': 'Bus, train and city transport timetables',
        'ru': 'Расписание автобусов, поездов и городского транспорта'},
    'red_voznje.sub': {
        'sr': 'Srbija i region — polasci, cene i linije na jednom mestu',
        'en': 'Serbia and the region — departures, prices and lines in one place',
        'ru': 'Сербия и регион — отправления, цены и линии в одном месте'},
    'red_voznje.intercity_h': {
        'sr': 'Međugradski red vožnje', 'en': 'Intercity timetables',
        'ru': 'Междугородние расписания'},
    'red_voznje.city_h': {
        'sr': 'Gradski red vožnje', 'en': 'City transport timetables',
        'ru': 'Городской транспорт'},
    'red_voznje.carriers_h': {
        'sr': 'Prevoznici', 'en': 'Carriers', 'ru': 'Перевозчики'},
    'red_voznje.prose': {
        'sr': 'Prevozni objedinjuje red vožnje autobusa, vozova i gradskog prevoza širom Srbije. Na jednom mestu pronađite polaske, cene i trajanje za međugradske rute, kao i linije, stajališta i vreme dolaska za gradski prevoz u Beogradu, Novom Sadu, Nišu i Kragujevcu. Podaci se osvežavaju svakodnevno iz zvaničnih izvora.',
        'en': 'Prevozni brings together bus, train and city transport timetables across Serbia. Find departures, prices and durations for intercity routes, plus lines, stops and arrival times for city transport in Belgrade, Novi Sad, Niš and Kragujevac — all in one place, refreshed daily from official sources.',
        'ru': 'Prevozni собирает расписание автобусов, поездов и городского транспорта по всей Сербии. Отправления, цены и время в пути для междугородних маршрутов, а также линии, остановки и время прибытия городского транспорта Белграда, Нови-Сада, Ниша и Крагуеваца — в одном месте, обновляется ежедневно.'},
    'about.meta_short': {
        'sr': 'Prevozni — besplatni red vožnje autobusa, vozova i gradskog prevoza u Srbiji. Bez registracije, na 3 jezika.',
        'en': 'Prevozni — free bus, train and city transport schedules across Serbia. No registration, in 3 languages.',
        'ru': 'Prevozni — бесплатное расписание автобусов, поездов и городского транспорта в Сербии. Без регистрации, на 3 языках.',
        'bg': 'Prevozni — безплатно разписание на автобуси, влакове и градски транспорт в Сърбия. Без регистрация, на 3 езика.',
    },
    'about.intro_short': {
        'sr': 'Prevozni objedinjuje raspored {routes}+ međugradskih ruta i {ops}+ prevoznika u Srbiji i regionu, plus gradski prevoz u 4 grada. Besplatno, bez registracije, na 3 jezika.',
        'en': 'Prevozni aggregates schedules for {routes}+ intercity routes from {ops}+ carriers in Serbia and the region, plus city transit in 4 cities. Free, no signup, in 3 languages.',
        'ru': 'Prevozni объединяет расписание {routes}+ междугородних маршрутов и {ops}+ перевозчиков в Сербии и регионе, плюс городской транспорт в 4 городах. Бесплатно, без регистрации, на 3 языках.',
        'bg': 'Prevozni обединява разписанието на {routes}+ междуградски линии и {ops}+ превозвачи в Сърбия и региона, плюс градски транспорт в 4 града. Безплатно, без регистрация, на 3 езика.',
    },
    'about.search_h': {
        'sr': 'Pronađite vožnju',
        'en': 'Find a ride',
        'ru': 'Найти рейс',
        'bg': 'Намерете превоз',
    },
    'about.sources_short': {
        'sr': 'Podatke prikupljamo svakodnevnim skraperima sa zvaničnih izvora — bgprevoz.rs, gspns.co.rs, jgpnis.rs, busticket4.me, polazak.rs, srbijavoz.rs i drugih. Pre putovanja proverite raspored direktno kod prevoznika; cene i polasci se mogu menjati. Prevozni je besplatan i ne prodaje karte — kupovina ide kod naših affiliate partnera.',
        'en': 'Data is collected daily from official sources — bgprevoz.rs, gspns.co.rs, jgpnis.rs, busticket4.me, polazak.rs, srbijavoz.rs and others. Always confirm the schedule with the carrier before traveling; prices and departures can change. Prevozni is free and does not sell tickets — purchases go through our affiliate partners.',
        'ru': 'Данные обновляются ежедневными скраперами из официальных источников — bgprevoz.rs, gspns.co.rs, jgpnis.rs, busticket4.me, polazak.rs, srbijavoz.rs и других. Перед поездкой обязательно сверяйтесь с расписанием перевозчика; цены и рейсы могут меняться. Prevozni бесплатен и не продает билеты — покупка идет через наших affiliate-партнёров.',
        'bg': 'Данните събираме ежедневно чрез скрепери от официални източници — bgprevoz.rs, gspns.co.rs, jgpnis.rs, busticket4.me, polazak.rs, srbijavoz.rs и други. Преди пътуване проверете разписанието директно при превозвача; цените и часовете на тръгване може да се променят. Prevozni е безплатен и не продава билети — покупката се извършва при нашите афилиейт партньори.',
    },
    'about.mission': {
        'sr': 'Prevozni prikuplja i objedinjuje podatke iz različitih izvora kako bi vam uštedeo vreme pri planiranju putovanja kroz Srbiju.',
        'en': 'Prevozni collects and aggregates data from various sources to save you time when planning travel through Serbia.',
        'ru': 'Prevozni собирает и объединяет данные из различных источников, чтобы сэкономить ваше время при планировании поездок по Сербии.',
    },
    'about.disclaimer_title': {'sr': 'Napomena', 'en': 'Disclaimer', 'ru': 'Примечание'},
    'about.disclaimer': {
        'sr': 'Ovaj sajt prikuplja podatke iz javno dostupnih izvora i ne garantuje njihovu tačnost. Pre putovanja obavezno proverite red vožnje direktno kod prevoznika pre putovanja. Prevozni ne prodaje karte niti posreduje u prodaji prevoznih usluga.',
        'en': 'This site collects data from publicly available sources and does not guarantee its accuracy. Always check the schedule directly with the carrier before traveling. Prevozni does not sell tickets.',
        'ru': 'Сайт собирает данные из открытых источников и не гарантирует их точность. Перед поездкой обязательно проверяйте расписание у перевозчика. Prevozni не продает билеты.',
    },

    # ── See also / shared sections ──
    'see_also.title': {'sr': 'Pogledajte još', 'en': 'See also', 'ru': 'Смотрите также', 'bg': 'Вижте още'},
    'see_also.all_routes': {'sr': 'Sve međugradske rute', 'en': 'All intercity routes', 'ru': 'Все междугородние маршруты', 'bg': 'Всички междуградски маршрути'},
    'see_also.all_routes_desc': {
        'sr': 'Autobus i voz između gradova Srbije',
        'en': 'Bus and train between Serbian cities',
        'ru': 'Автобус и поезд между городами Сербии',
        'bg': 'Автобус и влак между градовете на Сърбия',
    },
    'see_also.city_beograd': {'sr': 'Gradski prevoz Beograd', 'en': 'Belgrade city transport', 'ru': 'Городской транспорт Белград', 'bg': 'Градски транспорт Белград'},
    'see_also.city_desc': {'sr': 'Linije, stajališta, mapa', 'en': 'Lines, stops, map', 'ru': 'Линии, остановки, карта', 'bg': 'Линии, спирки, карта'},
    'see_also.about': {'sr': 'O nama', 'en': 'About us', 'ru': 'О нас'},
    'see_also.about_desc': {'sr': 'Misija i izvori podataka', 'en': 'Mission and data sources', 'ru': 'Миссия и источники данных', 'bg': 'Мисия и източници на данни'},
    'see_also.country_hint': {
        'sr': 'Pogledajte sve rute do destinacija u ovoj zemlji',
        'en': 'See all routes to destinations in this country',
        'ru': 'Все маршруты до направлений в этой стране',
    },
    'see_also.country_network': {
        'sr': 'Druge zemlje na Prevozni',
        'en': 'Other countries on Prevozni',
        'ru': 'Другие страны на Prevozni',
        'bg': 'Други държави в Prevozni',
    },

    # ── Route pages ──
    'route.schedule': {'sr': 'Red vožnje', 'en': 'Schedule', 'ru': 'Расписание', 'bg': 'Разписание'},
    'route.reverse': {
        'sr': 'Pogledajte i obrnuti smer',
        'en': 'See the reverse direction',
        'ru': 'Смотрите обратное направление',
        'bg': 'Вижте и обратната посока',
    },

    # ── Search results ──
    'search.title': {'sr': 'Pretraga', 'en': 'Search', 'ru': 'Поиск', 'bg': 'Търсене'},
    'search.results_for': {'sr': 'Rezultati pretrage', 'en': 'Search results', 'ru': 'Результаты поиска', 'bg': 'Резултати от търсенето'},
    'search.no_results': {'sr': 'Nema rezultata', 'en': 'No results', 'ru': 'Нет результатов', 'bg': 'Няма резултати'},
    'route.filter_no_match': {
        'sr': 'Nijedan polazak ne odgovara izabranim filterima.',
        'en': 'No departures match your filters.',
        'ru': 'Ни один рейс не соответствует выбранным фильтрам.',
        'bg': 'Нито едно тръгване не отговаря на избраните филтри.',
    },

    # ── Error pages ──
    'error.404_text': {
        'sr': 'Stranica koju tražite ne postoji ili je uklonjena.',
        'en': 'The page you are looking for does not exist or has been removed.',
        'ru': 'Страница, которую вы ищете, не существует или была удалена.',
    },
    'error.500_title': {'sr': 'Došlo je do greške', 'en': 'Something went wrong', 'ru': 'Произошла ошибка'},
    'error.500_text': {
        'sr': 'Pokušajte ponovo ili se vratite na početnu',
        'en': 'Try again or go back to the homepage',
        'ru': 'Попробуйте снова или вернитесь на главную',
    },

    # ── Carriers page ──
    'carriers.bus': {'sr': 'Autobuski prevoznici', 'en': 'Bus carriers', 'ru': 'Автобусные перевозчики'},
    'carriers.train': {'sr': 'Železnički prevoznici', 'en': 'Train carriers', 'ru': 'Железнодорожные перевозчики'},

    # ── Stations page ──

    # ── Line detail ──
    'line.stops': {'sr': 'stajališta', 'en': 'stops', 'ru': 'остановок', 'bg': 'спирки'},
    'line.direction_a': {'sr': 'Smer A', 'en': 'Direction A', 'ru': 'Направление А'},
    'line.direction_b': {'sr': 'Smer B', 'en': 'Direction B', 'ru': 'Направление Б'},
    'line.first_departure': {'sr': 'Prvi polazak', 'en': 'First departure', 'ru': 'Первый рейс'},
    'line.last_departure': {'sr': 'Poslednji polazak', 'en': 'Last departure', 'ru': 'Последний рейс'},

    # ── Stop detail ──
    'stop.lines_here': {'sr': 'Linije na ovom stajalištu', 'en': 'Lines at this stop', 'ru': 'Линии на этой остановке', 'bg': 'Линии на тази спирка'},
    'stop.next_arrivals': {'sr': 'Sledeći polasci', 'en': 'Next departures', 'ru': 'Ближайшие отправления'},

    # ── Route detail / search ──
    'route.daily_departures': {'sr': 'polazaka dnevno', 'en': 'departures daily', 'ru': 'рейсов в день', 'bg': 'тръгвания дневно'},
    'route.per_day': {'sr': 'polazaka/dan', 'en': 'departures/day', 'ru': 'рейсов/день', 'bg': 'тръгвания/ден'},
    'route.shown_of': {'sr': 'Prikazano', 'en': 'Shown', 'ru': 'Показано', 'bg': 'Показани'},
    'route.of': {'sr': 'od', 'en': 'of', 'ru': 'из', 'bg': 'от'},
    'route.km': {'sr': 'km', 'en': 'km', 'ru': 'км', 'bg': 'км'},
    'route.from_price': {'sr': 'od', 'en': 'from', 'ru': 'от', 'bg': 'от'},
    'route.see_reverse': {
        'sr': 'Pogledajte i obrnuti smer',
        'en': 'See also the reverse direction',
        'ru': 'Смотрите также обратное направление',
        'bg': 'Вижте също и обратната посока',
    },
    'route.all_routes': {'sr': 'Sve rute', 'en': 'All routes', 'ru': 'Все маршруты', 'bg': 'Всички маршрути'},
    'route.filter_all': {'sr': 'Svi polasci', 'en': 'All departures', 'ru': 'Все рейсы', 'bg': 'Всички тръгвания'},
    'route.sort_label': {'sr': 'Sortiraj', 'en': 'Sort', 'ru': 'Сортировка', 'bg': 'Сортирай'},
    'route.sort_time': {'sr': 'Po polasku', 'en': 'Departure', 'ru': 'По отправлению', 'bg': 'По тръгване'},
    'route.sort_price': {'sr': 'Najjeftinije', 'en': 'Cheapest', 'ru': 'Дешевле', 'bg': 'Най-евтино'},
    'route.sort_duration': {'sr': 'Najbrže', 'en': 'Fastest', 'ru': 'Быстрее', 'bg': 'Най-бързо'},
    'route.carrier_all': {'sr': 'Svi prevoznici', 'en': 'All carriers', 'ru': 'Все перевозчики', 'bg': 'Всички превозвачи'},
    'route.workday': {'sr': 'Radnim danom', 'en': 'Weekdays', 'ru': 'Будни', 'bg': 'Работни дни'},
    'route.weekend': {'sr': 'Vikend', 'en': 'Weekend', 'ru': 'Выходные', 'bg': 'Уикенд'},

    # ── Search page ──
    'search.departures_found': {'sr': 'polazaka', 'en': 'departures', 'ru': 'рейсов', 'bg': 'тръгвания'},
    'search.no_results_text': {
        'sr': 'Nismo pronašli direktne polaske za ovaj pravac.',
        'en': 'No direct departures found for this route.',
        'ru': 'Прямых рейсов по этому маршруту не найдено.',
        'bg': 'Не намерихме директни тръгвания за това направление.',
    },
    'connections.badge': {'sr': 'Sa presedanjem', 'en': 'With a connection', 'ru': 'С пересадкой', 'bg': 'С прекачване'},
    'connections.heading': {
        'sr': 'Nema direktne linije, ali možete presesti',
        'en': 'No direct route, but you can connect',
        'ru': 'Прямого рейса нет, но можно пересесть',
        'bg': 'Няма директна линия, но можете да прекачите',
    },
    'connections.via': {'sr': 'preko', 'en': 'via', 'ru': 'через', 'bg': 'през'},
    'connections.wait': {'sr': 'čekanje', 'en': 'wait', 'ru': 'ожидание', 'bg': 'изчакване'},
    'connections.leg': {'sr': 'Deonica', 'en': 'Leg', 'ru': 'Отрезок', 'bg': 'Отсечка'},
    'connections.total_price': {'sr': 'Ukupno od', 'en': 'Total from', 'ru': 'Всего от', 'bg': 'Общо от'},
    'connections.disclaimer': {
        'sr': 'Dve odvojene karte, kod različitih prevoznika — kupuju se posebno na svakoj deonici.',
        'en': 'Two separate tickets, different carriers — bought separately for each leg.',
        'ru': 'Два отдельных билета у разных перевозчиков — покупаются раздельно на каждом отрезке.',
        'bg': 'Два отделни билета, при различни превозвачи — купуват се поотделно за всяка отсечка.',
    },

    # ── Line detail ──
    'line.timeline': {'sr': 'Trasa linije', 'en': 'Line route', 'ru': 'Маршрут линии'},
    'line.schedule_title': {'sr': 'Red vožnje', 'en': 'Schedule', 'ru': 'Расписание', 'bg': 'Разписание'},
    'line.departures_from': {'sr': 'Polasci od', 'en': 'Departures from', 'ru': 'Отправление от'},

    # ── Stop detail ──
    'stop.title': {'sr': 'Stajalište', 'en': 'Stop', 'ru': 'Остановка'},
    'stop.on_map': {'sr': 'na mapi', 'en': 'on map', 'ru': 'на карте'},
    'stop.nearby': {'sr': 'Obližnja stajališta', 'en': 'Nearby stops', 'ru': 'Ближайшие остановки', 'bg': 'Близки спирки'},
    # New strings introduced when porting route_detail chrome to stop_detail
    # (parity audit 2026-04-26).
    'stop.subtitle': {
        'sr': 'Stajalište gradskog prevoza',
        'en': 'Public transport stop',
        'ru': 'Остановка городского транспорта',
        'bg': 'Спирка на градския транспорт',
    },
    'stop.back_to_city': {
        'sr': 'Sve linije i stajališta',
        'en': 'All lines and stops',
        'ru': 'Все линии и остановки',
        'bg': 'Всички линии и спирки',
    },
    'stop.lines_count_label': {
        'sr': 'linija', 'en': 'lines', 'ru': 'линий',
        'bg': 'линии',
    },
    'stop.first_dep_label': {
        'sr': 'prvi polazak', 'en': 'first departure', 'ru': 'первый рейс',
    },
    'stop.last_dep_label': {
        'sr': 'poslednji polazak', 'en': 'last departure', 'ru': 'последний рейс',
    },
    'stop.coords_label': {
        'sr': 'na mapi', 'en': 'on map', 'ru': 'на карте',
        'bg': 'на картата',
    },
    'stop.action_title': {
        'sr': 'Planiraj putovanje',
        'en': 'Plan your trip',
        'ru': 'Спланировать поездку',
        'bg': 'Планирай пътуването',
    },
    'stop.action_search': {
        'sr': 'Pretraži polaske odavde',
        'en': 'Search departures from here',
        'ru': 'Найти рейсы отсюда',
        'bg': 'Търси тръгванията оттук',
    },
    'stop.action_maps': {
        'sr': 'Otvori u mapama',
        'en': 'Open in maps',
        'ru': 'Открыть на карте',
        'bg': 'Отвори в картите',
    },
    'stop.action_note': {
        'sr': 'ETA se računa na osnovu zvaničnog GTFS reda vožnje.',
        'en': 'ETA is computed from the official GTFS schedule.',
        'ru': 'ETA рассчитывается по официальному расписанию GTFS.',
        'bg': 'ETA се изчислява въз основа на официалното разписание по GTFS.',
    },
    'stop.lines_via': {
        'sr': 'Linije kroz ovo stajalište',
        'en': 'Lines via this stop',
        'ru': 'Линии через эту остановку',
    },

    # ── Line detail (parity-port) ──
    'line.subtitle': {
        'sr': 'Linija gradskog prevoza',
        'en': 'Public transport line',
        'ru': 'Линия городского транспорта',
    },
    'line.back_to_city': {
        'sr': 'Sve linije',
        'en': 'All lines',
        'ru': 'Все линии',
        'bg': 'Всички линии',
    },
    'line.action_title': {
        'sr': 'Saznaj kada krećeš',
        'en': 'Find your departure',
        'ru': 'Найди свой рейс',
        'bg': 'Разбери кога тръгваш',
    },
    'line.action_search': {
        'sr': 'Pretraži kroz mrežu linija',
        'en': 'Search the line network',
        'ru': 'Поиск по сети линий',
        'bg': 'Търси в мрежата от линии',
    },
    'line.action_map': {
        'sr': 'Pogledaj trasu na mapi',
        'en': 'See route on map',
        'ru': 'Посмотреть маршрут на карте',
        'bg': 'Виж маршрута на картата',
    },
    'line.stop_count_label': {
        'sr': 'stajališta', 'en': 'stops', 'ru': 'остановок',
        'bg': 'спирки',
    },
    'line.type_label': {
        'sr': 'tip', 'en': 'type', 'ru': 'тип',
        'bg': 'тип',
    },
    'line.service_label': {
        'sr': 'polasci', 'en': 'service', 'ru': 'рейсы',
        'bg': 'тръгвания',
    },
    'line.frequency_label': {
        'sr': 'interval', 'en': 'every', 'ru': 'интервал',
        'bg': 'интервал',
    },
    'line.filter_all': {
        'sr': 'Svi polasci', 'en': 'All departures', 'ru': 'Все рейсы',
    },
    'line.filter_workday': {
        'sr': 'Radni dan', 'en': 'Workday', 'ru': 'Будни',
    },
    'line.filter_weekend': {
        'sr': 'Vikend', 'en': 'Weekend', 'ru': 'Выходные',
    },
    'line.day_workday': {
        'sr': 'Radni dan', 'en': 'Weekday', 'ru': 'Будни',
        'bg': 'Делничен ден',
    },
    'line.day_saturday': {
        'sr': 'Subota', 'en': 'Saturday', 'ru': 'Суббота',
        'bg': 'Събота',
    },
    'line.day_sunday': {
        'sr': 'Nedelja', 'en': 'Sunday', 'ru': 'Воскресенье',
        'bg': 'Неделя',
    },
    'line.schedule_from_first': {
        'sr': 'polasci od prvog stajališta',
        'en': 'from first stop',
        'ru': 'от первой остановки',
        'bg': 'тръгвания от първата спирка',
    },
    'line.schedule_from': {
        'sr': 'polasci sa',
        'en': 'departures from',
        'ru': 'отправления с',
        'bg': 'тръгвания от',
    },

    # ── City index ──
    'city_index.title': {
        'sr': 'Gradski Prevoz Srbija — Linije i Red Vožnje',
        'en': 'City Transport Serbia — Lines & Schedule',
        'ru': 'Городской Транспорт Сербии — Линии и Расписание',
    },

    # ── Carriers / Stations ──
    'stations.train': {'sr': 'Železničke stanice', 'en': 'Train stations', 'ru': 'Ж/д станции'},

    'search_results.sort_duration': {
        'sr': 'Trajanje',
        'en': 'Duration',
        'ru': 'Длительность',
        'bg': 'Продължителност',
    },

    # ── Operator detail page ──
    'operator.title_suffix': {
        'sr': 'rute i red vožnje',
        'en': 'routes and schedules',
        'ru': 'маршруты и расписание',
    },
    'operator.faq.q_routes': {
        'sr': 'Koliko ruta opslužuje {name}?',
        'en': 'How many routes does {name} operate?',
        'ru': 'Сколько маршрутов обслуживает {name}?',
    },
    'operator.faq.a_routes': {
        'sr': '{name} saobraća na {routes} ruta sa ukupno {trips} polazaka dnevno.',
        'en': '{name} operates {routes} routes with {trips} departures daily.',
        'ru': '{name} обслуживает {routes} маршрутов, всего {trips} рейсов в день.',
    },
    'operator.faq.q_price': {
        'sr': 'Koliko košta karta kod {name}?',
        'en': 'How much does a ticket with {name} cost?',
        'ru': 'Сколько стоит билет у {name}?',
    },
    'operator.faq.a_price': {
        'sr': 'Cene karata kod {name} kreću se od {min} do {max} RSD.',
        'en': 'Tickets with {name} cost from {min} to {max} RSD.',
        'ru': 'Билеты у {name} стоят от {min} до {max} RSD.',
    },
    'operator.faq.q_countries': {
        'sr': 'Koje zemlje pokriva {name}?',
        'en': 'Which countries does {name} serve?',
        'ru': 'Какие страны обслуживает {name}?',
    },
    'operator.faq.a_countries': {
        'sr': '{name} saobraća u: {countries}.',
        'en': '{name} operates to: {countries}.',
        'ru': '{name} обслуживает направления: {countries}.',
    },
    'country.faq.q_travel': {
        'sr': 'Kako doći do {country} iz Srbije?',
        'en': 'How to get to {country} from Serbia?',
        'ru': 'Как добраться до {country} из Сербии?',
        'bg': 'Как да стигна до {country} от Сърбия?',
    },
    'country.faq.a_travel': {
        'sr': 'Iz Srbije do {country} saobraća {routes} autobuskih linija. Red vožnje, cene i prevoznici na jednom mestu.',
        'en': '{routes} bus routes run from Serbia to {country}. Schedules, prices and carriers in one place.',
        'ru': 'Из Сербии в {country} ходит {routes} автобусных маршрутов. Расписание, цены и перевозчики в одном месте.',
        'bg': 'От Сърбия до {country} се движат {routes} автобусни линии. Разписание, цени и превозвачи на едно място.',
    },
    'country.faq.q_price': {
        'sr': 'Koliko košta karta za {country}?',
        'en': 'How much is a ticket to {country}?',
        'ru': 'Сколько стоит билет в {country}?',
        'bg': 'Колко струва билет за {country}?',
    },
    'country.faq.a_price': {
        'sr': 'Karte za {country} počinju od {min} RSD, u zavisnosti od grada i prevoznika.',
        'en': 'Tickets to {country} start from {min} RSD, depending on the city and carrier.',
        'ru': 'Билеты в {country} — от {min} RSD, в зависимости от города и перевозчика.',
        'bg': 'Билетите за {country} започват от {min} RSD, в зависимост от града и превозвача.',
    },
    'operator.meta_routes': {
        'sr': 'međugradskih ruta',
        'en': 'intercity routes',
        'ru': 'междугородних маршрутов',
    },
    'operator.meta_trips': {
        'sr': 'polazaka',
        'en': 'departures',
        'ru': 'отправлений',
    },
    'operator.meta_cta': {
        'sr': 'Uporedite cene, vidite raspored. Besplatno.',
        'en': 'Compare prices, see schedules. Free.',
        'ru': 'Сравните цены, посмотрите расписание. Бесплатно.',
    },
    'operator.cities_count': {
        'sr': 'gradova u mreži',
        'en': 'cities served',
        'ru': 'городов в сети',
    },
    'operator.routes_heading': {
        'sr': 'Sve rute prevoznika',
        'en': 'All operator routes',
        'ru': 'Все маршруты перевозчика',
    },
    'operator.no_routes': {
        'sr': 'Trenutno nema dostupnih ruta za ovog prevoznika.',
        'en': 'No routes available for this carrier at the moment.',
        'ru': 'В настоящее время нет доступных маршрутов для этого перевозчика.',
    },
    'operator.about_h': {
        'sr': 'O prevozniku {name}',
        'en': 'About carrier {name}',
        'ru': 'О перевозчике {name}',
    },
    'operator.about_p': {
        'sr': '{name} je autobuski prevoznik u Srbiji i regionu. Na Prevozni.com možete pronaći raspored i cene za {routes} međugradskih ruta ovog prevoznika sa ukupno {trips} dnevnih polazaka. Mreža pokriva {cities} gradova.',
        'en': '{name} is a bus carrier in Serbia and the region. On Prevozni.com you can find schedules and prices for {routes} intercity routes run by this carrier, with {trips} daily departures in total. The network covers {cities} cities.',
        'ru': '{name} — автобусный перевозчик в Сербии и регионе. На Prevozni.com можно найти расписание и цены на {routes} междугородних маршрутов этого перевозчика, всего {trips} ежедневных отправлений. Сеть охватывает {cities} городов.',
    },
    # ── Favourites (localStorage) ──
    'fav.title': {
        'sr': 'Sačuvane rute',
        'en': 'Saved routes',
        'ru': 'Сохранённые маршруты',
    },
    'fav.meta': {
        'sr': 'Vaše sačuvane autobuske rute na Prevozni. Rute su sačuvane lokalno u vašem pregledaču.',
        'en': 'Your saved bus routes on Prevozni. Routes are stored locally in your browser.',
        'ru': 'Ваши сохранённые автобусные маршруты на Prevozni. Маршруты хранятся локально в браузере.',
    },
    'fav.h1': {'sr': 'Sačuvane rute', 'en': 'Saved routes', 'ru': 'Сохранённые маршруты'},
    'fav.save_aria': {
        'sr': 'Sačuvaj rutu',
        'en': 'Save route',
        'ru': 'Сохранить маршрут',
        'bg': 'Запази маршрута',
    },
    'fav.remove': {
        'sr': 'Ukloni',
        'en': 'Remove',
        'ru': 'Убрать',
    },
    'fav.zero': {
        'sr': 'Još nemate sačuvanih ruta',
        'en': 'No saved routes yet',
        'ru': 'Сохранённых маршрутов пока нет',
    },
    'fav.count_suffix': {
        'sr': 'ruta sačuvano',
        'en': 'routes saved',
        'ru': 'маршрутов сохранено',
    },
    'fav.empty': {
        'sr': 'Nemate sačuvanih ruta',
        'en': 'You have no saved routes',
        'ru': 'У вас нет сохранённых маршрутов',
    },
    'fav.empty_sub': {
        'sr': 'Kliknite zvezdicu pored naziva rute da biste je sačuvali.',
        'en': 'Click the star next to a route name to save it.',
        'ru': 'Нажмите звёздочку рядом с названием маршрута чтобы сохранить его.',
    },
    'fav.browse_routes': {
        'sr': 'Pregledaj sve rute',
        'en': 'Browse all routes',
        'ru': 'Посмотреть все маршруты',
    },

    # ── Offline fallback (PWA) ──
    'offline.title': {
        'sr': 'Nema interneta',
        'en': 'You are offline',
        'ru': 'Нет интернета',
    },
    'offline.meta': {
        'sr': 'Trenutno ste van mreže. Prevozni će se ponovo povezati čim se vrati internet.',
        'en': 'You are currently offline. Prevozni will reconnect as soon as the internet is back.',
        'ru': 'Вы сейчас офлайн. Prevozni подключится снова как только появится интернет.',
    },
    'offline.h1': {
        'sr': 'Nema interneta',
        'en': 'You are offline',
        'ru': 'Нет интернета',
    },
    'offline.sub': {
        'sr': 'Proverite konekciju i pokušajte ponovo.',
        'en': 'Check your connection and try again.',
        'ru': 'Проверьте подключение и попробуйте снова.',
    },
    'offline.back_home': {
        'sr': 'Nazad na početnu',
        'en': 'Back to home',
        'ru': 'На главную',
    },

    # ── Guides / blog ──
    'guides.index_title': {
        'sr': 'Vodiči za putovanja autobusom — Prevozni',
        'en': 'Bus travel guides — Prevozni',
        'ru': 'Гиды по автобусным поездкам — Prevozni',
        'bg': 'Пътеводители за пътувания с автобус — Prevozni',
    },
    'guides.index_meta': {
        'sr': 'Praktični vodiči za putovanja autobusom i vozom po Srbiji i Balkanu: cene, redovi vožnje, poređenja, saveti.',
        'en': 'Practical guides for bus and train travel across Serbia and the Balkans: prices, schedules, comparisons, tips.',
        'ru': 'Практические гиды по автобусным и железнодорожным поездкам по Сербии и Балканам: цены, расписания, сравнения, советы.',
        'bg': 'Практични пътеводители за пътувания с автобус и влак из Сърбия и Балканите: цени, разписания, сравнения, съвети.',
    },
    'guides.index_h1': {
        'sr': 'Vodiči za putnike',
        'en': 'Traveller guides',
        'ru': 'Гиды для путешественников',
        'bg': 'Пътеводители за пътници',
    },
    'guides.index_subtitle': {
        'sr': 'Sve što treba da znate pre putovanja',
        'en': 'Everything you need to know before you travel',
        'ru': 'Всё что нужно знать перед поездкой',
        'bg': 'Всичко, което трябва да знаете преди пътуването',
    },
    'guides.intro_h': {
        'sr': 'Kako koristiti ove vodiče',
        'en': 'How to use these guides',
        'ru': 'Как пользоваться этими гидами',
        'bg': 'Как да използвате тези пътеводители',
    },
    'guides.intro_p': {
        'sr': 'Naši vodiči odgovaraju na konkretna pitanja putnika: kako doći do određenog grada, kada su najjeftinije karte, kako izabrati između autobusa i voza. Sav sadržaj se ažurira kada se promene redovi vožnje ili cene kod prevoznika.',
        'en': 'Our guides answer specific traveller questions: how to reach a specific city, when tickets are cheapest, how to choose between bus and train. All content is refreshed when carrier schedules or prices change.',
        'ru': 'Наши гиды отвечают на конкретные вопросы путешественников: как добраться до определённого города, когда билеты дешевле, как выбрать между автобусом и поездом. Весь контент обновляется при изменениях расписания или цен у перевозчиков.',
        'bg': 'Нашите пътеводители отговарят на конкретни въпроси на пътниците: как да стигнете до определен град, кога билетите са най-евтини, как да изберете между автобус и влак. Цялото съдържание се актуализира при промяна на разписанията или цените на превозвачите.',
    },
    'guides.cat_travel': {'sr': 'Putovanja', 'en': 'Travel', 'ru': 'Путешествия', 'bg': 'Пътувания'},
    'guides.cat_tips': {'sr': 'Saveti', 'en': 'Tips', 'ru': 'Советы', 'bg': 'Съвети'},

    # Guide 1 — Belgrade → Budva
    'guides.beograd_budva.title': {
        'sr': 'Kako doći iz Beograda u Budvu: autobus, voz, cene 2026',
        'en': 'How to get from Belgrade to Budva: bus, train, prices 2026',
        'ru': 'Как добраться из Белграда в Будву: автобус, поезд, цены 2026',
        'bg': 'Как да стигнете от Белград до Будва: автобус, влак, цени 2026',
    },
    'guides.beograd_budva.meta': {
        'sr': 'Pun vodič za put Beograd → Budva 2026: autobus (najbrže, 10–12h), cene od 30€, preporučeni prevoznici i saveti.',
        'en': 'Full guide for Belgrade → Budva trip in 2026: bus (fastest, 10–12h), prices from €30, recommended carriers and tips.',
        'ru': 'Полный гид по поездке Белград → Будва в 2026: автобус (быстрее всего, 10–12ч), цены от 30€, рекомендуемые перевозчики и советы.',
        'bg': 'Пълен наръчник за пътуването Белград → Будва 2026: автобус (най-бързо, 10–12ч), цени от 30€, препоръчани превозвачи и съвети.',
    },
    'guides.beograd_budva.p1': {
        'sr': 'Beograd i Budva razdvaja oko <strong>600 km</strong> — put kroz Užice, Zlatibor, Nikšić i Podgoricu. Direktnog voza nema; najpraktičniji način je <strong>autobus preko noći</strong> (10–12 sati). Letnja sezona: i dnevne linije i veći broj prevoznika. Zimi: uglavnom noćne linije.',
        'en': 'Belgrade and Budva are separated by about <strong>600 km</strong> — the route runs through Užice, Zlatibor, Nikšić and Podgorica. There is no direct train; the most practical way is an <strong>overnight bus</strong> (10–12 hours). In summer: more daytime lines and more carriers. In winter: mostly overnight lines.',
        'ru': 'Белград и Будву разделяет около <strong>600 км</strong> — путь через Ужице, Златибор, Никшич и Подгорицу. Прямого поезда нет; самый практичный вариант — <strong>ночной автобус</strong> (10–12 часов). Летом: больше дневных рейсов и перевозчиков. Зимой: в основном ночные рейсы.',
        'bg': 'Белград и Будва са разделени от около <strong>600 км</strong> — маршрут през Ужице, Златибор, Никшич и Подгорица. Директен влак няма; най-практичният начин е <strong>нощен автобус</strong> (10–12 часа). През летния сезон има и дневни линии, и повече превозвачи. През зимата — предимно нощни линии.',
    },
    'guides.beograd_budva.h2_options': {
        'sr': 'Opcije prevoza',
        'en': 'Travel options',
        'ru': 'Варианты транспорта',
        'bg': 'Варианти за превоз',
    },
    'guides.beograd_budva.p2': {
        'sr': 'Na ovoj relaciji prevoz organizuju <strong>Lasta</strong>, <strong>Kavim-Jedinstvo</strong>, <strong>OZLEM</strong> i još nekoliko regionalnih prevoznika. Prosečna vožnja traje <strong>10 sati 30 minuta</strong> sa jednom pauzom. Većina autobusa su savremeni, sa WC-om, WiFi-jem i klimom.',
        'en': 'The route is operated by <strong>Lasta</strong>, <strong>Kavim-Jedinstvo</strong>, <strong>OZLEM</strong> and several regional carriers. Average trip is <strong>10 hours 30 minutes</strong> with one break. Most buses are modern, with toilet, WiFi and A/C.',
        'ru': 'Маршрут обслуживают <strong>Lasta</strong>, <strong>Kavim-Jedinstvo</strong>, <strong>OZLEM</strong> и несколько региональных перевозчиков. Средняя поездка — <strong>10 часов 30 минут</strong> с одной остановкой. Большинство автобусов современные, с туалетом, WiFi и кондиционером.',
        'bg': 'На тази линия превоза организират <strong>Lasta</strong>, <strong>Kavim-Jedinstvo</strong>, <strong>OZLEM</strong> и още няколко регионални превозвача. Средното времетраене на пътуването е <strong>10 часа и 30 минути</strong>, с една почивка. Повечето автобуси са съвременни, с тоалетна, WiFi и климатик.',
    },
    'guides.beograd_budva.h2_price': {
        'sr': 'Cene karata',
        'en': 'Ticket prices',
        'ru': 'Цены билетов',
        'bg': 'Цени на билетите',
    },
    'guides.beograd_budva.p3': {
        'sr': 'Karte koštaju <strong>30–45€</strong> (3500–5200 RSD) zavisno od prevoznika i sezone. U julu-avgustu cene idu gore. Za najjeftinije karte: kupujte unapred i izbegavajte vikende. Povratna karta je često 5–10% jeftinija od dve u jednom smeru.',
        'en': 'Tickets cost <strong>€30–45</strong> (3500–5200 RSD) depending on carrier and season. Prices rise in July–August. For cheapest fares: book in advance and avoid weekends. Return tickets are often 5–10% cheaper than two one-ways.',
        'ru': 'Билеты стоят <strong>30–45€</strong> (3500–5200 RSD) в зависимости от перевозчика и сезона. Летом цены растут. Для самых дешёвых билетов: покупайте заранее и избегайте выходных. Обратный билет часто на 5–10% дешевле двух в одну сторону.',
        'bg': 'Билетите струват <strong>30–45€</strong> (3500–5200 RSD) в зависимост от превозвача и сезона. През юли и август цените се покачват. За най-евтини билети: купувайте предварително и избягвайте уикендите. Билетът за отиване и връщане често е с 5–10% по-евтин от два билета в една посока.',
    },
    'guides.beograd_budva.h2_when': {
        'sr': 'Kada putovati',
        'en': 'When to travel',
        'ru': 'Когда ехать',
        'bg': 'Кога да пътувате',
    },
    'guides.beograd_budva.p4': {
        'sr': 'Glavna sezona je <strong>jun-septembar</strong> — tada je najveći izbor polazaka i najviše turista. Van sezone (novembar-mart) put je jeftiniji i mirniji, ali je broj polazaka manji (obično samo noćni). Srećom, Budva radi cele godine — čak i zimi tu ima života.',
        'en': 'Peak season is <strong>June–September</strong> — most departures and most tourists. Off-season (November–March) is cheaper and quieter, but fewer departures (usually overnight only). Luckily Budva is open year-round — even in winter it has a pulse.',
        'ru': 'Пик — <strong>июнь-сентябрь</strong> — больше всего рейсов и туристов. Несезон (ноябрь-март) — дешевле и тише, но меньше рейсов (обычно только ночные). К счастью, Будва живёт круглый год — даже зимой там есть жизнь.',
        'bg': 'Основният сезон е <strong>юни–септември</strong> — тогава изборът от курсове е най-голям, а туристите — най-много. Извън сезона (ноември–март) пътуването е по-евтино и по-спокойно, но курсовете са по-малко (обикновено само нощни). За щастие Будва работи целогодишно — дори през зимата там кипи живот.',
    },
    'guides.beograd_budva.cta': {
        'sr': 'Proveri polazke Beograd → Budva',
        'en': 'Check Belgrade → Budva departures',
        'ru': 'Посмотреть рейсы Белград → Будва',
        'bg': 'Провери курсовете Белград → Будва',
    },

    # Guide 2 — cheap tickets
    'guides.cheap_tickets.title': {
        'sr': 'Najjeftinije autobus karte u Srbiji: 7 saveta 2026',
        'en': 'Cheapest bus tickets in Serbia: 7 tips for 2026',
        'ru': 'Самые дешёвые билеты на автобус в Сербии: 7 советов 2026',
        'bg': 'Най-евтините автобусни билети в Сърбия: 7 съвета за 2026',
    },
    'guides.cheap_tickets.meta': {
        'sr': 'Kako kupiti najjeftinije karte za autobus u Srbiji: kada bukirati, gde tražiti, koji prevoznici daju popuste.',
        'en': 'How to buy the cheapest bus tickets in Serbia: when to book, where to look, which carriers offer discounts.',
        'ru': 'Как купить самые дешёвые билеты на автобус в Сербии: когда бронировать, где искать, какие перевозчики дают скидки.',
        'bg': 'Как да купите най-евтините автобусни билети в Сърбия: кога да резервирате, къде да търсите, кои превозвачи предлагат отстъпки.',
    },
    'guides.cheap_tickets.p1': {
        'sr': 'Cene autobuskih karata u Srbiji variraju i do 40% zavisno od dana, prevoznika i načina kupovine. Evo kako ih spustiti na minimum.',
        'en': 'Bus ticket prices in Serbia vary by up to 40% depending on the day, carrier and purchase method. Here is how to push them to the minimum.',
        'ru': 'Цены автобусных билетов в Сербии различаются до 40% в зависимости от дня, перевозчика и способа покупки. Вот как опустить их до минимума.',
        'bg': 'Цените на автобусните билети в Сърбия варират до 40% в зависимост от деня, превозвача и начина на закупуване. Ето как да ги сведете до минимум.',
    },
    'guides.cheap_tickets.h2_when': {'sr': 'Kada kupiti', 'en': 'When to buy', 'ru': 'Когда покупать', 'bg': 'Кога да купите'},
    'guides.cheap_tickets.p2': {
        'sr': 'Autobuske karte u Srbiji nemaju tako izražen dynamic pricing kao avio, ali i dalje: <strong>utorak-četvrtak</strong> su najjeftiniji dani, vikendi i praznici 10–25% skuplji. Vožnje rano ujutru i kasno noću su obično jeftinije od popodnevnih.',
        'en': 'Serbian bus tickets don\'t have dynamic pricing like airlines, but still: <strong>Tuesday-Thursday</strong> are cheapest days, weekends and holidays 10–25% more expensive. Early morning and late-night runs are usually cheaper than afternoon ones.',
        'ru': 'Автобусные билеты в Сербии не имеют такого динамичного ценообразования как авиа, но всё же: <strong>вторник-четверг</strong> — самые дешёвые дни, выходные и праздники на 10–25% дороже. Утренние и ночные рейсы обычно дешевле дневных.',
        'bg': 'Автобусните билети в Сърбия нямат толкова изразено динамично ценообразуване като самолетните, но все пак: <strong>вторник-четвъртък</strong> са най-евтините дни, а през уикендите и празниците цените са с 10–25% по-високи. Курсовете рано сутрин и късно вечер обикновено са по-евтини от следобедните.',
    },
    'guides.cheap_tickets.h2_where': {'sr': 'Gde tražiti', 'en': 'Where to look', 'ru': 'Где искать', 'bg': 'Къде да търсите'},
    'guides.cheap_tickets.p3': {
        'sr': 'Većina prevoznika prodaje online preko partnera <strong>BusTicket4.me</strong>. Direktno na šalteru autobuske stanice ponekad je i jeftinije — posebno kod manjih lokalnih prevoznika (Niš-Ekspres, Severtrans, Autoprevoz).',
        'en': 'Most carriers sell online via partners <strong>BusTicket4.me</strong>. Buying directly at the bus-station counter is sometimes cheaper — especially with smaller local carriers (Niš-Ekspres, Severtrans, Autoprevoz).',
        'ru': 'Большинство перевозчиков продают онлайн через партнёров <strong>BusTicket4.me</strong>. Прямо на кассе автовокзала иногда дешевле — особенно у небольших местных перевозчиков (Niš-Ekspres, Severtrans, Autoprevoz).',
        'bg': 'Повечето превозвачи продават онлайн чрез партньора <strong>BusTicket4.me</strong>. Директно на гишето на автогарата понякога излиза дори по-евтино — особено при по-малките местни превозвачи (Niš-Ekspres, Severtrans, Autoprevoz).',
    },
    'guides.cheap_tickets.h2_tips': {'sr': 'Praktični saveti', 'en': 'Practical tips', 'ru': 'Практические советы', 'bg': 'Практични съвети'},
    'guides.cheap_tickets.p4': {
        'sr': 'Povratna karta obično je 5–10% jeftinija od dve odvojene. Studentske i penzionerske popuste daju Lasta, Kavim i Niš-Ekspres (do 30%). Za više ljudi: proveriti grupne cene kod prevoznika — česta ušteda 15–20%. Ne bukirati u petak popodne i nedelju uveče — to je cenovni pik nedelje.',
        'en': 'Return tickets are usually 5–10% cheaper than two one-ways. Student and senior discounts: Lasta, Kavim and Niš-Ekspres (up to 30%). For groups: check group rates with the carrier — typical savings 15–20%. Avoid booking Friday afternoon and Sunday evening — weekly price peak.',
        'ru': 'Обратные билеты обычно на 5–10% дешевле двух в одну сторону. Студенческие и пенсионерские скидки: Lasta, Kavim и Niš-Ekspres (до 30%). Для групп: проверьте групповые тарифы у перевозчика — обычно экономия 15–20%. Не бронируйте в пятницу днём и воскресенье вечером — пик цен недели.',
        'bg': 'Билетът за отиване и връщане обикновено е с 5–10% по-евтин от два отделни билета. Отстъпки за студенти и пенсионери предлагат Lasta, Kavim и Niš-Ekspres (до 30%). За по-големи групи: проверете груповите цени при превозвача — обичайно спестявате 15–20%. Избягвайте резервации в петък следобед и неделя вечер — това е ценовият пик на седмицата.',
    },
    'guides.cheap_tickets.cta': {
        'sr': 'Vidi sve rute i cene',
        'en': 'See all routes and prices',
        'ru': 'Посмотреть все маршруты и цены',
        'bg': 'Виж всички маршрути и цени',
    },

    # Guide 3 — bus vs train
    'guides.bus_vs_train.title': {
        'sr': 'Autobus ili voz u Srbiji: šta je bolje?',
        'en': 'Bus or train in Serbia: which is better?',
        'ru': 'Автобус или поезд в Сербии: что лучше?',
        'bg': 'Автобус или влак в Сърбия: кое е по-добро?',
    },
    'guides.bus_vs_train.meta': {
        'sr': 'Poređenje autobusa i voza u Srbiji: brzina, cena, komfor, pokrivenost. Kada izabrati šta.',
        'en': 'Bus vs. train comparison for Serbia: speed, price, comfort, coverage. When to pick which.',
        'ru': 'Сравнение автобуса и поезда в Сербии: скорость, цена, комфорт, покрытие. Когда что выбрать.',
        'bg': 'Сравнение между автобус и влак в Сърбия: скорост, цена, комфорт, покритие. Кога какво да изберете.',
    },
    'guides.bus_vs_train.p1': {
        'sr': 'U Srbiji autobus pokriva skoro sve relacije (275+ međugradskih), dok voz radi na oko 15 glavnih pravaca. Ipak, na nekim rutama voz je ozbiljan takmičar — jeftiniji i komforniji.',
        'en': 'In Serbia, the bus covers nearly every route (275+ intercity), while the train runs on about 15 main corridors. Still, on certain routes the train is a serious contender — cheaper and more comfortable.',
        'ru': 'В Сербии автобус покрывает почти все направления (275+ междугородних), поезд работает на ~15 основных коридорах. Тем не менее на некоторых маршрутах поезд — серьёзный конкурент: дешевле и комфортнее.',
        'bg': 'В Сърбия автобусът покрива почти всички връзки (над 275 междуградски линии), докато влакът обслужва около 15 главни направления. И все пак по някои маршрути влакът е сериозен конкурент — по-евтин и по-комфортен.',
    },
    'guides.bus_vs_train.h2_bus': {'sr': 'Kada autobus', 'en': 'When bus wins', 'ru': 'Когда автобус выигрывает', 'bg': 'Кога автобус'},
    'guides.bus_vs_train.p2': {
        'sr': 'Autobus je bolji izbor za <strong>manje gradove</strong> (Čačak, Kraljevo, Užice, Valjevo, Leskovac), <strong>putovanja u region</strong> (Crna Gora, Bosna, Hrvatska), i <strong>noćne polaske</strong> kada možete da spavate u sedištu. Prevoznika je mnogo, frekvencija velika.',
        'en': 'The bus is better for <strong>smaller cities</strong> (Čačak, Kraljevo, Užice, Valjevo, Leskovac), <strong>regional travel</strong> (Montenegro, Bosnia, Croatia), and <strong>overnight runs</strong> where you can sleep in the seat. Lots of carriers, high frequency.',
        'ru': 'Автобус лучше для <strong>небольших городов</strong> (Чачак, Кралево, Ужице, Валево, Лесковац), <strong>региональных поездок</strong> (Черногория, Босния, Хорватия) и <strong>ночных рейсов</strong> где можно поспать в кресле. Много перевозчиков, высокая частота.',
        'bg': 'Автобусът е по-добрият избор за <strong>по-малките градове</strong> (Чачак, Кралево, Ужице, Валево, Лесковац), <strong>пътувания в региона</strong> (Черна гора, Босна, Хърватия) и <strong>нощни курсове</strong>, когато можете да поспите на седалката. Превозвачите са много, а честотата е голяма.',
    },
    'guides.bus_vs_train.h2_train': {'sr': 'Kada voz', 'en': 'When train wins', 'ru': 'Когда поезд выигрывает', 'bg': 'Кога влак'},
    'guides.bus_vs_train.p3': {
        'sr': 'Voz je bolji na pravcu <strong>Beograd — Novi Sad</strong> (brza Soko linija, 37 min) i na relacijama <strong>Beograd — Subotica</strong>, <strong>Beograd — Niš</strong>. Komfor je veći (možete da ustanete i prošetate), cene često niže nego autobus, i nema zastoja u saobraćaju.',
        'en': 'The train wins on <strong>Belgrade — Novi Sad</strong> (the fast Soko line, 37 min) and on <strong>Belgrade — Subotica</strong>, <strong>Belgrade — Niš</strong>. More comfort (you can stand and walk), often cheaper than the bus, no traffic jams.',
        'ru': 'Поезд выигрывает на направлении <strong>Белград — Нови-Сад</strong> (скорая линия Soko, 37 мин) и на <strong>Белград — Суботица</strong>, <strong>Белград — Ниш</strong>. Больше комфорта (можно встать и пройтись), часто дешевле автобуса, нет пробок.',
        'bg': 'Влакът е по-добрият вариант в посока <strong>Белград — Нови Сад</strong> (бързата линия „Соко“, 37 мин.) и по маршрутите <strong>Белград — Суботица</strong>, <strong>Белград — Ниш</strong>. Комфортът е по-голям (можете да станете и да се разходите), цените често са по-ниски от тези на автобуса, а няма и задръствания.',
    },
    'guides.bus_vs_train.h2_verdict': {'sr': 'Verdikt', 'en': 'Verdict', 'ru': 'Вывод', 'bg': 'Заключение'},
    'guides.bus_vs_train.p4': {
        'sr': 'Za <strong>Novi Sad</strong>, <strong>Subotica</strong>, <strong>Niš</strong>: pokušajte voz (posebno Soko). Za sve ostalo: autobus. Kad god ima oba — uporedite cenu i vreme na ovom sajtu pre kupovine.',
        'en': 'For <strong>Novi Sad</strong>, <strong>Subotica</strong>, <strong>Niš</strong>: try the train (especially Soko). For everything else: bus. Whenever both are available — compare price and time on this site before buying.',
        'ru': 'Для <strong>Нови-Сад</strong>, <strong>Суботица</strong>, <strong>Ниш</strong>: попробуйте поезд (особенно Soko). Для всего остального: автобус. Когда оба варианта есть — сравните цену и время на этом сайте перед покупкой.',
        'bg': 'За <strong>Нови Сад</strong>, <strong>Суботица</strong>, <strong>Ниш</strong>: опитайте влака (особено „Соко“). За всичко останало: автобус. Когато има и двата варианта — сравнете цената и времето на този сайт, преди да купите билет.',
    },
    'guides.bus_vs_train.cta': {
        'sr': 'Uporedi polaske',
        'en': 'Compare departures',
        'ru': 'Сравнить рейсы',
        'bg': 'Сравни курсовете',
    },

    # ── Country hub page ──
    'country.title_prefix': {
        'sr': 'Autobus Srbija',
        'en': 'Bus Serbia',
        'ru': 'Автобус Сербия',
        'bg': 'Автобус Сърбия',
    },
    # Picked instead of country.title_prefix when a hub's routes are
    # actually dominated by a non-Serbia origin (currently: ardatur.bg's
    # Bulgaria-only routes feeding nemacka/turska/ceska/madjarska/austrija —
    # see _detect_home_country in app/routes/info.py). Without this, those
    # 5 hubs' <title>/meta falsely claimed "Bus Serbia -> Germany" etc. on
    # a page that's 100% Bulgaria-origin.
    'country.title_prefix_bg_anchor': {
        'sr': 'Autobus Bugarska',
        'en': 'Bus Bulgaria',
        'ru': 'Автобус Болгария',
        'bg': 'Автобус България',
    },
    'country.title_suffix': {
        'sr': 'raspored i cene',
        'en': 'schedule and prices',
        'ru': 'расписание и цены',
        'bg': 'разписание и цени',
    },
    'country.meta_prefix': {
        'sr': 'Red vožnje autobusa iz Srbije za',
        'en': 'Bus schedule from Serbia to',
        'ru': 'Расписание автобусов из Сербии в',
        'bg': 'Разписание на автобуси от Сърбия за',
    },
    'country.meta_prefix_bg_anchor': {
        'sr': 'Red vožnje autobusa iz Bugarske za',
        'en': 'Bus schedule from Bulgaria to',
        'ru': 'Расписание автобусов из Болгарии в',
        'bg': 'Разписание на автобуси от България за',
    },
    'country.meta_routes': {'sr': 'ruta', 'en': 'routes', 'ru': 'маршрутов', 'bg': 'маршрута'},
    'country.meta_trips': {'sr': 'polazaka', 'en': 'departures', 'ru': 'отправлений', 'bg': 'тръгвания'},
    'country.meta_cities': {'sr': 'gradova', 'en': 'cities', 'ru': 'городов', 'bg': 'града'},
    'country.meta_cta': {
        'sr': 'Uporedite cene i kupite kartu. Besplatno.',
        'en': 'Compare prices, buy tickets. Free.',
        'ru': 'Сравните цены, купите билет. Бесплатно.',
        'bg': 'Сравнете цени, купете билет. Безплатно.',
    },
    'country.h1': {
        'sr': 'Autobuske rute —',
        'en': 'Bus routes —',
        'ru': 'Автобусные маршруты —',
        'bg': 'Автобусни маршрути —',
    },
    'country.stat_routes': {'sr': 'ruta', 'en': 'routes', 'ru': 'маршрутов', 'bg': 'маршрута'},
    'country.stat_cities': {'sr': 'gradova', 'en': 'cities', 'ru': 'городов', 'bg': 'града'},
    'country.stat_trips': {'sr': 'dnevnih polazaka', 'en': 'daily departures', 'ru': 'ежедневных отправлений'},
    'country.routes_heading': {
        'sr': 'Sve rute za',
        'en': 'All routes to',
        'ru': 'Все маршруты в',
        'bg': 'Всички маршрути за',
    },
    'country.no_routes': {
        'sr': 'Trenutno nema dostupnih ruta za ovu zemlju.',
        'en': 'No routes available for this country at the moment.',
        'ru': 'В настоящее время нет доступных маршрутов в эту страну.',
        'bg': 'В момента няма налични маршрути за тази държава.',
    },
    'country.about_h': {
        'sr': 'Putovanja autobusom u {country}',
        'en': 'Bus travel to {country}',
        'ru': 'Автобусные поездки в {country}',
        'bg': 'Пътуване с автобус до {country}',
    },
    'country.about_p': {
        'sr': 'Na Prevozni.com pronaći ćete {routes} aktivnih autobuskih ruta koje povezuju Srbiju sa državom {country}, sa ukupno {trips} polazaka dnevno. Od toga {from_sr} rute polaze iz srpskih gradova, a {intra} rute su unutar same zemlje. Pokriveno je {cities} gradova.',
        'en': 'On Prevozni.com you will find {routes} active bus routes connecting Serbia with {country}, with {trips} daily departures in total. {from_sr} routes depart from Serbian cities, and {intra} routes are within the country itself. {cities} cities are covered.',
        'ru': 'На Prevozni.com вы найдёте {routes} активных автобусных маршрутов, соединяющих Сербию со страной {country}, всего {trips} ежедневных отправлений. Из них {from_sr} маршрутов отправляются из сербских городов, а {intra} маршрутов — внутри самой страны. Охвачено {cities} городов.',
        'bg': 'В Prevozni.com ще намерите {routes} активни автобусни маршрута, свързващи Сърбия с {country}, с общо {trips} тръгвания дневно. От тях {from_sr} маршрута тръгват от сръбски градове, а {intra} маршрута са в рамките на самата държава. Обхванати са {cities} града.',
    },
    'country.cities_p': {
        'sr': 'Gradovi u {country} koji su pokriveni: {cities}. Kliknite na rutu da vidite konkretne polaske, cene karata i kupovinu kod partnera.',
        'en': 'Cities in {country} covered: {cities}. Click a route to see departures, ticket prices and partner purchase links.',
        'ru': 'Города в {country}, охваченные сервисом: {cities}. Нажмите на маршрут чтобы увидеть отправления, цены билетов и покупку у партнёра.',
        'bg': 'Градове в {country}, които са обхванати: {cities}. Кликнете върху маршрут, за да видите конкретните тръгвания, цените на билетите и покупка при партньор.',
    },
    'country.carriers_h': {
        'sr': 'Prevoznici za {country}',
        'en': 'Carriers to {country}',
        'ru': 'Перевозчики в {country}',
        'bg': 'Превозвачи за {country}',
    },
    'country.subtitle': {
        'sr': 'Međugradske autobuske rute, cene i raspored',
        'en': 'Intercity bus routes, prices and schedules',
        'ru': 'Междугородние автобусные маршруты, цены и расписание',
        'bg': 'Междуградски автобусни маршрути, цени и разписание',
    },
    'country.stat_avg_distance': {
        'sr': 'prosečna razdaljina',
        'en': 'average distance',
        'ru': 'средняя дистанция',
        'bg': 'средно разстояние',
    },
    'country.stat_avg_price': {
        'sr': 'prosečna cena',
        'en': 'average price',
        'ru': 'средняя цена',
        'bg': 'средна цена',
    },
    'country.prose_travel_time': {
        'sr': 'Prosečna razdaljina rute do države {country} iznosi oko {km} km, što odgovara putovanju od približno {hours} sati standardnim autobusom.',
        'en': 'The average route distance to {country} is around {km} km, roughly {hours} hours by standard bus.',
        'ru': 'Средняя дистанция маршрута до страны {country} — около {km} км, что соответствует поездке примерно за {hours} часов на стандартном автобусе.',
        'bg': 'Средното разстояние на маршрута до {country} е около {km} км, което съответства на пътуване от приблизително {hours} часа със стандартен автобус.',
    },
    'country.prose_avg_price': {
        'sr': 'Prosečna najpovoljnija cena karte za pravac {country} kreće se oko {price} dinara.',
        'en': 'The average lowest ticket price for {country} is around {price} RSD.',
        'ru': 'Средняя минимальная цена билета в направлении {country} — около {price} динаров.',
        'bg': 'Средната най-изгодна цена на билет за {country} е около {price} динара.',
    },
    'country.prose_buy': {
        'sr': 'Sve cene su informativne i ažurirane prema podacima naših partnera. Karte za rute do države {country} kupuju se kod naših booking partnera; mi ne naplaćujemo dodatne provizije.',
        'en': 'All prices are indicative and updated from partner data. Tickets to {country} are purchased through our booking partners; we charge no extra fees.',
        'ru': 'Все цены ориентировочны и обновляются по данным наших партнёров. Билеты в страну {country} покупаются у наших партнёров; мы не берём дополнительной комиссии.',
        'bg': 'Всички цени са информативни и се актуализират според данните на нашите партньори. Билетите за маршрутите до {country} се купуват от нашите партньори за резервации; ние не начисляваме допълнителни такси.',
    },
    'country.filter_popular': {
        'sr': 'Najpopularnije',
        'en': 'Most popular',
        'ru': 'Самые популярные',
        'bg': 'Най-популярни',
    },
    'country.filter_cheap': {
        'sr': 'Najjeftinije',
        'en': 'Cheapest',
        'ru': 'Самые дешёвые',
        'bg': 'Най-евтини',
    },
    'country.filter_short': {
        'sr': 'Najkraće',
        'en': 'Shortest',
        'ru': 'Самые короткие',
        'bg': 'Най-кратки',
    },
    'country.reviews_heading': {
        'sr': 'Recenzije putnika za rute do države {country}',
        'en': 'Traveller reviews for routes to {country}',
        'ru': 'Отзывы пассажиров о маршрутах в страну {country}',
    },
    'country.from_belgrade_h': {
        'sr': 'Iz Beograda',
        'en': 'From Belgrade',
        'ru': 'Из Белграда',
        'bg': 'От Белград',
    },

    'operator.cities_p': {
        'sr': 'Najčešće tačke u mreži prevoznika {name}: {cities}. Kliknite na rutu da vidite konkretne polaske, cene i karte za kupovinu.',
        'en': 'Most frequent endpoints in {name}\'s network: {cities}. Click a route to see departures, prices and ticket purchase links.',
        'ru': 'Наиболее частые точки в сети {name}: {cities}. Нажмите на маршрут чтобы увидеть конкретные отправления, цены и ссылки на покупку.',
    },
    'operator.prose_serves': {
        'sr': '{name} servisira {n} međugradskih ruta sa polascima iz gradova {cities}.',
        'en': '{name} runs {n} intercity routes with departures from {cities}.',
        'ru': '{name} обслуживает {n} междугородних маршрутов с отправлениями из городов {cities}.',
    },
    'operator.prose_serves_no_cities': {
        'sr': '{name} servisira {n} međugradskih ruta.',
        'en': '{name} runs {n} intercity routes.',
        'ru': '{name} обслуживает {n} междугородних маршрутов.',
    },
    'operator.prose_price_range': {
        'sr': 'Cene karata kreću se od {min} do {max} dinara, u zavisnosti od relacije i datuma polaska.',
        'en': 'Ticket prices range from {min} to {max} RSD depending on the route and travel date.',
        'ru': 'Цены билетов варьируются от {min} до {max} динаров в зависимости от маршрута и даты выезда.',
    },
    'operator.prose_price_avg': {
        'sr': 'Prosečna cena karte iznosi oko {avg} dinara po polasku.',
        'en': 'The average ticket price is around {avg} RSD per departure.',
        'ru': 'Средняя цена билета — около {avg} динаров за поездку.',
    },
    'operator.prose_top_destinations': {
        'sr': 'Najčešća odredišta: {cities}.',
        'en': 'Most frequent destinations: {cities}.',
        'ru': 'Самые частые направления: {cities}.',
    },
    'operator.prose_countries': {
        'sr': 'Prevoznik takođe povezuje Srbiju sa državama: {countries}.',
        'en': 'The carrier also connects Serbia with: {countries}.',
        'ru': 'Перевозчик также связывает Сербию со странами: {countries}.',
    },
    'operator.prose_buy': {
        'sr': 'Na Prevozni.com možete porediti cene i raspored polazaka prevoznika {name} pre kupovine. Karte se kupuju kod naših partnera; mi ne naplaćujemo dodatne provizije i ne prodajemo karte direktno.',
        'en': 'On Prevozni.com you can compare {name} prices and timetables before buying. Tickets are purchased through our partners — we charge no extra fees and do not sell tickets directly.',
        'ru': 'На Prevozni.com можно сравнить цены и расписание перевозчика {name} перед покупкой. Билеты приобретаются у наших партнёров — мы не берём дополнительных комиссий и не продаём билеты напрямую.',
    },
    'operator.competitors_h': {
        'sr': 'Iste pravce kod drugih prevoznika',
        'en': 'Same corridors with other carriers',
        'ru': 'Те же направления у других перевозчиков',
    },
    'operator.reviews_heading': {
        'sr': 'Recenzije putnika za prevoznika {name}',
        'en': 'Traveller reviews for {name}',
        'ru': 'Отзывы пассажиров о перевозчике {name}',
    },

    # ── Buy ticket ──
    'buy.title': {
        'sr': 'Kupite kartu online',
        'en': 'Buy ticket online',
        'ru': 'Купить билет онлайн',
        'bg': 'Купете билет онлайн',
    },
    'buy.note': {
        'sr': 'Kupovina se obavlja na sajtovima partnera. Prevozni ne prodaje karte.',
        'en': 'Purchase is made on partner websites. Prevozni does not sell tickets.',
        'ru': 'Покупка на сайтах партнёров. Prevozni не продаёт билеты.',
        'bg': 'Покупката се извършва на сайтовете на партньорите. Prevozni не продава билети.',
    },
    'buy.book_ahead': {
        'sr': 'Samo {n} polazaka dnevno na ovoj relaciji — preporučujemo kupovinu unapred.',
        'en': 'Only {n} departures a day on this route — advance booking recommended.',
        'ru': 'Всего {n} рейс(ов) в день на этом направлении — рекомендуем покупать заранее.',
        'bg': 'Само {n} тръгвания дневно по това направление — препоръчваме предварителна покупка.',
    },
    'buy.cta': {
        'sr': 'Kupi',
        'en': 'Buy',
        'ru': 'Купить',
        'bg': 'Купи',
    },
    'buy.via_partner': {
        'sr': 'Kupi preko',
        'en': 'Buy via',
        'ru': 'Купить через',
        'bg': 'Купи през',
    },
    # ── Far-destination AI itinerary (search fallback to Bookaway) ──
    'ai_route.badge': {
        'sr': 'AI maršruta',
        'en': 'AI route',
        'ru': 'AI-маршрут',
    },
    'ai_route.heading': {
        'sr': 'Kako stići do',
        'en': 'How to get to',
        'ru': 'Как добраться до',
    },
    'ai_route.sub': {
        'sr': 'Nemamo direktnu liniju, ali evo predloga puta korak po korak — kartu za lokalni deo puta rezervišite kod partnera.',
        'en': 'We have no direct line, but here is a step-by-step plan — book the local leg with our partner.',
        'ru': 'Прямого рейса нет, но вот план поездки по шагам — билет на местный участок бронируйте у партнёра.',
    },
    'ai_route.loading': {
        'sr': 'Sastavljamo maršrutu…',
        'en': 'Composing the route…',
        'ru': 'Составляем маршрут…',
    },
    'ai_route.cta': {
        'sr': 'Rezerviši preko Bookaway',
        'en': 'Book via Bookaway',
        'ru': 'Забронировать через Bookaway',
    },
    'ai_route.disclaimer': {
        'sr': 'Orijentacioni plan koji generiše AI — vremena, cene i veze obavezno proverite kod prevoznika pre kupovine.',
        'en': 'AI-generated estimate — always verify times, prices and connections with the carrier before buying.',
        'ru': 'Ориентировочный план от AI — время, цены и стыковки обязательно проверяйте у перевозчика перед покупкой.',
    },
    'ai_route.error': {
        'sr': 'Trenutno ne možemo da sastavimo maršrutu. Pokušajte kasnije ili rezervišite direktno kod partnera.',
        'en': 'We could not compose a route right now. Try again later or book directly with the partner.',
        'ru': 'Сейчас не получилось составить маршрут. Попробуйте позже или забронируйте напрямую у партнёра.',
    },
    # Trust chips next to the Bookaway far-CTA — concrete reassurances that
    # nudge the click (Bookaway is a real booking platform: SSL checkout,
    # instant e-ticket, multilingual support).
    'ai_route.trust_secure': {
        'sr': 'Sigurna rezervacija', 'en': 'Secure booking', 'ru': 'Безопасное бронирование',
    },
    'ai_route.trust_instant': {
        'sr': 'Trenutna potvrda', 'en': 'Instant confirmation', 'ru': 'Мгновенное подтверждение',
    },
    'ai_route.trust_support': {
        'sr': 'Podrška 24/7', 'en': '24/7 support', 'ru': 'Поддержка 24/7',
    },
    'ai_route.mode_bus': {'sr': 'Autobus', 'en': 'Bus', 'ru': 'Автобус'},
    'ai_route.mode_train': {'sr': 'Voz', 'en': 'Train', 'ru': 'Поезд'},
    'ai_route.mode_flight': {'sr': 'Let', 'en': 'Flight', 'ru': 'Перелёт'},
    'ai_route.mode_ferry': {'sr': 'Trajekt', 'en': 'Ferry', 'ru': 'Паром'},
    'ai_route.mode_taxi': {'sr': 'Taksi', 'en': 'Taxi', 'ru': 'Такси'},
    'ai_route.mode_metro': {'sr': 'Metro', 'en': 'Metro', 'ru': 'Метро'},
    # Neutral "{from} → {to}: …?" shape — gluing "Kako stići" + city names
    # produced ungrammatical sr (no preposition/case: "Kako stići Beograd →
    # Bangkok?"); the colon form needs no declension in any language.
    'ai_route.faq.q_how': {
        'sr': '{from_city} → {to_city}: kako stići?',
        'en': '{from_city} → {to_city}: how to get there?',
        'ru': '{from_city} → {to_city}: как добраться?',
    },
    'ai_route.faq.q_time': {
        'sr': 'Koliko traje put?',
        'en': 'How long does the trip take?',
        'ru': 'Сколько занимает дорога?',
    },
    'ai_route.faq.q_cost': {
        'sr': 'Koliko košta put?',
        'en': 'How much does the trip cost?',
        'ru': 'Сколько стоит дорога?',
    },
    'ai_route.faq.a_varies': {
        'sr': 'Zavisi od datuma i prevoznika — proverite kod partnera.',
        'en': 'Depends on the date and carrier — check with the partner.',
        'ru': 'Зависит от даты и перевозчика — проверьте у партнёра.',
    },
    'buy.partners_heading': {
        'sr': 'Kupi kartu kod naših partnera',
        'en': 'Buy your ticket from our partners',
        'ru': 'Купить билет у наших партнёров',
        'bg': 'Купи билет от нашите партньори',
    },
    'buy.partners_note': {
        'sr': 'Cene su iste — mi dobijemo malu proviziju ako kupite preko ovih linkova.',
        'en': 'Prices are the same — we receive a small commission if you book via these links.',
        'ru': 'Цены одинаковые — мы получаем небольшую комиссию при бронировании по этим ссылкам.',
        'bg': 'Цените са същите — ние получаваме малка комисиона, ако купите през тези връзки.',
    },

    # ── Day labels ──
    'day.today': {'sr': 'Danas', 'en': 'Today', 'ru': 'Сегодня', 'bg': 'Днес'},
    'day.tomorrow': {'sr': 'Sutra', 'en': 'Tomorrow', 'ru': 'Завтра', 'bg': 'Утре'},
    'route.departures_left': {'sr': 'Još danas', 'en': 'Left today', 'ru': 'Ещё сегодня', 'bg': 'Още днес'},
    'route.departs_in': {'sr': 'Polazi za', 'en': 'Departs in', 'ru': 'Отправляется через', 'bg': 'Тръгва след'},
    'day.day_after': {'sr': 'Prekosutra', 'en': 'Day after', 'ru': 'Послезавтра', 'bg': 'Вдругиден'},

    'route.similar': {'sr': 'Slične rute iz', 'en': 'Similar routes from', 'ru': 'Похожие маршруты из', 'bg': 'Подобни маршрути от'},
    'route.other_from': {'sr': 'Drugi pravci iz', 'en': 'Other routes from', 'ru': 'Другие направления из', 'bg': 'Други направления от'},
    'route.city_transport_heading': {
        'sr': 'Gradski prevoz',
        'en': 'City transport',
        'ru': 'Городской транспорт',
        'bg': 'Градски транспорт',
    },
    'route.city_transport_link': {
        'sr': '{city}: linije i stajališta',
        'en': '{city}: lines and stops',
        'ru': '{city}: линии и остановки',
        'bg': '{city}: линии и спирки',
    },
    'route.carriers_on_route': {
        'sr': 'Prevoznici na ovoj ruti',
        'en': 'Carriers on this route',
        'ru': 'Перевозчики на этом маршруте',
        'bg': 'Превозвачи на този маршрут',
    },
    'route.about': {'sr': 'O ruti', 'en': 'About route', 'ru': 'О маршруте', 'bg': 'За маршрута'},

    # ── Destinations page ──
    'dest.title': {
        'sr': 'Top destinacije na Balkanu',
        'en': 'Top Balkan destinations',
        'ru': 'Лучшие направления на Балканах',
        'bg': 'Топ дестинации на Балканите',
    },
    'dest.subtitle': {
        'sr': 'Najpopularnija mesta za putovanje autobusom i vozom',
        'en': 'Most popular places to travel by bus and train',
        'ru': 'Самые популярные места для поездок на автобусе и поезде',
    },
    'dest.stat_countries': {
        'sr': 'zemalja u mreži',
        'en': 'countries in network',
        'ru': 'стран в сети',
    },
    'dest.stat_routes': {
        'sr': 'aktivnih ruta',
        'en': 'active routes',
        'ru': 'активных маршрутов',
    },
    'dest.stat_cities': {
        'sr': 'gradova',
        'en': 'cities',
        'ru': 'городов',
    },
    'dest.filter_all': {
        'sr': 'Sve',
        'en': 'All',
        'ru': 'Все',
    },
    'dest.filter_balkan': {
        'sr': 'Balkan',
        'en': 'Balkans',
        'ru': 'Балканы',
    },
    'dest.filter_eu': {
        'sr': 'EU',
        'en': 'EU',
        'ru': 'ЕС',
    },
    'dest.filter_beyond': {
        'sr': 'Dalje',
        'en': 'Beyond',
        'ru': 'Далее',
    },
    'carriers.stat_cross_border': {
        'sr': 'međunarodnih prevoznika',
        'en': 'cross-border carriers',
        'ru': 'международных перевозчиков',
    },
    'carriers.filter_domestic': {
        'sr': 'Domaći',
        'en': 'Domestic',
        'ru': 'Внутренние',
    },
    'carriers.filter_cross_border': {
        'sr': 'Međunarodni',
        'en': 'Cross-border',
        'ru': 'Международные',
    },
    'dest.meta': {
        'sr': 'Top destinacije na Balkanu — Srbija, Crna Gora, Bosna, Hrvatska, Mađarska. Autobuske i vozne veze. Prevozni.com',
        'en': 'Top Balkan destinations — Serbia, Montenegro, Bosnia, Croatia, Hungary. Bus and train connections. Prevozni.com',
        'ru': 'Лучшие направления на Балканах — Сербия, Черногория, Босния, Хорватия, Венгрия. Автобусное и ж/д сообщение.',
    },
    'dest.serbia': {'sr': 'Srbija', 'en': 'Serbia', 'ru': 'Сербия'},
    'dest.montenegro': {'sr': 'Crna Gora', 'en': 'Montenegro', 'ru': 'Черногория'},
    'dest.bosnia': {'sr': 'Bosna i Hercegovina', 'en': 'Bosnia & Herzegovina', 'ru': 'Босния и Герцеговина'},
    'dest.croatia': {'sr': 'Hrvatska', 'en': 'Croatia', 'ru': 'Хорватия'},
    'dest.hungary': {'sr': 'Mađarska', 'en': 'Hungary', 'ru': 'Венгрия'},
    'dest.greece': {'sr': 'Grčka', 'en': 'Greece', 'ru': 'Греция'},
    'dest.north_macedonia': {'sr': 'Severna Makedonija', 'en': 'North Macedonia', 'ru': 'Северная Македония'},
    'dest.austria': {'sr': 'Austrija', 'en': 'Austria', 'ru': 'Австрия'},
    'dest.beograd': {
        'sr': 'Glavni grad Srbije. Kalemegdan, Knez Mihailova, Skadarlija, noćni život i bogata istorija.',
        'en': 'Capital of Serbia. Kalemegdan fortress, Knez Mihailova street, Skadarlija, vibrant nightlife.',
        'ru': 'Столица Сербии. Крепость Калемегдан, улица Кнез Михайлова, Скадарлия, ночная жизнь.',
    },
    'dest.budva': {
        'sr': 'Biser crnogorskog primorja. Stari grad, plaže Mogren i Slovenska, žurke do zore.',
        'en': 'Pearl of the Montenegrin coast. Old town, Mogren beach, Slovenska beach, parties till dawn.',
        'ru': 'Жемчужина черногорского побережья. Старый город, пляжи Могрен и Словенска.',
    },
    'dest.herceg_novi': {
        'sr': 'Grad na ulazu u Boku Kotorsku. Tvrđave, botanički vrtovi, kristalno čisto more.',
        'en': 'City at the entrance to Bay of Kotor. Fortresses, botanical gardens, crystal clear sea.',
        'ru': 'Город у входа в Которский залив. Крепости, ботанические сады, кристально чистое море.',
    },
    'dest.kotor': {
        'sr': 'UNESCO grad u srcu Boke. Srednjovekovni zidovi, katedrale i pogled sa tvrđave Sv. Jovana.',
        'en': 'UNESCO city in the heart of Boka. Medieval walls, cathedrals and views from St. John fortress.',
        'ru': 'Город ЮНЕСКО в сердце Боки. Средневековые стены, соборы и вид с крепости Св. Иоанна.',
    },
    'dest.novi_sad': {
        'sr': 'Drugi grad Srbije. Petrovaradinska tvrđava, EXIT festival, Fruška gora, Dunav.',
        'en': 'Second city of Serbia. Petrovaradin fortress, EXIT festival, Fruška Gora, Danube.',
        'ru': 'Второй город Сербии. Петроварадинская крепость, фестиваль EXIT, Фрушка Гора, Дунай.',
    },
    'dest.nis': {
        'sr': 'Treći grad Srbije. Niška tvrđava, Ćele-kula, Medijana, Nišava i Niška Banja.',
        'en': 'Third city of Serbia. Niš fortress, Skull Tower, Mediana, Nišava river and Niška Banja spa.',
        'ru': 'Третий город Сербии. Нишская крепость, Челе-Кула, Медиана, река Нишава и курорт Нишка Баня.',
    },
    'dest.sarajevo': {
        'sr': 'Glavni grad BiH. Baščaršija, Latinska ćuprija, Tunnel of Hope, mešavina kultura.',
        'en': 'Capital of Bosnia. Baščaršija bazaar, Latin Bridge, Tunnel of Hope, cultural melting pot.',
        'ru': 'Столица Боснии. Базар Башчаршия, Латинский мост, Тоннель надежды, смешение культур.',
    },
    'dest.dubrovnik': {
        'sr': 'Biser Jadrana. Gradske zidine, Stari grad, Game of Thrones lokacije.',
        'en': 'Pearl of the Adriatic. City walls, Old Town, Game of Thrones filming locations.',
        'ru': 'Жемчужина Адриатики. Городские стены, Старый город, локации «Игры престолов».',
    },
    'dest.split': {
        'sr': 'Dioklecijanova palata, plaže Bačvice, brodske linije za ostrva Jadrana.',
        'en': "Diocletian's Palace, Bačvice beach, ferry connections to Adriatic islands.",
        'ru': 'Дворец Диоклетиана, пляж Бачвице, паромы на острова Адриатики.',
    },
    'dest.budapest': {
        'sr': 'Glavni grad Mađarske. Termalni bazeni, Budimski zamak, Parlament, Dunav noću.',
        'en': 'Capital of Hungary. Thermal baths, Buda Castle, Parliament, Danube by night.',
        'ru': 'Столица Венгрии. Термальные купальни, Будайская крепость, Парламент, Дунай ночью.',
    },
    'dest.thessaloniki': {
        'sr': 'Drugi grad Grčke. Bela kula, rimski forum, fantastična hrana i živahna obala.',
        'en': 'Second city of Greece. White Tower, Roman forum, amazing food and vibrant waterfront.',
        'ru': 'Второй город Греции. Белая башня, римский форум, потрясающая еда и набережная.',
    },
    'dest.skopje': {
        'sr': 'Glavni grad S. Makedonije. Stari bazar, Kameni most, Kale tvrđava, Matka kanjon.',
        'en': 'Capital of North Macedonia. Old Bazaar, Stone Bridge, Kale Fortress, Matka Canyon.',
        'ru': 'Столица С. Македонии. Старый базар, Каменный мост, крепость Кале, каньон Матка.',
    },
    'dest.vienna': {
        'sr': 'Austrijski glavni grad. Šenbrunn, Ringštrasse, Prater, kafane i klasična muzika.',
        'en': 'Austrian capital. Schönbrunn, Ringstraße, Prater, coffee houses and classical music.',
        'ru': 'Столица Австрии. Шёнбрунн, Рингштрассе, Пратер, кофейни и классическая музика.',
    },

    'nav.destinations': {'sr': 'Destinacije', 'en': 'Destinations', 'ru': 'Направления', 'bg': 'Дестинации'},

    'dest.turkey': {'sr': 'Turska', 'en': 'Turkey', 'ru': 'Турция'},
    'dest.istanbul': {
        'sr': 'Najveći grad Turske. Aja Sofija, Plava džamija, Grand bazar, Bosfor i dva kontinenta.',
        'en': 'Largest city in Turkey. Hagia Sophia, Blue Mosque, Grand Bazaar, Bosphorus and two continents.',
        'ru': 'Крупнейший город Турции. Айя-София, Голубая мечеть, Гранд-базар, Босфор и два континента.',
    },

    # ── Language names ──
    'lang.sr': {'sr': 'Srpski', 'en': 'Serbian', 'ru': 'Сербский'},
    'lang.en': {'sr': 'English', 'en': 'English', 'ru': 'English'},
    'lang.ru': {'sr': 'Русский', 'en': 'Russian', 'ru': 'Русский'},

    # ── Accessibility labels ──
    'a11y.skip_to_content': {
        'sr': 'Preskoči na sadržaj',
        'en': 'Skip to content',
        'ru': 'Перейти к содержимому',
        'bg': 'Прескочи към съдържанието',
    },
    'a11y.language_switcher': {
        'sr': 'Izbor jezika',
        'en': 'Language selector',
        'ru': 'Выбор языка',
        'bg': 'Избор на език',
    },
    'a11y.currency_switcher': {
        'sr': 'Izbor valute',
        'en': 'Currency selector',
        'ru': 'Выбор валюты',
        'bg': 'Избор на валута',
    },
    'a11y.search_form': {
        'sr': 'Pretraga polazaka',
        'en': 'Journey search',
        'ru': 'Поиск поездок',
        'bg': 'Търсене на тръгвания',
    },
    'a11y.swap_cities': {
        'sr': 'Zameni polazište i odredište',
        'en': 'Swap origin and destination',
        'ru': 'Поменять местами пункты',
        'bg': 'Размени начална и крайна точка',
    },
    'a11y.chat_toggle': {
        'sr': 'Otvori AI pomoćnika',
        'en': 'Open AI assistant',
        'ru': 'Открыть AI-помощника',
        'bg': 'Отвори AI асистент',
    },
    'a11y.share': {
        'sr': 'Podeli',
        'en': 'Share',
        'ru': 'Поделиться',
        'bg': 'Сподели',
    },
    'a11y.trip_date': {
        'sr': 'Datum putovanja',
        'en': 'Trip date',
        'ru': 'Дата поездки',
        'bg': 'Дата на пътуване',
    },
    # Visible field labels on the journey-search capsule. These were
    # hard-coded 'OD' / 'DO' in the macro and never reached the EN/RU
    # locales at all. Rendered small-caps by CSS, so store natural case.
    'form.label_from': {
        'sr': 'Polazak',
        'en': 'From',
        'ru': 'Откуда',
        'bg': 'От',
    },
    'form.label_to': {
        'sr': 'Odredište',
        'en': 'To',
        'ru': 'Куда',
        'bg': 'До',
    },
    # Example cities, not a restatement of the label. The placeholders used to
    # echo it — label "From" over placeholder "From?" — which reads as a
    # stutter and tells the user nothing about what to type.
    'form.placeholder_from': {
        'sr': 'npr. Beograd',
        'en': 'e.g. Belgrade',
        'ru': 'напр. Белград',
        'bg': 'напр. Белград',
    },
    'form.placeholder_to': {
        'sr': 'npr. Novi Sad',
        'en': 'e.g. Novi Sad',
        'ru': 'напр. Нови-Сад',
        'bg': 'напр. Нови Сад',
    },
    'form.label_date': {
        'sr': 'Datum',
        'en': 'Date',
        'ru': 'Дата',
        'bg': 'Дата',
    },
    'a11y.filters': {
        'sr': 'Filteri polazaka',
        'en': 'Journey filters',
        'ru': 'Фильтры поездок',
        'bg': 'Филтри на тръгванията',
    },
    'a11y.city_map': {
        'sr': 'Interaktivna mapa gradskih stajališta',
        'en': 'Interactive city stops map',
        'ru': 'Интерактивная карта городских остановок',
        'bg': 'Интерактивна карта на градските спирки',
    },
    'a11y.line_map': {
        'sr': 'Interaktivna mapa linije',
        'en': 'Interactive line map',
        'ru': 'Интерактивная карта линии',
        'bg': 'Интерактивна карта на линията',
    },
    'a11y.stop_map': {
        'sr': 'Mapa lokacije stajališta',
        'en': 'Stop location map',
        'ru': 'Карта местоположения остановки',
        'bg': 'Карта на местоположението на спирката',
    },
    'a11y.breadcrumb': {
        'sr': 'Putanja',
        'en': 'Breadcrumb',
        'ru': 'Хлебные крошки',
        'bg': 'Навигационна пътека',
    },
    'a11y.pagination': {
        'sr': 'Paginacija',
        'en': 'Pagination',
        'ru': 'Пагинация',
        'bg': 'Странициране',
    },

    # ── Default meta (base.html) ──
    'meta.default_title': {
        'sr': 'Prevozni — red vožnje u Srbiji',
        'en': 'Prevozni — transport schedules in Serbia',
        'ru': 'Prevozni — расписание транспорта в Сербии',
        'bg': 'Prevozni — разписания в Сърбия',
    },
    'meta.default_description': {
        'sr': 'Red vožnje autobusa, vozova i gradskog prevoza u Srbiji. Pronađite polazak, uporedite cene i prevoznike. Besplatno, bez registracije.',
        'en': 'Bus, train and city transport schedules in Serbia. Find departures, compare prices and carriers. Free, no registration.',
        'ru': 'Расписание автобусов, поездов и городского транспорта в Сербии. Ищите отправления, сравнивайте цены и перевозчиков. Бесплатно, без регистрации.',
        'bg': 'Разписания на автобуси, влакове и градски транспорт в Сърбия. Намерете тръгване, сравнете цени и превозвачи. Безплатно, без регистрация.',
    },
    'meta.og_image_alt': {
        'sr': 'Prevozni — red vožnje Srbija',
        'en': 'Prevozni — Serbia transport schedules',
        'ru': 'Prevozni — расписание транспорта Сербии',
        'bg': 'Prevozni — разписания Сърбия',
    },
    'meta.city_not_found': {
        'sr': 'Grad nije pronađen',
        'en': 'City not found',
        'ru': 'Город не найден',
        'bg': 'Градът не е намерен',
    },

    # ── Error pages ──
    'error.404_title': {
        'sr': '404 — Stranica nije pronađena',
        'en': '404 — Page not found',
        'ru': '404 — Страница не найдена',
    },

    # ── route_index.html ──
    'route_index.title': {
        'sr': 'Autobuske Linije Srbija — Red Vožnje i Cene',
        'en': 'Serbia Bus Routes — Schedules & Prices',
        'ru': 'Автобусные Маршруты Сербии — Расписание и Цены',
    },
    'route_index.meta': {
        'sr': 'autobuskih ruta u Srbiji 2026. Red vožnje, cene i prevoznici — Beograd, Novi Sad, Niš i dalje. Pronađi polazak →',
        'en': 'bus routes in Serbia 2026. Schedules, prices and carriers — Belgrade, Novi Sad, Niš and beyond. Find for free →',
        'ru': 'автобусных маршрутов в Сербии 2026. Расписание, цены и перевозчики — Белград, Нови-Сад, Ниш. Найди бесплатно →',
    },
    'route_index.h1': {
        'sr': 'Međugradske rute',
        'en': 'Intercity routes',
        'ru': 'Междугородние маршруты',
    },
    'route_index.subtitle': {
        'sr': 'ruta · autobus i voz',
        'en': 'routes · bus and train',
        'ru': 'маршрутов · автобус и поезд',
    },
    'route_index.subtitle_short': {
        'sr': 'pretraži ili izaberi sa liste',
        'en': 'search or pick from the list',
        'ru': 'найди или выбери из списка',
    },
    'route_index.filter_placeholder': {
        'sr': 'Pretraži po gradu...',
        'en': 'Filter by city...',
        'ru': 'Поиск по городу...',
    },
    'route_index.results_suffix': {
        'sr': 'rezultata',
        'en': 'results',
        'ru': 'результатов',
    },
    'route_index.show_more': {
        'sr': 'Prikaži još',
        'en': 'Show more',
        'ru': 'Показать ещё',
        'bg': 'Покажи още',
    },
    'route_index.show_more_suffix': {
        'sr': 'ruta',
        'en': 'routes',
        'ru': 'маршрутов',
        'bg': 'маршрута',
    },
    'route_index.no_results': {
        'sr': 'Nema rezultata za ovaj upit',
        'en': 'No results for this query',
        'ru': 'Нет результатов по запросу',
    },
    'route_index.no_routes': {
        'sr': 'Nema dostupnih ruta',
        'en': 'No routes available',
        'ru': 'Нет доступных маршрутов',
    },
    'route_index.data_updating': {
        'sr': 'Podaci se ažuriraju',
        'en': 'Data is being updated',
        'ru': 'Данные обновляются',
    },
    'route_index.from_price': {
        'sr': 'od',
        'en': 'from',
        'ru': 'от',
    },
    'breadcrumb.all_routes': {
        'sr': 'Sve rute',
        'en': 'All routes',
        'ru': 'Все маршруты',
        'bg': 'Всички маршрути',
    },

    # ── carriers_index.html ──
    'carriers.title': {
        'sr': 'Autobuski Prevoznici Srbije — Spisak i Kontakti',
        'en': 'Bus Carriers Serbia — List & Contacts',
        'ru': 'Перевозчики Сербии — Список и Контакты',
    },
    'carriers.meta': {
        'sr': 'Autobuski i železnički prevoznici u Srbiji 2026: Lasta, Niš-Ekspres, Srbija Voz i drugi.',
        'en': 'Bus and train carriers in Serbia 2026: Lasta, Niš-Ekspres, Srbija Voz and others.',
        'ru': 'Автобусные и железнодорожные перевозчики Сербии 2026: Lasta, Niš-Ekspres, Srbija Voz и другие.',
    },
    'carriers.h1': {
        'sr': 'Prevoznici',
        'en': 'Carriers',
        'ru': 'Перевозчики',
        'bg': 'Превозвачи',
    },
    'carriers.website': {
        'sr': 'Sajt',
        'en': 'Website',
        'ru': 'Сайт',
    },
    'carriers.cities_label': {
        'sr': 'Gradovi:',
        'en': 'Cities:',
        'ru': 'Города:',
    },
    'carriers.no_routes': {
        'sr': 'Nema ruta u bazi za ovog prevoznika.',
        'en': 'No routes in the database for this carrier.',
        'ru': 'Нет маршрутов в базе для этого перевозчика.',
    },
    'carriers.next_page': {
        'sr': 'Sledeća →',
        'en': 'Next →',
        'ru': 'Следующая →',
    },
    'carriers.count_suffix': {
        'sr': 'prevoznika',
        'en': 'carriers',
        'ru': 'перевозчиков',
    },
    'carriers.in_base_suffix': {
        'sr': 'prevoznika u bazi',
        'en': 'carriers in database',
        'ru': 'перевозчиков в базе',
    },
    'carriers.page_of': {
        'sr': 'strana',
        'en': 'page',
        'ru': 'страница',
    },
    'carriers.routes_count': {
        'sr': 'ruta',
        'en': 'routes',
        'ru': 'маршрутов',
    },
    'carriers.empty_loading': {
        'sr': 'Podaci se učitavaju',
        'en': 'Data is loading',
        'ru': 'Данные загружаются',
    },
    'carriers.prev_page': {
        'sr': '← Prethodna',
        'en': '← Previous',
        'ru': '← Предыдущая',
    },
    'carriers.page_info': {
        'sr': 'Strana',
        'en': 'Page',
        'ru': 'Страница',
    },

    # ── stations_index.html ──
    'stations.title': {
        'sr': 'Autobuske Stanice Srbije — Raspored i Info',
        'en': 'Serbia Bus Stations — Schedules & Info',
        'ru': 'Автобусные Станции Сербии — Расписание и Инфо',
    },
    'stations.meta': {
        'sr': 'Autobuske i železničke stanice u Srbiji.',
        'en': 'Bus and railway stations in Serbia.',
        'ru': 'Автобусные и железнодорожные станции в Сербии.',
    },
    'stations.h1': {
        'sr': 'Autobuske i železničke stanice',
        'en': 'Bus and railway stations',
        'ru': 'Автобусные и железнодорожные станции',
    },
    'stations.count_suffix': {
        'sr': 'stanica',
        'en': 'stations',
        'ru': 'станций',
    },
    'stations.meta_extra': {
        'sr': 'Adrese, red vožnje i polasci. Proveri pre puta →',
        'en': 'Addresses, schedules and departures. Check before you travel →',
        'ru': 'Адреса, расписание и отправления. Проверь перед поездкой →',
    },
    'stations.routes_count': {
        'sr': 'ruta',
        'en': 'routes',
        'ru': 'маршрутов',
    },
    'stations.in_base_suffix': {
        'sr': 'stanica u bazi',
        'en': 'stations in database',
        'ru': 'станций в базе',
    },
    'stations.type_train': {
        'sr': 'Železnička stanica',
        'en': 'Railway station',
        'ru': 'Железнодорожная станция',
    },
    'stations.type_bus': {
        'sr': 'Autobuska stanica',
        'en': 'Bus station',
        'ru': 'Автобусная станция',
    },
    'stations.type_generic': {
        'sr': 'Stanica',
        'en': 'Station',
        'ru': 'Станция',
    },
    'stations.empty_loading': {
        'sr': 'Podaci se učitavaju',
        'en': 'Data is loading',
        'ru': 'Данные загружаются',
    },
    'stations.breadcrumb': {
        'sr': 'Stanice',
        'en': 'Stations',
        'ru': 'Станции',
    },

    # ── city_index.html ──
    'city_index.subtitle': {
        'sr': 'Linije, stajališta i red vožnje',
        'en': 'Lines, stops and schedules',
        'ru': 'Линии, остановки и расписание',
    },
    'city_index.meta_cta': {
        'sr': 'Pronađi besplatno →',
        'en': 'Find for free →',
        'ru': 'Найди бесплатно →',
    },
    'city_index.lines_suffix': {
        'sr': 'linija',
        'en': 'lines',
        'ru': 'линий',
    },
    'city_index.breadcrumb': {
        'sr': 'Gradski prevoz',
        'en': 'City transport',
        'ru': 'Городской транспорт',
    },

    # ── city_pair.html ──
    'city_pair.title_suffix': {
        'sr': 'autobus i voz',
        'en': 'bus and train',
        'ru': 'автобус и поезд',
        'bg': 'автобус и влак',
    },
    'city_pair.meta_prefix': {
        'sr': 'Kako doći od',
        'en': 'How to travel from',
        'ru': 'Как добраться из',
        'bg': 'Как да стигнете от',
    },
    'city_pair.meta_mid': {
        'sr': 'do',
        'en': 'to',
        'ru': 'до',
        'bg': 'до',
    },
    'city_pair.meta_suffix': {
        'sr': 'Red vožnje, cene karata i prevoznici.',
        'en': 'Schedule, ticket prices and carriers.',
        'ru': 'Расписание, цены билетов и перевозчики.',
        'bg': 'Разписание, цени на билетите и превозвачи.',
    },
    'city_pair.see_all_departures': {
        'sr': 'Pogledaj sve polaske →',
        'en': 'See all departures →',
        'ru': 'Все отправления →',
        'bg': 'Виж всички тръгвания →',
    },
    'city_pair.carriers_heading': {
        'sr': 'Prevoznici',
        'en': 'Carriers',
        'ru': 'Перевозчики',
        'bg': 'Превозвачи',
    },
    'city_pair.carriers_hint': {
        'sr': 'Proverite kod prevoznika za aktuelne linije.',
        'en': 'Check with carriers for current lines.',
        'ru': 'Уточняйте актуальные рейсы у перевозчиков.',
        'bg': 'Проверете при превозвача за актуални линии.',
    },
    'city_pair.prices_heading': {
        'sr': 'Cene',
        'en': 'Prices',
        'ru': 'Цены',
        'bg': 'Цени',
    },
    'city_pair.prices_hint': {
        'sr': 'Cene variraju po prevoznicima. Kupite karte na blagajni.',
        'en': 'Prices vary by carrier. Buy tickets at the ticket office.',
        'ru': 'Цены у разных перевозчиков отличаются. Билеты продаются в кассе.',
        'bg': 'Цените варират според превозвача. Купете билети на касата.',
    },
    'city_pair.tips_heading': {
        'sr': 'Saveti',
        'en': 'Tips',
        'ru': 'Советы',
        'bg': 'Съвети',
    },
    'city_pair.tip_buy_early': {
        'sr': 'Kupite kartu unapred u sezoni i za vikende.',
        'en': 'Buy tickets in advance during the season and weekends.',
        'ru': 'Покупайте билеты заранее в сезон и на выходные.',
        'bg': 'Купете билет предварително през сезона и през уикендите.',
    },
    'city_pair.faq_heading': {
        'sr': 'Često postavljana pitanja',
        'en': 'Frequently asked questions',
        'ru': 'Часто задаваемые вопросы',
        'bg': 'Често задавани въпроси',
    },
    'city_pair.other_routes_from': {
        'sr': 'Druge rute iz grada',
        'en': 'Other routes from',
        'ru': 'Другие маршруты из',
        'bg': 'Други маршрути от града',
    },
    'city_pair.departures_word': {
        'sr': 'polazaka',
        'en': 'departures',
        'ru': 'отправлений',
        'bg': 'тръгвания',
    },
    'city_pair.no_direct': {
        'sr': 'Direktna veza nije u bazi',
        'en': 'No direct route in database',
        'ru': 'Прямой маршрут отсутствует в базе',
        'bg': 'Директна връзка не е в базата данни',
    },

    # ── city_pair body prose (was hardcoded SR; now translated) ──
    'city_pair.subtitle_daily': {
        'sr': '{count} polazaka dnevno',
        'en': '{count} departures per day',
        'ru': '{count} отправлений в день',
        'bg': '{count} тръгвания дневно',
    },
    'city_pair.subtitle_from_price': {
        'sr': 'od', 'en': 'from', 'ru': 'от',
        'bg': 'от',
    },
    'city_pair.seo_h2': {
        'sr': '{from_city} — {to_city}: prevoz',
        'en': '{from_city} — {to_city}: travel',
        'ru': '{from_city} — {to_city}: транспорт',
        'bg': '{from_city} — {to_city}: транспорт',
    },
    'city_pair.prose_distance': {
        'sr': 'Rastojanje između {from_city} i {to_city} iznosi {km} km.',
        'en': 'The distance between {from_city} and {to_city} is {km} km.',
        'ru': 'Расстояние между {from_city} и {to_city} составляет {km} км.',
        'bg': 'Разстоянието между {from_city} и {to_city} е {km} км.',
    },
    'city_pair.prose_duration_range': {
        'sr': 'Putovanje traje od {h_min}h {m_min}min do {h_max}h {m_max}min u zavisnosti od prevoznika.',
        'en': 'The journey takes {h_min}h {m_min}min to {h_max}h {m_max}min depending on the carrier.',
        'ru': 'Поездка занимает от {h_min}ч {m_min}мин до {h_max}ч {m_max}мин в зависимости от перевозчика.',
        'bg': 'Пътуването отнема от {h_min}ч {m_min}мин до {h_max}ч {m_max}мин в зависимост от превозвача.',
    },
    'city_pair.prose_operators': {
        'sr': 'Na ovoj ruti voze: {operators}.',
        'en': 'Carriers on this route: {operators}.',
        'ru': 'На этом маршруте работают перевозчики: {operators}.',
        'bg': 'По този маршрут пътуват: {operators}.',
    },
    'city_pair.prose_price_range': {
        'sr': 'Cene karata kreću se od {min} do {max} RSD ({eur_min}–{eur_max}€).',
        'en': 'Ticket prices range from {min} to {max} RSD ({eur_min}–{eur_max}€).',
        'ru': 'Цены на билеты — от {min} до {max} RSD ({eur_min}–{eur_max}€).',
        'bg': 'Цените на билетите варират от {min} до {max} RSD ({eur_min}–{eur_max}€).',
    },
    'city_pair.prose_first_last': {
        'sr': 'Prvi polazak je u {first}, a poslednji u {last}.',
        'en': 'The first departure is at {first}, the last at {last}.',
        'ru': 'Первое отправление в {first}, последнее в {last}.',
        'bg': 'Първото тръгване е в {first}, а последното в {last}.',
    },
    'city_pair.carriers_count': {
        'sr': 'Na liniji {from_city} — {to_city} voze {n} prevoznika: {operators}.',
        'en': 'There are {n} carriers on {from_city} — {to_city}: {operators}.',
        'ru': 'На линии {from_city} — {to_city} работают {n} перевозчиков: {operators}.',
        'bg': 'По линията {from_city} — {to_city} пътуват {n} превозвача: {operators}.',
    },
    'city_pair.cheapest_op': {
        'sr': 'Najjeftinije karte nudi {operator}.',
        'en': 'The cheapest tickets are offered by {operator}.',
        'ru': 'Самые дешёвые билеты предлагает {operator}.',
        'bg': 'Най-евтините билети предлага {operator}.',
    },
    'city_pair.prices_range_buy': {
        'sr': 'Karte od {min} RSD ({eur_min}€) do {max} RSD ({eur_max}€). Kupite na blagajni autobuske stanice ili online.',
        'en': 'Tickets from {min} RSD ({eur_min}€) to {max} RSD ({eur_max}€). Buy at the bus station counter or online.',
        'ru': 'Билеты от {min} RSD ({eur_min}€) до {max} RSD ({eur_max}€). Покупка в кассе автовокзала или онлайн.',
        'bg': 'Билети от {min} RSD ({eur_min}€) до {max} RSD ({eur_max}€). Купете на касата на автогарата или онлайн.',
    },
    'city_pair.tip_first_last_short': {
        'sr': 'Prvi polazak u {first}, poslednji u {last}.',
        'en': 'First departure {first}, last {last}.',
        'ru': 'Первое отправление {first}, последнее {last}.',
        'bg': 'Първо тръгване в {first}, последно в {last}.',
    },
    'city_pair.tip_duration': {
        'sr': 'Putovanje traje {h_min}h {m_min}min{suffix}.',
        'en': 'Journey takes {h_min}h {m_min}min{suffix}.',
        'ru': 'Поездка занимает {h_min}ч {m_min}мин{suffix}.',
        'bg': 'Пътуването отнема {h_min}ч {m_min}мин{suffix}.',
    },
    'city_pair.tip_duration_range_suffix': {
        'sr': '–{h_max}h {m_max}min',
        'en': '–{h_max}h {m_max}min',
        'ru': '–{h_max}ч {m_max}мин',
        'bg': '–{h_max}ч {m_max}мин',
    },

    # ── route_detail.html ──
    'route_detail.title_suffix': {
        'sr': 'red vožnje',
        'en': 'schedule',
        'ru': 'расписание',
        'bg': 'разписание',
    },
    'route_detail.meta_schedule': {
        'sr': 'Red vožnje',
        'en': 'Schedule',
        'ru': 'Расписание',
        'bg': 'Разписание',
    },
    'route_detail.meta_daily': {
        'sr': 'polazaka dnevno',
        'en': 'departures daily',
        'ru': 'отправлений в день',
        'bg': 'тръгвания дневно',
    },
    'route_detail.meta_carriers': {
        'sr': 'prevoznici',
        'en': 'carriers',
        'ru': 'перевозчики',
        'bg': 'превозвачи',
    },
    'route_detail.meta_and_more': {
        'sr': 'i dr',
        'en': 'and more',
        'ru': 'и др',
        'bg': 'и др.',
    },
    'route_detail.meta_from': {
        'sr': 'Od',
        'en': 'From',
        'ru': 'От',
        'bg': 'От',
    },
    # CTR-optimized snippets: title/meta rewrites (2026+)
    'route_detail.title_departures': {
        'sr': 'polazaka dnevno',
        'en': 'departures daily',
        'ru': 'отправлений в день',
        'bg': 'тръгвания дневно',
    },
    'route_detail.title_short': {
        'sr': 'red vožnje i cene',
        'en': 'schedule and prices',
        'ru': 'расписание и цены',
        'bg': 'разписание и цени',
    },
    'route_detail.meta_compare_cta': {
        'sr': 'Uporedi prevoznike i cene besplatno.',
        'en': 'Compare carriers and prices for free.',
        'ru': 'Сравните перевозчиков и цены бесплатно.',
        'bg': 'Сравнете превозвачи и цени безплатно.',
    },
    'route_detail.meta_prefix': {
        'sr': 'Autobuska ruta',
        'en': 'Bus route',
        'ru': 'Автобусный маршрут',
        'bg': 'Автобусен маршрут',
    },
    # Shortened 2026-09-10, then again 2026-09-13: the first pass dropped
    # an even longer lead-in but left "Red vožnje, cene karata, prevoznici
    # i trajanje putovanja." (60 chars) in place despite the comment above
    # already claiming the country.meta_cta-only phrasing — a live 150-route
    # sample after that fix still showed 28.7% over Google's ~160-char SERP
    # limit (median 134, p90 174), because the dynamic prefix (city names,
    # km, trip_count, price) already eats 60-100 chars before this fixed
    # tail even starts. That boilerplate sentence restates what the page
    # title/content already say on every one of 1539 routes — it doesn't
    # differentiate the snippet, it just eats the budget that would
    # otherwise show the actual price/schedule facts. Dropped for real this
    # time: now matches country.meta_cta exactly.
    'route_detail.meta_body': {
        'sr': 'Uporedite cene i kupite kartu. Besplatno.',
        'en': 'Compare prices, buy tickets. Free.',
        'ru': 'Сравните цены, купите билет. Бесплатно.',
        'bg': 'Сравнете цени, купете билет. Безплатно.',
    },
    # Same as meta_body but for routes with zero affiliate coverage (Union
    # Ivkoni, srbijatours.com) — drops the "buy online via partner" claim
    # that would otherwise be false for these, mirroring the on-page
    # route.prose_buy / _primary_href gate.
    'route_detail.meta_body_no_partner': {
        'sr': 'Uporedite polaske i cene. Besplatno.',
        'en': 'Compare departures and prices. Free.',
        'ru': 'Сравните рейсы и цены. Бесплатно.',
        'bg': 'Сравнете тръгвания и цени. Безплатно.',
    },
    'route.prose_distance': {
        'sr': 'Vožnja od {from_city} do {to_city} iznosi oko {km} km.',
        'en': 'The trip from {from_city} to {to_city} is about {km} km.',
        'ru': 'Поездка из {from_city} в {to_city} занимает около {km} км.',
        'bg': 'Пътуването от {from_city} до {to_city} е около {km} км.',
    },
    'route.prose_duration': {
        'sr': 'Prosečno trajanje putovanja autobusom je oko {hours} sata.',
        'en': 'Average bus trip duration is around {hours} hours.',
        'ru': 'Средняя длительность поездки на автобусе — около {hours} часов.',
        'bg': 'Средната продължителност на пътуването с автобус е около {hours} часа.',
    },
    'route.prose_operators': {
        'sr': 'Na ovoj ruti voze prevoznici: {ops}.',
        'en': 'Carriers on this route: {ops}.',
        'ru': 'На этом маршруте работают перевозчики: {ops}.',
        'bg': 'По този маршрут пътуват превозвачите: {ops}.',
    },
    'route.prose_price_range': {
        'sr': 'Cene karata se kreću od {min} do {max} RSD, u zavisnosti od prevoznika i dana.',
        'en': 'Ticket prices range from {min} to {max} RSD, depending on carrier and day.',
        'ru': 'Цены билетов колеблются от {min} до {max} RSD в зависимости от перевозчика и дня.',
        'bg': 'Цените на билетите варират от {min} до {max} RSD, в зависимост от превозвача и деня.',
    },
    'route.prose_price_single': {
        'sr': 'Cena karte iznosi oko {price} RSD.',
        'en': 'Ticket price is around {price} RSD.',
        'ru': 'Цена билета — около {price} RSD.',
        'bg': 'Цената на билета е около {price} RSD.',
    },
    'route.prose_context': {
        'sr': 'Autobuske linije između {from_city} i {to_city} povezuju putnike tokom cele godine. Na ovoj stranici prikazujemo kompletan red vožnje za svaki dan u nedelji, sa mogućnošću filtriranja po vremenu polaska, trajanju putovanja ili ceni. Podaci se ažuriraju svake noći iz više izvora (busticket4.me, polazak.rs, srbijavoz.rs), a prikazane cene su orjentacione — konačnu cenu i raspoloživost mesta potvrđuje partner kod kog kupujete kartu.',
        'en': 'Bus lines between {from_city} and {to_city} run year-round. This page shows the full schedule for each day of the week, with filters for departure time, trip duration and price. Data is refreshed nightly from multiple sources (busticket4.me, polazak.rs, srbijavoz.rs), and displayed prices are indicative — the final fare and seat availability is confirmed by the partner where you buy the ticket.',
        'ru': 'Автобусные рейсы между {from_city} и {to_city} работают круглый год. На этой странице показано полное расписание по дням недели, с фильтрами по времени отправления, длительности поездки и цене. Данные обновляются каждую ночь из нескольких источников (busticket4.me, polazak.rs, srbijavoz.rs), а показанные цены ориентировочные — финальную цену и наличие мест подтверждает партнёр, у которого вы покупаете билет.',
        'bg': 'Автобусните линии между {from_city} и {to_city} свързват пътници целогодишно. На тази страница показваме пълното разписание за всеки ден от седмицата, с възможност за филтриране по час на тръгване, продължителност на пътуването или цена. Данните се обновяват всяка нощ от няколко източника (busticket4.me, polazak.rs, srbijavoz.rs), а показаните цени са ориентировъчни — крайната цена и наличността на места се потвърждават от партньора, от когото купувате билета.',
    },
    'route.prose_buy': {
        'sr': 'Kartu za rutu {from_city} — {to_city} možete kupiti direktno kod prevoznika na autobuskoj stanici ili online preko partnera (BusTicket4.me). Online kupovina obično nudi nekoliko različitih polazaka po istoj ceni, pa vredi uporediti vremena. Za grupe preko 5 putnika ili studentske popuste kontaktirajte prevoznika direktno — Prevozni ne prodaje karte i nije posrednik u kupovini.',
        'en': 'You can buy a ticket for {from_city} — {to_city} directly from the carrier at the bus station or online via partners (BusTicket4.me). Online purchase usually offers several departures at the same price, so it is worth comparing times. For groups of 5+ or student discounts contact the carrier directly — Prevozni does not sell tickets and is not a purchase intermediary.',
        'ru': 'Билет на маршрут {from_city} — {to_city} можно купить напрямую у перевозчика на автовокзале или онлайн через партнёров (BusTicket4.me). Онлайн-покупка обычно предлагает несколько отправлений по одной цене — стоит сравнить время. Для групп от 5 человек или студенческих скидок обращайтесь напрямую к перевозчику — Prevozni не продаёт билеты и не является посредником.',
        'bg': 'Билет за маршрута {from_city} — {to_city} можете да купите директно от превозвача на автогарата или онлайн през партньор (BusTicket4.me). Онлайн покупката обикновено предлага няколко различни тръгвания на една и съща цена, затова си струва да сравните часовете. За групи над 5 души или студентски отстъпки се свържете директно с превозвача — Prevozni не продава билети и не е посредник в продажбата.',
    },
    'city_pair.title_travel': {
        'sr': 'autobus, voz, cene',
        'en': 'bus, train, prices',
        'ru': 'автобус, поезд, цены',
        'bg': 'автобус, влак, цени',
    },
    'city_pair.meta_cta': {
        'sr': 'Uporedi polaske, cene i vreme putovanja. Besplatno.',
        'en': 'Compare departures, prices and travel time. Free.',
        'ru': 'Сравните отправления, цены и время в пути. Бесплатно.',
        'bg': 'Сравнете тръгвания, цени и време на пътуване. Безплатно.',
    },
    'line_detail.title': {
        'sr': 'Red Vožnje Linije',
        'en': 'Line Schedule',
        'ru': 'Расписание Линии',
    },
    'line_detail.title_line_city': {
        'sr': 'stanice i red vožnje',
        'en': 'stops and schedule',
        'ru': 'остановки и расписание',
    },
    'line_detail.meta_eta': {
        'sr': 'Karta linije, sve stanice i uživo dolasci.',
        'en': 'Line map, all stops and live arrivals.',
        'ru': 'Карта линии, все остановки и прибытия онлайн.',
        'bg': 'Карта на линията, всички спирки и тръгвания на живо.',
    },
    'stop_detail.title_stop_city': {
        'sr': 'red vožnje i linije',
        'en': 'schedule and lines',
        'ru': 'расписание и линии',
        'bg': 'разписание и линии',
    },
    'stop_detail.meta_eta': {
        'sr': 'Sve linije, prvi i poslednji polazak, uživo ETA na karti.',
        'en': 'All lines, first and last departure, live ETA on the map.',
        'ru': 'Все линии, первый и последний рейс, онлайн-ETA на карте.',
        'bg': 'Всички линии, първо и последно тръгване, ETA на живо на картата.',
    },

    # ── search_results.html ──
    'search_results.meta_from': {
        'sr': 'Red vožnje od',
        'en': 'Schedule from',
        'ru': 'Расписание от',
        'bg': 'Разписание от',
    },
    'search_results.meta_to': {
        'sr': 'do',
        'en': 'to',
        'ru': 'до',
        'bg': 'до',
    },
    'search_results.meta_desc': {
        'sr': 'svi polasci, cene karata i prevoznici na jednom mestu.',
        'en': 'all departures, ticket prices and carriers in one place.',
        'ru': 'все отправления, цены билетов и перевозчики в одном месте.',
        'bg': 'всички тръгвания, цени на билетите и превозвачи на едно място.',
    },
    'search_results.meta_default': {
        'sr': 'Pretražite red vožnje autobusa i vozova između gradova Srbije. Uporedite polaske, cene i prevoznike. Besplatno.',
        'en': 'Search bus and train schedules between cities in Serbia. Compare departures, prices and carriers. Free.',
        'ru': 'Ищите расписание автобусов и поездов между городами Сербии. Сравнивайте отправления, цены и перевозчиков. Бесплатно.',
        'bg': 'Претърсете разписанието на автобуси и влакове между градовете на Сърбия. Сравнете тръгвания, цени и превозвачи. Безплатно.',
    },
    'search_results.h1': {
        'sr': 'Pronađite prevoz',
        'en': 'Find transport',
        'ru': 'Найдите транспорт',
        'bg': 'Намерете превоз',
    },
    'search_results.hero_sub': {
        'sr': 'Autobus ili voz između gradova Srbije',
        'en': 'Bus or train between cities in Serbia',
        'ru': 'Автобус или поезд между городами Сербии',
        'bg': 'Автобус или влак между градовете на Сърбия',
    },
    'search_results.sort_label': {
        'sr': 'Sortiraj:',
        'en': 'Sort:',
        'ru': 'Сортировка:',
        'bg': 'Сортирай:',
    },
    'search_results.sort_time': {
        'sr': 'Po vremenu',
        'en': 'By time',
        'ru': 'По времени',
        'bg': 'По време',
    },
    'search_results.sort_price': {
        'sr': 'Po ceni',
        'en': 'By price',
        'ru': 'По цене',
        'bg': 'По цена',
    },

    # ── city_transport.html ──
    'city_transport.title_prefix': {
        'sr': 'Gradski prevoz',
        'en': 'City transport',
        'ru': 'Городской транспорт',
        'bg': 'Градски транспорт',
    },
    'city_transport.title_suffix': {
        'sr': 'linije i stajališta',
        'en': 'lines and stops',
        'ru': 'линии и остановки',
        'bg': 'линии и спирки',
    },
    'city_transport.meta_prefix': {
        'sr': 'Red vožnje gradskog prevoza u',
        'en': 'City transport schedule in',
        'ru': 'Расписание городского транспорта в',
        'bg': 'Разписание на градския транспорт в',
    },
    'city_transport.meta_lines': {
        'sr': 'linija, stajališta i polasci.',
        'en': 'lines, stops and departures.',
        'ru': 'линий, остановок и отправлений.',
        'bg': 'линии, спирки и тръгвания.',
    },
    'city_transport.meta_extra': {
        'sr': 'Interaktivna mapa stajališta, red vožnje i dolasci uživo. Besplatno →',
        'en': 'Interactive stop map, schedules and live arrivals. Free →',
        'ru': 'Интерактивная карта остановок, расписание и прибытия онлайн. Бесплатно →',
        'bg': 'Интерактивна карта на спирките, разписание и тръгвания на живо. Безплатно →',
    },
    'city_transport.stop_popup_more': {
        'sr': 'Polasci →',
        'en': 'Departures →',
        'ru': 'Отправления →',
    },

    # ── line_detail.html ──
    'line_detail.schedule_heading': {
        'sr': 'Red vožnje',
        'en': 'Schedule',
        'ru': 'Расписание',
        'bg': 'Разписание',
    },
    'line_detail.line_prefix': {
        'sr': 'Linija',
        'en': 'Line',
        'ru': 'Линия',
        'bg': 'Линия',
    },
    'line_detail.meta_schedule': {
        'sr': 'Red vožnje linije',
        'en': 'Schedule for line',
        'ru': 'Расписание линии',
    },
    'line_detail.meta_in': {
        'sr': 'u',
        'en': 'in',
        'ru': 'в',
    },
    'line_detail.meta_stops': {
        'sr': 'stajališta.',
        'en': 'stops.',
        'ru': 'остановок.',
    },
    'line_detail.meta_departures': {
        'sr': 'Polasci od',
        'en': 'Departures from',
        'ru': 'Отправления с',
        'bg': 'Тръгвания от',
    },
    'line_detail.meta_to': {
        'sr': 'do',
        'en': 'to',
        'ru': 'до',
        'bg': 'до',
    },

    # ── stop_detail.html ──
    'stop_detail.stop_prefix': {
        'sr': 'Stajalište',
        'en': 'Stop',
        'ru': 'Остановка',
        'bg': 'Спирка',
    },
    'stop_detail.title_suffix': {
        'sr': 'red vožnje',
        'en': 'schedule',
        'ru': 'расписание',
        'bg': 'разписание',
    },
    'stop_detail.meta_schedule': {
        'sr': 'red vožnje i polasci.',
        'en': 'schedule and departures.',
        'ru': 'расписание и отправления.',
    },
    'stop_detail.meta_lines_suffix': {
        'sr': 'linija',
        'en': 'lines',
        'ru': 'линий',
        'bg': 'линии',
    },
    'stop_detail.meta_and_more': {
        'sr': 'i dr.',
        'en': 'and more',
        'ru': 'и др.',
    },

    # ── filter panel ──
    'filter.heading': {
        'sr': 'Filteri',
        'en': 'Filters',
        'ru': 'Фильтры',
        'bg': 'Филтри',
    },
    'filter.close': {
        'sr': 'Zatvori',
        'en': 'Close',
        'ru': 'Закрыть',
        'bg': 'Затвори',
    },
    'filter.transport_type': {
        'sr': 'Tip prevoza',
        'en': 'Transport type',
        'ru': 'Тип транспорта',
        'bg': 'Вид транспорт',
    },
    'filter.bus': {
        'sr': 'Autobus',
        'en': 'Bus',
        'ru': 'Автобус',
        'bg': 'Автобус',
    },
    'filter.train': {
        'sr': 'Voz',
        'en': 'Train',
        'ru': 'Поезд',
        'bg': 'Влак',
    },
    'filter.carrier': {
        'sr': 'Prevoznik',
        'en': 'Carrier',
        'ru': 'Перевозчик',
        'bg': 'Превозвач',
    },

    # ── Search form ──
    'search_form.swap': {
        'sr': 'Zameni',
        'en': 'Swap',
        'ru': 'Поменять',
    },

    # ── city_pair FAQ (interpolated) ──
    'city_pair.faq.q_duration': {
        'sr': 'Koliko traje putovanje {from_city} — {to_city}?',
        'en': 'How long does the {from_city} — {to_city} trip take?',
        'ru': 'Сколько длится поездка {from_city} — {to_city}?',
        'bg': 'Колко продължава пътуването {from_city} — {to_city}?',
    },
    'city_pair.faq.q_price': {
        'sr': 'Koja je cena karte {from_city} — {to_city}?',
        'en': 'What is the ticket price for {from_city} — {to_city}?',
        'ru': 'Сколько стоит билет {from_city} — {to_city}?',
        'bg': 'Каква е цената на билета {from_city} — {to_city}?',
    },
    'city_pair.faq.q_departures': {
        'sr': 'Koliko polazaka dnevno ima {from_city} — {to_city}?',
        'en': 'How many daily departures are there from {from_city} to {to_city}?',
        'ru': 'Сколько ежедневных рейсов {from_city} — {to_city}?',
        'bg': 'Колко тръгвания дневно има {from_city} — {to_city}?',
    },
    'city_pair.faq.q_operators': {
        'sr': 'Koji prevoznici voze {from_city} — {to_city}?',
        'en': 'Which carriers operate {from_city} — {to_city}?',
        'ru': 'Какие перевозчики обслуживают {from_city} — {to_city}?',
        'bg': 'Кои превозвачи обслужват {from_city} — {to_city}?',
    },
    'city_pair.faq.a_duration_range': {
        'sr': 'Putovanje od {from_city} do {to_city} traje od {h_min}h {m_min}min do {h_max}h {m_max}min.',
        'en': 'The trip from {from_city} to {to_city} takes from {h_min}h {m_min}min up to {h_max}h {m_max}min.',
        'ru': 'Поездка из {from_city} в {to_city} занимает от {h_min}ч {m_min}мин до {h_max}ч {m_max}мин.',
        'bg': 'Пътуването от {from_city} до {to_city} отнема от {h_min}ч {m_min}мин до {h_max}ч {m_max}мин.',
    },
    'city_pair.faq.a_duration_distance_suffix': {
        'sr': ' Rastojanje je {km} km.',
        'en': ' The distance is {km} km.',
        'ru': ' Расстояние — {km} км.',
        'bg': ' Разстоянието е {km} км.',
    },
    'city_pair.faq.a_duration_distance_only': {
        'sr': 'Rastojanje je oko {km} km. Tačno trajanje zavisi od prevoznika.',
        'en': 'The distance is about {km} km. Exact duration depends on the carrier.',
        'ru': 'Расстояние около {km} км. Точное время зависит от перевозчика.',
        'bg': 'Разстоянието е около {km} км. Точната продължителност зависи от превозвача.',
    },
    'city_pair.faq.a_duration_unknown': {
        'sr': 'Trajanje zavisi od prevoznika i tipa prevoza.',
        'en': 'Duration depends on the carrier and transport type.',
        'ru': 'Время в пути зависит от перевозчика и вида транспорта.',
        'bg': 'Продължителността зависи от превозвача и вида транспорт.',
    },
    'city_pair.faq.a_price_range': {
        'sr': 'Cene karata kreću se od {min} do {max} RSD ({eur_min}–{eur_max}€).',
        'en': 'Ticket prices range from {min} to {max} RSD ({eur_min}–{eur_max}€).',
        'ru': 'Цены билетов варьируются от {min} до {max} RSD ({eur_min}–{eur_max}€).',
        'bg': 'Цените на билетите варират от {min} до {max} RSD ({eur_min}–{eur_max}€).',
    },
    'city_pair.faq.a_price_cheapest_suffix': {
        'sr': ' Najjeftiniji prevoznik je {operator}.',
        'en': ' The cheapest carrier is {operator}.',
        'ru': ' Самый дешёвый перевозчик — {operator}.',
        'bg': ' Най-евтиният превозвач е {operator}.',
    },
    'city_pair.faq.a_price_from': {
        'sr': 'Cene karata počinju od {min} RSD (oko {eur}€).',
        'en': 'Ticket prices start from {min} RSD (about {eur}€).',
        'ru': 'Цены билетов начинаются от {min} RSD (около {eur}€).',
        'bg': 'Цените на билетите започват от {min} RSD (около {eur}€).',
    },
    'city_pair.faq.a_price_unknown': {
        'sr': 'Cene variraju u zavisnosti od prevoznika.',
        'en': 'Prices vary depending on the carrier.',
        'ru': 'Цены зависят от перевозчика.',
        'bg': 'Цените варират в зависимост от превозвача.',
    },
    'city_pair.faq.a_departures_full': {
        'sr': 'Na ovoj ruti ima {count} polazaka dnevno. Prvi polazak je u {first}, poslednji u {last}.',
        'en': 'This route has {count} daily departures. First at {first}, last at {last}.',
        'ru': 'На этом маршруте {count} рейсов в день. Первый в {first}, последний в {last}.',
        'bg': 'По този маршрут има {count} тръгвания дневно. Първото тръгване е в {first}, последното в {last}.',
    },
    'city_pair.faq.a_departures_operators_suffix': {
        'sr': ' Voze: {operators}.',
        'en': ' Operated by: {operators}.',
        'ru': ' Обслуживают: {operators}.',
        'bg': ' Пътуват: {operators}.',
    },
    'city_pair.faq.a_departures_count_only': {
        'sr': 'Na ovoj ruti ima {count} polazaka dnevno.',
        'en': 'This route has {count} daily departures.',
        'ru': 'На этом маршруте {count} рейсов в день.',
        'bg': 'По този маршрут има {count} тръгвания дневно.',
    },
    'city_pair.faq.a_departures_unknown': {
        'sr': 'Broj polazaka varira. Proverite aktuelni red vožnje.',
        'en': 'The number of departures varies. Check the current schedule.',
        'ru': 'Количество рейсов меняется. Проверьте актуальное расписание.',
        'bg': 'Броят на тръгванията варира. Проверете актуалното разписание.',
    },
    'city_pair.faq.a_operators_list': {
        'sr': 'Na liniji {from_city} — {to_city} voze {n} prevoznika: {operators}.',
        'en': 'On the {from_city} — {to_city} route there are {n} carriers: {operators}.',
        'ru': 'На маршруте {from_city} — {to_city} работают {n} перевозчиков: {operators}.',
        'bg': 'По линията {from_city} — {to_city} пътуват {n} превозвача: {operators}.',
    },
    'city_pair.faq.a_operators_cheapest_suffix': {
        'sr': ' Najjeftiniji prevoznik je {operator} sa cenama od {min} RSD.',
        'en': ' The cheapest carrier is {operator} with prices from {min} RSD.',
        'ru': ' Самый дешёвый перевозчик — {operator}, цены от {min} RSD.',
        'bg': ' Най-евтиният превозвач е {operator} с цени от {min} RSD.',
    },
    # JSON-LD short variants
    'city_pair.faq.ld_duration_range': {
        'sr': 'Putovanje traje od {h_min}h {m_min}min do {h_max}h {m_max}min.',
        'en': 'The trip takes from {h_min}h {m_min}min up to {h_max}h {m_max}min.',
        'ru': 'Поездка занимает от {h_min}ч {m_min}мин до {h_max}ч {m_max}мин.',
        'bg': 'Пътуването отнема от {h_min}ч {m_min}мин до {h_max}ч {m_max}мин.',
    },
    'city_pair.faq.ld_price_range': {
        'sr': 'Od {min} do {max} RSD ({eur_min}–{eur_max}€).',
        'en': 'From {min} to {max} RSD ({eur_min}–{eur_max}€).',
        'ru': 'От {min} до {max} RSD ({eur_min}–{eur_max}€).',
        'bg': 'От {min} до {max} RSD ({eur_min}–{eur_max}€).',
    },
    'city_pair.faq.ld_price_cheapest_suffix': {
        'sr': ' Najjeftiniji: {operator}.',
        'en': ' Cheapest: {operator}.',
        'ru': ' Самый дешёвый: {operator}.',
        'bg': ' Най-евтин: {operator}.',
    },
    'city_pair.faq.ld_price_from': {
        'sr': 'Od {min} RSD ({eur}€).',
        'en': 'From {min} RSD ({eur}€).',
        'ru': 'От {min} RSD ({eur}€).',
        'bg': 'От {min} RSD ({eur}€).',
    },
    'city_pair.faq.ld_price_unknown': {
        'sr': 'Cene variraju.',
        'en': 'Prices vary.',
        'ru': 'Цены варьируются.',
        'bg': 'Цените варират.',
    },
    'city_pair.faq.ld_departures_full': {
        'sr': '{count} polazaka dnevno. Prvi u {first}, poslednji u {last}.',
        'en': '{count} departures daily. First at {first}, last at {last}.',
        'ru': '{count} рейсов в день. Первый в {first}, последний в {last}.',
        'bg': '{count} тръгвания дневно. Първо в {first}, последно в {last}.',
    },
    'city_pair.faq.ld_departures_count_only': {
        'sr': '{count} polazaka dnevno.',
        'en': '{count} departures daily.',
        'ru': '{count} рейсов в день.',
        'bg': '{count} тръгвания дневно.',
    },
    'city_pair.faq.ld_departures_unknown': {
        'sr': 'Broj polazaka varira.',
        'en': 'The number of departures varies.',
        'ru': 'Количество рейсов меняется.',
        'bg': 'Броят на тръгванията варира.',
    },
    'city_pair.faq.ld_operators_list': {
        'sr': 'Voze {n} prevoznika: {operators}.',
        'en': '{n} carriers operate: {operators}.',
        'ru': '{n} перевозчиков: {operators}.',
        'bg': 'Пътуват {n} превозвача: {operators}.',
    },

    # ── route_detail FAQ JSON-LD ──
    'route_detail.faq.q_departures': {
        'sr': 'Koliko polazaka ima od {from_city} do {to_city}?',
        'en': 'How many departures are there from {from_city} to {to_city}?',
        'ru': 'Сколько рейсов из {from_city} в {to_city}?',
        'bg': 'Колко тръгвания има от {from_city} до {to_city}?',
    },
    'route_detail.faq.a_departures': {
        'sr': 'Dnevno ima {count} polazaka od {from_city} do {to_city}.',
        'en': 'There are {count} daily departures from {from_city} to {to_city}.',
        'ru': 'Ежедневно выполняется {count} рейсов из {from_city} в {to_city}.',
        'bg': 'Дневно има {count} тръгвания от {from_city} до {to_city}.',
    },
    'route_detail.faq.q_price': {
        'sr': 'Koliko košta karta {from_city} — {to_city}?',
        'en': 'How much is a {from_city} — {to_city} ticket?',
        'ru': 'Сколько стоит билет {from_city} — {to_city}?',
        'bg': 'Колко струва билет {from_city} — {to_city}?',
    },
    'route_detail.faq.a_price_from': {
        'sr': 'Cena karte počinje od {min} RSD.',
        'en': 'Ticket price starts from {min} RSD.',
        'ru': 'Цена билета начинается от {min} RSD.',
        'bg': 'Цената на билета започва от {min} RSD.',
    },
    'route_detail.faq.a_price_unknown': {
        'sr': 'Cene variraju u zavisnosti od prevoznika; proverite aktuelne cene na stranici.',
        'en': 'Prices vary by carrier; check current prices on the page.',
        'ru': 'Цены зависят от перевозчика; проверьте актуальные цены на странице.',
        'bg': 'Цените варират в зависимост от превозвача; проверете актуалните цени на страницата.',
    },
    'route_detail.faq.q_operators': {
        'sr': 'Koji prevoznici voze liniju {from_city} — {to_city}?',
        'en': 'Which carriers operate the {from_city} — {to_city} route?',
        'ru': 'Какие перевозчики обслуживают маршрут {from_city} — {to_city}?',
        'bg': 'Кои превозвачи обслужват линията {from_city} — {to_city}?',
    },
    'route_detail.faq.a_operators_list': {
        'sr': 'Na ovoj liniji voze: {operators}.',
        'en': 'This route is operated by: {operators}.',
        'ru': 'Этот маршрут обслуживают: {operators}.',
        'bg': 'По тази линия пътуват: {operators}.',
    },
    'route_detail.faq.a_operators_unknown': {
        'sr': 'Proverite listu polazaka za aktuelne prevoznike.',
        'en': 'Check the departures list for current carriers.',
        'ru': 'Проверьте список рейсов для актуальных перевозчиков.',
        'bg': 'Проверете списъка с тръгвания за актуалните превозвачи.',
    },

    # ── line_detail FAQ JSON-LD ──
    'line_detail.faq.q_stops': {
        'sr': 'Koliko stajališta ima linija {number}?',
        'en': 'How many stops does line {number} have?',
        'ru': 'Сколько остановок у линии {number}?',
        'bg': 'Колко спирки има линия {number}?',
    },
    'line_detail.faq.a_stops': {
        'sr': 'Linija {number} ({name}) u {city}u ima {count} stajališta, od {first} do {last}.',
        'en': 'Line {number} ({name}) in {city} has {count} stops, from {first} to {last}.',
        'ru': 'Линия {number} ({name}) в городе {city} имеет {count} остановок, от {first} до {last}.',
        'bg': 'Линия {number} ({name}) в {city} има {count} спирки, от {first} до {last}.',
    },
    'line_detail.faq.a_stops_no_endpoints': {
        'sr': 'Linija {number} ({name}) u {city}u ima {count} stajališta.',
        'en': 'Line {number} ({name}) in {city} has {count} stops.',
        'ru': 'Линия {number} ({name}) в городе {city} имеет {count} остановок.',
        'bg': 'Линия {number} ({name}) в {city} има {count} спирки.',
    },
    'line_detail.faq.q_when': {
        'sr': 'Kada saobraća linija {number}?',
        'en': 'When does line {number} run?',
        'ru': 'Когда работает линия {number}?',
        'bg': 'Кога се движи линия {number}?',
    },
    'line_detail.faq.a_when_range': {
        'sr': 'Linija {number} saobraća od {first} do {last} radnim danom prema GTFS redu vožnje.',
        'en': 'Line {number} runs from {first} to {last} on weekdays according to the GTFS schedule.',
        'ru': 'Линия {number} работает с {first} до {last} по будням согласно расписанию GTFS.',
        'bg': 'Линия {number} се движи от {first} до {last} в делничен ден според разписанието по GTFS.',
    },
    'line_detail.faq.a_when_unknown': {
        'sr': 'Tačan red vožnje linije {number} proverite na stajalištima ili kod gradskog prevoznika.',
        'en': 'Check the exact schedule for line {number} at the stops or with the city carrier.',
        'ru': 'Точное расписание линии {number} уточняйте на остановках или у городского перевозчика.',
        'bg': 'Точното разписание на линия {number} проверете на спирките или при градския превозвач.',
    },
    'line_detail.faq.q_type': {
        'sr': 'Koji je tip linije {number}?',
        'en': 'What type is line {number}?',
        'ru': 'Какой тип у линии {number}?',
        'bg': 'Какъв тип е линия {number}?',
    },
    'line_detail.faq.a_type': {
        'sr': 'Linija {number} je {type} u sistemu gradskog prevoza grada {city}.',
        'en': 'Line {number} is a {type} in the {city} city transport system.',
        'ru': 'Линия {number} — это {type} в системе городского транспорта города {city}.',
        'bg': 'Линия {number} е {type} в системата на градския транспорт на град {city}.',
    },
    # "Na koliko minuta ide linija N" is a top GSC query pattern; surfaced only
    # when we have a real GTFS-derived headway (gated in the template).
    'line_detail.faq.q_freq': {
        'sr': 'Na koliko minuta ide linija {number}?',
        'en': 'How often does line {number} run?',
        'ru': 'Как часто ходит линия {number}?',
        'bg': 'На колко минути идва линия {number}?',
    },
    'line_detail.faq.a_freq': {
        'sr': 'Linija {number} radnim danom ima polazak u proseku na svakih ~{headway} minuta.',
        'en': 'On weekdays line {number} departs on average about every ~{headway} minutes.',
        'ru': 'По будням линия {number} отправляется в среднем примерно каждые ~{headway} минут.',
        'bg': 'Линия {number} в делничен ден има тръгване средно на всеки ~{headway} минути.',
    },

    # ── stop_detail FAQ JSON-LD ──
    'stop_detail.faq.q_lines': {
        'sr': 'Koje linije staju na stajalištu {stop}?',
        'en': 'Which lines stop at {stop}?',
        'ru': 'Какие линии останавливаются на остановке {stop}?',
        'bg': 'Кои линии спират на спирка {stop}?',
    },
    'stop_detail.faq.a_lines': {
        'sr': 'Na stajalištu {stop} u {city}u staje {count} linija gradskog prevoza ({types}).',
        'en': 'At stop {stop} in {city}, {count} city transport lines stop ({types}).',
        'ru': 'На остановке {stop} в городе {city} останавливается {count} линий городского транспорта ({types}).',
        'bg': 'На спирка {stop} в {city} спират {count} линии на градския транспорт ({types}).',
    },
    'stop_detail.faq.q_when': {
        'sr': 'Kada polaze autobusi sa stajališta {stop}?',
        'en': 'When do buses depart from {stop}?',
        'ru': 'Когда отправляются автобусы с остановки {stop}?',
        'bg': 'Кога тръгват автобусите от спирка {stop}?',
    },
    'stop_detail.faq.a_when_range': {
        'sr': 'Prvi polazak sa stajališta {stop} je u {first}, a poslednji u {last} radnim danom.',
        'en': 'The first departure from {stop} is at {first}, the last at {last} on weekdays.',
        'ru': 'Первый рейс с остановки {stop} в {first}, последний в {last} по будням.',
        'bg': 'Първото тръгване от спирка {stop} е в {first}, а последното — в {last}, в делничен ден.',
    },
    'stop_detail.faq.a_when_unknown': {
        'sr': 'Tačan red vožnje proverite na samom stajalištu ili preko mobilne aplikacije gradskog prevoznika.',
        'en': 'Check the exact schedule at the stop itself or via the city carrier mobile app.',
        'ru': 'Точное расписание уточняйте на самой остановке или в мобильном приложении городского перевозчика.',
        'bg': 'Точното разписание проверете на самата спирка или чрез мобилното приложение на градския превозвач.',
    },
    'stop_detail.faq.q_where': {
        'sr': 'Gde se nalazi stajalište {stop}?',
        'en': 'Where is stop {stop} located?',
        'ru': 'Где находится остановка {stop}?',
        'bg': 'Къде се намира спирка {stop}?',
    },
    'stop_detail.faq.a_where': {
        'sr': 'Stajalište {stop} se nalazi u gradu {city}.',
        'en': 'Stop {stop} is located in the city of {city}.',
        'ru': 'Остановка {stop} находится в городе {city}.',
        'bg': 'Спирка {stop} се намира в град {city}.',
    },
    'stop_detail.faq.a_where_coords_suffix': {
        'sr': ' Koordinate: {lat}, {lon}.',
        'en': ' Coordinates: {lat}, {lon}.',
        'ru': ' Координаты: {lat}, {lon}.',
        'bg': ' Координати: {lat}, {lon}.',
    },
    'stop_detail.faq.a_where_outro': {
        'sr': ' Detaljna mapa i lista linija dostupni su besplatno na Prevozni.com.',
        'en': ' A detailed map and list of lines are available for free on Prevozni.com.',
        'ru': ' Подробная карта и список линий доступны бесплатно на Prevozni.com.',
        'bg': ' Подробна карта и списък на линиите са достъпни безплатно на Prevozni.com.',
    },

    # ── Hub SEO intros & FAQ: route_index (/rute/) ──
    'route_index.intro_h': {
        'sr': 'Međugradski autobusi i vozovi u Srbiji',
        'en': 'Intercity buses and trains in Serbia',
        'ru': 'Междугородние автобусы и поезда в Сербии',
    },
    'route_index.intro_p1': {
        'sr': 'Prevozni.com objedinjuje red vožnje za <strong>autobuske i železničke rute</strong> širom Srbije i regiona. '
              'Kataloške stranice pokrivaju preko 270 pravaca sa direktnim polascima između <a href="{prefix}/gradski/beograd/">Beograda</a>, '
              '<a href="{prefix}/gradski/novi-sad/">Novog Sada</a>, <a href="{prefix}/gradski/nis/">Niša</a>, <a href="{prefix}/gradski/kragujevac/">Kragujevca</a> '
              'i desetina manjih gradova, kao i međunarodne linije ka Crnoj Gori, Bosni i Hercegovini, Hrvatskoj, Severnoj Makedoniji, Sloveniji, Mađarskoj i Turskoj. '
              'Za svaku rutu prikazujemo broj dnevnih polazaka, trajanje putovanja, minimalnu cenu karte i listu prevoznika koji saobraćaju na toj relaciji, '
              'uključujući <a href="{prefix}/prevoznici/">Lastu, Niš-Ekspres, OZLEM, Srbija Voz</a> i druge operatere.',
        'en': 'Prevozni.com aggregates timetables for <strong>intercity buses and trains</strong> across Serbia and the Balkans. '
              'The catalog covers 270+ routes with direct departures between <a href="{prefix}/gradski/beograd/">Belgrade</a>, '
              '<a href="{prefix}/gradski/novi-sad/">Novi Sad</a>, <a href="{prefix}/gradski/nis/">Niš</a>, <a href="{prefix}/gradski/kragujevac/">Kragujevac</a> '
              'and dozens of smaller towns, plus international lines to Montenegro, Bosnia and Herzegovina, Croatia, North Macedonia, Slovenia, Hungary and Turkey. '
              'For every route we show the number of daily departures, journey time, minimum ticket price and the list of operators running the line, '
              'including <a href="{prefix}/prevoznici/">Lasta, Niš-Ekspres, OZLEM, Srbija Voz</a> and others.',
        'ru': 'Prevozni.com объединяет расписание <strong>междугородних автобусов и поездов</strong> по Сербии и Балканам. '
              'Каталог охватывает более 270 направлений с прямыми рейсами между <a href="{prefix}/gradski/beograd/">Белградом</a>, '
              '<a href="{prefix}/gradski/novi-sad/">Нови-Садом</a>, <a href="{prefix}/gradski/nis/">Нишем</a>, <a href="{prefix}/gradski/kragujevac/">Крагуевацем</a> '
              'и десятками небольших городов, а также международные рейсы в Черногорию, Боснию и Герцеговину, Хорватию, Северную Македонию, Словению, Венгрию и Турцию. '
              'По каждому маршруту мы показываем количество ежедневных рейсов, длительность поездки, минимальную цену билета и список перевозчиков, '
              'включая <a href="{prefix}/prevoznici/">Lasta, Niš-Ekspres, OZLEM, Srbija Voz</a> и других.',
    },
    'route_index.intro_p2': {
        'sr': 'Pretraga u vrhu stranice filtrira rute u realnom vremenu prema imenu polaznog ili ciljnog grada. '
              'Klikom na bilo koju rutu otvarate detaljnu stranicu sa spiskom polazaka po satu, cenama po prevozniku i filterima po delu dana '
              '(jutro 06–12, popodne 12–18, veče 18–22, noć 22–06). Svaka ruta ima i SEO parnu stranicu tipa '
              '<code>/voznja/grad1-do-grad2/</code> sa prosečnim trajanjem, rasponom cena i najjeftinijim prevoznikom — '
              'korisno kad biramo najpovoljniji termin putovanja. Red vožnje se automatski osvežava svakih 24 sata iz zvaničnih izvora '
              '(busticket4.me, polazak.rs, bgprevoz, gspns, srbijavoz). Karte se kupuju na blagajni autobuske stanice, u vozilu kod vozača ili online preko partnerskih sajtova.',
        'en': 'The search bar at the top filters routes live by origin or destination city. '
              'Clicking any route opens a detail page with hour-by-hour departures, prices per operator and time-of-day filters '
              '(morning 06–12, afternoon 12–18, evening 18–22, night 22–06). Every route also has an SEO city-pair page at '
              '<code>/voznja/city1-do-city2/</code> with average duration, price range and the cheapest operator — useful for picking the best-value departure. '
              'Timetables refresh every 24 hours from official sources (busticket4.me, polazak.rs, bgprevoz, gspns, srbijavoz). '
              'Tickets are sold at bus-station counters, on-board from the driver, or online through partner sites.',
        'ru': 'Строка поиска сверху фильтрует маршруты в реальном времени по названию города отправления или прибытия. '
              'При клике на маршрут открывается детальная страница с рейсами по часам, ценами по перевозчикам и фильтрами по времени суток '
              '(утро 06–12, день 12–18, вечер 18–22, ночь 22–06). У каждого маршрута также есть SEO-страница пары городов по адресу '
              '<code>/voznja/gorod1-do-gorod2/</code> со средней длительностью, диапазоном цен и самым дешёвым перевозчиком — полезно при выборе оптимального рейса. '
              'Расписание обновляется каждые 24 часа из официальных источников (busticket4.me, polazak.rs, bgprevoz, gspns, srbijavoz). '
              'Билеты продаются в кассах автовокзала, у водителя в автобусе или онлайн через партнёрские сайты.',
    },
    'route_index.faq_heading': {
        'sr': 'Česta pitanja o autobuskim rutama',
        'en': 'Frequently asked questions about bus routes',
        'ru': 'Частые вопросы об автобусных маршрутах',
    },
    'route_index.faq_q1': {
        'sr': 'Koliko međugradskih ruta pokriva Prevozni.com?',
        'en': 'How many intercity routes does Prevozni.com cover?',
        'ru': 'Сколько междугородних маршрутов охватывает Prevozni.com?',
    },
    'route_index.faq_a1': {
        'sr': 'U bazi imamo {n} domaćih i međunarodnih linija sa preko 2800 polazaka dnevno. Katalog uključuje sve velike prevoznike u Srbiji (Lasta, Niš-Ekspres, Srbija Voz) '
              'i regionalne operatere za linije ka Crnoj Gori, BiH, Hrvatskoj, Mađarskoj, Severnoj Makedoniji i Turskoj. Svakog dana se podaci ažuriraju iz zvaničnih izvora.',
        'en': 'The database holds {n} domestic and international routes with 2,800+ daily departures. The catalog includes all major Serbian carriers (Lasta, Niš-Ekspres, Srbija Voz) '
              'plus regional operators for lines to Montenegro, Bosnia, Croatia, Hungary, North Macedonia and Turkey. Data is refreshed daily from official sources.',
        'ru': 'В базе {n} внутренних и международных маршрутов с более чем 2800 рейсами в сутки. Каталог включает всех крупных сербских перевозчиков (Lasta, Niš-Ekspres, Srbija Voz) '
              'и региональных операторов на линиях в Черногорию, Боснию, Хорватию, Венгрию, Северную Македонию и Турцию. Данные обновляются ежедневно.',
    },
    'route_index.faq_q2': {
        'sr': 'Kako da nađem najjeftiniju autobusku kartu?',
        'en': 'How do I find the cheapest bus ticket?',
        'ru': 'Как найти самый дешёвый автобусный билет?',
    },
    'route_index.faq_a2': {
        'sr': 'Otvorite detaljnu stranicu rute i pogledajte kolonu cene — svaki polazak prikazuje cenu u RSD i EUR. '
              'Na SEO parnoj stranici /voznja/grad1-do-grad2/ prikazan je raspon cena i najjeftiniji prevoznik. '
              'Generalno, rani jutarnji (06–08) i noćni (22–06) polasci često imaju niže cene, a kupovina karte unapred može doneti dodatni popust kod nekih operatera.',
        'en': 'Open the route detail page and check the price column — each departure shows the price in RSD and EUR. '
              'The SEO city-pair page at /voznja/city1-do-city2/ displays the price range and the cheapest operator. '
              'In general, early morning (06–08) and overnight (22–06) departures often have lower fares, and buying in advance can unlock additional discounts with some operators.',
        'ru': 'Откройте детальную страницу маршрута и посмотрите колонку цены — у каждого рейса указана цена в RSD и EUR. '
              'На SEO-странице пары /voznja/gorod1-do-gorod2/ показан диапазон цен и самый дешёвый перевозчик. '
              'Обычно ранние утренние (06–08) и ночные (22–06) рейсы дешевле, а покупка билета заранее иногда даёт дополнительную скидку.',
    },
    'route_index.faq_q3': {
        'sr': 'Mogu li da kupim kartu direktno preko Prevozni.com?',
        'en': 'Can I buy a ticket directly through Prevozni.com?',
        'ru': 'Можно ли купить билет прямо через Prevozni.com?',
    },
    'route_index.faq_a3': {
        'sr': 'Prevozni.com je informativni servis — red vožnje je besplatan i bez registracije. '
              'Na svakoj stranici rute nalazi se dugme „Kupi kartu" koje vodi na partnerski sistem (BusTicket4.me) gde se kupovina obavlja online. '
              'Karte se takođe kupuju na blagajni autobuske stanice ili kod vozača u autobusu.',
        'en': 'Prevozni.com is an information service — timetables are free and require no registration. '
              'Each route page has a "Buy ticket" button that opens our partner (BusTicket4.me) for online booking. '
              'Tickets are also sold at the bus station counter or on-board from the driver.',
        'ru': 'Prevozni.com — информационный сервис: расписание бесплатно и без регистрации. '
              'На каждой странице маршрута есть кнопка «Купить билет», которая ведёт к партнёру (BusTicket4.me) для онлайн-покупки. '
              'Билеты также продаются в кассе автовокзала или у водителя.',
    },
    'route_index.faq_q4': {
        'sr': 'Koliko često se ažurira red vožnje?',
        'en': 'How often are timetables updated?',
        'ru': 'Как часто обновляется расписание?',
    },
    'route_index.faq_a4': {
        'sr': 'Osnovni podaci (rute, prevoznici, cene) ažuriraju se svakodnevno u 3:00 ujutru iz zvaničnih izvora. '
              'Za GTFS podatke o gradskom prevozu Beograda i Novog Sada, ažuriranje se vrši nedeljno. '
              'Ukoliko primetite netačan podatak, možete nas kontaktirati preko <a href="{prefix}/kontakt/">kontakt stranice</a>.',
        'en': 'Route-level data (routes, operators, prices) refresh nightly at 3:00 AM from official sources. '
              'GTFS city-transit data for Belgrade and Novi Sad is updated weekly. '
              'If you spot an error, please let us know via the <a href="{prefix}/kontakt/">contact page</a>.',
        'ru': 'Основные данные (маршруты, перевозчики, цены) обновляются ночью в 3:00 из официальных источников. '
              'GTFS-данные по городскому транспорту Белграда и Нови-Сада обновляются еженедельно. '
              'Если заметили неточность, напишите нам через <a href="{prefix}/kontakt/">страницу контактов</a>.',
    },
    'route_index.popular_heading': {
        'sr': 'Najpopularnije rute',
        'en': 'Most popular routes',
        'ru': 'Самые популярные маршруты',
    },

    # ── Hub SEO intros & FAQ: city_index (/gradski/) ──
    'city_index.intro_h': {
        'sr': 'Gradski prevoz u Srbiji: linije, stajališta, mape',
        'en': 'City public transit in Serbia: lines, stops, maps',
        'ru': 'Городской транспорт Сербии: линии, остановки, карты',
    },
    'city_index.intro_p1': {
        'sr': 'Četiri najveća grada Srbije imaju razvijenu mrežu javnog gradskog prevoza. '
              '<strong><a href="{prefix}/gradski/beograd/">Beograd</a></strong> operiše sa preko 500 linija autobusa, tramvaja i trolejbusa '
              'u okviru GSP Beograd, sa potpunim GTFS rasporedom od preko 87.000 dnevnih polazaka. '
              '<strong><a href="{prefix}/gradski/novi-sad/">Novi Sad</a></strong> ima 60+ linija JGSP Novi Sad sa rasporedom od 6.500 polazaka. '
              '<strong><a href="{prefix}/gradski/nis/">Niš</a></strong> opslužuje JGP Niš-Ekspres sa 50+ linija, '
              'a <strong><a href="{prefix}/gradski/kragujevac/">Kragujevac</a></strong> 23 linije lokalnog prevoznika. '
              'Ukupno je u bazi 610 linija i preko 3700 stajališta sa GPS koordinatama — praktično sve stajalište u glavnim gradovima možete pronaći na interaktivnoj mapi.',
        'en': 'Serbia\'s four largest cities run full-fledged public transit networks. '
              '<strong><a href="{prefix}/gradski/beograd/">Belgrade</a></strong> operates 500+ bus, tram and trolleybus lines under GSP Beograd, '
              'with a complete GTFS schedule of 87,000+ daily departures. '
              '<strong><a href="{prefix}/gradski/novi-sad/">Novi Sad</a></strong> has 60+ JGSP Novi Sad lines with a 6,500-departure schedule. '
              '<strong><a href="{prefix}/gradski/nis/">Niš</a></strong> is served by JGP Niš-Ekspres with 50+ lines, '
              'and <strong><a href="{prefix}/gradski/kragujevac/">Kragujevac</a></strong> by 23 local carrier lines. '
              'In total the database holds 610 lines and over 3,700 stops with GPS coordinates — you can find practically any stop in the main cities on the interactive map.',
        'ru': 'Четыре крупнейших города Сербии имеют развитую сеть городского транспорта. '
              '<strong><a href="{prefix}/gradski/beograd/">Белград</a></strong> — 500+ линий автобусов, трамваев и троллейбусов под управлением GSP Beograd, '
              'с полным GTFS-расписанием на 87 000+ рейсов в сутки. '
              '<strong><a href="{prefix}/gradski/novi-sad/">Нови-Сад</a></strong> — 60+ линий JGSP Novi Sad с расписанием на 6 500 рейсов. '
              '<strong><a href="{prefix}/gradski/nis/">Ниш</a></strong> обслуживается JGP Niš-Ekspres с 50+ линиями, '
              '<strong><a href="{prefix}/gradski/kragujevac/">Крагуевац</a></strong> — 23 линии местного перевозчика. '
              'Всего в базе 610 линий и более 3700 остановок с GPS-координатами — практически любую остановку крупных городов можно найти на интерактивной карте.',
    },
    'city_index.intro_p2': {
        'sr': 'Za svaku liniju prikazujemo trasu, spisak stajališta, tip prevoza (autobus / tramvaj / trolejbus / noćna linija) i, gde postoji GTFS feed, '
              'tačan raspored polazaka za radni dan, subotu i nedelju. Klikom na stajalište otvarate stranicu sa spiskom linija koje tu staju, '
              'procenom vremena dolaska narednog vozila (ETA) i najbližim stajalištima. '
              'Karte za gradski prevoz u Srbiji kupuju se preko BusPlus kartice (Beograd), AP karte (Novi Sad) ili na kioscima i kod vozača. '
              'Prevozni.com ne prodaje karte za gradski prevoz — naš cilj je da ponudi besplatan i brz pregled linija, stajališta i polazaka '
              'u svim većim gradovima, korisno putnicima, turistima i studentima koji se tek upoznaju sa mrežom.',
        'en': 'For every line we show the route path, stop list, transport type (bus / tram / trolleybus / night line) and, where a GTFS feed is available, '
              'the exact departure schedule for weekdays, Saturdays and Sundays. Clicking a stop opens a page with the lines serving it, '
              'an ETA estimate for the next arriving vehicle and nearby stops. '
              'Tickets for city transit in Serbia are purchased with the BusPlus card (Belgrade), AP card (Novi Sad) or at kiosks and from the driver. '
              'Prevozni.com does not sell city-transit tickets — our goal is to provide a free, fast overview of lines, stops and departures '
              'in every major city, useful for commuters, tourists and students learning the network.',
        'ru': 'Для каждой линии показываем трассу, список остановок, тип транспорта (автобус / трамвай / троллейбус / ночная линия) и, где есть GTFS, '
              'точное расписание на будни, субботу и воскресенье. При клике на остановку открывается страница со списком линий, '
              'прогнозом времени прибытия следующего транспорта (ETA) и ближайшими остановками. '
              'Билеты на городской транспорт покупаются по карте BusPlus (Белград), AP (Нови-Сад), в киосках или у водителя. '
              'Prevozni.com не продаёт билеты на городской транспорт — наша цель дать бесплатный и быстрый обзор линий, остановок и рейсов '
              'во всех крупных городах, что полезно местным жителям, туристам и студентам.',
    },
    'city_index.faq_heading': {
        'sr': 'Česta pitanja o gradskom prevozu',
        'en': 'Frequently asked questions about city transit',
        'ru': 'Частые вопросы о городском транспорте',
    },
    'city_index.faq_q1': {
        'sr': 'Koji gradovi imaju kompletne podatke na Prevozni.com?',
        'en': 'Which cities have complete data on Prevozni.com?',
        'ru': 'В каких городах есть полные данные на Prevozni.com?',
    },
    'city_index.faq_a1': {
        'sr': 'Trenutno pokrivamo Beograd (GSP, 514 linija, pun GTFS raspored), Novi Sad (JGSP, 61 linija, GTFS), '
              'Niš (JGP Niš-Ekspres, 53 linije) i Kragujevac (23 linije). Za Beograd i Novi Sad imamo tačne vremena polazaka; '
              'za Niš i Kragujevac prikazujemo trase i stajališta ali bez detaljnog GTFS rasporeda.',
        'en': 'We currently cover Belgrade (GSP, 514 lines, full GTFS schedule), Novi Sad (JGSP, 61 lines, GTFS), '
              'Niš (JGP Niš-Ekspres, 53 lines) and Kragujevac (23 lines). Belgrade and Novi Sad have precise departure times; '
              'Niš and Kragujevac show routes and stops but without detailed GTFS schedules.',
        'ru': 'Сейчас охвачены Белград (GSP, 514 линий, полный GTFS), Нови-Сад (JGSP, 61 линия, GTFS), '
              'Ниш (JGP Niš-Ekspres, 53 линии) и Крагуевац (23 линии). У Белграда и Нови-Сада точное время рейсов; '
              'у Ниша и Крагуеваца — только трассы и остановки без подробного GTFS-расписания.',
    },
    'city_index.faq_q2': {
        'sr': 'Kako da nađem stajalište najbliže mojoj adresi?',
        'en': 'How do I find the stop closest to my address?',
        'ru': 'Как найти остановку, ближайшую к моему адресу?',
    },
    'city_index.faq_a2': {
        'sr': 'Otvorite stranicu grada (npr. /gradski/beograd/) i koristite interaktivnu mapu. '
              'Mapa prikazuje sva stajališta sa GPS koordinatama — zumirajte do željenog dela grada i kliknite na marker '
              'da vidite koje linije tu staju. Na stranici svakog stajališta prikazujemo i obližnja stajališta u radijusu od 500 metara.',
        'en': 'Open the city page (e.g. /gradski/beograd/) and use the interactive map. '
              'The map shows every stop with GPS coordinates — zoom to your area and click a marker to see which lines stop there. '
              'Each stop\'s detail page also lists nearby stops within ~500 metres.',
        'ru': 'Откройте страницу города (например /gradski/beograd/) и воспользуйтесь интерактивной картой. '
              'На карте отмечены все остановки с GPS — приблизьте нужный район и кликните по маркеру, чтобы увидеть линии. '
              'На странице каждой остановки также есть список ближайших остановок в радиусе ~500 м.',
    },
    'city_index.faq_q3': {
        'sr': 'Da li je raspored tačan u realnom vremenu?',
        'en': 'Is the schedule real-time?',
        'ru': 'Показывается ли расписание в реальном времени?',
    },
    'city_index.faq_a3': {
        'sr': 'Prikazujemo planirani red vožnje iz GTFS feeda (ne GPS lokaciju vozila). ETA na stranici stajališta se računa iz rasporeda — '
              'za stvarni GPS položaj vozila koristite zvanične aplikacije gradskih prevoznika (BusPlus, Moj Grad Beograd, Beograd+). '
              'U praksi su polasci u Beogradu tačni unutar 5 minuta tokom radnog dana.',
        'en': 'We show the scheduled timetable from GTFS feeds, not live vehicle GPS. The ETA on a stop page is computed from the schedule — '
              'for real-time vehicle positions, use the official city-carrier apps (BusPlus, Moj Grad Beograd, Beograd+). '
              'In practice Belgrade departures are accurate within ~5 minutes on weekdays.',
        'ru': 'Показываем плановое расписание из GTFS (не GPS-позицию транспорта). ETA на странице остановки считается из расписания — '
              'для реального положения транспорта используйте официальные приложения (BusPlus, Moj Grad Beograd, Beograd+). '
              'На практике в Белграде рейсы по будням точны в пределах ~5 минут.',
    },

    # ── Hub SEO intros & FAQ: city_transport (/gradski/{city}/) ──
    'city_transport.intro_h': {
        'sr': 'O gradskom prevozu: {city}',
        'en': 'About public transit in {city}',
        'ru': 'О городском транспорте: {city}',
        'bg': 'За градския транспорт: {city}',
    },
    'city_transport.intro_beograd_p1': {
        'sr': '<strong>GSP Beograd</strong> upravlja najvećom mrežom javnog prevoza u Srbiji: autobusi, tramvaji i trolejbusi čine više od 500 linija, '
              'sa preko 87.000 dnevnih polazaka. Sistem pokriva 17 beogradskih opština, od Zemuna i Novog Beograda preko Vračara i Voždovca do Rakovice i Grocke. '
              'Noćne linije (oznaka „N") saobraćaju sedam dana u nedelji, svakih 30–60 minuta, povezujući centar sa glavnim perifernim kvartovima. '
              'Tramvajska mreža ima 12 dnevnih linija oko centra i Novog Beograda, trolejbuski sistem obuhvata 8 linija ka Zvezdari, Voždovcu i Paliluli. '
              'Pored ovoga, BG:Voz — prigradski železnički sistem — povezuje Beograd sa Batajnicom, Ovčom i Resnikom.',
        'en': '<strong>GSP Beograd</strong> operates the largest public-transit network in Serbia: buses, trams and trolleybuses form 500+ lines '
              'with 87,000+ daily departures. The system covers all 17 Belgrade municipalities, from Zemun and Novi Beograd through Vračar and Voždovac to Rakovica and Grocka. '
              'Night lines (prefix "N") run seven days a week every 30–60 minutes, linking the centre to major outer districts. '
              'The tram network has 12 daytime lines around the centre and Novi Beograd; 8 trolleybus lines connect Zvezdara, Voždovac and Palilula. '
              'BG:Voz suburban rail also links Belgrade with Batajnica, Ovča and Resnik.',
        'ru': '<strong>GSP Beograd</strong> управляет крупнейшей сетью общественного транспорта Сербии: автобусы, трамваи и троллейбусы — это 500+ линий '
              'и более 87 000 рейсов в сутки. Система охватывает все 17 белградских общин, от Земуна и Нового Белграда до Врачара, Вождовца, Раковицы и Гроцки. '
              'Ночные линии (префикс «N») работают 7 дней в неделю каждые 30–60 минут, соединяя центр с основными окраинами. '
              'Трамвайная сеть — 12 дневных линий в центре и Новом Белграде; 8 троллейбусных линий — Звездара, Вождовац и Палилула. '
              'BG:Voz — пригородная железная дорога до Батайницы, Овчи и Ресника.',
        'bg': '<strong>ГСП Белград</strong> управлява най-голямата мрежа за градски транспорт в Сърбия: автобусите, трамваите и тролейбусите образуват над 500 линии, с над 87 000 тръгвания дневно. Системата обхваща 17 белградски общини — от Земун и Нови Белград, през Врачар и Вождовац, до Раковица и Гроцка. Нощните линии (с обозначение „N“) се движат седем дни в седмицата, на всеки 30–60 минути, свързвайки центъра с основните периферни квартали. Трамвайната мрежа има 12 дневни линии около центъра и Нови Белград, а тролейбусната система обхваща 8 линии към Звездара, Вождовац и Палилула. Освен това BG:Voz — крайградската жп система — свързва Белград с Батайница, Овча и Ресник.',
    },
    'city_transport.intro_beograd_p2': {
        'sr': 'Karte se kupuju preko <strong>BusPlus kartice</strong>, koja se puni na kioscima ili u GSP-ovim prodajnim mestima. '
              'Cena jednokratne vožnje u zoni I iznosi oko 50 RSD, a dnevna karta košta 290 RSD. Studenti, penzioneri i đaci imaju popust uz potvrdu statusa. '
              'BG:Voz koristi drugačiji tarifni sistem — karte se kupuju na stanicama Srbija Voza. '
              'Za putovanja van Beograda koristi se mreža <a href="{prefix}/rute/">međugradskih autobusa i vozova</a>, sa polazcima sa Autobuske stanice BAS, '
              'Centralnog železničkog stajališta Prokop i Lasta stanice.',
        'en': 'Tickets are purchased with the <strong>BusPlus card</strong>, rechargeable at kiosks and GSP points. '
              'A single ride in Zone I costs around 50 RSD, a day pass 290 RSD. Students, pensioners and pupils get discounts with proof of status. '
              'BG:Voz uses a separate Srbija Voz ticket system. '
              'For travel outside Belgrade, use the <a href="{prefix}/rute/">intercity bus and train network</a>, with departures from BAS Bus Station, '
              'Prokop Central Station and the Lasta terminal.',
        'ru': 'Билеты покупаются по карте <strong>BusPlus</strong>, которую пополняют в киосках и точках GSP. '
              'Одна поездка в зоне I — около 50 RSD, проездной на день — 290 RSD. Студенты, пенсионеры и школьники — по скидке при наличии документа. '
              'У BG:Voz отдельная тарифная система — билеты Srbija Voz. '
              'Для поездок за пределами Белграда — сеть <a href="{prefix}/rute/">междугородних автобусов и поездов</a> с отправлением с автостанции BAS, '
              'центрального ж/д вокзала Прокоп и терминала Lasta.',
        'bg': 'Билетите се купуват чрез <strong>картата BusPlus</strong>, която се зарежда на павилиони или в продажните пунктове на ГСП. Цената на еднократно пътуване в зона I е около 50 RSD, а дневният билет струва 290 RSD. Студенти, пенсионери и ученици получават отстъпка срещу удостоверение за статут. BG:Voz използва различна тарифна система — билетите се купуват на гарите на Сърбия Воз. За пътувания извън Белград се използва мрежата от <a href="{prefix}/rute/">междуградски автобуси и влакове</a>, с тръгвания от автогара БАС, Централна железопътна гара Прокоп и автогара Ласта.',
    },
    'city_transport.intro_novi_sad_p1': {
        'sr': '<strong>JGSP Novi Sad</strong> upravlja javnim gradskim prevozom u drugom najvećem gradu Srbije. '
              'Mreža se sastoji od 60+ autobuskih linija koje povezuju centralno gradsko jezgro sa prigradskim naseljima (Petrovaradin, Sremska Kamenica, Futog, Veternik, Rumenka, Kać). '
              'Gradski prevoz u Novom Sadu je prvenstveno autobuski — tramvaja i trolejbusa u gradu nema. '
              'GTFS raspored za Novi Sad je dostupan u našoj bazi, tako da je moguće prikazati tačne polaske po satu za radni dan, subotu i nedelju.',
        'en': '<strong>JGSP Novi Sad</strong> runs city transit in Serbia\'s second-largest city. '
              'The network consists of 60+ bus lines connecting the city core with suburban settlements (Petrovaradin, Sremska Kamenica, Futog, Veternik, Rumenka, Kać). '
              'Novi Sad has no trams or trolleybuses — transit is bus-only. '
              'A GTFS schedule for Novi Sad is in our database, so exact departure times for weekdays, Saturdays and Sundays are available.',
        'ru': '<strong>JGSP Novi Sad</strong> управляет городским транспортом второго по величине города Сербии. '
              'Сеть — 60+ автобусных линий, соединяющих центр с пригородами (Петроварадин, Сремска-Каменица, Футог, Ветерник, Руменка, Кач). '
              'В Нови-Саде нет трамваев и троллейбусов — только автобусы. '
              'GTFS-расписание Нови-Сада есть в нашей базе, поэтому доступно точное время рейсов на будни, субботу и воскресенье.',
        'bg': '<strong>ЈГСП Нови Сад</strong> управлява градския обществен транспорт във втория по големина град на Сърбия. Мрежата се състои от над 60 автобусни линии, свързващи централното градско ядро с крайградските селища (Петроварадин, Сремска Каменица, Футог, Ветерник, Руменка, Кач). Градският транспорт в Нови Сад е предимно автобусен — в града няма трамваи или тролейбуси. GTFS разписание за Нови Сад е налично в нашата база данни, така че е възможно да се покажат точните часове на тръгване за делничен ден, събота и неделя.',
    },
    'city_transport.intro_novi_sad_p2': {
        'sr': 'Karte se kupuju preko <strong>AP kartice JGSP Novi Sad</strong>, pametne kartice koja se puni u AP kioscima ili aplikaciji Moj JGSP. '
              'Cena jednokratne vožnje iznosi oko 65 RSD, mesečna karta za đake košta od 1000 RSD. Pojedinačnu kartu moguće je kupiti i kod vozača po nešto višoj ceni. '
              'Za <a href="{prefix}/rute/">međugradske linije</a> koristi se Autobuska stanica Novi Sad — povezuje Novi Sad sa Beogradom, Suboticom, Nišom, Zrenjaninom i desetinama drugih gradova.',
        'en': 'Tickets use the <strong>JGSP Novi Sad AP card</strong>, a smart card rechargeable at AP kiosks or the Moj JGSP app. '
              'A single ride costs around 65 RSD, a monthly student pass starts at 1,000 RSD. Single tickets can also be purchased from the driver at a slightly higher price. '
              'For <a href="{prefix}/rute/">intercity routes</a> use Novi Sad Bus Station — connecting Novi Sad with Belgrade, Subotica, Niš, Zrenjanin and dozens of other cities.',
        'ru': 'Билеты — по смарт-карте <strong>JGSP Novi Sad (AP)</strong>, которую пополняют в киосках AP или приложении Moj JGSP. '
              'Одна поездка — около 65 RSD, ученический проездной — от 1000 RSD. Разовый билет можно купить и у водителя по чуть более высокой цене. '
              '<a href="{prefix}/rute/">Междугородние рейсы</a> — с автовокзала Нови-Сада: Белград, Суботица, Ниш, Зренянин и десятки других городов.',
        'bg': 'Билетите се купуват чрез <strong>картата АП на ЈГСП Нови Сад</strong>, безконтактна карта, която се зарежда на АП павилиони или в приложението Moj JGSP. Цената на еднократно пътуване е около 65 RSD, а месечната карта за ученици струва от 1000 RSD. Единичен билет може да се купи и при водача на малко по-висока цена. За <a href="{prefix}/rute/">междуградски линии</a> се използва автогара Нови Сад — свързваща Нови Сад с Белград, Суботица, Ниш, Зренянин и десетки други градове.',
    },
    'city_transport.intro_nis_p1': {
        'sr': '<strong>JGP Niš-Ekspres</strong> operiše gradskim prevozom u Nišu i okolini. '
              'Mreža obuhvata oko 50 autobuskih linija koje pokrivaju Niš i prigradska naselja — od Medoševca i Bubnja na zapadu do Donjeg Međurova i Crvenog Krsta na istoku. '
              'Ne postoji tramvajski ili trolejbuski sistem. GTFS raspored za Niš nije javno dostupan, zato prikazujemo trase i spiskove stajališta, '
              'a za tačno vreme polazaka preporučujemo proveru u vozilu ili na kioscima Niš-Ekspresa.',
        'en': '<strong>JGP Niš-Ekspres</strong> runs city transit in Niš and its surroundings. '
              'The network comprises some 50 bus lines covering Niš and suburban settlements — from Medoševac and Bubanj in the west to Donje Međurovo and Crveni Krst in the east. '
              'There are no trams or trolleybuses. A public GTFS schedule for Niš is not available, so we show routes and stop lists — '
              'for exact departure times, check on-board or at Niš-Ekspres kiosks.',
        'ru': '<strong>JGP Niš-Ekspres</strong> — городской перевозчик Ниша и окрестностей. '
              'Сеть — около 50 автобусных линий по Нишу и пригородам: от Медошеваца и Бубни на западе до Донего-Мэдюрова и Црвеного-Крста на востоке. '
              'Трамваев и троллейбусов нет. Публичного GTFS-расписания для Ниша нет, поэтому показываем трассы и списки остановок — '
              'точное время уточняйте в автобусе или в киосках Niš-Ekspres.',
        'bg': '<strong>ЈГП Ниш-Експрес</strong> управлява градския транспорт в Ниш и околността. Мрежата обхваща около 50 автобусни линии, покриващи Ниш и крайградските квартали — от Медошевац и Бубан на запад до Долно Меджурово и Червен кръст на изток. Няма трамвайна или тролейбусна система. GTFS разписание за Ниш не е публично достъпно, затова показваме маршрути и списъци със спирки, а за точното време на тръгване препоръчваме проверка във возилото или на павилионите на Ниш-Експрес.',
    },
    'city_transport.intro_nis_p2': {
        'sr': 'Karte se kupuju u vozilu kod vozača (jednokratna vožnja oko 50 RSD) ili na mesečnim karticama Niš-Ekspresa za đake, studente i penzionere. '
              'Niš je i važno čvorište za <a href="{prefix}/rute/">međugradske i međunarodne autobuske linije</a> ka Skoplju, Sofiji, Istanbulu i drugim evropskim gradovima — '
              'polaze sa Autobuske stanice Niš. Železnica Srbije (Srbija Voz) takođe opslužuje Niš preko linija ka Beogradu, Preševu (granica sa Severnom Makedonijom) i Pirotu.',
        'en': 'Tickets are bought on-board from the driver (single ride ~50 RSD) or via monthly Niš-Ekspres cards for pupils, students and pensioners. '
              'Niš is also a hub for <a href="{prefix}/rute/">intercity and international bus lines</a> to Skopje, Sofia, Istanbul and other European cities — '
              'departing from Niš Bus Station. Serbian Railways (Srbija Voz) also serves Niš via lines to Belgrade, Preševo (North Macedonia border) and Pirot.',
        'ru': 'Билеты — у водителя (одна поездка ~50 RSD) или по месячным картам Niš-Ekspres для школьников, студентов и пенсионеров. '
              'Ниш — важный узел <a href="{prefix}/rute/">междугородних и международных автобусных линий</a>: Скопье, София, Стамбул и др. — с автовокзала Ниша. '
              'Железные дороги Сербии (Srbija Voz) — линии на Белград, Прешево (граница с С. Македонией) и Пирот.',
        'bg': 'Билетите се купуват във возилото при водача (еднократно пътуване около 50 RSD) или чрез месечни карти на Ниш-Експрес за ученици, студенти и пенсионери. Ниш е и важен възел за <a href="{prefix}/rute/">междуградски и международни автобусни линии</a> към Скопие, София, Истанбул и други европейски градове — с тръгване от автогара Ниш. Железниците на Сърбия (Сърбия Воз) също обслужват Ниш чрез линии към Белград, Прешево (границата със Северна Македония) и Пирот.',
    },
    'city_transport.intro_kragujevac_p1': {
        'sr': '<strong>Kragujevac</strong>, četvrti po veličini grad Srbije i istorijska prestonica (1818–1841), '
              'ima kompaktnu autobusku mrežu od 23 linije koja pokriva centar i okolna naselja (Stanovo, Aerodrom, Pivara, Belošavac, Bubanj). '
              'Za Kragujevac prikazujemo trase i spiskove stajališta dobijene iz OSM/Overpass podataka; '
              'tačan GTFS raspored nije javno dostupan, pa za vreme polazaka preporučujemo proveru na stajalištima ili kod prevoznika.',
        'en': '<strong>Kragujevac</strong>, Serbia\'s fourth-largest city and former capital (1818–1841), '
              'has a compact 23-line bus network covering the centre and surrounding settlements (Stanovo, Aerodrom, Pivara, Belošavac, Bubanj). '
              'For Kragujevac we show routes and stop lists built from OSM/Overpass data; '
              'a public GTFS schedule is not available, so check departure times at the stops or with the carrier.',
        'ru': '<strong>Крагуевац</strong> — четвёртый по величине город Сербии и бывшая столица (1818–1841) — '
              'имеет компактную сеть из 23 автобусных линий: центр и пригороды (Станово, Аэродром, Пивара, Белошавац, Бубань). '
              'Показываем трассы и списки остановок по данным OSM/Overpass; '
              'публичного GTFS-расписания нет — время рейсов уточняйте на остановках или у перевозчика.',
        'bg': '<strong>Крагуевац</strong>, четвъртият по големина град в Сърбия и историческа столица (1818–1841), разполага с компактна автобусна мрежа от 23 линии, обхващаща центъра и околните квартали (Станово, Аеродром, Пивара, Белошавац, Бубан). За Крагуевац показваме маршрути и списъци със спирки, получени от данните на OSM/Overpass; точно GTFS разписание не е публично достъпно, затова за времето на тръгванията препоръчваме проверка на спирките или при превозвача.',
    },
    'city_transport.intro_kragujevac_p2': {
        'sr': 'Karte se kupuju u autobusu kod vozača, a za đake i studente postoje povlašćene mesečne karte. '
              'Kragujevac je odlično povezan sa Beogradom (preko 20 polazaka dnevno) i Kraljevom; '
              'pretraga <a href="{prefix}/rute/">svih međugradskih linija</a> vam pomaže da nađete najbolji polazak za svaki dan. '
              'Autobuska stanica Kragujevac nalazi se u centru grada, blizu železničke stanice koja je takođe povezana sa Beogradom i Lapovom.',
        'en': 'Tickets are bought on-board from the driver, with discounted monthly cards for pupils and students. '
              'Kragujevac is well-connected with Belgrade (20+ daily departures) and Kraljevo; '
              'search <a href="{prefix}/rute/">all intercity routes</a> to find the best departure for any day. '
              'Kragujevac Bus Station is in the city centre, near the railway station linked to Belgrade and Lapovo.',
        'ru': 'Билеты — у водителя, для учеников и студентов — скидочные месячные проездные. '
              'Крагуевац хорошо связан с Белградом (20+ рейсов в день) и Кралево; '
              'ищите <a href="{prefix}/rute/">все междугородние маршруты</a> для подбора оптимального рейса. '
              'Автовокзал в центре города, рядом с ж/д станцией, которая связана с Белградом и Лапово.',
        'bg': 'Билетите се купуват в автобуса при водача, а за ученици и студенти има преференциални месечни карти. Крагуевац е отлично свързан с Белград (над 20 тръгвания дневно) и Кралево; търсенето на <a href="{prefix}/rute/">всички междуградски линии</a> ви помага да намерите най-добрия курс за всеки ден. Автогара Крагуевац се намира в центъра на града, близо до железопътната гара, която също е свързана с Белград и Лапово.',
    },
    # Generic city-transport intro — fallback for cities without a hand-written
    # block (Montenegro: Podgorica, Herceg Novi, Budva). Honest about the data:
    # lines + stops + map from OpenStreetMap, no per-departure timetable.
    'city_transport.intro_generic_p1': {
        'sr': 'Gradski prevoz u {city} — sve autobuske linije, stajališta i trase na jednom mestu. '
              'Za svaku liniju prikazujemo redosled stajališta i trasu na mapi, pa lako vidiš kuda ide i gde da uđeš. '
              'Izaberi liniju ili stajalište ispod.',
        'en': 'City transport in {city} — all bus lines, stops and routes in one place. '
              'For each line we show the stop sequence and the route on the map, so you can see where it goes and where to board. '
              'Pick a line or stop below.',
        'ru': 'Городской транспорт в {city} — все автобусные линии, остановки и трассы в одном месте. '
              'Для каждой линии показываем последовательность остановок и трассу на карте — видно, куда идёт и где сесть. '
              'Выбери линию или остановку ниже.',
        'bg': 'Градски транспорт в {city} — всички автобусни линии, спирки и маршрути на едно място. За всяка линия показваме реда на спирките и маршрута на картата, за да виждате лесно накъде отива и къде да се качите. Изберете линия или спирка по-долу.',
    },
    'city_transport.intro_generic_p2': {
        'sr': 'Podaci o linijama i stajalištima dolaze iz OpenStreetMap zajednice i redovno se osvežavaju. '
              'Otvori stajalište da vidiš koje linije tu staju. '
              'Za međugradski prevoz pogledaj <a href="{prefix}/rute/">sve rute</a>.',
        'en': 'Line and stop data comes from the OpenStreetMap community and is refreshed regularly. '
              'Open a stop to see which lines call there. '
              'For intercity travel, browse <a href="{prefix}/rute/">all routes</a>.',
        'ru': 'Данные о линиях и остановках берутся из сообщества OpenStreetMap и регулярно обновляются. '
              'Открой остановку, чтобы увидеть, какие линии там останавливаются. '
              'Для междугородних поездок смотри <a href="{prefix}/rute/">все маршруты</a>.',
        'bg': 'Данните за линиите и спирките идват от общността на OpenStreetMap и се обновяват редовно. Отворете спирка, за да видите кои линии спират там. За междуградски транспорт вижте <a href="{prefix}/rute/">всички маршрути</a>.',
    },
    'city_transport.faq_heading': {
        'sr': 'Često postavljana pitanja',
        'en': 'Frequently asked questions',
        'ru': 'Частые вопросы',
        'bg': 'Често задавани въпроси',
    },
    'city_transport.faq_q1': {
        'sr': 'Kako da kupim kartu za gradski prevoz u {city}u?',
        'en': 'How do I buy a transit ticket in {city}?',
        'ru': 'Как купить билет на городской транспорт в {city}?',
        'bg': 'Как да купя билет за градския транспорт в {city}?',
    },
    'city_transport.faq_q2': {
        'sr': 'Koliko linija opslužuje {city}?',
        'en': 'How many lines serve {city}?',
        'ru': 'Сколько линий обслуживает {city}?',
        'bg': 'Колко линии обслужват {city}?',
    },
    'city_transport.faq_a2': {
        'sr': 'U mreži ima {n} aktivnih linija, sa ukupno {stops} stajališta mapiranih u našoj bazi. '
              'Brojevi linija prikazuju se sa filterom po tipu (autobus, tramvaj, trolejbus, noćna) u vrhu stranice.',
        'en': '{n} active lines serve the city, with {stops} stops mapped in our database. '
              'Lines are filterable by type (bus, tram, trolleybus, night) at the top of the page.',
        'ru': 'Сеть включает {n} активных линий и {stops} остановок в нашей базе. '
              'Линии можно фильтровать по типу (автобус, трамвай, троллейбус, ночная) вверху страницы.',
        'bg': 'В мрежата има {n} активни линии, с общо {stops} спирки, картографирани в нашата база данни. Номерата на линиите се показват с филтър по тип (автобус, трамвай, тролейбус, нощна) в горната част на страницата.',
    },
    'city_transport.faq_q3': {
        'sr': 'Radi li gradski prevoz nedeljom i praznikom?',
        'en': 'Does transit run on Sundays and holidays?',
        'ru': 'Работает ли транспорт по воскресеньям и праздникам?',
        'bg': 'Работи ли градският транспорт в неделя и на празници?',
    },
    'city_transport.faq_a3': {
        'sr': 'Da, većina linija saobraća sedam dana u nedelji, sa smanjenom frekvencijom subotom i nedeljom. '
              'Raspored vidite u rubrici „Subota" i „Nedelja" na stranici svake linije. Državnim praznicima obično se primenjuje nedeljni raspored.',
        'en': 'Yes, most lines run seven days a week with reduced weekend frequency. '
              'The schedule is split into Saturday and Sunday tabs on each line page. On public holidays the Sunday schedule typically applies.',
        'ru': 'Да, большинство линий работают 7 дней в неделю с сокращённой частотой по выходным. '
              'Расписание в табах «Субота» и «Недеља» на странице каждой линии. В госпраздники обычно действует воскресное расписание.',
        'bg': 'Да, повечето линии се движат седем дни в седмицата, с намалена честота в събота и неделя. Разписанието можете да видите в раздела „Събота“ и „Неделя“ на страницата на всяка линия. В държавни празници обикновено се прилага неделно разписание.',
    },
    'city_transport.faq_q4': {
        'sr': 'Kako stižem iz {city}a u druge gradove Srbije?',
        'en': 'How do I get from {city} to other cities in Serbia?',
        'ru': 'Как добраться из {city} в другие города Сербии?',
        'bg': 'Как да стигна от {city} до други градове в Сърбия?',
    },
    'city_transport.faq_a4': {
        'sr': 'Za međugradski prevoz koristite našu stranicu <a href="{prefix}/rute/">svih ruta</a> ili direktno tražite polazak preko '
              '<a rel="nofollow" href="{prefix}/pretraga/?od={city}">polazaka iz {city}a</a>. Prikazujemo autobuske i železničke rute sa cenom, trajanjem i brojem polazaka.',
        'en': 'For intercity travel use the <a href="{prefix}/rute/">all-routes page</a> or search directly via '
              '<a rel="nofollow" href="{prefix}/pretraga/?od={city}">departures from {city}</a>. We show bus and train routes with price, duration and departure count.',
        'ru': 'Для междугородних поездок используйте <a href="{prefix}/rute/">страницу всех маршрутов</a> или ищите напрямую через '
              '<a rel="nofollow" href="{prefix}/pretraga/?od={city}">рейсы из {city}</a>. Показываем автобусные и ж/д маршруты с ценой, временем и количеством рейсов.',
        'bg': 'За междуградски транспорт използвайте нашата страница <a href="{prefix}/rute/">всички маршрути</a> или потърсете директно тръгване чрез <a rel="nofollow" href="{prefix}/pretraga/?od={city}">тръгванията от {city}</a>. Показваме автобусни и железопътни маршрути с цена, продължителност и брой тръгвания.',
    },

    # ── Hub SEO intros & FAQ: carriers_index (/prevoznici/) ──
    'carriers.intro_h': {
        'sr': 'Autobuski i železnički prevoznici u Srbiji',
        'en': 'Bus and rail carriers in Serbia',
        'ru': 'Автобусные и железнодорожные перевозчики Сербии',
    },
    'carriers.intro_p1': {
        'sr': 'U Srbiji posluje više desetina autobuskih i železničkih prevoznika, od velikih nacionalnih operatera kao što su '
              '<strong>Lasta</strong> (najveći operater u zemlji sa bazom u Beogradu), '
              '<strong>Niš-Ekspres</strong> (lider na jugu Srbije), '
              '<strong>Srbija Voz</strong> (državna železnica) do malih lokalnih firmi koje povezuju udaljena mesta sa najbližim gradskim čvorištima. '
              'Međunarodni prevoznici poput <strong>OZLEM</strong>, <strong>GEA Tours</strong> i <strong>FUDEKS</strong> '
              'opslužuju linije ka Turskoj, Bugarskoj, Severnoj Makedoniji, Austriji, Nemačkoj, Mađarskoj i Crnoj Gori. '
              'Na Prevozni.com imamo preko 66 operatera sa 517 aktivnih linija — za svakog prikazujemo listu ruta, povezanih gradova i, kada je dostupno, zvanični sajt.',
        'en': 'Serbia is served by dozens of bus and rail carriers — from large national operators such as '
              '<strong>Lasta</strong> (the biggest carrier, based in Belgrade), '
              '<strong>Niš-Ekspres</strong> (leading in southern Serbia), '
              '<strong>Srbija Voz</strong> (state railway) — down to small local companies linking outlying towns to the nearest city hub. '
              'International carriers like <strong>OZLEM</strong>, <strong>GEA Tours</strong> and <strong>FUDEKS</strong> '
              'serve lines to Turkey, Bulgaria, North Macedonia, Austria, Germany, Hungary and Montenegro. '
              'Prevozni.com lists 66+ operators with 517 active lines — for each one we show the route list, cities served and, when available, the official site.',
        'ru': 'В Сербии работают десятки автобусных и ж/д перевозчиков — от крупных национальных операторов, таких как '
              '<strong>Lasta</strong> (крупнейший перевозчик, база в Белграде), '
              '<strong>Niš-Ekspres</strong> (лидер на юге Сербии), '
              '<strong>Srbija Voz</strong> (гос. ж/д), до мелких местных компаний, соединяющих отдалённые города с ближайшими узлами. '
              'Международные перевозчики <strong>OZLEM</strong>, <strong>GEA Tours</strong>, <strong>FUDEKS</strong> — '
              'линии в Турцию, Болгарию, С. Македонию, Австрию, Германию, Венгрию и Черногорию. '
              'На Prevozni.com — 66+ операторов и 517 активных линий; по каждому — список маршрутов, города обслуживания и, где доступно, официальный сайт.',
    },
    'carriers.intro_p2': {
        'sr': 'Prevoznici su sortirani po broju linija koje opslužuju, tako da su na vrhu stranice najveći operateri. '
              'Klikom na ime prevoznika dobijate listu svih njegovih ruta sa direktnim linkovima na stranice pojedinačnih linija '
              '(npr. <a href="{prefix}/rute/">pregled svih ruta</a>). '
              'Ukoliko ne znate pouzdano koji prevoznik vam odgovara, preporučujemo da krenete od odredišta: izaberite rutu (npr. '
              '<a href="{prefix}/voznja/beograd-do-budva/">Beograd — Budva</a>) i pogledajte polaske sortirane po ceni i vremenu — '
              'tu ćete videti koji operater nudi najbolju opciju za vaš termin. Za gradski prevoz svakog grada (GSP, JGSP, Niš-Ekspres) '
              'posetite <a href="{prefix}/gradski/">stranicu gradskog prevoza</a>.',
        'en': 'Carriers are sorted by number of routes served, so the biggest operators appear first. '
              'Clicking a carrier name opens a list of its routes with direct links to individual line pages '
              '(for example <a href="{prefix}/rute/">all routes</a>). '
              'If you\'re not sure which carrier suits you, start from the destination: pick a route (e.g. '
              '<a href="{prefix}/voznja/beograd-do-budva/">Belgrade — Budva</a>) and sort departures by price and time — '
              'you\'ll see which operator offers the best option for your schedule. For city transit (GSP, JGSP, Niš-Ekspres) '
              'visit the <a href="{prefix}/gradski/">city transit page</a>.',
        'ru': 'Перевозчики отсортированы по числу маршрутов, так что крупнейшие — сверху. '
              'При клике на имя перевозчика открывается список его маршрутов с прямыми ссылками на страницы линий '
              '(например <a href="{prefix}/rute/">все маршруты</a>). '
              'Если не уверены, какой перевозчик подходит, начните с направления: выберите маршрут (например '
              '<a href="{prefix}/voznja/beograd-do-budva/">Белград — Будва</a>), отсортируйте рейсы по цене и времени — '
              'увидите лучший вариант. Для городского транспорта (GSP, JGSP, Niš-Ekspres) — '
              '<a href="{prefix}/gradski/">страница городского транспорта</a>.',
    },
    'carriers.faq_heading': {
        'sr': 'Česta pitanja o prevoznicima',
        'en': 'Frequently asked questions about carriers',
        'ru': 'Частые вопросы о перевозчиках',
    },
    'carriers.faq_q1': {
        'sr': 'Koji je najveći autobuski prevoznik u Srbiji?',
        'en': 'Which is the largest bus carrier in Serbia?',
        'ru': 'Кто крупнейший автобусный перевозчик Сербии?',
    },
    'carriers.faq_a1': {
        'sr': 'Najveći operater je Lasta sa bazom u Beogradu — opslužuje preko 200 domaćih i međunarodnih linija. '
              'Niš-Ekspres dominira na jugu zemlje, dok je Srbija Voz jedini železnički operater. '
              'Kompletna lista prevoznika sa brojem linija i povezanim gradovima dostupna je na ovoj stranici.',
        'en': 'The largest operator is Lasta, based in Belgrade — serving 200+ domestic and international routes. '
              'Niš-Ekspres dominates the south, while Srbija Voz is the sole rail operator. '
              'A complete list of carriers with route counts and cities served is on this page.',
        'ru': 'Крупнейший оператор — Lasta (база в Белграде) — более 200 внутренних и международных маршрутов. '
              'Niš-Ekspres лидирует на юге, а Srbija Voz — единственный ж/д оператор. '
              'Полный список с числом маршрутов и городами — на этой странице.',
    },
    'carriers.faq_q2': {
        'sr': 'Kako da uporedim cene između različitih prevoznika?',
        'en': 'How do I compare prices between carriers?',
        'ru': 'Как сравнить цены между перевозчиками?',
    },
    'carriers.faq_a2': {
        'sr': 'Otvorite stranicu rute (npr. <a href="{prefix}/rute/">katalog ruta</a>) i pogledajte kolonu cene za svaki polazak — '
              'pored cene je naveden i prevoznik, tako da je lako uporediti. SEO parne stranice /voznja/grad1-do-grad2/ dodatno prikazuju raspon cena i najjeftinijeg operatera.',
        'en': 'Open a route page (e.g. the <a href="{prefix}/rute/">route catalog</a>) and check the price column — '
              'each departure shows the operator alongside the price. SEO city-pair pages at /voznja/city1-do-city2/ additionally show the price range and the cheapest operator.',
        'ru': 'Откройте страницу маршрута (например <a href="{prefix}/rute/">каталог маршрутов</a>) и смотрите столбец цены — '
              'рядом с ценой указан перевозчик. SEO-страницы пар /voznja/gorod1-do-gorod2/ также показывают диапазон цен и самого дешёвого оператора.',
    },
    'carriers.faq_q3': {
        'sr': 'Da li su podaci o prevoznicima zvanični?',
        'en': 'Is the carrier data official?',
        'ru': 'Официальные ли данные о перевозчиках?',
    },
    'carriers.faq_a3': {
        'sr': 'Podaci se dobijaju automatski iz javnih izvora (busticket4.me, polazak.rs, srbijavoz.rs) i agregiraju nekoliko puta dnevno. '
              'Nismo zvanični partner prevoznika — za rezervaciju mesta ili specifične uslove prevoza savetujemo posetu zvaničnog sajta operatera (link je na svakoj kartici).',
        'en': 'Data is pulled automatically from public sources (busticket4.me, polazak.rs, srbijavoz.rs) and aggregated several times a day. '
              'We are not an official carrier partner — for reservations or specific travel conditions please visit the carrier\'s official site (link on each card).',
        'ru': 'Данные автоматически собираются из публичных источников (busticket4.me, polazak.rs, srbijavoz.rs) и агрегируются несколько раз в день. '
              'Мы не являемся официальным партнёром перевозчиков — для бронирования или уточнения условий посетите официальный сайт оператора (ссылка на каждой карточке).',
    },

    # ── Hub SEO intros & FAQ: stations_index (/autobuske-stanice/) ──
    'stations.intro_h': {
        'sr': 'Autobuske i železničke stanice u Srbiji',
        'en': 'Bus and train stations in Serbia',
        'ru': 'Автобусные и железнодорожные станции Сербии',
    },
    'stations.intro_p1': {
        'sr': 'Glavne čvorne stanice Srbije — autobuske i železničke — povezuju preko 100 gradova i 66 prevoznika u jedinstvenu mrežu. '
              '<strong>Beogradska autobuska stanica (BAS)</strong> na Novom Beogradu je najveće čvorište u zemlji, sa preko 2000 dnevnih polazaka ka svim delovima Srbije i Evrope. '
              '<strong>Centralna železnička stanica Beograd Centar (Prokop)</strong> je glavni železnički čvor od 2018. — polazak za Novi Sad, Subotice, Niš i međunarodne pravce. '
              'Tu su i druga važna čvorišta: <strong>Autobuska stanica Novi Sad</strong>, <strong>Autobuska stanica Niš</strong>, '
              '<strong>Autobuska stanica Subotica</strong> (granica sa Mađarskom), <strong>Prijepolje</strong> i <strong>Užice</strong> za linije ka Crnoj Gori i BiH.',
        'en': 'Serbia\'s main hub stations — bus and rail — connect 100+ cities and 66 carriers into a single network. '
              '<strong>Belgrade Bus Station (BAS)</strong> in Novi Beograd is the country\'s largest hub, with 2,000+ daily departures across Serbia and Europe. '
              '<strong>Belgrade Centar (Prokop)</strong> is the country\'s main railway hub since 2018 — departures to Novi Sad, Subotica, Niš and international destinations. '
              'Other key hubs: <strong>Novi Sad Bus Station</strong>, <strong>Niš Bus Station</strong>, '
              '<strong>Subotica Bus Station</strong> (Hungarian border), and <strong>Prijepolje</strong> / <strong>Užice</strong> for lines to Montenegro and Bosnia.',
        'ru': 'Главные узловые станции Сербии — автобусные и ж/д — связывают 100+ городов и 66 перевозчиков в единую сеть. '
              '<strong>Белградский автовокзал (BAS)</strong> в Новом Белграде — крупнейший узел страны, 2000+ рейсов в сутки по всей Сербии и Европе. '
              '<strong>Белград Центар (Прокоп)</strong> — главный ж/д узел с 2018 года: рейсы в Нови-Сад, Суботицу, Ниш и международные направления. '
              'Другие важные узлы: <strong>автовокзал Нови-Сада</strong>, <strong>автовокзал Ниша</strong>, '
              '<strong>автовокзал Суботицы</strong> (граница с Венгрией), <strong>Приеполе</strong> и <strong>Ужице</strong> — линии в Черногорию и БиГ.',
    },
    'stations.intro_p2': {
        'sr': 'Za svaku stanicu prikazujemo grad, tip (autobuska / železnička) i broj ruta koje polaze sa nje. '
              'Ukupno u bazi imamo desetke stanica grupisanih po gradovima — pogledajte <a href="{prefix}/rute/">katalog međugradskih ruta</a> '
              'ili direktno otvorite stranicu nekog od ključnih gradova, npr. <a href="{prefix}/voznja/beograd-do-novi-sad/">Beograd — Novi Sad</a> '
              'ili <a href="{prefix}/voznja/beograd-do-budva/">Beograd — Budva</a>. '
              'Na stanicama se karte kupuju na blagajnama ili kod vozača u vozilu; u Beogradu i Novom Sadu su blagajne otvorene od 05:00 do 23:00, '
              'sa radom tokom noći na glavnim međunarodnim polazcima. Stanice u manjim mestima često nemaju noćnu smenu — preporučujemo kupovinu karte unapred.',
        'en': 'For every station we show the city, type (bus / rail) and the number of routes departing from it. '
              'The database holds dozens of stations grouped by city — browse the <a href="{prefix}/rute/">intercity route catalog</a> '
              'or jump to a key city pair directly, e.g. <a href="{prefix}/voznja/beograd-do-novi-sad/">Belgrade — Novi Sad</a> '
              'or <a href="{prefix}/voznja/beograd-do-budva/">Belgrade — Budva</a>. '
              'Tickets are sold at station counters or on-board from the driver; in Belgrade and Novi Sad counters are open 05:00–23:00, '
              'with overnight service on major international departures. Smaller stations often lack a night shift — buy your ticket in advance.',
        'ru': 'По каждой станции показываем город, тип (автобусная / ж/д) и количество маршрутов отправления. '
              'В базе — десятки станций, сгруппированных по городам. Смотрите <a href="{prefix}/rute/">каталог междугородних маршрутов</a> '
              'или переходите сразу к ключевой паре, например <a href="{prefix}/voznja/beograd-do-novi-sad/">Белград — Нови-Сад</a> '
              'или <a href="{prefix}/voznja/beograd-do-budva/">Белград — Будва</a>. '
              'Билеты продаются в кассах или у водителя; в Белграде и Нови-Саде кассы работают 05:00–23:00, '
              'с ночными окнами на крупных международных рейсах. В малых городах ночной смены часто нет — покупайте билет заранее.',
    },
    'stations.faq_heading': {
        'sr': 'Često postavljana pitanja o stanicama',
        'en': 'Frequently asked questions about stations',
        'ru': 'Частые вопросы о станциях',
    },
    'stations.faq_q1': {
        'sr': 'Gde se nalazi glavna autobuska stanica u Beogradu?',
        'en': 'Where is Belgrade\'s main bus station?',
        'ru': 'Где находится главный автовокзал Белграда?',
    },
    'stations.faq_a1': {
        'sr': 'Glavna BAS (Beogradska autobuska stanica) nalazi se u Novom Beogradu, Blok 42, odmah pored železničke stanice Beograd Centar (Prokop). '
              'Od centra grada do nje se stiže linijama gradskog autobusa 78, 95 i E9 za oko 15 minuta. '
              'Stara stanica BAS na Savamali zatvorena je 2019. godine.',
        'en': 'The main BAS (Belgrade Bus Station) is in Novi Beograd, Block 42, next to Belgrade Centar railway station (Prokop). '
              'From the city centre it\'s reachable by city buses 78, 95 or E9 in about 15 minutes. '
              'The old BAS in Savamala closed in 2019.',
        'ru': 'Главный BAS (Белградский автовокзал) — в Новом Белграде, Блок 42, рядом с ж/д вокзалом Београд Центар (Прокоп). '
              'Из центра — городскими автобусами 78, 95 или E9 за ~15 минут. '
              'Старый автовокзал BAS в Савамале закрыт в 2019 году.',
    },
    'stations.faq_q2': {
        'sr': 'Mogu li da kupim kartu na stanici ili samo online?',
        'en': 'Can I buy a ticket at the station or only online?',
        'ru': 'Можно ли купить билет на станции или только онлайн?',
    },
    'stations.faq_a2': {
        'sr': 'Karte se uvek mogu kupiti na blagajni autobuske ili železničke stanice, bez dodatnih taksi. '
              'Online kupovina preko partnerskih sajtova ponekad nudi popust ili bržu rezervaciju mesta, naročito za popularne linije tokom letnje sezone ili praznika. '
              'Za međugradske linije tokom leta preporučujemo kupovinu 2–3 dana unapred.',
        'en': 'Tickets are always sold at bus and train station counters, with no booking fees. '
              'Online purchase via partner sites sometimes offers a discount or faster seat reservation, especially for popular routes in summer and around holidays. '
              'For intercity lines in summer we recommend buying 2–3 days in advance.',
        'ru': 'Билеты всегда можно купить в кассах автовокзала или ж/д вокзала без дополнительных сборов. '
              'Онлайн-покупка через партнёров иногда даёт скидку или быстрое бронирование места, особенно на популярных рейсах летом и в праздники. '
              'Для междугородних рейсов летом советуем покупать билет за 2–3 дня.',
    },
    'stations.faq_q3': {
        'sr': 'Koja je najbliža međunarodna stanica u Srbiji?',
        'en': 'What is Serbia\'s closest international station?',
        'ru': 'Какая ближайшая международная станция в Сербии?',
    },
    'stations.faq_a3': {
        'sr': 'Zavisi od pravca putovanja: Subotica za Mađarsku, Dimitrovgrad za Bugarsku, Preševo za Severnu Makedoniju, '
              'Priboj ili Užice za Bosnu i Hercegovinu, Prijepolje ili Novi Pazar za Crnu Goru. '
              'Beogradski BAS takođe opslužuje najviše međunarodnih linija, uključujući direktne polaske ka Istanbulu, Beču, Minhenu, Frankfurtu i Zurich-u.',
        'en': 'It depends on direction: Subotica for Hungary, Dimitrovgrad for Bulgaria, Preševo for North Macedonia, '
              'Priboj or Užice for Bosnia, Prijepolje or Novi Pazar for Montenegro. '
              'Belgrade BAS also handles the most international lines, including direct departures to Istanbul, Vienna, Munich, Frankfurt and Zurich.',
        'ru': 'Зависит от направления: Суботица — в Венгрию, Димитровград — в Болгарию, Прешево — в С. Македонию, '
              'Прибой или Ужице — в БиГ, Приеполе или Нови-Пазар — в Черногорию. '
              'BAS Белграда также имеет больше всего международных рейсов, включая прямые на Стамбул, Вену, Мюнхен, Франкфурт и Цюрих.',
    },

    # ── Hub SEO intros & FAQ: destinations (/destinacije/) ──
    'dest.intro_h': {
        'sr': 'Popularne destinacije iz Srbije',
        'en': 'Popular destinations from Serbia',
        'ru': 'Популярные направления из Сербии',
    },
    'dest.intro_p1': {
        'sr': 'Sa centralnim položajem na Balkanu, Srbija je odlična polazna tačka za putovanja autobusom ili vozom ka glavnim turističkim i poslovnim centrima regiona. '
              'Letnji pravci ka <strong>Crnogorskom primorju</strong> (Budva, Herceg Novi, Kotor, Bar, Tivat, Ulcinj) imaju pojačane polaske tokom juna–septembra, '
              'sa noćnim autobusima iz Beograda koji stižu ujutru na obalu. '
              'Gradovi bivše Jugoslavije — <strong>Sarajevo, Mostar, Banja Luka, Zagreb, Split, Dubrovnik, Ljubljana, Skoplje, Bitola</strong> — '
              'su dostupni direktnim autobuskim linijama, sa putovanjem od 4 do 10 sati. '
              'Centralnoevropski pravci (<strong>Budimpešta, Beč, Minhen, Frankfurt, Prag</strong>) imaju dnevne i noćne autobuske rute sa Beogradske autobuske stanice, '
              'a za Tursku (<strong>Istanbul</strong>) polazi direktan autobus iz Beograda i Niša.',
        'en': 'With its central Balkan location, Serbia is a superb starting point for bus and rail travel to the region\'s main tourism and business hubs. '
              'Summer routes to the <strong>Montenegrin coast</strong> (Budva, Herceg Novi, Kotor, Bar, Tivat, Ulcinj) run on increased frequency June–September, '
              'with overnight buses from Belgrade arriving on the coast by morning. '
              'Former-Yugoslavia cities — <strong>Sarajevo, Mostar, Banja Luka, Zagreb, Split, Dubrovnik, Ljubljana, Skopje, Bitola</strong> — '
              'are reachable by direct bus lines, with journeys of 4–10 hours. '
              'Central-European routes (<strong>Budapest, Vienna, Munich, Frankfurt, Prague</strong>) run day and night from Belgrade Bus Station, '
              'and a direct bus to Turkey (<strong>Istanbul</strong>) departs from Belgrade and Niš.',
        'ru': 'Благодаря центральному положению на Балканах Сербия — отличная отправная точка для автобусных и ж/д поездок по региону. '
              'Летние рейсы на <strong>побережье Черногории</strong> (Будва, Херцег-Нови, Котор, Бар, Тиват, Улцинь) усилены июнь–сентябрь — '
              'ночные автобусы из Белграда приходят на побережье утром. '
              'Города бывшей Югославии — <strong>Сараево, Мостар, Баня-Лука, Загреб, Сплит, Дубровник, Любляна, Скопье, Битола</strong> — '
              'доступны прямыми автобусами, поездка 4–10 часов. '
              'Центральноевропейские направления (<strong>Будапешт, Вена, Мюнхен, Франкфурт, Прага</strong>) — дневные и ночные автобусы с BAS, '
              'в Турцию (<strong>Стамбул</strong>) прямой автобус отправляется из Белграда и Ниша.',
    },
    'dest.intro_p2': {
        'sr': 'Ispod je kratak pregled top 14 destinacija sa direktnim linkovima na stranice konkretnih ruta — '
              'za svaku destinaciju navedene su glavne polazišne tačke iz Srbije (Beograd, Novi Sad, Niš, Subotica). '
              'Za kompletan katalog međugradskih ruta posetite <a href="{prefix}/rute/">/rute/</a>, '
              'a za pretragu po imenu grada iskoristite <a href="{prefix}/pretraga/">pretragu polazaka</a>. '
              'Cene karata, broj dnevnih polazaka i prosečno trajanje putovanja prikazani su na stranici svake rute, sa mogućnošću online kupovine preko partnerskih sajtova. '
              'Savet: za letnje pravce ka obali rezervišite kartu bar 7 dana unapred, a za međunarodne linije ka Turskoj i Nemačkoj čak 14 dana — '
              'cene rastu kako se datum polaska približava, a kapacitet noćnih polazaka je ograničen.',
        'en': 'Below is a quick overview of the top 14 destinations with direct links to the route pages — '
              'each destination lists the main starting points from Serbia (Belgrade, Novi Sad, Niš, Subotica). '
              'For the full intercity catalog visit <a href="{prefix}/rute/">/rute/</a>, '
              'and for name-based search use <a href="{prefix}/pretraga/">the departures search</a>. '
              'Ticket prices, daily-departure counts and average journey time are listed on each route page, with online booking available via partner sites. '
              'Tip: for summer coastal routes book at least 7 days ahead, for international lines to Turkey and Germany as much as 14 days — '
              'prices rise as departure nears and night-bus capacity is limited.',
        'ru': 'Ниже — краткий обзор топ-14 направлений с прямыми ссылками на страницы маршрутов; '
              'у каждого направления указаны основные отправные точки в Сербии (Белград, Нови-Сад, Ниш, Суботица). '
              'Полный каталог — на <a href="{prefix}/rute/">/rute/</a>, '
              'поиск по названию города — в <a href="{prefix}/pretraga/">поиске рейсов</a>. '
              'Цены билетов, число рейсов в день и среднее время в пути — на странице каждого маршрута, с возможностью онлайн-покупки через партнёров. '
              'Совет: на летнее побережье бронируйте минимум за 7 дней, на международные рейсы в Турцию и Германию — за 14; '
              'цены растут по мере приближения даты, а ночные автобусы ограничены по вместимости.',
    },
    'dest.faq_heading': {
        'sr': 'Često postavljana pitanja',
        'en': 'Frequently asked questions',
        'ru': 'Частые вопросы',
    },
    'dest.by_country': {
        'sr': 'Po zemljama',
        'en': 'By country',
        'ru': 'По странам',
    },
    'review.prompt_aria': {
        'sr': 'Poziv da ostavite recenziju',
        'en': 'Review request',
        'ru': 'Запрос отзыва',
        'bg': 'Покана да оставите отзив',
    },
    'review.prompt_intro': {
        'sr': 'Kako je prošlo putovanje',
        'en': 'How was your trip',
        'ru': 'Как прошла поездка',
        'bg': 'Как премина пътуването',
    },
    'review.prompt_cta': {
        'sr': 'Ostavi recenziju',
        'en': 'Leave a review',
        'ru': 'Оставить отзыв',
        'bg': 'Остави отзив',
    },
    'a11y.dismiss': {
        'sr': 'Zatvori',
        'en': 'Dismiss',
        'ru': 'Закрыть',
        'bg': 'Затвори',
    },
    'dest.faq_q1': {
        'sr': 'Koliko traje putovanje autobusom od Beograda do Budve?',
        'en': 'How long is the bus ride from Belgrade to Budva?',
        'ru': 'Сколько едет автобус из Белграда в Будву?',
    },
    'dest.faq_a1': {
        'sr': 'Putovanje autobusom Beograd — Budva traje u proseku 11–12 sati, u zavisnosti od prevoznika i rute (preko Užica/Prijepolja ili Zlatibora). '
              'Noćni polasci (u 20:00–22:00) stižu u Budvu oko 07:00–09:00 ujutru, što je najpovoljniji izbor za letnju sezonu. '
              'Detalji na <a href="{prefix}/voznja/beograd-do-budva/">stranici Beograd — Budva</a>.',
        'en': 'The Belgrade — Budva bus ride averages 11–12 hours, depending on operator and routing (via Užice/Prijepolje or Zlatibor). '
              'Overnight departures (20:00–22:00) reach Budva around 07:00–09:00, the best option for summer. '
              'Details on the <a href="{prefix}/voznja/beograd-do-budva/">Belgrade — Budva page</a>.',
        'ru': 'Автобус Белград — Будва едет в среднем 11–12 часов в зависимости от перевозчика и маршрута (через Ужице/Приеполе или Златибор). '
              'Ночные рейсы (20:00–22:00) приходят в Будву ~07:00–09:00 — лучший вариант летом. '
              'Подробности на <a href="{prefix}/voznja/beograd-do-budva/">странице Белград — Будва</a>.',
    },
    'dest.faq_q2': {
        'sr': 'Treba li mi viza ili pasoš za Crnu Goru, BiH, Severnu Makedoniju?',
        'en': 'Do I need a visa or passport for Montenegro, Bosnia or North Macedonia?',
        'ru': 'Нужна ли виза или паспорт для Черногории, БиГ или С. Македонии?',
    },
    'dest.faq_a2': {
        'sr': 'Građani Srbije mogu da putuju sa ličnom kartom u Crnu Goru, Bosnu i Hercegovinu, Severnu Makedoniju i Albaniju — bez pasoša. '
              'Za Hrvatsku (članica Šengena od 2023.) potreban je pasoš ili lična karta u zavisnosti od dokumenta. '
              'Za zemlje EU van Šengena i Tursku preporučujemo pasoš sa važenjem od najmanje 6 meseci od datuma ulaska.',
        'en': 'Serbian citizens can travel with a national ID to Montenegro, Bosnia and Herzegovina, North Macedonia and Albania — no passport required. '
              'For Croatia (in Schengen since 2023) a passport or national ID is needed depending on the document. '
              'For non-Schengen EU countries and Turkey, carry a passport valid at least 6 months from the entry date.',
        'ru': 'Граждане Сербии могут ездить по внутреннему ID в Черногорию, Боснию и Герцеговину, С. Македонию и Албанию — без загранпаспорта. '
              'Для Хорватии (в Шенгене с 2023) нужен паспорт или ID в зависимости от документа. '
              'В страны ЕС вне Шенгена и Турцию — заграничный паспорт со сроком действия не менее 6 месяцев.',
    },
    'dest.faq_q3': {
        'sr': 'Koja destinacija ima najjeftiniji autobuski polazak iz Beograda?',
        'en': 'Which destination has the cheapest bus from Belgrade?',
        'ru': 'В какое направление самый дешёвый автобус из Белграда?',
    },
    'dest.faq_a3': {
        'sr': 'Za blize destinacije cene počinju od oko 10€: Novi Sad, Niš, Subotica, Kragujevac. '
              'Za regionalne destinacije najpovoljnije su Sarajevo, Skoplje i Banja Luka (20–30€). '
              'Letnji polasci na crnogorsko primorje mogu biti skuplji (30–45€) zbog veće tražnje — bukiranje unapred je ključno za niže cene.',
        'en': 'Nearby destinations start around €10: Novi Sad, Niš, Subotica, Kragujevac. '
              'In the region, the best-value are Sarajevo, Skopje and Banja Luka (€20–30). '
              'Summer coastal runs to Montenegro can cost €30–45 due to high demand — early booking matters for lower fares.',
        'ru': 'Ближние направления — от ~10€: Нови-Сад, Ниш, Суботица, Крагуевац. '
              'Из региональных выгоднее всего Сараево, Скопье и Баня-Лука (20–30€). '
              'Летние рейсы на побережье Черногории дороже (30–45€) из-за спроса — ранняя бронь снижает цену.',
    },
    # ── far-destination guide links (Phase 2) ──
    'dest.far_heading': {
        'sr': 'Daleke destinacije',
        'en': 'Far destinations',
        'ru': 'Дальние направления',
    },
    'dest.far_sub': {
        'sr': 'Vodiči korak po korak za putovanja van Evrope — prevoz do aerodroma, let i lokalni transfer na cilju.',
        'en': 'Step-by-step guides for trips beyond Europe — transport to the airport, the flight and a local transfer at the destination.',
        'ru': 'Пошаговые гайды для поездок за пределы Европы — транспорт до аэропорта, перелёт и местный трансфер на месте.',
    },

    # ── home FAQ (only) ──
    'home.faq_heading': {
        'sr': 'Često postavljana pitanja',
        'en': 'Frequently asked questions',
        'ru': 'Частые вопросы',
        'bg': 'Често задавани въпроси',
    },
    'home.faq_q1': {
        'sr': 'Šta je Prevozni.com?',
        'en': 'What is Prevozni.com?',
        'ru': 'Что такое Prevozni.com?',
        'bg': 'Какво е Prevozni.com?',
    },
    'home.faq_a1': {
        'sr': 'Prevozni.com je besplatan agregator reda vožnje autobusa, vozova, tramvaja i trolejbusa u Srbiji. '
              'Pokrivamo gradski prevoz u Beogradu, Novom Sadu, Nišu i Kragujevcu, kao i više od 270 međugradskih i međunarodnih ruta. '
              'Nema registracije, nema reklama, podaci se ažuriraju svakodnevno iz zvaničnih izvora.',
        'en': 'Prevozni.com is a free aggregator of bus, train, tram and trolleybus schedules in Serbia. '
              'We cover city transit in Belgrade, Novi Sad, Niš and Kragujevac, plus 270+ intercity and international routes. '
              'No signup, no ads, data refreshes daily from official sources.',
        'ru': 'Prevozni.com — бесплатный агрегатор расписания автобусов, поездов, трамваев и троллейбусов Сербии. '
              'Охватываем городской транспорт Белграда, Нови-Сада, Ниша и Крагуеваца, плюс 270+ междугородних и международных маршрутов. '
              'Без регистрации, без рекламы, данные обновляются ежедневно из официальных источников.',
        'bg': 'Prevozni.com е безплатен агрегатор на разписания на автобуси, влакове, трамваи и тролейбуси в Сърбия. Обхващаме градския транспорт в Белград, Нови Сад, Ниш и Крагуевац, плюс над 270 междуградски и международни маршрута. Без регистрация, без реклами, данните се обновяват ежедневно от официални източници.',
    },
    'home.faq_q2': {
        'sr': 'Koje gradove i rute pokriva sajt?',
        'en': 'Which cities and routes does the site cover?',
        'ru': 'Какие города и маршруты покрывает сайт?',
        'bg': 'Кои градове и маршрути покрива сайтът?',
    },
    'home.faq_a2': {
        'sr': 'U bazi imamo 4 grada sa detaljnim gradskim prevozom (610 linija, 3700+ stajališta) i 517 međugradskih/međunarodnih ruta '
              '(Crna Gora, BiH, Hrvatska, Mađarska, Severna Makedonija, Turska, Nemačka, Austrija i dr.). '
              'Puni pregled je na <a href="{prefix}/gradski/">stranici gradskog prevoza</a> i <a href="{prefix}/rute/">katalogu ruta</a>.',
        'en': 'The database holds 4 cities with detailed city transit (610 lines, 3,700+ stops) and 517 intercity/international routes '
              '(Montenegro, Bosnia, Croatia, Hungary, North Macedonia, Turkey, Germany, Austria and more). '
              'Full overview on the <a href="{prefix}/gradski/">city transit page</a> and <a href="{prefix}/rute/">route catalog</a>.',
        'ru': 'В базе — 4 города с подробным городским транспортом (610 линий, 3700+ остановок) и 517 междугородних/международных маршрутов '
              '(Черногория, БиГ, Хорватия, Венгрия, С. Македония, Турция, Германия, Австрия и др.). '
              'Полный обзор на <a href="{prefix}/gradski/">странице городского транспорта</a> и <a href="{prefix}/rute/">каталоге маршрутов</a>.',
        'bg': 'В базата има 4 града с подробен градски транспорт (610 линии, над 3700 спирки) и 517 междуградски/международни маршрута (Черна гора, Босна, Хърватия, Унгария, Северна Македония, Турция, Германия, Австрия и др.). Пълен преглед на <a href="{prefix}/gradski/">страницата за градски транспорт</a> и <a href="{prefix}/rute/">каталога с маршрути</a>.',
    },
    'home.faq_q3': {
        'sr': 'Da li je sajt besplatan i bez reklama?',
        'en': 'Is the site free and ad-free?',
        'ru': 'Бесплатный ли сайт и без рекламы?',
        'bg': 'Безплатен ли е сайтът и без реклами?',
    },
    'home.faq_a3': {
        'sr': 'Da, Prevozni.com je potpuno besplatan i bez registracije. Ne prikazujemo invazivne reklame i ne prodajemo vaše podatke. '
              'Posetu pratimo samo putem anonimne analitike (Umami), a projekat se izdržava povremenim affiliate provizijama kod kupovine karata preko naših partnera.',
        'en': 'Yes, Prevozni.com is fully free and no-signup. We do not display intrusive ads and do not sell your data. '
              'Visits are tracked only with anonymous analytics (Umami); the project is funded by occasional affiliate commissions when you buy tickets via our partners.',
        'ru': 'Да, Prevozni.com полностью бесплатный и без регистрации. Мы не показываем навязчивую рекламу и не продаём ваши данные. '
              'Посещения фиксируются только анонимной аналитикой (Umami); проект живёт за счёт редких партнёрских комиссий при покупке билетов через партнёров.',
        'bg': 'Да, Prevozni.com е напълно безплатен и без регистрация. Не показваме натрапчиви реклами и не продаваме вашите данни. Посещенията се проследяват само чрез анонимна аналитика (Umami); проектът се издържа от случайни партньорски комисиони при покупка на билети през нашите партньори.',
    },

    # ── Popular / "See also" blocks ──
    'city_transport.popular_routes_h': {
        'sr': 'Popularne međugradske rute iz {city}a',
        'en': 'Popular intercity routes from {city}',
        'ru': 'Популярные междугородние маршруты из {city}',
        'bg': 'Популярни междуградски маршрути от {city}',
    },
    'route_index.related_cities_h': {
        'sr': 'Otkrijte gradski prevoz',
        'en': 'Explore city transit',
        'ru': 'Изучите городской транспорт',
    },
    'stop_prose.heading': {
        'sr': 'O stajalištu {stop_name}',
        'en': 'About the {stop_name} stop',
        'ru': 'Об остановке {stop_name}',
        'bg': 'За спирка {stop_name}',
    },
    'line_prose.heading': {
        'sr': 'O liniji {number} — {city}',
        'en': 'About line {number} in {city}',
        'ru': 'О линии {number} — {city}',
        'bg': 'За линия {number} — {city}',
    },

    # ── Reviews / UGC ──
    'review.heading': {
        'sr': 'Iskustva putnika', 'en': 'Traveller reviews', 'ru': 'Отзывы пассажиров',
        'bg': 'Впечатления на пътниците',
    },
    'review.summary_empty': {
        'sr': 'Budite prvi koji ostavlja recenziju za ovu rutu.',
        'en': 'Be the first to review this route.',
        'ru': 'Будьте первым, кто оставит отзыв о маршруте.',
        'bg': 'Бъдете първият, който оставя отзив за този маршрут.',
    },
    'review.summary_few': {
        'sr': '{n} ocena, prosek {avg} ★ · podelite i vaše iskustvo',
        'en': '{n} ratings, average {avg} ★ · share your experience too',
        'ru': '{n} оценок, средняя {avg} ★ · поделитесь своим опытом',
        'bg': '{n} оценки, средно {avg} ★ · споделете и вашето впечатление',
    },
    'review.summary': {
        'sr': '{n} ocena · prosek {avg} ★',
        'en': '{n} ratings · average {avg} ★',
        'ru': '{n} оценок · средняя {avg} ★',
        'bg': '{n} оценки · средно {avg} ★',
    },
    'review.form_heading': {
        'sr': 'Ostavite vašu recenziju', 'en': 'Leave your review', 'ru': 'Оставить отзыв',
        'bg': 'Оставете своя отзив',
    },
    'review.cta_short': {
        'sr': 'Ostavite recenziju',
        'en': 'Write a review',
        'ru': 'Оставить отзыв',
    },
    'review.rating_label': {
        'sr': 'Ocena (1–5)', 'en': 'Rating (1–5)', 'ru': 'Оценка (1–5)',
        'bg': 'Оценка (1–5)',
    },
    'review.comment_label': {
        'sr': 'Komentar (50–500 znakova)',
        'en': 'Comment (50–500 characters)',
        'ru': 'Комментарий (50–500 символов)',
        'bg': 'Коментар (50–500 знака)',
    },
    'review.comment_ph': {
        'sr': 'Kako je bila vožnja? Komfor, tačnost, cena, osoblje, prtljag, WiFi, stajališta…',
        'en': 'How was the ride? Comfort, timekeeping, price, staff, luggage, WiFi, stops…',
        'ru': 'Как прошла поездка? Комфорт, пунктуальность, цена, персонал, багаж, WiFi, остановки…',
        'bg': 'Как мина пътуването? Комфорт, точност, цена, персонал, багаж, WiFi, спирки…',
    },
    'review.name_label': {'sr': 'Ime (2–40 slova)', 'en': 'Name (2–40 letters)', 'ru': 'Имя (2–40 букв)', 'bg': 'Име (2–40 букви)'},
    'review.email_label': {
        'sr': 'Email (opciono, za obaveštenje)',
        'en': 'Email (optional, for approval notice)',
        'ru': 'Email (необязательно, для уведомления)',
        'bg': 'Имейл (по избор, за известие)',
    },
    'review.submit': {'sr': 'Pošalji recenziju', 'en': 'Submit review', 'ru': 'Отправить отзыв', 'bg': 'Изпрати отзив'},
    'review.consent': {
        'sr': 'Slanjem dozvoljavate objavu vaše ocene i komentara nakon moderacije. Email ne objavljujemo.',
        'en': 'By submitting you allow us to publish the rating and comment after moderation. Email is never published.',
        'ru': 'Отправляя отзыв, вы разрешаете опубликовать оценку и комментарий после модерации. Email не публикуем.',
        'bg': 'С изпращането разрешавате публикуването на вашата оценка и коментар след модерация. Имейлът не се публикува.',
    },
    'review.ok.pending': {
        'sr': 'Hvala! Pregledaćemo recenziju u roku od 24–48 h.',
        'en': 'Thanks! We will review your comment within 24–48 hours.',
        'ru': 'Спасибо! Мы проверим отзыв в течение 24–48 часов.',
        'bg': 'Благодарим! Ще прегледаме отзива в срок от 24–48 ч.',
    },
    'review.ok.auto': {
        'sr': 'Hvala! Recenzija je objavljena.',
        'en': 'Thanks! Your review is live.',
        'ru': 'Спасибо! Отзыв опубликован.',
        'bg': 'Благодарим! Отзивът е публикуван.',
    },
    'review.err.generic': {
        'sr': 'Došlo je do greške. Pokušajte ponovo.',
        'en': 'Something went wrong. Please try again.',
        'ru': 'Что-то пошло не так. Попробуйте снова.',
        'bg': 'Възникна грешка. Опитайте отново.',
    },
    'review.err.rate_limit': {
        'sr': 'Previše pokušaja u kratkom vremenu. Pokušajte ponovo za sat vremena.',
        'en': 'Too many attempts. Please retry in about an hour.',
        'ru': 'Слишком много попыток. Повторите примерно через час.',
        'bg': 'Твърде много опити за кратко време. Опитайте отново след час.',
    },
    'review.err.rating': {
        'sr': 'Odaberite ocenu od 1 do 5 zvezdica.',
        'en': 'Pick a rating from 1 to 5 stars.',
        'ru': 'Выберите оценку от 1 до 5 звёзд.',
        'bg': 'Изберете оценка от 1 до 5 звезди.',
    },
    'review.err.comment_length': {
        'sr': 'Komentar treba da ima 50–500 znakova.',
        'en': 'Comment must be 50–500 characters.',
        'ru': 'Комментарий должен быть 50–500 символов.',
        'bg': 'Коментарът трябва да съдържа 50–500 знака.',
    },
    'review.err.name_length': {
        'sr': 'Ime treba da ima 2–40 slova.',
        'en': 'Name must be 2–40 letters.',
        'ru': 'Имя должно быть 2–40 букв.',
        'bg': 'Името трябва да съдържа 2–40 букви.',
    },
    'review.err.email_invalid': {
        'sr': 'Email adresa nije validna.',
        'en': 'Email address is not valid.',
        'ru': 'Email адрес недействителен.',
        'bg': 'Имейл адресът не е валиден.',
    },
    'review.err.no_urls': {
        'sr': 'Linkovi na spoljne sajtove nisu dozvoljeni u komentarima.',
        'en': 'Links to external sites are not allowed in comments.',
        'ru': 'Ссылки на внешние сайты в комментариях не разрешены.',
        'bg': 'Линкове към външни сайтове не са разрешени в коментарите.',
    },
    'review.err.profanity': {
        'sr': 'Komentar sadrži neprihvatljiv sadržaj.',
        'en': 'Comment contains unacceptable content.',
        'ru': 'Комментарий содержит неприемлемое содержание.',
        'bg': 'Коментарът съдържа неприемливо съдържание.',
    },
    'review.err.spam': {
        'sr': 'Slanje je odbijeno.',
        'en': 'Submission rejected.',
        'ru': 'Отправка отклонена.',
        'bg': 'Изпращането беше отхвърлено.',
    },
    'review.err.too_fast': {
        'sr': 'Pokušaj je prebrz — pročitajte formu pažljivo.',
        'en': 'That was too fast — please read the form and try again.',
        'ru': 'Слишком быстро — перечитайте форму и попробуйте ещё раз.',
        'bg': 'Опитът е твърде бърз — прочетете формата внимателно.',
    },
    'review.delete.link': {
        'sr': 'Zatraži brisanje',
        'en': 'Request deletion',
        'ru': 'Запросить удаление',
        'bg': 'Заявете изтриване',
    },
    'review.delete.prompt': {
        'sr': 'Unesite email adresu kojom ste ostavili recenziju:',
        'en': 'Enter the email you submitted the review with:',
        'ru': 'Введите email, с которым вы оставили отзыв:',
        'bg': 'Въведете имейл адреса, с който сте оставили отзива:',
    },
    'review.delete.sent': {
        'sr': 'Zahtev za brisanje je primljen. Obradićemo ga u roku od 7 dana u skladu sa GDPR-om.',
        'en': 'Deletion request received. We will process it within 7 days per GDPR.',
        'ru': 'Запрос на удаление принят. Обработаем в течение 7 дней согласно GDPR.',
        'bg': 'Заявката за изтриване е получена. Ще я обработим в срок от 7 дни в съответствие с GDPR.',
    },
    'review.lang_note': {
        'sr': 'Recenzija na srpskom', 'en': 'Review in English', 'ru': 'Отзыв на русском',
        'bg': 'Отзив на български',
    },

    # ── Newsletter / email subscribe ──
    'newsletter.title': {
        'sr': 'Newsletter',
        'en': 'Newsletter',
        'ru': 'Рассылка',
        'bg': 'Бюлетин',
    },
    'newsletter.subtitle': {
        'sr': 'Najjeftinije karte i nove rute — jednom nedeljno. Bez spama.',
        'en': 'Cheapest tickets and new routes, weekly. No spam.',
        'ru': 'Самые дешёвые билеты и новые маршруты — раз в неделю. Без спама.',
        'bg': 'Най-евтините билети и нови маршрути — веднъж седмично. Без спам.',
    },
    'newsletter.placeholder': {
        'sr': 'vaš@email.rs',
        'en': 'your@email.com',
        'ru': 'ваш@email.ru',
        'bg': 'ваш@email.bg',
    },
    'newsletter.button': {
        'sr': 'Pretplati se',
        'en': 'Subscribe',
        'ru': 'Подписаться',
        'bg': 'Абонирай се',
    },
    'newsletter.consent': {
        'sr': 'Saglasan/a sam sa obradom email adrese prema <a href="{prefix}/privatnost/">Politici privatnosti</a>.',
        'en': 'I agree to email processing per the <a href="{prefix}/privatnost/">Privacy policy</a>.',
        'ru': 'Согласен/на с обработкой email согласно <a href="{prefix}/privatnost/">Политике конфиденциальности</a>.',
        'bg': 'Съгласявам се с обработката на имейл адреса ми съгласно <a href="{prefix}/privatnost/">Политиката за поверителност</a>.',
    },
    'newsletter.success_pending': {
        'sr': 'Proverite email — poslali smo Vam link za potvrdu.',
        'en': 'Check your inbox — we sent a confirmation link.',
        'ru': 'Проверьте почту — отправили письмо с подтверждением.',
        'bg': 'Проверете имейла си — изпратихме ви линк за потвърждение.',
    },
    'newsletter.success_already': {
        'sr': 'Već ste pretplaćeni — hvala!',
        'en': "You're already subscribed — thanks!",
        'ru': 'Вы уже подписаны — спасибо!',
        'bg': 'Вече сте абонирани — благодарим!',
    },
    'newsletter.error_email': {
        'sr': 'Email adresa nije ispravna.',
        'en': 'Email address is invalid.',
        'ru': 'Некорректный email.',
        'bg': 'Имейл адресът не е валиден.',
    },
    'newsletter.error_consent': {
        'sr': 'Potvrdite saglasnost da biste se pretplatili.',
        'en': 'Tick the consent box to subscribe.',
        'ru': 'Отметьте согласие, чтобы подписаться.',
        'bg': 'Потвърдете съгласието си, за да се абонирате.',
    },
    'newsletter.error_generic': {
        'sr': 'Greška pri slanju. Pokušajte ponovo.',
        'en': 'Something went wrong. Try again.',
        'ru': 'Ошибка отправки. Попробуйте ещё раз.',
        'bg': 'Грешка при изпращане. Опитайте отново.',
    },
    'newsletter.error_ratelimit': {
        'sr': 'Previše pokušaja. Pokušajte za sat vremena.',
        'en': 'Too many attempts. Try again in an hour.',
        'ru': 'Слишком много попыток. Попробуйте через час.',
        'bg': 'Твърде много опити. Опитайте след час.',
    },

    # ── Price-alert (route-scoped newsletter) ──
    'price_alert.title': {
        'sr': 'Obaveštenje o ceni',
        'en': 'Price alert',
        'ru': 'Уведомление о цене',
        'bg': 'Известие за цена',
    },
    'price_alert.subtitle': {
        'sr': 'Javljamo kada cena za {pair} padne ili stigne akcija.',
        'en': "We'll email when {pair} drops in price or goes on sale.",
        'ru': 'Сообщим, когда цена {pair} упадёт или появится акция.',
        'bg': 'Ще ви уведомим, когато цената за {pair} падне или излезе промоция.',
    },
    'price_alert.button': {
        'sr': 'Prati cenu',
        'en': 'Track price',
        'ru': 'Следить за ценой',
        'bg': 'Следи цената',
    },
    'price_alert.sub_hint': {
        'sr': 'Jedan email kad najniža cena padne za 10% ili više.',
        'en': 'One email whenever the cheapest ticket drops 10% or more.',
        'ru': 'Одно письмо, когда минимальная цена падает на 10% и больше.',
        'bg': 'Един имейл, когато най-ниската цена падне с 10% или повече.',
    },
    'price_alert.ok_check_inbox': {
        'sr': 'Proverite email — poslali smo link za potvrdu.',
        'en': 'Check your inbox — we sent a confirmation link.',
        'ru': 'Проверьте почту — мы отправили ссылку для подтверждения.',
        'bg': 'Проверете имейла си — изпратихме линк за потвърждение.',
    },
    'price_alert.ok_already': {
        'sr': 'Već ste pretplaćeni — obaveštavaćemo Vas čim cena padne.',
        'en': "You're already subscribed — we'll email you on the next drop.",
        'ru': 'Вы уже подписаны — напишем, как только цена упадёт.',
        'bg': 'Вече сте абонирани — ще ви уведомим веднага щом цената падне.',
    },
    'price_alert.err': {
        'sr': 'Nešto je pošlo po zlu. Pokušajte ponovo.',
        'en': 'Something went wrong. Please try again.',
        'ru': 'Что-то пошло не так. Попробуйте ещё раз.',
        'bg': 'Нещо се обърка. Опитайте отново.',
    },
    'subscribe.email_placeholder': {
        'sr': 'Vaš email',
        'en': 'Your email',
        'ru': 'Ваш email',
    },
    'subscribe.consent_prefix': {
        'sr': 'Slažem se sa',
        'en': 'I agree to the',
        'ru': 'Я согласен с',
    },
    'subscribe.consent_link': {
        'sr': 'politikom privatnosti',
        'en': 'privacy policy',
        'ru': 'политикой конфиденциальности',
    },

    # ── Subscribe confirm / unsubscribe pages ──
    'sub.confirm.title_ok': {'sr': 'Pretplata potvrđena', 'en': 'Subscription confirmed', 'ru': 'Подписка подтверждена'},
    'sub.confirm.title_already': {'sr': 'Već ste pretplaćeni', 'en': 'Already subscribed', 'ru': 'Уже подписаны'},
    'sub.confirm.title_expired': {'sr': 'Link je istekao', 'en': 'Link expired', 'ru': 'Ссылка устарела'},
    'sub.confirm.title_error': {'sr': 'Nešto nije u redu', 'en': 'Something went wrong', 'ru': 'Что-то пошло не так'},
    'sub.confirm.body_ok': {
        'sr': 'Poslali smo vam dobrodošlicu na email. Jednom nedeljno ćete dobijati najjeftinije karte i nove rute.',
        'en': 'We sent you a welcome email. Once a week you will receive the cheapest tickets and new routes.',
        'ru': 'Мы отправили вам приветственное письмо. Раз в неделю вы будете получать лучшие цены и новые маршруты.',
    },
    'sub.confirm.body_already': {
        'sr': 'Ovaj email je već potvrđen ranije — ne morate ništa da radite.',
        'en': "This email was already confirmed — you don't need to do anything.",
        'ru': 'Этот email уже подтверждён — ничего делать не нужно.',
    },
    'sub.confirm.body_expired': {
        'sr': 'Potvrdni link traje 7 dana. Prijavite se ponovo sa iste adrese da dobijete svež link.',
        'en': 'Confirmation links are valid for 7 days. Sign up again with the same address to get a fresh link.',
        'ru': 'Ссылка действует 7 дней. Подпишитесь заново с того же адреса, чтобы получить новую.',
    },
    'sub.confirm.body_error': {
        'sr': 'Pokušajte da se prijavite ponovo.',
        'en': 'Please try signing up again.',
        'ru': 'Попробуйте подписаться снова.',
    },
    'sub.confirm.back': {'sr': 'Nazad na početnu', 'en': 'Back to home', 'ru': 'На главную'},
    'sub.unsub.h1_ok': {'sr': 'Odjavili ste se', 'en': "You've unsubscribed", 'ru': 'Вы отписались'},
    'sub.unsub.body_ok': {
        'sr': 'Više nećete dobijati email od nas. Ako ste se odjavili greškom, možete se prijaviti ponovo na početnoj strani.',
        'en': 'You will no longer receive emails from us. If you unsubscribed by mistake, you can sign up again on the home page.',
        'ru': 'Вы больше не будете получать письма от нас. Если вы отписались по ошибке, можете подписаться снова на главной странице.',
    },
    'sub.unsub.h1_error': {'sr': 'Link nije važeći', 'en': 'Invalid link', 'ru': 'Недействительная ссылка'},
    'sub.unsub.body_error': {
        'sr': 'Ovaj link je već iskorišćen ili nije ispravan.',
        'en': 'This link has already been used or is not valid.',
        'ru': 'Эта ссылка уже была использована или недействительна.',
    },

    # ── Misc UI strings ──

    # ── PWA install promo ──
    'pwa.install_title': {
        'sr': 'Instalirajte Prevozni',
        'en': 'Install Prevozni',
        'ru': 'Установить Prevozni',
        'bg': 'Инсталирайте Prevozni',
    },
    'pwa.install_sub': {
        'sr': 'Brže otvaranje, manje reklama, offline pretraga.',
        'en': 'Faster launches, less clutter, offline search.',
        'ru': 'Быстрый запуск, меньше шума, поиск офлайн.',
        'bg': 'По-бързо отваряне, по-малко реклами, офлайн търсене.',
    },
    'pwa.install_cta': {
        'sr': 'Instaliraj',
        'en': 'Install',
        'ru': 'Установить',
        'bg': 'Инсталирай',
    },
    'pwa.dismiss': {
        'sr': 'Ne sada',
        'en': 'Not now',
        'ru': 'Не сейчас',
        'bg': 'Не сега',
    },
    'pwa.install_ios_title': {
        'sr': 'Dodajte na početni ekran',
        'en': 'Add to Home Screen',
        'ru': 'На главный экран',
        'bg': 'Добавете към началния екран',
    },
    'pwa.install_ios_hint': {
        'sr': 'Otvorite stranicu u Safariju, tapnite dugme Podeli, pa '
              '"Na početni ekran" da instalirate Prevozni kao aplikaciju.',
        'en': 'Open this page in Safari, tap the Share button, then '
              'choose "Add to Home Screen" to install Prevozni as an app.',
        'ru': 'Откройте страницу в Safari, нажмите кнопку «Поделиться» и '
              'выберите «На экран „Домой"», чтобы установить Prevozni.',
        'bg': 'Отворете страницата в Safari, натиснете бутона Споделяне, после ',
    },
    'pwa.install_ios_close': {
        'sr': 'Zatvori',
        'en': 'Close',
        'ru': 'Закрыть',
        'bg': 'Затвори',
    },

    # ── Footer legal links + disclosure ──
    'footer.tos': {
        'sr': 'Uslovi korišćenja',
        'en': 'Terms of Service',
        'ru': 'Условия использования',
        'bg': 'Условия за ползване',
    },
    'footer.cookies': {
        'sr': 'Politika kolačića',
        'en': 'Cookie Policy',
        'ru': 'Политика cookies',
        'bg': 'Политика за бисквитките',
    },
    'footer.partners': {
        'sr': 'Partnerske provizije: BusTicket4.me. Klikom na "Kupi" možete napustiti naš sajt.',
        'en': 'Partner commissions: BusTicket4.me. Clicking "Buy" may take you off-site.',
        'ru': 'Партнёрские комиссии: BusTicket4.me. Нажатие «Купить» может увести с сайта.',
        'bg': 'Партньорски комисиони: BusTicket4.me. С клик върху "Купи" може да напуснете нашия сайт.',
    },

    # ── Cookie consent banner ──
    'cookies.banner.aria': {
        'sr': 'Obaveštenje o kolačićima',
        'en': 'Cookie notice',
        'ru': 'Уведомление о cookies',
        'bg': 'Известие за бисквитките',
    },
    'cookies.banner.text': {
        'sr': 'Koristimo kolačiće za osnovne funkcije (jezik, valuta, sačuvane rute) i anonimnu analitiku bez praćenja. Možete prihvatiti sve ili samo neophodne.',
        'en': 'We use cookies for essential features (language, currency, saved routes) and anonymous analytics without tracking. You can accept all or essentials only.',
        'ru': 'Мы используем cookies для базовых функций (язык, валюта, сохранённые маршруты) и анонимной аналитики без отслеживания. Можно принять всё или только необходимые.',
        'bg': 'Използваме бисквитки за основни функции (език, валута, запазени маршрути) и анонимна статистика без проследяване. Можете да приемете всички или само необходимите.',
    },
    'cookies.banner.accept_all': {
        'sr': 'Prihvatam',
        'en': 'Accept all',
        'ru': 'Принять всё',
        'bg': 'Приемам всички',
    },
    'cookies.banner.essential': {
        'sr': 'Samo neophodni',
        'en': 'Essentials only',
        'ru': 'Только необходимые',
        'bg': 'Само необходимите',
    },
    'cookies.banner.more': {
        'sr': 'Politika kolačića',
        'en': 'Cookie Policy',
        'ru': 'Политика cookie',
        'bg': 'Политика за бисквитки',
    },

    # ── Cookie Policy page ──
    'cookies.page.title': {
        'sr': 'Politika kolačića',
        'en': 'Cookie Policy',
        'ru': 'Политика cookies',
        'bg': 'Политика за бисквитките',
    },
    'cookies.page.meta': {
        'sr': 'Koje kolačiće Prevozni koristi, zašto, koliko se čuvaju i kako da ih onemogućite ili povučete saglasnost.',
        'en': 'Which cookies Prevozni uses, why, how long they are stored, and how to disable them or withdraw consent.',
        'ru': 'Какие cookies использует Prevozni, зачем, сколько хранятся и как их отключить или отозвать согласие.',
        'bg': 'Кои бисквитки използва Prevozni, защо, колко дълго се съхраняват и как да ги забраните или оттеглите съгласието си.',
    },
    'cookies.page.intro': {
        'sr': 'Ova stranica objašnjava koje kolačiće i tehnologije lokalnog skladištenja Prevozni koristi, u koju svrhu, koliko dugo se čuvaju i kako da kontrolišete ili povučete svoju saglasnost.',
        'en': 'This page explains which cookies and local-storage technologies Prevozni uses, their purpose, how long they are kept, and how you can control or withdraw your consent.',
        'ru': 'На этой странице описано, какие cookies и технологии локального хранения использует Prevozni, для чего, сколько они хранятся и как вы можете управлять своим согласием или отозвать его.',
    },
    'cookies.page.what_h': {
        'sr': 'Šta su kolačići',
        'en': 'What are cookies',
        'ru': 'Что такое cookies',
    },
    'cookies.page.what_body': {
        'sr': 'Kolačići (cookies) su mali tekstualni zapisi koje veb sajt postavlja u vaš pretraživač. Oni pomažu sajtu da upamti vaše preferencije između poseta — na primer izabrani jezik ili valutu — ili da razlikuje dve posete iste stranice. Local storage radi slično ali ostaje u pretraživaču dok ga ne obrišete. Prevozni koristi samo <strong>first-party</strong> kolačiće (postavljeni sa prevozni.com) i nikada ne postavlja reklamne ili praćeće kolačiće trećih strana.',
        'en': 'Cookies are small text records a website places in your browser. They help the site remember your preferences between visits — for example the selected language or currency — or distinguish between visits to the same page. Local storage works similarly but persists in the browser until you clear it. Prevozni uses only <strong>first-party</strong> cookies (set from prevozni.com) and never sets third-party advertising or tracking cookies.',
        'ru': 'Cookies — это небольшие текстовые записи, которые сайт сохраняет в вашем браузере. Они помогают сайту запоминать ваши настройки между посещениями — например выбранный язык или валюту — или различать посещения одной страницы. Local storage работает похожим образом, но остаётся в браузере, пока вы его не очистите. Prevozni использует только <strong>first-party</strong> cookies (установленные с prevozni.com) и никогда не ставит рекламные или трекинговые cookies третьих сторон.',
    },
    'cookies.page.used_h': {
        'sr': 'Koje kolačiće koristimo',
        'en': 'Which cookies we use',
        'ru': 'Какие cookies мы используем',
    },
    'cookies.page.used_intro': {
        'sr': 'Ovo je potpuna lista kolačića i local-storage zapisa koje Prevozni može postaviti u vašem pretraživaču:',
        'en': 'This is the complete list of cookies and local-storage items Prevozni may place in your browser:',
        'ru': 'Это полный список cookies и записей local storage, которые Prevozni может поставить в вашем браузере:',
    },
    'cookies.page.th_name': {
        'sr': 'Ime',
        'en': 'Name',
        'ru': 'Имя',
    },
    'cookies.page.th_purpose': {
        'sr': 'Svrha',
        'en': 'Purpose',
        'ru': 'Назначение',
    },
    'cookies.page.th_duration': {
        'sr': 'Trajanje',
        'en': 'Duration',
        'ru': 'Срок',
    },
    'cookies.page.th_type': {
        'sr': 'Tip',
        'en': 'Type',
        'ru': 'Тип',
    },
    'cookies.page.type_essential': {
        'sr': 'neophodan',
        'en': 'essential',
        'ru': 'необходимый',
    },
    'cookies.page.type_analytics': {
        'sr': 'analitika',
        'en': 'analytics',
        'ru': 'аналитика',
    },
    'cookies.page.dur_year': {
        'sr': '1 godina',
        'en': '1 year',
        'ru': '1 год',
    },
    'cookies.page.dur_session': {
        'sr': 'sesija',
        'en': 'session',
        'ru': 'сессия',
    },
    'cookies.page.dur_until_cleared': {
        'sr': 'dok ne obrišete',
        'en': 'until cleared',
        'ru': 'до очистки',
    },
    'cookies.page.purpose_consent': {
        'sr': 'Pamti vaš odabir u baneru saglasnosti (sve / samo neophodni).',
        'en': 'Remembers your choice in the consent banner (all / essentials only).',
        'ru': 'Запоминает ваш выбор в баннере согласия (всё / только необходимые).',
    },
    'cookies.page.purpose_ccy': {
        'sr': 'Pamti izabrani prikaz valute (RSD ili EUR).',
        'en': 'Remembers the selected currency display (RSD or EUR).',
        'ru': 'Запоминает выбранную валюту отображения (RSD или EUR).',
    },
    'cookies.page.purpose_ab': {
        'sr': 'Dodeljuje stabilan A/B redosled partnerskih ponuda (BusTicket4.me) po posetiocu.',
        'en': 'Assigns a stable A/B ordering of partner offers (BusTicket4.me) per visitor.',
        'ru': 'Назначает стабильный A/B порядок партнёрских предложений (BusTicket4.me) для посетителя.',
    },
    'cookies.page.purpose_saved': {
        'sr': 'Čuva vaše označene rute (lokalno u pretraživaču, ne šalje se na server).',
        'en': 'Stores your saved routes (locally in the browser, never sent to the server).',
        'ru': 'Хранит ваши сохранённые маршруты (локально в браузере, не отправляется на сервер).',
    },
    'cookies.page.purpose_session': {
        'sr': 'CSRF zaštita forme — traje samo tokom sesije.',
        'en': 'CSRF form protection — lasts only for the session.',
        'ru': 'CSRF-защита формы — только на время сессии.',
    },
    'cookies.page.third_party_h': {
        'sr': 'Treće strane',
        'en': 'Third parties',
        'ru': 'Третьи стороны',
    },
    'cookies.page.third_party_body': {
        'sr': '<strong>Umami</strong> (na našem serveru, ne kod treće strane) prikuplja anonimnu agregatnu statistiku poseta <strong>bez kolačića</strong> i bez ličnih identifikatora. Ako prihvatite sve kolačiće, učitavamo Umami skriptu; ako izaberete samo neophodne, skripta se ne učitava. <strong>BusTicket4.me</strong> su partnerski sajtovi — kada kliknete "Kupi", napuštate naš sajt i ulazite pod njihovu politiku kolačića.',
        'en': '<strong>Umami</strong> (self-hosted on our own server, no third party) collects anonymous aggregate visit statistics <strong>without cookies</strong> and without personal identifiers. If you accept all cookies, we load the Umami script; if you choose essentials only, the script is not loaded. <strong>BusTicket4.me</strong> are partner sites — when you click "Buy" you leave our site and fall under their cookie policy.',
        'ru': '<strong>Umami</strong> (на нашем собственном сервере, без третьих сторон) собирает анонимную агрегированную статистику посещений <strong>без cookies</strong> и без персональных идентификаторов. Если вы принимаете все cookies, мы загружаем скрипт Umami; если выбираете только необходимые — скрипт не загружается. <strong>BusTicket4.me</strong> — партнёрские сайты, при нажатии «Купить» вы покидаете наш сайт и попадаете под их политику cookies.',
    },
    'cookies.page.disable_h': {
        'sr': 'Kako da onemogućite kolačiće',
        'en': 'How to disable cookies',
        'ru': 'Как отключить cookies',
    },
    'cookies.page.disable_body': {
        'sr': 'Svaki pretraživač vam omogućava da blokirate ili obrišete kolačiće: pogledajte podešavanja Chrome / Firefox / Safari / Edge, obično pod "Privatnost i bezbednost". Ako blokirate neophodne kolačiće, neke funkcije (pamćenje valute, sačuvane rute) neće raditi, ali sajt ostaje upotrebljiv.',
        'en': 'Every browser lets you block or delete cookies: check Chrome / Firefox / Safari / Edge settings, typically under "Privacy and security". If you block essential cookies, some features (currency memory, saved routes) will not work, but the site remains usable.',
        'ru': 'Любой браузер позволяет блокировать или удалять cookies: откройте настройки Chrome / Firefox / Safari / Edge, обычно в разделе «Конфиденциальность и безопасность». Если блокировать необходимые cookies, некоторые функции (запоминание валюты, сохранённые маршруты) не будут работать, но сайт остаётся функциональным.',
    },
    'cookies.page.revoke_h': {
        'sr': 'Povlačenje saglasnosti',
        'en': 'Withdrawing consent',
        'ru': 'Отзыв согласия',
    },
    'cookies.page.revoke_body': {
        'sr': 'Da povučete svoju prethodnu saglasnost (ponovo vam se pojavi baner i možete da izaberete drugu opciju), kliknite dugme ispod — brišemo kolačić saglasnosti i osvežavamo stranicu.',
        'en': 'To withdraw your previous consent (so the banner appears again and you can pick a different option), click the button below — we clear the consent cookie and reload the page.',
        'ru': 'Чтобы отозвать ранее данное согласие (баннер появится снова, и вы сможете выбрать другой вариант), нажмите кнопку ниже — мы удаляем cookie согласия и перезагружаем страницу.',
    },
    'cookies.page.revoke_btn': {
        'sr': 'Resetuj moju saglasnost',
        'en': 'Reset my consent',
        'ru': 'Сбросить согласие',
    },
    'cookies.page.changes_h': {
        'sr': 'Izmene ove politike',
        'en': 'Changes to this policy',
        'ru': 'Изменения этой политики',
    },
    'cookies.page.changes_body': {
        'sr': 'Ako dodamo novi alat ili promenimo način korišćenja kolačića, ažuriraćemo ovu stranicu i datum ispod. Trenutna verzija: april 2026.',
        'en': 'If we add a new tool or change how we use cookies, we will update this page and the date below. Current version: April 2026.',
        'ru': 'Если мы добавим новый инструмент или изменим порядок использования cookies, мы обновим эту страницу и дату ниже. Текущая версия: апрель 2026.',
    },

    # ── Terms of Service page ──
    'tos.title': {
        'sr': 'Uslovi korišćenja',
        'en': 'Terms of Service',
        'ru': 'Условия использования',
        'bg': 'Условия за ползване',
    },
    'tos.meta': {
        'sr': 'Uslovi korišćenja sajta Prevozni — ko smo, šta nudimo, odricanje od odgovornosti za tačnost podataka, partnerski linkovi i korisnički sadržaj.',
        'en': 'Terms of Service for Prevozni — who we are, what we provide, disclaimer on data accuracy, affiliate links and user content.',
        'ru': 'Условия использования сайта Prevozni — кто мы, что предоставляем, отказ от ответственности за точность данных, партнёрские ссылки и пользовательский контент.',
        'bg': 'Условия за ползване на сайта Prevozni — кои сме, какво предлагаме, отказ от отговорност за точността на данните, партньорски линкове и потребителско съдържание.',
    },
    'tos.intro': {
        'sr': 'Ovi uslovi regulišu korišćenje sajta prevozni.com. Nastavkom korišćenja prihvatate ih u celini. Ako se ne slažete, molimo ne koristite sajt.',
        'en': 'These terms govern the use of prevozni.com. By continuing to use the site you accept them in full. If you disagree, please do not use the site.',
        'ru': 'Эти условия регулируют использование сайта prevozni.com. Продолжая использовать сайт, вы принимаете их полностью. Если не согласны, пожалуйста, не пользуйтесь сайтом.',
        'bg': 'Тези условия уреждат използването на сайта prevozni.com. С продължаването на използването ги приемате изцяло. Ако не сте съгласни, моля, не използвайте сайта.',
    },
    'tos.updated': {
        'sr': 'Poslednja izmena: april 2026.',
        'en': 'Last updated: April 2026.',
        'ru': 'Последнее обновление: апрель 2026.',
        'bg': 'Последна промяна: април 2026.',
    },
    'tos.s1_h': {
        'sr': '1. Ko smo',
        'en': '1. Who we are',
        'ru': '1. Кто мы',
        'bg': '1. Кои сме',
    },
    'tos.s1_body': {
        'sr': 'Prevozni je nezavisan projekat koji agregira javno dostupne podatke o javnom prevozu u Srbiji i regionu. Nismo prevoznik, agencija za prodaju karata ni zvanični predstavnik bilo kojeg prevoznika. Za kontakt koristite <strong>info@prevozni.com</strong> ili formu na <a href="/kontakt/">/kontakt/</a>.',
        'en': 'Prevozni is an independent project that aggregates publicly available public-transit data for Serbia and the region. We are not a carrier, a ticket agency, or an official representative of any carrier. For contact use <strong>info@prevozni.com</strong> or the form at <a href="/kontakt/">/kontakt/</a>.',
        'ru': 'Prevozni — независимый проект, агрегирующий общедоступные данные об общественном транспорте Сербии и региона. Мы не перевозчик, не билетное агентство и не официальный представитель какого-либо перевозчика. Для связи — <strong>info@prevozni.com</strong> или форма на <a href="/kontakt/">/kontakt/</a>.',
        'bg': 'Prevozni е независим проект, който агрегира публично достъпни данни за обществения транспорт в Сърбия и региона. Ние не сме превозвач, агенция за продажба на билети, нито официален представител на който и да е превозвач. За контакт използвайте <strong>info@prevozni.com</strong> или формата на <a href="/kontakt/">/kontakt/</a>.',
    },
    'tos.s2_h': {
        'sr': '2. Usluge',
        'en': '2. Services',
        'ru': '2. Услуги',
        'bg': '2. Услуги',
    },
    'tos.s2_body': {
        'sr': 'Sajt pruža besplatan pregled reda vožnje, cena i prevoznika za međugradske autobuse, vozove i gradski prevoz. Ne prodajemo karte; kupovinu obavlja sam prevoznik ili partnerska platforma na koju vas vodi dugme "Kupi". Ne garantujemo dostupnost polaska koji se prikazuje — proverite direktno kod prevoznika pre putovanja.',
        'en': 'The site provides free schedule, price and carrier information for intercity buses, trains and urban transport. We do not sell tickets; purchase is handled by the carrier itself or by a partner platform reached via the "Buy" button. We do not guarantee the availability of any displayed departure — please verify directly with the carrier before travelling.',
        'ru': 'Сайт предоставляет бесплатную информацию о расписании, ценах и перевозчиках для междугородних автобусов, поездов и городского транспорта. Мы не продаём билеты; покупка осуществляется самим перевозчиком или партнёрской платформой по кнопке «Купить». Мы не гарантируем наличие отображаемого рейса — проверяйте непосредственно у перевозчика перед поездкой.',
        'bg': 'Сайтът предоставя безплатен преглед на разписанията, цените и превозвачите за междуградски автобуси, влакове и градски транспорт. Ние не продаваме билети; покупката се извършва от самия превозвач или от партньорска платформа, към която ви насочва бутонът „Купи“. Не гарантираме наличността на показания курс — проверете директно при превозвача преди пътуването.',
    },
    'tos.s3_h': {
        'sr': '3. Tačnost podataka',
        'en': '3. Data accuracy',
        'ru': '3. Точность данных',
        'bg': '3. Точност на данните',
    },
    'tos.s3_body': {
        'sr': 'Podaci dolaze iz više javnih izvora (vidi <a href="/o-nama/">/o-nama/</a>) i osvežavaju se automatski. Trudimo se da budu tačni, ali ih pružamo "takve kakvi jesu" — bez garancije o ažurnosti, potpunosti ili pogodnosti za određenu namenu. Prevoznici mogu u svakom trenutku promeniti red vožnje, cene ili ukinuti liniju; uvek proverite zvanični sajt prevoznika ili stanice pre puta.',
        'en': 'Data comes from several public sources (see <a href="/o-nama/">/o-nama/</a>) and is refreshed automatically. We aim for accuracy but provide it "as is" — without warranty of timeliness, completeness or fitness for a particular purpose. Carriers can change schedules, prices or cancel lines at any time; always check the carrier\'s or station\'s official site before travelling.',
        'ru': 'Данные поступают из нескольких публичных источников (см. <a href="/o-nama/">/o-nama/</a>) и обновляются автоматически. Мы стремимся к точности, но предоставляем данные «как есть», без гарантий актуальности, полноты или пригодности для конкретной цели. Перевозчики могут в любой момент изменить расписание, цены или отменить рейс; всегда сверяйтесь с официальным сайтом перевозчика или станции перед поездкой.',
        'bg': 'Данните идват от множество публични източници (вижте <a href="/o-nama/">/o-nama/</a>) и се обновяват автоматично. Стараем се те да бъдат точни, но ги предоставяме „такива, каквито са“ — без гаранция за актуалност, пълнота или пригодност за определена цел. Превозвачите могат по всяко време да променят разписанието, цените или да прекратят линия; винаги проверявайте официалния сайт на превозвача или автогарата преди пътуването.',
    },
    'tos.s4_h': {
        'sr': '4. Partnerski linkovi (affiliate disclosure)',
        'en': '4. Affiliate links (disclosure)',
        'ru': '4. Партнёрские ссылки (disclosure)',
        'bg': '4. Партньорски линкове (affiliate disclosure)',
    },
    'tos.s4_body': {
        'sr': 'Neki linkovi za kupovinu karte (dugme "Kupi" pored polaska) vode na partnerske platforme <strong>BusTicket4.me</strong> ili <strong>FlixBus</strong>. Ako kupite kartu preko takvog linka, Prevozni može da dobije malu proviziju koja pokriva troškove održavanja sajta. <strong>Cena koju vi plaćate se ne menja.</strong> Partnerski linkovi su jasno obeleženi kao "Kupi" a u naš sistem se beleži samo anonimni agregirani zapis klika (bez ličnih podataka) — detalji u <a href="/privatnost/">Politici privatnosti</a>.',
        'en': 'Some ticket-purchase links (the "Buy" button next to a departure) go to partner platforms <strong>BusTicket4.me</strong> or <strong>FlixBus</strong>. If you buy a ticket via such a link, Prevozni may receive a small commission that helps cover hosting and maintenance. <strong>The price you pay is not affected.</strong> Affiliate links are clearly labelled "Buy" and only an anonymous aggregate click record (no personal data) is stored on our side — details in the <a href="/privatnost/">Privacy Policy</a>.',
        'ru': 'Некоторые ссылки покупки билета (кнопка «Купить» рядом с рейсом) ведут на партнёрские платформы <strong>BusTicket4.me</strong> или <strong>FlixBus</strong>. Если вы покупаете билет по такой ссылке, Prevozni может получить небольшую комиссию, которая покрывает расходы на хостинг и поддержку. <strong>Цена для вас не меняется.</strong> Партнёрские ссылки явно помечены как «Купить», а у нас сохраняется только анонимная агрегированная запись клика (без персональных данных) — подробности в <a href="/privatnost/">Политике конфиденциальности</a>.',
        'bg': 'Някои линкове за покупка на билет (бутонът „Купи“ до курса) водят към партньорските платформи <strong>BusTicket4.me</strong> или <strong>FlixBus</strong>. Ако купите билет чрез такъв линк, Prevozni може да получи малка комисиона, която покрива разходите за поддръжка на сайта. <strong>Цената, която вие плащате, не се променя.</strong> Партньорските линкове са ясно обозначени като „Купи“, а в нашата система се записва само анонимен, агрегиран запис за клика (без лични данни) — подробности в <a href="/privatnost/">Политиката за поверителност</a>.',
    },
    'tos.s5_h': {
        'sr': '5. Korisnički sadržaj (recenzije)',
        'en': '5. User content (reviews)',
        'ru': '5. Пользовательский контент (отзывы)',
        'bg': '5. Потребителско съдържание (отзиви)',
    },
    'tos.s5_body': {
        'sr': 'Korisnici mogu da ostave recenziju rute. Zadržavate autorska prava nad tekstom koji ste napisali; slanjem nam dajete <strong>ne-isključivu, besplatnu, globalnu licencu</strong> da recenziju javno prikazujemo, indeksiramo i prevodimo kada je to potrebno. Zabranjujemo: spam, linkove, lične podatke trećih lica, uvrede i govor mržnje. Zadržavamo pravo da moderiramo, uredimo ili obrišemo recenziju bez prethodnog obaveštenja. Možete zatražiti brisanje svoje recenzije dugmetom "Zatraži brisanje" ispod nje, u skladu sa <a href="/privatnost/">Politikom privatnosti</a>.',
        'en': 'Users may leave route reviews. You retain copyright over the text you wrote; by submitting you grant us a <strong>non-exclusive, royalty-free, worldwide licence</strong> to display, index and translate the review where relevant. We forbid: spam, links, third-party personal data, insults and hate speech. We reserve the right to moderate, edit or delete any review without prior notice. You can request deletion of your review via the "Request deletion" button beneath it, as described in the <a href="/privatnost/">Privacy Policy</a>.',
        'ru': 'Пользователи могут оставлять отзывы о маршрутах. Авторские права на текст остаются за вами; при отправке вы предоставляете нам <strong>неисключительную, безвозмездную, всемирную лицензию</strong> на публичное отображение, индексацию и перевод отзыва при необходимости. Запрещены: спам, ссылки, персональные данные третьих лиц, оскорбления и язык ненависти. Мы оставляем за собой право модерировать, редактировать или удалять любой отзыв без предварительного уведомления. Удаление своего отзыва можно запросить кнопкой «Запросить удаление» под ним, как описано в <a href="/privatnost/">Политике конфиденциальности</a>.',
        'bg': 'Потребителите могат да оставят отзив за маршрут. Вие запазвате авторските права върху текста, който сте написали; изпращайки го, ни давате <strong>неизключителен, безплатен, глобален лиценз</strong> да показваме отзива публично, да го индексираме и превеждаме, когато е необходимо. Забраняваме: спам, линкове, лични данни на трети лица, обиди и език на омразата. Запазваме правото да модерираме, редактираме или изтриваме отзив без предварително уведомление. Можете да поискате изтриване на своя отзив чрез бутона „Заявете изтриване“ под него, в съответствие с <a href="/privatnost/">Политиката за поверителност</a>.',
    },
    'tos.s6_h': {
        'sr': '6. Ograničenje odgovornosti',
        'en': '6. Limitation of liability',
        'ru': '6. Ограничение ответственности',
        'bg': '6. Ограничаване на отговорността',
    },
    'tos.s6_body': {
        'sr': 'U meri dozvoljenoj zakonom, Prevozni i njegovi autori nisu odgovorni za bilo kakvu direktnu, indirektnu, slučajnu ili posledičnu štetu koja proizlazi iz korišćenja ili nemogućnosti korišćenja sajta, uključujući ali ne ograničavajući se na propuštena putovanja, nekorektne informacije o polascima, cenama ili stanicama, i prekide u radu. Korišćenjem sajta prihvatate da je putovanje vaša lična odluka i odgovornost.',
        'en': 'To the extent permitted by law, Prevozni and its authors are not liable for any direct, indirect, incidental or consequential damages arising from use or inability to use the site, including but not limited to missed trips, incorrect departure / price / station information, and service interruptions. By using the site you agree that travel decisions remain your personal responsibility.',
        'ru': 'В той мере, в какой это допускается законом, Prevozni и его авторы не несут ответственности за прямые, косвенные, случайные или последующие убытки, возникающие в связи с использованием или невозможностью использования сайта, включая (но не ограничиваясь): пропущенные поездки, неверную информацию о рейсах / ценах / станциях и перебои в работе. Используя сайт, вы соглашаетесь, что решение о поездке остаётся вашей личной ответственностью.',
        'bg': 'До степента, разрешена от закона, Prevozni и неговите автори не носят отговорност за каквито и да било преки, косвени, случайни или последващи вреди, произтичащи от използването или невъзможността за използване на сайта, включително, но не само пропуснати пътувания, неточна информация за курсове, цени или автогари, и прекъсвания в работата. С използването на сайта приемате, че пътуването е ваше лично решение и отговорност.',
    },
    'tos.s7_h': {
        'sr': '7. Merodavno pravo',
        'en': '7. Governing law',
        'ru': '7. Применимое право',
        'bg': '7. Приложимо право',
    },
    'tos.s7_body': {
        'sr': 'Ovi uslovi se tumače u skladu sa pravom Republike Srbije. Za sve sporove koji proizlaze iz korišćenja sajta nadležan je sud u Beogradu, Srbija, osim ako imperativne norme zaštite potrošača u vašoj državi prebivališta ne propisuju drugačije.',
        'en': 'These terms are interpreted under the law of the Republic of Serbia. Any disputes arising from use of the site fall under the jurisdiction of the court in Belgrade, Serbia, unless mandatory consumer-protection rules in your country of residence require otherwise.',
        'ru': 'Эти условия толкуются в соответствии с правом Республики Сербия. Все споры, возникающие в связи с использованием сайта, подсудны суду в Белграде, Сербия, если иное не предусмотрено императивными нормами защиты прав потребителей страны вашего проживания.',
        'bg': 'Тези условия се тълкуват в съответствие с правото на Република Сърбия. За всички спорове, произтичащи от използването на сайта, компетентен е съдът в Белград, Сърбия, освен ако императивни норми за защита на потребителите в държавата на вашето местожителство не предвиждат друго.',
    },
    'tos.s8_h': {
        'sr': '8. Izmene uslova',
        'en': '8. Changes to these terms',
        'ru': '8. Изменения условий',
        'bg': '8. Промени в условията',
    },
    'tos.s8_body': {
        'sr': 'Možemo povremeno da ažuriramo ove uslove. Svaka nova verzija se objavljuje na ovoj stranici sa datumom izmene. Ako izmena bitno utiče na vaša prava, objavljujemo baner na početnoj strani najmanje 14 dana unapred. Nastavkom korišćenja sajta nakon objave prihvatate izmenjene uslove.',
        'en': 'We may update these terms from time to time. Each new version is published on this page with a change date. If a change materially affects your rights, we publish a homepage banner at least 14 days in advance. Continued use of the site after publication constitutes acceptance of the updated terms.',
        'ru': 'Мы можем периодически обновлять эти условия. Каждая новая версия публикуется на этой странице с датой изменения. Если изменение существенно затрагивает ваши права, мы вывешиваем баннер на главной странице минимум за 14 дней. Продолжение использования сайта после публикации означает принятие обновлённых условий.',
        'bg': 'Можем периодично да актуализираме тези условия. Всяка нова версия се публикува на тази страница с дата на промяната. Ако промяната съществено засяга вашите права, публикуваме банер на началната страница най-малко 14 дни предварително. С продължаването на използването на сайта след публикуването приемате изменените условия.',
    },

    'home.quick_label': {'sr': 'Popularno:', 'en': 'Popular:', 'ru': 'Популярно:'},
    'home.quick_links_aria': {'sr': 'Popularni maršruti', 'en': 'Popular routes', 'ru': 'Популярные маршруты'},


    'seasonal.tip_heading': {'sr': 'Planirate posetu?', 'en': 'Planning a visit?', 'ru': 'Планируете поездку?'},
    'seasonal.tip_route': {
        'sr': 'Rezervišite smeštaj u {to_city} na vreme — leto je sezona najveće potražnje.',
        'en': 'Book accommodation in {to_city} early — summer is peak season.',
        'ru': 'Забронируйте жильё в {to_city} заранее — летом высокий сезон.',
        'bg': 'Популярно:',
    },

    'city.loading': {'sr': 'Podaci se učitavaju...', 'en': 'Loading data...', 'ru': 'Загрузка...', 'bg': 'Данните се зареждат...'},
    'line.no_stops': {'sr': 'Nema podataka o stajalištima', 'en': 'No stop data available', 'ru': 'Нет данных об остановках', 'bg': 'Няма данни за спирки'},
    'stop.no_lines': {'sr': 'Nema podataka o linijama', 'en': 'No line data available', 'ru': 'Нет данных о маршрутах', 'bg': 'Няма данни за линии'},
    'line.schedule_unavailable': {
        'sr': 'Tačan raspored trenutno nije dostupan. Proverite direktno kod prevoznika ili na autobuskoj stanici.',
        'en': 'Exact schedule is not currently available. Please check directly with the carrier or at the bus station.',
        'ru': 'Точное расписание временно недоступно. Уточните у перевозчика или на автовокзале.',
        'bg': 'Точното разписание в момента не е достъпно. Проверете директно при превозвача или на автогарата.',
    },

    # ── Guide: Beograd–Novi Sad ──
    'guides.beograd_ns.title': {
        'sr': 'Autobus Beograd → Novi Sad {year} — Cene i Red Vožnje',
        'en': 'Bus Belgrade → Novi Sad {year} — Prices and Schedule',
        'ru': 'Автобус Белград → Нови-Сад {year} — Цены и Расписание',
        'bg': 'Автобус Белград → Нови Сад {year} — Цени и разписание',
    },
    'guides.beograd_ns.meta': {
        'sr': 'Sve o prevozu Beograd–Novi Sad: cene karata od 640 RSD, vreme putovanja 1–2h, poređenje autobusa i voza i aktuelni polasci.',
        'en': 'Everything about Belgrade–Novi Sad transport: ticket prices from 640 RSD, 1–2h travel time, bus vs train comparison and current departures.',
        'ru': 'Всё о транспорте Белград–Нови-Сад: билеты от 640 динаров, время в пути 1–2ч, сравнение автобуса и поезда, актуальные рейсы.',
        'bg': 'Всичко за транспорта Белград–Нови Сад: цени на билетите от 640 RSD, време за пътуване 1–2ч, сравнение между автобус и влак и актуални тръгвания.',
    },
    'guides.beograd_ns.p1': {
        'sr': 'Beograd i Novi Sad razdvaja svega 90 km auto-putom, a taj rastojanje možete prevaliti autobusom, vozom ili privatnim prevozom. '
              'Ovo je najpopularnija domaća linija — dnevno saobraća više od 30 polazaka, a cene su pristupačne za svaki budžet.',
        'en': 'Belgrade and Novi Sad are only 90 km apart by motorway, and you can cover that distance by bus, train or private transport. '
              'This is the most popular domestic route — over 30 departures run daily at prices to suit every budget.',
        'ru': 'Белград и Нови-Сад разделяют всего 90 км по автостраде. Добраться можно автобусом, поездом или на машине. '
              'Это самый популярный внутренний маршрут: более 30 рейсов в день по доступным ценам.',
        'bg': 'Белград и Нови Сад са отдалечени само на 90 км по магистралата, а това разстояние може да се измине с автобус, влак или личен превоз. Това е най-популярната вътрешна линия — дневно има над 30 курса, а цените са достъпни за всеки бюджет.',
    },
    'guides.beograd_ns.h2_options': {
        'sr': 'Opcije prevoza',
        'en': 'Transport options',
        'ru': 'Варианты транспорта',
        'bg': 'Варианти за превоз',
    },
    'guides.beograd_ns.p2': {
        'sr': '<strong>Autobus</strong> — najčešći izbor. Lasta, Jugoprevoz i drugi prevoznici voze svakih sat-dva tokom dana i noći. '
              'Polasci su sa Beogradske autobuske stanice (BAS), a dolasak na Novi Sad AS. Vreme vožnje: 60–90 minuta.<br><br>'
              '<strong>Voz</strong> — Srbija Voz ima nekoliko polazaka dnevno, vreme vožnje oko 1h 30min. '
              'Pojedini polasci su besplatni za putnike sa kartom daljinskog voza.<br><br>'
              '<strong>BlaBlaCar / taxi</strong> — fleksibilno, ali skuplje. Idealno ako putujete u grupi.',
        'en': '<strong>Bus</strong> — the most common choice. Lasta, Jugoprevoz and other carriers run every hour or two day and night. '
              'Departures from Belgrade Bus Station (BAS), arriving at Novi Sad Bus Station. Travel time: 60–90 minutes.<br><br>'
              '<strong>Train</strong> — Srbija Voz has several daily departures, travel time around 1h 30min. '
              'Some trips are free for passengers with an intercity train ticket.<br><br>'
              '<strong>BlaBlaCar / taxi</strong> — flexible but more expensive. Ideal for groups.',
        'ru': '<strong>Автобус</strong> — самый распространённый вариант. Lasta, Jugoprevoz и другие перевозчики ходят каждые час-два круглосуточно. '
              'Отправление с Белградского автовокзала (BAS), прибытие на Новисадский автовокзал. Время в пути: 60–90 минут.<br><br>'
              '<strong>Поезд</strong> — у Srbija Voz несколько рейсов в день, время в пути около 1ч 30мин. '
              'Некоторые поездки бесплатны для пассажиров с билетом на дальний поезд.<br><br>'
              '<strong>BlaBlaCar / такси</strong> — гибко, но дороже. Идеально для поездки группой.',
        'bg': '<strong>Автобус</strong> — най-честият избор. Lasta, Jugoprevoz и други превозвачи возят на всеки час-два, денем и нощем. Тръгването е от Белградската автобусна гара (BAS), а пристигането — на автогарата в Нови Сад. Времетраене на пътуването: 60–90 минути.<br><br><strong>Влак</strong> — Srbija Voz предлага няколко курса дневно, времетраене около 1 ч. и 30 мин. Някои курсове са безплатни за пътници с билет за далечен влак.<br><br><strong>BlaBlaCar / такси</strong> — гъвкаво, но по-скъпо. Идеално, ако пътувате в група.',
    },
    'guides.beograd_ns.h2_price': {
        'sr': 'Cene karata',
        'en': 'Ticket prices',
        'ru': 'Цены на билеты',
        'bg': 'Цени на билетите',
    },
    'guides.beograd_ns.p3': {
        'sr': 'Autobuska karta košta između <strong>640 i 1 050 RSD</strong> (5–9 €) u zavisnosti od prevoznika i polaska. '
              'Noćni polasci i polasci manjim prevoznicima su često jeftiniji. '
              'Voz Srbija Voz — cena varira, ali postoje povoljne dnevne karte. '
              'Kupovina karte online ili direktno na blagajni — nema razlike u ceni.',
        'en': 'A bus ticket costs between <strong>640 and 1,050 RSD</strong> (5–9 €) depending on the carrier and departure. '
              'Night departures and smaller carriers are often cheaper. '
              'Srbija Voz train — price varies but affordable daily tickets are available. '
              'Buying a ticket online or at the counter makes no difference in price.',
        'ru': 'Автобусный билет стоит от <strong>640 до 1 050 динаров</strong> (5–9 €) в зависимости от перевозчика и рейса. '
              'Ночные рейсы и небольшие перевозчики зачастую дешевле. '
              'Поезд Srbija Voz — цена варьируется, но есть доступные дневные билеты. '
              'Разницы между онлайн-покупкой и кассой нет.',
        'bg': 'Автобусният билет струва между <strong>640 и 1 050 RSD</strong> (5–9 €) в зависимост от превозвача и курса. Нощните курсове и тези с по-малки превозвачи често са по-евтини. Влакът на Srbija Voz — цената варира, но има изгодни дневни билети. Купуването на билет онлайн или на гишето — няма разлика в цената.',
    },
    'guides.beograd_ns.h2_tips': {
        'sr': 'Korisni saveti',
        'en': 'Useful tips',
        'ru': 'Полезные советы',
        'bg': 'Полезни съвети',
    },
    'guides.beograd_ns.p4': {
        'sr': '• Putujete vikendom ili praznikom? Kupite kartu unapred — popularni polasci se pune brzo.<br>'
              '• Autobuska stanica u Novom Sadu je u centru — lako se dolazi peške do Bulevara oslobođenja i tržnog centra.<br>'
              '• Noćni polasci (posle ponoći) su jeftiniji i dobra opcija ako vam nije hitno.<br>'
              '• Parkiranje u NS može biti skupo vikendom — autobus je pametnije rešenje.',
        'en': '• Travelling at the weekend or on a holiday? Buy your ticket in advance — popular departures fill up fast.<br>'
              '• Novi Sad Bus Station is in the centre — it\'s easy to walk to Bulevar oslobođenja and the shopping centre.<br>'
              '• Night departures (after midnight) are cheaper and a good option if you\'re not in a hurry.<br>'
              '• Parking in NS can be expensive at weekends — the bus is the smarter choice.',
        'ru': '• Едете в выходные или праздник? Купите билет заранее — популярные рейсы быстро заполняются.<br>'
              '• Автовокзал Нови-Сада находится в центре — до Бульвара освобождения и торгового центра пешком.<br>'
              '• Ночные рейсы (после полуночи) дешевле и подходят, если не торопитесь.<br>'
              '• Парковка в Нови-Саде в выходные дорогая — автобус выгоднее.',
        'bg': '• Пътувате през уикенда или на празник? Купете билет предварително — популярните курсове се запълват бързо.<br>• Автогарата в Нови Сад е в центъра — лесно се стига пеша до булевард „Освобождение“ и търговския център.<br>• Нощните курсове (след полунощ) са по-евтини и са добър вариант, ако не бързате.<br>• Паркирането в Нови Сад може да е скъпо през уикенда — автобусът е по-разумното решение.',
    },
    'guides.beograd_ns.h2_departures': {
        'sr': 'Aktuelni polasci',
        'en': 'Current departures',
        'ru': 'Актуальные рейсы',
        'bg': 'Актуални курсове',
    },
    'guides.beograd_ns.cta': {
        'sr': 'Pogledaj sve polaske',
        'en': 'View all departures',
        'ru': 'Смотреть все рейсы',
        'bg': 'Виж всички курсове',
    },

    # ── Guide: Prevoz do mora ──
    'guides.more.title': {
        'sr': 'Prevoz do mora iz Srbije {year} — Autobus, Cene, Saveti',
        'en': 'Transport to the Sea from Serbia {year} — Bus, Prices, Tips',
        'ru': 'Транспорт к морю из Сербии {year} — Автобус, Цены, Советы',
        'bg': 'Транспорт до морето от Сърбия {year} — Автобус, цени, съвети',
    },
    'guides.more.meta': {
        'sr': 'Kako doći do mora iz Beograda autobusom: Budva, Bar, Herceg Novi, Split, Dubrovnik — cene, vreme putovanja i letnji saveti.',
        'en': 'How to get to the sea from Belgrade by bus: Budva, Bar, Herceg Novi, Split, Dubrovnik — prices, travel times and summer tips.',
        'ru': 'Как добраться до моря из Белграда автобусом: Будва, Бар, Херцег-Нови, Сплит, Дубровник — цены, время в пути и советы на лето.',
        'bg': 'Как да стигнете до морето от Белград с автобус: Будва, Бар, Херцег Нови, Сплит, Дубровник — цени, време за пътуване и летни съвети.',
    },
    'guides.more.p1': {
        'sr': 'Leto je — i Beograd se prazni. Hiljade putnika svake sezone kreću prema Jadranskom i Jonskom moru, '
              'a autobus ostaje najpopularniji i najisplativiji način prevoza. '
              'Evo svega što treba da znate pre nego što krenete.',
        'en': 'It\'s summer — and Belgrade empties out. Thousands of passengers head to the Adriatic and Ionian Sea each season, '
              'and the bus remains the most popular and cost-effective way to travel. '
              'Here\'s everything you need to know before you set off.',
        'ru': 'Лето — и Белград пустеет. Тысячи пассажиров каждый сезон направляются к Адриатическому и Ионическому морям, '
              'а автобус остаётся самым популярным и выгодным способом добраться. '
              'Вот всё, что нужно знать перед отправлением.',
        'bg': 'Лято е — и Белград се изпразва. Всеки сезон хиляди пътници потеглят към Адриатическо и Йонийско море, а автобусът остава най-популярният и най-изгоден начин на придвижване. Ето всичко, което трябва да знаете, преди да тръгнете.',
    },
    'guides.more.h2_destinations': {
        'sr': 'Najpopularnije destinacije i cene',
        'en': 'Most popular destinations and prices',
        'ru': 'Самые популярные направления и цены',
        'bg': 'Най-популярни дестинации и цени',
    },
    'guides.more.p2': {
        'sr': 'Iz Beograda saobraćaju direktne linije do svih glavnih primorskih gradova. '
              'Cene su okvirne i mogu se razlikovati po prevozniku i sezoni:',
        'en': 'Direct lines from Belgrade run to all the main coastal towns. '
              'Prices are approximate and may vary by carrier and season:',
        'ru': 'Из Белграда ходят прямые рейсы во все основные прибрежные города. '
              'Цены приблизительные и могут варьироваться в зависимости от перевозчика и сезона:',
        'bg': 'От Белград има директни линии до всички основни крайморски градове. Цените са ориентировъчни и може да варират в зависимост от превозвача и сезона:',
    },
    'guides.more.h2_tips': {
        'sr': 'Saveti za letnje putovanje',
        'en': 'Summer travel tips',
        'ru': 'Советы для летних поездок',
        'bg': 'Съвети за лятното пътуване',
    },
    'guides.more.p3': {
        'sr': '• <strong>Kupite kartu 2–3 nedelje unapred</strong> — leto je vrhunac sezone, autobuske karte nestaju brzo posebno za vikende.<br>'
              '• <strong>Noćni polasci</strong> su zlatni standard: krećete uveče, budite se na moru. Uštedite na hotelu.<br>'
              '• <strong>Pratite prtljag</strong> — svaki kofer u prtljažniku autobus naplaćuje posebno (obično 200–300 RSD).<br>'
              '• <strong>Crna Gora</strong>: Budva je najpopularnija, ali Bar ima bolji autobuski terminal i niže cene.<br>'
              '• <strong>Hrvatska</strong>: Split i Dubrovnik zahtevaju granični prelaz — pripremite dokumenta na vidljivom mestu.',
        'en': '• <strong>Buy your ticket 2–3 weeks in advance</strong> — summer is peak season and bus tickets sell out fast, especially at weekends.<br>'
              '• <strong>Night departures</strong> are the golden standard: leave in the evening, wake up by the sea. Save on accommodation.<br>'
              '• <strong>Watch your luggage</strong> — each bag in the hold is charged separately (usually 200–300 RSD).<br>'
              '• <strong>Montenegro</strong>: Budva is the most popular, but Bar has a better bus terminal and lower prices.<br>'
              '• <strong>Croatia</strong>: Split and Dubrovnik require a border crossing — keep your documents within easy reach.',
        'ru': '• <strong>Купите билет за 2–3 недели</strong> — лето пиковый сезон, автобусные билеты раскупаются быстро, особенно на выходные.<br>'
              '• <strong>Ночные рейсы</strong> — золотой стандарт: уезжаете вечером, просыпаетесь у моря. Экономите на ночлеге.<br>'
              '• <strong>Следите за багажом</strong> — каждый чемодан в багажном отсеке оплачивается отдельно (обычно 200–300 динаров).<br>'
              '• <strong>Черногория</strong>: Будва самая популярная, но Бар лучший терминал и цены ниже.<br>'
              '• <strong>Хорватия</strong>: Сплит и Дубровник — пограничный переход, держите документы под рукой.',
        'bg': '• <strong>Купете билета 2–3 седмици предварително</strong> — лятото е върхът на сезона и автобусните билети се изчерпват бързо, особено за уикендите.<br>• <strong>Нощните тръгвания</strong> са златният стандарт: тръгвате вечерта, а се събуждате на морето. Спестявате от хотел.<br>• <strong>Внимавайте с багажа</strong> — всеки куфар в багажното отделение се таксува отделно от автобуса (обикновено 200–300 RSD).<br>• <strong>Черна гора</strong>: Будва е най-популярна, но Бар има по-добър автобусен терминал и по-ниски цени.<br>• <strong>Хърватия</strong>: Сплит и Дубровник изискват граничен преход — подгответе документите на видимо място.',
    },
    'guides.more.h2_routes': {
        'sr': 'Aktuelne linije do mora',
        'en': 'Current sea routes',
        'ru': 'Актуальные маршруты к морю',
        'bg': 'Актуални линии до морето',
    },
    'guides.more.cta': {
        'sr': 'Pretraži karte za more',
        'en': 'Search sea tickets',
        'ru': 'Найти билеты к морю',
        'bg': 'Търсене на билети за морето',
    },

    # ── Guide: FlixBus Srbija ──
    'guides.tramvaj_bg.title': {
        'sr': 'Tramvaj Beograd {year}: sve tramvajske linije i red vožnje',
        'en': 'Belgrade tram {year}: all tram lines and schedule',
        'ru': 'Трамвай Белград {year}: все трамвайные линии и расписание',
        'bg': 'Трамвай Белград {year}: всички трамвайни линии и разписание',
    },
    'guides.tramvaj_bg.meta': {
        'sr': 'Sve tramvajske linije u Beogradu — kompletna lista tramvaja sa redom vožnje, stajalištima i mapom trase. Tramvajska mreža grada na jednom mestu.',
        'en': 'All tram lines in Belgrade — the complete list of trams with schedules, stops and route maps. The city tram network in one place.',
        'ru': 'Все трамвайные линии Белграда — полный список трамваев с расписанием, остановками и картой маршрута. Трамвайная сеть города в одном месте.',
        'bg': 'Всички трамвайни линии в Белград — пълен списък на трамваите с разписание, спирки и карта на маршрута. Трамвайната мрежа на града на едно място.',
    },
    'guides.tramvaj_bg.p1': {
        'sr': 'U Beogradu tramvaji saobraćaju na {count} linija koje povezuju centar grada i druge delove. Ispod su sve tramvajske linije sa direktnim linkom na red vožnje i stajališta.',
        'en': 'Belgrade has {count} tram lines connecting the city centre with other parts of town. Below are all the tram lines with a direct link to their schedule and stops.',
        'ru': 'В Белграде трамваи ходят по {count} линиям, связывая центр города с другими районами. Ниже все трамвайные линии со ссылкой на расписание и остановки.',
        'bg': 'В Белград трамваите се движат по {count} линии, които свързват центъра на града с останалите части. По-долу са всички трамвайни линии с директен линк към разписанието и спирките.',
    },
    'guides.tramvaj_bg.h2_lines': {
        'sr': 'Sve tramvajske linije u Beogradu',
        'en': 'All Belgrade tram lines',
        'ru': 'Все трамвайные линии Белграда',
        'bg': 'Всички трамвайни линии в Белград',
    },
    'guides.tramvaj_bg.p_lines': {
        'sr': 'Kliknite na liniju za tačan red vožnje, stajališta i mapu trase:',
        'en': 'Tap a line for its exact schedule, stops and route map:',
        'ru': 'Нажмите на линию для точного расписания, остановок и карты маршрута:',
        'bg': 'Кликнете върху линията за точното разписание, спирките и картата на маршрута:',
    },
    'guides.tramvaj_bg.line_prefix': {
        'sr': 'Linija', 'en': 'Line', 'ru': 'Линия',
        'bg': 'Линия',
    },
    'guides.tramvaj_bg.h2_tips': {
        'sr': 'Korisni saveti',
        'en': 'Useful tips',
        'ru': 'Полезные советы',
        'bg': 'Полезни съвети',
    },
    'guides.tramvaj_bg.p_tips': {
        'sr': 'Tačan red vožnje i učestalost tramvaja proverite na stranici svake linije — raspored se razlikuje radnim danom i vikendom. Noću mrežu preuzimaju noćne autobuske linije.',
        'en': 'Check each tram\'s exact schedule and frequency on its line page — the timetable differs on weekdays and weekends. At night the network is covered by night bus lines.',
        'ru': 'Точное расписание и частоту трамваев смотрите на странице каждой линии — расписание отличается в будни и выходные. Ночью сеть обслуживают ночные автобусные линии.',
        'bg': 'Точното разписание и честотата на трамваите проверявайте на страницата на всяка линия — графикът се различава в работни дни и през уикенда. Нощем мрежата се поема от нощните автобусни линии.',
    },
    'guides.aerodrom_bg.title': {
        'sr': 'Kako doći do aerodroma Beograd {year}: autobus i prevoz',
        'en': 'How to get to Belgrade airport {year}: bus and transport',
        'ru': 'Как добраться до аэропорта Белграда {year}: автобус и транспорт',
        'bg': 'Как да стигнете до летище Белград {year}: автобус и транспорт',
    },
    'guides.aerodrom_bg.meta': {
        'sr': 'Gradski autobus do aerodroma „Nikola Tesla“ iz Beograda — linije 72, A1 (ekspres), 600, 607 i noćna 72N, sa redom vožnje i stajalištima.',
        'en': 'City bus to „Nikola Tesla“ airport from Belgrade — lines 72, A1 (express), 600, 607 and night line 72N, with schedules and stops.',
        'ru': 'Городской автобус до аэропорта «Никола Тесла» из Белграда — линии 72, A1 (экспресс), 600, 607 и ночная 72N, с расписанием и остановками.',
        'bg': 'Градски автобус до летище „Никола Тесла“ от Белград — линии 72, A1 (експресна), 600, 607 и нощна 72N, с разписание и спирки.',
    },
    'guides.aerodrom_bg.p1': {
        'sr': 'Do beogradskog aerodroma „Nikola Tesla“ iz grada vodi {count} linija gradskog prevoza, pa ne morate na taksi. Ispod su sve linije sa direktnim linkom na red vožnje i stajališta.',
        'en': 'There are {count} city-transport lines from Belgrade to „Nikola Tesla“ airport, so you don\'t need a taxi. Below are all the lines with a direct link to their schedule and stops.',
        'ru': 'До белградского аэропорта «Никола Тесла» из города идёт {count} линий городского транспорта, так что такси не обязательно. Ниже все линии со ссылкой на расписание и остановки.',
        'bg': 'До белградското летище „Никола Тесла“ от града водят {count} линии на градския транспорт, така че не се налага да вземате такси. По-долу ще намерите всички линии с директен линк към разписанието и спирките.',
    },
    'guides.aerodrom_bg.h2_lines': {
        'sr': 'Linije do aerodroma „Nikola Tesla“',
        'en': 'Lines to „Nikola Tesla“ airport',
        'ru': 'Линии до аэропорта «Никола Тесла»',
        'bg': 'Линии до летище „Никола Тесла“',
    },
    'guides.aerodrom_bg.p_lines': {
        'sr': 'Kliknite na liniju za tačan red vožnje, stajališta i mapu trase:',
        'en': 'Tap a line for its exact schedule, stops and route map:',
        'ru': 'Нажмите на линию для точного расписания, остановок и карты маршрута:',
        'bg': 'Кликнете върху линията, за да видите точното разписание, спирките и картата на маршрута:',
    },
    'guides.aerodrom_bg.line_prefix': {
        'sr': 'Linija', 'en': 'Line', 'ru': 'Линия',
        'bg': 'Линия',
    },
    'guides.aerodrom_bg.h2_which': {
        'sr': 'Koju liniju izabrati',
        'en': 'Which line to choose',
        'ru': 'Какую линию выбрать',
        'bg': 'Коя линия да изберете',
    },
    'guides.aerodrom_bg.p_which': {
        'sr': 'Linija 72 polazi sa Zelenog venca, a ekspres e-bus A1 sa Trga Slavija — obe idu pravo do aerodroma. Linije 600 (od Železničke stanice) i 607 (Banovo Brdo) povezuju druge delove grada. Noću do aerodroma saobraća linija 72N.',
        'en': 'Line 72 departs from Zeleni venac, and the express e-bus A1 from Trg Slavija — both go straight to the airport. Lines 600 (from the railway station) and 607 (Banovo Brdo) connect other parts of the city. At night, line 72N serves the airport.',
        'ru': 'Линия 72 отправляется с Zeleni venac, а экспресс e-bus A1 — с Trg Slavija; обе идут прямо в аэропорт. Линии 600 (от ж/д вокзала) и 607 (Banovo Brdo) связывают другие районы. Ночью в аэропорт ходит линия 72N.',
        'bg': 'Линия 72 тръгва от Зелени венац, а експресният електробус A1 — от площад Славия — и двете стигат направо до летището. Линиите 600 (от Железопътната гара) и 607 (Баново бърдо) свързват други части на града. През нощта до летището се движи линия 72N.',
    },
    'guides.aerodrom_bg.h2_tips': {
        'sr': 'Korisni saveti',
        'en': 'Useful tips',
        'ru': 'Полезные советы',
        'bg': 'Полезни съвети',
    },
    'guides.aerodrom_bg.p_tips': {
        'sr': 'Tačno vreme polaska i učestalost proverite na stranici svake linije — red vožnje se razlikuje radnim danom i vikendom. Ako putujete iz drugog grada u Srbiji, međugradske polaske ka Beogradu uporedite u našem pretraživaču.',
        'en': 'Check the exact departure time and frequency on each line\'s page — the schedule differs on weekdays and weekends. If you are travelling from another city in Serbia, compare intercity departures to Belgrade in our search.',
        'ru': 'Точное время отправления и частоту смотрите на странице каждой линии — расписание отличается в будни и выходные. Если вы едете из другого города Сербии, сравните междугородние рейсы до Белграда в нашем поиске.',
        'bg': 'Точния час на тръгване и честотата проверявайте на страницата на всяка линия — разписанието се различава в работни дни и през уикенда. Ако пътувате от друг град в Сърбия, сравнете междуградските курсове до Белград в нашата търсачка.',
    },
    'guides.nocni_bg.title': {
        'sr': 'Noćni autobus Beograd {year}: noćne linije i red vožnje',
        'en': 'Belgrade night bus {year}: all night lines and schedule',
        'ru': 'Ночной автобус Белград {year}: ночные линии и расписание',
        'bg': 'Нощен автобус Белград {year}: нощни линии и разписание',
    },
    'guides.nocni_bg.meta': {
        'sr': 'Sve noćne linije gradskog prevoza u Beogradu — kompletna lista noćnih autobusa, red vožnje i stajališta. Uključujući noćni prevoz do aerodroma.',
        'en': 'All Belgrade night-bus lines — the complete list of night buses with schedules and stops, including night transport to the airport.',
        'ru': 'Все ночные линии городского транспорта Белграда — полный список ночных автобусов, расписание и остановки, включая ночной транспорт до аэропорта.',
        'bg': 'Всички нощни линии на градския транспорт в Белград — пълен списък на нощните автобуси, разписанието и спирките. Включително нощен транспорт до летището.',
    },
    'guides.nocni_bg.p1': {
        'sr': 'U Beogradu noću saobraća {count} noćnih linija gradskog prevoza, koje preuzimaju mrežu kada dnevni autobusi, tramvaji i trolejbusi prestanu da voze. Polasci kreću sa centralnih čvorišta u gradu i pokrivaju sve delove Beograda i prigradska naselja.',
        'en': 'Belgrade has {count} night public-transport lines that take over the network once the daytime buses, trams and trolleybuses stop running. They depart from the central hubs in the city and reach every part of Belgrade and the suburbs.',
        'ru': 'В Белграде ночью работает {count} ночных линий городского транспорта, которые берут на себя сеть, когда дневные автобусы, трамваи и троллейбусы прекращают ходить. Рейсы отправляются с центральных узлов города и охватывают все районы Белграда и пригороды.',
        'bg': 'В Белград нощем се движат {count} нощни линии на градския транспорт, които поемат мрежата, когато дневните автобуси, трамваи и тролейбуси спрат да возят. Тръгванията са от централните възлови точки в града и покриват всички части на Белград и крайградските селища.',
    },
    'guides.nocni_bg.h2_lines': {
        'sr': 'Spisak noćnih linija u Beogradu',
        'en': 'List of Belgrade night lines',
        'ru': 'Список ночных линий Белграда',
        'bg': 'Списък на нощните линии в Белград',
    },
    'guides.nocni_bg.p_lines': {
        'sr': 'Kliknite na liniju za tačan red vožnje, stajališta i mapu trase:',
        'en': 'Tap a line for its exact schedule, stops and route map:',
        'ru': 'Нажмите на линию для точного расписания, остановок и карты маршрута:',
        'bg': 'Кликнете върху линията за точното разписание, спирките и картата на маршрута:',
    },
    'guides.nocni_bg.line_prefix': {
        'sr': 'Linija', 'en': 'Line', 'ru': 'Линия',
        'bg': 'Линия',
    },
    'guides.nocni_bg.h2_airport': {
        'sr': 'Noćni prevoz do aerodroma',
        'en': 'Night transport to the airport',
        'ru': 'Ночной транспорт до аэропорта',
        'bg': 'Нощен превоз до летището',
    },
    'guides.nocni_bg.p_airport': {
        'sr': 'Do aerodroma „Nikola Tesla“ noću saobraća i noćna linija',
        'en': 'The „Nikola Tesla“ airport is also served at night by night line',
        'ru': 'До аэропорта «Никола Тесла» ночью ходит и ночная линия',
        'bg': 'До летище „Никола Тесла“ нощем се движи и нощна линия',
    },
    'guides.nocni_bg.h2_tips': {
        'sr': 'Korisni saveti',
        'en': 'Useful tips',
        'ru': 'Полезные советы',
        'bg': 'Полезни съвети',
    },
    'guides.nocni_bg.p_tips': {
        'sr': 'Noćne linije obično voze ređe od dnevnih, pa unapred proverite vreme polaska na stranici izabrane linije. Glavna polazna mesta u centru su Trg republike, Studentski trg i Trg Slavija. Za putovanja van Beograda uporedite i međugradske polaske u našem pretraživaču.',
        'en': 'Night lines usually run less frequently than daytime ones, so check the departure time on the line\'s page in advance. The main central departure points are Trg republike, Studentski trg and Trg Slavija. For trips outside Belgrade, compare intercity departures in our search too.',
        'ru': 'Ночные линии обычно ходят реже дневных, поэтому заранее проверьте время отправления на странице нужной линии. Главные точки отправления в центре — Trg republike, Studentski trg и Trg Slavija. Для поездок за пределы Белграда сравните и междугородние рейсы в нашем поиске.',
        'bg': 'Нощните линии обикновено се движат по-рядко от дневните, затова проверете предварително часа на тръгване на страницата на избраната линия. Основните тръгвания в центъра са от площад Република, Студентски площад и площад Славия. За пътувания извън Белград сравнете и междуградските тръгвания в нашата търсачка.',
    },
    'guides.flixbus.title': {
        'sr': 'FlixBus Srbija {year} — Linije, Cene i Poređenje',
        'en': 'FlixBus Serbia {year} — Routes, Prices and Comparison',
        'ru': 'FlixBus Сербия {year} — Маршруты, Цены и Сравнение',
        'bg': 'FlixBus Сърбия {year} — Линии, цени и сравнение',
    },
    'guides.flixbus.meta': {
        'sr': 'FlixBus linije kroz Srbiju, poređenje sa Lastom i BEX-om — kad je FlixBus jeftiniji i kad da birate domaći prevoz.',
        'en': 'FlixBus routes through Serbia, comparison with Lasta and BEX — when FlixBus is cheaper and when to choose a local carrier.',
        'ru': 'Маршруты FlixBus через Сербию, сравнение с Lasta и BEX — когда FlixBus дешевле и когда выбрать местного перевозчика.',
        'bg': 'Линии на FlixBus през Сърбия, сравнение с Lasta и BEX — кога FlixBus е по-евтин и кога да изберете местен превозвач.',
    },
    'guides.flixbus.p1': {
        'sr': 'FlixBus je 2019. ušao na srpsko tržište i od tada nudi međunarodne i tranzitne linije kroz Srbiju. '
              'Zeleni autobusi su postali prepoznatljivi, ali da li su uvek i najjeftiniji? '
              'Upored smo FlixBus sa domaćim prevoznicima da biste mogli da donesete pravu odluku.',
        'en': 'FlixBus entered the Serbian market in 2019 and has since offered international and transit routes through Serbia. '
              'The green buses have become a familiar sight, but are they always the cheapest option? '
              'We\'ve compared FlixBus with local carriers so you can make the right choice.',
        'ru': 'FlixBus вышел на сербский рынок в 2019 году и с тех пор предлагает международные и транзитные маршруты через Сербию. '
              'Зелёные автобусы стали узнаваемы, но всегда ли они самые дешёвые? '
              'Мы сравнили FlixBus с местными перевозчиkami, чтобы вы приняли правильное решение.',
        'bg': 'FlixBus навлезе на сръбския пазар през 2019 г. и оттогава предлага международни и транзитни линии през Сърбия. Зелените автобуси станаха разпознаваеми, но винаги ли са и най-евтини? Сравнихме FlixBus с местните превозвачи, за да можете да вземете правилното решение.',
    },
    'guides.flixbus.h2_lines': {
        'sr': 'FlixBus linije koje prolaze kroz Srbiju',
        'en': 'FlixBus routes through Serbia',
        'ru': 'Маршруты FlixBus через Сербию',
        'bg': 'Линии на FlixBus през Сърбия',
    },
    'guides.flixbus.p2': {
        'sr': 'FlixBus ne nudi domaći prevoz unutar Srbije, ali saobraća na brojnim međunarodnim linijama koje prolaze kroz Beograd:<br><br>'
              '• <strong>Beograd → Budimpešta</strong> (4–5h, od ~15 €)<br>'
              '• <strong>Beograd → Beč</strong> (8h, od ~20 €)<br>'
              '• <strong>Beograd → Zagreb</strong> (5h, od ~12 €)<br>'
              '• <strong>Beograd → Ljubljana</strong> (7h, od ~15 €)<br>'
              '• <strong>Beograd → Skoplje</strong> (4h, od ~10 €)<br><br>'
              'Polasci su sa BAS stanice u centru Beograda. Karte se kupuju isključivo online na <strong>flixbus.rs</strong>.',
        'en': 'FlixBus does not offer domestic transport within Serbia, but it operates on many international routes passing through Belgrade:<br><br>'
              '• <strong>Belgrade → Budapest</strong> (4–5h, from ~€15)<br>'
              '• <strong>Belgrade → Vienna</strong> (8h, from ~€20)<br>'
              '• <strong>Belgrade → Zagreb</strong> (5h, from ~€12)<br>'
              '• <strong>Belgrade → Ljubljana</strong> (7h, from ~€15)<br>'
              '• <strong>Belgrade → Skopje</strong> (4h, from ~€10)<br><br>'
              'Departures are from BAS station in central Belgrade. Tickets are purchased exclusively online at <strong>flixbus.rs</strong>.',
        'ru': 'FlixBus не предлагает внутренние перевозки по Сербии, но работает на международных маршрутах через Белград:<br><br>'
              '• <strong>Белград → Будапешт</strong> (4–5ч, от ~15 €)<br>'
              '• <strong>Белград → Вена</strong> (8ч, от ~20 €)<br>'
              '• <strong>Белград → Загреб</strong> (5ч, от ~12 €)<br>'
              '• <strong>Белград → Любляна</strong> (7ч, от ~15 €)<br>'
              '• <strong>Белград → Скопье</strong> (4ч, от ~10 €)<br><br>'
              'Отправление с автовокзала BAS в центре Белграда. Билеты покупаются только онлайн на <strong>flixbus.rs</strong>.',
        'bg': 'FlixBus не предлага вътрешен превоз в Сърбия, но обслужва множество международни линии, минаващи през Белград:<br><br>• <strong>Белград → Будапеща</strong> (4–5h, от ~15 €)<br>• <strong>Белград → Виена</strong> (8h, от ~20 €)<br>• <strong>Белград → Загреб</strong> (5h, от ~12 €)<br>• <strong>Белград → Любляна</strong> (7h, от ~15 €)<br>• <strong>Белград → Скопие</strong> (4h, от ~10 €)<br><br>Тръгванията са от автогара BAS в центъра на Белград. Билети се купуват единствено онлайн на <strong>flixbus.rs</strong>.',
    },
    'guides.flixbus.h2_compare': {
        'sr': 'FlixBus vs domaći prevoz — kad šta birati',
        'en': 'FlixBus vs local carriers — when to choose what',
        'ru': 'FlixBus vs местные перевозчики — когда что выбрать',
        'bg': 'FlixBus срещу местния превоз — кога какво да изберете',
    },
    'guides.flixbus.p3': {
        'sr': '<strong>Izaberite FlixBus kada:</strong><br>'
              '• Putujete u inostranstvo (Mađarska, Austrija, Hrvatska) — FlixBus je često konkurentan u ceni i nudi udobne autobuse.<br>'
              '• Volite online rezervaciju sa mogućnošću promene karte.<br>'
              '• Putujete noću i cimate besplatnu Wi-Fi i USB punjač.<br><br>'
              '<strong>Izaberite domaći prevoz (Lasta, BEX, Niš-Ekspres) kada:</strong><br>'
              '• Putujete unutar Srbije — FlixBus ne pokriva ove destinacije.<br>'
              '• Idete na more (Crna Gora, Jadran) — domaći prevoznici imaju gustu mrežu primorskih linija.<br>'
              '• Kupujete kartu u poslednjem trenutku na blagajni.',
        'en': '<strong>Choose FlixBus when:</strong><br>'
              '• You\'re travelling abroad (Hungary, Austria, Croatia) — FlixBus is often competitive on price and offers comfortable coaches.<br>'
              '• You prefer online booking with the option to change your ticket.<br>'
              '• You\'re travelling at night and value free Wi-Fi and a USB charger.<br><br>'
              '<strong>Choose a local carrier (Lasta, BEX, Niš-Ekspres) when:</strong><br>'
              '• You\'re travelling within Serbia — FlixBus doesn\'t cover these destinations.<br>'
              '• You\'re heading to the sea (Montenegro, Adriatic) — local carriers have a dense network of coastal routes.<br>'
              '• You\'re buying a last-minute ticket at the counter.',
        'ru': '<strong>Выбирайте FlixBus, когда:</strong><br>'
              '• Едете за границу (Венгрия, Австрия, Хорватия) — FlixBus часто конкурентен по цене и предлагает комфортные автобусы.<br>'
              '• Предпочитаете онлайн-бронирование с возможностью изменить билет.<br>'
              '• Едете ночью и цените бесплатный Wi-Fi и USB-зарядку.<br><br>'
              '<strong>Выбирайте местного перевозчика (Lasta, BEX, Niš-Ekspres), когда:</strong><br>'
              '• Путешествуете внутри Сербии — FlixBus эти направления не охватывает.<br>'
              '• Едете к морю (Черногория, Адриатика) — у местных перевозчиков густая сеть прибрежных маршрутов.<br>'
              '• Покупаете билет в последний момент на кассе.',
        'bg': '<strong>Изберете FlixBus, когато:</strong><br>• Пътувате в чужбина (Унгария, Австрия, Хърватия) — FlixBus често е конкурентен по цена и предлага удобни автобуси.<br>• Предпочитате онлайн резервация с възможност за промяна на билета.<br>• Пътувате нощем и цените безплатния Wi-Fi и USB зарядно.<br><br><strong>Изберете местен превоз (Lasta, BEX, Niš-Ekspres), когато:</strong><br>• Пътувате в рамките на Сърбия — FlixBus не покрива тези дестинации.<br>• Пътувате към морето (Черна гора, Адриатика) — местните превозвачи имат гъста мрежа от крайморски линии.<br>• Купувате билет в последния момент на гишето.',
    },
    'guides.flixbus.h2_tips': {
        'sr': 'Saveti za putovanje FlixBusom',
        'en': 'Tips for travelling with FlixBus',
        'ru': 'Советы для поездок на FlixBus',
        'bg': 'Съвети за пътуване с FlixBus',
    },
    'guides.flixbus.p4': {
        'sr': '• Karte su najjeftinije ako kupujete 4–6 nedelja unapred.<br>'
              '• FlixBus ima program lojalnosti — skupljate poene za svaku kartu.<br>'
              '• Kašnjenja su moguća na tranzitnim linijama (autobus dolazi iz druge države).<br>'
              '• Prtljag: jedan komad u prtljažniku besplatno, ručni prtljag na sedištu.<br>'
              '• U Srbiji FlixBus nema sopstvene stanice — koristite BAS ili oznake na mapi na aplikaciji.',
        'en': '• Tickets are cheapest if you buy 4–6 weeks in advance.<br>'
              '• FlixBus has a loyalty programme — you earn points for every ticket.<br>'
              '• Delays are possible on transit routes (the bus is coming from another country).<br>'
              '• Luggage: one piece in the hold free of charge, hand luggage at your seat.<br>'
              '• In Serbia, FlixBus has no dedicated stations — use BAS or the map markers in the app.',
        'ru': '• Билеты дешевле всего за 4–6 недель до поездки.<br>'
              '• У FlixBus есть программа лояльности — баллы за каждый билет.<br>'
              '• Задержки возможны на транзитных маршрутах (автобус едет из другой страны).<br>'
              '• Багаж: одно место в багажном отсеке бесплатно, ручная кладь на сиденье.<br>'
              '• В Сербии у FlixBus нет своих станций — используйте BAS или маркеры на карте в приложении.',
        'bg': '• Билетите са най-евтини, ако ги купите 4–6 седмици предварително.<br>• FlixBus има програма за лоялност — събирате точки за всеки билет.<br>• Възможни са закъснения по транзитните линии (автобусът пристига от друга държава).<br>• Багаж: един куфар в багажното отделение безплатно, ръчен багаж на седалката.<br>• В Сърбия FlixBus няма собствени автогари — използвайте BAS или означенията на картата в приложението.',
    },
    'guides.flixbus.cta': {
        'sr': 'Pretraži domaće polaske',
        'en': 'Search local departures',
        'ru': 'Найти внутренние рейсы',
        'bg': 'Търсене на вътрешни курсове',
    },
    # ── Operator/Country FAQ ──

}

SUPPORTED_LANGS = ('sr', 'en', 'ru', 'bg')
DEFAULT_LANG = 'sr'


def get_text(key: str, lang: str = DEFAULT_LANG) -> str:
    """Get translated string. Falls back to Serbian, then to key itself."""
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get(DEFAULT_LANG) or key
