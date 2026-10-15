"""Bibliographic normalization. Source filenames/IDs are preserved in the inventory.

Rules use filename credits, author collections, extracted text and curated corrections.
Unverified language/title/author inferences are explicitly recorded in each row's notes.
"""
import re,unicodedata,json,pathlib,collections
ROOT=pathlib.Path(__file__).resolve().parent
C={'A':'Arts & Culture','M':'Biography & Memoir','B':'Business & Economics','H':'History','L':'Language & Linguistics','F':'Literary Fiction','D':'Mystery & Thriller','P':'Philosophy','Y':'Psychology','R':'Religion','S':'Social Sciences','N':'Science','Q':'Science Fiction','I':'Historical Fiction','G':'Travel & Geography','U':'Unknown'}
def norm(s):
 s=unicodedata.normalize('NFKC',s).translate(str.maketrans('يكۀ','یکه')).replace('ـ','')
 return re.sub(r'\s+',' ',s).strip()
def key(s):return re.sub(r'[^\w\u0600-\u06ff]+','',norm(s).casefold()).replace('_','')
ALIASES={}
def register(canonical,*aliases):
 for a in (canonical,*aliases):ALIASES[key(a)]=canonical
AUTHOR_DATA='''Verne, Jules|JULES VERNE|ژول ورن
Dickens, Charles|CHARLS DICKENS|چارلز دیکنز|Charles Dickens
Aristotle|ARISTOTLE|ارسطو
Beckett, Samuel|SAMUEL BECKETT|ساموئل بکت
Sartre, Jean-Paul|JAN POL SARTER|سارتر|ژان پل سارتر
Shakespeare, William|WILLIAM SHAKESPEAR|شکسپیر|ویلیام شکسپیر
Rolland, Romain|ROMAIN ROLLAND|رومن رولان|رومان رولان
Tolstoy, Leo|LEO TOLSTOY|تولستوی|لئو تولستوی
Dostoevsky, Fyodor|FYODOR DOSTOYEVSKY|داستایوفسکی|داستایفسکی|fyodor dostoyevsky
Woolf, Virginia|VIRGINIA WOOLF|ویرجینیا ولف|ویرجینیا وولف
Tracy, Brian|BRIAN TRACY|برایان تریسی
Beauvoir, Simone de|SIMONE DE BEAUVOIR|سیمون دوبووار
García Márquez, Gabriel|GABRIEL GARCIA MARQUEZ|مارکز|گابریل گارسیا مارکز
Hugo, Victor|VICTOR HUGO|ویکتور هوگو
Kundera, Milan|MILAN KUNDERA|کوندرا|میلان کوندرا
Balzac, Honoré de|BALZAK|بالزاک|اونوره دو بالزاک
Ishiguro, Kazuo|ISHIGURO|ایشی گورو|کازوئو ایشی گورو
Dumas, Alexandre|ALEKSANDER DUMAS|الکساندر دوما
Chandler, Steve|STEVE CHANDLER|Steve Chandler
Proust, Marcel|MARCEL PROUST|مارسل پروست
Faulkner, William|WILLIAM FAULKNER|ویلیام فاکنر
Orwell, George|GEORGE ORWELL|جورج اورول
Brzezinski, Zbigniew|Zbigniew Brzezinski|Brzezinski
Brecht, Bertolt|BERESHT|برشت|برتولت برشت
Brontë, Emily|EMILEY BRONTE|Emily Bronte|امیلی برونته
Oates, Joyce Carol|Joyce Carol Oates
Gaarder, Jostein|JOSTEIN GAARDER|Jostein Gaarder
Steinbeck, John|JOHN STEINBECK|جان اشتاین بک
Murakami, Haruki|HARUKI MURAKAMI|هاروکی موراکامی
Gide, André|GIDE, ANDRE|آندره ژید
Sharp, Gene|GENE SHARP|جین شارپ
Robbins, Anthony|ANTHONY ROBBINS|Anthony Robbins|آنتونی رابینز
Kierkegaard, Søren|SOREN KIERKEGAARD|سورن کیرکگور
Bach, Richard|RICHARD BACH|ریچارد باخ
Gorky, Maxim|MAXIM GORKY|ماکسیم گورکی
Kazantzakis, Nikos|KAZANTAZAKIS, NIKOS|نیکوس کازانتزاکیس
Saramago, José|JOSE SARAMAGO|ژوزه ساراماگو
Zola, Émile|EMILE ZOLA|امیل زولا
Saint-Exupéry, Antoine de|EXUPERY|Antoine de Saint Exupery|Saint Exupery, Antoine de
Fallaci, Oriana|FALLACI|فالاچی|اوریانا فالاچی
Grass, Günter|GUNTER GRASS|گونترگراس|گونتر گراس
Gary, Romain|ROMAIN GRAY|رومن گاری|رومان گاری
Coelho, Paulo|PAULO COELHO|Coelho|coelhopaulo|coelho paulo|پائولو کوئیلو
Chomsky, Noam|NOAM CHAMESKY|نوام چامسکی
Salinger, J. D.|J. D. SALINGER|سلینجر|سالینجر
Nietzsche, Friedrich|Friedrich Wilhelm Nietzsche|فردریش نیچه
Kafka, Franz|FRANZ KAFKA|کافکا|فرانتس کافکا
Borges, Jorge Luis|BORGES|بورخس|خورخه لوئیس بورخس
Hemingway, Ernest|ERNEST HEMINGWAY|همینگوی|ارنست همینگوی|ErnestHemingvey
Russell, Bertrand|BERTRAND RUSSELL|راسل|برتراند راسل
Chekhov, Anton|ANTON CHEKHOV|Anton Chekhov|چخوف
Camus, Albert|ALBERT CAMUS|کامو|آلبر کامو
Bazin, André|آندره بازن
Bickel, Margot|مارگوت بیکل
Lorca, Federico García|فدریکو گارسیا لورکا
Renou, Louis|لوئی رنو
Basu, Romen|رومن باسو
Kracauer, Siegfried|زیگفرید کراکائر
Dawkins, Richard|ریچارد داوکینز
Robinson, Neal|Neal Robinson
De Angelis, Barbara|باربارا دی آنجلیس
Covey, Stephen R.|Stephen R. Covey
Gray, John|جان گری
Carnegie, Dale|دیل کارنگی
Maurois, André|آندره موروآ
Harvey, Steve|استیو هاروی
Crement, Xavier|خاویر کرمنت
Johnson, Spencer|اسپنسور جانستون|Spencer Johnson|Spenser Johnson
Blanchard, Kenneth H.|Kenneth Blanchard
Appignanesi, Richard|ریچارد آپیگنانسی
Acemoglu, Daron|دارون عجم اوغلو
Robinson, James A.|جیمز رابینسون
Jentleson, Bruce W.|Bruce W. Jentleson
Kuhn, Thomas S.|Thomas S. Kuhn
Bartlett, Bruce|Bruce Bartlett
Fouskas, Vassilis K.|Vassilis K. Fouskas
Delpech, Thérèse|Thérèse Delpech
Barrett, Roby C.|Roby C. Barrett
Kamrava, Mehran|MEHRAN KAMRAVA
Kissinger, Henry|Henry Kissinger
Wagner, Heather Lehr|HEATHER LEHR WAGNER
Jung, Dietrich|Dietrich Jung
Dueck, Colin|COLIN DUECK
Wroe, Andrew|Andrew Wroe
Halabi, Yakub|Yakub Halabi
Marx, Karl|کارل مارکس
Engels, Friedrich|فردریش انگلس
Guevara, Ernesto Che|چگوارا
Thoreau, Henry David|هنری دیوید ثرو
Fischer, Louis|لویی فیشر
Mernissi, Fatema|فاطمه مرنیسی
Lenin, Vladimir Ilyich|لنین
Trotsky, Leon|تروتسکی
Einstein, Albert|آلبرت اینشتین
Lessing, Doris|Doris Lessing|دوریس لسینگ
Bulgakov, Mikhail|میخائیل بولگاکف|بولگاکف
Shan, Darren|دارن شان
Mann, Thomas|توماس مان
Miller, Arthur|آرتور میلر
Nabokov, Vladimir|ولادمیر ناباکف
Mayakovsky, Vladimir|ولادمیر مایاکوفسکی
Azuela, Mariano|ماریانو آسوئلا
Vonnegut, Kurt|کورت ونه گات
Korolenko, Vladimir|کارلنکو
Sholokhov, Mikhail|شولوخوف
Merle, Robert|روبر مرل
Böll, Heinrich|بُل|هاینریش بل
Turgenev, Ivan|تورگنیف
Ionesco, Eugène|اوژن یونسکو
Greene, Graham|گراهام گرین
Melville, Herman|هرمان ملویل
Waltari, Mika|میکا والتاری
Brontë, Charlotte|شارلوت برونته
Fitzgerald, F. Scott|فیتس جرالد
Malraux, André|آندره مالرو
Lermontov, Mikhail|لرمانتف
Zévaco, Michel|میشل زواگو
Flaubert, Gustave|گوستاو فلوبر
Fuentes, Carlos|کارلوس فوئنتس|کارلوس فوئنتز
Schiller, Friedrich|شیلر
Sophocles|سوفوکلس
Eisenstein, Sergei|سرگئی میخایلوویچ ایزنشتاین
Poe, Edgar Allan|Edgar Allan Poe
Sebold, Alice|Alice Sebold
Asturias, Miguel Ángel|میگل آنخا استوریاس
Stevenson, Robert Louis|Robert Louis Stevenson
Hašek, Jaroslav|یاروسلاو هاشک
Bobin, Christian|کریستیان بوبن
Golding, William|ویلیام گلدینگ
Crichton, Michael|مایکل کرایتون
Roth, Philip|فیلیپ راث
Nesin, Aziz|عزیز نسین
Remarque, Erich Maria|رکوارک
Voynich, Ethel Lilian|لیلیان اتیل وینیچ
O. Henry|ا هنری
Hitler, Adolf|آدولف هیتلر
Twain, Mark|mark twain
Mitchell, Margaret|Margaret Mitchell
Montgomery, Lucy Maud|lucy maud montgomery
Hosseini, Khaled|Khaled Hosseini
Webster, Jean|Jean Webster
Andersen, Hans Christian|Hans Christian Anderson
Brown, Dan|Dan Brown|دن براون
Doyle, Arthur Conan|ARTHUR CONAN DOYLE
Frank, Christopher|کریستوفر فرانک
Potter, Beatrix|بئاتریکس پاتر
Levi, Primo|پریمو لوی
Blanchot, Maurice|موریس بلانشو
Akutagawa, Ryūnosuke|ریونوسوکه آکوتاگاوا
du Maurier, Daphne|دافنه دو موریه
Austen, Jane|جین آستین
Hrabal, Bohumil|بهومیل هرابال
Shaw, George Bernard|برنارد شاو
Silone, Ignazio|اینیا تسیو سیلونه
Strindberg, August|استریند برگ
Stendhal|استاندال
Schmitt, Éric-Emmanuel|اریک امانوئل اشمیت
Alcott, Louisa May|louisa may alcott
Carroll, Lewis|lewis carroll
Anderson, Sherwood|شرور اندرسون
Hesse, Hermann|هرمان هسه
Tagore, Rabindranath|تاگور
Joyce, James|James Joyce
Jackson, Shirley|شرلی جکسون
Borchert, Wolfgang|ولفگانگ بورشرت
Pirsig, Robert M.|رابرت پیرسیگ
Durant, Will|ویل دورانت
Kant, Immanuel|کانت
Rousseau, Jean-Jacques|ژان ژاک روسو
Maeterlinck, Maurice|موریس مترلینگ
Lessnoff, Michael H.|مایکل اچ لسناف
Ghazali, Abu Hamid|غزالی
Collin, Denis|دنیس کولن
Plato|افلاطون
Zweig, Stefan|اشتفان تسوایگ
Frost, S. E.|اس ای فراست
Kelley, David|دیوید کلی
Mandel, Ernest|ارنست مندل
Ryan, Robin|Robin Ryan
Leifman, Howard|Howard Leifman
Williams, Lynn|Lynn Williams
Marcus, John|John Marcus
Andrews, Brad|Brad Andrews
Devine, Felice Primeau|Felice Primeau Devine
Farr, Michael|Michael Farr
Kursmark, Louise M.|Louise M. Kursmark
Márquez, Gabriel García|گابریل گارسیا مارکز'''
for line in AUTHOR_DATA.splitlines():
 p=line.split('|');register(p[0],*p[1:])
# Keep one spelling for each Persian author across folders and filename variants.
for canonical,aliases in {
 'محمد مصدق':['مصدق'],'مرتضی مطهری':['مطهري'],'محمدحسین بهشتی':['بهشتي'],'ابوالحسن بنی صدر':['بنی صدر'],'حسینعلی منتظری':['منتظری'],
 'عبدالکریم سروش':['سروش'],'علی شریعتی':['شریعتی'],'مصطفی چمران':['چمران'],'سید محمدعلی جمالزاده':['جمال زاده','جمالزاده','محمد علی جمالزاده'],
 'بهرام بیضایی':['بهرام بیضائی'],'بهرام صادقی':['بهرام صادقي'],'عبدالحسین زرین کوب':['زرین کوب'],
 'محمود دولت آبادی':['دولت آبادی','دولت آیادی'],'احمد شاملو':['Shamlo','Shamloo','شاملو'],'غلامحسین ساعدی':['ساعدی'],
 'فروغ فرخزاد':['فروغ فرخ زاد'],'حافظ شیرازی':['حافظ'],'عمر خیام':['خیام'],'سعدی شیرازی':['سعدی'],
 'ابوالقاسم فردوسی':['فردوسی'],'جلال الدین محمد بلخی (مولانا)':['مولانا','مولوی'],'نظامی گنجوی':[],
 'محمدحسین شهریار':['شهریار'],'مهدی بازرگان':['بازرگان'],'همایون کاتوزیان':[],
 'یرواند آبراهامیان':['یرواند ابراهامیان','یروان آبراهامیان'],'محمدرضا شفیعی کدکنی':['شفیعی کدکنی'],
 'محمدتقی بهار':['ملک الشعرای بهار'],'نیما یوشیج':[],'محمدعلی سپانلو':['سپانلو'],'علی اکبر سعیدی سیرجانی':['سعیدی سیرجانی'],
 'علی مراد فدایی نیا':['علی مراد فدایی نیا'],'پیمان هوشمندزاده':['پیمان هوشمند زاده'],'مصطفی رضیئی':[],
 'علی رضا نوری زاده':['علی رضا نوری زاده'],'حسین بشیریه':['حسین بشریه'],'داریوش شایگان':['داریوش شایگاه'],
 'عطاءالله مهاجرانی':['مهاجرانی'],'ابوالقاسم فنایی':['ابولقاسم فنایی'],'هوشنگ مرادی کرمانی':['مرادی کرمانی'],
 'محمد مؤدب پور':['م مودب پور'],'شاهرخ مسکوب':[],'احمد گلشیری':[],'احمد محمود':[],'نادر ابراهیمی':[],
 'ابراهیم گلستان':[],'صادق هدایت':[],'صادق چوبک':[],'سیمین دانشور':[],'هوشنگ گلشیری':[],
}.items():register(canonical,*aliases)
def author_name(s):return ALIASES.get(key(s),norm(s))
for f in json.loads((ROOT/'vault_inventory.json').read_text(encoding='utf-8'))['files']:
 top=f['folder'].split('/')[0]
 if top not in ['0-OTHERS','_ NEEDED SOFTWARES']:register(author_name(top),top)

OVERRIDES={}
def put(indices,**values):
 for i in indices if isinstance(indices,list) else [indices]:OVERRIDES.setdefault(i,{}).update(values)
# Per-file corrections: author versus subject/translator, misleading folders, clean titles.
for indices,a in [([41,682],'همایون کاتوزیان'),([42,43],'غلامرضا نجاتی'),(377,'Unknown'),(421,'Lorca, Federico García'),(425,'Bickel, Margot'),(426,'آزاده فراهانی; رسول عبدالمحمدی'),(428,'اشرف دهقانی'),(437,'Various authors'),(442,'Unknown'),([460,1237],'محمدرضا نیکفر'),(461,'مصطفی حسینی طباطبایی'),([472,489,494,495,517,551,552,739,779],'Unknown'),(502,'عبدالکریم سروش'),(528,'رضا علیجانی'),(634,'حنا مخملباف'),([719,1367],'Shaw, George Bernard'),([771,1060],'Camus, Albert'),(778,'سیمین دانشور'),(829,'Gibran, Kahlil'),(869,'داریوش آشوری'),(880,'نیما یوشیج'),([911,914],'پروین دولت آبادی'),([912,913],'ابوالمعالی نصرالله منشی'),(910,'محمود شبستری'),(915,'نیما یوشیج'),(916,'عبید زاکانی'),(917,'خواجه عبدالله انصاری'),(918,'ایرج میرزا'),(919,'ناصرخسرو'),(920,'عبید زاکانی'),([907,921],'پروین اعتصامی'),(922,'ابوسعید ابوالخیر'),(923,'محمدحسین شهریار'),([924,925],'فریدالدین عطار'),([926,927,931],'Unknown'),([932,933,934],'Unknown'),([940,941],'De Angelis, Barbara'),(942,'Covey, Stephen R.'),([943,949],'Gray, John'),(946,'Unknown'),(948,'Tracy, Brian'),(950,'Harvey, Steve'),(951,'Unknown'),(953,'حسن نراقی'),(954,'Johnson, Spencer'),(955,'Blanchard, Kenneth H.; Johnson, Spencer'),(956,'Appignanesi, Richard; Garratt, Chris'),(968,'Borges, Jorge Luis; Jurado, Alicia'),(1063,"O’Brien, Conor Cruise"),(1107,'Saint-Exupéry, Antoine de'),(1145,'Acemoglu, Daron; Robinson, James A.'),([1151,1152,1153],'میرحسین موسوی'),(1158,'Unknown'),(1160,'Unknown'),(1181,'Marx, Karl; Engels, Friedrich'),(1187,'محسن هاشمی; حبیب الله حمیدی'),(1188,'Popović, Srđa; Milivojević, Andrej; Đinović, Slobodan'),(1189,'Marx, Karl; Engels, Friedrich'),(1191,'Lindgren, Stefan'),([1192,1431],'Unknown'),(1200,'Unknown'),([1205,1206],'Unknown'),([1208,1209,1210,1211],'اکبر هاشمی رفسنجانی'),(1212,'Unknown'),(1213,'Unknown'),(1215,'British Legation, Tehran'),(1216,'Rushdie, Salman'),(1218,'Unknown'),(1220,'Unknown'),(1221,'Einstein, Albert'),(1222,'Unknown'),(1223,'Unknown'),(1224,'داریوش آشوری; علی اصغر سیدآبادی'),([1225,1226],'علی میرفطروس'),(1228,'جمهوری اسلامی ایران'),(1229,'Unknown'),(1230,'یدالله موقن'),(1231,'مرکز مطالعات دفاع استراتژیک بی خشونت'),(1232,'Unknown'),([1233,1234],'Lenin, Vladimir Ilyich'),(1235,'Lamb, David'),(1236,'محمد خاتمی'),([1238,1239,1240,1244,1245,1248,1249],'Trotsky, Leon'),(1241,'Unknown'),(1246,'میرحسین موسوی'),(1247,'Unknown'),(1250,'Unknown'),(1251,'Unknown'),(1274,'Unknown'),(1276,'Unknown'),(1287,'آمین اشکور'),(1306,'Unknown'),(1319,'Various authors'),(1324,'Various authors'),(1332,'محمدعلی نقیب الممالک'),([1342,1377],'Andersen, Hans Christian'),(1345,'Various authors'),(1348,'Potter, Beatrix'),([1363,1364],'Various authors'),(1369,'Unknown'),(1378,'Various authors'),(1379,'Hergé'),(1383,'م. میرابوطالبی'),(1384,'فریدون تنکابنی'),(1385,'قاضی ربیحاوی'),([1386,1387,1390],'Unknown'),(1395,'گلی ترقی'),(1397,'Unknown'),(1398,'Dawkins, Richard'),(1399,'Hawthorne, Nathaniel'),(1400,'کورش اسدی'),([1401,1402,1403,1404,1406,1409,1412,1413],'Unknown'),([1405,1410,1414],'Joyce, James'),(1407,'Jackson, Shirley'),(1408,'Bradbury, Ray'),(1411,'Borchert, Wolfgang'),(1415,'Blanchot, Maurice'),(1416,'Pirsig, Robert M.'),([1428,1429],'Marx, Karl; Engels, Friedrich'),(1432,'Unknown'),(1451,'Lenin, Vladimir Ilyich'),(1452,'Unknown'),(1453,'Unknown'),(1454,'Lenin, Vladimir Ilyich'),(1458,'Unknown'),(1459,'Unknown'),(1460,'Unknown'),(1461,'Unknown'),(1462,'Unknown'),(1463,'FIDE'),(1464,'Unknown'),(1514,'Unknown'),(1515,'Piotrowski, William J.'), (1516,'Enelow, Wendy S.; Kursmark, Louise M.'),(1517,'Fry, Ron'),(1519,'Leifman, Howard; Muir, Marcy Lerner; Konrad, Ed'),(1523,'Unknown'),(1525,'Farr, Michael; Kursmark, Louise M.'),(1526,'Unknown'),(1527,'Unknown'),(1528,'Unknown'),(1529,'Unknown'),(1530,'Unknown'),(1531,'Unknown'),(1532,'Unknown')]:put(indices,author=a)
register('Gibran, Kahlil','جبران خلیل جبران')
put([1238,1239,1240,1244,1248],author='Unknown',note='Article discusses these thinkers; their names in the title do not establish authorship.')
put(1241,author='عبدالله شهبازی')
put(1247,author='علی خامنه ای',note='Collection of statements on the Islamic Republic system, published by the Centre for Islamic Political Studies.')
put(1250,author='عبدالله نوری',title='دفاعیه عبدالله نوری از آیت الله منتظری در دادگاه ویژه روحانیت')
put(1251,author='علی میرفطروس')
put(1385,title='حفره')
# Unverified attributions remain Unknown rather than copying a biography's subject.
put(377,note='Filename attributes this biography to Romain Gary; attribution conflicts with the well-known Romain Rolland biography and needs title-page verification.')
put(634,note='Interview with Hana Makhmalbaf; interviewer not identified in extracted opening.')
put(739,author='Various authors',note='Special issue about Bozorg Alavi; contains multiple contributors, not a sole-authored Alavi work.')
put(829,note='Kahlil Gibran letters, selected/adapted by Paulo Coelho; translator Arash Hejazi. Coelho is not the original letter writer.')
put(442,note='Traditional biblical Song of Songs, Persian recreation by Ahmad Shamlou; original authorship not asserted.')
put([926,927,931],note='Quran; Persian translation credited to Taheri Qazvini. Translator is not treated as author.',language='Arabic; Persian')
put([933,934],note='Avesta; traditional sacred text. Translator/editor requires title-page verification.',language='Unknown')
put(932,note='Article about the Avesta; authorship unverified.')
put(923,language='Azerbaijani',language_verified=True,note='Azerbaijani poem confirmed in the extracted text; Persian introductory material is present.')
put(106,language='Romanian',language_verified=True,title='Succesul în viață')
put(804,language='Italian',note='Italian language indicated by filename MaktubItaliano; raw RTF text not readable via Drive.')
put(1125,language='English',language_verified=True,title='Rubaiyat of Omar Khayyam',note='English verse rendering by Edward FitzGerald, confirmed on title page.')
put(1130,language='English',language_verified=True,title='The Epic of Kings; or, Shahname',note='English translation by Helen Zimmern, confirmed on title page.')
put([104,118],author='Tracy, Brian; Arden, Ron')

TITLE_DATA='''101|TurboCoach: A Powerful System for Achieving Breakthrough Career Success|Tracy, Brian; Campbell, Campbell Fraser
102|Time Power: A Proven System for Getting More Done in Less Time Than You Ever Thought Possible
103|Time Power: A Proven System for Getting More Done in Less Time Than You Ever Thought Possible
104|The Power of Charm: How to Win Anyone Over in Any Situation
105|The 21 Success Secrets of Self-Made Millionaires
107|Speak to Win: How to Present with Power in Any Situation
108|Reinvention: How to Make the Rest of Your Life the Best of Your Life
109|Million Dollar Habits
110|Many Miles to Go
111|Goals!
112|Getting Rich Your Own Way
113|Focal Point: A Proven System to Simplify Your Life, Double Your Productivity, and Achieve All Your Goals
114|Focal Point: A Proven System to Simplify Your Life, Double Your Productivity, and Achieve All Your Goals
115|Flight Plan: The Real Secret of Success
116|Change Your Thinking, Change Your Life
149|Testaments Betrayed: An Essay in Nine Parts
157|The Farewell Waltz
163|The Curtain
171|کتاب خنده و فراموشی
274|Broke Heart Blues
284|خوشه های خشم — جلد 1
335|The Little Prince
421|یرما
422|وحدت آری؛ اما دروغ گفتن برای وحدت خیر!
423|برنامه طلوع خورشید لغو شده است!
424|ترانه های کوچک غربت
425|سکوت سرشار از ناگفته هاست
426|درآمدی بر شیوه نوشتاری اشعار شاملو
427|شکفتن در مه
428|شاملو در شط جاری تاریخ
429|چراغم در این خانه می سوزد
430|تکه هایی از روزنامه سفر میمنت اثر به ایالات متفرقه آمریکا
431|پریا
432|نگرانی های یک شاعر
433|نامه ای از احمد شاملو
434|مدایح بی صله
435|لحظه ها و همیشه
436|کاشفان فروتن شوکران
437|ژرف تر از اقیانوس: شعر جهان در ترجمه شاملو
438|هنر و سیاست
439|حدیث بی قراری ماهان
440|گزارش اهل قلم
441|ققنوس در باران
442|غزل غزل های سلیمان
443|قطعنامه
444|ابراهیم در آتش
445|دشنه در دیس
446|در انتهای اندوه دریچه روشنی گشوده است
447|در آستانه
448|آیدا در آینه
449|آهن ها و احساس
450|آهنگ های فراموش شده
451|۲۳
452|۱۸۷ شمع روشن
551|معرفی صادق هدایت و آثارش
612|سگ ولگرد
622|اولدوز
624|تلخون
625|ماهی سیاه کوچولو
694|جوان مرگی در نثر معاصر فارسی
735|هویت، کیهان، سعید امامی
802|Manual of the Warrior of Light
803|Stories for Parents
804|Maktub
805|Veronika Decides to Die
806|Maktub
807|Eleven Minutes
808|The Zahir
809|The Witch of Portobello
810|The Valkyries
811|The Devil and Miss Prym
812|The Alchemist
813|By the River Piedra I Sat Down and Wept
823|کیمیاگر
858|Hapworth 16, 1924
1003|زندگی خوش و کوتاه فرانسیس مکومبر
1004|تپه هایی چون فیل های سفید
1005|ده نفر سرخپوست
1006|اردوگاه سرخپوستان
1007|مشت زن حرفه ای
1008|جایی دنج و روشن
1009|تپه هایی همچون فیل های سفید
1010|گربه زیر باران
1011|پیرمرد و دریا
1125|Rubaiyat of Omar Khayyam
1130|The Epic of Kings; or, Shahname
1150|ابتذال مرجعیت شیعه
1151|صدای مردم — فصل یکم
1152|صدای مردم — فصل یکم
1153|صدای مردم — فصل یکم
1160|فتحعلی شاه قاجار
1163|The Structure of Scientific Revolutions
1188|مبارزه خشونت پرهیز: ۵۰ نکته اساسی
1216|آیات شیطانی
1222|زبان قرآن؟ مخاطبان قرآن؟ پاسخ به اولین نقد عطاءالله مهاجرانی
1223|هدی صابر: یادنامه
1224|مدرنیته را در بشقاب به کسی تعارف نمی کنند
1225|مدرنیته: بایست ها و بن بست های پیدایش آن در ایران — بخش دوم
1226|مدرنیته: بایست ها و بن بست های پیدایش آن در ایران — بخش اول
1235|سوسیالیسم لیبرتاریایی
1337|Gone with the Wind
1342|Hans Christian Andersen — selected works
1377|Hans Christian Andersen — selected works
1379|The Adventures of Tintin: Flight 714 to Sydney
1397|زباله
1398|ویروس های ذهن
1399|ویکفیلد
1400|سان شاین
1401|سیاه مست
1402|شکوه قانون
1403|پرواز
1404|پاهای کثیف
1405|اولیس
1406|عقده ادیپ من
1407|قرعه کشی
1408|لبخند
1409|فاجعه معدن
1410|گل
1411|داستانی از ولفگانگ بورشرت
1412|برخورد
1413|اولین اشتباه
1414|عربی
1415|آن دم مرگم
1416|Zen and the Art of Motorcycle Maintenance
1423|قرائت دینی
1515|Fearless Interviewing: How to Win the Job by Communicating with Confidence
1516|Cover Letter Magic: Trade Secrets of Professional Résumé Writers
1517|101 Great Résumés
1518|Winning Cover Letters
1519|Vault Guide to Résumés, Cover Letters & Interviews
1520|Ultimate Job Search
1521|The Résumé Makeover: 50 Common Problems with Résumés and Cover Letters — and How to Solve Them
1522|How to Land a Top-Paying Purchasing Job
1524|Goof-Proof Résumés & Cover Letters
1525|15-Minute Cover Letter'''
for line in TITLE_DATA.splitlines():
 p=line.split('|');put(int(p[0]),title=p[1]);
 if len(p)>2:put(int(p[0]),author=p[2])

# Categories match the original Bookshelf vocabulary, with specific subjects where useful.
for ids,cat,sub,kind in [
 ([20,315,864,865,866,867,868,869,1012,1013,1014,1015,1016,1017,1018,1019,1020,1021,1022],'P','General philosophy','Nonfiction'),
 ([1019,1020,1417,1437,1450],'P','History of philosophy','Nonfiction'),
 ([31,60,164,167,199,201,319,426,694,1103,905,1284,1285,1306],'A','Literary criticism','Nonfiction'),
 ([21,22,24,26,29,34,35,36,37,38,39,242,243,246,247,308,309,421,577,583,587,635,636,637,719,897,898,1027,1028,1038,1039,1058,1257,1278,1299,1302,1305,1359,1367,1370,1371],'A','Drama','Drama'),
 ([40,41,42,43,98,99,100,236,237,238,239,240,257,265,266,268,269,270,271,295,296,297,301,304,306,307,338,339,340,341,343,344,345,346,347,348,349,350,351,352,353,354,355,370,371,372,373,374,375,392,393,394,395,396,680,681,682,683,684,732,733,734,735,736,765,767,791,846,847,848,849,850,851,852],'S','Politics & society','Nonfiction'),
 ([44,268,271,301,305,120,121,122,123,740,743,747,1159,1207,1208,1209,1210,1211,1214],'M','Political memoir','Nonfiction'),
 ([49,50,51,52,377,951,1063,1191],'M','Biography','Nonfiction'),
 ([228,231,235,321,317,318,780,1300,1349],'M','Personal memoir','Nonfiction'),
 ([997,656,769,919,1259,1314],'G','Travel writing','Nonfiction'),
 ([101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,195,196,197,298,299,300,942,948,954,955],'B','Personal development & leadership','Nonfiction'),
 ([261,262,263,264,258,259,302,303,356,357,359,360,361,362,363,364,365,366,367,368,369,399,398,400,456,457,458,459,460,461,464,465,468,470,471,472,473,474,477,478,482,483,484,490,491,492,493,496,497,498,499,500,501,502,503,504,505,506,507,508,509,510,511,512,513,514,515,516,517,518,519,520,521,522,523,524,525,526,527,528,529,530,531,532,533,754,755,756,757,758,759,760,761,762,763],'R','Islamic thought','Nonfiction'),
 ([265,266,937,1155,1160,1161,1168,1179,1208,1209,1210,1211,1213,1215,1218],'H','Iranian history','Nonfiction'),
 ([358,348,1195,1203,1231],'S','Gender & society','Nonfiction'),
 ([940,941,943,944,945,946,947,949,950,952],'Y','Relationships & personal development','Nonfiction'),
 ([953,1157,681,791],'S','Sociology','Nonfiction'),
 ([475,476,479,480,481,1163],'P','Philosophy of science','Nonfiction'),
 ([149,163,164,167,202,208,693,790,880,903,905,915,426,432,437,440,452],'A','Writing & literature','Nonfiction'),
 ([882,892,893,895,896,899,900,901,902,1303],'A','Film & cinema','Nonfiction'),
 ([891,894],'A','Literary history','Nonfiction'),
 ([883,884,885,886,887,888,889,890,739],'A','Literary periodicals','Reference'),
 ([926,927,931,930,935,936,1142,1143,1144],'R','Islam & Quran','Nonfiction'),
 ([932,933,934],'R','Zoroastrianism','Nonfiction'),
 ([929],'R','Religion & criticism','Nonfiction'),
 ([442],'R','Biblical literature','Poetry'),
 ([968],'R','Buddhism','Nonfiction'),
 ([53,54,55,56,57,58,59,65,68,182,183,184,185,146,147,148,1090,1091,1092,1093,1094,1095,1096,1097,1098,1099,1264,1265,1266,1267,1281,1295,1316,1337],'I','Historical novels','Fiction'),
 ([0,1,232,180,1331,1320],'Q','Speculative fiction','Fiction'),
 ([227,233],'Q','Dystopian fiction','Fiction'),
 ([79,93],'M','Prison writing','Nonfiction'),
 ([125,135],'H','Crime & political reporting','Nonfiction'),
 ([1315,971,335,333,334,1107,1348,1375,1376,1379,1338],'F','Children & young adult fiction','Fiction'),
 ([1254],'F','Young adult fiction','Fiction'),
 ([1078],'P','Existentialism','Nonfiction'),
 ([27,30,28,1055,1056,1060,1061,1062,1079,276,277,278,279,1416],'F','Philosophical fiction','Fiction'),
 ([1339,1340],'F','Family fiction','Fiction'),
 ([1279,1308,1343,1361,1362,1344],'D','Mystery & suspense','Fiction'),
 ([1420,1421],'L','General linguistics','Nonfiction'),
 ([1145,1180,1212,1219],'B','Economics','Nonfiction'),
 ([1462,1463],'A','Games & recreation','Reference'),
 ([1458,1526,1527,1528,1529,1530,1531,1532],'A','Drawing & visual arts','Nonfiction'),
 ([1459],'A','Writing & literature','Nonfiction'),
 ([1460],'A','Photography','Nonfiction'),
 ([1461],'A','Film & cinema','Nonfiction'),
 ([1514,1515,1516,1517,1518,1519,1520,1521,1522,1523,1524,1525],'B','Careers & job search','Reference'),
 ([1156,1176,1181,1183,1189,1202,1230,1233,1234,1235,1238,1244,1245,1248,1249,1424,1427,1428,1429,1430,1433,1444,1445,1451,1452,1454,1456],'P','Political philosophy','Nonfiction'),
 ([1418,1422,1423,1425,1434,1435,1436,1439],'R','Religion & philosophy','Nonfiction'),
 ([1426,1440,1441,1442,1443,1446,1447,1448,1449,1453],'P','General philosophy','Nonfiction'),
 ([1455,1457],'P','Logic & critical thinking','Nonfiction'),
 ([188,189,190,191,186,187],'H','Iranian political history','Nonfiction'),
 ([551,552,489,494,495,634,739,779,1223],'M','Biography','Nonfiction'),
 ([624,625,622,623,616,617,618,619,620,621],'F','Children & young adult fiction','Fiction'),
 ([829,433,741,745,746,666,667,668,671,1024,1025,1026],'M','Letters & correspondence','Nonfiction'),
 ([422,423,429,430,438,446],'A','Essays','Nonfiction'),
]:
 put(ids,category=C[cat],subcategory=sub,kind=kind)
for i in list(range(421,453))+[198,424,427,431,434,435,436,439,441,443,444,445,447,448,449,450,451,1100,1101,1102,1104,1105,1106,1108,1109,1110,1111,1120,1121,1122,1123,1124,1125,1126,1129,1130,1131,1132,1133,1134,1135,1136,1137,1138,1139,1140,1141]:
 if i not in OVERRIDES or 'category' not in OVERRIDES[i]:put(i,category=C['A'],subcategory='Poetry',kind='Poetry')
for i in [421]:put(i,category=C['A'],subcategory='Drama',kind='Drama')
for i in [425,437]:put(i,category=C['A'],subcategory='Poetry in translation',kind='Poetry')
for i in [904,906,907,908,909,910,911,914,916,918,921,922,923]:put(i,category=C['A'],subcategory='Poetry',kind='Poetry')
put([912,913],category=C['F'],subcategory='Fables',kind='Fiction')
put([917,924,925],category=C['R'],subcategory='Sufism & mysticism',kind='Nonfiction')
put(880,note='Diaries by Nima Yushij; Sharaġim Yushij is the editor/compiler, not the diary author.',category=C['M'],subcategory='Diaries',kind='Nonfiction')
put(903,category=C['M'],subcategory='Diaries',kind='Nonfiction')

def read_evidence():
 e={}
 if (ROOT/'metadata_evidence.json').exists():e.update(json.loads((ROOT/'metadata_evidence.json').read_text(encoding='utf-8')))
 for path in sorted(ROOT.glob('text_evidence*.json')):
  for k,v in json.loads(path.read_text(encoding='utf-8')).items():
   if v is None:continue
   id=v.get('id',k)
   if not v.get('text') and e.get(id,{}).get('text'):continue
   e[id]=v
 return e
EVIDENCE=read_evidence()
def content_language(text):
 # Broken legacy font encodings and OCR soup must not be mistaken for English.
 t=text[:5000];letters=re.findall(r'[^\W\d_]',t,re.U);pers=len(re.findall(r'[\u0621-\u064a\u067e\u0686\u0698\u06af\u06a9\u06cc]',t))
 if sum(ord(c)<32 and c not in '\n\r\t' for c in t)>max(10,len(t)*.01):return None
 if pers>160 and pers/max(1,len(letters))>.55:return 'Persian'
 words=re.findall(r'[a-z]+',t.casefold());common=sum(w in {'the','and','of','to','in','is','a','that','it','for','with','was','you','this','by','from'} for w in words)
 if len(words)>120 and common/len(words)>.14:return 'English'
 return None

def enrich(i,f,row):
 if SOURCE_INDEX:i=SOURCE_INDEX.get(f['id'],-1)
 original=f['title'];folder=f['folder'];parts=folder.split('/');top=parts[0]
 notes=[];review=[];provenance={}
 # Strip actual file suffixes, not arbitrary dots inside titles.
 title=re.sub(r'\.(pdf|djvu|epub|docx?|rtf|mht|html?|rar|zip|mp3)$','',original,flags=re.I)
 title=norm(title.replace('%20',' '))
 copy_number=re.search(r'_(\d+)$',title)
 if copy_number:notes.append('Source numeric copy suffix: '+copy_number[0]+'.');title=title[:copy_number.start()]
 title=re.sub(r'\((?:www\.)?(?:BookFi\.org|omideiran\.net_www\.irebooks\.com)\)','',title,flags=re.I)
 title=title.replace('WwW.Clicker.Net.Tf','')
 # Extract author credit only when an explicit known name precedes or follows a delimiter.
 author=author_name(top) if top!='0-OTHERS' else 'Unknown';provenance['author']='source author collection' if author!='Unknown' else 'unresolved'
 if '/0-POEM/' in folder:author=author_name(parts[2]);provenance['author']='source poet collection'
 # Names in bibliographic brackets are credits, not part of the work title.
 brackets=re.search(r'\[([^]]+)\]',title)
 if brackets and re.search(r'[A-Za-z]',brackets[1]):
  credit=brackets[1].replace('_',' ');author='; '.join(author_name(x.strip()) for x in credit.split(',')) if ',' in credit else author_name(credit)
  title=title[:brackets.start()]+title[brackets.end():];provenance['author']='filename credit'
 segments=re.split(r'\s*[-_]\s*',title)
 if len(segments)>1:
  for pos in (0,-1):
   token=segments[pos]
   if key(token) in ALIASES:
    author=author_name(token);segments.pop(pos);title=' — '.join(segments);provenance['author']='explicit filename credit';break
  else:
   # Persian/English full-name prefixes in mixed collections. Avoid treating subtitles as names.
   first=segments[0].strip()
   if top=='0-OTHERS' and author=='Unknown' and 2<=len(first.split())<=7 and 4<len(first)<65 and not re.search(r'جلد|بخش|کتاب|قصه|قرآن|اوستا|قانون|داستان|خاطرات|دیوان|ترانه|سنت|صدای|مردان|سیستم|مانیفست|Coelho|Volume|The ',first,re.I):
    author=author_name(first);title=' — '.join(segments[1:]);provenance['author']='filename credit'
 title=re.sub(r'[_]+',' ',title)
 # Save layout/scan labels and translator credits as notes instead of title words.
 tr=re.search(r'(?:—|-)\s*ترجمه\s+([^—-]+)',title)
 if tr:notes.append('Translator credit in filename: '+tr[1].strip()+'.');title=title[:tr.start()]+title[tr.end():]
 labels=r'\s*(?:—|-)?\s*(OCR version|scanned version|single page format|single pages?|اسکن شده|تایپ شده|نسخه ی تایپ شده|بدون حاشیه ی سیاه|ORIGINAL VERSION|A5 VERSION)\s*'
 found=re.findall(labels,title,flags=re.I)
 if found:notes.append('Source version: '+', '.join(found)+'.');title=re.sub(labels,' ',title,flags=re.I)
 title=re.sub(r'\s*\(ترجمه[^)]*\)','',title)
 copy=re.search(r'\s*\((\d+)\)\s*$',title)
 if copy and 'مجله' not in title:notes.append('Source copy suffix: '+copy[0].strip()+'.');title=title[:copy.start()]
 title=re.sub(r'[_](\d+)$','',title)
 title=norm(title).strip(' —-_') or 'Unknown'
 fmt=pathlib.Path(original).suffix.upper().lstrip('.')
 if fmt not in {'PDF','DJVU','EPUB','DOC','DOCX','RTF','HTM','HTML','MHT','RAR','ZIP','MP3'}:
  fmt={'application/pdf':'PDF','text/html':'HTML','application/msword':'DOC'}.get(f.get('mime_type'),'Unknown')
 category=C['F'];sub='General fiction';kind='Fiction'
 if 'SHORT STORIES' in folder.upper() or '/short stories' in folder:sub='Short stories'
 if '/0-POEM' in folder or top=='احمد شاملو':category=C['A'];sub='Poetry';kind='Poetry'
 if top in ['ARISTOTLE','SOREN KIERKEGAARD','Friedrich Wilhelm Nietzsche','BERTRAND RUSSELL']:category=C['P'];sub='General philosophy';kind='Nonfiction'
 if top in ['BRIAN TRACY','STEVE CHANDLER','ANTHONY ROBBINS']:category=C['B'];sub='Personal development & leadership';kind='Nonfiction'
 if top in ['مصدق','ابراهیم یزدی','مهدی بازرگان','بنی صدر','Zbigniew Brzezinski','GENE SHARP','رضا علیجانی','اکبر گنجی','همایون کاتوزیان','NOAM CHAMESKY','نهضت آزادی']:category=C['S'];sub='Politics & society';kind='Nonfiction'
 if top in ['مطهري','محمد مجتهد شبستری','منتظری','سروش','شریعتی','شهاب الدین سهروردی','بهشتي','چمران']:category=C['R'];sub='Islamic thought';kind='Nonfiction'
 if 'PHILOSOPHY' in folder:category=C['P'];sub='General philosophy';kind='Nonfiction'
 if 'POLITICAL' in folder:category=C['S'];sub='Politics & society';kind='Nonfiction'
 if 'RELIGIOUS' in folder:category=C['R'];sub='Religion & philosophy';kind='Nonfiction'
 if 'LITERATURE & CINEMA' in folder:category=C['A'];sub='Film & cinema';kind='Nonfiction'
 if 'PSYCHOLOGY' in folder:category=C['Y'];sub='Personal development';kind='Nonfiction'
 if 'TRANING' in folder:category=C['A'];sub='Practical arts';kind='Nonfiction'
 if 'اشعار مشهور' in folder:title=re.sub(r'\.mht$','',title,flags=re.I);kind='Poetry';sub='Poetry';category=C['A']
 evidence=EVIDENCE.get(f['id'],{});text=evidence.get('text','');detected_language=content_language(text) or evidence.get('language');language=detected_language;language_method='extracted document text' if language else ''
 if not language:
  if re.search(r'[\u0600-\u06ff]',original):language='Persian';language_method='inferred from Persian title; document language not verified'
  elif '/IN PERSIAN' in folder:language='Persian';language_method='explicit language folder'
  elif '/IN ENGLISH' in folder:language='English';language_method='explicit language folder'
  elif re.search(r'[A-Za-z]',original) and not (top=='احمد شاملو' or (top=='ERNEST HEMINGWAY' and 'short stories' in folder) or original.lower().startswith(('rubiayat','shahnam')) or i in range(1397,1416)):
   language='English';language_method='inferred from English title; document language not verified'
  else:language='Unknown';review.append('Language needs verification')
 # Manuscript names are Persian transliterations, never assumed English.
 if i in range(421,453) or i in range(1003,1012) or i in range(1112,1120) or i in [622,624,625,1011] or i in range(1397,1416):
  if not detected_language:language='Persian';language_method='inferred from Persian transliteration/collection; document language not verified'
 o=OVERRIDES.get(i,{})
 title=o.get('title',title);author=o.get('author',author);category=o.get('category',category);sub=o.get('subcategory',sub);kind=o.get('kind',kind)
 if 'language' in o:language=o['language'];language_method='document text / title page' if o.get('language_verified') else 'curated source indication; see notes'
 if 'author' in o:provenance['author']='curated credit; see notes and source filename'
 if o.get('note'):notes.append(o['note'])
 if o.get('source_url'):notes.append('Bibliographic source: '+o['source_url'])
 if author=='Unknown':review.append('Author unresolved')
 if author=='Various authors':notes.append('Anthology or collective work; individual contributor list not established.')
 if author!= 'Unknown' and provenance.get('author')=='source author collection':notes.append('Author attributed from the author collection; no title-page authorship confirmation.')
 # Biographies, interviews and tributes must not inherit their subject as author.
 if re.search(r'ABOUT',folder) or i in [489,494,495,517,551,552,739,779,1223]:
  if i not in OVERRIDES or 'author' not in o:author='Unknown';review.append('Authorship of secondary material unresolved')
 # Override titles of romanized poetry fascicles and audio tracks.
 if 1112<=i<=1119:title='هوای تازه — دفتر '+str(1120-i)
 if fmt=='MP3':
  m=re.search(r'(\d+)\)?$',re.sub(r'\.mp3$','',original,flags=re.I));track=int(m[1]) if m else None
  title='The Little Prince'+(' — Track '+str(track) if track else '');author='Saint-Exupéry, Antoine de';kind='Audiobook';category=C['F'];sub='Children & young adult fiction';language='English';language_method='inferred from audiobook folder and track labels; audio not transcribed'
 if fmt in ['RAR','ZIP']:
  kind='Archive / Collection'
  if i!=149:review.append('Archive contents not inspected')
  else:notes.append('ZIP text/HTML contents inspected locally; English language established from contained book text.')
 title=norm(title);title=re.sub(r'\s*—\s*',' — ',title)
 series=o.get('series','Unknown')
 volume=re.search(r'(?:جلد|بخش|دفتر|کتاب)\s*([0-9۰-۹]+|اول|دوم|سوم|چهارم|پنجم|ششم|هفتم|هشتم|نهم|دهم)|\b(?:Volume|Vol\.?|Track)\s*(\d+)',title,re.I)
 if volume:series=title[:volume.start()].strip(' —-:')+'; '+volume[0]
 if series=='Unknown' and 'کلیدر' in folder:series='کلیدر'
 if i in [1143,1144]:title='شهید جاوید — فایل '+('2' if i==1143 else '1')
 # Requested catalog policy is distinct from evidence about the document language.
 content_language_method=language_method
 if detected_language or o.get('language_verified'):review=[r for r in review if r!='Language needs verification']
 persian_policy=bool(re.search(r'[\u0600-\u06ff]',original+' '+author))
 if persian_policy:
  confirmed=bool(detected_language or o.get('language_verified'))
  langs=[x.strip() for x in language.split(';') if x.strip()!='Unknown']
  if not confirmed and language_method.startswith('inferred'):langs=[]
  language='; '.join(dict.fromkeys(langs+['Persian']))
  notes.append('Persian language tag assigned by user rule: Persian-script filename or author name (including Iranian authors). This policy tag does not assert the language of the book text.')
  if not confirmed:
   language_method='user-requested Persian tagging rule; document language not independently confirmed'
  review=[r for r in review if r!='Language needs verification']
 notes.append('Language: '+language_method+'.')
 if language_method.startswith('inferred'):review.append('Language inferred')
 if evidence and not detected_language:notes.append('No readable language evidence from text extraction; rely on visual verification or the stated catalog tagging rule where available.')
 if title=='Unknown' or (re.fullmatch(r'\d+',title) and i not in [451,232]):review.append('Title needs verification')
 if i==451:notes.append('Title ۲۳ is confirmed in extracted text; it is not an unidentified numeric filename.')
 if re.search(r'زنده?گی.?نامه|زندگینامه|معرفی|ویژه نامه|یادنامه',title) and 'category' not in o:category=C['M'];sub='Biography';kind='Nonfiction'
 # Every normalized field is traceable without claiming unverified edition details.
 notes.append('Author source: '+provenance['author']+'.')
 notes.append('Original file: '+original+' | Source folder: '+folder+'.')
 if review:notes.insert(0,'REVIEW: '+('; '.join(dict.fromkeys(review)))+'.')
 tags=[sub]
 if 'Persian' in language.split('; '):tags.append('Persian language tag' if persian_policy else 'Persian-language edition')
 if kind=='Poetry':tags.append('Poetry')
 if category in [C['F'],C['D'],C['Q'],C['I']]:tags.append('Fiction')
 if re.search(r'ترجمه|برگردان',original):tags.append('Translation')
 row=[f['id'],title,author,kind,category,sub,'; '.join(dict.fromkeys(tags)),language,row[8],series,' '.join(notes),row[11],row[12],fmt,f['url']]
 return row,bool(review),{'author_source':provenance['author'],'language_source':language_method,'content_language_source':content_language_method,'persian_tag_by_user_rule':persian_policy,'text_checked':bool(evidence),'text_readable_language':bool(content_language(text) or evidence.get('language'))}

# Corrections confirmed in extracted title pages or retained as explicitly uncertain.
put(1515,author='Stein, Marky',note='Author confirmed on the extracted title and copyright pages.')
put(1523,author='Public Library Association; Editors of VGM Career Books',title='The Guide to Basic Cover Letter Writing')
put(1514,author='Career Confidential',title='Interview Prep Kit',note='Corporate source credited in the document; individual writer not established.')
put(1461,author='جعفر حسنی بروجردی')
put(1452,author='Castoriadis, Cornelius')
put(1453,author='بهرام محیی')
put(1386,author='قاضی ربیحاوی')
put(1387,author='محمود داوودی')
put(1390,author='میترا الیاتی')
put([1402,1406],author="O’Connor, Frank")
put(1403,author='Fitzgerald, F. Scott',title='سه ساعت بین دو پرواز')
put(1411,title='شب ها موش های صحرایی هم می خوابند!')
put(1413,author='Barthelme, Donald',title='اولین اشتباه بچه')
put(939,author='Various authors',title='بازگشت به تنهایی: ۱۵ داستان از ۱۵ نویسنده')
put(1204,author='Unknown',title='سیستم جنایتکار: اسناد دادگاه میکونوس')
put([1120,1121,1122],author='حافظ شیرازی')
put(1120,title='دیوان کهنه حافظ',note='Edited under the supervision of Iraj Afshar; poet Hafez is the author.')
put([1123,1124],author='عمر خیام')
put(1123,title='رباعیات خیام',note='Khanji credited in filename; contributor role requires verification.')
put(1124,title='ترانه های خیام',note='Sadegh Hedayat is the editor/commentator; Omar Khayyam is the poet.')
put(1134,author='جلال الدین محمد بلخی (مولانا)',title='گزیده هایی از مثنوی مولوی')
put([1135,1136,1137],author='جلال الدین محمد بلخی (مولانا)',title='دیوان شمس تبریزی')
put(list(range(1112,1120)),author='احمد شاملو')
put([924,925],title='تذکرة الاولیا')
put(918,title='عارف نامه')
put([262,477,1439],author='عبدالکریم سروش; محمد مجتهد شبستری; مصطفی ملکیان; محسن کدیور',title='سنت و سکولاریسم')
put(943,title='مردان مریخی، زنان ونوسی')
put(954,title='Who Moved My Cheese?')
put(955,title='The One Minute Manager')
put([1428,1429],title='مانیفست حزب کمونیست',note='Numeric filename suffix distinguishes source files; volume assignment unverified.')
put([926,927,931],title='قرآن مبین',category=C['R'],subcategory='Islam & Quran',kind='Reference')
put(1253,author='Bulgakov, Mikhail',title='دل سگ')
put([692,695,696],author='هوشنگ گلشیری')
put(1022,author='Russell, Bertrand',category=C['F'],subcategory='Short stories',kind='Fiction')
put(1150,author='محسن کدیور',category=C['R'],subcategory='Islamic thought',kind='Nonfiction')
put(68,title='War and Peace',series='War and Peace; source file 1')
put(69,title='Father Sergius')
put(71,title='Anna Karenina')
put(300,title='Awaken the Giant Within')
put(302,title='رساله',language='Persian',note='Archive named resaleh; title inferred from Persian transliteration, archive contents unverified.')
put(32,title='سووشون')
put(285,title='خوشه های خشم — جلد 3')
put(286,title='خوشه های خشم — جلد 2')
put(237,title='The Grand Chessboard: American Primacy and Its Geostrategic Imperatives')
put(238,title='Second Chance')
put(239,title="Between Two Ages: America’s Role in the Technetronic Era")
put(240,title='America and the World',author='Brzezinski, Zbigniew; Scowcroft, Brent',note='Conversations moderated by David Ignatius; co-contributor requires edition-level verification.')
put(336,category=C['F'],subcategory='Biographical fiction',kind='Fiction')
put(342,category=C['Y'],subcategory='Personal development',kind='Nonfiction')
put(397,category=C['A'],subcategory='Sports & recreation',kind='Nonfiction')
put(938,author='Wolff, Tobias')
put(1351,author='ناصر نامدار')
put(1156,author='Gray, John (political philosopher)')
put(1216,category=C['F'],subcategory='General fiction',kind='Fiction')
put(1335,category=C['H'],subcategory='Political history',kind='Nonfiction')
put([124,127,128,130,133,134,139,141,142,144,151,152,169,170,272,287,288,289,290,291,1358,1360,1363,1364,1377,1342],category=C['F'],subcategory='Short stories',kind='Fiction')
for i,a in [(377,'Rolland, Romain'),(882,'Various authors'),(892,'محمد تهامی نژاد'),(893,'Bazin, André'),(895,'بصیر نصیبی'),(896,'Huaco, George A.'),(900,'بصیر نصیبی'),(901,'Casebier, Allan; DeNitto, Dennis; Herman, William'),(902,'Kracauer, Siegfried'),(946,'Pease, Allan'),(1432,'Dunayevskaya, Raya'),(1276,'Myrivilis, Stratis'),(1274,'Millon, Robert P.')]:
 put(i,author=a,language='Persian',language_verified=True,note='Author and Persian edition verified by visual inspection of scanned title/front-matter pages.')
put(377,note='Scanned title page credits Romain Rolland; the filename incorrectly says Romain Gary.')
put(882,note='Anthology edited by Bill Nichols; Persian translation by Mohammad Shahba. Editor is distinguished from chapter authors.')
put(1369,author='Various authors',title='این راز سر به مهر: داستان هایی درباره زندگانی نویسندگان روس',language='Persian',language_verified=True,note='Title-page subject list includes Pushkin, Lermontov, Dostoevsky, Chekhov and Tolstoy; their names are not taken as authorship credits. Translation credited to F. M. Javan.')
put(1274,title='زاپاتا: ایدئولوژی یک دهقان انقلابی',category=C['M'],subcategory='Political biography',kind='Nonfiction')
put(1276,category=C['I'],subcategory='War fiction',kind='Fiction')
put(1458,author='Lin, Mike W.',title='Drawing and Designing with Confidence: A Step-by-Step Guide',language='English',language_verified=True,note='Author/title matched to the publisher Wiley catalog; this scan omits the original title page.',source_url='https://uat.store.wiley.com/en-us/drawing-and-designing-with-confidence-a-step-by-step-guide-p-9780471283904')
for i,a in [(693,'هوشنگ گلشیری'),(694,'هوشنگ گلشیری'),(1213,'عبدالحسین آگاهی'),(1160,'پناهی سمنانی'),(1218,'Roosevelt, Kermit'),(1404,'ناصر زراعتی')]:
 put(i,author=a,language='Persian',language_verified=True,note='Credit and language verified from rendered document pages.')
put(1306,author='Various authors',language='Persian',language_verified=True,note='Literary essay anthology, selected and translated by Abolhassan Najafi; he is not the sole original author.')
put(1214,author='بهداد',title='خاطرات زندان — بخش اول',language='Persian',language_verified=True,note='Author credited as Behdad; full identity is not expanded.')
put(1160,title='فتحعلی شاه قاجار: سقوط در کام استعمار')
put(489,title='زندگی نامه دکتر علی شریعتی')
put(552,title='زندگی نامه صادق هدایت')
put(779,title='زندگی نامه جلال آل احمد')
put(1404,author='Silverstein, Shel',category=C['A'],subcategory='Poetry',kind='Poetry',language='Persian',language_verified=True,note='Persian translation; author Shel Silverstein is credited on the first page.')
put(1412,author='Joyce, James',language='Persian',language_verified=True,note='Persian excerpt with Joyce biographical introduction; work title retained from filename.')
for i,a in [(1409,'Murakami, Haruki'),(472,'فروغ جهانبخش'),(932,'Kellens, Jean'),(1177,'منوچهر طباطبایی مؤتمنی'),(1148,'هوشنگ صدیق'),(1205,'علی رضا نوری زاده'),(1232,'Cline, Austin'),(1229,'اعظم کیانجوئی'),(1194,'Cliff, Tony; Birchall, Ian'),(1459,'ارسلان میربشری')]:
 put(i,author=a,language='Persian',language_verified=True,note='Credit and language verified from rendered title/front-matter pages.')
put(1409,title='فاجعه معدن در نیویورک')
put(517,author='علی شریعتی',note='Compilation of Shariati quotations, assembled by Amir Rezaei; compiler distinguished from quoted author.',language='Persian',language_verified=True)
put([1143,1144],author='نعمت الله صالحی نجف آبادی',title='شهید جاوید',language='Persian',language_verified=True,note='Numeric filenames resolved by scanned title pages; different scans/excerpts retained.')
put([1146,1147],author='مرکز مشاوره و آموزش حقوقی ویژه فعالان مدنی و سیاسی',language='Persian',language_verified=True,note='Institution credited on the cover; individual authors not listed.')
put(1146,title='اصول حاکم بر دادرسی و مراحل مختلف رسیدگی به اتهام')
put(1147,title='احضار، بازداشت و سایر قرارهای تامین')
put(1206,author='مؤسسه مطالعات و پژوهش های سیاسی',title='سازمان مجاهدین خلق: پیدایی تا فرجام',language='Persian',language_verified=True)
put(1200,author='Various authors',note='Essay collection; contributors named on the title page include Mohsen Sazegara, Emadeddin Afrough, Mohsen Kadivar, Mohammad Reza Tajik, Mohammad Reza Hajipour, Saeed Hajjarian and Ali Alavi-Tabar.',language='Persian',language_verified=True)
put(1528,author='کمال الدین بهزاد',note='Collection of artworks; artist credited, compiler not identified.',language='Persian',language_verified=True)
put(1529,author='Leonardo Collection (editorial collective)',note='Series/editorial credit, not Leonardo da Vinci as a personal author. Translation by Parinaz Shahneh.',language='Persian',language_verified=True)
put(1532,author='رضا صادقیان',note='Credit read from scanned title page; Hans Thoma is the subject.',language='Persian',language_verified=True)
put(1176,title='درباره آمریکا: قانون اساسی ایالات متحده آمریکا همراه با یادداشت های تکمیلی',author='United States Department of State',kind='Reference',note='Corporate compilation includes the United States Constitution; individual framers are not listed as sole authors.',language='Persian',language_verified=True)
for i in [489,494,495,551,552,779,951,1212,1223,1238,1239,1240,1244,1248,1158,1192,1220,1222,1460,1526,1527,1530,1531]:put(i,language='Persian',language_verified=True)
SOURCE_INDEX=json.loads((ROOT/'metadata_source_order.json').read_text(encoding='utf-8')) if (ROOT/'metadata_source_order.json').exists() else {}
put(1384,author='رسول پرویزی',source_url='https://fa.wikisource.org/wiki/فهرست:Shalvarha-ye_vassle_dar_-_Rasoul_Parvizi.pdf',note='Matched to the contents of the author’s collection Shalvarha-ye vassle-dar.')
put(1532,author='هلموت دله',note='Author name transcribed from scanned title page; Hans Thoma is the subject.')
put([422,446,452],author='Unknown',note='Secondary political commentary found in the Shamlou collection; no reliable author credit established.')
for i,a in [(1238,'حمید حمید'),(1239,'Pannekoek, Anton'),(1244,'Anderson, Perry')]:
 put(i,author=a,language='Persian',language_verified=True,note='Author signature and Persian language verified on the final page of the document; publisher and transcription credits distinguished from authorship.')
for i,a in [(1526,'Loomis, Andrew'),(1527,'غلامحسین امیرخانی'),(1530,'Franks, Gene'),(1531,'Tacconi, Ferdinando')]:
 put(i,author=a,language='Persian',language_verified=True,note='Author/artist credit read on the scanned cover or title page; Persian instructional edition verified visually.')
put(779,author='جلال آل احمد',category=C['M'],subcategory='Autobiography',note='First-person autobiographical text checked visually, beginning with the author’s family background and birth in 1302; distinguished from third-person biographies.')
put(551,author='Various authors',note='Multiple essays and a biographical chronology; individual essay contributors not established. Collective authorship recorded rather than the subject Hedayat.')
put(446,author='مسلم منصوری',language='Persian',language_verified=True,note='Author signature read at the end of the complete extracted document; Ahmad Shamlou is the subject and quoted poet.')
for i in [238,1169,1252,1379]:put(i,language='English',language_verified=True,note='English text verified visually on rendered opening and final pages of this file.')
for i in [421,1011,1398,1401,1405,1407,1410,1414,1464]:put(i,language='Persian',language_verified=True,note='Persian text verified visually on rendered pages; romanized or English filename was not taken as language proof.')
put(1252,title='The Grass Is Singing — Penguin Readers adaptation',note='Scanned cover identifies Penguin Readers Level 5; catalog distinguishes the graded adaptation from the unabridged novel.')
put(1464,title='لئوناردو داوینچی و پابلو پیکاسو',note='Biographical/art overview; artists are subjects, no author byline established.')
put(1397,author='خسرو شاهانی',title='زباله های دولتی',language='Persian',language_verified=True,note='Author explicitly credited in the decoded Windows-1256 HTML body; office-file editor metadata was not taken as authorship.')
put(1408,author='محمد پورثانی',title='لبخند',language='Persian',language_verified=True,note='Author explicitly credited in the decoded Windows-1256 HTML body; replaces earlier attribution based on filename/collection.')
for i in [272,274,275,287]:put(i,language='English',language_verified=True,note='English narrative paragraphs read directly from the legacy Word file contents; language not inferred from the filename.')
put(1340,language='English',language_verified=True,note='English narrative verified in the source RTF body, including the final scene; embedded image data ignored.')
