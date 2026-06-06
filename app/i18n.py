"""
Simple i18n system for Prevozni.

Usage in templates:  {{ _('nav.all_routes') }}
Usage in Python:     from app.i18n import get_text; get_text('nav.all_routes', 'en')

Supported languages: sr (default), en, ru
"""

TRANSLATIONS: dict[str, dict[str, str]] = {
    # ── Navigation ──
    'nav.all_routes': {
        'sr': 'Sve rute',
        'en': 'All routes',
        'ru': 'Все маршруты',
    },
    'nav.city_transport': {
        'sr': 'Gradski prevoz',
        'en': 'City transport',
        'ru': 'Городской транспорт',
    },
    'nav.search': {
        'sr': 'Pretraga',
        'en': 'Search',
        'ru': 'Поиск',
    },
    'nav.about': {
        'sr': 'O nama',
        'en': 'About',
        'ru': 'О нас',
    },
    'nav.menu': {
        'sr': 'Meni',
        'en': 'Menu',
        'ru': 'Меню',
    },
    'a11y.mobile_nav': {
        'sr': 'Donja navigacija',
        'en': 'Bottom navigation',
        'ru': 'Нижняя навигация',
    },
    'nav.home': {
        'sr': 'Početna',
        'en': 'Home',
        'ru': 'Главная',
    },
    'nav.routes': {
        'sr': 'Rute',
        'en': 'Routes',
        'ru': 'Маршруты',
    },
    'nav.city': {
        'sr': 'Gradski',
        'en': 'City',
        'ru': 'Город',
    },
    'nav.saved': {
        'sr': 'Sačuvano',
        'en': 'Saved',
        'ru': 'Избранное',
    },
    'nav.more': {
        'sr': 'Više',
        'en': 'More',
        'ru': 'Ещё',
    },
    'a11y.bottom_nav': {
        'sr': 'Glavna mobilna navigacija',
        'en': 'Primary mobile navigation',
        'ru': 'Основная мобильная навигация',
    },
    'browse.title': {
        'sr': 'Pregledaj sve',
        'en': 'Browse all',
        'ru': 'Смотреть все',
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
        'sr': 'Beograd, Novi Sad, Niš, Kragujevac',
        'en': 'Beograd, Novi Sad, Niš, Kragujevac',
        'ru': 'Белград, Нови-Сад, Ниш, Крагуевац',
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
    },
    'footer.navigation': {
        'sr': 'Navigacija',
        'en': 'Navigation',
        'ru': 'Навигация',
    },
    'footer.popular_routes': {
        'sr': 'Popularne rute',
        'en': 'Popular routes',
        'ru': 'Популярные маршруты',
    },
    'footer.cities': {
        'sr': 'Gradovi',
        'en': 'Cities',
        'ru': 'Города',
    },
    'footer.carriers': {
        'sr': 'Prevoznici',
        'en': 'Carriers',
        'ru': 'Перевозчики',
    },
    'footer.stations': {
        'sr': 'Stanice',
        'en': 'Stations',
        'ru': 'Станции',
    },
    'footer.about': {
        'sr': 'O nama',
        'en': 'About us',
        'ru': 'О нас',
    },
    'footer.contact': {
        'sr': 'Kontakt',
        'en': 'Contact',
        'ru': 'Контакт',
    },
    'footer.copyright': {
        'sr': 'Sva prava zadržana.',
        'en': 'All rights reserved.',
        'ru': 'Все права защищены.',
    },
    'footer.privacy': {
        'sr': 'Privatnost',
        'en': 'Privacy',
        'ru': 'Конфиденциальность',
    },
    'privacy.title': {
        'sr': 'Politika privatnosti',
        'en': 'Privacy Policy',
        'ru': 'Политика конфиденциальности',
    },
    'privacy.intro': {
        'sr': 'Prevozni poštuje vašu privatnost. Ova stranica objašnjava koje podatke prikupljamo i kako ih koristimo.',
        'en': 'Prevozni respects your privacy. This page explains what data we collect and how we use it.',
        'ru': 'Prevozni уважает вашу конфиденциальность. Здесь описано, какие данные мы собираем и как используем.',
    },
    'privacy.cookies_h': {
        'sr': 'Kolačići',
        'en': 'Cookies',
        'ru': 'Cookies',
    },
    'privacy.cookies_ab_h': {
        'sr': 'A/B testiranje',
        'en': 'A/B testing',
        'ru': 'A/B-тестирование',
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
    },
    'privacy.cookies_body': {
        'sr': 'Koristimo samo neophodne kolačiće (npr. CSRF token). Ne koristimo reklamne niti praćeće kolačiće trećih strana.',
        'en': 'We use only essential cookies (e.g. CSRF token). No third-party advertising or tracking cookies.',
        'ru': 'Мы используем только необходимые cookies (например, CSRF-токен). Никаких рекламных или трекинговых cookies третьих сторон.',
    },
    'privacy.analytics_h': {
        'sr': 'Analitika',
        'en': 'Analytics',
        'ru': 'Аналитика',
    },
    'privacy.analytics_body': {
        'sr': 'Koristimo Umami analitiku — anonimne, agregirane statistike poseta bez kolačića i bez praćenja pojedinaca.',
        'en': 'We use Umami analytics — anonymous, aggregated page view statistics with no cookies and no individual tracking.',
        'ru': 'Мы используем Umami — анонимную агрегированную статистику посещений без cookies и отслеживания пользователей.',
    },
    'privacy.contact_h': {
        'sr': 'Kontakt forma',
        'en': 'Contact form',
        'ru': 'Контактная форма',
    },
    'privacy.contact_body': {
        'sr': 'Poruke iz kontakt forme se šalju preko Telegram bota i čuvaju u logovima radi odgovora. Ne delimo ih sa trećim stranama.',
        'en': 'Messages from the contact form are sent via a Telegram bot and stored in logs so we can reply. They are not shared with third parties.',
        'ru': 'Сообщения из контактной формы отправляются через Telegram-бот и сохраняются в логах для ответа. Третьим лицам не передаются.',
    },
    'privacy.rights_h': {
        'sr': 'Vaša prava (GDPR)',
        'en': 'Your rights (GDPR)',
        'ru': 'Ваши права (GDPR)',
    },
    'privacy.rights_body': {
        'sr': 'Imate pravo pristupa, ispravke i brisanja podataka. Za zahteve pišite na info@prevozni.com.',
        'en': 'You have the right to access, rectify and erase your data. Email info@prevozni.com for requests.',
        'ru': 'Вы имеете право на доступ, исправление и удаление данных. Запросы — на info@prevozni.com.',
    },
    'footer.disclaimer': {
        'sr': 'Podaci su informativnog karaktera i preuzeti iz javno dostupnih izvora. Prevozni ne garantuje tačnost podataka — uvek proverite red vožnje direktno kod prevoznika. Ovaj sajt ne prodaje karte niti posreduje u prodaji prevoznih usluga.',
        'en': 'Data is for informational purposes and sourced from publicly available sources. Prevozni does not guarantee data accuracy — always check the schedule directly with the carrier. This site does not sell tickets.',
        'ru': 'Данные носят информационный характер и получены из открытых источников. Prevozni не гарантирует точность данных — всегда проверяйте расписание у перевозчика. Сайт не продает билеты.',
    },

    # ── Homepage ──
    'home.title': {
        'sr': 'Prevozni — Red Vožnje Srbija 2026: Autobus i Voz',
        'en': 'Prevozni — Serbia Bus & Train 2026: Schedules & Prices',
        'ru': 'Prevozni — Автобусы Сербии 2026: Расписание и Цены',
    },
    'home.meta': {
        'sr': 'Autobus i voz između gradova Srbije — red vožnje, cene od 350 din, 500+ ruta. Beograd, Novi Sad, Niš i region. Pronađi besplatno →',
        'en': 'Bus and train in Serbia 2026 — schedules, prices from 350 RSD, 500+ routes. Belgrade, Novi Sad, Niš. Find for free →',
        'ru': 'Автобусы и поезда по Сербии 2026 — расписание, цены от 350 din, 500+ маршрутов. Белград, Нови-Сад, Ниш. Бесплатно →',
    },
    'about.title_suffix': {
        'sr': 'Prevozni Srbija, misija i kontakt',
        'en': 'Prevozni Serbia, mission and contact',
        'ru': 'Prevozni Сербия, миссия и контакт',
    },
    'contact.meta': {
        'sr': 'Imate pitanje, sugestiju ili ste primetili grešku na Prevozni? Pišite nam na info@prevozni.com ili popunite kontakt formu. Odgovaramo u roku od 48 sati.',
        'en': 'Got a question, suggestion or spotted a bug on Prevozni? Email info@prevozni.com or use the contact form. We reply within 48 hours.',
        'ru': 'Есть вопрос, предложение или заметили ошибку на Prevozni? Напишите на info@prevozni.com или заполните контактную форму. Отвечаем в течение 48 часов.',
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
        'sr': 'Mi ne prodajemo karte i ne naplaćujemo pretragu. Kupovina se obavlja direktno na sajtovima prevoznika ili preko partnera kao što je Bookaway. Kada kliknete na dugme "Kupi" pored polaska, bićete prebačeni na sajt partnera — on prodaje kartu, a Prevozni može da dobije malu proviziju koja pokriva troškove održavanja sajta. Pregled raspored, poređenje prevoznika i cena ostaju besplatni.',
        'en': 'We don\'t sell tickets and we don\'t charge for search. Purchase happens directly on the carrier\'s site or via a partner like Bookaway. When you click "Buy" next to a departure you are taken to the partner\'s site — they sell the ticket, and Prevozni may receive a small commission that covers the cost of running this site. Browsing schedules, comparing carriers and prices stays free.',
        'ru': 'Мы не продаём билеты и не берём деньги за поиск. Покупка происходит напрямую на сайте перевозчика или через партнёра типа Bookaway. При клике на кнопку "Купить" рядом с рейсом вы попадаете на сайт партнёра — он продаёт билет, а Prevozni может получить небольшую комиссию, которая покрывает расходы на работу сайта. Просмотр расписаний, сравнение перевозчиков и цен остаются бесплатными.',
    },
    'about.sources_h': {
        'sr': 'Odakle dolaze podaci',
        'en': 'Where the data comes from',
        'ru': 'Откуда берутся данные',
    },
    'contact.intro_h': {
        'sr': 'Kako da nam pišete',
        'en': 'How to reach us',
        'ru': 'Как с нами связаться',
    },
    'contact.intro_p1': {
        'sr': 'Najbrži način: <strong>info@prevozni.com</strong>. Možete i da koristite formu ispod — poruka stiže u isti inbox + automatski u naš Telegram kanal za operativne stvari, pa je odgovor obično u roku od 24 sata (radnim danima) ili do 48 sati (vikendom i praznicima).',
        'en': 'Fastest channel: <strong>info@prevozni.com</strong>. You can also use the form below — it lands in the same inbox plus our ops Telegram channel, so typical response time is within 24 hours on weekdays, up to 48 hours on weekends and holidays.',
        'ru': 'Самый быстрый канал: <strong>info@prevozni.com</strong>. Также можно использовать форму ниже — сообщение попадает в тот же ящик плюс в наш оперативный Telegram-канал, поэтому обычно отвечаем в течение 24 часов по будням и до 48 часов по выходным и праздникам.',
    },
    'privacy.cookies_body2': {
        'sr': 'Koristimo isključivo kolačiće prve strane (eng. first-party cookies) za čuvanje vaših preferenci (jezik sajta, valuta za cene, sačuvane rute). Ne postavljamo marketinške kolačiće trećih strana, ne pratimo vas na drugim sajtovima, ne gradimo vaš profil za prodaju oglasnih agencija.',
        'en': 'We only use first-party cookies to remember your preferences (site language, currency display, saved routes). We do not set third-party marketing cookies, do not track you across other sites, and do not build profiles for sale to ad networks.',
        'ru': 'Мы используем только first-party cookies для сохранения ваших настроек (язык сайта, валюта цен, сохранённые маршруты). Мы не ставим маркетинговые cookies третьих сторон, не отслеживаем вас на других сайтах и не строим профили для продажи рекламным сетям.',
    },
    'privacy.analytics_body2': {
        'sr': 'Za razumevanje kako ljudi koriste Prevozni koristimo Umami — privacy-first analitiku koja ne koristi kolačiće i ne prikuplja lične identifikatore. Umami beleži agregatne statistike (broj poseta po stranici, dolazni izvori, tip uređaja) ali ne povezuje događaje sa individualnim korisnikom. Svi podaci ostaju na našem serveru; ne šalju se Google Analytics-u ili drugim trećim stranama.',
        'en': 'To understand how people use Prevozni we use Umami — privacy-first analytics that does not use cookies and does not collect personal identifiers. Umami records aggregate statistics (visits per page, referrers, device type) but does not tie events to individual users. All data stays on our server; it is not sent to Google Analytics or any third party.',
        'ru': 'Чтобы понимать как люди пользуются Prevozni мы используем Umami — privacy-first аналитику, которая не использует cookies и не собирает персональные идентификаторы. Umami записывает агрегированную статистику (визиты по страницам, источники переходов, тип устройства), но не связывает события с конкретным пользователем. Все данные остаются на нашем сервере, они не отправляются в Google Analytics или другие третьи стороны.',
    },
    'privacy.third_party_h': {
        'sr': 'Linkovi trećih strana',
        'en': 'Third-party links',
        'ru': 'Ссылки третьих сторон',
    },
    'privacy.third_party_body': {
        'sr': 'Prevozni sadrži linkove ka sajtovima prevoznika i partnera (Bookaway, BusTicket4.me i drugi). Kada kliknete na takav link, napuštate naš sajt i ulazite u politiku privatnosti tog partnera. Nismo odgovorni za njihove prakse — pročitajte njihovu politiku pre nego što unesete lične podatke ili kupite kartu. Mi možemo da dobijemo proviziju od partnera ako kupite preko linka sa našeg sajta; to nikad ne utiče na cenu koju vi plaćate.',
        'en': 'Prevozni contains links to carriers and partners (Bookaway, BusTicket4.me and others). When you click such a link you leave our site and enter that partner\'s privacy policy. We are not responsible for their practices — read their policy before entering personal data or buying a ticket. We may receive a commission from partners if you buy via a link on our site; this never affects the price you pay.',
        'ru': 'Prevozni содержит ссылки на сайты перевозчиков и партнёров (Bookaway, BusTicket4.me и другие). При клике на такую ссылку вы покидаете наш сайт и попадаете под политику конфиденциальности этого партнёра. Мы не отвечаем за их практики — прочитайте их политику перед вводом личных данных или покупкой билета. Мы можем получать комиссию от партнёров при покупке через нашу ссылку; это никак не влияет на цену которую вы платите.',
    },
    'privacy.affiliate_h': {
        'sr': 'Praćenje klikova na "Kupi" (Bookaway)',
        'en': 'Tracking of "Buy" (Bookaway) clicks',
        'ru': 'Отслеживание кликов по кнопке «Купить» (Bookaway)',
    },
    'privacy.adsense_h': {
        'sr': 'Google AdSense (reklame)',
        'en': 'Google AdSense (advertising)',
        'ru': 'Google AdSense (реклама)',
    },
    'privacy.adsense_body': {
        'sr': 'Na nekim stranicama prikazujemo reklame preko Google AdSense. Ako ste prihvatili sve kolačiće, AdSense može da koristi kolačiće trećih strana za personalizaciju reklama na osnovu vaše istorije pregleda na drugim sajtovima. Ako ste izabrali samo osnovne kolačiće, AdSense radi u režimu neperonalizovanih reklama (requestNonPersonalizedAds) — reklame se biraju na osnovu sadržaja stranice, a ne vašeg profila. AdSense automatski dobija minimalne podatke o pregledu (IP, user-agent) prema njihovoj <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener nofollow">politici reklamiranja</a>. Možete da isključite personalizaciju u <a href="https://adssettings.google.com/" target="_blank" rel="noopener nofollow">Google Ads Settings</a> u bilo kom trenutku.',
        'en': 'On some pages we display ads through Google AdSense. If you accepted all cookies, AdSense may use third-party cookies to personalise ads based on your browsing history across other sites. If you accepted only essential cookies, AdSense runs in non-personalised mode (requestNonPersonalizedAds) — ads are picked based on page content, not your profile. AdSense automatically receives minimal request data (IP, user-agent) per their <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener nofollow">advertising policy</a>. You can opt out of personalisation in <a href="https://adssettings.google.com/" target="_blank" rel="noopener nofollow">Google Ads Settings</a> at any time.',
        'ru': 'На некоторых страницах мы показываем рекламу через Google AdSense. Если вы приняли все cookies, AdSense может использовать сторонние cookies для персонализации рекламы на основе истории просмотров на других сайтах. Если вы выбрали только основные cookies, AdSense работает в режиме неперсонализированной рекламы (requestNonPersonalizedAds) — реклама подбирается по содержанию страницы, а не по вашему профилю. AdSense автоматически получает минимальные данные запроса (IP, user-agent) согласно их <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener nofollow">политике рекламы</a>. Отключить персонализацию можно в любой момент в <a href="https://adssettings.google.com/" target="_blank" rel="noopener nofollow">Google Ads Settings</a>.',
    },
    'privacy.reviews_h': {
        'sr': 'Korisničke recenzije',
        'en': 'User reviews',
        'ru': 'Пользовательские отзывы',
    },
    'privacy.reviews_body': {
        'sr': 'Ako ostavite recenziju rute (dugme „Ostavite vašu recenziju" na stranici rute), čuvamo vašu ocenu, tekst komentara i ime koje ste uneli — oni se javno prikazuju nakon moderacije. Email adresu ne čuvamo u otvorenom obliku: sa nje računamo sha256 hash sa solju radi provere autorstva (za brisanje recenzije) i identifikacije „proverenih" autora koji su ranije objavili 3+ odobrene recenzije. Pored toga čuvamo jezik (sr/en/ru), anonimizovani hash IP adrese, i vreme slanja — isključivo za zaštitu od spama i auditing. U svakom trenutku možete da zatražite brisanje svoje recenzije dugmetom „Zatraži brisanje" ispod svake recenzije; potvrđujete uneti istu email adresu kojom ste prvobitno poslali, a naš moderator soft-briše zapis u roku od 7 dana u skladu sa GDPR-om.',
        'en': 'If you leave a route review (via the "Leave your review" form), we store your rating, comment text, and the name you entered — these are shown publicly after moderation. Your email address is never stored in cleartext: we compute a salted sha256 hash of it for authorship checks (so you can request deletion later) and to identify "trusted" authors who have previously posted 3+ approved reviews. We also keep the submission language (sr/en/ru), a salted IP hash, and the timestamp — only for spam protection and audit. You can request deletion any time via the "Request deletion" button under each review; you prove ownership by re-entering the same email, and our moderator soft-deletes the record within 7 days per GDPR.',
        'ru': 'Если вы оставите отзыв о маршруте (через форму «Оставить отзыв»), мы храним оценку, текст комментария и указанное имя — они публикуются после модерации. Email в открытом виде не храним: вычисляем sha256-хэш с солью, чтобы позже проверить авторство (при запросе удаления) и опознать «проверенных» авторов, у которых уже опубликовано 3+ одобренных отзыва. Также храним язык отправки (sr/en/ru), хэш IP и время отправки — только для защиты от спама и аудита. В любой момент можно запросить удаление кнопкой «Запросить удаление» под каждым отзывом; вы подтверждаете владение, указав тот же email, а модератор мягко удалит запись в течение 7 дней согласно GDPR.',
    },
    'privacy.affiliate_body': {
        'sr': 'Kad kliknete na dugme "Kupi" koje vodi na Bookaway, beležimo minimalni zapis o kliku na sopstvenom serveru: identifikator rute (npr. beograd-budva), tip stranice sa koje ste kliknuli (katalog, detalj rute, pretraga), prevoznika, vreme polaska, anonimizovani hash vaše IP adrese (sha256 sa sol-tajnom koja se redovno menja) i osnovne tehničke podatke pretraživača. Ne beležimo sirovu IP adresu, ime, email niti bilo šta što može direktno da vas identifikuje. Ove zapise čuvamo maksimalno 90 dana u interne svrhe — da znamo koji delovi sajta ljudima stvarno pomažu da nađu kartu i da pravilno pripišemo proviziju od Bookaway-a. Isti zapisi se šalju i u našu analitiku (Umami) kao anonimni event "ba_click". Ako želite da vaši klikovi ne budu zabeleženi, uključite ad-blocker ili privatni mod u pretraživaču — naš sajt nastavlja da radi bez ovih zapisa.',
        'en': 'When you click a "Buy" button that goes to Bookaway, we keep a minimal click record on our own server: the route identifier (e.g. beograd-budva), the page type the click came from (catalog, route detail, search), the carrier, departure time, a salted sha256 hash of your IP (salt rotates regularly) and basic browser technical data. We do not store raw IPs, names, emails or anything directly identifying you. These records are kept for at most 90 days and used internally to understand which parts of the site actually help people find a ticket and to correctly attribute Bookaway commissions. The same events are mirrored to our analytics (Umami) as an anonymous "ba_click" event. If you prefer your clicks not to be recorded, use an ad-blocker or private browsing — the site works without these records.',
        'ru': 'Когда вы нажимаете кнопку «Купить», ведущую на Bookaway, мы сохраняем на нашем сервере минимальную запись: идентификатор маршрута (например beograd-budva), тип страницы с которой был клик (каталог, детали маршрута, поиск), перевозчика, время рейса, анонимизированный sha256-хэш вашего IP с регулярно меняющейся солью и базовые технические данные браузера. Мы не храним сырой IP, имя, email или что-либо прямо вас идентифицирующее. Эти записи хранятся не более 90 дней и используются внутренне — чтобы понимать какие части сайта реально помогают людям найти билет и корректно атрибутировать комиссии Bookaway. Эти же события отправляются в нашу аналитику (Umami) как анонимный event «ba_click». Если вы не хотите чтобы клики записывались — включите ad-blocker или приватный режим, сайт работает и без этих записей.',
    },
    'privacy.rights_body2': {
        'sr': 'Ako želite da zatražite izvoz, izmenu ili brisanje podataka (na primer vaše kontakt poruke), pošaljite zahtev na info@prevozni.com. Obradićemo ga u roku od 30 dana u skladu sa GDPR-om i srpskim Zakonom o zaštiti podataka o ličnosti. Nije potrebno da navodite razlog.',
        'en': 'If you want to request export, correction or deletion of your data (for example a contact form message you sent), email info@prevozni.com. We will process the request within 30 days in line with GDPR and the Serbian Personal Data Protection Act. You do not need to state a reason.',
        'ru': 'Если вы хотите запросить экспорт, исправление или удаление данных (например вашего сообщения из контактной формы), напишите на info@prevozni.com. Мы обработаем запрос в течение 30 дней в соответствии с GDPR и сербским законом о защите персональных данных. Причину указывать не обязательно.',
    },
    'privacy.changes_h': {
        'sr': 'Izmene ove politike',
        'en': 'Changes to this policy',
        'ru': 'Изменения этой политики',
    },
    'privacy.changes_body': {
        'sr': 'Ako nešto bitno promenimo (na primer dodamo novi analitički alat ili pustimo reklame), objavićemo novu verziju ove stranice i ažurirati datum ispod. Za suštinske izmene obavestićemo i preko banera na početnoj strani minimalno 14 dana unapred. Trenutna verzija: april 2026.',
        'en': 'If we change something material (for example add a new analytics tool or enable ads), we publish a new version of this page and update the date below. For substantive changes we also announce a homepage banner at least 14 days in advance. Current version: April 2026.',
        'ru': 'Если мы изменяем что-то существенное (например добавляем новый аналитический инструмент или включаем рекламу), мы публикуем новую версию этой страницы и обновляем дату ниже. Для существенных изменений также вывешиваем баннер на главной странице минимум за 14 дней. Текущая версия: апрель 2026.',
    },

    'contact.intro_p2': {
        'sr': 'Šta nam najviše pomaže: <strong>tačan URL stranice</strong> gde ste naišli na grešku, <strong>screenshot</strong> (ako je vizuelni bug) i <strong>naziv pretraživača i uređaja</strong>. Za predloge novih gradova ili ruta — napišite kuda biste voleli da putujete, ubrzavamo obogaćivanje podataka na osnovu stvarne potražnje.',
        'en': 'What helps us most: the <strong>exact URL</strong> where you hit the problem, a <strong>screenshot</strong> (for visual bugs), and the <strong>browser + device</strong> you are on. For feature requests or new cities/routes — tell us where you\'d like to travel; we prioritise data enrichment based on actual demand.',
        'ru': 'Что помогает больше всего: <strong>точный URL</strong> страницы где вы столкнулись с проблемой, <strong>скриншот</strong> (для визуальных багов) и <strong>браузер + устройство</strong>. Для предложений по новым городам или маршрутам — напишите куда вам хотелось бы поехать, мы приоритизируем обогащение данных по реальному спросу.',
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
    },
    'home.hero_subtitle': {
        'sr': 'Pronađite autobus, voz ili gradski prevoz na jednom mestu',
        'en': 'Find bus, train or city transport in one place',
        'ru': 'Найдите автобус, поезд или городской транспорт в одном месте',
    },
    'home.hero_sub_descriptive': {
        'sr': 'Autobus, voz i gradska mreža — Srbija, Crna Gora, BiH i region',
        'en': 'Bus, train and city transport — Serbia, Montenegro, BiH & region',
        'ru': 'Автобус, поезд и городской транспорт — Сербия, Черногория, БиГ и регион',
    },
    'home.hero_sub_feature_list': {
        'sr': '335 ruta · karta stajališta · 6 zemalja · besplatno',
        'en': '335 routes · stop map · 6 countries · free',
        'ru': '335 маршрутов · карта остановок · 6 стран · бесплатно',
    },
    'home.hero_sub_price_compare': {
        'sr': 'Uporedite cene Lasta, Niš-Ekspres i drugih — bez naknade',
        'en': 'Compare Lasta, Niš-Ekspres and other carriers — no fee',
        'ru': 'Сравните цены Lasta, Niš-Ekspres и других — без комиссии',
    },
    'home.search_from': {
        'sr': 'Odakle?',
        'en': 'From?',
        'ru': 'Откуда?',
    },
    'home.search_to': {
        'sr': 'Dokle?',
        'en': 'To?',
        'ru': 'Куда?',
    },
    'home.search_btn': {
        'sr': 'Pretraži',
        'en': 'Search',
        'ru': 'Найти',
    },
    'home.popular_routes': {
        'sr': 'Popularne rute',
        'en': 'Popular routes',
        'ru': 'Популярные маршруты',
    },
    'home.city_transport': {
        'sr': 'Gradski prevoz',
        'en': 'City transport',
        'ru': 'Городской транспорт',
    },
    'home.all_routes': {
        'sr': 'Sve rute',
        'en': 'All routes',
        'ru': 'Все маршруты',
    },

    # ── Common ──
    'common.departure': {
        'sr': 'Polazak',
        'en': 'Departure',
        'ru': 'Отправление',
    },
    'common.arrival': {
        'sr': 'Dolazak',
        'en': 'Arrival',
        'ru': 'Прибытие',
    },
    'common.duration': {
        'sr': 'Trajanje',
        'en': 'Duration',
        'ru': 'Время в пути',
    },
    'common.price': {
        'sr': 'Cena',
        'en': 'Price',
        'ru': 'Цена',
    },
    'common.carrier': {
        'sr': 'Prevoznik',
        'en': 'Carrier',
        'ru': 'Перевозчик',
    },
    'common.daily': {
        'sr': 'dnevno',
        'en': 'daily',
        'ru': 'ежедневно',
    },
    'common.lines': {
        'sr': 'linija',
        'en': 'lines',
        'ru': 'линий',
    },
    'common.stops': {
        'sr': 'stajališta',
        'en': 'stops',
        'ru': 'остановок',
    },
    'common.routes': {
        'sr': 'ruta',
        'en': 'routes',
        'ru': 'маршрутов',
    },
    'common.show_more': {
        'sr': 'Prikaži još',
        'en': 'Show more',
        'ru': 'Показать ещё',
    },
    'common.read_more': {
        'sr': 'Pročitaj više',
        'en': 'Read more',
        'ru': 'Читать дальше',
    },
    'common.read_less': {
        'sr': 'Sakri',
        'en': 'Read less',
        'ru': 'Свернуть',
    },
    'common.carriers': {
        'sr': 'prevoznika',
        'en': 'carriers',
        'ru': 'перевозчиков',
    },
    'common.languages': {
        'sr': 'jezika',
        'en': 'languages',
        'ru': 'языка',
    },
    'common.countries': {
        'sr': 'zemalja',
        'en': 'countries',
        'ru': 'стран',
    },
    'home.valueprop_aria': {
        'sr': 'Ključne brojke',
        'en': 'Key numbers',
        'ru': 'Ключевые цифры',
    },
    'home.valueprop_free': {
        'sr': 'Besplatno',
        'en': 'Free',
        'ru': 'бесплатно',
    },
    'ads.label': {
        'sr': 'Reklama',
        'en': 'Advertisement',
        'ru': 'Реклама',
    },
    'house_ad.popular_route_title': {
        'sr': 'Najtraženija ruta',
        'en': 'Most popular route',
        'ru': 'Самый популярный маршрут',
    },
    'house_ad.popular_route_sub': {
        'sr': 'Pogledaj polaske i cene',
        'en': 'See departures and prices',
        'ru': 'Посмотреть рейсы и цены',
    },
    'house_ad.destinations_title': {
        'sr': 'Top destinacije',
        'en': 'Top destinations',
        'ru': 'Топ направлений',
    },
    'house_ad.destinations_sub': {
        'sr': 'Balkan i Evropa autobusom',
        'en': 'Balkans & Europe by bus',
        'ru': 'Балканы и Европа автобусом',
    },
    'common.now': {
        'sr': 'sada',
        'en': 'now',
        'ru': 'сейчас',
    },
    'common.min': {
        'sr': 'min',
        'en': 'min',
        'ru': 'мин',
    },
    'common.h': {
        'sr': 'h',
        'en': 'h',
        'ru': 'ч',
    },
    'common.map_on_map': {
        'sr': 'stajališta na mapi',
        'en': 'stops on map',
        'ru': 'остановок на карте',
    },

    # ── Routes page ──
    'routes.title': {
        'sr': 'Sve autobuske i vozne rute u Srbiji',
        'en': 'All bus and train routes in Serbia',
        'ru': 'Все автобусные и железнодорожные маршруты Сербии',
    },
    'routes.departures': {
        'sr': 'polazaka',
        'en': 'departures',
        'ru': 'рейсов',
    },
    'routes.routes_label': {
        'sr': 'ruta',
        'en': 'routes',
        'ru': 'маршрутов',
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
    },
    'city.lines_count': {
        'sr': 'linija',
        'en': 'lines',
        'ru': 'линий',
    },
    'city.stops_on_map': {
        'sr': 'stajališta na mapi',
        'en': 'stops on map',
        'ru': 'остановок на карте',
    },
    'city.stops_label': {
        'sr': 'stajališta',
        'en': 'stops',
        'ru': 'остановок',
    },
    'city.tram_trolley_label': {
        'sr': 'tramvaja i trolejbusa',
        'en': 'tram + trolley lines',
        'ru': 'трамв./троллейб.',
    },
    'city.popular_stops': {
        'sr': 'Popularna stajališta',
        'en': 'Popular stops',
        'ru': 'Популярные остановки',
    },
    'city.carriers_from': {
        'sr': 'Prevoznici iz {city}',
        'en': 'Carriers from {city}',
        'ru': 'Перевозчики из {city}',
    },
    'line.interchange_stops': {
        'sr': 'Glavna stajališta — presedanja',
        'en': 'Major interchange stops',
        'ru': 'Главные пересадочные остановки',
    },
    'city.intercity': {
        'sr': 'Međugradski prevoz',
        'en': 'Intercity transport',
        'ru': 'Междугородний транспорт',
    },
    'city.all_intercity': {
        'sr': 'Sve međugradske rute',
        'en': 'All intercity routes',
        'ru': 'Все междугородние маршруты',
    },
    'city.bus_train_from': {
        'sr': 'Autobus i voz iz',
        'en': 'Bus and train from',
        'ru': 'Автобус и поезд из',
    },
    'city.departures_from': {
        'sr': 'Polasci iz',
        'en': 'Departures from',
        'ru': 'Отправления из',
    },
    'city.search_dest': {
        'sr': 'Pretraži destinacije',
        'en': 'Search destinations',
        'ru': 'Поиск направлений',
    },
    'city.eta_note': {
        'sr': 'Vreme dolaska na mapi je procena prema rasporedu. Moguća su odstupanja.',
        'en': 'Arrival times on the map are estimates based on the schedule. Deviations are possible.',
        'ru': 'Время прибытия на карте — оценка по расписанию. Возможны отклонения.',
    },
    'city.search_line': {
        'sr': 'Broj linije ili naziv...',
        'en': 'Line number or name...',
        'ru': 'Номер линии или название...',
    },
    'city.all': {
        'sr': 'Sve',
        'en': 'All',
        'ru': 'Все',
    },
    'city.tram': {
        'sr': 'Tramvaj',
        'en': 'Tram',
        'ru': 'Трамвай',
    },
    'city.trolleybus': {
        'sr': 'Trolejbus',
        'en': 'Trolleybus',
        'ru': 'Троллейбус',
    },
    'city.bus': {
        'sr': 'Autobus',
        'en': 'Bus',
        'ru': 'Автобус',
    },
    'city.night': {
        'sr': 'Noćne linije',
        'en': 'Night lines',
        'ru': 'Ночные линии',
    },

    # ── Breadcrumbs ──
    'breadcrumb.home': {
        'sr': 'Početna',
        'en': 'Home',
        'ru': 'Главная',
    },

    # ── Contact page ──
    'contact.title': {'sr': 'Kontakt', 'en': 'Contact', 'ru': 'Контакт'},
    'contact.subtitle': {
        'sr': 'Imate pitanje, sugestiju ili ste primetili grešku?',
        'en': 'Have a question, suggestion, or found an error?',
        'ru': 'Есть вопрос, предложение или нашли ошибку?',
    },
    'contact.name': {'sr': 'Ime', 'en': 'Name', 'ru': 'Имя'},
    'contact.name_ph': {'sr': 'Vaše ime', 'en': 'Your name', 'ru': 'Ваше имя'},
    'contact.email': {'sr': 'Email', 'en': 'Email', 'ru': 'Email'},
    'contact.message': {'sr': 'Poruka', 'en': 'Message', 'ru': 'Сообщение'},
    'contact.message_ph': {
        'sr': 'Opišite vaše pitanje ili sugestiju...',
        'en': 'Describe your question or suggestion...',
        'ru': 'Опишите ваш вопрос или предложение...',
    },
    'contact.send': {'sr': 'Pošalji', 'en': 'Send', 'ru': 'Отправить'},
    'contact.response_time': {
        'sr': 'Odgovaramo u roku od',
        'en': 'We respond within',
        'ru': 'Отвечаем в течение',
    },
    'contact.hours': {'sr': '24 sata', 'en': '24 hours', 'ru': '24 часов'},
    'contact.sent_ok': {
        'sr': 'Poruka je poslata. Hvala!',
        'en': 'Message sent. Thanks!',
        'ru': 'Сообщение отправлено. Спасибо!',
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
    'about.title': {'sr': 'O nama', 'en': 'About us', 'ru': 'О нас'},
    'about.meta_short': {
        'sr': 'Prevozni — besplatni red vožnje autobusa, vozova i gradskog prevoza u Srbiji. Bez registracije, na 3 jezika.',
        'en': 'Prevozni — free bus, train and city transport schedules across Serbia. No registration, in 3 languages.',
        'ru': 'Prevozni — бесплатное расписание автобусов, поездов и городского транспорта в Сербии. Без регистрации, на 3 языках.',
    },
    'about.intro_short': {
        'sr': 'Prevozni objedinjuje raspored {routes}+ međugradskih ruta i {ops}+ prevoznika u Srbiji i regionu, plus gradski prevoz u 4 grada. Besplatno, bez registracije, na 3 jezika.',
        'en': 'Prevozni aggregates schedules for {routes}+ intercity routes from {ops}+ carriers in Serbia and the region, plus city transit in 4 cities. Free, no signup, in 3 languages.',
        'ru': 'Prevozni объединяет расписание {routes}+ междугородних маршрутов и {ops}+ перевозчиков в Сербии и регионе, плюс городской транспорт в 4 городах. Бесплатно, без регистрации, на 3 языках.',
    },
    'about.search_h': {
        'sr': 'Pronađite vožnju',
        'en': 'Find a ride',
        'ru': 'Найти рейс',
    },
    'about.sources_short': {
        'sr': 'Podatke prikupljamo svakodnevnim skraperima sa zvaničnih izvora — bgprevoz.rs, gspns.co.rs, jgpnis.rs, busticket4.me, polazak.rs, srbijavoz.rs i drugih. Pre putovanja proverite raspored direktno kod prevoznika; cene i polasci se mogu menjati. Prevozni je besplatan i ne prodaje karte — kupovina ide kod naših affiliate partnera.',
        'en': 'Data is collected daily from official sources — bgprevoz.rs, gspns.co.rs, jgpnis.rs, busticket4.me, polazak.rs, srbijavoz.rs and others. Always confirm the schedule with the carrier before traveling; prices and departures can change. Prevozni is free and does not sell tickets — purchases go through our affiliate partners.',
        'ru': 'Данные обновляются ежедневными скраперами из официальных источников — bgprevoz.rs, gspns.co.rs, jgpnis.rs, busticket4.me, polazak.rs, srbijavoz.rs и других. Перед поездкой обязательно сверяйтесь с расписанием перевозчика; цены и рейсы могут меняться. Prevozni бесплатен и не продает билеты — покупка идет через наших affiliate-партнёров.',
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
    'see_also.title': {'sr': 'Pogledajte još', 'en': 'See also', 'ru': 'Смотрите также'},
    'see_also.all_routes': {'sr': 'Sve međugradske rute', 'en': 'All intercity routes', 'ru': 'Все междугородние маршруты'},
    'see_also.all_routes_desc': {
        'sr': 'Autobus i voz između gradova Srbije',
        'en': 'Bus and train between Serbian cities',
        'ru': 'Автобус и поезд между городами Сербии',
    },
    'see_also.city_beograd': {'sr': 'Gradski prevoz Beograd', 'en': 'Belgrade city transport', 'ru': 'Городской транспорт Белград'},
    'see_also.city_desc': {'sr': 'Linije, stajališta, mapa', 'en': 'Lines, stops, map', 'ru': 'Линии, остановки, карта'},
    'see_also.about': {'sr': 'O nama', 'en': 'About us', 'ru': 'О нас'},
    'see_also.about_desc': {'sr': 'Misija i izvori podataka', 'en': 'Mission and data sources', 'ru': 'Миссия и источники данных'},
    'see_also.country_hint': {
        'sr': 'Pogledajte sve rute do destinacija u ovoj zemlji',
        'en': 'See all routes to destinations in this country',
        'ru': 'Все маршруты до направлений в этой стране',
    },
    'see_also.country_network': {
        'sr': 'Druge zemlje na Prevozni',
        'en': 'Other countries on Prevozni',
        'ru': 'Другие страны на Prevozni',
    },

    # ── Route pages ──
    'route.schedule': {'sr': 'Red vožnje', 'en': 'Schedule', 'ru': 'Расписание'},
    'route.reverse': {
        'sr': 'Pogledajte i obrnuti smer',
        'en': 'See the reverse direction',
        'ru': 'Смотрите обратное направление',
    },

    # ── Search results ──
    'search.title': {'sr': 'Pretraga', 'en': 'Search', 'ru': 'Поиск'},
    'search.results_for': {'sr': 'Rezultati pretrage', 'en': 'Search results', 'ru': 'Результаты поиска'},
    'search.no_results': {'sr': 'Nema rezultata', 'en': 'No results', 'ru': 'Нет результатов'},

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
    'line.stops': {'sr': 'stajališta', 'en': 'stops', 'ru': 'остановок'},
    'line.direction_a': {'sr': 'Smer A', 'en': 'Direction A', 'ru': 'Направление А'},
    'line.direction_b': {'sr': 'Smer B', 'en': 'Direction B', 'ru': 'Направление Б'},
    'line.first_departure': {'sr': 'Prvi polazak', 'en': 'First departure', 'ru': 'Первый рейс'},
    'line.last_departure': {'sr': 'Poslednji polazak', 'en': 'Last departure', 'ru': 'Последний рейс'},

    # ── Stop detail ──
    'stop.lines_here': {'sr': 'Linije na ovom stajalištu', 'en': 'Lines at this stop', 'ru': 'Линии на этой остановке'},
    'stop.next_arrivals': {'sr': 'Sledeći polasci', 'en': 'Next departures', 'ru': 'Ближайшие отправления'},

    # ── Route detail / search ──
    'route.daily_departures': {'sr': 'polazaka dnevno', 'en': 'departures daily', 'ru': 'рейсов в день'},
    'route.per_day': {'sr': 'polazaka/dan', 'en': 'departures/day', 'ru': 'рейсов/день'},
    'route.shown_of': {'sr': 'Prikazano', 'en': 'Shown', 'ru': 'Показано'},
    'route.of': {'sr': 'od', 'en': 'of', 'ru': 'из'},
    'route.km': {'sr': 'km', 'en': 'km', 'ru': 'км'},
    'route.from_price': {'sr': 'od', 'en': 'from', 'ru': 'от'},
    'route.see_reverse': {
        'sr': 'Pogledajte i obrnuti smer',
        'en': 'See also the reverse direction',
        'ru': 'Смотрите также обратное направление',
    },
    'route.all_routes': {'sr': 'Sve rute', 'en': 'All routes', 'ru': 'Все маршруты'},
    'route.filter_all': {'sr': 'Svi polasci', 'en': 'All departures', 'ru': 'Все рейсы'},
    'route.sort_label': {'sr': 'Sortiraj', 'en': 'Sort', 'ru': 'Сортировка'},
    'route.sort_time': {'sr': 'Po polasku', 'en': 'Departure', 'ru': 'По отправлению'},
    'route.sort_price': {'sr': 'Najjeftinije', 'en': 'Cheapest', 'ru': 'Дешевле'},
    'route.sort_duration': {'sr': 'Najbrže', 'en': 'Fastest', 'ru': 'Быстрее'},
    'route.carrier_all': {'sr': 'Svi prevoznici', 'en': 'All carriers', 'ru': 'Все перевозчики'},
    'route.workday': {'sr': 'Radnim danom', 'en': 'Weekdays', 'ru': 'Будни'},
    'route.weekend': {'sr': 'Vikend', 'en': 'Weekend', 'ru': 'Выходные'},

    # ── Search page ──
    'search.departures_found': {'sr': 'polazaka', 'en': 'departures', 'ru': 'рейсов'},
    'search.no_results_text': {
        'sr': 'Nismo pronašli direktne polaske za ovaj pravac.',
        'en': 'No direct departures found for this route.',
        'ru': 'Прямых рейсов по этому маршруту не найдено.',
    },

    # ── Line detail ──
    'line.timeline': {'sr': 'Trasa linije', 'en': 'Line route', 'ru': 'Маршрут линии'},
    'line.schedule_title': {'sr': 'Red vožnje', 'en': 'Schedule', 'ru': 'Расписание'},
    'line.departures_from': {'sr': 'Polasci od', 'en': 'Departures from', 'ru': 'Отправление от'},

    # ── Stop detail ──
    'stop.title': {'sr': 'Stajalište', 'en': 'Stop', 'ru': 'Остановка'},
    'stop.on_map': {'sr': 'na mapi', 'en': 'on map', 'ru': 'на карте'},
    'stop.nearby': {'sr': 'Obližnja stajališta', 'en': 'Nearby stops', 'ru': 'Ближайшие остановки'},
    # New strings introduced when porting route_detail chrome to stop_detail
    # (parity audit 2026-04-26).
    'stop.subtitle': {
        'sr': 'Stajalište gradskog prevoza',
        'en': 'Public transport stop',
        'ru': 'Остановка городского транспорта',
    },
    'stop.back_to_city': {
        'sr': 'Sve linije i stajališta',
        'en': 'All lines and stops',
        'ru': 'Все линии и остановки',
    },
    'stop.lines_count_label': {
        'sr': 'linija', 'en': 'lines', 'ru': 'линий',
    },
    'stop.first_dep_label': {
        'sr': 'prvi polazak', 'en': 'first departure', 'ru': 'первый рейс',
    },
    'stop.last_dep_label': {
        'sr': 'poslednji polazak', 'en': 'last departure', 'ru': 'последний рейс',
    },
    'stop.coords_label': {
        'sr': 'na mapi', 'en': 'on map', 'ru': 'на карте',
    },
    'stop.action_title': {
        'sr': 'Planiraj putovanje',
        'en': 'Plan your trip',
        'ru': 'Спланировать поездку',
    },
    'stop.action_search': {
        'sr': 'Pretraži polaske odavde',
        'en': 'Search departures from here',
        'ru': 'Найти рейсы отсюда',
    },
    'stop.action_maps': {
        'sr': 'Otvori u mapama',
        'en': 'Open in maps',
        'ru': 'Открыть на карте',
    },
    'stop.action_note': {
        'sr': 'ETA se računa na osnovu zvaničnog GTFS reda vožnje.',
        'en': 'ETA is computed from the official GTFS schedule.',
        'ru': 'ETA рассчитывается по официальному расписанию GTFS.',
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
    },
    'line.action_title': {
        'sr': 'Saznaj kada krećeš',
        'en': 'Find your departure',
        'ru': 'Найди свой рейс',
    },
    'line.action_search': {
        'sr': 'Pretraži kroz mrežu linija',
        'en': 'Search the line network',
        'ru': 'Поиск по сети линий',
    },
    'line.action_map': {
        'sr': 'Pogledaj trasu na mapi',
        'en': 'See route on map',
        'ru': 'Посмотреть маршрут на карте',
    },
    'line.stop_count_label': {
        'sr': 'stajališta', 'en': 'stops', 'ru': 'остановок',
    },
    'line.type_label': {
        'sr': 'tip', 'en': 'type', 'ru': 'тип',
    },
    'line.service_label': {
        'sr': 'polasci', 'en': 'service', 'ru': 'рейсы',
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
    },
    'line.day_saturday': {
        'sr': 'Subota', 'en': 'Saturday', 'ru': 'Суббота',
    },
    'line.day_sunday': {
        'sr': 'Nedelja', 'en': 'Sunday', 'ru': 'Воскресенье',
    },
    'line.schedule_from_first': {
        'sr': 'polasci od prvog stajališta',
        'en': 'from first stop',
        'ru': 'от первой остановки',
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
    },

    # ── Operator detail page ──
    'operator.title_suffix': {
        'sr': 'rute i red vožnje',
        'en': 'routes and schedules',
        'ru': 'маршруты и расписание',
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
    },
    'guides.index_meta': {
        'sr': 'Praktični vodiči za putovanja autobusom i vozom po Srbiji i Balkanu: cene, redovi vožnje, poređenja, saveti.',
        'en': 'Practical guides for bus and train travel across Serbia and the Balkans: prices, schedules, comparisons, tips.',
        'ru': 'Практические гиды по автобусным и железнодорожным поездкам по Сербии и Балканам: цены, расписания, сравнения, советы.',
    },
    'guides.index_h1': {
        'sr': 'Vodiči za putnike',
        'en': 'Traveller guides',
        'ru': 'Гиды для путешественников',
    },
    'guides.index_subtitle': {
        'sr': 'Sve što treba da znate pre putovanja',
        'en': 'Everything you need to know before you travel',
        'ru': 'Всё что нужно знать перед поездкой',
    },
    'guides.intro_h': {
        'sr': 'Kako koristiti ove vodiče',
        'en': 'How to use these guides',
        'ru': 'Как пользоваться этими гидами',
    },
    'guides.intro_p': {
        'sr': 'Naši vodiči odgovaraju na konkretna pitanja putnika: kako doći do određenog grada, kada su najjeftinije karte, kako izabrati između autobusa i voza. Sav sadržaj se ažurira kada se promene redovi vožnje ili cene kod prevoznika.',
        'en': 'Our guides answer specific traveller questions: how to reach a specific city, when tickets are cheapest, how to choose between bus and train. All content is refreshed when carrier schedules or prices change.',
        'ru': 'Наши гиды отвечают на конкретные вопросы путешественников: как добраться до определённого города, когда билеты дешевле, как выбрать между автобусом и поездом. Весь контент обновляется при изменениях расписания или цен у перевозчиков.',
    },
    'guides.cat_travel': {'sr': 'Putovanja', 'en': 'Travel', 'ru': 'Путешествия'},
    'guides.cat_tips': {'sr': 'Saveti', 'en': 'Tips', 'ru': 'Советы'},

    # Guide 1 — Belgrade → Budva
    'guides.beograd_budva.title': {
        'sr': 'Kako doći iz Beograda u Budvu: autobus, voz, cene 2026',
        'en': 'How to get from Belgrade to Budva: bus, train, prices 2026',
        'ru': 'Как добраться из Белграда в Будву: автобус, поезд, цены 2026',
    },
    'guides.beograd_budva.meta': {
        'sr': 'Pun vodič za put Beograd → Budva 2026: autobus (najbrže, 10–12h), cene od 30€, preporučeni prevoznici i saveti.',
        'en': 'Full guide for Belgrade → Budva trip in 2026: bus (fastest, 10–12h), prices from €30, recommended carriers and tips.',
        'ru': 'Полный гид по поездке Белград → Будва в 2026: автобус (быстрее всего, 10–12ч), цены от 30€, рекомендуемые перевозчики и советы.',
    },
    'guides.beograd_budva.p1': {
        'sr': 'Beograd i Budva razdvaja oko <strong>600 km</strong> — put kroz Užice, Zlatibor, Nikšić i Podgoricu. Direktnog voza nema; najpraktičniji način je <strong>autobus preko noći</strong> (10–12 sati). Letnja sezona: i dnevne linije i veći broj prevoznika. Zimi: uglavnom noćne linije.',
        'en': 'Belgrade and Budva are separated by about <strong>600 km</strong> — the route runs through Užice, Zlatibor, Nikšić and Podgorica. There is no direct train; the most practical way is an <strong>overnight bus</strong> (10–12 hours). In summer: more daytime lines and more carriers. In winter: mostly overnight lines.',
        'ru': 'Белград и Будву разделяет около <strong>600 км</strong> — путь через Ужице, Златибор, Никшич и Подгорицу. Прямого поезда нет; самый практичный вариант — <strong>ночной автобус</strong> (10–12 часов). Летом: больше дневных рейсов и перевозчиков. Зимой: в основном ночные рейсы.',
    },
    'guides.beograd_budva.h2_options': {
        'sr': 'Opcije prevoza',
        'en': 'Travel options',
        'ru': 'Варианты транспорта',
    },
    'guides.beograd_budva.p2': {
        'sr': 'Na ovoj relaciji prevoz organizuju <strong>Lasta</strong>, <strong>Kavim-Jedinstvo</strong>, <strong>OZLEM</strong> i još nekoliko regionalnih prevoznika. Prosečna vožnja traje <strong>10 sati 30 minuta</strong> sa jednom pauzom. Većina autobusa su savremeni, sa WC-om, WiFi-jem i klimom.',
        'en': 'The route is operated by <strong>Lasta</strong>, <strong>Kavim-Jedinstvo</strong>, <strong>OZLEM</strong> and several regional carriers. Average trip is <strong>10 hours 30 minutes</strong> with one break. Most buses are modern, with toilet, WiFi and A/C.',
        'ru': 'Маршрут обслуживают <strong>Lasta</strong>, <strong>Kavim-Jedinstvo</strong>, <strong>OZLEM</strong> и несколько региональных перевозчиков. Средняя поездка — <strong>10 часов 30 минут</strong> с одной остановкой. Большинство автобусов современные, с туалетом, WiFi и кондиционером.',
    },
    'guides.beograd_budva.h2_price': {
        'sr': 'Cene karata',
        'en': 'Ticket prices',
        'ru': 'Цены билетов',
    },
    'guides.beograd_budva.p3': {
        'sr': 'Karte koštaju <strong>30–45€</strong> (3500–5200 RSD) zavisno od prevoznika i sezone. U julu-avgustu cene idu gore. Za najjeftinije karte: kupujte unapred i izbegavajte vikende. Povratna karta je često 5–10% jeftinija od dve u jednom smeru.',
        'en': 'Tickets cost <strong>€30–45</strong> (3500–5200 RSD) depending on carrier and season. Prices rise in July–August. For cheapest fares: book in advance and avoid weekends. Return tickets are often 5–10% cheaper than two one-ways.',
        'ru': 'Билеты стоят <strong>30–45€</strong> (3500–5200 RSD) в зависимости от перевозчика и сезона. Летом цены растут. Для самых дешёвых билетов: покупайте заранее и избегайте выходных. Обратный билет часто на 5–10% дешевле двух в одну сторону.',
    },
    'guides.beograd_budva.h2_when': {
        'sr': 'Kada putovati',
        'en': 'When to travel',
        'ru': 'Когда ехать',
    },
    'guides.beograd_budva.p4': {
        'sr': 'Glavna sezona je <strong>jun-septembar</strong> — tada je najveći izbor polazaka i najviše turista. Van sezone (novembar-mart) put je jeftiniji i mirniji, ali je broj polazaka manji (obično samo noćni). Srećom, Budva radi cele godine — čak i zimi tu ima života.',
        'en': 'Peak season is <strong>June–September</strong> — most departures and most tourists. Off-season (November–March) is cheaper and quieter, but fewer departures (usually overnight only). Luckily Budva is open year-round — even in winter it has a pulse.',
        'ru': 'Пик — <strong>июнь-сентябрь</strong> — больше всего рейсов и туристов. Несезон (ноябрь-март) — дешевле и тише, но меньше рейсов (обычно только ночные). К счастью, Будва живёт круглый год — даже зимой там есть жизнь.',
    },
    'guides.beograd_budva.cta': {
        'sr': 'Proveri polazke Beograd → Budva',
        'en': 'Check Belgrade → Budva departures',
        'ru': 'Посмотреть рейсы Белград → Будва',
    },

    # Guide 2 — cheap tickets
    'guides.cheap_tickets.title': {
        'sr': 'Najjeftinije autobus karte u Srbiji: 7 saveta 2026',
        'en': 'Cheapest bus tickets in Serbia: 7 tips for 2026',
        'ru': 'Самые дешёвые билеты на автобус в Сербии: 7 советов 2026',
    },
    'guides.cheap_tickets.meta': {
        'sr': 'Kako kupiti najjeftinije karte za autobus u Srbiji: kada bukirati, gde tražiti, koji prevoznici daju popuste.',
        'en': 'How to buy the cheapest bus tickets in Serbia: when to book, where to look, which carriers offer discounts.',
        'ru': 'Как купить самые дешёвые билеты на автобус в Сербии: когда бронировать, где искать, какие перевозчики дают скидки.',
    },
    'guides.cheap_tickets.p1': {
        'sr': 'Cene autobuskih karata u Srbiji variraju i do 40% zavisno od dana, prevoznika i načina kupovine. Evo kako ih spustiti na minimum.',
        'en': 'Bus ticket prices in Serbia vary by up to 40% depending on the day, carrier and purchase method. Here is how to push them to the minimum.',
        'ru': 'Цены автобусных билетов в Сербии различаются до 40% в зависимости от дня, перевозчика и способа покупки. Вот как опустить их до минимума.',
    },
    'guides.cheap_tickets.h2_when': {'sr': 'Kada kupiti', 'en': 'When to buy', 'ru': 'Когда покупать'},
    'guides.cheap_tickets.p2': {
        'sr': 'Autobuske karte u Srbiji nemaju tako izražen dynamic pricing kao avio, ali i dalje: <strong>utorak-četvrtak</strong> su najjeftiniji dani, vikendi i praznici 10–25% skuplji. Vožnje rano ujutru i kasno noću su obično jeftinije od popodnevnih.',
        'en': 'Serbian bus tickets don\'t have dynamic pricing like airlines, but still: <strong>Tuesday-Thursday</strong> are cheapest days, weekends and holidays 10–25% more expensive. Early morning and late-night runs are usually cheaper than afternoon ones.',
        'ru': 'Автобусные билеты в Сербии не имеют такого динамичного ценообразования как авиа, но всё же: <strong>вторник-четверг</strong> — самые дешёвые дни, выходные и праздники на 10–25% дороже. Утренние и ночные рейсы обычно дешевле дневных.',
    },
    'guides.cheap_tickets.h2_where': {'sr': 'Gde tražiti', 'en': 'Where to look', 'ru': 'Где искать'},
    'guides.cheap_tickets.p3': {
        'sr': 'Većina prevoznika prodaje online preko partnera <strong>Bookaway</strong> ili <strong>BusTicket4.me</strong>. Direktno na šalteru autobuske stanice ponekad je i jeftinije — posebno kod manjih lokalnih prevoznika (Niš-Ekspres, Severtrans, Autoprevoz).',
        'en': 'Most carriers sell online via partners <strong>Bookaway</strong> or <strong>BusTicket4.me</strong>. Buying directly at the bus-station counter is sometimes cheaper — especially with smaller local carriers (Niš-Ekspres, Severtrans, Autoprevoz).',
        'ru': 'Большинство перевозчиков продают онлайн через партнёров <strong>Bookaway</strong> или <strong>BusTicket4.me</strong>. Прямо на кассе автовокзала иногда дешевле — особенно у небольших местных перевозчиков (Niš-Ekspres, Severtrans, Autoprevoz).',
    },
    'guides.cheap_tickets.h2_tips': {'sr': 'Praktični saveti', 'en': 'Practical tips', 'ru': 'Практические советы'},
    'guides.cheap_tickets.p4': {
        'sr': 'Povratna karta obično je 5–10% jeftinija od dve odvojene. Studentske i penzionerske popuste daju Lasta, Kavim i Niš-Ekspres (do 30%). Za više ljudi: proveriti grupne cene kod prevoznika — česta ušteda 15–20%. Ne bukirati u petak popodne i nedelju uveče — to je cenovni pik nedelje.',
        'en': 'Return tickets are usually 5–10% cheaper than two one-ways. Student and senior discounts: Lasta, Kavim and Niš-Ekspres (up to 30%). For groups: check group rates with the carrier — typical savings 15–20%. Avoid booking Friday afternoon and Sunday evening — weekly price peak.',
        'ru': 'Обратные билеты обычно на 5–10% дешевле двух в одну сторону. Студенческие и пенсионерские скидки: Lasta, Kavim и Niš-Ekspres (до 30%). Для групп: проверьте групповые тарифы у перевозчика — обычно экономия 15–20%. Не бронируйте в пятницу днём и воскресенье вечером — пик цен недели.',
    },
    'guides.cheap_tickets.cta': {
        'sr': 'Vidi sve rute i cene',
        'en': 'See all routes and prices',
        'ru': 'Посмотреть все маршруты и цены',
    },

    # Guide 3 — bus vs train
    'guides.bus_vs_train.title': {
        'sr': 'Autobus ili voz u Srbiji: šta je bolje?',
        'en': 'Bus or train in Serbia: which is better?',
        'ru': 'Автобус или поезд в Сербии: что лучше?',
    },
    'guides.bus_vs_train.meta': {
        'sr': 'Poređenje autobusa i voza u Srbiji: brzina, cena, komfor, pokrivenost. Kada izabrati šta.',
        'en': 'Bus vs. train comparison for Serbia: speed, price, comfort, coverage. When to pick which.',
        'ru': 'Сравнение автобуса и поезда в Сербии: скорость, цена, комфорт, покрытие. Когда что выбрать.',
    },
    'guides.bus_vs_train.p1': {
        'sr': 'U Srbiji autobus pokriva skoro sve relacije (275+ međugradskih), dok voz radi na oko 15 glavnih pravaca. Ipak, na nekim rutama voz je ozbiljan takmičar — jeftiniji i komforniji.',
        'en': 'In Serbia, the bus covers nearly every route (275+ intercity), while the train runs on about 15 main corridors. Still, on certain routes the train is a serious contender — cheaper and more comfortable.',
        'ru': 'В Сербии автобус покрывает почти все направления (275+ междугородних), поезд работает на ~15 основных коридорах. Тем не менее на некоторых маршрутах поезд — серьёзный конкурент: дешевле и комфортнее.',
    },
    'guides.bus_vs_train.h2_bus': {'sr': 'Kada autobus', 'en': 'When bus wins', 'ru': 'Когда автобус выигрывает'},
    'guides.bus_vs_train.p2': {
        'sr': 'Autobus je bolji izbor za <strong>manje gradove</strong> (Čačak, Kraljevo, Užice, Valjevo, Leskovac), <strong>putovanja u region</strong> (Crna Gora, Bosna, Hrvatska), i <strong>noćne polaske</strong> kada možete da spavate u sedištu. Prevoznika je mnogo, frekvencija velika.',
        'en': 'The bus is better for <strong>smaller cities</strong> (Čačak, Kraljevo, Užice, Valjevo, Leskovac), <strong>regional travel</strong> (Montenegro, Bosnia, Croatia), and <strong>overnight runs</strong> where you can sleep in the seat. Lots of carriers, high frequency.',
        'ru': 'Автобус лучше для <strong>небольших городов</strong> (Чачак, Кралево, Ужице, Валево, Лесковац), <strong>региональных поездок</strong> (Черногория, Босния, Хорватия) и <strong>ночных рейсов</strong> где можно поспать в кресле. Много перевозчиков, высокая частота.',
    },
    'guides.bus_vs_train.h2_train': {'sr': 'Kada voz', 'en': 'When train wins', 'ru': 'Когда поезд выигрывает'},
    'guides.bus_vs_train.p3': {
        'sr': 'Voz je bolji na pravcu <strong>Beograd — Novi Sad</strong> (brza Soko linija, 37 min) i na relacijama <strong>Beograd — Subotica</strong>, <strong>Beograd — Niš</strong>. Komfor je veći (možete da ustanete i prošetate), cene često niže nego autobus, i nema zastoja u saobraćaju.',
        'en': 'The train wins on <strong>Belgrade — Novi Sad</strong> (the fast Soko line, 37 min) and on <strong>Belgrade — Subotica</strong>, <strong>Belgrade — Niš</strong>. More comfort (you can stand and walk), often cheaper than the bus, no traffic jams.',
        'ru': 'Поезд выигрывает на направлении <strong>Белград — Нови-Сад</strong> (скорая линия Soko, 37 мин) и на <strong>Белград — Суботица</strong>, <strong>Белград — Ниш</strong>. Больше комфорта (можно встать и пройтись), часто дешевле автобуса, нет пробок.',
    },
    'guides.bus_vs_train.h2_verdict': {'sr': 'Verdikt', 'en': 'Verdict', 'ru': 'Вывод'},
    'guides.bus_vs_train.p4': {
        'sr': 'Za <strong>Novi Sad</strong>, <strong>Subotica</strong>, <strong>Niš</strong>: pokušajte voz (posebno Soko). Za sve ostalo: autobus. Kad god ima oba — uporedite cenu i vreme na ovom sajtu pre kupovine.',
        'en': 'For <strong>Novi Sad</strong>, <strong>Subotica</strong>, <strong>Niš</strong>: try the train (especially Soko). For everything else: bus. Whenever both are available — compare price and time on this site before buying.',
        'ru': 'Для <strong>Нови-Сад</strong>, <strong>Суботица</strong>, <strong>Ниш</strong>: попробуйте поезд (особенно Soko). Для всего остального: автобус. Когда оба варианта есть — сравните цену и время на этом сайте перед покупкой.',
    },
    'guides.bus_vs_train.cta': {
        'sr': 'Uporedi polaske',
        'en': 'Compare departures',
        'ru': 'Сравнить рейсы',
    },

    # ── Country hub page ──
    'country.title_prefix': {
        'sr': 'Autobus Srbija',
        'en': 'Bus Serbia',
        'ru': 'Автобус Сербия',
    },
    'country.title_suffix': {
        'sr': 'raspored i cene',
        'en': 'schedule and prices',
        'ru': 'расписание и цены',
    },
    'country.meta_prefix': {
        'sr': 'Red vožnje autobusa iz Srbije za',
        'en': 'Bus schedule from Serbia to',
        'ru': 'Расписание автобусов из Сербии в',
    },
    'country.meta_routes': {'sr': 'ruta', 'en': 'routes', 'ru': 'маршрутов'},
    'country.meta_trips': {'sr': 'polazaka', 'en': 'departures', 'ru': 'отправлений'},
    'country.meta_cities': {'sr': 'gradova', 'en': 'cities', 'ru': 'городов'},
    'country.meta_cta': {
        'sr': 'Uporedite cene i kupite kartu. Besplatno.',
        'en': 'Compare prices, buy tickets. Free.',
        'ru': 'Сравните цены, купите билет. Бесплатно.',
    },
    'country.h1': {
        'sr': 'Autobuske rute —',
        'en': 'Bus routes —',
        'ru': 'Автобусные маршруты —',
    },
    'country.stat_routes': {'sr': 'ruta', 'en': 'routes', 'ru': 'маршрутов'},
    'country.stat_cities': {'sr': 'gradova', 'en': 'cities', 'ru': 'городов'},
    'country.stat_trips': {'sr': 'dnevnih polazaka', 'en': 'daily departures', 'ru': 'ежедневных отправлений'},
    'country.routes_heading': {
        'sr': 'Sve rute za',
        'en': 'All routes to',
        'ru': 'Все маршруты в',
    },
    'country.no_routes': {
        'sr': 'Trenutno nema dostupnih ruta za ovu zemlju.',
        'en': 'No routes available for this country at the moment.',
        'ru': 'В настоящее время нет доступных маршрутов в эту страну.',
    },
    'country.about_h': {
        'sr': 'Putovanja autobusom u {country}',
        'en': 'Bus travel to {country}',
        'ru': 'Автобусные поездки в {country}',
    },
    'country.about_p': {
        'sr': 'Na Prevozni.com pronaći ćete {routes} aktivnih autobuskih ruta koje povezuju Srbiju sa državom {country}, sa ukupno {trips} polazaka dnevno. Od toga {from_sr} rute polaze iz srpskih gradova, a {intra} rute su unutar same zemlje. Pokriveno je {cities} gradova.',
        'en': 'On Prevozni.com you will find {routes} active bus routes connecting Serbia with {country}, with {trips} daily departures in total. {from_sr} routes depart from Serbian cities, and {intra} routes are within the country itself. {cities} cities are covered.',
        'ru': 'На Prevozni.com вы найдёте {routes} активных автобусных маршрутов, соединяющих Сербию со страной {country}, всего {trips} ежедневных отправлений. Из них {from_sr} маршрутов отправляются из сербских городов, а {intra} маршрутов — внутри самой страны. Охвачено {cities} городов.',
    },
    'country.cities_p': {
        'sr': 'Gradovi u {country} koji su pokriveni: {cities}. Kliknite na rutu da vidite konkretne polaske, cene karata i kupovinu kod partnera.',
        'en': 'Cities in {country} covered: {cities}. Click a route to see departures, ticket prices and partner purchase links.',
        'ru': 'Города в {country}, охваченные сервисом: {cities}. Нажмите на маршрут чтобы увидеть отправления, цены билетов и покупку у партнёра.',
    },
    'country.carriers_h': {
        'sr': 'Prevoznici za {country}',
        'en': 'Carriers to {country}',
        'ru': 'Перевозчики в {country}',
    },
    'country.subtitle': {
        'sr': 'Međugradske autobuske rute, cene i raspored',
        'en': 'Intercity bus routes, prices and schedules',
        'ru': 'Междугородние автобусные маршруты, цены и расписание',
    },
    'country.stat_avg_distance': {
        'sr': 'prosečna razdaljina',
        'en': 'average distance',
        'ru': 'средняя дистанция',
    },
    'country.stat_avg_price': {
        'sr': 'prosečna cena',
        'en': 'average price',
        'ru': 'средняя цена',
    },
    'country.prose_travel_time': {
        'sr': 'Prosečna razdaljina rute do države {country} iznosi oko {km} km, što odgovara putovanju od približno {hours} sati standardnim autobusom.',
        'en': 'The average route distance to {country} is around {km} km, roughly {hours} hours by standard bus.',
        'ru': 'Средняя дистанция маршрута до страны {country} — около {km} км, что соответствует поездке примерно за {hours} часов на стандартном автобусе.',
    },
    'country.prose_avg_price': {
        'sr': 'Prosečna najpovoljnija cena karte za pravac {country} kreće se oko {price} dinara.',
        'en': 'The average lowest ticket price for {country} is around {price} RSD.',
        'ru': 'Средняя минимальная цена билета в направлении {country} — около {price} динаров.',
    },
    'country.prose_buy': {
        'sr': 'Sve cene su informativne i ažurirane prema podacima naših partnera. Karte za rute do države {country} kupuju se kod naših booking partnera; mi ne naplaćujemo dodatne provizije.',
        'en': 'All prices are indicative and updated from partner data. Tickets to {country} are purchased through our booking partners; we charge no extra fees.',
        'ru': 'Все цены ориентировочны и обновляются по данным наших партнёров. Билеты в страну {country} покупаются у наших партнёров; мы не берём дополнительной комиссии.',
    },
    'country.filter_popular': {
        'sr': 'Najpopularnije',
        'en': 'Most popular',
        'ru': 'Самые популярные',
    },
    'country.filter_cheap': {
        'sr': 'Najjeftinije',
        'en': 'Cheapest',
        'ru': 'Самые дешёвые',
    },
    'country.filter_short': {
        'sr': 'Najkraće',
        'en': 'Shortest',
        'ru': 'Самые короткие',
    },
    'country.sample_schedule': {
        'sr': 'Primeri polazaka',
        'en': 'Sample departures',
        'ru': 'Примеры рейсов',
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
    'operator.sample_schedule': {
        'sr': 'Primeri polazaka',
        'en': 'Sample departures',
        'ru': 'Примеры рейсов',
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
    },
    'buy.note': {
        'sr': 'Kupovina se obavlja na sajtovima partnera. Prevozni ne prodaje karte.',
        'en': 'Purchase is made on partner websites. Prevozni does not sell tickets.',
        'ru': 'Покупка на сайтах партнёров. Prevozni не продаёт билеты.',
    },
    'buy.cta': {
        'sr': 'Kupi',
        'en': 'Buy',
        'ru': 'Купить',
    },
    'buy.via_partner': {
        'sr': 'Kupi preko',
        'en': 'Buy via',
        'ru': 'Купить через',
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
    'ai_route.mode_bus': {'sr': 'Autobus', 'en': 'Bus', 'ru': 'Автобус'},
    'ai_route.mode_train': {'sr': 'Voz', 'en': 'Train', 'ru': 'Поезд'},
    'ai_route.mode_flight': {'sr': 'Let', 'en': 'Flight', 'ru': 'Перелёт'},
    'ai_route.mode_ferry': {'sr': 'Trajekt', 'en': 'Ferry', 'ru': 'Паром'},
    'ai_route.mode_taxi': {'sr': 'Taksi', 'en': 'Taxi', 'ru': 'Такси'},
    'ai_route.mode_metro': {'sr': 'Metro', 'en': 'Metro', 'ru': 'Метро'},
    'ai_route.faq.q_how': {
        'sr': 'Kako stići',
        'en': 'How to get from',
        'ru': 'Как добраться',
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
    },
    'buy.partners_note': {
        'sr': 'Cene su iste — mi dobijemo malu proviziju ako kupite preko ovih linkova.',
        'en': 'Prices are the same — we receive a small commission if you book via these links.',
        'ru': 'Цены одинаковые — мы получаем небольшую комиссию при бронировании по этим ссылкам.',
    },

    # ── Day labels ──
    'day.today': {'sr': 'Danas', 'en': 'Today', 'ru': 'Сегодня'},
    'day.tomorrow': {'sr': 'Sutra', 'en': 'Tomorrow', 'ru': 'Завтра'},
    'day.day_after': {'sr': 'Prekosutra', 'en': 'Day after', 'ru': 'Послезавтра'},

    'route.similar': {'sr': 'Slične rute iz', 'en': 'Similar routes from', 'ru': 'Похожие маршруты из'},
    'route.other_from': {'sr': 'Drugi pravci iz', 'en': 'Other routes from', 'ru': 'Другие направления из'},
    'route.carriers_on_route': {
        'sr': 'Prevoznici na ovoj ruti',
        'en': 'Carriers on this route',
        'ru': 'Перевозчики на этом маршруте',
    },
    'route.about': {'sr': 'O ruti', 'en': 'About route', 'ru': 'О маршруте'},

    # ── Destinations page ──
    'dest.title': {
        'sr': 'Top destinacije na Balkanu',
        'en': 'Top Balkan destinations',
        'ru': 'Лучшие направления на Балканах',
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

    'nav.destinations': {'sr': 'Destinacije', 'en': 'Destinations', 'ru': 'Направления'},

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
    },
    'a11y.language_switcher': {
        'sr': 'Izbor jezika',
        'en': 'Language selector',
        'ru': 'Выбор языка',
    },
    'a11y.currency_switcher': {
        'sr': 'Izbor valute',
        'en': 'Currency selector',
        'ru': 'Выбор валюты',
    },
    'a11y.search_form': {
        'sr': 'Pretraga polazaka',
        'en': 'Journey search',
        'ru': 'Поиск поездок',
    },
    'a11y.swap_cities': {
        'sr': 'Zameni polazište i odredište',
        'en': 'Swap origin and destination',
        'ru': 'Поменять местами пункты',
    },
    'a11y.share': {
        'sr': 'Podeli',
        'en': 'Share',
        'ru': 'Поделиться',
    },
    'a11y.trip_date': {
        'sr': 'Datum putovanja',
        'en': 'Trip date',
        'ru': 'Дата поездки',
    },
    'a11y.filters': {
        'sr': 'Filteri polazaka',
        'en': 'Journey filters',
        'ru': 'Фильтры поездок',
    },
    'a11y.city_map': {
        'sr': 'Interaktivna mapa gradskih stajališta',
        'en': 'Interactive city stops map',
        'ru': 'Интерактивная карта городских остановок',
    },
    'a11y.line_map': {
        'sr': 'Interaktivna mapa linije',
        'en': 'Interactive line map',
        'ru': 'Интерактивная карта линии',
    },
    'a11y.stop_map': {
        'sr': 'Mapa lokacije stajališta',
        'en': 'Stop location map',
        'ru': 'Карта местоположения остановки',
    },
    'a11y.breadcrumb': {
        'sr': 'Putanja',
        'en': 'Breadcrumb',
        'ru': 'Хлебные крошки',
    },
    'a11y.pagination': {
        'sr': 'Paginacija',
        'en': 'Pagination',
        'ru': 'Пагинация',
    },

    # ── Default meta (base.html) ──
    'meta.default_title': {
        'sr': 'Prevozni — red vožnje u Srbiji',
        'en': 'Prevozni — transport schedules in Serbia',
        'ru': 'Prevozni — расписание транспорта в Сербии',
    },
    'meta.default_description': {
        'sr': 'Red vožnje autobusa, vozova i gradskog prevoza u Srbiji. Pronađite polazak, uporedite cene i prevoznike. Besplatno, bez registracije.',
        'en': 'Bus, train and city transport schedules in Serbia. Find departures, compare prices and carriers. Free, no registration.',
        'ru': 'Расписание автобусов, поездов и городского транспорта в Сербии. Ищите отправления, сравнивайте цены и перевозчиков. Бесплатно, без регистрации.',
    },
    'meta.og_image_alt': {
        'sr': 'Prevozni — red vožnje Srbija',
        'en': 'Prevozni — Serbia transport schedules',
        'ru': 'Prevozni — расписание транспорта Сербии',
    },
    'meta.city_not_found': {
        'sr': 'Grad nije pronađen',
        'en': 'City not found',
        'ru': 'Город не найден',
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
    },
    'route_index.show_more_suffix': {
        'sr': 'ruta',
        'en': 'routes',
        'ru': 'маршрутов',
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
    },
    'city_pair.meta_prefix': {
        'sr': 'Kako doći od',
        'en': 'How to travel from',
        'ru': 'Как добраться из',
    },
    'city_pair.meta_mid': {
        'sr': 'do',
        'en': 'to',
        'ru': 'до',
    },
    'city_pair.meta_suffix': {
        'sr': 'Red vožnje, cene karata i prevoznici.',
        'en': 'Schedule, ticket prices and carriers.',
        'ru': 'Расписание, цены билетов и перевозчики.',
    },
    'city_pair.see_all_departures': {
        'sr': 'Pogledaj sve polaske →',
        'en': 'See all departures →',
        'ru': 'Все отправления →',
    },
    'city_pair.carriers_heading': {
        'sr': 'Prevoznici',
        'en': 'Carriers',
        'ru': 'Перевозчики',
    },
    'city_pair.carriers_hint': {
        'sr': 'Proverite kod prevoznika za aktuelne linije.',
        'en': 'Check with carriers for current lines.',
        'ru': 'Уточняйте актуальные рейсы у перевозчиков.',
    },
    'city_pair.prices_heading': {
        'sr': 'Cene',
        'en': 'Prices',
        'ru': 'Цены',
    },
    'city_pair.prices_hint': {
        'sr': 'Cene variraju po prevoznicima. Kupite karte na blagajni.',
        'en': 'Prices vary by carrier. Buy tickets at the ticket office.',
        'ru': 'Цены у разных перевозчиков отличаются. Билеты продаются в кассе.',
    },
    'city_pair.tips_heading': {
        'sr': 'Saveti',
        'en': 'Tips',
        'ru': 'Советы',
    },
    'city_pair.tip_buy_early': {
        'sr': 'Kupite kartu unapred u sezoni i za vikende.',
        'en': 'Buy tickets in advance during the season and weekends.',
        'ru': 'Покупайте билеты заранее в сезон и на выходные.',
    },
    'city_pair.faq_heading': {
        'sr': 'Često postavljana pitanja',
        'en': 'Frequently asked questions',
        'ru': 'Часто задаваемые вопросы',
    },
    'city_pair.other_routes_from': {
        'sr': 'Druge rute iz grada',
        'en': 'Other routes from',
        'ru': 'Другие маршруты из',
    },
    'city_pair.departures_word': {
        'sr': 'polazaka',
        'en': 'departures',
        'ru': 'отправлений',
    },
    'city_pair.no_direct': {
        'sr': 'Direktna veza nije u bazi',
        'en': 'No direct route in database',
        'ru': 'Прямой маршрут отсутствует в базе',
    },

    # ── city_pair body prose (was hardcoded SR; now translated) ──
    'city_pair.subtitle_daily': {
        'sr': '{count} polazaka dnevno',
        'en': '{count} departures per day',
        'ru': '{count} отправлений в день',
    },
    'city_pair.subtitle_from_price': {
        'sr': 'od', 'en': 'from', 'ru': 'от',
    },
    'city_pair.seo_h2': {
        'sr': '{from_city} — {to_city}: prevoz',
        'en': '{from_city} — {to_city}: travel',
        'ru': '{from_city} — {to_city}: транспорт',
    },
    'city_pair.prose_distance': {
        'sr': 'Rastojanje između {from_city} i {to_city} iznosi {km} km.',
        'en': 'The distance between {from_city} and {to_city} is {km} km.',
        'ru': 'Расстояние между {from_city} и {to_city} составляет {km} км.',
    },
    'city_pair.prose_duration_range': {
        'sr': 'Putovanje traje od {h_min}h {m_min}min do {h_max}h {m_max}min u zavisnosti od prevoznika.',
        'en': 'The journey takes {h_min}h {m_min}min to {h_max}h {m_max}min depending on the carrier.',
        'ru': 'Поездка занимает от {h_min}ч {m_min}мин до {h_max}ч {m_max}мин в зависимости от перевозчика.',
    },
    'city_pair.prose_operators': {
        'sr': 'Na ovoj ruti voze: {operators}.',
        'en': 'Carriers on this route: {operators}.',
        'ru': 'На этом маршруте работают перевозчики: {operators}.',
    },
    'city_pair.prose_price_range': {
        'sr': 'Cene karata kreću se od {min} do {max} RSD ({eur_min}–{eur_max}€).',
        'en': 'Ticket prices range from {min} to {max} RSD ({eur_min}–{eur_max}€).',
        'ru': 'Цены на билеты — от {min} до {max} RSD ({eur_min}–{eur_max}€).',
    },
    'city_pair.prose_first_last': {
        'sr': 'Prvi polazak je u {first}, a poslednji u {last}.',
        'en': 'The first departure is at {first}, the last at {last}.',
        'ru': 'Первое отправление в {first}, последнее в {last}.',
    },
    'city_pair.carriers_count': {
        'sr': 'Na liniji {from_city} — {to_city} voze {n} prevoznika: {operators}.',
        'en': 'There are {n} carriers on {from_city} — {to_city}: {operators}.',
        'ru': 'На линии {from_city} — {to_city} работают {n} перевозчиков: {operators}.',
    },
    'city_pair.cheapest_op': {
        'sr': 'Najjeftinije karte nudi {operator}.',
        'en': 'The cheapest tickets are offered by {operator}.',
        'ru': 'Самые дешёвые билеты предлагает {operator}.',
    },
    'city_pair.prices_range_buy': {
        'sr': 'Karte od {min} RSD ({eur_min}€) do {max} RSD ({eur_max}€). Kupite na blagajni autobuske stanice ili online.',
        'en': 'Tickets from {min} RSD ({eur_min}€) to {max} RSD ({eur_max}€). Buy at the bus station counter or online.',
        'ru': 'Билеты от {min} RSD ({eur_min}€) до {max} RSD ({eur_max}€). Покупка в кассе автовокзала или онлайн.',
    },
    'city_pair.tip_first_last_short': {
        'sr': 'Prvi polazak u {first}, poslednji u {last}.',
        'en': 'First departure {first}, last {last}.',
        'ru': 'Первое отправление {first}, последнее {last}.',
    },
    'city_pair.tip_duration': {
        'sr': 'Putovanje traje {h_min}h {m_min}min{suffix}.',
        'en': 'Journey takes {h_min}h {m_min}min{suffix}.',
        'ru': 'Поездка занимает {h_min}ч {m_min}мин{suffix}.',
    },
    'city_pair.tip_duration_range_suffix': {
        'sr': '–{h_max}h {m_max}min',
        'en': '–{h_max}h {m_max}min',
        'ru': '–{h_max}ч {m_max}мин',
    },

    # ── route_detail.html ──
    'route_detail.title_suffix': {
        'sr': 'red vožnje',
        'en': 'schedule',
        'ru': 'расписание',
    },
    'route_detail.meta_schedule': {
        'sr': 'Red vožnje',
        'en': 'Schedule',
        'ru': 'Расписание',
    },
    'route_detail.meta_daily': {
        'sr': 'polazaka dnevno',
        'en': 'departures daily',
        'ru': 'отправлений в день',
    },
    'route_detail.meta_carriers': {
        'sr': 'prevoznici',
        'en': 'carriers',
        'ru': 'перевозчики',
    },
    'route_detail.meta_and_more': {
        'sr': 'i dr',
        'en': 'and more',
        'ru': 'и др',
    },
    'route_detail.meta_from': {
        'sr': 'Od',
        'en': 'From',
        'ru': 'От',
    },
    # CTR-optimized snippets: title/meta rewrites (2026+)
    'route_detail.title_departures': {
        'sr': 'polazaka dnevno',
        'en': 'departures daily',
        'ru': 'отправлений в день',
    },
    'route_detail.title_short': {
        'sr': 'red vožnje i cene',
        'en': 'schedule and prices',
        'ru': 'расписание и цены',
    },
    'route_detail.meta_compare_cta': {
        'sr': 'Uporedi prevoznike i cene besplatno.',
        'en': 'Compare carriers and prices for free.',
        'ru': 'Сравните перевозчиков и цены бесплатно.',
    },
    'route_detail.meta_prefix': {
        'sr': 'Autobuska ruta',
        'en': 'Bus route',
        'ru': 'Автобусный маршрут',
    },
    'route_detail.meta_body': {
        'sr': 'Red vožnje, cene karata, prevoznici i trajanje putovanja. Uporedite polaske i kupite kartu online preko partnera. Besplatno, bez registracije.',
        'en': 'Schedule, ticket prices, carriers and trip duration. Compare departures and buy a ticket online via partners. Free, no registration required.',
        'ru': 'Расписание, цены билетов, перевозчики и время в пути. Сравните отправления и купите билет онлайн через партнёров. Бесплатно, без регистрации.',
    },
    'route.prose_distance': {
        'sr': 'Vožnja od {from_city} do {to_city} iznosi oko {km} km.',
        'en': 'The trip from {from_city} to {to_city} is about {km} km.',
        'ru': 'Поездка из {from_city} в {to_city} занимает около {km} км.',
    },
    'route.prose_duration': {
        'sr': 'Prosečno trajanje putovanja autobusom je oko {hours} sata.',
        'en': 'Average bus trip duration is around {hours} hours.',
        'ru': 'Средняя длительность поездки на автобусе — около {hours} часов.',
    },
    'route.prose_operators': {
        'sr': 'Na ovoj ruti voze prevoznici: {ops}.',
        'en': 'Carriers on this route: {ops}.',
        'ru': 'На этом маршруте работают перевозчики: {ops}.',
    },
    'route.prose_price_range': {
        'sr': 'Cene karata se kreću od {min} do {max} RSD, u zavisnosti od prevoznika i dana.',
        'en': 'Ticket prices range from {min} to {max} RSD, depending on carrier and day.',
        'ru': 'Цены билетов колеблются от {min} до {max} RSD в зависимости от перевозчика и дня.',
    },
    'route.prose_price_single': {
        'sr': 'Cena karte iznosi oko {price} RSD.',
        'en': 'Ticket price is around {price} RSD.',
        'ru': 'Цена билета — около {price} RSD.',
    },
    'route.prose_context': {
        'sr': 'Autobuske linije između {from_city} i {to_city} povezuju putnike tokom cele godine. Na ovoj stranici prikazujemo kompletan red vožnje za svaki dan u nedelji, sa mogućnošću filtriranja po vremenu polaska, trajanju putovanja ili ceni. Podaci se ažuriraju svake noći iz više izvora (busticket4.me, polazak.rs, srbijavoz.rs), a prikazane cene su orjentacione — konačnu cenu i raspoloživost mesta potvrđuje partner kod kog kupujete kartu.',
        'en': 'Bus lines between {from_city} and {to_city} run year-round. This page shows the full schedule for each day of the week, with filters for departure time, trip duration and price. Data is refreshed nightly from multiple sources (busticket4.me, polazak.rs, srbijavoz.rs), and displayed prices are indicative — the final fare and seat availability is confirmed by the partner where you buy the ticket.',
        'ru': 'Автобусные рейсы между {from_city} и {to_city} работают круглый год. На этой странице показано полное расписание по дням недели, с фильтрами по времени отправления, длительности поездки и цене. Данные обновляются каждую ночь из нескольких источников (busticket4.me, polazak.rs, srbijavoz.rs), а показанные цены ориентировочные — финальную цену и наличие мест подтверждает партнёр, у которого вы покупаете билет.',
    },
    'route.prose_buy': {
        'sr': 'Kartu za rutu {from_city} — {to_city} možete kupiti direktno kod prevoznika na autobuskoj stanici ili online preko partnera (Bookaway, BusTicket4.me). Online kupovina obično nudi nekoliko različitih polazaka po istoj ceni, pa vredi uporediti vremena. Za grupe preko 5 putnika ili studentske popuste kontaktirajte prevoznika direktno — Prevozni ne prodaje karte i nije posrednik u kupovini.',
        'en': 'You can buy a ticket for {from_city} — {to_city} directly from the carrier at the bus station or online via partners (Bookaway, BusTicket4.me). Online purchase usually offers several departures at the same price, so it is worth comparing times. For groups of 5+ or student discounts contact the carrier directly — Prevozni does not sell tickets and is not a purchase intermediary.',
        'ru': 'Билет на маршрут {from_city} — {to_city} можно купить напрямую у перевозчика на автовокзале или онлайн через партнёров (Bookaway, BusTicket4.me). Онлайн-покупка обычно предлагает несколько отправлений по одной цене — стоит сравнить время. Для групп от 5 человек или студенческих скидок обращайтесь напрямую к перевозчику — Prevozni не продаёт билеты и не является посредником.',
    },
    'city_pair.title_travel': {
        'sr': 'autobus, voz, cene',
        'en': 'bus, train, prices',
        'ru': 'автобус, поезд, цены',
    },
    'city_pair.meta_cta': {
        'sr': 'Uporedi polaske, cene i vreme putovanja. Besplatno.',
        'en': 'Compare departures, prices and travel time. Free.',
        'ru': 'Сравните отправления, цены и время в пути. Бесплатно.',
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
    },
    'stop_detail.title_stop_city': {
        'sr': 'linije i polasci',
        'en': 'lines and departures',
        'ru': 'линии и отправления',
    },
    'stop_detail.meta_eta': {
        'sr': 'Sve linije, prvi i poslednji polazak, uživo ETA na karti.',
        'en': 'All lines, first and last departure, live ETA on the map.',
        'ru': 'Все линии, первый и последний рейс, онлайн-ETA на карте.',
    },

    # ── search_results.html ──
    'search_results.meta_from': {
        'sr': 'Red vožnje od',
        'en': 'Schedule from',
        'ru': 'Расписание от',
    },
    'search_results.meta_to': {
        'sr': 'do',
        'en': 'to',
        'ru': 'до',
    },
    'search_results.meta_desc': {
        'sr': 'svi polasci, cene karata i prevoznici na jednom mestu.',
        'en': 'all departures, ticket prices and carriers in one place.',
        'ru': 'все отправления, цены билетов и перевозчики в одном месте.',
    },
    'search_results.meta_default': {
        'sr': 'Pretražite red vožnje autobusa i vozova između gradova Srbije. Uporedite polaske, cene i prevoznike. Besplatno.',
        'en': 'Search bus and train schedules between cities in Serbia. Compare departures, prices and carriers. Free.',
        'ru': 'Ищите расписание автобусов и поездов между городами Сербии. Сравнивайте отправления, цены и перевозчиков. Бесплатно.',
    },
    'search_results.h1': {
        'sr': 'Pronađite prevoz',
        'en': 'Find transport',
        'ru': 'Найдите транспорт',
    },
    'search_results.hero_sub': {
        'sr': 'Autobus ili voz između gradova Srbije',
        'en': 'Bus or train between cities in Serbia',
        'ru': 'Автобус или поезд между городами Сербии',
    },
    'search_results.sort_label': {
        'sr': 'Sortiraj:',
        'en': 'Sort:',
        'ru': 'Сортировка:',
    },
    'search_results.sort_time': {
        'sr': 'Po vremenu',
        'en': 'By time',
        'ru': 'По времени',
    },
    'search_results.sort_price': {
        'sr': 'Po ceni',
        'en': 'By price',
        'ru': 'По цене',
    },

    # ── city_transport.html ──
    'city_transport.title_prefix': {
        'sr': 'Gradski prevoz',
        'en': 'City transport',
        'ru': 'Городской транспорт',
    },
    'city_transport.title_suffix': {
        'sr': 'linije i stajališta',
        'en': 'lines and stops',
        'ru': 'линии и остановки',
    },
    'city_transport.meta_prefix': {
        'sr': 'Red vožnje gradskog prevoza u',
        'en': 'City transport schedule in',
        'ru': 'Расписание городского транспорта в',
    },
    'city_transport.meta_lines': {
        'sr': 'linija, stajališta i polasci.',
        'en': 'lines, stops and departures.',
        'ru': 'линий, остановок и отправлений.',
    },
    'city_transport.meta_extra': {
        'sr': 'Interaktivna mapa stajališta, red vožnje i dolasci uživo. Besplatno →',
        'en': 'Interactive stop map, schedules and live arrivals. Free →',
        'ru': 'Интерактивная карта остановок, расписание и прибытия онлайн. Бесплатно →',
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
    },
    'line_detail.line_prefix': {
        'sr': 'Linija',
        'en': 'Line',
        'ru': 'Линия',
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
    },
    'line_detail.meta_to': {
        'sr': 'do',
        'en': 'to',
        'ru': 'до',
    },

    # ── stop_detail.html ──
    'stop_detail.stop_prefix': {
        'sr': 'Stajalište',
        'en': 'Stop',
        'ru': 'Остановка',
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
    },
    'filter.close': {
        'sr': 'Zatvori',
        'en': 'Close',
        'ru': 'Закрыть',
    },
    'filter.transport_type': {
        'sr': 'Tip prevoza',
        'en': 'Transport type',
        'ru': 'Тип транспорта',
    },
    'filter.bus': {
        'sr': 'Autobus',
        'en': 'Bus',
        'ru': 'Автобус',
    },
    'filter.train': {
        'sr': 'Voz',
        'en': 'Train',
        'ru': 'Поезд',
    },
    'filter.carrier': {
        'sr': 'Prevoznik',
        'en': 'Carrier',
        'ru': 'Перевозчик',
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
    },
    'city_pair.faq.q_price': {
        'sr': 'Koja je cena karte {from_city} — {to_city}?',
        'en': 'What is the ticket price for {from_city} — {to_city}?',
        'ru': 'Сколько стоит билет {from_city} — {to_city}?',
    },
    'city_pair.faq.q_departures': {
        'sr': 'Koliko polazaka dnevno ima {from_city} — {to_city}?',
        'en': 'How many daily departures are there from {from_city} to {to_city}?',
        'ru': 'Сколько ежедневных рейсов {from_city} — {to_city}?',
    },
    'city_pair.faq.q_operators': {
        'sr': 'Koji prevoznici voze {from_city} — {to_city}?',
        'en': 'Which carriers operate {from_city} — {to_city}?',
        'ru': 'Какие перевозчики обслуживают {from_city} — {to_city}?',
    },
    'city_pair.faq.a_duration_range': {
        'sr': 'Putovanje od {from_city} do {to_city} traje od {h_min}h {m_min}min do {h_max}h {m_max}min.',
        'en': 'The trip from {from_city} to {to_city} takes from {h_min}h {m_min}min up to {h_max}h {m_max}min.',
        'ru': 'Поездка из {from_city} в {to_city} занимает от {h_min}ч {m_min}мин до {h_max}ч {m_max}мин.',
    },
    'city_pair.faq.a_duration_distance_suffix': {
        'sr': ' Rastojanje je {km} km.',
        'en': ' The distance is {km} km.',
        'ru': ' Расстояние — {km} км.',
    },
    'city_pair.faq.a_duration_distance_only': {
        'sr': 'Rastojanje je oko {km} km. Tačno trajanje zavisi od prevoznika.',
        'en': 'The distance is about {km} km. Exact duration depends on the carrier.',
        'ru': 'Расстояние около {km} км. Точное время зависит от перевозчика.',
    },
    'city_pair.faq.a_duration_unknown': {
        'sr': 'Trajanje zavisi od prevoznika i tipa prevoza.',
        'en': 'Duration depends on the carrier and transport type.',
        'ru': 'Время в пути зависит от перевозчика и вида транспорта.',
    },
    'city_pair.faq.a_price_range': {
        'sr': 'Cene karata kreću se od {min} do {max} RSD ({eur_min}–{eur_max}€).',
        'en': 'Ticket prices range from {min} to {max} RSD ({eur_min}–{eur_max}€).',
        'ru': 'Цены билетов варьируются от {min} до {max} RSD ({eur_min}–{eur_max}€).',
    },
    'city_pair.faq.a_price_cheapest_suffix': {
        'sr': ' Najjeftiniji prevoznik je {operator}.',
        'en': ' The cheapest carrier is {operator}.',
        'ru': ' Самый дешёвый перевозчик — {operator}.',
    },
    'city_pair.faq.a_price_from': {
        'sr': 'Cene karata počinju od {min} RSD (oko {eur}€).',
        'en': 'Ticket prices start from {min} RSD (about {eur}€).',
        'ru': 'Цены билетов начинаются от {min} RSD (около {eur}€).',
    },
    'city_pair.faq.a_price_unknown': {
        'sr': 'Cene variraju u zavisnosti od prevoznika.',
        'en': 'Prices vary depending on the carrier.',
        'ru': 'Цены зависят от перевозчика.',
    },
    'city_pair.faq.a_departures_full': {
        'sr': 'Na ovoj ruti ima {count} polazaka dnevno. Prvi polazak je u {first}, poslednji u {last}.',
        'en': 'This route has {count} daily departures. First at {first}, last at {last}.',
        'ru': 'На этом маршруте {count} рейсов в день. Первый в {first}, последний в {last}.',
    },
    'city_pair.faq.a_departures_operators_suffix': {
        'sr': ' Voze: {operators}.',
        'en': ' Operated by: {operators}.',
        'ru': ' Обслуживают: {operators}.',
    },
    'city_pair.faq.a_departures_count_only': {
        'sr': 'Na ovoj ruti ima {count} polazaka dnevno.',
        'en': 'This route has {count} daily departures.',
        'ru': 'На этом маршруте {count} рейсов в день.',
    },
    'city_pair.faq.a_departures_unknown': {
        'sr': 'Broj polazaka varira. Proverite aktuelni red vožnje.',
        'en': 'The number of departures varies. Check the current schedule.',
        'ru': 'Количество рейсов меняется. Проверьте актуальное расписание.',
    },
    'city_pair.faq.a_operators_list': {
        'sr': 'Na liniji {from_city} — {to_city} voze {n} prevoznika: {operators}.',
        'en': 'On the {from_city} — {to_city} route there are {n} carriers: {operators}.',
        'ru': 'На маршруте {from_city} — {to_city} работают {n} перевозчиков: {operators}.',
    },
    'city_pair.faq.a_operators_cheapest_suffix': {
        'sr': ' Najjeftiniji prevoznik je {operator} sa cenama od {min} RSD.',
        'en': ' The cheapest carrier is {operator} with prices from {min} RSD.',
        'ru': ' Самый дешёвый перевозчик — {operator}, цены от {min} RSD.',
    },
    # JSON-LD short variants
    'city_pair.faq.ld_duration_range': {
        'sr': 'Putovanje traje od {h_min}h {m_min}min do {h_max}h {m_max}min.',
        'en': 'The trip takes from {h_min}h {m_min}min up to {h_max}h {m_max}min.',
        'ru': 'Поездка занимает от {h_min}ч {m_min}мин до {h_max}ч {m_max}мин.',
    },
    'city_pair.faq.ld_price_range': {
        'sr': 'Od {min} do {max} RSD ({eur_min}–{eur_max}€).',
        'en': 'From {min} to {max} RSD ({eur_min}–{eur_max}€).',
        'ru': 'От {min} до {max} RSD ({eur_min}–{eur_max}€).',
    },
    'city_pair.faq.ld_price_cheapest_suffix': {
        'sr': ' Najjeftiniji: {operator}.',
        'en': ' Cheapest: {operator}.',
        'ru': ' Самый дешёвый: {operator}.',
    },
    'city_pair.faq.ld_price_from': {
        'sr': 'Od {min} RSD ({eur}€).',
        'en': 'From {min} RSD ({eur}€).',
        'ru': 'От {min} RSD ({eur}€).',
    },
    'city_pair.faq.ld_price_unknown': {
        'sr': 'Cene variraju.',
        'en': 'Prices vary.',
        'ru': 'Цены варьируются.',
    },
    'city_pair.faq.ld_departures_full': {
        'sr': '{count} polazaka dnevno. Prvi u {first}, poslednji u {last}.',
        'en': '{count} departures daily. First at {first}, last at {last}.',
        'ru': '{count} рейсов в день. Первый в {first}, последний в {last}.',
    },
    'city_pair.faq.ld_departures_count_only': {
        'sr': '{count} polazaka dnevno.',
        'en': '{count} departures daily.',
        'ru': '{count} рейсов в день.',
    },
    'city_pair.faq.ld_departures_unknown': {
        'sr': 'Broj polazaka varira.',
        'en': 'The number of departures varies.',
        'ru': 'Количество рейсов меняется.',
    },
    'city_pair.faq.ld_operators_list': {
        'sr': 'Voze {n} prevoznika: {operators}.',
        'en': '{n} carriers operate: {operators}.',
        'ru': '{n} перевозчиков: {operators}.',
    },

    # ── route_detail FAQ JSON-LD ──
    'route_detail.faq.q_departures': {
        'sr': 'Koliko polazaka ima od {from_city} do {to_city}?',
        'en': 'How many departures are there from {from_city} to {to_city}?',
        'ru': 'Сколько рейсов из {from_city} в {to_city}?',
    },
    'route_detail.faq.a_departures': {
        'sr': 'Dnevno ima {count} polazaka od {from_city} do {to_city}.',
        'en': 'There are {count} daily departures from {from_city} to {to_city}.',
        'ru': 'Ежедневно выполняется {count} рейсов из {from_city} в {to_city}.',
    },
    'route_detail.faq.q_price': {
        'sr': 'Koliko košta karta {from_city} — {to_city}?',
        'en': 'How much is a {from_city} — {to_city} ticket?',
        'ru': 'Сколько стоит билет {from_city} — {to_city}?',
    },
    'route_detail.faq.a_price_from': {
        'sr': 'Cena karte počinje od {min} RSD.',
        'en': 'Ticket price starts from {min} RSD.',
        'ru': 'Цена билета начинается от {min} RSD.',
    },
    'route_detail.faq.a_price_unknown': {
        'sr': 'Cene variraju u zavisnosti od prevoznika; proverite aktuelne cene na stranici.',
        'en': 'Prices vary by carrier; check current prices on the page.',
        'ru': 'Цены зависят от перевозчика; проверьте актуальные цены на странице.',
    },
    'route_detail.faq.q_operators': {
        'sr': 'Koji prevoznici voze liniju {from_city} — {to_city}?',
        'en': 'Which carriers operate the {from_city} — {to_city} route?',
        'ru': 'Какие перевозчики обслуживают маршрут {from_city} — {to_city}?',
    },
    'route_detail.faq.a_operators_list': {
        'sr': 'Na ovoj liniji voze: {operators}.',
        'en': 'This route is operated by: {operators}.',
        'ru': 'Этот маршрут обслуживают: {operators}.',
    },
    'route_detail.faq.a_operators_unknown': {
        'sr': 'Proverite listu polazaka za aktuelne prevoznike.',
        'en': 'Check the departures list for current carriers.',
        'ru': 'Проверьте список рейсов для актуальных перевозчиков.',
    },

    # ── line_detail FAQ JSON-LD ──
    'line_detail.faq.q_stops': {
        'sr': 'Koliko stajališta ima linija {number}?',
        'en': 'How many stops does line {number} have?',
        'ru': 'Сколько остановок у линии {number}?',
    },
    'line_detail.faq.a_stops': {
        'sr': 'Linija {number} ({name}) u {city}u ima {count} stajališta, od {first} do {last}.',
        'en': 'Line {number} ({name}) in {city} has {count} stops, from {first} to {last}.',
        'ru': 'Линия {number} ({name}) в городе {city} имеет {count} остановок, от {first} до {last}.',
    },
    'line_detail.faq.a_stops_no_endpoints': {
        'sr': 'Linija {number} ({name}) u {city}u ima {count} stajališta.',
        'en': 'Line {number} ({name}) in {city} has {count} stops.',
        'ru': 'Линия {number} ({name}) в городе {city} имеет {count} остановок.',
    },
    'line_detail.faq.q_when': {
        'sr': 'Kada saobraća linija {number}?',
        'en': 'When does line {number} run?',
        'ru': 'Когда работает линия {number}?',
    },
    'line_detail.faq.a_when_range': {
        'sr': 'Linija {number} saobraća od {first} do {last} radnim danom prema GTFS redu vožnje.',
        'en': 'Line {number} runs from {first} to {last} on weekdays according to the GTFS schedule.',
        'ru': 'Линия {number} работает с {first} до {last} по будням согласно расписанию GTFS.',
    },
    'line_detail.faq.a_when_unknown': {
        'sr': 'Tačan red vožnje linije {number} proverite na stajalištima ili kod gradskog prevoznika.',
        'en': 'Check the exact schedule for line {number} at the stops or with the city carrier.',
        'ru': 'Точное расписание линии {number} уточняйте на остановках или у городского перевозчика.',
    },
    'line_detail.faq.q_type': {
        'sr': 'Koji je tip linije {number}?',
        'en': 'What type is line {number}?',
        'ru': 'Какой тип у линии {number}?',
    },
    'line_detail.faq.a_type': {
        'sr': 'Linija {number} je {type} u sistemu gradskog prevoza grada {city}.',
        'en': 'Line {number} is a {type} in the {city} city transport system.',
        'ru': 'Линия {number} — это {type} в системе городского транспорта города {city}.',
    },

    # ── stop_detail FAQ JSON-LD ──
    'stop_detail.faq.q_lines': {
        'sr': 'Koje linije staju na stajalištu {stop}?',
        'en': 'Which lines stop at {stop}?',
        'ru': 'Какие линии останавливаются на остановке {stop}?',
    },
    'stop_detail.faq.a_lines': {
        'sr': 'Na stajalištu {stop} u {city}u staje {count} linija gradskog prevoza ({types}).',
        'en': 'At stop {stop} in {city}, {count} city transport lines stop ({types}).',
        'ru': 'На остановке {stop} в городе {city} останавливается {count} линий городского транспорта ({types}).',
    },
    'stop_detail.faq.q_when': {
        'sr': 'Kada polaze autobusi sa stajališta {stop}?',
        'en': 'When do buses depart from {stop}?',
        'ru': 'Когда отправляются автобусы с остановки {stop}?',
    },
    'stop_detail.faq.a_when_range': {
        'sr': 'Prvi polazak sa stajališta {stop} je u {first}, a poslednji u {last} radnim danom.',
        'en': 'The first departure from {stop} is at {first}, the last at {last} on weekdays.',
        'ru': 'Первый рейс с остановки {stop} в {first}, последний в {last} по будням.',
    },
    'stop_detail.faq.a_when_unknown': {
        'sr': 'Tačan red vožnje proverite na samom stajalištu ili preko mobilne aplikacije gradskog prevoznika.',
        'en': 'Check the exact schedule at the stop itself or via the city carrier mobile app.',
        'ru': 'Точное расписание уточняйте на самой остановке или в мобильном приложении городского перевозчика.',
    },
    'stop_detail.faq.q_where': {
        'sr': 'Gde se nalazi stajalište {stop}?',
        'en': 'Where is stop {stop} located?',
        'ru': 'Где находится остановка {stop}?',
    },
    'stop_detail.faq.a_where': {
        'sr': 'Stajalište {stop} se nalazi u gradu {city}.',
        'en': 'Stop {stop} is located in the city of {city}.',
        'ru': 'Остановка {stop} находится в городе {city}.',
    },
    'stop_detail.faq.a_where_coords_suffix': {
        'sr': ' Koordinate: {lat}, {lon}.',
        'en': ' Coordinates: {lat}, {lon}.',
        'ru': ' Координаты: {lat}, {lon}.',
    },
    'stop_detail.faq.a_where_outro': {
        'sr': ' Detaljna mapa i lista linija dostupni su besplatno na Prevozni.com.',
        'en': ' A detailed map and list of lines are available for free on Prevozni.com.',
        'ru': ' Подробная карта и список линий доступны бесплатно на Prevozni.com.',
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
              'Na svakoj stranici rute nalazi se dugme „Kupi kartu" koje vodi na partnerski sistem (Bookaway) gde se kupovina obavlja online. '
              'Karte se takođe kupuju na blagajni autobuske stanice ili kod vozača u autobusu.',
        'en': 'Prevozni.com is an information service — timetables are free and require no registration. '
              'Each route page has a "Buy ticket" button that opens our partner (Bookaway) for online booking. '
              'Tickets are also sold at the bus station counter or on-board from the driver.',
        'ru': 'Prevozni.com — информационный сервис: расписание бесплатно и без регистрации. '
              'На каждой странице маршрута есть кнопка «Купить билет», которая ведёт к партнёру (Bookaway) для онлайн-покупки. '
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
    },
    'city_transport.faq_heading': {
        'sr': 'Često postavljana pitanja',
        'en': 'Frequently asked questions',
        'ru': 'Частые вопросы',
    },
    'city_transport.faq_q1': {
        'sr': 'Kako da kupim kartu za gradski prevoz u {city}u?',
        'en': 'How do I buy a transit ticket in {city}?',
        'ru': 'Как купить билет на городской транспорт в {city}?',
    },
    'city_transport.faq_q2': {
        'sr': 'Koliko linija opslužuje {city}?',
        'en': 'How many lines serve {city}?',
        'ru': 'Сколько линий обслуживает {city}?',
    },
    'city_transport.faq_a2': {
        'sr': 'U mreži ima {n} aktivnih linija, sa ukupno {stops} stajališta mapiranih u našoj bazi. '
              'Brojevi linija prikazuju se sa filterom po tipu (autobus, tramvaj, trolejbus, noćna) u vrhu stranice.',
        'en': '{n} active lines serve the city, with {stops} stops mapped in our database. '
              'Lines are filterable by type (bus, tram, trolleybus, night) at the top of the page.',
        'ru': 'Сеть включает {n} активных линий и {stops} остановок в нашей базе. '
              'Линии можно фильтровать по типу (автобус, трамвай, троллейбус, ночная) вверху страницы.',
    },
    'city_transport.faq_q3': {
        'sr': 'Radi li gradski prevoz nedeljom i praznikom?',
        'en': 'Does transit run on Sundays and holidays?',
        'ru': 'Работает ли транспорт по воскресеньям и праздникам?',
    },
    'city_transport.faq_a3': {
        'sr': 'Da, većina linija saobraća sedam dana u nedelji, sa smanjenom frekvencijom subotom i nedeljom. '
              'Raspored vidite u rubrici „Subota" i „Nedelja" na stranici svake linije. Državnim praznicima obično se primenjuje nedeljni raspored.',
        'en': 'Yes, most lines run seven days a week with reduced weekend frequency. '
              'The schedule is split into Saturday and Sunday tabs on each line page. On public holidays the Sunday schedule typically applies.',
        'ru': 'Да, большинство линий работают 7 дней в неделю с сокращённой частотой по выходным. '
              'Расписание в табах «Субота» и «Недеља» на странице каждой линии. В госпраздники обычно действует воскресное расписание.',
    },
    'city_transport.faq_q4': {
        'sr': 'Kako stižem iz {city}a u druge gradove Srbije?',
        'en': 'How do I get from {city} to other cities in Serbia?',
        'ru': 'Как добраться из {city} в другие города Сербии?',
    },
    'city_transport.faq_a4': {
        'sr': 'Za međugradski prevoz koristite našu stranicu <a href="{prefix}/rute/">svih ruta</a> ili direktno tražite polazak preko '
              '<a rel="nofollow" href="{prefix}/pretraga/?od={city}">polazaka iz {city}a</a>. Prikazujemo autobuske i železničke rute sa cenom, trajanjem i brojem polazaka.',
        'en': 'For intercity travel use the <a href="{prefix}/rute/">all-routes page</a> or search directly via '
              '<a rel="nofollow" href="{prefix}/pretraga/?od={city}">departures from {city}</a>. We show bus and train routes with price, duration and departure count.',
        'ru': 'Для междугородних поездок используйте <a href="{prefix}/rute/">страницу всех маршрутов</a> или ищите напрямую через '
              '<a rel="nofollow" href="{prefix}/pretraga/?od={city}">рейсы из {city}</a>. Показываем автобусные и ж/д маршруты с ценой, временем и количеством рейсов.',
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
    },
    'review.prompt_intro': {
        'sr': 'Kako je prošlo putovanje',
        'en': 'How was your trip',
        'ru': 'Как прошла поездка',
    },
    'review.prompt_cta': {
        'sr': 'Ostavi recenziju',
        'en': 'Leave a review',
        'ru': 'Оставить отзыв',
    },
    'a11y.dismiss': {
        'sr': 'Zatvori',
        'en': 'Dismiss',
        'ru': 'Закрыть',
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

    # ── home FAQ (only) ──
    'home.faq_heading': {
        'sr': 'Često postavljana pitanja',
        'en': 'Frequently asked questions',
        'ru': 'Частые вопросы',
    },
    'home.faq_q1': {
        'sr': 'Šta je Prevozni.com?',
        'en': 'What is Prevozni.com?',
        'ru': 'Что такое Prevozni.com?',
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
    },
    'home.faq_q2': {
        'sr': 'Koje gradove i rute pokriva sajt?',
        'en': 'Which cities and routes does the site cover?',
        'ru': 'Какие города и маршруты покрывает сайт?',
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
    },
    'home.faq_q3': {
        'sr': 'Da li je sajt besplatan i bez reklama?',
        'en': 'Is the site free and ad-free?',
        'ru': 'Бесплатный ли сайт и без рекламы?',
    },
    'home.faq_a3': {
        'sr': 'Da, Prevozni.com je potpuno besplatan i bez registracije. Ne prikazujemo invazivne reklame i ne prodajemo vaše podatke. '
              'Posetu pratimo samo putem anonimne analitike (Umami), a projekat se izdržava povremenim affiliate provizijama kod kupovine karata preko naših partnera.',
        'en': 'Yes, Prevozni.com is fully free and no-signup. We do not display intrusive ads and do not sell your data. '
              'Visits are tracked only with anonymous analytics (Umami); the project is funded by occasional affiliate commissions when you buy tickets via our partners.',
        'ru': 'Да, Prevozni.com полностью бесплатный и без регистрации. Мы не показываем навязчивую рекламу и не продаём ваши данные. '
              'Посещения фиксируются только анонимной аналитикой (Umami); проект живёт за счёт редких партнёрских комиссий при покупке билетов через партнёров.',
    },

    # ── Popular / "See also" blocks ──
    'city_transport.popular_routes_h': {
        'sr': 'Popularne međugradske rute iz {city}a',
        'en': 'Popular intercity routes from {city}',
        'ru': 'Популярные междугородние маршруты из {city}',
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
    },
    'line_prose.heading': {
        'sr': 'O liniji {number} — {city}',
        'en': 'About line {number} in {city}',
        'ru': 'О линии {number} — {city}',
    },

    # ── Reviews / UGC ──
    'review.heading': {
        'sr': 'Iskustva putnika', 'en': 'Traveller reviews', 'ru': 'Отзывы пассажиров',
    },
    'review.summary_empty': {
        'sr': 'Budite prvi koji ostavlja recenziju za ovu rutu.',
        'en': 'Be the first to review this route.',
        'ru': 'Будьте первым, кто оставит отзыв о маршруте.',
    },
    'review.summary_few': {
        'sr': '{n} ocena, prosek {avg} ★ · podelite i vaše iskustvo',
        'en': '{n} ratings, average {avg} ★ · share your experience too',
        'ru': '{n} оценок, средняя {avg} ★ · поделитесь своим опытом',
    },
    'review.summary': {
        'sr': '{n} ocena · prosek {avg} ★',
        'en': '{n} ratings · average {avg} ★',
        'ru': '{n} оценок · средняя {avg} ★',
    },
    'review.form_heading': {
        'sr': 'Ostavite vašu recenziju', 'en': 'Leave your review', 'ru': 'Оставить отзыв',
    },
    'review.cta_short': {
        'sr': 'Ostavite recenziju',
        'en': 'Write a review',
        'ru': 'Оставить отзыв',
    },
    'review.rating_label': {
        'sr': 'Ocena (1–5)', 'en': 'Rating (1–5)', 'ru': 'Оценка (1–5)',
    },
    'review.comment_label': {
        'sr': 'Komentar (50–500 znakova)',
        'en': 'Comment (50–500 characters)',
        'ru': 'Комментарий (50–500 символов)',
    },
    'review.comment_ph': {
        'sr': 'Kako je bila vožnja? Komfor, tačnost, cena, osoblje, prtljag, WiFi, stajališta…',
        'en': 'How was the ride? Comfort, timekeeping, price, staff, luggage, WiFi, stops…',
        'ru': 'Как прошла поездка? Комфорт, пунктуальность, цена, персонал, багаж, WiFi, остановки…',
    },
    'review.name_label': {'sr': 'Ime (2–40 slova)', 'en': 'Name (2–40 letters)', 'ru': 'Имя (2–40 букв)'},
    'review.email_label': {
        'sr': 'Email (opciono, za obaveštenje)',
        'en': 'Email (optional, for approval notice)',
        'ru': 'Email (необязательно, для уведомления)',
    },
    'review.submit': {'sr': 'Pošalji recenziju', 'en': 'Submit review', 'ru': 'Отправить отзыв'},
    'review.consent': {
        'sr': 'Slanjem dozvoljavate objavu vaše ocene i komentara nakon moderacije. Email ne objavljujemo.',
        'en': 'By submitting you allow us to publish the rating and comment after moderation. Email is never published.',
        'ru': 'Отправляя отзыв, вы разрешаете опубликовать оценку и комментарий после модерации. Email не публикуем.',
    },
    'review.ok.pending': {
        'sr': 'Hvala! Pregledaćemo recenziju u roku od 24–48 h.',
        'en': 'Thanks! We will review your comment within 24–48 hours.',
        'ru': 'Спасибо! Мы проверим отзыв в течение 24–48 часов.',
    },
    'review.ok.auto': {
        'sr': 'Hvala! Recenzija je objavljena.',
        'en': 'Thanks! Your review is live.',
        'ru': 'Спасибо! Отзыв опубликован.',
    },
    'review.err.generic': {
        'sr': 'Došlo je do greške. Pokušajte ponovo.',
        'en': 'Something went wrong. Please try again.',
        'ru': 'Что-то пошло не так. Попробуйте снова.',
    },
    'review.err.rate_limit': {
        'sr': 'Previše pokušaja u kratkom vremenu. Pokušajte ponovo za sat vremena.',
        'en': 'Too many attempts. Please retry in about an hour.',
        'ru': 'Слишком много попыток. Повторите примерно через час.',
    },
    'review.err.rating': {
        'sr': 'Odaberite ocenu od 1 do 5 zvezdica.',
        'en': 'Pick a rating from 1 to 5 stars.',
        'ru': 'Выберите оценку от 1 до 5 звёзд.',
    },
    'review.err.comment_length': {
        'sr': 'Komentar treba da ima 50–500 znakova.',
        'en': 'Comment must be 50–500 characters.',
        'ru': 'Комментарий должен быть 50–500 символов.',
    },
    'review.err.name_length': {
        'sr': 'Ime treba da ima 2–40 slova.',
        'en': 'Name must be 2–40 letters.',
        'ru': 'Имя должно быть 2–40 букв.',
    },
    'review.err.email_invalid': {
        'sr': 'Email adresa nije validna.',
        'en': 'Email address is not valid.',
        'ru': 'Email адрес недействителен.',
    },
    'review.err.no_urls': {
        'sr': 'Linkovi na spoljne sajtove nisu dozvoljeni u komentarima.',
        'en': 'Links to external sites are not allowed in comments.',
        'ru': 'Ссылки на внешние сайты в комментариях не разрешены.',
    },
    'review.err.profanity': {
        'sr': 'Komentar sadrži neprihvatljiv sadržaj.',
        'en': 'Comment contains unacceptable content.',
        'ru': 'Комментарий содержит неприемлемое содержание.',
    },
    'review.err.spam': {
        'sr': 'Slanje je odbijeno.',
        'en': 'Submission rejected.',
        'ru': 'Отправка отклонена.',
    },
    'review.err.too_fast': {
        'sr': 'Pokušaj je prebrz — pročitajte formu pažljivo.',
        'en': 'That was too fast — please read the form and try again.',
        'ru': 'Слишком быстро — перечитайте форму и попробуйте ещё раз.',
    },
    'review.delete.link': {
        'sr': 'Zatraži brisanje',
        'en': 'Request deletion',
        'ru': 'Запросить удаление',
    },
    'review.delete.prompt': {
        'sr': 'Unesite email adresu kojom ste ostavili recenziju:',
        'en': 'Enter the email you submitted the review with:',
        'ru': 'Введите email, с которым вы оставили отзыв:',
    },
    'review.delete.sent': {
        'sr': 'Zahtev za brisanje je primljen. Obradićemo ga u roku od 7 dana u skladu sa GDPR-om.',
        'en': 'Deletion request received. We will process it within 7 days per GDPR.',
        'ru': 'Запрос на удаление принят. Обработаем в течение 7 дней согласно GDPR.',
    },
    'review.lang_note': {
        'sr': 'Recenzija na srpskom', 'en': 'Review in English', 'ru': 'Отзыв на русском',
    },

    # ── Newsletter / email subscribe ──
    'newsletter.title': {
        'sr': 'Newsletter',
        'en': 'Newsletter',
        'ru': 'Рассылка',
    },
    'newsletter.subtitle': {
        'sr': 'Najjeftinije karte i nove rute — jednom nedeljno. Bez spama.',
        'en': 'Cheapest tickets and new routes, weekly. No spam.',
        'ru': 'Самые дешёвые билеты и новые маршруты — раз в неделю. Без спама.',
    },
    'newsletter.placeholder': {
        'sr': 'vaš@email.rs',
        'en': 'your@email.com',
        'ru': 'ваш@email.ru',
    },
    'newsletter.button': {
        'sr': 'Pretplati se',
        'en': 'Subscribe',
        'ru': 'Подписаться',
    },
    'newsletter.consent': {
        'sr': 'Saglasan/a sam sa obradom email adrese prema <a href="{prefix}/privatnost/">Politici privatnosti</a>.',
        'en': 'I agree to email processing per the <a href="{prefix}/privatnost/">Privacy policy</a>.',
        'ru': 'Согласен/на с обработкой email согласно <a href="{prefix}/privatnost/">Политике конфиденциальности</a>.',
    },
    'newsletter.success_pending': {
        'sr': 'Proverite email — poslali smo Vam link za potvrdu.',
        'en': 'Check your inbox — we sent a confirmation link.',
        'ru': 'Проверьте почту — отправили письмо с подтверждением.',
    },
    'newsletter.success_already': {
        'sr': 'Već ste pretplaćeni — hvala!',
        'en': "You're already subscribed — thanks!",
        'ru': 'Вы уже подписаны — спасибо!',
    },
    'newsletter.error_email': {
        'sr': 'Email adresa nije ispravna.',
        'en': 'Email address is invalid.',
        'ru': 'Некорректный email.',
    },
    'newsletter.error_consent': {
        'sr': 'Potvrdite saglasnost da biste se pretplatili.',
        'en': 'Tick the consent box to subscribe.',
        'ru': 'Отметьте согласие, чтобы подписаться.',
    },
    'newsletter.error_generic': {
        'sr': 'Greška pri slanju. Pokušajte ponovo.',
        'en': 'Something went wrong. Try again.',
        'ru': 'Ошибка отправки. Попробуйте ещё раз.',
    },
    'newsletter.error_ratelimit': {
        'sr': 'Previše pokušaja. Pokušajte za sat vremena.',
        'en': 'Too many attempts. Try again in an hour.',
        'ru': 'Слишком много попыток. Попробуйте через час.',
    },

    # ── Price-alert (route-scoped newsletter) ──
    'price_alert.title': {
        'sr': 'Obaveštenje o ceni',
        'en': 'Price alert',
        'ru': 'Уведомление о цене',
    },
    'price_alert.subtitle': {
        'sr': 'Javljamo kada cena za {pair} padne ili stigne akcija.',
        'en': "We'll email when {pair} drops in price or goes on sale.",
        'ru': 'Сообщим, когда цена {pair} упадёт или появится акция.',
    },
    'price_alert.button': {
        'sr': 'Prati cenu',
        'en': 'Track price',
        'ru': 'Следить за ценой',
    },
    'price_alert.sub_hint': {
        'sr': 'Jedan email kad najniža cena padne za 10% ili više.',
        'en': 'One email whenever the cheapest ticket drops 10% or more.',
        'ru': 'Одно письмо, когда минимальная цена падает на 10% и больше.',
    },
    'price_alert.ok_check_inbox': {
        'sr': 'Proverite email — poslali smo link za potvrdu.',
        'en': 'Check your inbox — we sent a confirmation link.',
        'ru': 'Проверьте почту — мы отправили ссылку для подтверждения.',
    },
    'price_alert.ok_already': {
        'sr': 'Već ste pretplaćeni — obaveštavaćemo Vas čim cena padne.',
        'en': "You're already subscribed — we'll email you on the next drop.",
        'ru': 'Вы уже подписаны — напишем, как только цена упадёт.',
    },
    'price_alert.err': {
        'sr': 'Nešto je pošlo po zlu. Pokušajte ponovo.',
        'en': 'Something went wrong. Please try again.',
        'ru': 'Что-то пошло не так. Попробуйте ещё раз.',
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
    },
    'pwa.install_sub': {
        'sr': 'Brže otvaranje, manje reklama, offline pretraga.',
        'en': 'Faster launches, less clutter, offline search.',
        'ru': 'Быстрый запуск, меньше шума, поиск офлайн.',
    },
    'pwa.install_cta': {
        'sr': 'Instaliraj',
        'en': 'Install',
        'ru': 'Установить',
    },
    'pwa.dismiss': {
        'sr': 'Ne sada',
        'en': 'Not now',
        'ru': 'Не сейчас',
    },
    'pwa.install_ios_title': {
        'sr': 'Dodajte na početni ekran',
        'en': 'Add to Home Screen',
        'ru': 'На главный экран',
    },
    'pwa.install_ios_hint': {
        'sr': 'Otvorite stranicu u Safariju, tapnite dugme Podeli, pa '
              '"Na početni ekran" da instalirate Prevozni kao aplikaciju.',
        'en': 'Open this page in Safari, tap the Share button, then '
              'choose "Add to Home Screen" to install Prevozni as an app.',
        'ru': 'Откройте страницу в Safari, нажмите кнопку «Поделиться» и '
              'выберите «На экран „Домой"», чтобы установить Prevozni.',
    },
    'pwa.install_ios_close': {
        'sr': 'Zatvori',
        'en': 'Close',
        'ru': 'Закрыть',
    },

    # ── Footer legal links + disclosure ──
    'footer.tos': {
        'sr': 'Uslovi korišćenja',
        'en': 'Terms of Service',
        'ru': 'Условия использования',
    },
    'footer.cookies': {
        'sr': 'Politika kolačića',
        'en': 'Cookie Policy',
        'ru': 'Политика cookies',
    },
    'footer.partners': {
        'sr': 'Partnerske provizije: Bookaway, FlixBus. Klikom na "Kupi" možete napustiti naš sajt.',
        'en': 'Partner commissions: Bookaway, FlixBus. Clicking "Buy" may take you off-site.',
        'ru': 'Партнёрские комиссии: Bookaway, FlixBus. Нажатие «Купить» может увести с сайта.',
    },

    # ── Cookie consent banner ──
    'cookies.banner.aria': {
        'sr': 'Obaveštenje o kolačićima',
        'en': 'Cookie notice',
        'ru': 'Уведомление о cookies',
    },
    'cookies.banner.text': {
        'sr': 'Koristimo kolačiće za osnovne funkcije (jezik, valuta, sačuvane rute) i anonimnu analitiku bez praćenja. Možete prihvatiti sve ili samo neophodne.',
        'en': 'We use cookies for essential features (language, currency, saved routes) and anonymous analytics without tracking. You can accept all or essentials only.',
        'ru': 'Мы используем cookies для базовых функций (язык, валюта, сохранённые маршруты) и анонимной аналитики без отслеживания. Можно принять всё или только необходимые.',
    },
    'cookies.banner.accept_all': {
        'sr': 'Prihvatam',
        'en': 'Accept all',
        'ru': 'Принять всё',
    },
    'cookies.banner.essential': {
        'sr': 'Samo neophodni',
        'en': 'Essentials only',
        'ru': 'Только необходимые',
    },
    'cookies.banner.more': {
        'sr': 'Više',
        'en': 'More',
        'ru': 'Подробнее',
    },

    # ── Cookie Policy page ──
    'cookies.page.title': {
        'sr': 'Politika kolačića',
        'en': 'Cookie Policy',
        'ru': 'Политика cookies',
    },
    'cookies.page.meta': {
        'sr': 'Koje kolačiće Prevozni koristi, zašto, koliko se čuvaju i kako da ih onemogućite ili povučete saglasnost.',
        'en': 'Which cookies Prevozni uses, why, how long they are stored, and how to disable them or withdraw consent.',
        'ru': 'Какие cookies использует Prevozni, зачем, сколько хранятся и как их отключить или отозвать согласие.',
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
        'sr': 'Dodeljuje stabilan A/B redosled partnerskih ponuda (Bookaway / FlixBus) po posetiocu.',
        'en': 'Assigns a stable A/B ordering of partner offers (Bookaway / FlixBus) per visitor.',
        'ru': 'Назначает стабильный A/B порядок партнёрских предложений (Bookaway / FlixBus) для посетителя.',
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
        'sr': '<strong>Umami</strong> (analytics.farmako.ro) prikuplja anonimnu agregatnu statistiku poseta <strong>bez kolačića</strong> i bez ličnih identifikatora. Ako prihvatite sve kolačiće, učitavamo Umami skriptu; ako izaberete samo neophodne, skripta se ne učitava. <strong>Bookaway i FlixBus</strong> su partnerski sajtovi — kada kliknete "Kupi", napuštate naš sajt i ulazite pod njihovu politiku kolačića.',
        'en': '<strong>Umami</strong> (analytics.farmako.ro) collects anonymous aggregate visit statistics <strong>without cookies</strong> and without personal identifiers. If you accept all cookies, we load the Umami script; if you choose essentials only, the script is not loaded. <strong>Bookaway and FlixBus</strong> are partner sites — when you click "Buy" you leave our site and fall under their cookie policy.',
        'ru': '<strong>Umami</strong> (analytics.farmako.ro) собирает анонимную агрегированную статистику посещений <strong>без cookies</strong> и без персональных идентификаторов. Если вы принимаете все cookies, мы загружаем скрипт Umami; если выбираете только необходимые — скрипт не загружается. <strong>Bookaway и FlixBus</strong> — партнёрские сайты, при нажатии «Купить» вы покидаете наш сайт и попадаете под их политику cookies.',
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
    },
    'tos.meta': {
        'sr': 'Uslovi korišćenja sajta Prevozni — ko smo, šta nudimo, odricanje od odgovornosti za tačnost podataka, partnerski linkovi i korisnički sadržaj.',
        'en': 'Terms of Service for Prevozni — who we are, what we provide, disclaimer on data accuracy, affiliate links and user content.',
        'ru': 'Условия использования сайта Prevozni — кто мы, что предоставляем, отказ от ответственности за точность данных, партнёрские ссылки и пользовательский контент.',
    },
    'tos.intro': {
        'sr': 'Ovi uslovi regulišu korišćenje sajta prevozni.com. Nastavkom korišćenja prihvatate ih u celini. Ako se ne slažete, molimo ne koristite sajt.',
        'en': 'These terms govern the use of prevozni.com. By continuing to use the site you accept them in full. If you disagree, please do not use the site.',
        'ru': 'Эти условия регулируют использование сайта prevozni.com. Продолжая использовать сайт, вы принимаете их полностью. Если не согласны, пожалуйста, не пользуйтесь сайтом.',
    },
    'tos.updated': {
        'sr': 'Poslednja izmena: april 2026.',
        'en': 'Last updated: April 2026.',
        'ru': 'Последнее обновление: апрель 2026.',
    },
    'tos.s1_h': {
        'sr': '1. Ko smo',
        'en': '1. Who we are',
        'ru': '1. Кто мы',
    },
    'tos.s1_body': {
        'sr': 'Prevozni je nezavisan projekat koji agregira javno dostupne podatke o javnom prevozu u Srbiji i regionu. Nismo prevoznik, agencija za prodaju karata ni zvanični predstavnik bilo kojeg prevoznika. Za kontakt koristite <strong>info@prevozni.com</strong> ili formu na <a href="/kontakt/">/kontakt/</a>.',
        'en': 'Prevozni is an independent project that aggregates publicly available public-transit data for Serbia and the region. We are not a carrier, a ticket agency, or an official representative of any carrier. For contact use <strong>info@prevozni.com</strong> or the form at <a href="/kontakt/">/kontakt/</a>.',
        'ru': 'Prevozni — независимый проект, агрегирующий общедоступные данные об общественном транспорте Сербии и региона. Мы не перевозчик, не билетное агентство и не официальный представитель какого-либо перевозчика. Для связи — <strong>info@prevozni.com</strong> или форма на <a href="/kontakt/">/kontakt/</a>.',
    },
    'tos.s2_h': {
        'sr': '2. Usluge',
        'en': '2. Services',
        'ru': '2. Услуги',
    },
    'tos.s2_body': {
        'sr': 'Sajt pruža besplatan pregled reda vožnje, cena i prevoznika za međugradske autobuse, vozove i gradski prevoz. Ne prodajemo karte; kupovinu obavlja sam prevoznik ili partnerska platforma na koju vas vodi dugme "Kupi". Ne garantujemo dostupnost polaska koji se prikazuje — proverite direktno kod prevoznika pre putovanja.',
        'en': 'The site provides free schedule, price and carrier information for intercity buses, trains and urban transport. We do not sell tickets; purchase is handled by the carrier itself or by a partner platform reached via the "Buy" button. We do not guarantee the availability of any displayed departure — please verify directly with the carrier before travelling.',
        'ru': 'Сайт предоставляет бесплатную информацию о расписании, ценах и перевозчиках для междугородних автобусов, поездов и городского транспорта. Мы не продаём билеты; покупка осуществляется самим перевозчиком или партнёрской платформой по кнопке «Купить». Мы не гарантируем наличие отображаемого рейса — проверяйте непосредственно у перевозчика перед поездкой.',
    },
    'tos.s3_h': {
        'sr': '3. Tačnost podataka',
        'en': '3. Data accuracy',
        'ru': '3. Точность данных',
    },
    'tos.s3_body': {
        'sr': 'Podaci dolaze iz više javnih izvora (vidi <a href="/o-nama/">/o-nama/</a>) i osvežavaju se automatski. Trudimo se da budu tačni, ali ih pružamo "takve kakvi jesu" — bez garancije o ažurnosti, potpunosti ili pogodnosti za određenu namenu. Prevoznici mogu u svakom trenutku promeniti red vožnje, cene ili ukinuti liniju; uvek proverite zvanični sajt prevoznika ili stanice pre puta.',
        'en': 'Data comes from several public sources (see <a href="/o-nama/">/o-nama/</a>) and is refreshed automatically. We aim for accuracy but provide it "as is" — without warranty of timeliness, completeness or fitness for a particular purpose. Carriers can change schedules, prices or cancel lines at any time; always check the carrier\'s or station\'s official site before travelling.',
        'ru': 'Данные поступают из нескольких публичных источников (см. <a href="/o-nama/">/o-nama/</a>) и обновляются автоматически. Мы стремимся к точности, но предоставляем данные «как есть», без гарантий актуальности, полноты или пригодности для конкретной цели. Перевозчики могут в любой момент изменить расписание, цены или отменить рейс; всегда сверяйтесь с официальным сайтом перевозчика или станции перед поездкой.',
    },
    'tos.s4_h': {
        'sr': '4. Partnerski linkovi (affiliate disclosure)',
        'en': '4. Affiliate links (disclosure)',
        'ru': '4. Партнёрские ссылки (disclosure)',
    },
    'tos.s4_body': {
        'sr': 'Neki linkovi za kupovinu karte (dugme "Kupi" pored polaska) vode na partnerske platforme <strong>Bookaway</strong> ili <strong>FlixBus</strong>. Ako kupite kartu preko takvog linka, Prevozni može da dobije malu proviziju koja pokriva troškove održavanja sajta. <strong>Cena koju vi plaćate se ne menja.</strong> Partnerski linkovi su jasno obeleženi kao "Kupi" a u naš sistem se beleži samo anonimni agregirani zapis klika (bez ličnih podataka) — detalji u <a href="/privatnost/">Politici privatnosti</a>.',
        'en': 'Some ticket-purchase links (the "Buy" button next to a departure) go to partner platforms <strong>Bookaway</strong> or <strong>FlixBus</strong>. If you buy a ticket via such a link, Prevozni may receive a small commission that helps cover hosting and maintenance. <strong>The price you pay is not affected.</strong> Affiliate links are clearly labelled "Buy" and only an anonymous aggregate click record (no personal data) is stored on our side — details in the <a href="/privatnost/">Privacy Policy</a>.',
        'ru': 'Некоторые ссылки покупки билета (кнопка «Купить» рядом с рейсом) ведут на партнёрские платформы <strong>Bookaway</strong> или <strong>FlixBus</strong>. Если вы покупаете билет по такой ссылке, Prevozni может получить небольшую комиссию, которая покрывает расходы на хостинг и поддержку. <strong>Цена для вас не меняется.</strong> Партнёрские ссылки явно помечены как «Купить», а у нас сохраняется только анонимная агрегированная запись клика (без персональных данных) — подробности в <a href="/privatnost/">Политике конфиденциальности</a>.',
    },
    'tos.s5_h': {
        'sr': '5. Korisnički sadržaj (recenzije)',
        'en': '5. User content (reviews)',
        'ru': '5. Пользовательский контент (отзывы)',
    },
    'tos.s5_body': {
        'sr': 'Korisnici mogu da ostave recenziju rute. Zadržavate autorska prava nad tekstom koji ste napisali; slanjem nam dajete <strong>ne-isključivu, besplatnu, globalnu licencu</strong> da recenziju javno prikazujemo, indeksiramo i prevodimo kada je to potrebno. Zabranjujemo: spam, linkove, lične podatke trećih lica, uvrede i govor mržnje. Zadržavamo pravo da moderiramo, uredimo ili obrišemo recenziju bez prethodnog obaveštenja. Možete zatražiti brisanje svoje recenzije dugmetom "Zatraži brisanje" ispod nje, u skladu sa <a href="/privatnost/">Politikom privatnosti</a>.',
        'en': 'Users may leave route reviews. You retain copyright over the text you wrote; by submitting you grant us a <strong>non-exclusive, royalty-free, worldwide licence</strong> to display, index and translate the review where relevant. We forbid: spam, links, third-party personal data, insults and hate speech. We reserve the right to moderate, edit or delete any review without prior notice. You can request deletion of your review via the "Request deletion" button beneath it, as described in the <a href="/privatnost/">Privacy Policy</a>.',
        'ru': 'Пользователи могут оставлять отзывы о маршрутах. Авторские права на текст остаются за вами; при отправке вы предоставляете нам <strong>неисключительную, безвозмездную, всемирную лицензию</strong> на публичное отображение, индексацию и перевод отзыва при необходимости. Запрещены: спам, ссылки, персональные данные третьих лиц, оскорбления и язык ненависти. Мы оставляем за собой право модерировать, редактировать или удалять любой отзыв без предварительного уведомления. Удаление своего отзыва можно запросить кнопкой «Запросить удаление» под ним, как описано в <a href="/privatnost/">Политике конфиденциальности</a>.',
    },
    'tos.s6_h': {
        'sr': '6. Ograničenje odgovornosti',
        'en': '6. Limitation of liability',
        'ru': '6. Ограничение ответственности',
    },
    'tos.s6_body': {
        'sr': 'U meri dozvoljenoj zakonom, Prevozni i njegovi autori nisu odgovorni za bilo kakvu direktnu, indirektnu, slučajnu ili posledičnu štetu koja proizlazi iz korišćenja ili nemogućnosti korišćenja sajta, uključujući ali ne ograničavajući se na propuštena putovanja, nekorektne informacije o polascima, cenama ili stanicama, i prekide u radu. Korišćenjem sajta prihvatate da je putovanje vaša lična odluka i odgovornost.',
        'en': 'To the extent permitted by law, Prevozni and its authors are not liable for any direct, indirect, incidental or consequential damages arising from use or inability to use the site, including but not limited to missed trips, incorrect departure / price / station information, and service interruptions. By using the site you agree that travel decisions remain your personal responsibility.',
        'ru': 'В той мере, в какой это допускается законом, Prevozni и его авторы не несут ответственности за прямые, косвенные, случайные или последующие убытки, возникающие в связи с использованием или невозможностью использования сайта, включая (но не ограничиваясь): пропущенные поездки, неверную информацию о рейсах / ценах / станциях и перебои в работе. Используя сайт, вы соглашаетесь, что решение о поездке остаётся вашей личной ответственностью.',
    },
    'tos.s7_h': {
        'sr': '7. Merodavno pravo',
        'en': '7. Governing law',
        'ru': '7. Применимое право',
    },
    'tos.s7_body': {
        'sr': 'Ovi uslovi se tumače u skladu sa pravom Republike Srbije. Za sve sporove koji proizlaze iz korišćenja sajta nadležan je sud u Beogradu, Srbija, osim ako imperativne norme zaštite potrošača u vašoj državi prebivališta ne propisuju drugačije.',
        'en': 'These terms are interpreted under the law of the Republic of Serbia. Any disputes arising from use of the site fall under the jurisdiction of the court in Belgrade, Serbia, unless mandatory consumer-protection rules in your country of residence require otherwise.',
        'ru': 'Эти условия толкуются в соответствии с правом Республики Сербия. Все споры, возникающие в связи с использованием сайта, подсудны суду в Белграде, Сербия, если иное не предусмотрено императивными нормами защиты прав потребителей страны вашего проживания.',
    },
    'tos.s8_h': {
        'sr': '8. Izmene uslova',
        'en': '8. Changes to these terms',
        'ru': '8. Изменения условий',
    },
    'tos.s8_body': {
        'sr': 'Možemo povremeno da ažuriramo ove uslove. Svaka nova verzija se objavljuje na ovoj stranici sa datumom izmene. Ako izmena bitno utiče na vaša prava, objavljujemo baner na početnoj strani najmanje 14 dana unapred. Nastavkom korišćenja sajta nakon objave prihvatate izmenjene uslove.',
        'en': 'We may update these terms from time to time. Each new version is published on this page with a change date. If a change materially affects your rights, we publish a homepage banner at least 14 days in advance. Continued use of the site after publication constitutes acceptance of the updated terms.',
        'ru': 'Мы можем периодически обновлять эти условия. Каждая новая версия публикуется на этой странице с датой изменения. Если изменение существенно затрагивает ваши права, мы вывешиваем баннер на главной странице минимум за 14 дней. Продолжение использования сайта после публикации означает принятие обновлённых условий.',
    },

    'home.quick_label': {'sr': 'Popularno:', 'en': 'Popular:', 'ru': 'Популярно:'},
    'home.quick_links_aria': {'sr': 'Popularni maršruti', 'en': 'Popular routes', 'ru': 'Популярные маршруты'},

    'home.feat_map_label': {'sr': 'Interaktivna karta', 'en': 'Interactive map', 'ru': 'Интерактивная карта'},
    'home.feat_map_sub': {'sr': 'stajališta · vreme dolaska', 'en': 'stops · arrival times', 'ru': 'остановок · время прибытия'},
    'home.feat_region_label': {'sr': 'Srbija i region', 'en': 'Serbia & region', 'ru': 'Сербия и регион'},
    'home.feat_region_desc': {'sr': 'Crna Gora, BiH, Hrvatska i još', 'en': 'Montenegro, BiH, Croatia & more', 'ru': 'Черногория, БиГ, Хорватия и ещё'},
    'home.feat_schedule_label': {'sr': 'Aktuelni polasci', 'en': 'Live schedules', 'ru': 'Актуальные отправления'},
    'home.feat_schedule_sub': {'sr': 'ruta · gradskih linija', 'en': 'routes · city lines', 'ru': 'маршрутов · линий'},

    'seasonal.tip_heading': {'sr': 'Planirate posetu?', 'en': 'Planning a visit?', 'ru': 'Планируете поездку?'},
    'seasonal.tip_route': {
        'sr': 'Rezervišite smeštaj u {to_city} na vreme — leto je sezona najveće potražnje.',
        'en': 'Book accommodation in {to_city} early — summer is peak season.',
        'ru': 'Забронируйте жильё в {to_city} заранее — летом высокий сезон.',
    },

    'city.loading': {'sr': 'Podaci se učitavaju...', 'en': 'Loading data...', 'ru': 'Загрузка...'},
    'line.no_stops': {'sr': 'Nema podataka o stajalištima', 'en': 'No stop data available', 'ru': 'Нет данных об остановках'},
    'stop.no_lines': {'sr': 'Nema podataka o linijama', 'en': 'No line data available', 'ru': 'Нет данных о маршрутах'},
    'line.schedule_unavailable': {
        'sr': 'Tačan raspored trenutno nije dostupan. Proverite direktno kod prevoznika ili na autobuskoj stanici.',
        'en': 'Exact schedule is not currently available. Please check directly with the carrier or at the bus station.',
        'ru': 'Точное расписание временно недоступно. Уточните у перевозчика или на автовокзале.',
    },

    # ── Guide: Beograd–Novi Sad ──
    'guides.beograd_ns.title': {
        'sr': 'Autobus Beograd → Novi Sad {year} — Cene i Red Vožnje',
        'en': 'Bus Belgrade → Novi Sad {year} — Prices and Schedule',
        'ru': 'Автобус Белград → Нови-Сад {year} — Цены и Расписание',
    },
    'guides.beograd_ns.meta': {
        'sr': 'Sve o prevozu Beograd–Novi Sad: cene karata od 640 RSD, vreme putovanja 1–2h, poređenje autobusa i voza i aktuelni polasci.',
        'en': 'Everything about Belgrade–Novi Sad transport: ticket prices from 640 RSD, 1–2h travel time, bus vs train comparison and current departures.',
        'ru': 'Всё о транспорте Белград–Нови-Сад: билеты от 640 динаров, время в пути 1–2ч, сравнение автобуса и поезда, актуальные рейсы.',
    },
    'guides.beograd_ns.p1': {
        'sr': 'Beograd i Novi Sad razdvaja svega 90 km auto-putom, a taj rastojanje možete prevaliti autobusom, vozom ili privatnim prevozom. '
              'Ovo je najpopularnija domaća linija — dnevno saobraća više od 30 polazaka, a cene su pristupačne za svaki budžet.',
        'en': 'Belgrade and Novi Sad are only 90 km apart by motorway, and you can cover that distance by bus, train or private transport. '
              'This is the most popular domestic route — over 30 departures run daily at prices to suit every budget.',
        'ru': 'Белград и Нови-Сад разделяют всего 90 км по автостраде. Добраться можно автобусом, поездом или на машине. '
              'Это самый популярный внутренний маршрут: более 30 рейсов в день по доступным ценам.',
    },
    'guides.beograd_ns.h2_options': {
        'sr': 'Opcije prevoza',
        'en': 'Transport options',
        'ru': 'Варианты транспорта',
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
    },
    'guides.beograd_ns.h2_price': {
        'sr': 'Cene karata',
        'en': 'Ticket prices',
        'ru': 'Цены на билеты',
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
    },
    'guides.beograd_ns.h2_tips': {
        'sr': 'Korisni saveti',
        'en': 'Useful tips',
        'ru': 'Полезные советы',
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
    },
    'guides.beograd_ns.h2_departures': {
        'sr': 'Aktuelni polasci',
        'en': 'Current departures',
        'ru': 'Актуальные рейсы',
    },
    'guides.beograd_ns.cta': {
        'sr': 'Pogledaj sve polaske',
        'en': 'View all departures',
        'ru': 'Смотреть все рейсы',
    },

    # ── Guide: Prevoz do mora ──
    'guides.more.title': {
        'sr': 'Prevoz do mora iz Srbije {year} — Autobus, Cene, Saveti',
        'en': 'Transport to the Sea from Serbia {year} — Bus, Prices, Tips',
        'ru': 'Транспорт к морю из Сербии {year} — Автобус, Цены, Советы',
    },
    'guides.more.meta': {
        'sr': 'Kako doći do mora iz Beograda autobusom: Budva, Bar, Herceg Novi, Split, Dubrovnik — cene, vreme putovanja i letnji saveti.',
        'en': 'How to get to the sea from Belgrade by bus: Budva, Bar, Herceg Novi, Split, Dubrovnik — prices, travel times and summer tips.',
        'ru': 'Как добраться до моря из Белграда автобусом: Будва, Бар, Херцег-Нови, Сплит, Дубровник — цены, время в пути и советы на лето.',
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
    },
    'guides.more.h2_destinations': {
        'sr': 'Najpopularnije destinacije i cene',
        'en': 'Most popular destinations and prices',
        'ru': 'Самые популярные направления и цены',
    },
    'guides.more.p2': {
        'sr': 'Iz Beograda saobraćaju direktne linije do svih glavnih primorskih gradova. '
              'Cene su okvirne i mogu se razlikovati po prevozniku i sezoni:',
        'en': 'Direct lines from Belgrade run to all the main coastal towns. '
              'Prices are approximate and may vary by carrier and season:',
        'ru': 'Из Белграда ходят прямые рейсы во все основные прибрежные города. '
              'Цены приблизительные и могут варьироваться в зависимости от перевозчика и сезона:',
    },
    'guides.more.h2_tips': {
        'sr': 'Saveti za letnje putovanje',
        'en': 'Summer travel tips',
        'ru': 'Советы для летних поездок',
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
    },
    'guides.more.h2_routes': {
        'sr': 'Aktuelne linije do mora',
        'en': 'Current sea routes',
        'ru': 'Актуальные маршруты к морю',
    },
    'guides.more.cta': {
        'sr': 'Pretraži karte za more',
        'en': 'Search sea tickets',
        'ru': 'Найти билеты к морю',
    },

    # ── Guide: FlixBus Srbija ──
    'guides.flixbus.title': {
        'sr': 'FlixBus Srbija {year} — Linije, Cene i Poređenje',
        'en': 'FlixBus Serbia {year} — Routes, Prices and Comparison',
        'ru': 'FlixBus Сербия {year} — Маршруты, Цены и Сравнение',
    },
    'guides.flixbus.meta': {
        'sr': 'FlixBus linije kroz Srbiju, poređenje sa Lastom i BEX-om — kad je FlixBus jeftiniji i kad da birate domaći prevoz.',
        'en': 'FlixBus routes through Serbia, comparison with Lasta and BEX — when FlixBus is cheaper and when to choose a local carrier.',
        'ru': 'Маршруты FlixBus через Сербию, сравнение с Lasta и BEX — когда FlixBus дешевле и когда выбрать местного перевозчика.',
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
    },
    'guides.flixbus.h2_lines': {
        'sr': 'FlixBus linije koje prolaze kroz Srbiju',
        'en': 'FlixBus routes through Serbia',
        'ru': 'Маршруты FlixBus через Сербию',
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
    },
    'guides.flixbus.h2_compare': {
        'sr': 'FlixBus vs domaći prevoz — kad šta birati',
        'en': 'FlixBus vs local carriers — when to choose what',
        'ru': 'FlixBus vs местные перевозчики — когда что выбрать',
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
    },
    'guides.flixbus.h2_tips': {
        'sr': 'Saveti za putovanje FlixBusom',
        'en': 'Tips for travelling with FlixBus',
        'ru': 'Советы для поездок на FlixBus',
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
    },
    'guides.flixbus.cta': {
        'sr': 'Pretraži domaće polaske',
        'en': 'Search local departures',
        'ru': 'Найти внутренние рейсы',
    },
    # ── Operator/Country FAQ ──

}

SUPPORTED_LANGS = ('sr', 'en', 'ru')
DEFAULT_LANG = 'sr'


def get_text(key: str, lang: str = DEFAULT_LANG) -> str:
    """Get translated string. Falls back to Serbian, then to key itself."""
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get(DEFAULT_LANG) or key
