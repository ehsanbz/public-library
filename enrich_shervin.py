"""Recover searchable metadata from saved Telegram descriptors, recording each basis.

Run explicitly before build_catalog.py. Never infer edition/ISBN/year from title
numbers, or language from an author's nationality or a translated caption.
"""
import collections
import json
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent
UNKNOWN = 'Unknown'

def norm(value):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', value).translate(str.maketrans('يك', 'یک')).replace('\u200c', ' ').replace('_', ' ')).strip().casefold()

# Deliberately specific terms. A generic word such as "life", "world", or an
# author's name cannot assign a subject. First match supplies the main category;
# all matching subjects remain searchable as topic tags.
SUBJECTS = [
 ('Science Fiction','Science fiction',r'\bscience fiction\b|علمی تخیلی|utopia classics|perry rhodan'),
 ('Mystery & Thriller','Crime & mystery',r'\b(?:detective|crime fiction|murder mystery|thriller)\b|رمان جنایی|داستان پلیسی|#جنایی|#پلیسی'),
 ('Historical Fiction','Historical fiction',r'\bhistorical (?:novel|fiction)\b|رمان تاریخی'),
 ('Biography & Memoir','Biography & memoir',r'\b(?:autobiography|biography|biographical|memoirs?)\b|زندگی ?نامه|خاطرات|خودزندگینامه'),
 ('Arts & Culture','Poetry',r'\b(?:poems?|poetry|poetics)\b|\bدیوان\b|\bاشعار\b|\bشعر\b|#شعر'),
 ('Arts & Culture','Drama',r'\b(?:plays|drama|playwright)\b|نمایشنامه|نمایش نامه|فیلمنامه'),
 ('Language & Linguistics','Language & linguistics',r'\b(?:linguistics?|grammar|dictionary|dictionaries|vocabulary|ielts|toefl|etymology|lexicon|translation studies)\b|زبان ?شناسی|دستور زبان|فرهنگ لغت|واژه نامه|آیلتس|آیلس|تافل|#زبان'),
 ('Technology & Computing','Computing & engineering',r'\b(?:algorithms?|programming|computer|computing|software|javascript|python|machine learning|artificial intelligence|engineering|robotics|cryptography)\b|برنامه نویسی|هوش مصنوعی|مهندسی|کامپیوتر|رایانه'),
 ('Health','Medicine & health',r'\b(?:medicine|medical|clinical|anatomy|physiology|nursing|nutrition|psychiatry|pharmacology|diseases|surgery|healthcare)\b|پزشکی|پرستاری|داروشناسی|تغذیه|#سلامت'),
 ('Psychology','Psychology & personal development',r'\b(?:psycholog\w*|psychoanal\w*|psychotherap\w*|cognitive therapy|self.help|motivation)\b|روان ?شناسی|روانکاوی|روان ?درمانی|روان ?پزشکی|#موفقیت'),
 ('Business & Economics','Economics & business',r'\b(?:econom\w*|finance|financial|accounting|marketing|entrepreneur\w*|business|macroeconomics|microeconomics|management)\b|اقتصاد|بازاریابی|حسابداری|کارآفرینی|مدیریت'),
 ('Philosophy','Philosophy',r'\b(?:philosoph\w*|epistemolog\w*|metaphysics|ontology|ethics|phenomenolog\w*|existentialism|aesthetics|dialectic\w*)\b|فلسفه|فلسفی|معرفت ?شناسی|هستی ?شناسی|متافیزیک|پدیدارشناسی|دیالکتیک|\bمنطق\b'),
 ('Religion','Religion & spirituality',r'\b(?:religion|religious|theolog\w*|quran|koran|bible|biblical|christianity|buddhism|hinduism|zoroastrian\w*|sufism|mysticism|islamic theology)\b|ادیان|دین ?پژوهی|الهیات|قرآن|تفسیر قرآن|تصوف|عرفان|زرتشت|مذهبی|#دین|#اسلام'),
 ('Science','Mathematics & natural sciences',r'\b(?:mathematics|mathematical|algebra|geometry|calculus|physics|quantum|chemistry|biology|biological|geology|astronomy|astrophysics|neuroscience|botany|zoology|genetics|thermodynamics|ecology|evolutionary biology)\b|ریاضی|جبر|هندسه|فیزیک|شیمی|زیست ?شناسی|زمین ?شناسی|نجوم|ژنتیک|بوم ?شناسی|#علمی'),
 ('Social Sciences','Politics, law & society',r'\b(?:politic\w*|sociolog\w*|anthropolog\w*|democra\w*|socialism|communism|marxism|capitalism|imperialism|colonial\w*|feminism|feminist|geopolitics|international relations|jurisprudence|law|social theory)\b|سیاست|سیاسی|جامعه ?شناسی|انسان ?شناسی|دموکراسی|سوسیالیسم|کمونیسم|مارکسیسم|سرمایه ?داری|فمینیسم|حقوق|استعمار|#اجتماعی'),
 ('History','History & archaeology',r'\b(?:history|historical|historian|archaeolog\w*|ancient|achaemenid|sasanian|sassanian|safavid|world war)\b|تاریخ|باستان ?شناسی|هخامنشی|ساسانی|صفوی|قاجار|جنگ جهانی'),
 ('Travel & Geography','Travel & geography',r'\b(?:geography|geographical|travelogue|travel guide|cartography|atlas)\b|جغرافیا|سفرنامه|سفر نامه|اطلس'),
 ('Arts & Culture','Arts, literature & culture',r'\b(?:literary criticism|literature|cinema|film studies|photography|architecture|painting|music|folklore|mythology|mythologies)\b|نقد ادبی|ادبیات|سینما|عکاسی|معماری|نقاشی|موسیقی|فولکلور|اسطوره|فرهنگ عامه|#ادبی'),
 ('Literary Fiction','Fiction',r'\b(?:novel|fiction|short stories|fairy tales)\b|\bرمان\b|داستان|قصه|افسانه|#عاشقانه'),
]
LANGUAGES = {
 'english':'English','انگلیسی':'English','فارسی':'Persian','پارسی':'Persian','persian':'Persian','farsi':'Persian',
 'arabic':'Arabic','عربی':'Arabic','german':'German','deutsch':'German','آلمانی':'German',
 'french':'French','français':'French','فرانسه':'French','فرانسوی':'French','spanish':'Spanish','español':'Spanish','اسپانیایی':'Spanish',
 'italian':'Italian','italiano':'Italian','ایتالیایی':'Italian','russian':'Russian','روسی':'Russian','turkish':'Turkish','ترکی':'Turkish',
 'portuguese':'Portuguese','پرتغالی':'Portuguese','azerbaijani':'Azerbaijani','آذری':'Azerbaijani','kurdish':'Kurdish','کردی':'Kurdish',
 'latin':'Latin','لاتین':'Latin','hebrew':'Hebrew','عبری':'Hebrew','armenian':'Armenian','ارمنی':'Armenian',
}

def explicit_language(lines):
    found = set()
    for line in lines:
        m = re.search(r'(?:\blanguages?\b|زبان)\s*[:：]\s*(.+)', line, re.I)
        if not m: continue
        value = norm(m[1])
        for label, canonical in LANGUAGES.items():
            if re.search(r'(?<!\w)'+re.escape(label)+r'(?!\w)', value): found.add(canonical)
    return '; '.join(sorted(found))

def inferred_language(title, filename):
    # Analyze the attachment's wording, not its promotional Persian caption.
    text = norm(re.sub(r'\.(pdf|epub|djvu|docx?|rtf|zip|rar)$', '', filename, flags=re.I)+' '+title)
    words = re.findall(r'[^\W\d_]+', text)
    arabic = re.findall(r'[\u0600-\u06ff]',text)
    if len(arabic)>8 and re.search(r'[پچژگکی]',text) and len(arabic)>len(re.findall(r'[a-z]',text)):
        if re.search(r'\b(?:کتاب|های|هایی|در|از|به|برای|شناسی|و|یک|این|آن|تاریخ|فلسفه|داستان|زندگی)\b',text):
            return 'Persian','Persian orthography and wording in title/attachment filename'
    sets = {
      'English':set('the of and to in for with from on a an its this how what why is are as by'.split()),
      'German':set('der die das und ein eine einer eines von zur zum über zwischen geschichte mit für des den dem im'.split()),
      'French':set('le la les des du une un et dans pour avec sur aux histoire philosophie'.split()),
      'Spanish':set('el los las del una y para con historia filosofía'.split()),
      'Italian':set('il gli della dello delle degli alla nella nel storia filosofia'.split()),
    }
    if len(arabic)>5:return '', ''
    scores={lang:len(set(words)&v) for lang,v in sets.items()}
    rank=sorted(scores,key=scores.get,reverse=True)
    if scores[rank[0]]>=2 and scores[rank[0]]>scores[rank[1]]:
        return rank[0], 'distinctive '+rank[0]+' wording in title/attachment filename'
    return '', ''

def enrich(row, descriptor, existing_matches):
    row=list(row)
    evidence={}
    def put(index,value,basis,quote):
        if not value:return
        row[index]=value
        evidence[str(index)]={'value':value,'basis':basis,'excerpt':quote[:350]}
    lines=descriptor['fields']
    language=explicit_language(lines)
    if language:put(7,language,'explicit source language label',next(x for x in lines if re.search(r'(?:\blanguages?\b|زبان)\s*[:：]',x,re.I)))
    else:
        language,basis=inferred_language(row[1],descriptor['filename'])
        if language:put(7,language,'inferred: '+basis,descriptor['filename'])
    titletext=norm(row[1]+' '+descriptor['filename'])
    hashtags=[tag for tag in descriptor['hashtags'] if not re.search(r'کتابخان|دانلود|کانال|منابع|عیدانه|نوروز|مناسبتی|\d|[۰-۹]|صدکتاب|pdf|epub',tag,re.I)]
    subjecttext=norm(' '.join(hashtags)+' '+' '.join(x for x in lines if re.search(r'^(?:subject|genre|category|موضوع|ژانر|دسته)\s*[:：]',x,re.I)))
    tags=[]
    matches=[]
    for category,theme,pattern in SUBJECTS:
        hit=re.search(pattern,subjecttext,re.I)
        if hit:matches.append((category,theme,'source subject label/hashtag',hit[0]))
    if not matches:
        for category,theme,pattern in SUBJECTS:
            hit=re.search(pattern,titletext,re.I)
            if hit:matches.append((category,theme,'inferred: explicit subject/genre term in title or filename',hit[0]))
    key=(norm(row[1]),norm(row[2]))
    reference=existing_matches.get(key)
    if reference:
        put(4,reference[4],'exact title and author match to existing catalog subject',reference[1]+' / '+reference[2])
        put(5,reference[5],'exact title and author match to existing catalog subject',reference[1]+' / '+reference[2])
        tags.extend(reference[6].split('; '))
    elif matches:
        c,t,b,q=matches[0];put(4,c,b,q);put(5,t,b,q)
    for _,theme,_,_ in matches:tags.append(theme)
    for tag in hashtags:
        clean=tag.lstrip('#').replace('_',' ').strip()
        if clean and len(clean)<65 and not re.search(r'کتابخانه|دانلود|کانال|ممنوعه|کمیاب|نایاب|درخواستی|pdf|epub|عیدانه|نوروز|مناسبتی',clean,re.I):tags.append(clean)
    tags=list(dict.fromkeys(x for x in tags if x and x!='Unknown'))
    if tags:put(6,'; '.join(tags),'source subject tags, matched subjects and contributor credits','; '.join(descriptor['hashtags']))
    years=set()
    for line in lines:
        m=re.search(r'^(?:publication year|published|year|سال انتشار|سال نشر|تاریخ انتشار)\s*[:：]\s*([0-9۰-۹٠-٩]{4})(?!\d)',line,re.I)
        if m:
            n=''.join(str(unicodedata.digit(c)) for c in m[1])
            if 1000<=int(n)<=2026:years.add(n)
    if len(years)==1:put(8,next(iter(years)),'explicit source publication-year label','; '.join(lines))
    volumes=re.findall(r'(?:\b(?:vol(?:ume)?\.?|part)\s*[IVXivx\d]+\b|(?:جلد|ج|بخش)\s*[۰-۹0-9]+|جلد\s+(?:اول|دوم|سوم|چهارم|پنجم|ششم|هفتم|هشتم|نهم|دهم))',row[1],re.I)
    if volumes:put(9,'; '.join(dict.fromkeys(volumes)),'explicit volume/part marker in source title',row[1])
    for line in lines:
        m=re.search(r'\bISBN(?:-1[03])?\s*[:：]?\s*([\dXx -]{10,25})',line,re.I)
        if m:
            isbn=re.sub(r'[^\dXx]','',m[1]).upper()
            valid=(len(isbn)==13 and isbn.isdigit() and sum(int(c)*(1 if i%2==0 else 3) for i,c in enumerate(isbn))%10==0) or (len(isbn)==10 and isbn[:9].isdigit() and (isbn[-1].isdigit() or isbn[-1]=='X') and sum((10-i)*(10 if c=='X' else int(c)) for i,c in enumerate(isbn))%11==0)
            if valid:put(11,isbn,'explicit source ISBN label; checksum verified',line)
        m=re.search(r'^(?:edition|ویرایش|نوبت چاپ)\s*[:：]\s*(.{1,70})$',line,re.I)
        if m:put(12,m[1].strip(),'explicit source edition label',line)
    # Remove the original blanket unknown claim now that per-field evidence exists.
    note=re.sub(r'^REVIEW: Imported book classification; language, subject and edition not verified\.\s*','',row[10])
    note=re.sub(r'^REVIEW: Source metadata and inferred fields require verification against the attachment\.\s*','',note)
    note=re.split(r' Metadata enrichment:',note)[0]
    details=' '.join(f'{["Original ID","Title","Author","Type","Category","Theme","Topics","Language","Year","Volume","Notes","ISBN","Edition"][int(i)]}: {v["basis"]} ({v["excerpt"][:100]}).' for i,v in evidence.items())
    details+=' Source filename: '+descriptor['filename']+'.'
    if descriptor.get('editor'):details+=' Editor: '+descriptor['editor']+'.'
    row[10]='REVIEW: Source metadata and inferred fields require verification against the attachment. '+note+' Metadata enrichment: '+details
    return row,evidence

def main():
    source=json.loads((ROOT/'shervin_vakili_source.json').read_text(encoding='utf-8'))
    descriptors=json.loads((ROOT/'shervin_vakili_metadata.json').read_text(encoding='utf-8'))
    catalog=json.loads((ROOT/'catalog_data.json').read_text(encoding='utf-8'))
    references=collections.defaultdict(list)
    for r in catalog['rows']:
        if r[15]!='Shervin Vakili Library' and r[2]!='Unknown' and r[4]!='Unknown':references[(norm(r[1]),norm(r[2]))].append(r)
    references={k:v[0] for k,v in references.items() if len({(r[4],r[5]) for r in v})==1}
    audit={};rows=[]
    for row in source['rows']:
        revised,evidence=enrich(row,descriptors[row[0]],references)
        rows.append(revised)
        if evidence:audit[row[0]]={'source_url':row[14],'fields':evidence}
    source['rows']=rows
    source['metadata_enriched_at']=source['updated_at']
    source['metadata_evidence']='shervin_vakili_metadata_audit.json'
    (ROOT/'shervin_vakili_source.json').write_text(json.dumps(source,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    (ROOT/'shervin_vakili_metadata_audit.json').write_text(json.dumps(audit,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    coverage={name:sum(r[index]!='Unknown' for r in rows) for index,name in [(2,'author'),(4,'category'),(5,'theme'),(7,'language'),(8,'year'),(9,'volume'),(11,'isbn'),(12,'edition')]}
    report={'records':len(rows),'coverage':coverage,'language_methods':dict(collections.Counter(v['fields']['7']['basis'].split(':')[0] for v in audit.values() if '7' in v['fields'])),'category_methods':dict(collections.Counter(v['fields']['4']['basis'].split(':')[0] for v in audit.values() if '4' in v['fields']))}
    (ROOT/'shervin_vakili_metadata_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':main()
