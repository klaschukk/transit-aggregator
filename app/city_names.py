"""City names as foreign searchers type them, for /en/, /ru/ and /bg/ pages.

The DB keeps Serbian Latin names ("Beograd", "Solun", "Minhen"). An English
searcher types "Belgrade to Budva bus", a Russian one "автобус Будва Котор",
so titles / H1 on those language versions use these names. Serbian pages are
untouched. Unknown slugs fall back to the DB name.

Table: slug | English (empty = same as the Serbian Latin name) | Russian | Bulgarian
"""
_TABLE = """
beograd|Belgrade|Белград|Белград
novi-sad||Нови-Сад|Нови Сад
nis||Ниш|Ниш
subotica||Суботица|Суботица
krusevac||Крушевац|Крушевац
jagodina||Ягодина|Ягодина
leskovac||Лесковац|Лесковац
vranje||Вране|Враня
bujanovac||Буяновац|Буяновац
vladicin-han||Владичин-Хан|Владичин хан
aleksinac||Алексинац|Алексинац
presevo||Прешево|Прешево
paracin||Парачин|Парачин
cuprija||Чуприя|Чуприя
velika-plana||Велика-Плана|Велика Плана
kragujevac||Крагуевац|Крагуевац
berlin||Берлин|Берлин
budva||Будва|Будва
sofija|Sofia|София|София
drezden|Dresden|Дрезден|Дрезден
kotor||Котор|Котор
podgorica||Подгорица|Подгорица
hamburg||Гамбург|Хамбург
bremen||Бремен|Бремен
herceg-novi||Херцег-Нови|Херцег Нови
memingen|Memmingen|Мемминген|Меминген
ulm||Ульм|Улм
rozenhajm|Rosenheim|Розенхайм|Розенхайм
svajnfurt|Schweinfurt|Швайнфурт|Швайнфурт
sarajevo||Сараево|Сараево
diseldorf|Düsseldorf|Дюссельдорф|Дюселдорф
hanover||Ганновер|Хановер
paderborn||Падерборн|Падерборн
fridrihshafen|Friedrichshafen|Фридрихсхафен|Фридрихсхафен
landsberg||Ландсберг|Ландсберг
minhen|Munich|Мюнхен|Мюнхен
stutgart|Stuttgart|Штутгарт|Щутгарт
augsburg||Аугсбург|Аугсбург
esen|Essen|Эссен|Есен
frankfurt||Франкфурт|Франкфурт
vircburg|Würzburg|Вюрцбург|Вюрцбург
bamberg||Бамберг|Бамберг
nirnberg|Nuremberg|Нюрнберг|Нюрнберг
lindau||Линдау|Линдау
ravensburg||Равенсбург|Равенсбург
duizburg|Duisburg|Дуйсбург|Дуисбург
keln|Cologne|Кёльн|Кьолн
bilefeld|Bielefeld|Билефельд|Билефелд
kasel|Kassel|Кассель|Касел
fulda||Фульда|Фулда
regensburg||Регенсбург|Регенсбург
mostar||Мостар|Мостар
banja-luka||Баня-Лука|Баня Лука
solun|Thessaloniki|Салоники|Солун
split||Сплит|Сплит
kraljevo||Кралево|Кралево
atina|Athens|Афины|Атина
rijeka||Риека|Риека
tirana||Тирана|Тирана
cacak||Чачак|Чачак
plovdiv||Пловдив|Пловдив
manhajm|Mannheim|Мангейм|Манхайм
uzice||Ужице|Ужице
tuzla||Тузла|Тузла
zagreb||Загреб|Загреб
indija||Инджия|Инджия
ohrid||Охрид|Охрид
dubrovnik||Дубровник|Дубровник
novi-pazar||Нови-Пазар|Нови Пазар
bar||Бар|Бар
stara-pazova||Стара-Пазова|Стара Пазова
niksic||Никшич|Никшич
varna||Варна|Варна
skoplje|Skopje|Скопье|Скопие
tivat||Тиват|Тиват
pirot||Пирот|Пирот
valjevo||Валево|Валево
budimpesta|Budapest|Будапешт|Будапеща
senta||Сента|Сента
sombor||Сомбор|Сомбор
kanjiza||Канижа|Канижа
zenica||Зеница|Зеница
sabac||Шабац|Шабац
drac|Durrës|Дуррес|Дуръс
kikinda||Кикинда|Кикинда
smederevo||Смедерево|Смедерево
zrenjanin||Зренянин|Зренянин
ada||Ада|Ада
priboj||Прибой|Прибой
bor||Бор|Бор
zajecar||Зайечар|Зайчар
varvarin||Варварин|Варварин
loznica||Лозница|Лозница
pula||Пула|Пула
trebinje||Требине|Требине
mladenovac||Младеновац|Младеновац
pozarevac||Пожаревац|Пожаревац
negotin||Неготин|Неготин
pancevo||Панчево|Панчево
ruma||Рума|Рума
arandelovac||Аранджеловац|Аранджеловац
gornji-milanovac||Горни-Милановац|Горни Милановац
backa-palanka||Бачка-Паланка|Бачка Паланка
becej||Бечей|Бечей
burgas||Бургас|Бургас
temerin||Темерин|Темерин
vrbas||Врбас|Врбас
zadar||Задар|Задар
smederevska-palanka||Смедеревска-Паланка|Смедеревска Паланка
istanbul||Стамбул|Истанбул
sremska-mitrovica||Сремска-Митровица|Сремска Митровица
bec|Vienna|Вена|Виена
ivanjica||Иваница|Иваница
apatin||Апатин|Апатин
prag|Prague|Прага|Прага
lazarevac||Лазаревац|Лазаревац
osijek||Осиек|Осиек
bitolj|Bitola|Битола|Битоля
tetovo||Тетово|Тетово
obrenovac||Обреновац|Обреновац
ljubljana||Любляна|Любляна
pleven||Плевен|Плевен
veliko-tarnovo||Велико-Тырново|Велико Търново
skadar|Shkodër|Шкодер|Шкодра
stip||Штип|Щип
blagoevgrad||Благоевград|Благоевград
stara-zagora||Стара-Загора|Стара Загора
ruse||Русе|Русе
sid||Шид|Шид
vrsac|Vršac|Вршац|Вършац
"""

_LANG_COL = {'en': 0, 'ru': 1, 'bg': 2}
NAMES: dict[str, tuple[str, str, str]] = {}
for _line in _TABLE.strip().splitlines():
    _slug, _en, _ru, _bg = _line.split('|')
    NAMES[_slug] = (_en, _ru, _bg)


def city_name(name: str, slug: str, lang: str) -> str:
    """`name` (DB, Serbian Latin) as searchers of `lang` write it."""
    col = _LANG_COL.get(lang)
    if col is None:
        return name
    return NAMES.get(slug, ('', '', ''))[col] or name
