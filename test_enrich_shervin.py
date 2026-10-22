import unittest
from enrich_shervin import enrich

def row(title='An opaque title', author='Unknown'):
    return ['shervin-vakili:1',title,author,'Book','Unknown','Unknown','Shervin Vakili Library','Unknown','Unknown','Unknown','REVIEW: Imported book classification; language, subject and edition not verified. Original description.','Unknown','Unknown','PDF','https://t.me/SherwinVakiliLibrary/1']

def descriptor(filename='opaque.pdf',fields=None,hashtags=None):
    return {'filename':filename,'fields':fields or [],'hashtags':hashtags or [],'translator':'','editor':''}

class MetadataRecovery(unittest.TestCase):
    def test_label_overrides_language_of_title(self):
        result,evidence=enrich(row('The History of Iran'),descriptor(fields=['Language: Persian','Year: 2014']),{})
        self.assertEqual(result[7:9],['Persian','2014'])
        self.assertEqual(evidence['7']['basis'],'explicit source language label')

    def test_language_not_from_author_or_subject(self):
        result,_=enrich(row('Iran','William Shakespeare'),descriptor(),{})
        self.assertEqual(result[7],'Unknown')

    def test_channel_branding_is_not_a_subject(self):
        result,_=enrich(row('آس و پاس ها'),descriptor(hashtags=['#کتابخانۀ_منابع_تاریخ_وادیان_ایران_وجهان']),{})
        self.assertEqual(result[4],'Unknown')

    def test_explanation_does_not_imply_religion(self):
        result,_=enrich(row('ترجمه و تفسیر برهان شفای'),descriptor(),{})
        self.assertEqual(result[4],'Unknown')

    def test_caption_tag_supports_subject_and_filename_is_searchable(self):
        result,evidence=enrich(row('A cryptic title'),descriptor('original-name.pdf',hashtags=['#روانشناسی']),{})
        self.assertEqual(result[4],'Psychology')
        self.assertIn('original-name.pdf',result[10])
        self.assertEqual(evidence['4']['basis'],'source subject label/hashtag')

    def test_conflicting_years_and_invalid_isbn_remain_unknown(self):
        result,_=enrich(row(),descriptor(fields=['Year: 2010','Year: 2011','ISBN: 9781234567890']),{})
        self.assertEqual(result[8],'Unknown')
        self.assertEqual(result[11],'Unknown')

    def test_valid_isbn_and_explicit_volume(self):
        result,_=enrich(row('History of Iran Volume 2'),descriptor(fields=['ISBN: 978-0-306-40615-7']),{})
        self.assertEqual(result[11],'9780306406157')
        self.assertEqual(result[9],'Volume 2')

    def test_repeat_enrichment_is_stable(self):
        original=row('The History of Iran')
        desc=descriptor('The History of Iran.pdf',fields=['Language: English'])
        first,_=enrich(original,desc,{})
        second,_=enrich(first,desc,{})
        self.assertEqual(first,second)

if __name__=='__main__':unittest.main()
